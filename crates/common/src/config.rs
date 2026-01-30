use serde::Deserialize;
use anyhow::Result;
use config::{Config as ConfigLoader, Environment};

#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    pub openai_base_url: String,
    pub openai_api_key: String,
    pub model: String,
    pub max_workers: usize,
}

impl Config {
    pub fn load() -> Result<Self> {
        let mut builder = ConfigLoader::builder();

        // One primary URL: LiteLLM Proxy default
        builder = builder
            .set_default("openai_base_url", "http://localhost:4000/v1")?
            .set_default("openai_api_key", "sk-1234")?
            .set_default("model", "gpt-4o")?
            .set_default("max_workers", 4)?;

        // Allow overrides via KOVAL_* environment variables
        builder = builder.add_source(Environment::with_prefix("KOVAL"));

        let config = builder.build()?;
        Ok(config.try_deserialize()?)
    }
}