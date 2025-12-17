# Placeholder

# core/config/settings.py
from pydantic import BaseSettings, Field
from typing import List

class Settings(BaseSettings):
    # App
    app_name: str = "agentic-rag"
    env: str = Field(default="dev", description="Environment: dev/staging/prod")
    log_level: str = Field(default="INFO", description="Logging level")

    # Data
    data_root: str = Field(default="./data/raw", description="Read-only data directory")

    # Sandbox
    sandbox_timeout_sec: int = Field(default=8, description="Max execution time for code")
    allowed_libs: List[str] = ["pandas", "polars", "csv", "pathlib", "json", "openpyxl"]

    # LLM
    llm_model: str = Field(default="your-llm-name", description="Model identifier")
    llm_temperature: float = Field(default=0.2, description="Deterministic codegen")

    # MLflow (wired later)
    mlflow_tracking_uri: str = Field(default="file:./mlruns")
    mlflow_experiment: str = Field(default="agentic_rag_dev")

    class Config:
        env_file = f"core/config/env/.env"
        env_file_encoding = "utf-8"

settings = Settings()

