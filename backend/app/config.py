from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator


_INSECURE_DEFAULT = "change-me-in-production"


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    database_url: str = "sqlite:///./storage.db"
    secret_key: str = _INSECURE_DEFAULT
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    upload_dir: str = "./uploads"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_bucket_name: str = ""
    aws_region: str = "us-east-1"

    @field_validator("secret_key")
    @classmethod
    def secret_key_must_be_set(cls, v: str) -> str:
        if v == _INSECURE_DEFAULT:
            import warnings
            warnings.warn(
                "SECRET_KEY is set to the insecure default value. "
                "Set the SECRET_KEY environment variable before deploying to production.",
                stacklevel=2,
            )
        return v


settings = Settings()
