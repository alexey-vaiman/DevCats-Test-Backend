from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Marketplace Prototype API"
    API_V1_STR: str = "/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/marketplace"
    
    # Security
    SECRET_KEY: str = "secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:80",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5173",
    ]
    
    # S3 (MinIO)
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "marketplace-images"
    S3_PUBLIC_URL_PREFIX: str = "http://localhost:9000/marketplace-images"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
