def openai_config(model):
    if model == '<YOUR_OWN_GPT_MODEL_I>':
        config = {
            "model": "davinci-002",
            "api_key": "<API_KEY>",
            "base_url": "<BASE_URL>",
            "api_version": "1",
        }
    elif model == 'gpt-35-turbo':
        config = {
            "model": "gpt-35-turbo",
            "api_key": "<API_KEY>",
            "base_url": "<BASE_URL>",
            "api_version": "2024-08-01-preview",
        }
    else:
        config = {
            "test": "openai/deployments/gpt-35-turbo/chat/completions"
        }
    return config

def llm_config_list(seed, config_list):
    llm_config_list = {
        "functions": [
            {
                "name": "python",
                "description": "run the entire code and return the execution result. Only generate the code.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cell": {
                            "type": "string",
                            "description": "Valid Python code to execute.",
                        }
                    },
                    "required": ["cell"],
                },
            },
        ],
        "config_list": config_list,
        "timeout": 120,
        "cache_seed": seed,
        "temperature": 0,
    }
    return llm_config_list