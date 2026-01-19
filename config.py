import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CREDENTIALS_FILENAME = os.getenv("CREDENTIALS_FILENAME", "credentials.json")
QUESTIONS_SPREADSHEET_URL = os.getenv("QUESTIONS_SPREADSHEET_URL")
ADMIN_IDS = os.getenv("ADMIN_IDS").split()