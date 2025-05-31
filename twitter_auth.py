# twitter_auth.py  (drop-in replacement)

import os, secrets, hashlib, base64, urllib.parse, webbrowser, requests, json

# ------------------------------------------------------------
CLIENT_ID     = os.environ["TW_CLIENT_ID"]
CLIENT_SECRET = os.environ["TW_CLIENT_SECRET"]
REDIRECT_URI  = os.environ["TW_REDIRECT_URI"]  # e.g. https://localhost/twitter-callback
SCOPES        = "tweet.read tweet.write users.read offline.access"
# ------------------------------------------------------------

# 1️⃣ Generate PKCE codes
code_verifier  = secrets.token_urlsafe(64)
code_challenge = (
    base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
    .decode()
    .rstrip("=")
)

# 2️⃣ Build & open the auth URL
params = {
    "response_type": "code",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPES,
    "state": secrets.token_urlsafe(8),
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
}
auth_url = "https://twitter.com/i/oauth2/authorize?" + urllib.parse.urlencode(params)

print("\nOpen this URL → sign in → Authorize, then copy the long value after code=\n")
print(auth_url + "\n")

try:
    webbrowser.open(auth_url)
except Exception:
    pass  # no browser in Replit

auth_code = input("Paste the code value here (no 'code=' prefix):\n").strip()

# 3️⃣ Build Basic header
basic = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

# 4️⃣ Exchange code for tokens
print(
    "\nDEBUG → POST payload",
    {
        "grant_type": "authorization_code",
        "code": "<redacted>",
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier[:12] + "…",
    },
)

token_resp = requests.post(
    "https://api.twitter.com/2/oauth2/token",
    headers={
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded",
    },
    data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,
    },
    timeout=30,
)

print("\nDEBUG ←", token_resp.status_code, token_resp.text)
token_resp.raise_for_status()

tokens = token_resp.json()
print("\n✅  SUCCESS — add these to Replit Secrets:\n")
print(json.dumps(tokens, indent=2))
