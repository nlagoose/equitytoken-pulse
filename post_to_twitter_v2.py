# post_to_twitter_v2.py

import os
from requests_oauthlib import OAuth1Session

# Read your OAuth 1.0a consumer & access tokens from environment:
OAUTH1_CONSUMER_KEY        = os.environ["OAUTH1_CONSUMER_KEY"]
OAUTH1_CONSUMER_SECRET     = os.environ["OAUTH1_CONSUMER_SECRET"]
OAUTH1_ACCESS_TOKEN        = os.environ["OAUTH1_ACCESS_TOKEN"]
OAUTH1_ACCESS_TOKEN_SECRET = os.environ["OAUTH1_ACCESS_TOKEN_SECRET"]

def tweet_v2(text: str, image_file: str = None) -> dict:
    """
    Posts a text-only tweet via Twitter API v1.1 using OAuth 1.0a user context.
    (We ignore image_file here because v2/media is not allowed under Essential.)
    """
    oauth = OAuth1Session(
        client_key=OAUTH1_CONSUMER_KEY,
        client_secret=OAUTH1_CONSUMER_SECRET,
        resource_owner_key=OAUTH1_ACCESS_TOKEN,
        resource_owner_secret=OAUTH1_ACCESS_TOKEN_SECRET,
    )

    payload = {"status": text}

    resp = oauth.post(
        "https://api.twitter.com/1.1/statuses/update.json",
        data=payload,
        timeout=30
    )

    resp.raise_for_status()
    return resp.json()
