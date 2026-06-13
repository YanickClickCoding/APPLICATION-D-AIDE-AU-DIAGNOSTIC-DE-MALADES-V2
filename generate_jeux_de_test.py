import json
import os

# Liste des 50 maladies déjà faites
done_diseases = [
    "Hypertension", "Infarctus du myocarde", "Insuffisance cardiaque", "Arythmie cardiaque", "Angine de poitrine",
    "Asthme", "Pneumonie", "BPCO", "Tuberculose", "COVID-19",
    "Diabète Type 2", "Diabète Type 1", "Hypothyroïdie", "Hyperthyroïdie", "Syndrome de Cushing",
    "Gastrite", "RGO", "Ulcère gastro-duodénal", "Hépatite B", "Cirrhose",
    "Insuffisance rénale chronique", "Lithiase rénale", "Cystite",
    "Migraine", "Épilepsie", "Accident vasculaire cérébral", "Parkinson",
    "Grippe", "Typhoïde", "Malaria", "VIH/SIDA", "Dengue",
    "Anémie ferriprive", "Leucémie", "Thrombose veineuse profonde",
    "Arthrite rhumatoïde", "Lupus érythémateux systémique", "Goutte",
    "Psoriasis", "Eczéma", "Dermatite atopique", "Urticaire",
    "Conjonctivite", "Glaucome",
    "Rhinite allergique", "Pancréatite", "Syndrome du côlon irritable", "Embolie pulmonaire", "Sclérose en plaques", "Fibromyalgie", "Mononucléose infectieuse"
]

def is_done(disease):
    d_lower = disease.lower().replace(" ", "").replace("-", "").replace("é", "e").replace("è", "e")
    for d in done_diseases:
        d_cmp = d.lower().replace(" ", "").replace("-", "").replace("é", "e").replace("è", "e")
        if d_lower in d_cmp or d_cmp in d_lower:
            return True
    return False

json_path = r"les ressources dataset\dataset_medical_robust_10000_cas.json"

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print("Erreur de lecture du dataset:", e)
    exit(1)

disease_cases = {}
for row in data:
    maladie = row.get("Maladie_Diagnostic")
    if not maladie:
        continue
    if maladie not in disease_cases:
        disease_cases[maladie] = row

out_lines = []
out_lines.append("# Jeux de Test — Suite des Maladies (51 à 122)\n")

count = 51
for maladie, row in sorted(disease_cases.items()):
    if is_done(maladie):
        continue
    
    out_lines.append(f"### {count}. {maladie}")
    out_lines.append("| Signes vitaux | Valeur |")
    out_lines.append("|---|---|")
    out_lines.append(f"| Âge | {row.get('Age')} ans, {row.get('Sexe')} |")
    
    ant_med = row.get('Antecedents_Medicaux', 'Aucun')
    if ant_med != "Aucun":
        out_lines.append(f"| **Antécédents personnels** | {ant_med} |")
        
    out_lines.append(f"| Tension systolique | {row.get('Vital_Tension Systolique (mmHg)', 120):.0f} mmHg |")
    out_lines.append(f"| Tension diastolique | {row.get('Vital_Tension Diastolique (mmHg)', 80):.0f} mmHg |")
    out_lines.append(f"| Fréquence cardiaque | {row.get('Vital_Fréquence Cardiaque (bpm)', row.get('Vital_FrǸquence Cardiaque (bpm)', 75)):.0f} bpm |")
    out_lines.append(f"| Température | {row.get('Vital_Température (°C)', row.get('Vital_TempǸrature (C)', 37.0)):.1f} °C |")
    out_lines.append(f"| Fréquence respiratoire | {row.get('Vital_Fréquence Respiratoire (resp/min)', row.get('Vital_FrǸquence Respiratoire (resp/min)', 16)):.0f} resp/min |")
    out_lines.append(f"| Saturation O2 | {row.get('Vital_Saturation O2 (%)', 98):.0f} % |")
    out_lines.append(f"| IMC | {row.get('Vital_IMC (kg/m²)', row.get('Vital_IMC (kg/m)', 22.0)):.1f} |")
    out_lines.append(f"| Durée symptômes | {row.get('Duree_Symptomes_Jours', 5)} j |")
    
    sev = str(row.get('Severite', 'modere')).lower().replace('lǸgre', 'leger')
    out_lines.append(f"| Sévérité | {sev} |")
    out_lines.append("\n**Symptômes :**\n")
    out_lines.append("| Symptôme | Sévérité | Durée |")
    out_lines.append("|----------|----------|-------|")
    
    symps = str(row.get("Symptomes_Rapportes", "")).replace('Ǹ', 'e').split(",")
    for s in symps:
        s = s.strip()
        if s:
            sev_symp = "MODERE"
            if "critique" in sev: sev_symp = "SEVERE"
            out_lines.append(f"| {s} | {sev_symp} | {row.get('Duree_Symptomes_Jours', 5)} j |")
    
    out_lines.append("\n**Examens à ajouter :**")
    has_exam = False
    for k, v in row.items():
        if k.startswith("Lab_") and isinstance(v, (int, float)) and v > 0:
            k_clean = k.replace('Lab_', '').replace('Ǹ', 'e')
            if any(x in k_clean for x in ["Glucose", "Hémoglobine", "Hemoglobine", "Créatinine", "Creatinine", "ALT", "Cholest", "CRP", "Globules"]):
                out_lines.append(f"- BIOLOGIE → {k_clean}: `{v}`")
                has_exam = True
    if not has_exam:
         out_lines.append("- Aucun examen anormal notable dans cet exemple.")
    out_lines.append("\n---\n")
    count += 1

output_file = "JEUX_DE_TEST_123_MALADIES_SUITE.md"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("\n".join(out_lines))
print(f"Fichier {output_file} généré avec succès ! ({count - 51} maladies ajoutées)")
