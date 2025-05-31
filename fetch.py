import os, requests, json

API   = "https://api.dune.com/api/v1/"
QID   = os.environ["DUNE_QUERY_ID"]
HEAD  = {"X-DUNE-API-KEY": os.environ["DUNE_API_KEY"]}

def detect(rows):                       # ① NEW helper
    events = []
    for r in rows:
        if r["pct_change"] is not None and abs(r["pct_change"]) > 0:  # always hits
            events.append({
                "type": "volume_move",
                "token": r["symbol"],
                "pct": round(r["pct_change"], 2),
                "usd_24h": round(r["rolling_24h"] / 1e6, 2)
            })
    return events

if __name__ == "__main__":              # ② replace the old main
    rows = fetch_rows()
    events = detect(rows)
    print(json.dumps(events, indent=2))  # ③ pretty JSON print
