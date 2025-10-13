from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    ECHO_SQL: bool

    REDIS_CONNECTION_STRING: str

    API_KEYS: list[str]
    SECRET_KEY: str
    ALGORITHM: str

    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str

    ENVIRONMENT: str

    ADMIN_EMAILS: list[str] = ["courageadedara@gmail.com", "dennisoduola@gmail.com"]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


class EmailSettings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str

    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


# noinspection PyArgumentList
email_settings_config = EmailSettings()

# noinspection PyArgumentList
settings = Settings()
