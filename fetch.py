# fetch.py

import os
import requests
import json

API   = "https://api.dune.com/api/v1/"
QID   = os.environ["DUNE_QUERY_ID"]
HEAD  = {"X-DUNE-API-KEY": os.environ["DUNE_API_KEY"]}


def fetch_rows():
    """
    Call Dune’s “query results” endpoint and return the list of rows.
    Adjust the JSON‐path below if your Dune response uses different field names.
    """
    url = f"{API}query/{QID}/results"
    r = requests.get(url, headers=HEAD, timeout=30)
    r.raise_for_status()
    resp = r.json()

    # ── Depending on your Dune API version, the rows may live under:
    # resp["data"]["get_query_result"]["rows"]
    # or resp["data"]["get_query_data"]["result"]["rows"]
    #
    # Inspect your actual Dune response if this key is wrong. For many setups, it’s:
    #
    #    resp["data"]["get_query_result"]["rows"]
    #
    try:
        return resp["data"]["get_query_result"]["rows"]
    except KeyError:
        # fallback if the structure is slightly different
        return resp["data"]["get_query_data"]["result"]["rows"]


def detect(rows):
    """
    Given a list of rows (each row is a dict with keys including 'pct_change'),
    return a list of simplified event dicts.
    """
    events = []
    for r in rows:
        if r.get("pct_change") is not None and abs(r["pct_change"]) > 0:
            events.append({
                "type": "volume_move",
                "token": r["symbol"],
                "pct": round(r["pct_change"], 2),
                "usd_24h": round(r["rolling_24h"] / 1e6, 2)
            })
    return events


if __name__ == "__main__":
    # Quick local sanity check
    rows = fetch_rows()
    events = detect(rows)
    print(json.dumps(events, indent=2))
