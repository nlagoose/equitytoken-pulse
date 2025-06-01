# pulse_runner.py

import time
import requests
from fetch import fetch_rows         # your Dune data helper
from generate import craft           # generates GPT copy
from post_to_twitter import tweet    # posts to Twitter (auto-refreshing)

MIN_MOVE = 2.5   # only tweet if abs(pct_change) ≥ 2.5%

def run_once():
    # 1. Fetch on-chain data
    rows = fetch_rows()

    # 2. Filter for significant moves
    events = [r for r in rows if abs(r["pct_change"]) >= MIN_MOVE]
    if not events:
        print("No significant moves to tweet.")
        return

    # 3. Pick the single top event by absolute percent change
    top = max(events, key=lambda r: abs(r["pct_change"]))

    # 4. Generate the tweet copy with GPT
    copy = craft(top)   # returns a dict with "tweet" (≤280 chars)

    # 5. Attempt to post the one tweet, catching 429 if rate-limited
    try:
        res = tweet(copy["tweet"])
        print(f"✅ Posted: {res['data']['id']} → {copy['tweet']}")
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 429:
            print("⚠️ Hit Twitter rate limit (429). Skipping tweet.")
        else:
            raise

if __name__ == "__main__":
    run_once()
