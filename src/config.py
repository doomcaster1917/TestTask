import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

TELEGRAM_ID = os.environ.get("TELEGRAM_ID")
FIRST_NAME = os.environ.get("FIRST_NAME")
LAST_NAME = os.environ.get("LAST_NAME")
USER_TG_NAME = os.environ.get("USER_TG_NAME")


