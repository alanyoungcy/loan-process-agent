from pydantic_settings import BaseSettings
from typing import List, Union


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Loan Agent Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://admin:change-me@localhost:5432/loan_agent"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://admin:change-me@localhost:5672/"

    # External Services
    CAMUNDA_DMN_URL: str = "http://localhost:8081"
    DROOLS_URL: str = "http://localhost:8081"  # Backward compatibility - now points to Camunda DMN

    # Camunda 8 Services
    ZEEBE_GATEWAY_ADDRESS: str = "localhost:26500"
    CAMUNDA_OPERATE_URL: str = "http://localhost:8080"
    CAMUNDA_TASKLIST_URL: str = "http://localhost:8082"
    CAMUNDA_OPTIMIZE_URL: str = "http://localhost:8083"
    CAMUNDA_CONNECTORS_URL: str = "http://localhost:8085"

    CHROMADB_URL: str = "http://localhost:8100"
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8100

    # JWT
    SECRET_KEY: str = "change-me-in-local-env"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:5173"
    ]

    # GenAI - OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"

    # GenAI - Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_BASE_URL: str = "https://api.anthropic.com"
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # GenAI - Default Provider
    DEFAULT_LLM_PROVIDER: str = "openai"  # openai or anthropic

    # Task Queue
    TASK_TIMEOUT: int = 300  # 5 minutes
    MAX_RETRIES: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = True

    def model_post_init(self, __context):
        """Convert CORS_ORIGINS string to list if needed"""
        if isinstance(self.CORS_ORIGINS, str):
            self.CORS_ORIGINS = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
