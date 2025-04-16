import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("UPS_CLIENT_ID")
client_secret = os.getenv("UPS_CLIENT_SECRET")
env = os.getenv("UPS_ENV", "production")

base_url = "https://www.ups.com" if env == "production" else "https://wwwcie.ups.com"
auth_url = f"{base_url}/security/v1/oauth/token"

auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {auth_header}"
}

data = {"grant_type": "client_credentials"}

print(f"🔐 Envoi de la requête vers {auth_url}...")

response = requests.post(auth_url, headers=headers, data=data)

print("✅ Code HTTP :", response.status_code)
print("📦 Réponse complète :")
print(response.text)
