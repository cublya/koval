use crate::{Agent, Client, Planner, Reviewer};
use koval_common::Config;
use koval_protocol::openai::Message;
use koval_tools::{shell::ShellTool, files::{ReadFileTool, WriteFileTool, ListDirTool}};
use std::sync::Arc;
use std::path::PathBuf;
use std::process::Command;
use anyhow::Result;
use futures::future::join_all;
use tokio::sync::Semaphore;

pub struct Swarm {
    config: Config,
    client: Client,
    planner: Planner,
    semaphore: Arc<Semaphore>,
}

impl Swarm {
    pub fn new(config: Config, client: Client) -> Self {
        let planner = Planner::new(config.clone(), client.clone());
        let max_workers = config.max_workers;
        Self {
            config,
            client,
            planner,
            semaphore: Arc::new(Semaphore::new(max_workers)),
        }
    }

    pub async fn run(&self, goal: &str) -> Result<()> {
        println!("Orchestrator: analyzing goal '{}'...", goal);
        
        let subtasks = self.planner.plan(goal).await?;
        println!("Plan: {:?}", subtasks);

        let mut handles = Vec::new();

        for (i, task) in subtasks.into_iter().enumerate() {
            let config = self.config.clone();
            let client = self.client.clone();
            let task_prompt = task.clone();
            let permit = self.semaphore.clone().acquire_owned().await;

            // Spawn a new async task for each subtask
            let handle = tokio::spawn(async move {
                // Hold permit until task is done
                let _permit = permit; // Move permit into closure
                
                println!("[Agent {}] Starting task: {}", i, task_prompt);
                
                // 1. Setup Git Worktree for Isolation
                let work_dir = match setup_worktree(i) {
                    Ok(p) => p,
                    Err(e) => {
                        eprintln!("[Agent {}] Failed to setup worktree: {}", i, e);
                        return;
                    }
                };

                // Ensure cleanup happens (rudimentary defer)
                let run_result = async {
                    let mut agent = Agent::new(config.clone(), client.clone());
                    // Initialize LLM-based Reviewer
                    let mut reviewer = Reviewer::new(config.clone(), client.clone(), work_dir.clone());
                    
                    // Register Tools with isolated work_dir
                    agent.register_tool(Arc::new(ShellTool::new(work_dir.clone())));
                    agent.register_tool(Arc::new(ReadFileTool::new(work_dir.clone())));
                    agent.register_tool(Arc::new(WriteFileTool::new(work_dir.clone())));
                    agent.register_tool(Arc::new(ListDirTool::new(work_dir.clone())));

                    // Context specific prompt
                    let system_msg = Message::system(format!(
                        "You are a specialized Swarm Agent working on task #{}: '{}'. 
                        Execute this task efficiently. 
                        You are working in an isolated git worktree at {:?}.
                        After you complete your work, a Lead Reviewer (Agent) will verify your work.
                        If they reject it, you must fix the issues.", 
                        i, task_prompt, work_dir
                    ));
                    
                    agent.add_message(system_msg);
                    agent.add_message(Message::user(format!("Please execute: {}", task_prompt)));

                    let max_retries = 3;
                    let mut attempts = 0;
                    let mut success = false;

                    while attempts < max_retries && !success {
                        attempts += 1;
                        println!("[Agent {}] Execution Attempt {}/{}", i, attempts, max_retries);

                        // 1. Run Agent
                        if let Err(e) = agent.run().await {
                            eprintln!("[Agent {}] Execution failed: {}", i, e);
                            return Ok(()); // Or retry?
                        }

                        // 2. Review Loop (LLM-based)
                        println!("[Agent {}] Requesting Review...", i);
                        match reviewer.review(&task_prompt).await {
                            Ok((approved, feedback)) => {
                                if approved {
                                    println!("[Agent {}] Reviewer APPROVED.", i);
                                    success = true;
                                }
                                else {
                                    println!("[Agent {}] Reviewer REJECTED.\nFeedback: {}", i, feedback);
                                    // Feed failure back to agent
                                    agent.add_message(Message::user(format!(
                                        "The Lead Reviewer rejected your work. Please fix the issues based on this feedback:\n\n{}", 
                                        feedback
                                    )));
                                }
                            }
                            Err(e) => {
                                eprintln!("[Agent {}] Reviewer crashed: {}", i, e);
                                // If reviewer crashes, maybe we stop?
                                break;
                            }
                        }
                    }
                    
                    if !success {
                         println!("[Agent {}] Failed to complete task after {} attempts.", i, max_retries);
                    }

                    Ok::<(), anyhow::Error>(())
                }.await;

                if let Err(e) = run_result {
                     eprintln!("[Agent {}] Error in run loop: {}", i, e);
                }

                // Cleanup
                if let Err(e) = teardown_worktree(i) {
                     eprintln!("[Agent {}] Failed to teardown worktree: {}", i, e);
                } else {
                    println!("[Agent {}] Worktree cleanup complete.", i);
                }
            });
            
            handles.push(handle);
        }

        join_all(handles).await;
        
        println!("Swarm run complete.");
        Ok(())
    }
}

// Helper: Setup isolated worktree
fn setup_worktree(id: usize) -> Result<PathBuf> {
    let dir_name = format!(".koval_worktrees/agent_{}", id);
    let path = PathBuf::from(&dir_name);
    
    // Ensure parent dir exists
    if let Some(parent) = path.parent() {
        if !parent.exists() {
             std::fs::create_dir_all(parent)?;
        }
    }
    
    // Clean up if exists
    if path.exists() {
        teardown_worktree(id)?;
    }
    
    // Run git worktree add
    let output = Command::new("git")
        .args(&["worktree", "add", "--detach", &dir_name])
        .output()?;
        
    if !output.status.success() {
        return Err(anyhow::anyhow!("git worktree add failed: {}", String::from_utf8_lossy(&output.stderr)));
    }
    
    // Return absolute path for better safety with tools?
    // current_dir() + path
    Ok(std::env::current_dir()?.join(path))
}

// Helper: Teardown worktree
fn teardown_worktree(id: usize) -> Result<()> {
    let dir_name = format!(".koval_worktrees/agent_{}", id);
    let path = PathBuf::from(&dir_name);

    if !path.exists() {
        return Ok(());
    }

    // Try git worktree remove
    let output = Command::new("git")
        .args(&["worktree", "remove", "--force", &dir_name])
        .output()?;

    // If git failed, try manual remove (e.g., if the .git file is gone)
    if !output.status.success() {
        if path.exists() {
            std::fs::remove_dir_all(&path)?;
        }
    }
    
    Ok(())
}