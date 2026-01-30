use clap::{Parser, Subcommand};
use koval_common::Config;
use koval_core::{Agent, Client, Swarm};
use koval_protocol::openai::Message;
use koval_tools::{shell::ShellTool, files::{ReadFileTool, WriteFileTool, ListDirTool}};
use std::io::{self, Write};
use std::sync::Arc;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[command(subcommand)]
    command: Option<Commands>,

    /// Initial prompt to start the conversation (Single Player Mode)
    #[arg(short, long)]
    prompt: Option<String>,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Start the Multi-Agent Swarm
    Swarm {
        /// The goal or task for the swarm
        task: String,
    },
    /// Start Single Player Mode (default)
    Cli,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let args = Args::parse();
    let config = Config::load()?;
    let client = Client::new(&config)?;

    match args.command {
        Some(Commands::Swarm { task }) => {
            let swarm = Swarm::new(config, client);
            swarm.run(&task).await?;
        }
        Some(Commands::Cli) | None => {
            run_cli(config, client, args.prompt).await?;
        }
    }

    Ok(())
}

async fn run_cli(config: Config, client: Client, initial_prompt: Option<String>) -> anyhow::Result<()> {
    let mut agent = Agent::new(config, client);
    let work_dir = std::env::current_dir()?;

    // Register Tools
    agent.register_tool(Arc::new(ShellTool::new(work_dir.clone())));
    agent.register_tool(Arc::new(ReadFileTool::new(work_dir.clone())));
    agent.register_tool(Arc::new(WriteFileTool::new(work_dir.clone())));
    agent.register_tool(Arc::new(ListDirTool::new(work_dir.clone())));

    println!("Welcome to Koval (Rust Edition). Type '/exit' to quit.");

    if let Some(prompt) = initial_prompt {
        println!("User: {}", prompt);
        agent.add_message(Message::user(prompt));
        if let Err(e) = agent.run().await {
            eprintln!("Error: {}", e);
        }
    }

    loop {
        print!("> ");
        io::stdout().flush()?;

        let mut input = String::new();
        if io::stdin().read_line(&mut input).is_err() {
            break;
        }

        let input = input.trim();
        if input == "/exit" || input == "/quit" {
            break;
        }
        if input.is_empty() {
            continue;
        }

        agent.add_message(Message::user(input));

        if let Err(e) = agent.run().await {
            eprintln!("Error: {}", e);
        }
    }
    Ok(())
}