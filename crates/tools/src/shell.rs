use crate::Tool;
use async_trait::async_trait;
use serde_json::{json, Value};
use tokio::process::Command;
use std::path::PathBuf;

pub struct ShellTool {
    work_dir: PathBuf,
}

impl ShellTool {
    pub fn new(work_dir: PathBuf) -> Self {
        Self { work_dir }
    }
}

#[derive(serde::Deserialize)]
struct ShellArgs {
    command: String,
}

#[async_trait]
impl Tool for ShellTool {
    fn name(&self) -> &str {
        "run_shell_command"
    }

    fn description(&self) -> &str {
        "Executes a shell command on the local machine."
    }

    fn schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute (e.g. 'ls -la', 'grep pattern file')"
                }
            },
            "required": ["command"]
        })
    }

    async fn execute(&self, args: Value) -> Result<Value, String> {
        let shell_args: ShellArgs = serde_json::from_value(args)
            .map_err(|e| format!("Invalid arguments: {}", e))?;
        
        let output = Command::new("sh")
            .current_dir(&self.work_dir)
            .arg("-c")
            .arg(&shell_args.command)
            .output()
            .await
            .map_err(|e| format!("Failed to execute command: {}", e))?;

        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);

        Ok(json!({
            "exit_code": output.status.code(),
            "stdout": stdout,
            "stderr": stderr
        }))
    }
}
