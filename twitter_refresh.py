import os, requests, time

def fresh_access_token() -> str:
    issued_at = int(os.environ.get("TW_AT_ISSUED", "0"))
    if time.time() - issued_at < 5400:          # < 90 min old → still valid
        return os.environ["TW_ACCESS_TOKEN"]

    r = requests.post(
        "https://api.twitter.com/2/oauth2/token",
        auth=(os.environ["TW_CLIENT_ID"], os.environ["TW_CLIENT_SECRET"]),
        data={
            "grant_type":    "refresh_token",
            "refresh_token": os.environ["TW_REFRESH_TOKEN"],
        },
        timeout=30,
    )

    # ── DEBUG: print Twitter’s error if it isn’t 200
    if r.status_code != 200:
        print("\n🔴 TWITTER REFRESH ERROR →", r.status_code, r.text)

    r.raise_for_status()
    data = r.json()

    # Extract the new tokens
    new_access  = data["access_token"]
    new_refresh = data["refresh_token"]

    # Update in-memory for this run
    os.environ["TW_ACCESS_TOKEN"]  = new_access
    os.environ["TW_REFRESH_TOKEN"] = new_refresh
    os.environ["TW_AT_ISSUED"]     = str(int(time.time()))

    # ── WRITE the new refresh token to a file for later steps
    with open("new_refresh_token.txt", "w") as f:
        f.write(new_refresh)

    return new_access
