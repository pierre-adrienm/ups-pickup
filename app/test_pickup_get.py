import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("UPS_CLIENT_ID")
client_secret = os.getenv("UPS_CLIENT_SECRET")

# Obtenir token
auth = requests.post(
    "https://wwwcie.ups.com/security/v1/oauth/token",
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    },
    data={"grant_type": "client_credentials"}
)
token = auth.json().get("access_token")

if not token:
    print("Token invalide :", auth.text)
    exit()

# Test GET Pickup (savoir s’il existe ou pas)
pickup_url = "https://wwwcie.ups.com/api/pickup/v1/pickups"
headers = {
    "Authorization": f"Bearer {token}",
    "transId": "TestGETPickup",
    "transactionSrc": "Labeko",
    "Content-Type": "application/json"
}

r = requests.get(pickup_url, headers=headers)

print("Code retour :", r.status_code)
print("Contenu brut :", r.text)
