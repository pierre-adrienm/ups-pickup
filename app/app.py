import os
from flask import Flask, jsonify
from pickup import schedule_pickup
import requests

app = Flask(__name__)

@app.route('/api/pickup/test')
def test():
    test_data = {
        "nom": "Jean Dupont",
        "telephone": "0601020304",
        "adresse": "7 allée Métis",
        "ville": "Saint-Malo",
        "code_postal": "35400",
        "date": "20250418",
        "nombre_colis": 2,
        "poids_total": 2
    }

    # 🔐 Récupérer le token d'accès UPS
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

    # 📦 Appel de la fonction avec le bon token
    result = schedule_pickup(test_data, access_token)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
