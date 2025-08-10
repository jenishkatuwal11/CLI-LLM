from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

class ClientSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLM_", case_sensitive=False)

    base_url: str = Field(default="")
    api_key: str = Field(default="")
    default_model: str = Field(default="")

    http_referer: str = Field(default="")
    x_title: str = Field(default="LLM CLI")

    connect_timeout: float = Field(default=10.0)
    read_timeout: float = Field(default=300.0)

    verbose: bool = Field(default=False)

    def ensure_valid(self) -> None:
        if not self.base_url:
            raise ValueError("LLM_BASE_URL is required. Set it in .env or environment variables.")

class ChatOptions(BaseModel):
    model: Optional[str] = None
    stream: bool = True
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
