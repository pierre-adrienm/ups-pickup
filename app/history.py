import json
import csv
from flask import jsonify, Response

HISTORY_FILE = "data/pickup_history.json"

def save_pickup(entry):
    try:
        with open(HISTORY_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return True
    except Exception as e:
        print("❌ Erreur lors de l'enregistrement :", e)
        return False

def get_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return [json.loads(line) for line in f.readlines()]
    except FileNotFoundError:
        return []
    except Exception as e:
        raise RuntimeError(f"Erreur lecture historique : {e}")

def export_history_csv():
    try:
        pickups = get_history()
        fieldnames = ["pickup_id", "nom", "telephone", "adresse", "date", "heure"]

        def generate():
            yield ",".join(fieldnames) + "\n"
            for entry in pickups:
                row = [entry.get(field, "") for field in fieldnames]
                yield ",".join(row) + "\n"

        return Response(generate(), mimetype='text/csv',
                        headers={"Content-Disposition": "attachment;filename=pickup_history.csv"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
