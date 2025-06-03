# pulse_runner.py

import os
import json
from fetch import detect, fetch_rows
from generate import craft
from post_to_twitter_v2 import tweet_v2 as tweet

def run_once():
    # 1) Fetch raw rows from Dune
    rows = fetch_rows()

    # 2) Detect all “events” (volume moves etc.)
    events = detect(rows)

    # 3) If no events, nothing to do
    if not events:
        print("❌ No events detected—nothing to tweet.")
        return

    # 4) Take up to the first 3 events
    to_post = events[:3]

    for idx, event in enumerate(to_post, start=1):
        print(f"\n── Crafting tweet #{idx} for token {event['token']} ──")
        copy = craft(event)

        text       = copy["tweet"]
        image_file = copy["image_file"]

        # 5) Post the tweet (text + optional image) via v2 endpoints
        try:
            resp = tweet(text, image_file)
            tweet_id = resp["data"]["id"]
            print(f"✅ Posted tweet #{idx}: {tweet_id} → {repr(text[:60] + '…')}")
        except Exception as e:
            print(f"❌ Failed to post tweet #{idx}:", e)

if __name__ == "__main__":
    run_once()
