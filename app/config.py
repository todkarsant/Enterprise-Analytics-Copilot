from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "local"
    db_backend: str = "sqlite"
    sqlite_path: str = "data/analytics.db"
    postgres_dsn: str = "postgresql+psycopg://analytics:analytics@localhost:5432/analytics"
    llm_provider: str = "mock"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3"
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2025-01-01-preview"
    azure_openai_deployment: str = ""
    max_result_rows: int = 50
    max_sql_length: int = 4000
    max_repair_attempts: int = 2
    schema_top_k: int = 6
    query_timeout_seconds: int = 20
    cache_ttl_seconds: int = 300
    cost_per_1k_input_tokens_usd: float = 0.0
    cost_per_1k_output_tokens_usd: float = 0.0
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
