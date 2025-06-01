# update_secret.py

import os, base64, json, requests
from nacl import encoding, public

# ── CONFIGURATION (injected by our workflow) ──
GH_PAT             = os.environ["GH_PAT"]             # PAT with repo & workflow scopes
REPO               = os.environ["GITHUB_REPOSITORY"]  # e.g. "youruser/yourrepo"
SECRET_NAME        = "TW_REFRESH_TOKEN"
NEW_REFRESH_FILE   = "new_refresh_token.txt"

def encrypt_secret(public_key: str, plaintext_value: str) -> str:
    """
    Given GitHub’s Base64-encoded public key and the plaintext secret,
    returns the encrypted secret as a Base64 string.
    """
    public_key_bytes = base64.b64decode(public_key)
    pub_key = public.PublicKey(public_key_bytes, encoding.RawEncoder())
    sealed_box = public.SealedBox(pub_key)
    encrypted = sealed_box.encrypt(plaintext_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def main():
    # 1. Read the newly rotated refresh token from file
    if not os.path.exists(NEW_REFRESH_FILE):
        print(f"⚠️  {NEW_REFRESH_FILE} not found—nothing to update.")
        return

    new_refresh = open(NEW_REFRESH_FILE).read().strip()
    if not new_refresh:
        print(f"⚠️  {NEW_REFRESH_FILE} is empty—skipping.")
        return

    # 2. Get the repository’s public key from GitHub
    headers = {
        "Accept":                "application/vnd.github+json",
        "Authorization":         f"Bearer {GH_PAT}",
        "X-GitHub-Api-Version":  "2022-11-28"
    }
    url_key = f"https://api.github.com/repos/{REPO}/actions/secrets/public-key"
    resp_key = requests.get(url_key, headers=headers, timeout=30)
    resp_key.raise_for_status()
    key_json    = resp_key.json()
    public_key  = key_json["key"]      # Base64-encoded
    public_key_id = key_json["key_id"]

    # 3. Encrypt the new refresh token
    encrypted_value = encrypt_secret(public_key, new_refresh)

    # 4. Update the secret
    url_put = f"https://api.github.com/repos/{REPO}/actions/secrets/{SECRET_NAME}"
    payload = {
        "encrypted_value": encrypted_value,
        "key_id":          public_key_id
    }
    resp_put = requests.put(
        url_put,
        headers=headers,
        data=json.dumps(payload),
        timeout=30
    )
    if resp_put.status_code not in (201, 204):
        print("❌ Failed to update secret:", resp_put.status_code, resp_put.text)
        resp_put.raise_for_status()

    print(f"✅ Secret `{SECRET_NAME}` updated successfully.")

if __name__ == "__main__":
    main()
