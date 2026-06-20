import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

APP_NAME = "PredictHood"
VERSION = "1.0.0"
