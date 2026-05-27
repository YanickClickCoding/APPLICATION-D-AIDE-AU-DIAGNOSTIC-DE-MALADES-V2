"""Ajout des FK InnoDB réelles avec gestion des données orphelines"""
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='',
                       database='gasa_sad_ia _v2.sql', port=3306, charset='utf8mb4',
                       autocommit=True)
cur = conn.cursor()

# Désactiver temporairement les FK checks pour nettoyage
cur.execute("SET FOREIGN_KEY_CHECKS=0")

# Nettoyer les données orphelines avant d'ajouter les FK
cleanups = [
    # consultations dont le patient n'existe pas
    "DELETE FROM consultations WHERE patient_id IS NOT NULL AND patient_id NOT IN (SELECT patient_id FROM patients)",
    # consultations dont le medecin n'existe pas
    "UPDATE consultations SET medecin_id=NULL WHERE medecin_id IS NOT NULL AND medecin_id NOT IN (SELECT medecin_id FROM medecins)",
    # analyses_ia sans consultation
    "DELETE FROM analyses_ia WHERE consultation_id NOT IN (SELECT consultation_id FROM consultations)",
    # diagnostics sans consultation
    "DELETE FROM diagnostics WHERE consultation_id NOT IN (SELECT consultation_id FROM consultations)",
    # diagnostics sans dossier
    "DELETE FROM diagnostics WHERE dossier_id NOT IN (SELECT dossier_id FROM dossiers_medicaux)",
    # examens sans consultation
    "DELETE FROM examens WHERE consultation_id NOT IN (SELECT consultation_id FROM consultations)",
    # signes_vitaux sans consultation
    "DELETE FROM signes_vitaux WHERE consultation_id NOT IN (SELECT consultation_id FROM consultations)",
    # symptomes sans consultation
    "DELETE FROM symptomes WHERE consultation_id NOT IN (SELECT consultation_id FROM consultations)",
    # traitements sans diagnostic
    "DELETE FROM traitements WHERE diagnostic_id NOT IN (SELECT diagnostic_id FROM diagnostics)",
    # ordonnances sans traitement
    "DELETE FROM ordonnances WHERE traitement_id NOT IN (SELECT traitement_id FROM traitements)",
    # ordonnances sans patient
    "DELETE FROM ordonnances WHERE patient_id NOT IN (SELECT patient_id FROM patients)",
    # ordonnances sans dossier
    "DELETE FROM ordonnances WHERE dossier_id NOT IN (SELECT dossier_id FROM dossiers_medicaux)",
    # medicaments sans ordonnance
    "DELETE FROM medicaments WHERE ordonnance_id NOT IN (SELECT ordonnance_id FROM ordonnances)",
    # suivis sans patient
    "DELETE FROM suivis WHERE patient_id IS NOT NULL AND patient_id NOT IN (SELECT patient_id FROM patients)",
    # dossiers_medicaux sans patient
    "DELETE FROM dossiers_medicaux WHERE patient_id NOT IN (SELECT patient_id FROM patients)",
    # historique_prediction sans patient
    "DELETE FROM historique_prediction WHERE patient_id NOT IN (SELECT patient_id FROM patients)",
]

print("Nettoyage des orphelins...")
for sql in cleanups:
    cur.execute(sql)
    if cur.rowcount > 0:
        print(f"  Supprime {cur.rowcount} ligne(s): {sql[:70]}...")

cur.execute("SET FOREIGN_KEY_CHECKS=1")

# Définition des FK à ajouter
fk_definitions = [
    # consultations
    ("consultations", "fk_cons_patient",     "patient_id",       "patients",          "patient_id"),
    ("consultations", "fk_cons_medecin",      "medecin_id",       "medecins",          "medecin_id"),
    # dossiers_medicaux
    ("dossiers_medicaux", "fk_doss_patient",  "patient_id",       "patients",          "patient_id"),
    # analyses_ia
    ("analyses_ia",   "fk_anal_cons",         "consultation_id",  "consultations",     "consultation_id"),
    # diagnostics
    ("diagnostics",   "fk_diag_cons",         "consultation_id",  "consultations",     "consultation_id"),
    ("diagnostics",   "fk_diag_analyse",      "analyse_ia_id",    "analyses_ia",       "analyse_id"),
    ("diagnostics",   "fk_diag_medecin",      "medecin_id",       "medecins",          "medecin_id"),
    ("diagnostics",   "fk_diag_dossier",      "dossier_id",       "dossiers_medicaux", "dossier_id"),
    # examens
    ("examens",       "fk_exam_cons",         "consultation_id",  "consultations",     "consultation_id"),
    # signes_vitaux
    ("signes_vitaux", "fk_sv_cons",           "consultation_id",  "consultations",     "consultation_id"),
    # symptomes
    ("symptomes",     "fk_symp_cons",         "consultation_id",  "consultations",     "consultation_id"),
    # traitements
    ("traitements",   "fk_trait_diag",        "diagnostic_id",    "diagnostics",       "diagnostic_id"),
    # ordonnances
    ("ordonnances",   "fk_ord_trait",         "traitement_id",    "traitements",       "traitement_id"),
    ("ordonnances",   "fk_ord_medecin",       "medecin_id",       "medecins",          "medecin_id"),
    ("ordonnances",   "fk_ord_patient",       "patient_id",       "patients",          "patient_id"),
    ("ordonnances",   "fk_ord_dossier",       "dossier_id",       "dossiers_medicaux", "dossier_id"),
    # medicaments
    ("medicaments",   "fk_med_ord",           "ordonnance_id",    "ordonnances",       "ordonnance_id"),
    # suivis
    ("suivis",        "fk_suiv_patient",      "patient_id",       "patients",          "patient_id"),
    ("suivis",        "fk_suiv_cons",         "consultation_id",  "consultations",     "consultation_id"),
    ("suivis",        "fk_suiv_diag",         "diagnostic_id",    "diagnostics",       "diagnostic_id"),
    ("suivis",        "fk_suiv_trait",        "traitement_id",    "traitements",       "traitement_id"),
    ("suivis",        "fk_suiv_dossier",      "dossier_id",       "dossiers_medicaux", "dossier_id"),
    # historique_prediction
    ("historique_prediction", "fk_hist_patient", "patient_id",    "patients",          "patient_id"),
    ("historique_prediction", "fk_hist_cons",    "consultation_id","consultations",    "consultation_id"),
]

print("\nAjout des FK...")
ok, skipped = 0, 0
for table, fk_name, col, ref_table, ref_col in fk_definitions:
    # Vérifier si la colonne est nullable (si oui: SET NULL, sinon: CASCADE ou RESTRICT)
    cur.execute(f"SELECT IS_NULLABLE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='{table}' AND COLUMN_NAME='{col}'")
    row = cur.fetchone()
    if not row:
        print(f"  SKIP {table}.{col} (colonne absente)")
        skipped += 1
        continue
    nullable = row[0] == 'YES'
    on_delete = "SET NULL" if nullable else "CASCADE"
    try:
        cur.execute(f"""
            ALTER TABLE `{table}`
            ADD CONSTRAINT `{fk_name}`
            FOREIGN KEY (`{col}`) REFERENCES `{ref_table}`(`{ref_col}`)
            ON DELETE {on_delete} ON UPDATE CASCADE
        """)
        print(f"  OK  {table}.{col} -> {ref_table}.{ref_col}  (ON DELETE {on_delete})")
        ok += 1
    except Exception as e:
        print(f"  ERR {table}.{col}: {e}")
        skipped += 1

print(f"\nFK ajoutees: {ok}  ignorees/erreur: {skipped}")
conn.close()
