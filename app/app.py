import os
import requests
from flask import Flask, jsonify, request
from pickup import schedule_pickup
from email_sender import send_email
from history import save_pickup, get_history, export_history_csv
from datetime import datetime
from babel.dates import format_date
from pytz import timezone
from ups_status_sync import sync_pickups_from_csv
from db import get_session, Pickup

def get_current_horodatage():
    tz = timezone('Europe/Paris')
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S")

app = Flask(__name__)

@app.route('/api/pickup/create')
def create():
    test_data = {
        "nom": "Camille HAUTEFAYE",
        "telephone": "0672093189",
        "adresse": "7 allée Métis",
        "ville": "Saint-Malo",
        "code_postal": "35400",
        "date": "20250430",
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
            
            tz = timezone('Europe/Paris')
            horodatage = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            
            pickup_entry = {
                "pickup_id": pickup_id,
                "nom": test_data["nom"],
                "telephone": test_data["telephone"],
                "adresse": test_data["adresse"],
                "nombr_Colis": test_data["nombre_colis"],
                "poids_total": test_data["poids_total"],
                "date": test_data["date"],
                "heure": f"{test_data['heure_debut']} - {test_data['heure_fin']}",
                "horodatage": horodatage
            }
            save_pickup(pickup_entry)

            pickup_date = datetime.strptime(test_data["date"], "%Y%m%d")
            formatted_date = format_date(pickup_date, format='full', locale='fr_FR')

            heureDebut = f"{test_data['heure_debut'][:2]}h{test_data['heure_debut'][2:]}"
            heureFin = f"{test_data['heure_fin'][:2]}h{test_data['heure_fin'][2:]}"

            subject = f"Confirmation de votre enlèvement UPS numéro {pickup_id}"
            html_body = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; color: #333;">
                        <p>Bonjour <strong>{test_data['nom']}</strong>,</p>

                        <p>Votre demande d'enlèvement a bien été prise en compte :</p>

                        <ul>
                        <li><strong>📦 Numéro d'enlèvement :</strong> {pickup_id}</li>
                        <li><strong>🏠 Adresse :</strong> {test_data['adresse']}, {test_data['code_postal']} {test_data['ville']}</li>
                        <li><strong>📅 Date :</strong> {formatted_date}</li>
                        <li><strong>⏰ Créneau :</strong> {heureDebut} - {heureFin}</li>
                        <li><strong>📦 Colis :</strong> {test_data['nombre_colis']} colis pour un poids total de {test_data['poids_total']} kg</li>
                        </ul>

                        <p>Pour toute modification de l'enlèvement, merci de contacter Labeko à l'adresse suivante :
                        <a href="mailto:contact@labeko.fr">contact@labeko.fr</a>
                        </p>

                        <p style="margin-top: 30px;">Merci pour votre confiance,<br>
                        <em>L’équipe Labeko</em></p>
                    </body>
                </html>
                """

            send_email(
                to="marque.pierre-adrien@orange.fr",
                cc="pierreadrien.marque@reseau.eseo.fr",
                subject=subject,
                body=html_body,
                html=True
            )

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

@app.route('/api/pickup/history', methods=['GET'])
def pickup_history():
    try:
        history = get_history()

        # Ajout explicite d'un champ "etat" s'il n'existe pas
        for entry in history:
            if "etat" not in entry:
                entry["etat"] = "Non défini"

        return jsonify({"status": "success", "data": history})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/pickup/export', methods=['GET'])
def pickup_export():
    return export_history_csv()


@app.route('/api/pickup/clear', methods=['GET','POST'])
def clear_pickup_history():
    try:
        history_path = "data/pickup_history.json"
        if os.path.exists(history_path):
            open(history_path, 'w').close()  # Vide le fichier sans le supprimer
            return jsonify({"status": "success", "message": "Historique des enlèvements vidé."}), 200
        else:
            return jsonify({"status": "error", "message": "Aucun historique à vider."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/pickup/upload_csv', methods=['GET','POST'])
def generate_fake_csv():
    try:
        csv_path = "data/ups_pickup_history.csv"
        with open(csv_path, mode='w', encoding='utf-8', newline='') as f:
            f.write("Date d'enlèvement,Numéro de demande,Nom du contact,Références d'enlèvement,État de la demande\n")
            f.write("5/2/2025,29W44M509BJ,GALLAND Gregory,,Votre demande d'enlèvement est en cours de traitement.\n")
            f.write("4/30/2025,29H42MEG2IB,GAEL MORISSEAU,,Votre demande d'enlèvement a bien été reçue. Un conducteur UPS passera enlever votre/vos colis.\n")
            f.write("4/30/2025,29Z445R6DEP,LABEKO UTOPI,,Votre demande d'enlèvement a été annulée.\n")

        return jsonify({
            "status": "success",
            "message": "Fichier CSV UPS fictif généré avec succès",
            "path": csv_path
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/pickup/sync', methods=['POST', 'GET'])
def sync_ups_status():
    try:
        maj_count = synchroniser()
        return jsonify({
            "status": "success",
            "message": f"{maj_count} statuts synchronisés depuis le CSV UPS"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/pickup/add_test', methods=['POST', 'GET'])
def add_test_entry():
    try:
        test_entry = {
            "pickup_id": "29Z445R6DEP",
            "nom": "Test Synchronisation",
            "telephone": "0612345678",
            "adresse": "1 rue de Test",
            "nombr_Colis": 4,
            "poids_total": 15,
            "date": "20250507",
            "heure": "1300 - 1700",
            "horodatage": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        save_pickup(test_entry)

        return jsonify({
            "status": "success",
            "message": f"Entrée de test ajoutée avec pickup_id {test_entry['pickup_id']}"
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/sync", methods=["POST"])
def sync():
    try:
        sync_pickups_from_csv()
        return jsonify({"message": "Synchronisation réussie", "status": "ok"}), 200
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

@app.route("/status/<pickup_id>", methods=["GET"])
def get_status(pickup_id):
    session = get_session()
    pickup = session.query(Pickup).filter_by(pickup_id=pickup_id).first()
    session.close()

    if pickup:
        return jsonify({
            "pickup_id": pickup.pickup_id,
            "nom": pickup.nom,
            "date": pickup.date,
            "etat": pickup.etat,
            "horodatage": pickup.horodatage.isoformat()
        })
    else:
        return jsonify({"message": "Enlèvement non trouvé", "status": "not_found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
