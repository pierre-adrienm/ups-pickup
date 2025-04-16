import os
from flask import Flask, jsonify
from pickup import schedule_pickup

app = Flask(__name__)

@app.route("/api/pickup/test", methods=["GET"])
def test():
    try:
        test_data = {
            "nom": "Jean Dupont",
            "telephone": "0601020304",
            "adresse": "7 allée Métis",
            "ville": "Saint-Malo",
            "code_postal": "35400",
            "date": "20250417",
            "nombre_colis": 1,
            "poids_total": 2,
            "account_number": os.getenv("UPS_ACCOUNT_NUMBER")
        }
        result = schedule_pickup(test_data)
        return jsonify(result)
    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        print("🧨 Une erreur s'est produite :")
        print(trace)
        return jsonify({
            "status": "error",
            "message": str(e),
            "trace": trace
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
