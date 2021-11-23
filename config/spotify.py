from pydantic import BaseSettings


class SpotifyConfig(BaseSettings):
    client_id: str
    client_secret: str

    class Config:
        env_file = ".env"
        env_prefix = "spotify_"


spotify_config = SpotifyConfig()
