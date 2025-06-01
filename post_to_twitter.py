# post_to_twitter.py

import os
import requests
from twitter_refresh import fresh_access_token

def upload_media(filename: str) -> str:
    """
    Upload a local image file to Twitter v1.1 API and return media_id_string.
    """
    token = fresh_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    files = {"media": open(filename, "rb")}
    r = requests.post(
        "https://upload.twitter.com/1.1/media/upload.json",
        headers=headers,
        files=files,
        timeout=30
    )
    r.raise_for_status()
    return r.json()["media_id_string"]

def tweet(text: str, image_file: str = None) -> dict:
    """
    Post a tweet with optional image. Returns the JSON response from /2/tweets.
    """
    token = fresh_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {"text": text}
    if image_file:
        # 1) Upload the image to get a media_id
        media_id = upload_media(image_file)
        # 2) Attach it to the tweet payload
        data["media"] = {"media_ids": [media_id]}

    r = requests.post("https://api.twitter.com/2/tweets", json=data, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()
