use crate::Client;
use koval_common::Config;
use koval_protocol::openai::{ChatCompletionRequest, Message};
use serde_json::Value;
use anyhow::{anyhow, Result};

pub struct Planner {
    client: Client,
    config: Config,
}

impl Planner {
    pub fn new(config: Config, client: Client) -> Self {
        Self { client, config }
    }

    pub async fn plan(&self, goal: &str) -> Result<Vec<String>> {
        let system_prompt = r#"
You are a Senior Technical Project Manager.
Your goal is to break down a high-level user request into a list of specific, isolated, actionable coding tasks.
Each task must be clear enough for a junior developer to execute independently.

Return the result strictly as a JSON list of strings.
Do not include markdown formatting or explanation.
Example: ["Create utils.rs file", "Add unit tests for utils.rs", "Update main.rs"]
"#;

        let request = ChatCompletionRequest {
            model: self.config.model.clone(),
            messages: vec![
                Message::system(system_prompt),
                Message::user(goal),
            ],
            tools: None,
            stream: true, // We still use stream internally but call 'chat' which collects it
        };

        let response = self.client.chat(request).await?;
        let full_content = response.content.unwrap_or_default();

        // Clean up markdown code blocks if present
        let clean_content = full_content
            .trim()
            .trim_start_matches("```json")
            .trim_start_matches("```")
            .trim_end_matches("```")
            .trim();

        let parsed: Value = serde_json::from_str(clean_content)
            .map_err(|e| anyhow!("Failed to parse planner JSON: {}. Content: {}", e, clean_content))?;

        if let Some(arr) = parsed.as_array() {
            let tasks: Vec<String> = arr.iter()
                .filter_map(|v| v.as_str().map(|s| s.to_string()))
                .collect();
            
            if tasks.is_empty() {
                Ok(vec![goal.to_string()]) // Fallback
            } else {
                Ok(tasks)
            }
        } else if let Some(obj) = parsed.as_object() {
             // Handle {"tasks": [...]} case
             if let Some(val) = obj.values().find(|v| v.is_array()) {
                 let tasks: Vec<String> = val.as_array().unwrap().iter()
                    .filter_map(|v| v.as_str().map(|s| s.to_string()))
                    .collect();
                 Ok(tasks)
             } else {
                 Ok(vec![goal.to_string()])
             }
        } else {
            Ok(vec![goal.to_string()])
        }
    }
}
