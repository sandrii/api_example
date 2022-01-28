from pydantic import BaseSettings


class ConfigurationParameters(BaseSettings):

    db_address: str
    db_port: int
    db_name: str
    db_username: str
    db_password: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = "app/.env"


settings = ConfigurationParameters()
