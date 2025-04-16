import os
import requests
from dotenv import load_dotenv
import base64

load_dotenv()

client_id = os.getenv("UPS_CLIENT_ID")
client_secret = os.getenv("UPS_CLIENT_SECRET")

# Auth
auth_url = "https://wwwcie.ups.com/security/v1/oauth/token"
auth_headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
}
auth_data = {
    "grant_type": "client_credentials"
}
auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
access_token = auth_response.json().get("access_token")

if not access_token:
    print("Erreur lors du token :", auth_response.text)
    exit()

# Test endpoint (par exemple, le Locator — renvoie les points relais disponibles)
url = "https://wwwcie.ups.com/api/locator/v1/drop-off-points?country=FR&postalCode=35400"
headers = {
    "Authorization": f"Bearer {access_token}",
    "transId": "LabekoTestLocator",
    "transactionSrc": "Labeko",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
print("Code retour :", response.status_code)
try:
    print("Réponse JSON :", response.json())
except Exception as e:
    print("Contenu brut :", response.text)
