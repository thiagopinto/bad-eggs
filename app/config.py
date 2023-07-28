from typing import List, Union
from pydantic import BaseSettings, AnyHttpUrl, validator
from functools import lru_cache

class Settings(BaseSettings):
    #PATH
    APP_NAME: str
    APP_URL: str
    API_PREFIX: str
    #CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    #DATABASE
    DATABASE_PROVIDER: str
    DATABASE_PROVIDER: str
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASS: str
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_DEBUG_MODE: bool
    DATABASE_CLEAR: bool
    #JWT
    TOKEN_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    #MAIL
    MAIL_MAILER: str
    MAIL_HOST: str
    MAIL_PORT: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_ENCRYPTION: str

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()