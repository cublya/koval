use std::path::PathBuf;
use async_trait::async_trait;
use serde_json::json;
use tokio::fs;
use crate::Tool;

pub struct ReadFileTool {
    work_dir: PathBuf,
}

impl ReadFileTool {
    pub fn new(work_dir: PathBuf) -> Self {
        Self { work_dir }
    }
}

#[async_trait]
impl Tool for ReadFileTool {
    fn name(&self) -> &str {
        "read_file"
    }

    fn description(&self) -> &str {
        "Reads the content of a file."
    }

    fn schema(&self) -> serde_json::Value {
        json!({
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to read."
                }
            },
            "required": ["path"]
        })
    }

    async fn execute(&self, args: serde_json::Value) -> Result<serde_json::Value, String> {
        let path_str = args.get("path")
            .and_then(|v| v.as_str())
            .ok_or("Missing 'path' argument")?;
        
        let path = self.work_dir.join(path_str);
        
        match fs::read_to_string(&path).await {
            Ok(content) => Ok(json!({ "content": content })),
            Err(e) => Err(format!("Failed to read file '{}': {}", path.display(), e)),
        }
    }
}

pub struct WriteFileTool {
    work_dir: PathBuf,
}

impl WriteFileTool {
    pub fn new(work_dir: PathBuf) -> Self {
        Self { work_dir }
    }
}

#[async_trait]
impl Tool for WriteFileTool {
    fn name(&self) -> &str {
        "write_file"
    }

    fn description(&self) -> &str {
        "Writes content to a file. Overwrites existing files."
    }

    fn schema(&self) -> serde_json::Value {
        json!({
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to write."
                },
                "content": {
                    "type": "string",
                    "description": "The content to write."
                }
            },
            "required": ["path", "content"]
        })
    }

    async fn execute(&self, args: serde_json::Value) -> Result<serde_json::Value, String> {
        let path_str = args.get("path")
            .and_then(|v| v.as_str())
            .ok_or("Missing 'path' argument")?;
        
        let content = args.get("content")
            .and_then(|v| v.as_str())
            .ok_or("Missing 'content' argument")?;

        let path = self.work_dir.join(path_str);

        if let Some(parent) = path.parent() {
            if let Err(e) = fs::create_dir_all(parent).await {
                return Err(format!("Failed to create parent directory: {}", e));
            }
        }

        match fs::write(&path, content).await {
            Ok(_) => Ok(json!({ "status": "success", "path": path_str })),
            Err(e) => Err(format!("Failed to write to file '{}': {}", path.display(), e)),
        }
    }
}

pub struct ListDirTool {
    work_dir: PathBuf,
}

impl ListDirTool {
    pub fn new(work_dir: PathBuf) -> Self {
        Self { work_dir }
    }
}

#[async_trait]
impl Tool for ListDirTool {
    fn name(&self) -> &str {
        "list_dir"
    }

    fn description(&self) -> &str {
        "Lists files and directories in a path."
    }

    fn schema(&self) -> serde_json::Value {
        json!({
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The directory path to list. Defaults to current directory if omitted."
                }
            }
        })
    }

    async fn execute(&self, args: serde_json::Value) -> Result<serde_json::Value, String> {
        let default_path = ".".to_string();
        let path_str = args.get("path")
            .and_then(|v| v.as_str())
            .unwrap_or(&default_path);
        
        let path = self.work_dir.join(path_str);
        
        let mut entries = Vec::new();
        
        match fs::read_dir(&path).await {
            Ok(mut dir) => {
                while let Ok(Some(entry)) = dir.next_entry().await {
                    if let Ok(file_name) = entry.file_name().into_string() {
                         let file_type = if let Ok(ft) = entry.file_type().await {
                             if ft.is_dir() { "dir" } else { "file" }
                         } else {
                             "unknown"
                         };
                        entries.push(json!({ "name": file_name, "type": file_type }));
                    }
                }
                Ok(json!({ "entries": entries }))
            }
            Err(e) => Err(format!("Failed to list directory '{}': {}", path.display(), e)),
        }
    }
}