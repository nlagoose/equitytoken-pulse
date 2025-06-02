# post_to_twitter.py

import os
from requests_oauthlib import OAuth1Session

# Read your four OAuth 1.0a secrets from environment
OAUTH1_CONSUMER_KEY        = os.environ["OAUTH1_CONSUMER_KEY"]
OAUTH1_CONSUMER_SECRET     = os.environ["OAUTH1_CONSUMER_SECRET"]
OAUTH1_ACCESS_TOKEN        = os.environ["OAUTH1_ACCESS_TOKEN"]
OAUTH1_ACCESS_TOKEN_SECRET = os.environ["OAUTH1_ACCESS_TOKEN_SECRET"]

def upload_media(image_file: str) -> str:
    """
    Uploads a local image to Twitter v1.1 media endpoint using OAuth1.0a user context.
    Returns the "media_id_string" to attach to a tweet.
    """
    oauth = OAuth1Session(
        client_key=OAUTH1_CONSUMER_KEY,
        client_secret=OAUTH1_CONSUMER_SECRET,
        resource_owner_key=OAUTH1_ACCESS_TOKEN,
        resource_owner_secret=OAUTH1_ACCESS_TOKEN_SECRET,
    )

    with open(image_file, "rb") as f:
        files = {"media": f}
        resp = oauth.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            files=files
        )

    resp.raise_for_status()
    return resp.json()["media_id_string"]

def tweet(text: str, image_file: str = None) -> dict:
    """
    Posts a tweet (with optional media) via Twitter v1.1 statuses/update.
    Both upload_media() and status update use OAuth1.0a.
    """
    oauth = OAuth1Session(
        client_key=OAUTH1_CONSUMER_KEY,
        client_secret=OAUTH1_CONSUMER_SECRET,
        resource_owner_key=OAUTH1_ACCESS_TOKEN,
        resource_owner_secret=OAUTH1_ACCESS_TOKEN_SECRET,
    )

    payload = {"status": text}
    if image_file:
        media_id = upload_media(image_file)
        payload["media_ids"] = media_id

    resp = oauth.post(
        "https://api.twitter.com/1.1/statuses/update.json",
        data=payload
    )
    resp.raise_for_status()
    return resp.json()
