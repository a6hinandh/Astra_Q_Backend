import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import schedule # type: ignore
import time
from mosdac_full_extractor import main as run_full_extractor

# Run immediately when started
print("🚀 Starting initial scrape...")
run_full_extractor()
print("✅ Initial scrape completed!")

# Schedule every hour
schedule.every().hour.do(run_full_extractor)

print("🔄 MOSDAC Full Extractor is running (Ctrl+C to stop)...")
print("📅 Will scrape and update data every hour")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute