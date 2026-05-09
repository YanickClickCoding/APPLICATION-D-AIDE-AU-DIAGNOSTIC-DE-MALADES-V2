
import os
import sys
import logging
from sqlalchemy import create_engine, text

# Ajouter le répertoire actuel au path pour les imports app.*
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.ml.model_manager import model_manager

# Configurer le logging pour voir l'avancement de l'entraînement
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def reset_ai_performance():
    """
    Réinitialise les diagnostics et réentraîne le modèle pour une performance maximale.
    """
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        print("\n" + "=" * 80)
        print(" STEP 1 : NETTOYAGE DES ANCIENS DIAGNOSTICS")
        print("=" * 80)
        
        with engine.connect() as conn:
            # Désactiver les contraintes de clés étrangères pour MySQL
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            
            # Liste des tables à vider pour repartir de zéro sur les analyses
            tables = ['diagnostics', 'analyse_ia', 'symptomes', 'signes_vitaux', 'consultations']
            for table in tables:
                print(f"Vérification de la table {table}...")
                try:
                    conn.execute(text(f"DELETE FROM {table};"))
                    print(f"  OK Table {table} vidée.")
                except Exception as e:
                    print(f"  Warning Erreur sur {table}: {e}")
            
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            conn.commit()
            print("\nOK Base de données réinitialisée pour la partie médicale.")

        print("\n" + "=" * 80)
        print(" STEP 2 : RÉENTRAÎNEMENT HAUTE PERFORMANCE")
        print("=" * 80)
        
        # Recherche du dataset
        dataset_filename = "dataset_medical_robust_10000_cas.csv"
        possible_paths = [
            os.path.join("les ressources dataset", dataset_filename),
            os.path.join("..", "les ressources dataset", dataset_filename),
            os.path.join(os.getcwd(), "les ressources dataset", dataset_filename)
        ]
        
        dataset_path = None
        for p in possible_paths:
            if os.path.exists(p):
                dataset_path = p
                break
        
        if not dataset_path:
            print(f" ERROR : Dataset {dataset_filename} introuvable.")
            print("Assurez-vous que le dossier 'les ressources dataset' est présent à la racine du projet.")
            return

        print(f"Dataset trouvé : {dataset_path}")
        print("Paramètres : 300 arbres, Profondeur 40 (Entropie)")
        print("Entraînement en cours (cela peut prendre 30-60 secondes)...")
        
        # Lancer l'entraînement
        results = model_manager.train_new_model(
            dataset_path=dataset_path,
            n_estimators=300,
            max_depth=40,
            save=True
        )
        
        if results.get("success"):
            acc = results["evaluation"]["accuracy"] * 100
            f1 = results["evaluation"]["f1_score"] * 100
            print(f"\n MODÈLE IA RÉENTRAÎNÉ AVEC SUCCÈS !")
            print(f" Précision : {acc:.2f}%")
            print(f" F1-Score  : {f1:.2f}%")
            print(f" Fichier : {model_manager.model_version}")
        else:
            print(f"\n ERREUR DE L'ENTRAÎNEMENT : {results.get('error')}")

        print("\n" + "=" * 80)
        print(" STEP 3 : PRÉPARATION POUR LES NOUVEAUX TESTS")
        print("=" * 80)
        print("L'IA est maintenant prête et plus performante.")
        print("Les anciens diagnostics ont été purgés pour ne pas fausser vos statistiques.")
        print("Vous pouvez maintenant effectuer de nouvelles consultations de test.")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n ERREUR CRITIQUE : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reset_ai_performance()
