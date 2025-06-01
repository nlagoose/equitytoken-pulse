# pulse_runner.py

import time
import requests
from fetch import fetch_rows         # fetch_rows() unchanged
from generate import craft           # now returns {"tweet", "image_file"}
from post_to_twitter import tweet

MIN_MOVE = 2.5   # threshold for percent-change

def run_once():
    # 1. Fetch on-chain data
    rows = fetch_rows()

    # 2. Filter for significant moves
    events = [r for r in rows if abs(r["pct_change"]) >= MIN_MOVE]
    if not events:
        print("No significant moves to tweet.")
        return

    # 3. Pick the top mover
    top = max(events, key=lambda r: abs(r["pct_change"]))

    # 4. Generate text + image via GPT + DALL·E
    copy = craft(top)   # now has {"tweet": "...", "image_file": "image_<token>.png"}

    # 5. Post the tweet with image
    try:
        res = tweet(copy["tweet"], copy["image_file"])
        print(f"✅ Posted: {res['data']['id']} → {copy['tweet']}")
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 429:
            print("⚠️ Hit Twitter rate limit (429). Skipping.")
        else:
            raise

if __name__ == "__main__":
    run_once()
