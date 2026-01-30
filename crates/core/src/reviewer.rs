use crate::Agent;
use crate::Client;
use koval_common::Config;
use koval_protocol::openai::Message;
use koval_tools::{shell::ShellTool, files::{ReadFileTool, ListDirTool}};
use std::path::PathBuf;
use std::sync::Arc;
use anyhow::Result;

pub struct Reviewer {
    agent: Agent,
    work_dir: PathBuf,
}

impl Reviewer {
    pub fn new(config: Config, client: Client, work_dir: PathBuf) -> Self {
        let mut agent = Agent::new(config, client);
        
        // Give Reviewer tools to verify work
        agent.register_tool(Arc::new(ShellTool::new(work_dir.clone())));
        agent.register_tool(Arc::new(ReadFileTool::new(work_dir.clone())));
        agent.register_tool(Arc::new(ListDirTool::new(work_dir.clone())));

        // System Prompt: The Lead/Reviewer Persona
        let system_msg = Message::system(format!(
            "You are the Lead Reviewer and Planner.
            Your job is to verify that the sub-agent has correctly completed their assigned task.
            
            You are working in: {:?}
            
            1. Analyze the task description.
            2. Explore the files or run tests to verify correctness.
            3. If the work is correct, respond with exactly 'APPROVED'.
            4. If the work is incorrect or incomplete, explain what is wrong and provide specific instructions to fix it.
            
            Do not fix it yourself. Your job is to Review.",
            work_dir
        ));
        agent.add_message(system_msg);

        Self {
            agent,
            work_dir,
        }
    }

    /// Detects the project type and returns an appropriate test command.
    pub fn detect_test_command(&self) -> String {
        if self.work_dir.join("Cargo.toml").exists() {
            return "cargo test".to_string();
        }
        if self.work_dir.join("package.json").exists() {
            if self.work_dir.join("yarn.lock").exists() {
                return "yarn test".to_string();
            }
            if self.work_dir.join("pnpm-lock.yaml").exists() {
                return "pnpm test".to_string();
            }
            return "npm test".to_string();
        }
        if self.work_dir.join("pyproject.toml").exists() || self.work_dir.join("requirements.txt").exists() {
            return "python3 -m pytest".to_string();
        }
        // Fallback default
        "python3 -m pytest".to_string()
    }

    /// Reviews the task. Returns (approved: bool, feedback: String).
    pub async fn review(&mut self, task: &str) -> Result<(bool, String)> {
        // Hint the reviewer about how to test
        let suggested_cmd = self.detect_test_command();
        
        let prompt = format!(
            "The sub-agent reports that the task '{}' is complete.
            Please verify this.
            
            Suggested verification command based on file structure: '{}'.
            You may run this command or check files manually.
            
            Is the task completed correctly?
            Response must start with 'APPROVED' if good.", 
            task, suggested_cmd
        );

        self.agent.add_message(Message::user(prompt));

        // Run the agent loop
        self.agent.run().await?;

        // Inspect the last message
        if let Some(last_msg) = self.agent.history.last() {
            if let Some(content) = &last_msg.content {
                let content = content.trim();
                if content.contains("APPROVED") {
                    return Ok((true, content.to_string()));
                } else {
                    return Ok((false, content.to_string()));
                }
            }
        }

        Ok((false, "Reviewer provided no output.".to_string()))
    }
}