import sys
sys.path.insert(0, ".")
from app.ml.model_manager import model_manager
model_manager.load_latest_model()

ok_count = 0
alt_count = 0
rate_count = 0

def tester(nom_attendu, symptomes, vitaux_custom=None, examens=None, age=40, sexe="M", duree=7, severite="MODERE"):
    global ok_count, alt_count, rate_count
    vitaux = {"tension_systolique": 120, "tension_diastolique": 80,
              "frequence_cardiaque": 75, "frequence_respiratoire": 16,
              "temperature": 37.0, "saturation_oxygene": 98, "imc": 22}
    if vitaux_custom:
        vitaux.update(vitaux_custom)
    r = model_manager.predict({
        "age": age, "sexe": sexe, "duree_symptomes_jours": duree,
        "severite": severite, "vitaux": vitaux,
        "symptomes": symptomes, "examens": examens or []
    })
    diag = r["diagnostic_propose"]
    conf = round(r["confiance"] * 100, 1)
    alts = [a["diagnostic"] for a in r.get("diagnostics_alternatifs", [])]
    top = nom_attendu.lower() in diag.lower()
    alt_ok = any(nom_attendu.lower() in a.lower() for a in alts)
    if top:
        statut = "OK "
        ok_count += 1
    elif alt_ok:
        statut = "ALT"
        alt_count += 1
    else:
        statut = "RATE"
        rate_count += 1
    print(f"  [{statut}] {nom_attendu:40s} -> {diag:40s} ({conf}%)")

# ================================================================
print("=== INFECTIEUSES ===")
tester("COVID-19",               ["Perte d'odorat", "Perte de goût", "Fièvre", "Toux sèche", "Fatigue"])
tester("Tuberculose",            ["Hémoptysie", "Toux persistante", "Sueurs nocturnes", "Perte de poids"])
tester("Dengue",                 ["Douleur oculaire", "Fièvre", "Douleurs articulaires", "Éruption cutanée"], {"temperature": 39.5})
tester("Malaria",                ["Fièvre intermittente", "Frissons", "Sueurs", "Douleurs musculaires"], {"temperature": 40.0})
tester("VIH/SIDA",               ["Infections récurrentes", "Candidose buccale", "Fièvre", "Perte de poids"])
tester("Mononucléose",           ["Mal de gorge", "Ganglions enflés", "Fièvre", "Fatigue"], {"temperature": 38.5})
tester("Varicelle",              ["Éruption vésiculaire", "Démangeaisons", "Fièvre", "Malaise"], {"temperature": 38.2})
tester("Syphilis",               ["Chancre", "Rash", "Lymphadénopathie"])
tester("Salmonellose",           ["Diarrhée", "Crampes abdominales", "Fièvre", "Nausées"], {"temperature": 38.8})
tester("Angine streptococcique", ["Rougeur pharyngée", "Mal de gorge", "Fièvre", "Difficultés à avaler"], {"temperature": 38.5})
tester("Gonorrhée",              ["Écoulement purulent", "Dysurie", "Cervicite"])
tester("Chlamydia",              ["Souvent asymptomatique", "Cervicite", "Écoulement urétral"])
tester("Herpès génital",         ["Vésicules", "Récidives", "Dysurie", "Brûlures génitales"])
tester("Condylomes",             ["Verrues génitales", "Prurit", "Dyspareurie"])
tester("Rougeole",               ["Éruption cutanée", "Fièvre", "Toux", "Yeux rouges", "Taches de Koplik"], {"temperature": 39.0})

print()
print("=== CARDIOVASCULAIRES ===")
tester("Infarctus du myocarde",  ["Douleur thoracique sévère", "Sueurs froides", "Douleur au bras/épaule"], {"tension_systolique": 85, "frequence_cardiaque": 110})
tester("Accident vasculaire",    ["Paralysie", "Difficultés à parler", "Confusion", "Maux de tête sévère"], {"tension_systolique": 180})
tester("Insuffisance cardiaque", ["Essoufflement", "Oedèmes", "Gonflement des chevilles", "Toux nocturne"])
tester("Embolie pulmonaire",     ["Essoufflement soudain", "Douleur thoracique", "Syncope"], {"saturation_oxygene": 89, "frequence_cardiaque": 120})
tester("Péricardite",            ["Douleur thoracique pleurétique", "Frottement péricardique", "Fièvre"], {"temperature": 38.5})
tester("Hypertension",           ["Maux de tête", "Essoufflement", "Épistaxis"], {"tension_systolique": 170})
tester("Arythmie cardiaque",     ["Palpitations", "Sensation d'accélération", "Essoufflement", "Vertiges"], {"frequence_cardiaque": 145})
tester("Angine de poitrine",     ["Douleur thoracique", "Douleur au bras/épaule", "Douleur à la mâchoire"])
tester("Thrombose veineuse",     ["Gonflement d'un membre", "Douleur", "Rougeur", "Chaleur", "Claudication"])
tester("Polyglobulie",           ["Visage rouge", "Prurit", "Vertiges", "Céphalées"], {"tension_systolique": 155})

