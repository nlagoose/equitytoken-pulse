# generate.py

import os
import json
import openai
import requests

# Ensure your OPENAI_API_KEY is set in the environment
openai.api_key = os.environ["OPENAI_API_KEY"]

PROMPT = """
You are a cheeky crypto marketer. Given this event JSON:
{event_json}
Return a JSON object with two keys:
  • "tweet": (string, ≤280 chars) – the text to tweet.
  • "image_prompt": (string, ≤60 words) – a concise DALL·E prompt describing the graphic.

Example output:
{{
  "tweet": "🚨 ETH volume just spiked 42%! Time to watch the flames. 🔥 #Crypto",
  "image_prompt": "A dramatic chart showing Ethereum volume surging, in stylized crypto-art colors"
}}
"""

def craft(event: dict) -> dict:
    # 1) Ask ChatGPT for both tweet text and an image_prompt
    chat_resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a crypto marketer."},
            {"role": "user",   "content": PROMPT.format(event_json=json.dumps(event))}
        ],
        temperature=0.7,
    )
    choice     = chat_resp.choices[0].message.content
    result     = json.loads(choice)
    tweet_text = result["tweet"]
    img_prompt = result["image_prompt"].strip()

    # ── DEBUG: show exactly what we're sending to DALL·E
    print("\n🔍 DALL·E prompt:", repr(img_prompt), "\n")

    # 2) Try image generation; if it fails, fall back to text-only
    image_file = None
    if img_prompt:
        try:
            img_resp = openai.images.generate(
                prompt=img_prompt,
                n=1,
                size="1024x1024"
            )
            img_url = img_resp["data"][0]["url"]

            # 3) Download that image locally
            filename = f"image_{event['token']}.png"
            img_data = requests.get(img_url).content
            with open(filename, "wb") as f:
                f.write(img_data)
            image_file = filename

        except Exception as e:
            # Catch any exception (including OpenAI bad‐request errors)
            print("❌ DALL·E generation failed:", e)
            # Proceed without an image (image_file stays None)

    return {
        "tweet":      tweet_text,
        "image_file": image_file
    }
