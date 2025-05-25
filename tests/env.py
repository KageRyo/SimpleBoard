import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "dev", "localtest.env")
load_dotenv(dotenv_path)
