import requests, json
from twitter_refresh import fresh_access_token   # ← add this

def tweet(text: str) -> dict:
    token = fresh_access_token()                 # always fresh
    resp = requests.post(
        "https://api.twitter.com/2/tweets",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"text": text[:280]},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()

# optional quick test
if __name__ == "__main__":
    print(tweet("TEST after refresh helper ✅"))
