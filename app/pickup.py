import os
import requests
import json
from dotenv import load_dotenv

import logging

def schedule_pickup(data, access_token):
    print("📦 Planification d’un enlèvement UPS...")

    version = "v1"
    # url = f"https://onlinetools.ups.com/api/pickupcreation/{version}/pickup"
    url = f"https://wwwcie.ups.com/api/pickupcreation/{version}/pickup"

    payload = {
        "PickupCreationRequest": {
            "RatePickupIndicator": "N",
            "Shipper": {
                "Account": {
                    "AccountNumber": os.getenv("UPS_ACCOUNT_NUMBER"),
                    "AccountCountryCode": "FR"
                }
            },
            "PickupDateInfo": {
                "CloseTime": data["heure_fin"],
                "ReadyTime": data["heure_debut"],
                "PickupDate": data["date"]
            },
            "PickupAddress": {
                "CompanyName": "Labeko",
                "ContactName": data["nom"],
                "AddressLine": data["adresse"],
                "City": data["ville"],
                "PostalCode": data["code_postal"],
                "CountryCode": "FR",
                "ResidentialIndicator": "N",
                "PickupPoint": "Porte",
                "Phone": {
                    "Number": data["telephone"],
                    "Extension": ""
                }
            },
            "AlternateAddressIndicator": "N",
            "PickupPiece": [
                {
                    "ServiceCode": "065",
                    "Quantity": str(data["nombre_colis"]),
                    "DestinationCountryCode": "FR",
                    "ContainerCode": "02"
                }
            ],
            "TotalWeight": {
                "Weight": str(data["poids_total"]),
                "UnitOfMeasurement": "KGS"
            },
            "OverweightIndicator": "N",
            "PaymentMethod": "01",
            "SpecialInstruction": "Test depuis Labeko"
        }
    }

    headers = {
        "Content-Type": "application/json",
        "transId": "Labeko123",
        "transactionSrc": "LabekoApp",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {
            "status": "error",
            "message": str(response),
            "details": response.text
        }
