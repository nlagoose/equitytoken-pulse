# post_to_twitter_v2.py

import os
import base64
import requests
from requests.exceptions import HTTPError

# --Your OAuth 2.0 bearer from PKCE
BEARER = os.environ["TW_ACCESS_TOKEN"]

def upload_media_v2(image_file: str) -> str:
    """
    Try to upload a local image via Twitter v2 media endpoint.
    If a 403 comes back, re-raise it so the caller can fall back to text-only.
    """
    with open(image_file, "rb") as f:
        img_bytes = f.read()

    b64str = base64.b64encode(img_bytes).decode("utf-8")
    endpoint = "https://upload.twitter.com/2/media/upload"

    headers = {
        "Authorization": f"Bearer {BEARER}",
        "Content-Type": "application/json"
    }
    body = {
        "media_category": "tweet_image",
        "media": b64str
    }

    resp = requests.post(endpoint, headers=headers, json=body, timeout=30)
    try:
        resp.raise_for_status()
    except HTTPError as e:
        # If v2/media is forbidden (403), bubble that up so caller can fallback
        if resp.status_code == 403:
            raise
        else:
            raise
    return resp.json()["media_key"]


def tweet_v2(text: str, image_file: str = None) -> dict:
    """
    Post a tweet via Twitter API v2. If image_file is provided, try v2/media first.
    If v2/media returns 403, fall back to a text‐only tweet.
    """
    endpoint = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {BEARER}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}

    if image_file:
        try:
            media_key = upload_media_v2(image_file)
            payload["media"] = {"media_ids": [media_key]}
        except HTTPError as err:
            # 403 means no v2 media access—just send text only
            if err.response.status_code == 403:
                print("⚠️ v2/media upload forbidden—posting text-only.")
            else:
                # re-raise any other HTTP errors
                raise

    resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()
