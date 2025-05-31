# pulse_runner.py
from main import fetch_rows, detect   # ← use the file that actually holds the functions
         # your data helpers
from generate import craft                    # GPT copy helper
from post_to_twitter import tweet             # tweet helper
import time, json

EVENT_LIMIT = 3          # tweet at most N events per run
MIN_MOVE    = 1.0        # ignore pct_change smaller than this

def run_once():
    rows   = fetch_rows()
    events = [e for e in detect(rows) if abs(e["pct"]) >= MIN_MOVE]

    if not events:
        print("Nothing interesting right now.")
        return

    for ev in events[:EVENT_LIMIT]:
        copy = craft(ev)["tweet"]
        res  = tweet(copy)
        print("✅ Posted:", res["data"]["id"], "→", copy)
        time.sleep(2)    # polite spacing for API rate-limits

if __name__ == "__main__":
    run_once()
