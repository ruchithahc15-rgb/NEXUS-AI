
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    nexus_db_password: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

DB_CONFIG = {
    "username": "postgres",
    "password": settings.nexus_db_password,
    "host": "localhost",
    "port": 5432,
    "database": "nexus_ai"
}

database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_CONFIG["username"],
    password=DB_CONFIG["password"],
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
    database=DB_CONFIG["database"]
)

engine = create_engine(
    database_url,
    pool_pre_ping=True
)
