# post_to_twitter.py
import os, requests, json

def tweet(text: str) -> dict:
    """Post plain text using the user-access token obtained via OAuth 2 PKCE."""
    token = os.environ["TW_ACCESS_TOKEN"]          # 2-hour token you just saved
    url   = "https://api.twitter.com/2/tweets"
    resp  = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"text": text[:280]},                 # hard cut at 280 chars
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()                             # contains tweet ID & text

# run a quick self-test when you execute the file directly
if __name__ == "__main__":
    print(tweet("TEST tweet via OAuth2 PKCE 🚀  (safe to delete)"))
