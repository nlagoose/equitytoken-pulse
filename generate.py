import os, json
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PROMPT = """
You are EquityToken Pulse. Craft concise, crypto-native social copy
about a token’s on-chain volume change.

INPUT:
{event_json}

Respond in **valid JSON** exactly like:
{{
  "tweet":   "<≤280 chars>",
  "linkedin":"<≤700 chars>",
  "tldr":    "<≤140 chars>"
}}
""".strip()

def craft(event: dict) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a crypto-savvy copywriter."},
            {"role": "user",   "content": PROMPT.format(event_json=json.dumps(event))}
        ],
        temperature=0.7
    )
    return json.loads(response.choices[0].message.content)

# quick test
if __name__ == "__main__":
    sample = {
        "type": "volume_move",
        "token": "USDC",
        "pct": -11.48,
        "usd_24h": 19987.53
    }
    print(json.dumps(craft(sample), indent=2))
