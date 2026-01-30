use crate::Client;
use anyhow::Result;
use futures::StreamExt;
use koval_common::Config;
use koval_protocol::openai::{
    ChatCompletionRequest, Function, Message, Role, ToolCall, ToolDefinition, FunctionDefinition,
};
use koval_tools::Tool;
use std::collections::HashMap;
use std::sync::Arc;
use std::io::{self, Write};

pub struct Agent {
    client: Client,
    config: Config,
    pub history: Vec<Message>,
    tools: Vec<Arc<dyn Tool>>,
}

impl Agent {
    pub fn new(config: Config, client: Client) -> Self {
        Self {
            client,
            config,
            history: Vec::new(),
            tools: Vec::new(),
        }
    }

    pub fn register_tool(&mut self, tool: Arc<dyn Tool>) {
        self.tools.push(tool);
    }

    pub fn add_message(&mut self, message: Message) {
        self.history.push(message);
    }

    pub async fn run(&mut self) -> Result<()> {
        loop {
            // Prepare tools definition
            let tool_definitions: Option<Vec<ToolDefinition>> = if self.tools.is_empty() {
                None
            } else {
                Some(
                    self.tools
                        .iter()
                        .map(|t| ToolDefinition {
                            kind: "function".to_string(),
                            function: FunctionDefinition {
                                name: t.name().to_string(),
                                description: Some(t.description().to_string()),
                                parameters: t.schema(),
                            },
                        })
                        .collect(),
                )
            };

            let request = ChatCompletionRequest {
                model: self.config.model.clone(),
                messages: self.history.clone(),
                tools: tool_definitions,
                stream: true,
            };

            let mut stream = self.client.chat_stream(request).await?;

            let mut accumulated_content = String::new();
            // Map index -> (id, function_name, arguments_buffer)
            let mut pending_tools: HashMap<i32, (String, String, String)> = HashMap::new();

            print!("Assistant: ");
            io::stdout().flush()?;

            while let Some(chunk_result) = stream.next().await {
                let chunk = chunk_result?;
                if let Some(choice) = chunk.choices.first() {
                    let delta = &choice.delta;

                    // Handle Content
                    if let Some(content) = &delta.content {
                        print!("{}", content);
                        io::stdout().flush()?;
                        accumulated_content.push_str(content);
                    }

                    // Handle Tool Calls
                    if let Some(tool_calls) = &delta.tool_calls {
                        for tool_call in tool_calls {
                            let index = tool_call.index;
                            let entry = pending_tools.entry(index).or_insert((
                                String::new(),
                                String::new(),
                                String::new(),
                            ));

                            if let Some(id) = &tool_call.id {
                                entry.0 = id.clone();
                            }
                            
                            if let Some(function) = &tool_call.function {
                                if let Some(name) = &function.name {
                                    entry.1.push_str(name);
                                }
                                if let Some(args) = &function.arguments {
                                    entry.2.push_str(args);
                                }
                            }
                        }
                    }
                    
                    if choice.finish_reason.is_some() {
                        println!(); // Newline after stream ends
                    }
                }
            }

            // Construct final Assistant Message
            let mut final_tool_calls = Vec::new();
            // Sort by index to maintain order
            let mut sorted_indices: Vec<i32> = pending_tools.keys().cloned().collect();
            sorted_indices.sort();

            for index in sorted_indices {
                let (id, name, args) = pending_tools.remove(&index).unwrap();
                if !name.is_empty() {
                    final_tool_calls.push(ToolCall {
                        id,
                        kind: "function".to_string(),
                        function: Function {
                            name,
                            arguments: args,
                        },
                    });
                }
            }

            let assistant_msg = Message {
                role: Role::Assistant,
                content: if accumulated_content.is_empty() { None } else { Some(accumulated_content) },
                tool_calls: if final_tool_calls.is_empty() { None } else { Some(final_tool_calls.clone()) },
                tool_call_id: None,
                name: None,
            };

            self.history.push(assistant_msg);

            // Execute Tools if any
            if !final_tool_calls.is_empty() {
                for call in final_tool_calls {
                    let tool_name = call.function.name;
                    let tool_args = call.function.arguments;
                    let call_id = call.id;

                    println!("> Executing tool: {} with args: {}", tool_name, tool_args);

                    let tool = self.tools.iter().find(|t| t.name() == tool_name);
                    
                    let result_content = match tool {
                        Some(t) => {
                            match serde_json::from_str::<serde_json::Value>(&tool_args) {
                                Ok(args_value) => {
                                    match t.execute(args_value).await {
                                        Ok(res) => res.to_string(),
                                        Err(e) => format!("Error: {}", e),
                                    }
                                }
                                Err(e) => format!("Error parsing arguments: {}", e),
                            }
                        }
                        None => format!("Error: Tool '{}' not found.", tool_name),
                    };

                    println!("> Result: {}", result_content);

                    self.history.push(Message {
                        role: Role::Tool,
                        content: Some(result_content),
                        tool_calls: None,
                        tool_call_id: Some(call_id),
                        name: Some(tool_name),
                    });
                }
                // Loop continues to send tool results back to LLM
            } else {
                // No tool calls, turn finished (waiting for user input)
                break;
            }
        }

        Ok(())
    }
}