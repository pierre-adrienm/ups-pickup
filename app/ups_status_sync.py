import csv
from datetime import datetime
from db import get_session, Pickup, create_tables

def sync_pickups_from_csv(csv_path='data/ups_pickup_history.csv'):
    create_tables()
    session = get_session()

    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            print(f"📋 Colonnes du CSV : {reader.fieldnames}")

            for row in reader:
                pickup_id = row["Numéro de demande"]
                existing = session.query(Pickup).filter_by(pickup_id=pickup_id).first()

                if existing:
                    existing.etat = row["État de la demande"]
                    existing.horodatage = datetime.now()
                    print(f"🔁 Mise à jour de {pickup_id} → {existing.etat}")
                else:
                    pickup = Pickup(
                        pickup_id=pickup_id,
                        nom=row.get("Nom du contact", "Inconnu"),
                        adresse="",
                        telephone="",
                        date=row.get("Date d'enlèvement", ""),
                        heure="",
                        poids_total=0.0,  
                        nombr_Colis=0,   
                        etat=row["État de la demande"],
                        horodatage=datetime.now()
                    )
                    session.add(pickup)
                    print(f"➕ Insertion de {pickup_id}")

            session.commit()
            print("✅ Synchronisation PostgreSQL terminée.")

    except FileNotFoundError:
        print("❌ Fichier CSV non trouvé.")
    finally:
        session.close()
