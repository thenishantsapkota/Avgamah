from pydantic import BaseSettings


class BotConfig(BaseSettings):
    token: str

    class Config:
        env_file = ".env"
        env_prefix = "bot_"


bot_config = BotConfig()
