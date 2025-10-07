from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Create a single instance of Settings to be used throughout the application
settings = Settings()


class Settings(BaseSettings):
    #Flags
    debug: bool = Field(default=False, description="Enable verbose logging / debug toggles")
    
    #Ollama
    ollama_url: AnyUrl = Field(default="http://localhost:11434", description="Ollama base URL")
    model_general: str = Field(default="llama3.1:8b", description="General Model Llama")
    model_code: str = Field(default="codellama:7b", description="Code Model Codellama")
    
    #Optional DB
    database_url: str | None = Field(default=None, description="Optional DB")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )