"""
Enrichissement des symptômes pour les 122 maladies du dataset.
Même approche que pour l'insuffisance rénale :
- Pool complet de symptômes médicalement validés par maladie
- Distribution variée 3-6 symptômes par cas
- Symptômes pathognomoniques garantis dans ~70% des cas
"""
import pandas as pd
import random
import collections

random.seed(42)

df = pd.read_csv("les ressources dataset/dataset_medical_robust_enhanced.csv")

# ============================================================
# POOLS DE SYMPTOMES PAR MALADIE
# ============================================================
POOLS = {

    # ── INFECTIEUSES ─────────────────────────────────────────
    "COVID-19": {
        "core": ["Perte d'odorat", "Perte de goût"],
        "pool": ["Fièvre", "Toux sèche", "Essoufflement", "Fatigue", "Maux de tête",
                 "Douleurs musculaires", "Mal de gorge", "Congestion nasale", "Diarrhée",
                 "Nausées", "Vomissements", "Douleur thoracique", "Perte d'appétit",
                 "Frissons", "Confusion", "Éruption cutanée"],
    },
    "Grippe": {
        "core": ["Fièvre élevée", "Douleurs musculaires"],
        "pool": ["Toux", "Mal de gorge", "Congestion nasale", "Maux de tête",
                 "Fatigue", "Frissons", "Sueurs", "Perte d'appétit", "Nausées",
                 "Vomissements", "Courbatures", "Essoufflement"],
    },
    "Influenza A/B": {
        "core": ["Fièvre élevée", "Douleurs musculaires"],
        "pool": ["Toux", "Mal de gorge", "Fatigue", "Maux de tête", "Frissons",
                 "Congestion nasale", "Perte d'appétit", "Nausées", "Sueurs", "Courbatures"],
    },
    "Pneumonie": {
        "core": ["Fièvre", "Toux productive"],
        "pool": ["Essoufflement", "Douleur thoracique", "Frissons", "Fatigue",
                 "Crachats purulents", "Expectorations", "Sueurs nocturnes",
                 "Confusion", "Perte d'appétit", "Nausées", "Cyanose"],
    },
    "Tuberculose": {
        "core": ["Hémoptysie", "Toux persistante"],
        "pool": ["Sueurs nocturnes", "Perte de poids", "Fièvre", "Fatigue",
                 "Douleur thoracique", "Essoufflement", "Ganglions enflés",
                 "Perte d'appétit", "Frissons", "Anorexie"],
    },
    "Dengue": {
        "core": ["Douleur oculaire", "Fièvre"],
        "pool": ["Douleurs articulaires", "Éruption cutanée", "Maux de tête",
                 "Vomissements", "Nausées", "Fatigue", "Douleurs musculaires",
                 "Saignement des gencives", "Pétéchies", "Rash"],
    },
    "Malaria": {
        "core": ["Fièvre intermittente", "Frissons"],
        "pool": ["Sueurs", "Maux de tête", "Douleurs musculaires", "Fatigue",
                 "Nausées", "Vomissements", "Anémie", "Splénomégalie",
                 "Confusion", "Jaunisse", "Pâleur"],
    },
    "Hépatite A": {
        "core": ["Jaunisse", "Urine foncée"],
        "pool": ["Nausées", "Selles pâles", "Douleurs abdominales", "Fatigue",
                 "Perte d'appétit", "Fièvre", "Vomissements", "Démangeaisons",
                 "Hépatomégalie", "Malaise"],
    },
    "Hépatite B": {
        "core": ["Jaunisse", "Urine foncée"],
        "pool": ["Démangeaisons", "Nausées", "Fatigue", "Douleurs abdominales",
                 "Selles pâles", "Vomissements", "Perte d'appétit", "Fièvre",
                 "Hépatomégalie", "Malaise", "Douleur articulaire"],
    },
    "Hépatite C": {
        "core": ["Jaunisse", "Fatigue"],
        "pool": ["Nausées", "Douleurs abdominales", "Urine foncée", "Perte d'appétit",
                 "Démangeaisons", "Douleur musculaire", "Saignements", "Confusion",
                 "Hépatomégalie", "Selles pâles"],
    },
    "VIH/SIDA": {
        "core": ["Ganglions enflés", "Infections récurrentes"],
        "pool": ["Fièvre", "Fatigue", "Diarrhée", "Perte de poids", "Sueurs nocturnes",
                 "Candidose buccale", "Éruption cutanée", "Maux de tête",
                 "Douleurs musculaires", "Perte d'appétit"],
    },
    "Mononucléose": {
        "core": ["Mal de gorge", "Ganglions enflés"],
        "pool": ["Fièvre", "Fatigue", "Maux de tête", "Splénomégalie",
                 "Amygdalite", "Éruption cutanée", "Perte d'appétit",
                 "Douleurs musculaires", "Douleur abdominale"],
    },
    "Varicelle": {
        "core": ["Démangeaisons", "Éruption vésiculaire"],
        "pool": ["Fièvre", "Malaise", "Fatigue", "Perte d'appétit",
                 "Maux de tête", "Éruption cutanée", "Vésicules",
                 "Croûtes", "Irritabilité"],
    },
    "Rougeole": {
        "core": ["Éruption cutanée", "Fièvre"],
        "pool": ["Toux", "Yeux rouges", "Congestion nasale", "Malaise",
                 "Fatigue", "Sensibilité à la lumière", "Perte d'appétit",
                 "Taches de Koplik", "Conjonctivite"],
    },
    "Typhoïde": {
        "core": ["Fièvre", "Rash rose"],
        "pool": ["Constipation", "Délire", "Faiblesse", "Maux de tête",
                 "Douleurs abdominales", "Nausées", "Diarrhée", "Splénomégalie",
                 "Perte d'appétit", "Bradycardie relative"],
    },
    "Salmonellose": {
        "core": ["Diarrhée", "Crampes abdominales"],
        "pool": ["Fièvre", "Nausées", "Vomissements", "Frissons", "Maux de tête",
                 "Fatigue", "Perte d'appétit", "Sang dans les selles",
                 "Déshydratation", "Douleurs musculaires"],
    },
    "Angine streptococcique": {
        "core": ["Mal de gorge", "Rougeur pharyngée"],
        "pool": ["Fièvre", "Difficultés à avaler", "Ganglions enflés",
                 "Maux de tête", "Nausées", "Vomissements", "Frissons",
                 "Perte d'appétit", "Taches blanches pharyngées"],
    },
    "Sinusite": {
        "core": ["Douleur faciale", "Congestion nasale"],
        "pool": ["Maux de tête", "Perte d'odorat", "Fièvre", "Toux",
                 "Sécrétions nasales épaisses", "Douleur dentaire",
                 "Fatigue", "Gonflement facial", "Haleine désagréable"],
    },
    "Bronchite": {
        "core": ["Toux", "Expectorations"],
        "pool": ["Essoufflement", "Frissons", "Mal de gorge", "Fatigue",
                 "Fièvre légère", "Douleur thoracique", "Sifflement respiratoire",
                 "Congestion nasale", "Maux de tête"],
    },
    "Laryngite": {
        "core": ["Perte de voix", "Mal de gorge"],
        "pool": ["Difficultés à avaler", "Fièvre", "Toux sèche",
                 "Enrouement", "Douleur laryngée", "Fatigue",
                 "Ganglions enflés", "Irritation throat"],
    },
    "Otite": {
        "core": ["Otalgie", "Fièvre"],
        "pool": ["Écoulement auriculaire", "Vertiges", "Perte d'audition",
                 "Bourdonnements", "Nausées", "Maux de tête",
                 "Irritabilité", "Difficulté à entendre"],
    },
    "Conjonctivite": {
        "core": ["Rougeur oculaire", "Larmoiement"],
        "pool": ["Démangeaisons oculaires", "Écoulement", "Photophobie",
                 "Sensation de brûlure", "Yeux collants", "Gonflement des paupières",
                 "Vision floue légère", "Malaise"],
    },
    "Trachéite": {
        "core": ["Toux aboyante", "Stridor inspiratoire"],
        "pool": ["Fièvre", "Essoufflement", "Hoarseness", "Douleur thoracique",
                 "Difficultés à respirer", "Mal de gorge", "Fatigue"],
    },
    "Chlamydia": {
        "core": ["Souvent asymptomatique", "Écoulement urétral"],
        "pool": ["Dysurie", "Douleur pelvienne", "Cervicite", "Brûlures urinaires",
                 "Douleur testiculaire", "Urgence urinaire", "Saignement intermenstruel",
                 "Douleur lors des rapports"],
    },
    "Gonorrhée": {
        "core": ["Écoulement purulent", "Dysurie"],
        "pool": ["Cervicite", "Salpingite", "Urétrite", "Douleur pelvienne",
                 "Fièvre", "Douleur testiculaire", "Brûlures urinaires",
                 "Urgence urinaire", "Saignement anormal"],
    },
    "Syphilis": {
        "core": ["Chancre", "Rash"],
        "pool": ["Lymphadénopathie", "Fièvre", "Complications neurologiques",
                 "Malaise", "Douleurs articulaires", "Éruption palmoplantaire",
                 "Alopécie", "Ulcérations muqueuses"],
    },
    "Herpès génital": {
        "core": ["Vésicules", "Dysurie"],
        "pool": ["Douleur", "Récidives", "Malaise", "Fièvre", "Ganglions enflés",
                 "Brûlures génitales", "Prurit", "Démangeaisons génitales"],
    },
    "Condylomes": {
        "core": ["Verrues génitales", "Prurit"],
        "pool": ["Dyspareurie", "Saignement", "Irritation génitale",
                 "Brûlures génitales", "Inconfort"],
    },
    "Molluscum contagiosum": {
        "core": ["Petites bosses ombiliquées"],
        "pool": ["Démangeaisons légères", "Nodules cutanés", "Lésions groupées",
                 "Lésions dispersées", "Irritation cutanée"],
    },
    "Verrue": {
        "core": ["Excroissance cutanée"],
        "pool": ["Verrue plantaire douloureuse", "Verrue génitale", "Rugosité cutanée",
                 "Saignement", "Démangeaisons locales"],
    },

    # ── CARDIOVASCULAIRES ─────────────────────────────────────
    "Hypertension": {
        "core": ["Maux de tête", "Essoufflement"],
        "pool": ["Fatigue", "Vision floue", "Douleur thoracique", "Nervosité",
                 "Palpitations", "Épistaxis", "Vertiges", "Rougeur du visage",
                 "Acouphènes", "Douleur à la nuque"],
    },
    "Insuffisance cardiaque": {
        "core": ["Essoufflement", "Oedèmes"],
        "pool": ["Fatigue", "Gonflement des chevilles", "Prise de poids rapide",
                 "Toux nocturne", "Orthopnée", "Dyspnée de décubitus",
                 "Cyanose", "Palpitations", "Confusion", "Nausées",
                 "Perte d'appétit"],
    },
    "Infarctus du myocarde": {
        "core": ["Douleur thoracique sévère", "Sueurs froides"],
        "pool": ["Nausées", "Syncope", "Palpitations", "Essoufflement",
                 "Douleur au bras/épaule", "Douleur à la mâchoire",
                 "Anxiété", "Vomissements", "Fatigue soudaine", "Cyanose"],
    },
    "Accident vasculaire cérébral": {
        "core": ["Paralysie", "Difficultés à parler"],
        "pool": ["Maux de tête sévère", "Confusion", "Vision floue",
                 "Vertige soudain", "Faiblesse soudaine", "Engourdissement facial",
                 "Trouble de la marche", "Dysphagie", "Perte de conscience",
                 "Diplopie"],
    },
    "Arythmie cardiaque": {
        "core": ["Palpitations", "Sensation d'accélération"],
        "pool": ["Essoufflement", "Fatigue", "Vertiges", "Syncope",
                 "Douleur thoracique", "Anxiety", "Confusion",
                 "Pouls irrégulier", "Essoufflement d'effort"],
    },
    "Embolie pulmonaire": {
        "core": ["Essoufflement soudain", "Douleur thoracique"],
        "pool": ["Syncope", "Toux", "Cyanose", "Palpitations", "Hémoptysie",
                 "Tachycardie", "Anxiété", "Jambe gonflée", "Fièvre"],
    },
    "Angine de poitrine": {
        "core": ["Douleur thoracique", "Douleur au bras/épaule"],
        "pool": ["Essoufflement", "Sueurs froides", "Nausées", "Fatigue",
                 "Anxiété", "Douleur à la mâchoire", "Vertiges",
                 "Oppression thoracique", "Douleur irradiante"],
    },
    "Hypotension": {
        "core": ["Vertiges", "Évanouissement"],
        "pool": ["Vision floue", "Faiblesse", "Fatigue", "Perte de conscience",
                 "Nausées", "Pâleur", "Soif", "Confusion",
                 "Difficultés de concentration"],
    },
    "Myocardite": {
        "core": ["Douleur thoracique", "Essoufflement"],
        "pool": ["Syncope", "Fatigue", "Fièvre", "Palpitations",
                 "Tachycardie", "Oedèmes", "Vertiges", "Dyspnée d'effort",
                 "Douleurs musculaires"],
    },
    "Péricardite": {
        "core": ["Douleur thoracique pleurétique", "Frottement péricardique"],
        "pool": ["Essoufflement", "Fièvre", "Toux", "Fatigue",
                 "Douleur calmée penché en avant", "Palpitations",
                 "Malaise", "Sueurs"],
    },
    "Athérosclérose": {
        "core": ["Douleur thoracique", "Douleur à l'effort"],
        "pool": ["Essoufflement", "Fatigue", "Tachycardie",
                 "Douleur membre inférieur", "Claudication",
                 "Vertiges", "AVC transitoire"],
    },
    "Thrombose veineuse": {
        "core": ["Gonflement d'un membre", "Douleur"],
        "pool": ["Rougeur", "Chaleur", "Claudication", "Thrombose",
                 "Oedème unilatéral", "Sensibilité à la palpation",
                 "Cyanose distale", "Phlébite"],
    },

    # ── RESPIRATOIRES ──────────────────────────────────────────
    "Asthme": {
        "core": ["Respiration sifflante", "Oppression thoracique"],
        "pool": ["Toux", "Essoufflement", "Fatigue", "Dyspnée nocturne",
                 "Toux nocturne", "Wheezing", "Limitation de l'activité",
                 "Cyanose légère", "Expectoration"],
    },
    "BPCO": {
        "core": ["Toux chronique", "Expectorations"],
        "pool": ["Essoufflement", "Respiration sifflante", "Fatigue",
                 "Cyanose", "Dyspnée d'effort", "Perte de poids",
                 "Utilisation muscles accessoires", "Barrel chest"],
    },
    "Emphysème": {
        "core": ["Essoufflement", "Barrel chest"],
        "pool": ["Toux", "Cyanose", "Respiration sifflante", "Fatigue",
                 "Perte de poids", "Expectorations", "Dyspnée progressive"],
    },
    "Apnée du sommeil": {
        "core": ["Ronflement", "Somnolence diurne"],
        "pool": ["Maux de tête matinaux", "Dépression", "Irritabilité",
                 "Difficultés de concentration", "Insomnie", "Fatigue chronique",
                 "Pauses respiratoires nocturnes", "Nycturie", "Bouche sèche au réveil"],
    },

    # ── GASTRO-INTESTINALES ─────────────────────────────────────
    "Gastrite": {
        "core": ["Brûlures d'estomac", "Douleurs abdominales"],
        "pool": ["Nausées", "Perte d'appétit", "Vomissements",
                 "Ballonnements", "Éructations", "Satiété précoce",
                 "Méléna", "Régurgitation acide"],
    },
    "Gastroentérite": {
        "core": ["Diarrhée", "Vomissements"],
        "pool": ["Nausées", "Crampes abdominales", "Fièvre", "Fatigue",
                 "Perte d'appétit", "Déshydratation", "Malaise",
                 "Douleurs abdominales", "Frissons"],
    },
    "Ulcère gastro-duodénal": {
        "core": ["Douleurs abdominales", "Méléna"],
        "pool": ["Nausées", "Perte d'appétit", "Vomissements",
                 "Brûlures épigastriques", "Douleur à jeun",
                 "Satiété précoce", "Saignements digestifs", "Hématémèse"],
    },
    "Colite ulcéreuse": {
        "core": ["Diarrhée sanguinolente", "Besoin impérieux de déféquer"],
        "pool": ["Crampes abdominales", "Fatigue", "Fièvre", "Perte de poids",
                 "Douleur abdominale", "Urgence défécation", "Mucus dans selles",
                 "Anémie", "Anorexie"],
    },
    "Crohn": {
        "core": ["Diarrhée", "Douleurs abdominales"],
        "pool": ["Fatigue", "Malabsorption", "Fièvre", "Perte de poids",
                 "Saignements rectaux", "Fistules", "Anémie", "Nausées",
                 "Douleur à la déglutition"],
    },
    "Constipation chronique": {
        "core": ["Selles dures", "Infrequence des selles"],
        "pool": ["Efforts pour défécation", "Douleur abdominale",
                 "Sensation de blocage", "Ballonnements", "Fatigue",
                 "Gaz", "Sensation d'évacuation incomplète"],
    },
    "Syndrome du côlon irritable": {
        "core": ["Douleurs abdominales", "Alternance diarrhée-constipation"],
        "pool": ["Diarrhée", "Constipation", "Gaz", "Mucus dans les selles",
                 "Ballonnements", "Fatigue", "Nausées", "Urgence défécation",
                 "Douleur soulagée par défécation"],
    },
    "RGO": {
        "core": ["Brûlures d'estomac", "Régurgitation"],
        "pool": ["Rot", "Douleur thoracique", "Difficultés à avaler",
                 "Nausées", "Toux nocturne", "Enrouement matinal",
                 "Sensation de brûlure rétrosternale", "Perte d'appétit",
                 "Sensation de satiété rapide", "Sécheresse buccale"],
    },
    "Hernie hiatale": {
        "core": ["Brûlures d'estomac", "Régurgitation"],
        "pool": ["Rot", "Douleur thoracique", "Difficultés à avaler",
                 "Nausées", "Ballonnements", "Essoufflement postprandial",
                 "Douleur rétrosternale"],
    },
    "Cholécystite": {
        "core": ["Douleur abdominale supérieure", "Fièvre"],
        "pool": ["Nausées", "Vomissements", "Douleur après repas gras",
                 "Douleur irradiant épaule droite", "Frissons",
                 "Ictère léger", "Indigestion"],
    },
    "Pancréatite": {
        "core": ["Douleur abdominale sévère", "Nausées"],
        "pool": ["Vomissements", "Fièvre", "Choc", "Ballonnements",
                 "Douleur irradiant dans le dos", "Tachycardie",
                 "Ictère", "Perte d'appétit"],
    },
    "Cholangite": {
        "core": ["Fièvre", "Ictère"],
        "pool": ["Douleur abdominale", "Hypercholangiite", "Infection",
                 "Frissons", "Confusion", "Choc septique", "Nausées"],
    },
    "Cirrhose": {
        "core": ["Ascite", "Ictère"],
        "pool": ["Varices oesophagiennes", "Hypertension portale",
                 "Saignement digestif", "Hépatomégalie", "Encéphalopathie",
                 "Oedèmes", "Démangeaisons", "Fatigue",
                 "Gynécomastie", "Érythème palmaire"],
    },
    "Stéatose hépatique": {
        "core": ["Fatigue", "Hépatomégalie"],
        "pool": ["Douleur abdominale droite", "Ballonnements",
                 "Souvent asymptomatique", "Nausées", "Malaise",
                 "Perte d'appétit", "Légère jaunisse"],
    },

    # ── ENDOCRINIENNES ──────────────────────────────────────────
    "Diabète Type 1": {
        "core": ["Urination fréquente", "Soif excessive"],
        "pool": ["Perte de poids", "Fatigue", "Faim excessive", "Vision floue",
                 "Engourdissement", "Plaies lentes à cicatriser", "Infections fréquentes",
                 "Nausées", "Vomissements", "Douleurs abdominales", "Irritabilité"],
    },
    "Diabète Type 2": {
        "core": ["Urination fréquente", "Soif excessive"],
        "pool": ["Vision floue", "Fatigue", "Engourdissement des pieds",
                 "Plaies lentes à cicatriser", "Infections fréquentes",
                 "Perte de poids", "Faim excessive", "Sécheresse buccale",
                 "Maux de tête", "Vertiges"],
    },
    "Diabète gestationnel": {
        "core": ["Aucun symptôme habituellement", "Infections urinaires"],
        "pool": ["Vision floue", "Fatigue", "Infections fréquentes",
                 "Soif excessive", "Urination fréquente", "Nausées"],
    },
    "Hypothyroïdie": {
        "core": ["Fatigue", "Peau sèche"],
        "pool": ["Cheveux cassants", "Dépression", "Ralentissement intellectuel",
                 "Prise de poids", "Constipation", "Intolérance au froid",
                 "Bradycardie", "Oedème facial", "Voix rauque", "Myxoedème"],
    },
    "Hyperthyroïdie": {
        "core": ["Perte de poids", "Tremblements"],
        "pool": ["Intolérance à la chaleur", "Yeux saillants", "Insomnie",
                 "Palpitations", "Tachycardie", "Irritabilité", "Diarrhée",
                 "Transpiration excessive", "Fatigue", "Faiblesse musculaire"],
    },
    "Syndrome de Cushing": {
        "core": ["Vergetures", "Prise de poids"],
        "pool": ["Hypertension", "Fragilité osseuse", "Dépression",
                 "Grossissement du visage", "Bosse de bison", "Faiblesse musculaire",
                 "Acné", "Pilosité excessive", "Déséquilibre glycémique",
                 "Ecchymoses faciles"],
    },
    "Acromégalie": {
        "core": ["Agrandissement des mains/pieds", "Grossissement du visage"],
        "pool": ["Hypertension", "Apnée du sommeil", "Arthralgie",
                 "Transpiration excessive", "Maux de tête", "Vision floue",
                 "Fatigue", "Voix grave", "Espacement des dents"],
    },
    "Maladie d'Addison": {
        "core": ["Hyperpigmentation", "Fatigue"],
        "pool": ["Hypotension", "Nausées", "Évanouissements", "Perte de poids",
                 "Douleurs musculaires", "Anorexie", "Dépression",
                 "Soif excessive", "Hypoglycémie", "Sel craving"],
    },
    "Thyroïdite": {
        "core": ["Douleur thyroïdienne", "Fatigue"],
        "pool": ["Fièvre", "Mal de gorge", "Malaise", "Douleur au cou",
                 "Gonflement thyroïde", "Palpitations", "Hyperthyroïdie transitoire",
                 "Tremblements", "Sensibilité à la palpation"],
    },
    "Neuropathie diabétique": {
        "core": ["Engourdissement des pieds", "Douleur neuropathique"],
        "pool": ["Perte de réflexes", "Faiblesse", "Ulcères des pieds",
                 "Brûlures aux pieds", "Fourmillements", "Perte de sensibilité",
                 "Douleurs nocturnes", "Gangrène distale"],
    },
    "Rétinopathie diabétique": {
        "core": ["Vision floue", "Taches sombres"],
        "pool": ["Flotteurs", "Perte de vision progressive", "Vision centrale floue",
                 "Hémorragie rétinienne", "Scotome", "Perte de vision nocturne"],
    },
    "Hypercholestérolémie": {
        "core": ["Aucun symptôme", "Xanthomes"],
        "pool": ["Douleur thoracique", "Dépôts lipidiques aux paupières",
                 "Xanthomes tendineux", "Arc cornéen",
                 "Douleur membre inférieur", "AVC transitoire"],
    },

    # ── NEUROLOGIQUES ───────────────────────────────────────────
    "Alzheimer": {
        "core": ["Perte de mémoire", "Désorientation"],
        "pool": ["Comportement inapproprié", "Difficultés de langage",
                 "Perte d'autonomie", "Confusion", "Agitation",
                 "Dépression", "Hallucinations", "Troubles du sommeil",
                 "Incontinence", "Perte de poids"],
    },
    "Parkinson": {
        "core": ["Tremblements", "Rigidité"],
        "pool": ["Lenteur de mouvement", "Trouble de l'équilibre",
                 "Insomnie", "Dépression", "Démence", "Voix monotone",
                 "Écriture micrographique", "Visage inexpressif",
                 "Constipation", "Dysphagie"],
    },
    "Épilepsie": {
        "core": ["Convulsions", "Perte de conscience"],
        "pool": ["Aura", "Incontinence", "Fatigue post-critique",
                 "Chute", "Morsure de langue", "Absence",
                 "Mouvements automatiques", "Confusion post-critique"],
    },
    "Sclérose en plaques": {
        "core": ["Engourdissement", "Fatigue"],
        "pool": ["Dépression", "Vertiges", "Tremblements", "Vision floue",
                 "Spasticité", "Difficulté à marcher", "Faiblesse",
                 "Troubles cognitifs", "Névrite optique", "Troubles urinaires"],
    },
    "Sclérose latérale amyotrophique": {
        "core": ["Faiblesse musculaire", "Atrophie musculaire"],
        "pool": ["Difficultés à parler", "Difficultés à avaler", "Spasticité",
                 "Fasciculations", "Dyspnée", "Faiblesse des membres",
                 "Crampes musculaires", "Perte de poids"],
    },
    "Migraine": {
        "core": ["Maux de tête sévères", "Photophobie"],
        "pool": ["Nausées", "Phonophobie", "Vomissements", "Aura",
                 "Sensibilité aux odeurs", "Vertiges", "Fatigue",
                 "Douleur unilatérale", "Pulsation céphalique"],
    },
    "Céphale de tension": {
        "core": ["Maux de tête diffus", "Sensation de pression"],
        "pool": ["Fatigue", "Dépression", "Nervosité", "Tension nucale",
                 "Sensibilité du cuir chevelu", "Douleur bilatérale",
                 "Maux d'yeux", "Irritabilité"],
    },
    "Syndrome de Guillain-Barré": {
        "core": ["Faiblesse ascendante", "Paresthésies"],
        "pool": ["Dysphagie", "Dysarthrie", "Dyspnée", "Réflexes abolis",
                 "Douleur neuropathique", "Instabilité végétative",
                 "Paralysie faciale", "Difficultés à marcher"],
    },
    "Fibromyalgie": {
        "core": ["Douleurs musculaires diffuses", "Fatigue"],
        "pool": ["Troubles cognitifs", "Dépression", "Anxiété", "Insomnie",
                 "Raideur matinale", "Maux de tête", "Syndrome côlon irritable",
                 "Hyperesthésie", "Fatigue au réveil"],
    },

    # ── RHUMATOLOGIQUES ─────────────────────────────────────────
    "Goutte": {
        "core": ["Douleur articulaire soudaine", "Rougeur"],
        "pool": ["Chaleur", "Gonflement", "Fièvre", "Tophi",
                 "Hyperuricémie", "Douleur nocturne", "Sensibilité articulaire",
                 "Lithiase rénale associée"],
    },
    "Arthrite rhumatoïde": {
        "core": ["Raideur matinale", "Gonflement"],
        "pool": ["Fatigue", "Déformation progressive", "Malaise",
                 "Douleur articulaire", "Nodules rhumatoïdes", "Anémie",
                 "Fièvre légère", "Œil sec", "Douleur bilatérale"],
    },
    "Lupus érythémateux systémique": {
        "core": ["Éruption malaire", "Photosensibilité"],
        "pool": ["Douleurs articulaires", "Ulcères buccaux", "Anémie",
                 "Fièvre", "Fatigue", "Rash photosensible",
                 "Alopécie", "Pleurite", "Néphrite lupique"],
    },
    "Spondylarthrite ankylosante": {
        "core": ["Douleur lombaire", "Raideur matinale"],
        "pool": ["Restriction de mobilité", "Fatigue", "Uvéite",
                 "Douleur nocturne", "Douleur améliorée par l'exercice",
                 "Arthralgie périphérique", "Enthésite"],
    },
    "Syndrome de Sjögren": {
        "core": ["Sécheresse oculaire", "Sécheresse buccale"],
        "pool": ["Fatigue", "Arthralgie", "Lymphadénopathie",
                 "Difficultés à avaler", "Caries dentaires",
                 "Gonflement parotides", "Névrite périphérique"],
    },
    "Polymyosite/Dermatomyosite": {
        "core": ["Faiblesse musculaire", "Rash photosensible"],
        "pool": ["Dysphagie", "Arthralgie", "Dyspnée",
                 "Fièvre", "Fatigue", "Héliotrope éruption",
                 "Papules de Gottron", "Calcinose"],
    },
    "Sclérodermie": {
        "core": ["Durcissement cutané", "Raynaud"],
        "pool": ["Difficultés à avaler", "Dyspnée", "Reflux gastro-oesophagien",
                 "Télangiectasies", "Fibrose pulmonaire", "Douleur articulaire",
                 "Hypertension pulmonaire"],
    },

    # ── DERMATOLOGIQUES ─────────────────────────────────────────
    "Psoriasis": {
        "core": ["Plaques rouges squameuses", "Desquamation"],
        "pool": ["Prurit", "Saignement des plaques", "Arthralgie",
                 "Ongles dystrophiques", "Éruption chronique",
                 "Douleur articulaire", "Squames argentées"],
    },
    "Eczéma": {
        "core": ["Prurit", "Sécheresse cutanée"],
        "pool": ["Éruption", "Crevasses", "Vésicules", "Infection secondaire",
                 "Érythème", "Suintement", "Croûtes", "Lichénification"],
    },
    "Dermatite atopique": {
        "core": ["Prurit sévère", "Sécheresse cutanée"],
        "pool": ["Éruption", "Insomnie", "Infection secondaire",
                 "Érythème", "Squames", "Peau épaissie",
                 "Fissures cutanées", "Vésicules"],
    },
    "Acné": {
        "core": ["Comédones", "Papules"],
        "pool": ["Pustules", "Nodules", "Cicatrices", "Points noirs",
                 "Points blancs", "Kystes", "Rougeur cutanée",
                 "Prurit léger", "Peau grasse"],
    },
    "Urticaire": {
        "core": ["Éruption prurigineuse", "Angioedème"],
        "pool": ["Gonflement des lèvres", "Difficultés à respirer",
                 "Démangeaisons", "Plaques rouges", "Histaminémie",
                 "Brûlures cutanées", "Gonflement facial"],
    },
    "Pemphigus": {
        "core": ["Bulles", "Érosions"],
        "pool": ["Ulcérations", "Douleur", "Cicatrices", "Lésions muqueuses",
                 "Prurit", "Infection secondaire", "Fragilité cutanée"],
    },
    "Vitiligo": {
        "core": ["Taches blanches", "Dépigmentation"],
        "pool": ["Photosensibilité", "Impact psychologique", "Rash",
                 "Poliose", "Leucodermie", "Sensibilité solaire"],
    },

    # ── OPHTALMOLOGIQUES ────────────────────────────────────────
    "Glaucome": {
        "core": ["Vision tunnel", "Halos colorés"],
        "pool": ["Douleur oculaire", "Vision floue", "Nausées",
                 "Rougeur", "Perte de vision périphérique",
                 "Maux de tête", "Vomissements"],
    },
    "Cataracte": {
        "core": ["Vision floue", "Sensibilité à la lumière"],
        "pool": ["Vision jaunâtre", "Difficulté nocturne",
                 "Diplopie monoculaire", "Halos autour des lumières",
                 "Perte de contraste", "Éblouissement"],
    },
    "Kératite": {
        "core": ["Douleur oculaire", "Photophobie"],
        "pool": ["Larmoiement", "Vision floue", "Injection conjonctivale",
                 "Sensation de corps étranger", "Rougeur oculaire",
                 "Ulcère cornéen", "Blépharospasme"],
    },
    "Dégénérescence maculaire": {
        "core": ["Vision centrale floue", "Lignes ondulées"],
        "pool": ["Scotome central", "Perte de vision", "Taches sombres",
                 "Difficulté à lire", "Perte de contraste",
                 "Métamorphopsies", "Hémorragie rétinienne"],
    },
    "Astigmatisme": {
        "core": ["Vision floue à toutes distances", "Fatigue oculaire"],
        "pool": ["Maux de tête", "Plissement des yeux", "Yeux saillants",
                 "Diplopie légère", "Difficultés à lire",
                 "Vision déformée", "Éblouissement"],
    },
    "Myopie": {
        "core": ["Vision floue de loin", "Plissement des yeux"],
        "pool": ["Fatigue oculaire", "Maux de tête", "Vision nocturne difficile",
                 "Éblouissement", "Difficultés à conduire la nuit"],
    },
    "Hypermétropie": {
        "core": ["Vision floue de près", "Fatigue oculaire"],
        "pool": ["Maux de tête", "Nervosité", "Difficultés à lire",
                 "Yeux plissés", "Douleur oculaire"],
    },
    "Presbytie": {
        "core": ["Vision rapprochée floue", "Difficulté de lecture"],
        "pool": ["Fatigue oculaire", "Maux de tête",
                 "Nécessité d'éloigner la lecture", "Flou proche"],
    },

    # ── HÉMATOLOGIQUES ───────────────────────────────────────────
    "Anémie ferriprive": {
        "core": ["Fatigue", "Pâleur"],
        "pool": ["Essoufflement", "Vertiges", "Palpitations", "Maux de tête",
                 "Dysphagie", "Cheveux cassants", "Ongles cassants",
                 "Glossite", "Koïlonychie", "Irritabilité"],
    },
    "Anémie aplasique": {
        "core": ["Fatigue", "Saignements"],
        "pool": ["Ecchymoses", "Épistaxis", "Infections fréquentes",
                 "Pâleur", "Essoufflement", "Pétéchies",
                 "Fièvre", "Saignement gencives"],
    },
    "Anémie hémolytique": {
        "core": ["Fatigue", "Ictère"],
        "pool": ["Urines foncées", "Vertiges", "Fièvre", "Pâleur",
                 "Splénomégalie", "Lithiase biliaire", "Essoufflement",
                 "Palpitations"],
    },
    "Leucémie": {
        "core": ["Bleus faciles", "Douleurs osseuses"],
        "pool": ["Saignements", "Perte de poids", "Infections fréquentes",
                 "Fatigue", "Ganglions enflés", "Splénomégalie",
                 "Fièvre", "Pâleur", "Sueurs nocturnes"],
    },
    "Lymphome": {
        "core": ["Adénopathie", "Sueurs nocturnes"],
        "pool": ["Fièvre", "Perte de poids", "Fatigue", "Prurit",
                 "Splénomégalie", "Essoufflement",
                 "Douleurs thoraciques", "Infections fréquentes"],
    },
    "Polyglobulie": {
        "core": ["Visage rouge", "Prurit"],
        "pool": ["Vertiges", "Céphalées", "Saignements", "Thrombose",
                 "Splénomégalie", "Bourdonnements", "Vision floue",
                 "Hypertension"],
    },
    "Thrombocytémie": {
        "core": ["Paresthésies", "Thrombose"],
        "pool": ["Rougeur cutanée", "Ecchymoses", "Saignements",
                 "Maux de tête", "Vertiges", "Vision floue",
                 "Douleur aux extrémités", "Érythromélalgie"],
    },
    "Trouble de coagulation": {
        "core": ["Saignements prolongés", "Bleus faciles"],
        "pool": ["Épistaxis", "Hémorragie digestive", "Saignement gencives",
                 "Ménorragie", "Hématurie", "Hémarthrose",
                 "Pétéchies", "Purpura"],
    },

    # ── RÉNALES/URINAIRES ─────────────────────────────────────
    "Insuffisance rénale aiguë": {
        "core": ["Oligurie ou polyurie", "Anurie"],
        "pool": ["Oedèmes", "Hématurie", "Urine foncée", "Urine mousseuse",
                 "Dysurie", "Nycturie", "Fatigue", "Nausées", "Vomissements",
                 "Hypertension", "Confusion", "Crampes musculaires",
                 "Haleine urémique", "Goût métallique", "Douleur thoracique",
                 "Palpitations", "Essoufflement", "Pâleur", "Démangeaisons",
                 "Convulsions", "Douleurs abdominales", "Prise de poids rapide"],
    },
    "Insuffisance rénale chronique": {
        "core": ["Fatigue", "Démangeaisons"],
        "pool": ["Nycturie", "Urination fréquente", "Urine mousseuse",
                 "Hématurie", "Oligurie ou polyurie", "Anurie",
                 "Oedèmes", "Gonflement des chevilles", "Prise de poids rapide",
                 "Peau sèche", "Pâleur", "Teint grisâtre",
                 "Hypertension", "Essoufflement", "Palpitations", "Douleur thoracique",
                 "Crampes musculaires", "Engourdissements", "Confusion",
                 "Nausées", "Vomissements", "Douleurs abdominales",
                 "Haleine urémique", "Goût métallique", "Douleurs osseuses",
                 "Perte de poids", "Anorexie"],
    },
    "Glomérulonéphrite": {
        "core": ["Hématurie", "Protéinurie"],
        "pool": ["Oedèmes", "Hypertension", "Fatigue", "Maux de tête",
                 "Nausées", "Essoufflement", "Oligurie",
                 "Urine trouble", "Douleur lombaire"],
    },
    "Néphrotique": {
        "core": ["Oedèmes", "Protéinurie"],
        "pool": ["Albuminémie basse", "Hyperlipidémie", "Fatigue",
                 "Urine mousseuse", "Gonflement des paupières",
                 "Ascite", "Hypertension légère"],
    },
    "Lithiase rénale": {
        "core": ["Douleur colique intense", "Hématurie"],
        "pool": ["Nausées", "Fièvre", "Dysurie", "Vomissements",
                 "Douleur irradiant vers aine", "Urgence urinaire",
                 "Pollakiurie", "Urine trouble"],
    },
    "Cystite": {
        "core": ["Dysurie", "Urgence urinaire"],
        "pool": ["Fréquence urinaire", "Douleur pelvipérinéale",
                 "Malaise", "Brûlures mictionnelles", "Hématurie",
                 "Urine trouble", "Nycturie"],
    },
    "Pyélonéphrite": {
        "core": ["Fièvre", "Douleur lombaire"],
        "pool": ["Urgence urinaire", "Nausées", "Frissons",
                 "Dysurie", "Vomissements", "Frissons intenses",
                 "Hématurie", "Bactériurie", "Douleur costovertébrale"],
    },
    "Urétrite": {
        "core": ["Écoulement urétral", "Dysurie"],
        "pool": ["Urgence urinaire", "Douleur testiculaire",
                 "Fièvre légère", "Brûlures mictionnelles",
                 "Prurit urétral", "Écoulement purulent"],
    },
    "Hypertrophie bénigne de prostate": {
        "core": ["Difficultés à uriner", "Nycturie"],
        "pool": ["Flux faible", "Urgence urinaire", "Besoin fréquent d'uriner",
                 "Jet urinaire faible", "Sensation vidange incomplète",
                 "Pollakiurie", "Rétention urinaire"],
    },
    "Prostatite": {
        "core": ["Douleur périnéale", "Urgence urinaire"],
        "pool": ["Nocturia", "Fièvre", "Éjaculation douloureuse",
                 "Dysurie", "Douleur pelvienne", "Frissons",
                 "Difficulté à uriner", "Hématurie"],
    },

    # ── AUTRES ──────────────────────────────────────────────────
    "Anémie aplasique": {
        "core": ["Fatigue", "Saignements"],
        "pool": ["Ecchymoses", "Épistaxis", "Infections fréquentes", "Pâleur",
                 "Essoufflement", "Pétéchies", "Fièvre", "Saignement gencives"],
    },
}

