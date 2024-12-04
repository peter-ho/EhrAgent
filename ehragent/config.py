def openai_config(model):
    ## refer to configuration example: https://microsoft.github.io/autogen/0.2/docs/reference/oai/client#create
    if model == 'gpt-35-turbo_azure':
        config = {
            "model": "gpt-35-turbo",
            "api_key": "<azure-key>",
            "base_url": "https://ksind-m3ln7i5d-westeurope.openai.azure.com/",
            "api_version": "2024-08-01-preview",
            "api_type": "azure",
        }
    elif model == 'gpt-35-turbo_autogen':
        config = {
            "model": "gpt-35-turbo",
            "api_key": "<azure-key>",
            "base_url": "https://ksind-m3ln7i5d-westeurope.openai.azure.com/openai/deployments/gpt-35-turbo",
            "api_type": "AZURE"
        }
    elif model == 'health_ehragent':
        config = {
            "model": "gpt-4o-mini",
            "api_key": "<azure-key>",
            "api_type": "azure",
            "base_url": "https://ai-peterho4772ai457264831480.openai.azure.com/",
            "api_version": "2024-02-15-preview"
        }
    elif model == 'gpt-4-0613':
        config = {
            "model": "gpt-4",
            "api_key": "<azure-key>",
            "api_type": "azure",
            "base_url": "https://peter-m3vi8tto-canadaeast.openai.azure.com/",
            "api_version": "2024-08-01-preview"
        }
    else:
        config = {
            "test": "openai/deployments/gpt-35-turbo/chat/completions",
            "base_url": "https://ksind-m3ln7i5d-westeurope.openai.azure.com/openai/deployments/gpt-35-turbo",
            "base_url": "https://ksind-m3ln7i5d-westeurope.openai.azure.com/",
            "base_url": "https://ksind-m3ln7i5d-westeurope.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2024-08-01-preview",
            "base_url": "https://ksind-m3ln7i5d-westeurope.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2024-08-01-preview",
            "api_version": "2024-08-01-preview",
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