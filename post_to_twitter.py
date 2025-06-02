# post_to_twitter.py

import os
import requests
from twitter_refresh import fresh_access_token

def upload_media(filename: str) -> str:
    token = fresh_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    print("[DEBUG] upload_media: attempting to open file:", filename)
    if not os.path.exists(filename):
        print(f"[ERROR] upload_media: file does NOT exist → {filename}")
    else:
        print(f"[DEBUG] upload_media: file exists, size={os.path.getsize(filename)} bytes")

    files = {"media": open(filename, "rb")}
    r = requests.post(
        "https://upload.twitter.com/1.1/media/upload.json",
        headers=headers,
        files=files,
        timeout=30
    )
    print("[DEBUG] upload_media: HTTP status", r.status_code)
    r.raise_for_status()
    media_id = r.json()["media_id_string"]
    print("[DEBUG] upload_media: got media_id_string:", media_id)
    return media_id

def tweet(text: str, image_file: str = None) -> dict:
    token = fresh_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("[DEBUG] tweet(): text length:", len(text))
    print("[DEBUG] tweet(): image_file passed in:", image_file)

    data = {"text": text}
    if image_file:
        media_id = upload_media(image_file)
        data["media"] = {"media_ids": [media_id]}

    print("[DEBUG] tweet(): final payload to /2/tweets:", data)
    r = requests.post("https://api.twitter.com/2/tweets", json=data, headers=headers, timeout=30)
    print("[DEBUG] tweet(): HTTP status", r.status_code)
    r.raise_for_status()
    print("[DEBUG] tweet(): response JSON keys:", r.json().keys())
    return r.json()
