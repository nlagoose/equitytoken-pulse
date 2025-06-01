# generate.py

import os
import json
import openai
import requests

PROMPT = """
You are a cheeky crypto marketer. Given this event JSON:
{event_json}
Return a JSON object with two keys:
  • "tweet": (string, ≤280 chars) – the text to tweet.
  • "image_prompt": (string, ≤60 words) – a concise DALL·E prompt describing the graphic.

Example output:
{{
  "tweet": "🚨 ETH volume just spiked 42%! Time to watch the flames. 🔥 #Crypto",
  "image_prompt": "A dramatic chart showing Ethereum volume surging, in stylized crypto‐art colors"
}}
"""

def craft(event: dict) -> dict:
    # 1) Ask ChatGPT for both tweet text and an image prompt
    chat_resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a crypto marketer."},
            {"role": "user",   "content": PROMPT.format(event_json=json.dumps(event))}
        ],
        temperature=0.7,
    )
    result = json.loads(chat_resp.choices[0].message.content)
    tweet_text = result["tweet"]
    img_prompt = result["image_prompt"]

    # 2) Generate a DALL·E image from the image_prompt
    img_resp = openai.Image.create(
        prompt=img_prompt,
        n=1,
        size="1024x1024"
    )
    # Grab the URL of the generated image
    img_url = img_resp["data"][0]["url"]

    # 3) Download the image to a local file
    #    We’ll name it based on the token so multiple runs don’t clash.
    filename = f"image_{event['token']}.png"
    img_data = requests.get(img_url).content
    with open(filename, "wb") as f:
        f.write(img_data)

    # 4) Return both the tweet text and the local image filename
    return {
        "tweet": tweet_text,
        "image_file": filename
    }
