from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Flags

    # App Basics
    app_name: str = Field(default="Coeus", description="Service name")
    app_env: str = Field(
        default="development", description="Env: development|staging|production"
    )
    app_host: str = Field(default="127.0.0.1", description="Bind host for uvicorn")
    app_port: int = Field(default=8000, description="Bind port for uvicorn")
    log_level: str = Field(
        default="INFO", description="Logging level: DEBUG/INFO/WARNING/ERROR"
    )
    debug: bool = Field(default=False, description="Enable verbose debugging features")

    # Ollama
    ollama_url: AnyUrl = Field(
        default="http://127.0.0.1:11434", description="Ollama base URL"
    )
    model_general: str = Field(default="llama3.1:8b", description="General Model Llama")
    model_code: str = Field(default="codellama:7b", description="Code Model Codellama")

    # Optional DB
    database_url: str | None = Field(default=None, description="Optional DB")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


# Create a single instance of Settings to be used throughout the application
settings = Settings()
