# twitter_refresh.py
import os, requests, time

def fresh_access_token() -> str:
    """
    Return a valid user access token for the Twitter/X API.
    If the cached token is older than 90 minutes, refresh it via the
    OAuth 2 refresh-token flow and update the environment variables in-memory.
    """
    issued_at = int(os.environ.get("TW_AT_ISSUED", "0"))
    if time.time() - issued_at < 5400:          # < 90 min old → still good
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
    # DEBUG printing for future: uncomment if you need to see errors
    # if r.status_code != 200:
    #     print("TWITTER REFRESH ERROR →", r.status_code, r.text)

    r.raise_for_status()
    data = r.json()

    # store new tokens in this process; Actions env lasts only for this run
    os.environ["TW_ACCESS_TOKEN"]  = data["access_token"]
    os.environ["TW_REFRESH_TOKEN"] = data["refresh_token"]
    os.environ["TW_AT_ISSUED"]     = str(int(time.time()))
    return data["access_token"]
