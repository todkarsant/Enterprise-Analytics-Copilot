from app.config import get_settings
from app.services.llm import AzureOpenAIProvider, LLMProvider, MockProvider, OllamaProvider

def get_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider == "ollama":
        return OllamaProvider(settings.ollama_base_url, settings.ollama_model)
    if settings.llm_provider == "azure_openai":
        return AzureOpenAIProvider(
            settings.azure_openai_endpoint,
            settings.azure_openai_api_key,
            settings.azure_openai_api_version,
            settings.azure_openai_deployment,
        )
    return MockProvider()
