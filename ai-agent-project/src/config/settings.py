from pydantic import BaseSettings

class Settings(BaseSettings):
    llm_model: str
    mcp_host: str
    mcp_port: int

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()