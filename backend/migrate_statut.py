"""
Migration : change la colonne 'statut' de ENUM vers VARCHAR(30)
afin de supporter la valeur 'en_attente_medecin'.

Exécuter UNE SEULE FOIS depuis le dossier backend/ :
    python migrate_statut.py
"""
import sys
import os

# Ajouter le dossier courant au path pour importer la config
sys.path.insert(0, os.path.dirname(__file__))

from app.config import settings
from sqlalchemy import create_engine, text

def run_migration():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text(
                "ALTER TABLE consultations "
                "MODIFY COLUMN statut VARCHAR(30) NOT NULL DEFAULT 'en attente'"
            ))
            conn.commit()
            print("OK - Migration reussie : colonne statut convertie en VARCHAR(30)")
        except Exception as e:
            if "doesn't exist" in str(e).lower():
                print("WARN - La table 'consultations' n'existe pas encore.")
            elif "varchar" in str(e).lower() or "already" in str(e).lower():
                print("INFO - Colonne deja en VARCHAR, migration ignoree.")
            else:
                print(f"ERREUR ALTER TABLE : {e}")

        # Corriger les enregistrements avec statut vide (crees avant la migration)
        try:
            result = conn.execute(text(
                "UPDATE consultations SET statut = 'en_attente_medecin' "
                "WHERE (statut = '' OR statut IS NULL) AND medecin_id IS NOT NULL"
            ))
            conn.execute(text(
                "UPDATE consultations SET statut = 'en attente' "
                "WHERE statut = '' OR statut IS NULL"
            ))
            conn.commit()
            print("OK - Statuts vides corriges")
        except Exception as e:
            print(f"ERREUR UPDATE : {e}")

if __name__ == "__main__":
    run_migration()
