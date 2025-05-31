import os, requests, time

def fresh_access_token() -> str:
    """
    Return a valid user access token.
    Refreshes automatically if we’re > 90 minutes old (tokens last 120 min).
    """
    issued = int(os.environ.get("TW_AT_ISSUED", "0"))
    if time.time() - issued < 5400:       # < 90 min old → still fresh
        return os.environ["TW_ACCESS_TOKEN"]

    r = requests.post(
        "https://api.twitter.com/2/oauth2/token",
        auth=(os.environ["TW_CLIENT_ID"], os.environ["TW_CLIENT_SECRET"]),
        data={
            "grant_type":    "refresh_token",
            "refresh_token": os.environ["TW_REFRESH_TOKEN"],
        },
        timeout=30,
    )r = requests.post(...)

    # 🔎 print Twitter's own error JSON / text
    if r.status_code != 200:
        print("TWITTER REFRESH ERROR →", r.status_code, r.text)

    r.raise_for_status()

    r.raise_for_status()
    j = r.json()

    # update env (memory) so the rest of this run uses the new token
    os.environ["TW_ACCESS_TOKEN"] = j["access_token"]
    os.environ["TW_REFRESH_TOKEN"] = j["refresh_token"]
    os.environ["TW_AT_ISSUED"]    = str(int(time.time()))
    return j["access_token"]