print()
print("=== RESPIRATOIRES ===")
tester("Pneumonie",              ["Fièvre", "Toux productive", "Crachats purulents", "Essoufflement"], {"temperature": 39.0, "saturation_oxygene": 92})
tester("Asthme",                 ["Respiration sifflante", "Oppression thoracique", "Toux", "Dyspnée nocturne"])
tester("BPCO",                   ["Toux chronique", "Expectorations", "Essoufflement", "Barrel chest"])
tester("Apnée du sommeil",       ["Ronflement", "Somnolence diurne", "Maux de tête matinaux", "Irritabilité"])
tester("Bronchite",              ["Toux", "Expectorations", "Essoufflement", "Frissons"], {"temperature": 38.0})
tester("Emphysème",              ["Essoufflement", "Barrel chest", "Toux", "Cyanose"])

print()
print("=== GASTRO-INTESTINALES ===")
tester("Cirrhose",               ["Ascite", "Ictère", "Varices oesophagiennes", "Gynécomastie"])
tester("Ulcère gastro-duodénal", ["Douleur à jeun", "Méléna", "Brûlures épigastriques"])
tester("Colite ulcéreuse",       ["Diarrhée sanguinolente", "Besoin impérieux de déféquer", "Crampes abdominales"])
tester("Pancréatite",            ["Douleur irradiant dans le dos", "Nausées", "Vomissements", "Fièvre"], {"temperature": 38.5})
tester("Cholécystite",           ["Douleur après repas gras", "Fièvre", "Douleur irradiant épaule droite"], {"temperature": 38.2})
tester("Crohn",                  ["Fistules", "Diarrhée", "Douleurs abdominales", "Perte de poids"])
tester("RGO",                    ["Brûlures d'estomac", "Régurgitation", "Rot", "Toux nocturne"])
tester("Syndrome du côlon irritable", ["Alternance diarrhée-constipation", "Mucus dans les selles", "Ballonnements"])
tester("Gastroentérite",         ["Diarrhée", "Vomissements", "Nausées", "Crampes abdominales", "Fièvre"], {"temperature": 38.0})

print()
print("=== ENDOCRINIENNES ===")
tester("Diabète Type 2",         ["Urination fréquente", "Soif excessive", "Vision floue", "Engourdissement des pieds"])
tester("Hypothyroïdie",          ["Fatigue", "Peau sèche", "Cheveux cassants", "Voix rauque", "Prise de poids"])
tester("Hyperthyroïdie",         ["Perte de poids", "Tremblements", "Intolérance à la chaleur", "Yeux saillants"], {"frequence_cardiaque": 115})
tester("Syndrome de Cushing",    ["Vergetures", "Bosse de bison", "Prise de poids", "Hypertension"], {"tension_systolique": 160})
tester("Acromégalie",            ["Agrandissement des mains/pieds", "Grossissement du visage", "Apnée du sommeil"])
tester("Maladie d'Addison",      ["Hyperpigmentation", "Fatigue", "Nausées"], {"tension_systolique": 85})
tester("Neuropathie diabétique", ["Engourdissement des pieds", "Douleur neuropathique", "Ulcères des pieds", "Perte de réflexes"])
tester("Rétinopathie diabétique", ["Vision floue", "Flotteurs", "Hémorragie rétinienne"])

print()
print("=== NEUROLOGIQUES ===")
tester("Alzheimer",              ["Perte de mémoire", "Désorientation", "Comportement inapproprié"], age=72)
tester("Parkinson",              ["Tremblements", "Rigidité", "Lenteur de mouvement", "Écriture micrographique"], age=65)
tester("Épilepsie",              ["Convulsions", "Perte de conscience", "Aura", "Incontinence"])
tester("Sclérose en plaques",    ["Engourdissement", "Névrite optique", "Fatigue", "Spasticité"], age=30)
tester("Migraine",               ["Maux de tête sévères", "Photophobie", "Phonophobie", "Aura"])
tester("Guillain-Barré",         ["Faiblesse ascendante", "Réflexes abolis", "Paresthésies", "Dyspnée"])
tester("Fibromyalgie",           ["Douleurs musculaires diffuses", "Fatigue", "Hyperesthésie", "Insomnie"])
tester("Sclérose latérale amyotrophique", ["Faiblesse musculaire", "Atrophie musculaire", "Fasciculations", "Difficultés à parler"])

