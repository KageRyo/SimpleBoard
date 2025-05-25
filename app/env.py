import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "dev", "local.env")
load_dotenv(dotenv_path)

def get_env(key: str, default=None):
    return os.environ.get(key, default)
