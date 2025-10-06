from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
SYMBOLS = ["AAPL", "GOOG", "MSFT"]
RAW_DATA_DIR = "raw_data"

DB_URL = "sqlite:///stock_data.db"
