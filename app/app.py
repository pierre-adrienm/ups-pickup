import os
import requests
from flask import Flask, jsonify
from pickup import schedule_pickup
from email_sender import send_email

app = Flask(__name__)

@app.route('/api/pickup/test')
def test():
    test_data = {
        "nom": "Camille HAUTEFAYE",
        "telephone": "0672093189",
        "adresse": "7 allée Métis",
        "ville": "Saint-Malo",
        "code_postal": "35400",
        "date": "20250425",
        "heure_debut": "1300",
        "heure_fin": "1700",
        "nombre_colis": 3,
        "poids_total": 8
    }

    # 🔐 Authentification UPS
    auth_response = requests.post(
        "https://onlinetools.ups.com/security/v1/oauth/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + os.getenv("UPS_ENCODED_CREDENTIALS")
        },
        data={"grant_type": "client_credentials"}
    )

    if auth_response.status_code != 200:
        return jsonify({
            "status": "error",
            "message": "Échec de l'authentification",
            "details": auth_response.text
        })

    access_token = auth_response.json()["access_token"]

    # 📦 Demande d’enlèvement
    result = schedule_pickup(test_data, access_token)
    email_status = {
        "status": "not_sent",
        "message": "E-mail non tenté"
    }

    if result["status"] == "success":
        try:
            pickup_data = result["data"]["PickupCreationResponse"]
            pickup_id = pickup_data.get("PRN") or pickup_data.get("PickupRequestConfirmationNumber")

            if not pickup_id:
                raise KeyError("Numéro d'enlèvement manquant dans la réponse UPS.")

            subject = f"Confirmation de votre enlèvement UPS numéro {pickup_id}"
            body = f"Votre demande d'enlèvement a bien été prise en compte.\nNuméro d'enlèvement : {pickup_id} \nÉquipe Labeko"
            send_email(subject, body, "marque.pierre-adrien@orange.fr")

            email_status = {
                "status": "sent",
                "message": "E-mail envoyé avec succès",
                "pickup_id": pickup_id
            }

        except Exception as e:
            email_status = {
                "status": "error",
                "message": "Erreur lors de l’envoi de l’e-mail",
                "details": str(e)
            }

    return jsonify({
        "ups_response": result,
        "email_status": email_status
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
