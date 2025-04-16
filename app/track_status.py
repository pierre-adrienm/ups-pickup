import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import base64
from tabulate import tabulate

# === Init ===
print("🚀 Script UPS Tracking lancé...")
load_dotenv()

client_id = os.getenv("UPS_CLIENT_ID")
client_secret = os.getenv("UPS_CLIENT_SECRET")
env = os.getenv("UPS_ENV", "sandbox").lower()

# === Config URL ===
# base_url = "https://www.ups.com" if env == "production" else "https://wwwcie.ups.com"
base_url = "https://www.ups.com"  # ⚠️ Forcé en production pour tracking réel
auth_url = f"{base_url}/security/v1/oauth/token"
track_url = f"{base_url}/api/track/v1/details"
print(f"🔧 Environnement : {env.upper()} - Base URL : {base_url}")

# === Authentification ===
auth_headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
}
auth_data = {"grant_type": "client_credentials"}

token_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
access_token = token_response.json().get("access_token")
if not access_token:
    print("❌ Erreur d'authentification :", token_response.text)
    exit()

# === Détection de problème ===
def detect_problem(description):
    problems = {
        "Pickup attempt failed": "Enlèvement échoué",
        "Delivery rescheduled": "Livraison reprogrammée",
        "Address information required": "Adresse incomplète",
        "Exception": "Exception détectée"
    }
    for keyword, issue in problems.items():
        if keyword.lower() in description.lower():
            return issue
    return "-"

# === Suivi UPS ===
def get_tracking_status(tracking_number):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "trackingNumber": [tracking_number]
    }

    response = requests.post(track_url, headers=headers, json=payload)
    print(f"\n🔎 Requête pour {tracking_number} - Code HTTP : {response.status_code}")

    try:
        data = response.json()
        print("📨 Contenu brut de la réponse :")
        print(data)
    except Exception as e:
        print("❌ Erreur de décodage JSON :", e)
        print("📝 Réponse brute :", response.text)
        return {
            "Numéro de suivi": tracking_number,
            "État": "Erreur JSON",
            "Dernière mise à jour": "-",
            "Problème détecté": "Erreur de parsing"
        }

    if response.status_code != 200:
        return {
            "Numéro de suivi": tracking_number,
            "État": "Erreur",
            "Dernière mise à jour": "-",
            "Problème détecté": f"Erreur API ({response.status_code})"
        }

    try:
        shipment = data["trackResponse"]["shipment"][0]
        activity = shipment["package"][0]["activity"][0]
        status = activity["status"]["description"]
        status_type = activity["status"].get("type", "")
        last_update = datetime.strptime(
            activity["date"] + activity["time"], "%Y%m%d%H%M%S"
        ).strftime("%d/%m/%Y à %Hh%M")

        full_desc = f"{status_type} - {status}"
        problem = detect_problem(full_desc)

        return {
            "Numéro de suivi": tracking_number,
            "État": status,
            "Dernière mise à jour": last_update,
            "Problème détecté": problem
        }
    except Exception as e:
        return {
            "Numéro de suivi": tracking_number,
            "État": "Erreur",
            "Dernière mise à jour": "-",
            "Problème détecté": f"Erreur lecture données : {e}"
        }

# === Numéros à suivre ===
tracking_numbers = [
    "1ZJ40D016813310612"
]

results = []
for tn in tracking_numbers:
    info = get_tracking_status(tn)
    results.append(info)

# === Affichage du tableau final
print("\n📦 Tableau de suivi UPS :\n")
print(tabulate(results, headers="keys", tablefmt="grid"))
