use koval_common::Config;
use koval_protocol::openai::{ChatCompletionRequest, ChatCompletionChunk, Message, Role};
use anyhow::{Result, Context};
use futures::Stream;
use reqwest::header::{AUTHORIZATION, CONTENT_TYPE, HeaderMap, HeaderValue};
use futures::StreamExt;

#[derive(Clone)]
pub struct Client {
    http: reqwest::Client,
    base_url: String,
}

impl Client {
    pub fn new(config: &Config) -> Result<Self> {
        let mut headers = HeaderMap::new();
        let mut auth_val = HeaderValue::from_str(&format!("Bearer {}", config.openai_api_key))?;
        auth_val.set_sensitive(true);
        headers.insert(AUTHORIZATION, auth_val);
        headers.insert(CONTENT_TYPE, HeaderValue::from_static("application/json"));

        let http = reqwest::Client::builder()
            .default_headers(headers)
            .build()?;

        Ok(Self {
            http,
            base_url: config.openai_base_url.trim_end_matches('/').to_string(),
        })
    }

    /// Primary endpoint for streaming chat completions
    pub async fn chat_stream(
        &self,
        req: ChatCompletionRequest,
    ) -> Result<impl Stream<Item = Result<ChatCompletionChunk>>> {
        let url = format!("{}/chat/completions", self.base_url);
        
        let res = self.http.post(&url)
            .json(&req)
            .send()
            .await
            .context("Failed to send request to LLM provider")?;

        if !res.status().is_success() {
             let text = res.text().await?;
             anyhow::bail!("LLM API Error: {}", text);
        }

        let stream = res.bytes_stream()
            .map(|result| {
                match result {
                    Ok(bytes) => {
                        let s = String::from_utf8_lossy(&bytes);
                        let mut chunks = Vec::new();
                        for line in s.lines() {
                            if line.starts_with("data: ") {
                                let data = &line[6..];
                                if data == "[DONE]" {
                                    continue;
                                }
                                if let Ok(chunk) = serde_json::from_str::<ChatCompletionChunk>(data) {
                                    chunks.push(Ok(chunk));
                                }
                            }
                        }
                        futures::stream::iter(chunks)
                    },
                    Err(e) => futures::stream::iter(vec![Err(anyhow::anyhow!(e))]),
                }
            })
            .flatten();

        Ok(stream)
    }

    /// Non-streaming chat completion helper
    pub async fn chat(&self, req: ChatCompletionRequest) -> Result<Message> {
        let mut stream = self.chat_stream(req).await?;
        let mut content = String::new();
        let mut role = Role::Assistant;

        while let Some(chunk_res) = stream.next().await {
            let chunk = chunk_res?;
            if let Some(choice) = chunk.choices.first() {
                if let Some(c) = &choice.delta.content {
                    content.push_str(c);
                }
                if let Some(r) = &choice.delta.role {
                    role = r.clone();
                }
            }
        }

        Ok(Message {
            role,
            content: Some(content),
            tool_calls: None,
            tool_call_id: None,
            name: None,
        })
    }
}
