import schedule
import time
from etl_pipeline import run_etl

schedule.every().day.at("18:00").do(run_etl)

print("Scheduler is running. Press Ctrl+C to exit.")
while True:
    schedule.run_pending()
    time.sleep(60)
