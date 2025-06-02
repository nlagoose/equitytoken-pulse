# generate.py

import os
import json
import openai
import requests
import matplotlib.pyplot as plt

# Ensure your OPENAI_API_KEY is set in the environment
openai.api_key = os.environ["OPENAI_API_KEY"]

PROMPT = """
You are the world’s most over-the-top, electrifying crypto hype master.  
Given an event JSON describing an on-chain volume move:
{event_json}

Produce a JSON object with two keys:
  1) "tweet": (string, ≤280 chars)  
     – Write as if you’re on stage at a crypto concert: flamboyant metaphors, all-caps excitement, emojis everywhere.  
     – Mention the token symbol (e.g. WBTC) and highlight the % change and dollar volume.  
     – End with 1–2 trending hashtags like #CryptoMania, #TokenFrenzy, etc.

  2) "image_prompt": (string, ≤60 words)  
     – A wild, cartoonish scene—imagine a rocket blasting off from a shiny token, confetti raining down, dollar‐sign fireworks.  
     – Keep it concise and vivid, so DALL·E can draw it.

Example output:
{{
  "tweet": "🚀🚨 WBTC JUST EXPLODED UP 35%! VOLUME SMASHED $1.2B IN 24H! WHOA, BUCKLE UP & HODL LOUD! 🤯🔥 #CryptoMania #BTCBOOM",
  "image_prompt": "A giant WBTC coin rocket blasting off into space with fireworks and confetti, neon colors, cartoon style"
}}
"""

def craft(event: dict) -> dict:
    """
    1) Ask GPT for hype‐level tweet + an “image_prompt”.  
    2) Try DALL·E for that prompt. If it fails, draw a simple bar chart.  
    3) Return {"tweet": <text>, "image_file": <filename or None>}.
    """
    # ---- 1) Ask GPT to generate text + image prompt ----
    chat_resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a flamboyant, over-the-top crypto hype master."},
            {"role": "user",   "content": PROMPT.format(event_json=json.dumps(event))}
        ],
        temperature=0.9,  # high temperature for more flamboyant output
    )
    choice     = chat_resp.choices[0].message.content
    result     = json.loads(choice)
    tweet_text = result["tweet"]
    img_prompt = result["image_prompt"].strip()

    # ---- Debug: show DALL·E prompt ----
    print("\n🔍 DALL·E prompt:", repr(img_prompt), "\n")

    image_file = None

    if img_prompt:
        # ---- 2) Try DALL·E first ----
        try:
            img_resp = openai.images.generate(
                prompt=img_prompt,
                n=1,
                size="1024x1024"
            )
            img_url = img_resp["data"][0]["url"]

            filename = f"image_{event['token']}.png"
            img_data = requests.get(img_url).content
            with open(filename, "wb") as f:
                f.write(img_data)
            image_file = filename

        except Exception as e:
            # If DALL·E fails, fall back to bar chart
            print("❌ DALL·E generation failed:", e)
            image_file = _make_bar_chart(event)
    else:
        # If GPT returned no prompt, immediately fall back
        image_file = _make_bar_chart(event)

    return {
        "tweet":      tweet_text,
        "image_file": image_file
    }


def _make_bar_chart(event: dict) -> str:
    """
    Draw a two-bar chart comparing prev_24h vs rolling_24h (both in USD millions).
    Save it as chart_<token>.png and return that filename.
    """
    token = event["token"]
    prev  = event["prev_24h"]    / 1e6  # millions
    curr  = event["rolling_24h"] / 1e6  # millions

    fig, ax = plt.subplots(figsize=(6, 6))
    bars = ax.bar(
        ["Prev 24h", "Curr 24h"],
        [prev, curr],
        color=["#555555", "#ffcc00"]
    )
    ax.set_title(f"{token} 24h Volume (in $M)", fontsize=16)
    ax.set_ylabel("Volume (millions USD)", fontsize=14)
    ax.tick_params(axis="x", labelsize=12)
    ax.tick_params(axis="y", labelsize=12)

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.5,
            f"{height:.1f}M",
            ha="center",
            va="bottom",
            fontsize=12
        )

    filename = f"chart_{token}.png"
    abs_path = os.path.join(os.getcwd(), filename)
    fig.tight_layout()
    fig.savefig(abs_path, dpi=170)
    plt.close(fig)

    print("[DEBUG] Saved fallback bar chart as", abs_path, "→ exists?", os.path.exists(abs_path))
    return filename