print()
print("=== RHUMATOLOGIQUES ===")
tester("Lupus érythémateux",     ["Éruption malaire", "Photosensibilité", "Ulcères buccaux", "Douleurs articulaires"])
tester("Goutte",                 ["Douleur articulaire soudaine", "Tophi", "Rougeur", "Chaleur"])
tester("Arthrite rhumatoïde",    ["Raideur matinale", "Gonflement", "Nodules rhumatoïdes", "Déformation progressive"])
tester("Spondylarthrite ankylosante", ["Douleur lombaire", "Raideur matinale", "Uvéite", "Enthésite"])
tester("Syndrome de Sjögren",    ["Sécheresse oculaire", "Sécheresse buccale", "Fatigue", "Gonflement parotides"])
tester("Polymyosite",            ["Faiblesse musculaire", "Papules de Gottron", "Dysphagie", "Rash photosensible"])
tester("Sclérodermie",           ["Durcissement cutané", "Raynaud", "Télangiectasies", "Fibrose pulmonaire"])

print()
print("=== DERMATOLOGIQUES ===")
tester("Psoriasis",              ["Plaques rouges squameuses", "Desquamation", "Prurit", "Squames argentées"])
tester("Eczéma",                 ["Prurit", "Sécheresse cutanée", "Crevasses", "Vésicules"])
tester("Acné",                   ["Comédones", "Pustules", "Papules", "Nodules"])
tester("Vitiligo",               ["Taches blanches", "Dépigmentation", "Photosensibilité"])
tester("Pemphigus",              ["Bulles", "Érosions", "Ulcérations", "Douleur"])
tester("Urticaire",              ["Angioedème", "Gonflement des lèvres", "Éruption prurigineuse"])
tester("Dermatite atopique",     ["Prurit sévère", "Sécheresse cutanée", "Éruption", "Insomnie"])

print()
print("=== OPHTALMOLOGIQUES ===")
tester("Glaucome",               ["Vision tunnel", "Halos colorés", "Douleur oculaire", "Nausées"])
tester("Cataracte",              ["Vision floue", "Vision jaunâtre", "Diplopie monoculaire", "Halos autour des lumières"])
tester("Kératite",               ["Douleur oculaire", "Photophobie", "Ulcère cornéen", "Larmoiement"])
tester("Dégénérescence maculaire", ["Vision centrale floue", "Lignes ondulées", "Scotome central", "Métamorphopsies"])
tester("Rétinopathie diabétique", ["Vision floue", "Flotteurs", "Hémorragie rétinienne", "Taches sombres"])
tester("Conjonctivite",          ["Rougeur oculaire", "Larmoiement", "Démangeaisons oculaires", "Écoulement"])

print()
print("=== HÉMATOLOGIQUES ===")
tester("Anémie ferriprive",      ["Fatigue", "Pâleur", "Essoufflement", "Vertiges", "Cheveux cassants"])
tester("Leucémie",               ["Bleus faciles", "Douleurs osseuses", "Ganglions enflés", "Infections fréquentes", "Saignements"])
tester("Lymphome",               ["Adénopathie", "Sueurs nocturnes", "Perte de poids", "Fièvre"])
tester("Trouble de coagulation", ["Saignements prolongés", "Épistaxis", "Pétéchies", "Purpura", "Ménorragie"])

print()
print("=== RÉNALES / URINAIRES ===")
tester("Insuffisance rénale aiguë", ["Anurie", "Oedèmes", "Haleine urémique", "Confusion", "Hypertension"],
       {"tension_systolique": 160}, [{"nom": "Créatinine", "valeur_numerique": 6.5, "unite_mesure": "mg/dL"}])
tester("Insuffisance rénale chronique", ["Nycturie", "Démangeaisons", "Urine mousseuse", "Teint grisâtre", "Fatigue"],
       None, [{"nom": "TFG", "valeur_numerique": 18, "unite_mesure": "mL/min"}])
tester("Glomérulonéphrite",      ["Hématurie", "Protéinurie", "Oedèmes", "Hypertension"])
tester("Syndrome néphrotique",   ["Oedèmes", "Protéinurie", "Albuminémie basse", "Hyperlipidémie", "Urine mousseuse"])
tester("Lithiase rénale",        ["Douleur colique intense", "Hématurie", "Nausées", "Dysurie"])
tester("Cystite",                ["Dysurie", "Urgence urinaire", "Fréquence urinaire", "Brûlures mictionnelles"])
tester("Pyélonéphrite",          ["Fièvre", "Douleur lombaire", "Douleur costovertébrale", "Frissons"], {"temperature": 39.2})
tester("Hypertrophie bénigne de prostate", ["Difficultés à uriner", "Nycturie", "Flux faible", "Rétention urinaire"], sexe="M", age=65)
tester("Prostatite",             ["Douleur périnéale", "Éjaculation douloureuse", "Urgence urinaire", "Fièvre"], {"temperature": 38.5}, sexe="M")

print()
print("=" * 60)
total = ok_count + alt_count + rate_count
print(f"RESULTATS: {ok_count} OK | {alt_count} en alternative | {rate_count} rates")
print(f"Taux detection (top1):  {round(ok_count/total*100, 1)}%")
print(f"Taux detection (top3):  {round((ok_count+alt_count)/total*100, 1)}%")
print(f"Total teste: {total} maladies")
