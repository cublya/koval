import yaml
from pathlib import Path

CONFIG_PATH = Path("koval.yaml")

def load_config():
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def get_model_config(model_name=None):
    config = load_config()
    system_config = config.get("system", {})
    models_config = config.get("models", {})

    if not model_name:
        model_name = system_config.get("default_model", "gpt-4o")

    if model_name in models_config:
        return models_config[model_name]
    else:
        # Fallback or direct string
        return {"model_name": model_name}
