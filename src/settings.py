import string
from pathlib import Path

from pydantic_settings import BaseSettings

ROOT_PATH = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_mode: str = "production"
    data_path: Path = ROOT_PATH / "data"
    min_password_length: int = 5
    stop_probability: float = 0.125

    alphabet: str = string.ascii_letters + string.digits + "!@#%&*()"
    alphabet_size: int = alphabet.__len__()
    default_steps: int = 1000

    green_color: str = "\033[92m"
    yellow_color: str = "\033[93m"
    reset_color: str = "\033[0m"

    class Config:
        env_file = str(ROOT_PATH / "config.env")


settings = Settings()
