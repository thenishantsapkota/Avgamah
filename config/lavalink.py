from pydantic import BaseSettings


class LavalinkConfig(BaseSettings):
    password: str

    class Config:
        env_file = ".env"
        env_prefix = "lavalink_"


lavalink_config = LavalinkConfig()
