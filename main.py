import os, requests, json, pprint

API_KEY = os.environ["DUNE_API_KEY"]
QID     = os.environ["DUNE_QUERY_ID"]

import os, requests, json

API_KEY = os.environ["DUNE_API_KEY"]
QID     = os.environ["DUNE_QUERY_ID"]

def fetch_rows():
    url = f"https://api.dune.com/api/v1/query/{QID}/results"
    r   = requests.get(
            url,
            headers={"X-Dune-API-Key": API_KEY},
            params={"limit": 20}          # grab up to 20 rows
        )
    r.raise_for_status()
    return r.json()["result"]["rows"]

# ---------- NEW code starts here ----------

def detect(rows):
    """Turn raw rows into simpler event objects."""
    events = []
    for r in rows:
        if r["pct_change"] is not None:         # accept every row for now
            events.append({
                "type": "volume_move",
                "token": r["symbol"],
                "pct":  round(r["pct_change"], 2),
                "usd_24h": round(r["rolling_24h"] / 1e6, 2)
            })
    return events

if __name__ == "__main__":
    rows   = fetch_rows()       # pull raw data
    events = detect(rows)       # transform
    print(json.dumps(events, indent=2))   # pretty-print JSON
