from pydantic import BaseSettings


class ConfigurationParameters(BaseSettings):

    port: int = 8008
    db_address: str
    db_port: int
    db_name: str
    db_username: str
    db_password: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = "fastapi_example/.env"
#        env_file = ".env"


settings = ConfigurationParameters()
