import requests
import json
import os
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from database import engine
from config import API_KEY, SYMBOLS, RAW_DATA_DIR
from models import AlphaVantageResponse

os.makedirs(RAW_DATA_DIR, exist_ok=True)

def extract(symbol):
    print(f"Fetching data for {symbol}")
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": API_KEY,
        "outputsize": "compact"
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "Error Message" in data:
        print(f"API error for {symbol}: {data['Error Message']}")
        return None

    try:
        validated = AlphaVantageResponse(**data)
    except Exception as e:
        print(f"Validation error: {e}")
        return None

    filename = f"{RAW_DATA_DIR}/{symbol}_{datetime.today().date()}.json"
    with open(filename, "w") as f:
        json.dump(data, f)
    return validated

def transform(symbol, validated_data):
    records = []
    for date, values in validated_data.TimeSeries.items():
        open_price = values.open
        close_price = values.close
        daily_change = ((close_price - open_price) / open_price) * 100

        records.append({
            "symbol": symbol,
            "date": date,
            "open_price": open_price,
            "high_price": values.high,
            "low_price": values.low,
            "close_price": close_price,
            "volume": values.volume,
            "daily_change_percentage": daily_change,
            "extraction_timestamp": datetime.now().isoformat()
        })
    df = pd.DataFrame(records)
    return df

def load(df):
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS stock_daily_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date TEXT,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                close_price REAL,
                volume INTEGER,
                daily_change_percentage REAL,
                extraction_timestamp TEXT
            )
        """))

        for _, row in df.iterrows():
            result = conn.execute(text("""
                SELECT 1 FROM stock_daily_data
                WHERE symbol = :symbol AND date = :date
            """), {"symbol": row["symbol"], "date": row["date"]}).fetchone()

            if not result:
                conn.execute(text("""
                    INSERT INTO stock_daily_data (
                        symbol, date, open_price, high_price, low_price,
                        close_price, volume, daily_change_percentage, extraction_timestamp
                    ) VALUES (
                        :symbol, :date, :open_price, :high_price, :low_price,
                        :close_price, :volume, :daily_change_percentage, :extraction_timestamp
                    )
                """), row.to_dict())

def run_etl():
    for symbol in SYMBOLS:
        validated = extract(symbol)
        if validated:
            df = transform(symbol, validated)
            load(df)

if __name__ == "__main__":
    run_etl()
