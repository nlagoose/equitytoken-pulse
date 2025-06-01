# fetch.py

import os
import requests
import json

API   = "https://api.dune.com/api/v1/"
QID   = os.environ["DUNE_QUERY_ID"]
HEAD  = {"X-DUNE-API-KEY": os.environ["DUNE_API_KEY"]}


def fetch_rows():
    """
    Call Dune’s /query/{QID}/results endpoint and return the list of rows.
    The rows are under resp["result"]["rows"] based on your sample output.
    """
    url = f"{API}query/{QID}/results"
    r = requests.get(url, headers=HEAD, timeout=30)
    r.raise_for_status()
    resp = r.json()

    # ── Your fetch output shows "result" at top level:
    if "result" in resp and "rows" in resp["result"]:
        return resp["result"]["rows"]

    # ── Fallback to old shapes if needed later:
    if "data" in resp and "get_query_result" in resp["data"]:
        return resp["data"]["get_query_result"]["rows"]
    if "data" in resp and "get_query_data" in resp["data"]:
        return resp["data"]["get_query_data"]["result"]["rows"]

    # ── If nothing matches, print payload and abort
    print("\n❌ Unexpected Dune response shape:\n")
    print(json.dumps(resp, indent=2))
    raise RuntimeError("Cannot find row data in Dune response—see above payload")


def detect(rows):
    """
    Given a list of rows, return simplified event dicts with keys:
      - type, token, pct, usd_24h
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
    # Local sanity-check
    rows = fetch_rows()
    events = detect(rows)
    print(json.dumps(events, indent=2))
