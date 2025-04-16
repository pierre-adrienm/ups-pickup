import os
import requests
import json
from dotenv import load_dotenv

import logging

# Affiche tous les logs HTTP bas niveau
try:
    import http.client as http_client
except ImportError:
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


load_dotenv()

def schedule_pickup(data):
    print("📦 Planification d’un enlèvement UPS...")

    client_id = os.getenv("UPS_CLIENT_ID")
    client_secret = os.getenv("UPS_CLIENT_SECRET")
    account_number = os.getenv("UPS_ACCOUNT_NUMBER")
    environment = os.getenv("UPS_ENV", "sandbox")

    base_url = "https://wwwcie.ups.com" if environment == "sandbox" else "https://onlinetools.ups.com"
    auth_url = f"{base_url}/security/v1/oauth/token"
    pickup_url = f"{base_url}/api/shipments/v1/pickup/confirm"


    print("🧪 Environnement UPS :", environment)
    print("🔗 URL finale appelée :", pickup_url)

    auth_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    auth_data = {
        "grant_type": "client_credentials"
    }

    print("🔐 Authentification en cours...")
    response = requests.post(auth_url, headers=auth_headers, auth=(client_id, client_secret), data=auth_data)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("🛑 ERREUR DÉTAILLÉE UPS :", response.text)
        return {"status": "error", "message": str(err), "details": response.text}
    auth_token = response.json()["access_token"]

    pickup_headers = {
        "Content-Type": "application/json",
        "transId": "test123",
        "transactionSrc": "LabekoApp",
        "Authorization": f"Bearer {auth_token}"
    }

    pickup_payload = {
        "PickupCreationRequest": {
            "Requester": {
                "AccountNumber": account_number,
                "AttentionName": "Jessica Touffet",
                "Name": "Labeko",
                "Phone": {
                    "Number": "0601020304"
                },
                "Address": {
                    "AddressLine": ["7 allée Métis"],
                    "City": "Saint-Malo",
                    "PostalCode": "35400",
                    "CountryCode": "FR"
                }
            },
            "Shipper": {
                "AccountNumber": account_number,
                "Phone": {
                    "Number": "0601020304"
                },
                "Address": {
                    "CompanyName": "Labeko",
                    "ContactName": "Jessica Touffet",
                    "Phone": {
                        "Number": "0601020304"
                    },
                    "AddressLine": ["7 allée Métis"],
                    "City": "Saint-Malo",
                    "PostalCode": "35400",
                    "CountryCode": "FR"
                }
            },
            "PickupAddress": {
                "CompanyName": "Labeko",
                "ContactName": "Jessica Touffet",
                "Phone": {
                    "Number": "0601020304"
                },
                "AddressLine": ["7 allée Métis"],
                "City": "Saint-Malo",
                "PostalCode": "35400",
                "CountryCode": "FR",
                "ResidentialIndicator": "N"
            },
            "PickupDateInfo": {
                "CloseTime": "1700",
                "ReadyTime": "0900",
                "PickupDate": "20250417"
            },
            "AlternateAddressIndicator": "N",
            "PickupPiece": [
                {
                    "ServiceCode": "001",
                    "Quantity": "1",
                    "DestinationCountryCode": "FR",
                    "ContainerCode": "02",
                    "Weight": {
                        "Weight": "2",
                        "UnitOfMeasurement": {
                            "Code": "KGS"
                        }
                    }
                }
            ],
            "PaymentMethod": {
                "Code": "01"
            },
            "RatePickupIndicator": "Y",
            "SpecialInstruction": "Test depuis Labeko"
        }
    }

    print("\n🚀 Envoi vers UPS")
    print("🌍 URL :", pickup_url)
    print("🧾 Headers :", json.dumps(pickup_headers, indent=2))
    print("📦 Payload :", json.dumps(pickup_payload, indent=2))

    try:
        response = requests.post(pickup_url, headers=pickup_headers, json=pickup_payload,timeout=15)

        print("🧾 Code réponse UPS :", response.status_code)
        print("📨 Contenu réponse :", response.text)
        
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if "status"== 200:
            return {"status": "success", "data": response.json()}
        else: 
            print("🛑 ERREUR DÉTAILLÉE UPS :", response.text)
            return {"status": "error", "message": str(err), "details": response.text}
        
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}