# ============================================================
# MISE A JOUR DU DATASET
# ============================================================

def enrichir_maladie(df, maladie, core_symptoms, pool, core_prob=0.70):
    idx_list = df[df["Maladie_Diagnostic"] == maladie].index.tolist()
    if not idx_list:
        return 0
    for idx in idx_list:
        n = random.randint(3, 6)
        if core_symptoms and random.random() < core_prob:
            obligatoire = random.choice(core_symptoms)
            reste = [s for s in pool if s != obligatoire]
            autres = random.sample(reste, min(n - 1, len(reste)))
            df.at[idx, "Symptomes_Rapportes"] = obligatoire + ", " + ", ".join(autres)
        else:
            tous = pool + core_symptoms
            choix = random.sample(tous, min(n, len(tous)))
            df.at[idx, "Symptomes_Rapportes"] = ", ".join(choix)
    return len(idx_list)

total = 0
for maladie, cfg in POOLS.items():
    n = enrichir_maladie(df, maladie, cfg["core"], cfg["pool"])
    if n > 0:
        print(f"  ✓ {maladie}: {n} cas mis à jour")
    total += n

df.to_csv("les ressources dataset/dataset_medical_robust_enhanced.csv", index=False)
print(f"\nDataset sauvegardé. {total} cas enrichis sur {len(df)} total.")
print(f"Maladies couvertes: {len(POOLS)}")
