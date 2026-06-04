"""
Model Manager Module - Singleton pour gérer le cycle de vie du modèle
Gère le chargement, l'entraînement et les prédictions
"""
import os
import json
import logging
from typing import Optional, Dict, List
from datetime import datetime
import pandas as pd
import numpy as np

from .data_preprocessing import DataPreprocessor
from .model_training import ModelTrainer
from .predictor import Predictor

logger = logging.getLogger(__name__)

# Chemins candidats pour trouver le dataset CSV
# Utiliser le dataset enrichi avec les 3 nouveaux examens microbiologiques (BAAR, Culture, Xpert)
_DATASET_FILENAME = "dataset_medical_robust_enhanced.csv"
_DATASET_FILENAME_FALLBACK = "dataset_medical_robust_10000_cas.csv"  # Fallback si le nouveau n'existe pas
# Traduction des noms de maladies : labels internes du modèle → noms affichés
DISEASE_DISPLAY_NAMES: dict[str, str] = {
    "Malaria": "Paludisme",
}

# ============================================================
# TABLE DE SYNONYMES — normalise TOUS les termes alternatifs
# vers le nom canonique utilisé dans le dataset d'entraînement.
# Clés en minuscules, valeurs = nom exact du dataset.
# ============================================================
SYNONYMES_SYMPTOMES: dict[str, str] = {
    # ── RÉNAUX / ŒDÈMES ──────────────────────────────────────
    "gonflement des pieds":              "Gonflement des chevilles",
    "pieds gonflés":                     "Gonflement des chevilles",
    "chevilles gonflées":                "Gonflement des chevilles",
    "oedème des pieds":                  "Gonflement des chevilles",
    "oedème des chevilles":              "Gonflement des chevilles",
    "œdème des pieds":                   "Gonflement des chevilles",
    "œdème des chevilles":               "Gonflement des chevilles",
    "jambes gonflées":                   "Gonflement des chevilles",
    "gonflement des membres inférieurs": "Gonflement des chevilles",
    "rétention d'eau":                   "Oedèmes",
    "rétention hydrique":                "Oedèmes",
    "corps gonflé":                      "Oedèmes",
    "gonflement du corps":               "Oedèmes",
    "absence d'urine":                   "Anurie",
    "pas d'urine":                       "Anurie",
    "urine absente":                     "Anurie",
    "pas uriner":                        "Anurie",
    "peu d'urine":                       "Oligurie ou polyurie",
    "urine rare":                        "Oligurie ou polyurie",
    "urine abondante":                   "Oligurie ou polyurie",
    "polyurie":                          "Oligurie ou polyurie",
    "oligurie":                          "Oligurie ou polyurie",
    "urine écumeuse":                    "Urine mousseuse",
    "urine avec mousse":                 "Urine mousseuse",
    "urine trouble":                     "Urine mousseuse",
    "sang dans les urines":              "Hématurie",
    "urines rouges":                     "Hématurie",
    "urines roses":                      "Hématurie",
    "uriner la nuit":                    "Nycturie",
    "se lever la nuit pour uriner":      "Nycturie",
    "odeur d'urine dans l'haleine":      "Haleine urémique",
    "haleine ammoniacale":               "Haleine urémique",
    "odeur ammoniaque":                  "Haleine urémique",
    "mauvaise haleine":                  "Haleine urémique",
    "goût amer":                         "Goût métallique",
    "arrière-goût métallique":           "Goût métallique",
    "crampes dans les jambes":           "Crampes musculaires",
    "crampes nocturnes":                 "Crampes musculaires",
    "fourmillements":                    "Engourdissements",
    "fourmillements dans les membres":   "Engourdissements",
    "engourdissement":                   "Engourdissements",
    "picotements":                       "Engourdissements",
    "peau qui gratte":                   "Démangeaisons",
    "prurit cutané":                     "Démangeaisons",
    "peau grise":                        "Teint grisâtre",
    "teint pâle grisâtre":               "Teint grisâtre",

    # ── CARDIOVASCULAIRES ─────────────────────────────────────
    "point dans la poitrine":            "Douleur thoracique",
    "douleur dans la poitrine":          "Douleur thoracique",
    "poitrine serrée":                   "Oppression thoracique",
    "chest pain":                        "Douleur thoracique",
    "battements du cœur rapides":        "Palpitations",
    "cœur qui bat vite":                 "Palpitations",
    "rythme cardiaque irrégulier":       "Palpitations",
    "battements irréguliers":            "Palpitations",
    "cœur qui saute":                    "Palpitations",
    "difficultés à respirer":            "Essoufflement",
    "manque d'air":                      "Essoufflement",
    "souffle court":                     "Essoufflement",
    "essoufflement":                     "Essoufflement",
    "dyspnée":                           "Essoufflement",
    "pression sanguine élevée":          "Hypertension",
    "tension artérielle élevée":         "Hypertension",
    "tension haute":                     "Hypertension",
    "jambe rouge et gonflée":            "Gonflement d'un membre",
    "jambe enflée":                      "Gonflement d'un membre",

    # ── RESPIRATOIRES ─────────────────────────────────────────
    "crachat":                           "Crachats purulents",
    "crachats":                          "Crachats purulents",
    "expectoration":                     "Expectorations",
    "mucus":                             "Expectorations",
    "toux grasse":                       "Toux productive",
    "toux avec mucus":                   "Toux productive",
    "sifflement en respirant":           "Respiration sifflante",
    "respiration difficile":             "Essoufflement",
    "halètement":                        "Essoufflement",
    "apnée":                             "Apnée du sommeil",
    "ronflement fort":                   "Ronflement",

    # ── DIGESTIFS ─────────────────────────────────────────────
    "douleur au ventre":                 "Douleurs abdominales",
    "ventre qui fait mal":               "Douleurs abdominales",
    "mal au ventre":                     "Douleurs abdominales",
    "crampes au ventre":                 "Crampes abdominales",
    "sang dans les selles":              "Diarrhée sanguinolente",
    "selles sanglantes":                 "Diarrhée sanguinolente",
    "selles noires":                     "Méléna",
    "sang noir dans les selles":         "Méléna",
    "vomissements de sang":              "Hématémèse",
    "vomir du sang":                     "Hématémèse",
    "brûlures à l'estomac":             "Brûlures d'estomac",
    "acidité":                           "Brûlures d'estomac",
    "reflux acide":                      "Régurgitation",
    "remontées acides":                  "Régurgitation",
    "remontées gastriques":              "Régurgitation",
    "reflux":                            "Reflux gastro-esophagien",
    "aller aux toilettes souvent":       "Diarrhée",
    "selles liquides":                   "Diarrhée",
    "pas de selles":                     "Constipation",
    "difficultés à déféquer":            "Constipation",
    "ventre gonflé":                     "Ballonnements",
    "ballonnement":                      "Ballonnements",

    # ── NEUROLOGIQUES ─────────────────────────────────────────
    "mal de tête":                       "Maux de tête",
    "mal à la tête":                     "Maux de tête",
    "céphalée":                          "Maux de tête",
    "céphalées":                         "Maux de tête",
    "migraine":                          "Maux de tête sévères",
    "tête qui tourne":                   "Vertiges",
    "vertiges":                          "Vertiges",
    "étourdissements":                   "Vertiges",
    "trous de mémoire":                  "Perte de mémoire",
    "oublis fréquents":                  "Perte de mémoire",
    "crise d'épilepsie":                 "Convulsions",
    "crise convulsive":                  "Convulsions",
    "attaque épileptique":               "Convulsions",
    "tremblements des mains":            "Tremblements",
    "mains qui tremblent":               "Tremblements",
    "brûlures dans les pieds":           "Engourdissement des pieds",
    "pieds qui brûlent":                 "Engourdissement des pieds",
    "picotements dans les pieds":        "Engourdissement des pieds",

    # ── ENDOCRINIENNES ────────────────────────────────────────
    "soif anormale":                     "Soif excessive",
    "soif intense":                      "Soif excessive",
    "grande soif":                       "Soif excessive",
    "uriner souvent":                    "Urination fréquente",
    "envies fréquentes d'uriner":        "Urination fréquente",
    "polyurie fréquente":               "Urination fréquente",
    "grossir sans raison":               "Prise de poids",
    "prise de poids inexpliquée":        "Prise de poids",
    "maigrir sans raison":               "Perte de poids",
    "perte de poids inexpliquée":        "Perte de poids",
    "pas d'appétit":                     "Anorexie",
    "manque d'appétit":                  "Perte d'appétit",
    "sans appétit":                      "Perte d'appétit",

    # ── DOULEURS GÉNÉRALES ────────────────────────────────────
    "courbatures":                       "Douleurs musculaires",
    "douleurs dans les muscles":         "Douleurs musculaires",
    "douleurs dans les os":              "Douleurs osseuses",
    "douleurs articulaires":             "Douleurs articulaires",
    "articulations douloureuses":        "Douleurs articulaires",
    "douleur aux articulations":         "Douleurs articulaires",
    "douleur au dos":                    "Douleur lombaire",
    "mal de dos":                        "Douleur lombaire",
    "douleur dans le dos":               "Douleur lombaire",
    "douleur au flanc":                  "Douleur lombaire",
    "douleur au rein":                   "Douleur lombaire",

    # ── CUTANÉS ───────────────────────────────────────────────
    "peau sèche":                        "Peau sèche",
    "peau qui pèle":                     "Desquamation",
    "peau qui s'écaille":                "Desquamation",
    "plaques rouges":                    "Éruption cutanée",
    "rougeurs cutanées":                 "Éruption cutanée",
    "boutons":                           "Pustules",
    "points noirs":                      "Comédones",
    "taches blanches sur la peau":       "Taches blanches",
    "peau décolorée":                    "Dépigmentation",
    "ampoules":                          "Bulles",
    "cloques":                           "Vésicules",

    # ── OCULAIRES ─────────────────────────────────────────────
    "vue brouillée":                     "Vision floue",
    "trouble de la vision":              "Vision floue",
    "voir flou":                         "Vision floue",
    "double vision":                     "Diplopie monoculaire",
    "voir double":                       "Diplopie monoculaire",
    "mouches volantes":                  "Flotteurs",
    "points noirs dans la vision":       "Flotteurs",
    "yeux qui piquent":                  "Démangeaisons oculaires",
    "yeux qui brûlent":                  "Démangeaisons oculaires",
    "yeux qui coulent":                  "Larmoiement",
    "larmes":                            "Larmoiement",
    "yeux rouges":                       "Rougeur oculaire",

    # ── GÉNÉRAUX ──────────────────────────────────────────────
    "fatigue intense":                   "Fatigue",
    "épuisement":                        "Fatigue",
    "se sentir fatigué":                 "Fatigue",
    "faiblesse générale":                "Faiblesse",
    "fièvre":                            "Fièvre",
    "température élevée":                "Fièvre",
    "fièvre élevée":                     "Fièvre élevée",
    "grosse fièvre":                     "Fièvre élevée",
    "frissons":                          "Frissons",
    "avoir froid":                       "Frissons",
    "nausée":                            "Nausées",
    "envie de vomir":                    "Nausées",
    "mal au cœur":                       "Nausées",
    "vomissement":                       "Vomissements",
    "vomir":                             "Vomissements",
    "perte de connaissance":             "Perte de conscience",
    "évanouissement":                    "Syncope",
    "tomber dans les pommes":            "Syncope",
    "ganglions":                         "Ganglions enflés",
    "ganglions gonflés":                 "Ganglions enflés",
    "sueurs nocturnes":                  "Sueurs nocturnes",
    "transpiration nocturne":            "Sueurs nocturnes",
    "pâleur":                            "Pâleur",
    "teint pâle":                        "Pâleur",
    "jaunisse":                          "Ictère",
    "peau jaune":                        "Ictère",
    "yeux jaunes":                       "Ictère",
    "saignement de nez":                 "Épistaxis",
    "saignement du nez":                 "Épistaxis",
    "nez qui saigne":                    "Épistaxis",
    "confusion mentale":                 "Confusion",
    "désorientation":                    "Confusion",
    "ne reconnaît plus":                 "Confusion",
    # ── SYNONYMES ENRICHIS (langage courant → terme médical) ──────────────
    "39 degrés"                                 : "Fièvre élevée",
    "40 degrés"                                 : "Fièvre élevée",
    "abattement"                                : "Fatigue",
    "abdomen distendu"                          : "Ballonnements",
    "abdomen douloureux"                        : "Douleurs abdominales",
    "absence d'urines"                          : "Anurie",
    "acné"                                      : "Acné",
    "adénopathie"                               : "Ganglions enflés",
    "affaibli"                                  : "Fatigue",
    "aigreurs"                                  : "Brûlures gastriques",
    "alopécie"                                  : "Chute de cheveux",
    "altération de la conscience"               : "Altération de la conscience",
    "amaigrissement"                            : "Perte de poids",
    "amaigrissement rapide"                     : "Perte de poids",
    "amnésie"                                   : "Perte de mémoire",
    "angine"                                    : "Douleurs thoraciques",
    "angoisse"                                  : "Anxiété",
    "anxiété"                                   : "Anxiété",
    "anémié"                                    : "Pâleur",
    "aphasie"                                   : "Troubles de la parole",
    "aphtes"                                    : "Ulcères buccaux",
    "apnée pendant le sommeil"                  : "Apnées du sommeil",
    "appétit excessif"                          : "Polyphagie",
    "arrêt de respirer pendant le sommeil"      : "Apnées du sommeil",
    "arthrite"                                  : "Arthrite",
    "articulations gonflées"                    : "Arthrite",
    "arythmie"                                  : "Pouls irrégulier",
    "asthénie"                                  : "Fatigue",
    "avaler est douloureux"                     : "Difficultés à avaler",
    "avoir de la fièvre"                        : "Fièvre",
    "ballonnements"                             : "Ballonnements",
    "barbouillé"                                : "Nausées",
    "battements forts"                          : "Palpitations",
    "beaucoup transpirer"                       : "Sudation excessive",
    "besoins urinaires fréquents"               : "Pollakiurie",
    "bilan perturbé"                            : "Bilan sanguin anormal",
    "bleus sans raison"                         : "Ecchymoses",
    "blocage en avalant"                        : "Dysphagie",
    "boire beaucoup"                            : "Polydipsie",
    "bouche douloureuse"                        : "Ulcères buccaux",
    "boule au cou"                              : "Ganglions enflés",
    "boule à la gorge"                          : "Goître",
    "bourdonnements"                            : "Acouphènes",
    "boutons de fièvre"                         : "Herpès labial",
    "boutons de jeunesse"                       : "Acné",
    "bpco"                                      : "Obstruction bronchique",
    "bronchite chronique"                       : "Obstruction bronchique",
    "bronchospasme"                             : "Sibilances",
    "bruit insupportable"                       : "Phonophobie",
    "brûlure en urinant"                        : "Brûlures mictionnelles",
    "bulles"                                    : "Bulles",
    "bégaiement soudain"                        : "Troubles de la parole",
    "cachexie"                                  : "Perte de poids",
    "calvitie"                                  : "Chute de cheveux",
    "cercles autour des lampes"                 : "Halos autour des lumières",
    "chair de poule"                            : "Frissons",
    "chaleur corporelle"                        : "Fièvre",
    "chaleur excessive"                         : "Intolérance à la chaleur",
    "chancre"                                   : "Chancre",
    "chaud"                                     : "Fièvre",
    "cheveux qui tombent"                       : "Chute de cheveux",
    "coeur au bord des lèvres"                  : "Nausées",
    "coeur irrégulier"                          : "Pouls irrégulier",
    "coeur qui bat vite"                        : "Palpitations",
    "coliques"                                  : "Douleurs abdominales",
    "coloration jaune"                          : "Jaunisse",
    "comportement bizarre"                      : "Comportement inapproprié",
    "condylomes"                                : "Condylomes",
    "confus"                                    : "Confusion",
    "conjonctivite"                             : "Yeux rouges",
    "conscience altérée"                        : "Altération de la conscience",
    "constipé"                                  : "Constipation",
    "convulsion"                                : "Convulsions",
    "corps chaud"                               : "Fièvre",
    "corps douloureux"                          : "Courbatures",
    "corps qui brûle"                           : "Fièvre",
    "corps raide au réveil"                     : "Raideur matinale",
    "cou gonflé"                                : "Goître",
    "cou raide"                                 : "Raideur de la nuque",
    "courbaturé"                                : "Courbatures",
    "crachats sanglants"                        : "Hémoptysie",
    "cracher du sang"                           : "Hémoptysie",
    "crampes"                                   : "Crampes musculaires",
    "crêtes de coq"                             : "Condylomes",
    "cystalgie"                                 : "Brûlures mictionnelles",
    "côte qui fait mal en respirant"            : "Douleur pleurale",
    "cœur qui s'emballe"                        : "Palpitations",
    "dermatose"                                 : "Éruption cutanée",
    "desquamation"                              : "Desquamation",
    "diabète"                                   : "Hyperglycémie",
    "diaphorèse"                                : "Sueurs nocturnes",
    "diarrhée"                                  : "Diarrhée",
    "difficile à réveiller"                     : "Altération de la conscience",
    "difficulté à avaler"                       : "Difficultés à avaler",
    "difficulté à déféquer"                     : "Constipation",
    "difficultés à dormir"                      : "Insomnie",
    "difficultés à se lever"                    : "Raideur matinale",
    "diurèse abondante"                         : "Polyurie",
    "dorsalgie"                                 : "Douleur dorsale",
    "douleur au niveau du sein"                 : "Mastalgie",
    "douleur crânienne"                         : "Maux de tête",
    "douleur dans le bras gauche"               : "Douleurs thoraciques",
    "douleur dans les genoux"                   : "Arthralgie",
    "douleur dans les joints"                   : "Arthralgie",
    "douleur dans les muscles"                  : "Douleurs musculaires",
    "douleur en respirant"                      : "Douleur pleurale",
    "douleur en urinant"                        : "Brûlures mictionnelles",
    "douleur flanc"                             : "Douleur lombaire",
    "douleur inter-scapulaire"                  : "Douleur dorsale",
    "douleur rénale"                            : "Douleur lombaire",
    "douleur thoracique"                        : "Douleurs thoraciques",
    "douleur à l'oeil"                          : "Douleur oculaire",
    "douleur à l'oreille"                       : "Douleur auriculaire",
    "douleur à la gorge"                        : "Mal de gorge",
    "douleur à la tête"                         : "Maux de tête",
    "douleurs dans tout le corps"               : "Douleurs musculaires",
    "douleurs diffuses"                         : "Courbatures",
    "draps mouillés"                            : "Sueurs nocturnes",
    "dysarthrie"                                : "Troubles de la parole",
    "dysphagie"                                 : "Dysphagie",
    "dysphonie"                                 : "Enrouement",
    "dysurie"                                   : "Brûlures mictionnelles",
    "dégoût pour la nourriture"                 : "Anorexie",
    "délire"                                    : "Comportement inapproprié",
    "démangeaisons"                             : "Prurit",
    "dépigmentation"                            : "Vitiligo",
    "déprime"                                   : "Dépression",
    "dépôt sous la peau"                        : "Tophi",
    "désorienté"                                : "Confusion",
    "déséquilibre"                              : "Vertiges",
    "ecchymoses"                                : "Ecchymoses",
    "emphysème"                                 : "Emphysème",
    "entendre des voix"                         : "Hallucinations",
    "envie fréquente d'uriner"                  : "Pollakiurie",
    "envie impérieuse d'uriner"                 : "Pollakiurie",
    "esprit embrouillé"                         : "Confusion",
    "faiblesse dans les bras"                   : "Faiblesse musculaire",
    "faiblesse dans les jambes"                 : "Faiblesse musculaire",
    "faim excessive"                            : "Polyphagie",
    "faim tout le temps"                        : "Polyphagie",
    "faire beaucoup de pipi"                    : "Polyurie",
    "feu sauvage"                               : "Herpès labial",
    "fibrillation"                              : "Pouls irrégulier",
    "fièvre forte"                              : "Fièvre élevée",
    "fièvre légère"                             : "Fièvre",
    "fièvre à 40"                               : "Fièvre élevée",
    "flatulences"                               : "Flatulences",
    "flou visuel"                               : "Vision floue",
    "foie gros"                                 : "Hépatomégalie",
    "foie grossi"                               : "Hépatomégalie",
    "frilosité"                                 : "Intolérance au froid",
    "froid dans le dos"                         : "Frissons",
    "fébrilité"                                 : "Fièvre",
    "ganglions au cou"                          : "Ganglions enflés",
    "ganglions au niveau des aisselles"         : "Ganglions enflés",
    "ganglions douloureux"                      : "Ganglions enflés",
    "ganglions inguinaux"                       : "Ganglions enflés",
    "ganglions partout"                         : "Adénopathie",
    "gaz"                                       : "Ballonnements",
    "glaires"                                   : "Crachats",
    "glycémie élevée"                           : "Hyperglycémie",
    "goitre"                                    : "Goître",
    "gonflement des articulations"              : "Arthrite",
    "gorge douloureuse"                         : "Mal de gorge",
    "gorge en feu"                              : "Mal de gorge",
    "gorge irritée"                             : "Mal de gorge",
    "gorge qui fait mal"                        : "Mal de gorge",
    "gorge qui gratte"                          : "Mal de gorge",
    "grattage"                                  : "Prurit",
    "grelotter"                                 : "Frissons",
    "gros orteil douloureux"                    : "Tophi",
    "gros orteil rouge et gonflé"               : "Tophi",
    "grosseur dans le cou"                      : "Adénopathie",
    "grosseurs sous les bras"                   : "Adénopathie",
    "grossissement du foie"                     : "Hépatomégalie",
    "haleine d'urine"                           : "Haleine urémique",
    "haleter"                                   : "Essoufflement",
    "halitose"                                  : "Haleine urémique",
    "hallucinations"                            : "Hallucinations",
    "halos autour des lumières"                 : "Halos autour des lumières",
    "herpès"                                    : "Éruption génitale",
    "hta"                                       : "Hypertension",
    "hypersudation"                             : "Sudation excessive",
    "hypertendu"                                : "Hypertension",
    "hyperthermie"                              : "Fièvre élevée",
    "hypotendu"                                 : "Hypotension",
    "hématomes spontanés"                       : "Ecchymoses",
    "hématurie"                                 : "Hématurie",
    "ictère"                                    : "Jaunisse",
    "idées noires"                              : "Dépression",
    "inquiétude excessive"                      : "Anxiété",
    "insomnie"                                  : "Insomnie",
    "instabilité"                               : "Vertiges",
    "intolérance au bruit"                      : "Phonophobie",
    "intolérance au froid"                      : "Intolérance au froid",
    "intolérance à la lumière"                  : "Photophobie",
    "joint chaud et gonflé"                     : "Arthrite",
    "larmoiement"                               : "Larmoiement",
    "lassitude"                                 : "Fatigue",
    "leucorrhée"                                : "Pertes vaginales anormales",
    "lipothymie"                                : "Syncope",
    "lombalgie"                                 : "Douleur lombaire",
    "lumière douloureuse"                       : "Photophobie",
    "lymphadénopathie"                          : "Ganglions enflés",
    "lésions cutanées"                          : "Éruption cutanée",
    "maigrir"                                   : "Perte de poids",
    "mal au coeur"                              : "Nausées",
    "mal aux articulations"                     : "Arthralgie",
    "mal aux oreilles"                          : "Douleur auriculaire",
    "mal aux reins"                             : "Douleur lombaire",
    "mal aux yeux"                              : "Douleur oculaire",
    "mal dans le dos"                           : "Douleur dorsale",
    "mal dans le dos en bas"                    : "Douleur lombaire",
    "mal en avalant"                            : "Difficultés à avaler",
    "mal partout"                               : "Douleurs musculaires",
    "mal voir de loin"                          : "Myopie",
    "mal voir de près"                          : "Hypermétropie",
    "mal à la gorge"                            : "Mal de gorge",
    "mal à la poitrine"                         : "Douleurs thoraciques",
    "mal à respirer"                            : "Essoufflement",
    "malaise"                                   : "Syncope",
    "manger beaucoup"                           : "Polyphagie",
    "manque d'énergie"                          : "Fatigue",
    "mictions abondantes"                       : "Polyurie",
    "moral bas"                                 : "Dépression",
    "morve"                                     : "Rhinorrhée",
    "mucus dans les poumons"                    : "Crachats",
    "muscles douloureux"                        : "Douleurs musculaires",
    "muscles qui font mal"                      : "Douleurs musculaires",
    "muscles qui lâchent"                       : "Faiblesse musculaire",
    "muscles qui s'affaiblissent"               : "Faiblesse musculaire",
    "myalgie"                                   : "Douleurs musculaires",
    "myalgies"                                  : "Douleurs musculaires",
    "mémoire qui baisse"                        : "Perte de mémoire",
    "méningisme"                                : "Raideur de la nuque",
    "ne dort pas"                               : "Insomnie",
    "ne fait plus pipi"                         : "Anurie",
    "ne mange plus"                             : "Anorexie",
    "ne parle plus bien"                        : "Troubles de la parole",
    "ne peut pas aller à la selle"              : "Constipation",
    "ne peut pas respirer"                      : "Essoufflement",
    "ne sait plus où il est"                    : "Confusion",
    "ne va pas à la selle"                      : "Constipation",
    "ne voit plus bien de loin"                 : "Myopie",
    "ne voit plus bien de près"                 : "Hypermétropie",
    "nervosité"                                 : "Anxiété",
    "nez bouché"                                : "Congestion nasale",
    "nez encombré"                              : "Congestion nasale",
    "nez qui coule"                             : "Rhinorrhée",
    "nuit mouillée"                             : "Sueurs nocturnes",
    "nuque raide"                               : "Raideur de la nuque",
    "obstruction nasale"                        : "Congestion nasale",
    "obésité"                                   : "Prise de poids",
    "odeur bizarre dans la bouche"              : "Haleine urémique",
    "odynophagie"                               : "Difficultés à avaler",
    "oedème"                                    : "Gonflement des chevilles",
    "oedème des membres inférieurs"             : "Gonflement des chevilles",
    "ongles cassants"                           : "Ongles dystrophiques",
    "ongles fragiles"                           : "Ongles dystrophiques",
    "ongles qui se cassent"                     : "Ongles dystrophiques",
    "oppression respiratoire"                   : "Essoufflement",
    "oppression thoracique"                     : "Douleurs thoraciques",
    "oreille bouchée"                           : "Acouphènes",
    "oreille qui fait mal"                      : "Douleur auriculaire",
    "otalgie"                                   : "Douleur auriculaire",
    "oubli"                                     : "Perte de mémoire",
    "palpitations"                              : "Palpitations",
    "paralysie partielle"                       : "Faiblesse musculaire",
    "parole difficile"                          : "Troubles de la parole",
    "parésie"                                   : "Faiblesse musculaire",
    "pas d'énergie"                             : "Fatigue",
    "pas faim"                                  : "Anorexie",
    "paupières gonflées"                        : "Paupières gonflées",
    "peau dépigmentée"                          : "Vitiligo",
    "peau grasse avec boutons"                  : "Acné",
    "peau pâle"                                 : "Pâleur",
    "peau qui rougit"                           : "Éruption cutanée",
    "peau sèche et froide"                      : "Peau sèche",
    "peau épaissie rouge"                       : "Plaques rouges squameuses",
    "pelure"                                    : "Desquamation",
    "perte d'appétit"                           : "Anorexie",
    "perte de cheveux"                          : "Chute de cheveux",
    "perte de poids"                            : "Perte de poids",
    "pertes anormales"                          : "Pertes vaginales anormales",
    "pertes du pénis"                           : "Écoulement urétral",
    "pertes vaginales"                          : "Pertes vaginales anormales",
    "petites taches rouges"                     : "Pétéchies",
    "petits points rouges"                      : "Pétéchies",
    "pipi marron"                               : "Urines foncées",
    "pipi mousseux"                             : "Urine mousseuse",
    "piquer en urinant"                         : "Brûlures mictionnelles",
    "plaie génitale"                            : "Ulcère génital",
    "plaie sur le sexe"                         : "Ulcère génital",
    "plaies buccales"                           : "Ulcères buccaux",
    "plaies dans la bouche"                     : "Ulcères buccaux",
    "plaies sur la langue"                      : "Ulcères buccaux",
    "plaques qui gonflent"                      : "Urticaire",
    "plaques urticariennes"                     : "Urticaire",
    "plus d'appétit"                            : "Anorexie",
    "plus d'urine"                              : "Anurie",
    "poids qui augmente"                        : "Prise de poids",
    "point de côté"                             : "Douleur pleurale",
    "poitrine qui fait mal"                     : "Douleurs thoraciques",
    "polyarthralgie"                            : "Arthralgie",
    "poumons abîmés"                            : "Emphysème",
    "prendre du poids"                          : "Prise de poids",
    "pression artérielle basse"                 : "Hypotension",
    "pression artérielle haute"                 : "Hypertension",
    "pression dans la poitrine"                 : "Douleurs thoraciques",
    "prise de sang anormale"                    : "Bilan sanguin anormal",
    "protéinurie"                               : "Urine mousseuse",
    "prurit"                                    : "Prurit",
    "psoriasis"                                 : "Plaques rouges squameuses",
    "purpura"                                   : "Purpura",
    "pus du pénis"                              : "Écoulement urétral",
    "pyrosis"                                   : "Brûlures gastriques",
    "raideur au réveil"                         : "Raideur matinale",
    "raideur du cou"                            : "Raideur de la nuque",
    "raideur le matin"                          : "Raideur matinale",
    "rash"                                      : "Éruption cutanée",
    "rate gonflée"                              : "Splénomégalie",
    "rate grosse"                               : "Splénomégalie",
    "refus de manger"                           : "Anorexie",
    "respiration sifflante"                     : "Sibilances",
    "rhinite"                                   : "Rhinorrhée",
    "rhumatisme"                                : "Arthralgie",
    "rhume"                                     : "Congestion nasale",
    "rigidité cervicale"                        : "Raideur de la nuque",
    "ronflements"                               : "Ronflements",
    "ronfler"                                   : "Ronflements",
    "rougeurs"                                  : "Éruption cutanée",
    "régurgitation"                             : "Vomissements",
    "s'essouffle vite"                          : "Essoufflement",
    "s'est évanoui"                             : "Syncope",
    "saignement excessif"                       : "Saignements prolongés",
    "saignement nasal"                          : "Épistaxis",
    "saignement qui ne s'arrête pas"            : "Saignements prolongés",
    "sang dans les crachats"                    : "Hémoptysie",
    "sans énergie"                              : "Fatigue",
    "se fait des bleus facilement"              : "Ecchymoses",
    "se sent faible"                            : "Fatigue",
    "sein douloureux"                           : "Mastalgie",
    "seins sensibles"                           : "Mastalgie",
    "seizure"                                   : "Convulsions",
    "selles dures"                              : "Constipation",
    "selles fréquentes"                         : "Diarrhée",
    "selles molles"                             : "Diarrhée",
    "semi-coma"                                 : "Altération de la conscience",
    "sensation de nausée"                       : "Nausées",
    "sensation de tourner"                      : "Vertiges",
    "sensible au bruit"                         : "Phonophobie",
    "sensible à la lumière"                     : "Photophobie",
    "sifflement dans les oreilles"              : "Acouphènes",
    "sifflement respiratoire"                   : "Sibilances",
    "soif excessive"                            : "Polydipsie",
    "soif inextinguible"                        : "Polydipsie",
    "sommeil agité"                             : "Apnées du sommeil",
    "somnolent"                                 : "Altération de la conscience",
    "spasmes"                                   : "Convulsions",
    "squames"                                   : "Desquamation",
    "stomatite"                                 : "Ulcères buccaux",
    "stress"                                    : "Anxiété",
    "subfébrile"                                : "Fièvre",
    "sucre dans le sang"                        : "Hyperglycémie",
    "sucrerie dans le sang"                     : "Hyperglycémie",
    "sueurs"                                    : "Sueurs nocturnes",
    "sueurs la nuit"                            : "Sueurs nocturnes",
    "suppression urinaire"                      : "Anurie",
    "taches violettes"                          : "Purpura",
    "tachycardie"                               : "Palpitations",
    "température"                               : "Fièvre",
    "tension basse"                             : "Hypotension",
    "thyroïde gonflée"                          : "Goître",
    "tinnitus"                                  : "Acouphènes",
    "toujours chaud"                            : "Intolérance à la chaleur",
    "toujours froid"                            : "Intolérance au froid",
    "tournis"                                   : "Vertiges",
    "tousser"                                   : "Toux",
    "toux"                                      : "Toux",
    "toux avec crachats"                        : "Toux grasse",
    "toux sans crachat"                         : "Toux sèche",
    "toux sèche"                                : "Toux sèche",
    "tranchées"                                 : "Douleurs abdominales",
    "transit accéléré"                          : "Diarrhée",
    "transpiration excessive"                   : "Sudation excessive",
    "transpirer la nuit"                        : "Sueurs nocturnes",
    "tremblement au repos"                      : "Tremblements",
    "tremblement des mains"                     : "Tremblements",
    "tremblement involontaire"                  : "Convulsions",
    "trembler"                                  : "Tremblements",
    "trembler de froid"                         : "Frissons",
    "tristesse"                                 : "Dépression",
    "troubles de la coagulation"                : "Saignements prolongés",
    "troubles de la mémoire"                    : "Perte de mémoire",
    "troubles du sommeil"                       : "Insomnie",
    "très fatigué"                              : "Fatigue",
    "très forte fièvre"                         : "Fièvre élevée",
    "très soif"                                 : "Polydipsie",
    "tête lourde"                               : "Maux de tête",
    "tête qui fait mal"                         : "Maux de tête",
    "ulcération génitale"                       : "Ulcère génital",
    "ulcérations buccales"                      : "Ulcères buccaux",
    "uriner beaucoup"                           : "Polyurie",
    "uriner fait mal"                           : "Brûlures mictionnelles",
    "urines couleur thé"                        : "Urines foncées",
    "urines foncées"                            : "Urines foncées",
    "urines fréquentes"                         : "Pollakiurie",
    "urines marrons"                            : "Urines foncées",
    "urines mousseuses"                         : "Urine mousseuse",
    "urines sanglantes"                         : "Hématurie",
    "urticaire"                                 : "Urticaire",
    "ventre qui dérange"                        : "Diarrhée",
    "verrues"                                   : "Verrues",
    "vision trouble"                            : "Vision floue",
    "voix cassée"                               : "Enrouement",
    "voix qui change"                           : "Enrouement",
    "voix rauque"                               : "Enrouement",
    "voix éraillée"                             : "Enrouement",
    "vomi"                                      : "Vomissements",
    "végétations"                               : "Condylomes",
    "vésicules"                                 : "Vésicules",
    "vésicules génitales"                       : "Éruption génitale",
    "vésicules sur les lèvres"                  : "Herpès labial",
    "wheezing"                                  : "Sibilances",
    "yeux douloureux"                           : "Douleur oculaire",
    "yeux gonflés"                              : "Paupières gonflées",
    "yeux injectés"                             : "Yeux rouges",
    "yeux irrités"                              : "Yeux rouges",
    "yeux larmoyants"                           : "Larmoiement",
    "yeux qui brouillent"                       : "Vision floue",
    "yeux sensibles à la lumière"               : "Photophobie",
    "ça gratte"                                 : "Prurit",
    "écailles sur la peau"                      : "Plaques rouges squameuses",
    "écoulement nasal"                          : "Rhinorrhée",
    "écoulement urétral"                        : "Écoulement urétral",
    "écoulement vaginal"                        : "Pertes vaginales anormales",
    "émèse"                                     : "Vomissements",
    "épuisé"                                    : "Fatigue",
    "éruption"                                  : "Éruption cutanée",
    "éruption autour des parties"               : "Éruption génitale",
    "étau dans la poitrine"                     : "Douleurs thoraciques",
    "étourdissement"                            : "Vertiges",
    "œdème des paupières"                       : "Paupières gonflées",
    # ── SYNONYMES COMPLETS — 444 symptômes couverts ─────────────────────────
    "37.5 degrés"                                   : "Fièvre légère",
    "abdomen en planche"                            : "Douleur abdominale sévère",
    "absence"                                       : "Absence",
    "acide urique élevé"                            : "Hyperuricémie",
    "acouphènes"                                    : "Bourdonnements",
    "acromégalie des extrémités"                    : "Agrandissement des mains/pieds",
    "acuité visuelle réduite"                       : "Vision floue à toutes distances",
    "addiction au sel"                              : "Sel craving",
    "agitation"                                     : "Agitation",
    "agité"                                         : "Agitation",
    "agueusie"                                      : "Perte de goût",
    "albumine basse"                                : "Albuminémie basse",
    "albumine dans les urines"                      : "Protéinurie",
    "alternance constipation diarrhée"              : "Alternance diarrhée-constipation",
    "amygdales gonflées"                            : "Amygdalite",
    "amyotrophie"                                   : "Atrophie musculaire",
    "anesthésie partielle"                          : "Perte de sensibilité",
    "angine de poitrine sévère"                     : "Douleur thoracique sévère",
    "angioedème"                                    : "Angioedème",
    "angle costo-vertébral sensible"                : "Douleur costovertébrale",
    "anneau blanc dans l'oeil"                      : "Arc cornéen",
    "anosmie"                                       : "Perte d'odorat",
    "anxiety"                                       : "Anxiété",
    "anémie"                                        : "Anémie",
    "aphonie"                                       : "Perte de voix",
    "apnée du sommeil"                              : "Pauses respiratoires nocturnes",
    "arc cornéen"                                   : "Arc cornéen",
    "arrêt de respiration pendant sommeil"          : "Pauses respiratoires nocturnes",
    "arthralgie périphérique"                       : "Arthralgie périphérique",
    "articulation douloureuse"                      : "Douleur articulaire",
    "articulation gonflée de sang"                  : "Hémarthrose",
    "articulations sensibles"                       : "Sensibilité articulaire",
    "aréflexie"                                     : "Réflexes abolis",
    "ascite"                                        : "Ascite",
    "asthme sifflant"                               : "Wheezing",
    "asthénopie"                                    : "Fatigue oculaire",
    "ataxie"                                        : "Difficultés à marcher",
    "ataxie vestibulaire"                           : "Trouble de l'équilibre",
    "atrophie musculaire"                           : "Atrophie musculaire",
    "attaque cérébrale passagère"                   : "AVC transitoire",
    "atteinte cérébrale"                            : "Encéphalopathie",
    "atteinte du système nerveux"                   : "Complications neurologiques",
    "atteinte rénale du lupus"                      : "Néphrite lupique",
    "aura"                                          : "Aura",
    "automatismes"                                  : "Mouvements automatiques",
    "avaler est difficile"                          : "Difficultés à avaler",
    "avc transitoire"                               : "AVC transitoire",
    "avoir mal"                                     : "Douleur",
    "avoir soif"                                    : "Soif",
    "baisse d'acuité visuelle"                      : "Perte de vision",
    "baisse progressive de la vue"                  : "Perte de vision progressive",
    "barrel chest"                                  : "Barrel chest",
    "beaucoup de sueur"                             : "Transpiration excessive",
    "besoin de sel"                                 : "Sel craving",
    "besoin de tenir le livre loin"                 : "Nécessité d'éloigner la lecture",
    "blessure langue pendant crise"                 : "Morsure de langue",
    "bleu autour des lèvres"                        : "Cyanose",
    "bleus spontanés"                               : "Bleus faciles",
    "blocage gorge ou intestin"                     : "Sensation de blocage",
    "blépharospasme"                                : "Blépharospasme",
    "boiter"                                        : "Claudication",
    "boitera"                                       : "Difficultés à marcher",
    "bosse dans le dos"                             : "Bosse de bison",
    "bosse de bison"                                : "Bosse de bison",
    "bosse sur la peau"                             : "Excroissance cutanée",
    "bouche de travers"                             : "Paralysie faciale",
    "bouche desséchée le matin"                     : "Bouche sèche au réveil",
    "bouche qui sent mauvais"                       : "Haleine désagréable",
    "bouche sèche"                                  : "Sécheresse buccale",
    "bouche sèche au lever"                         : "Bouche sèche au réveil",
    "bouche sèche et soif intense"                  : "Déshydratation",
    "bouffissure du visage"                         : "Gonflement facial",
    "bouffées de chaleur"                           : "Chaleur",
    "boules sous la peau"                           : "Kystes",
    "bourdonnements dans les oreilles"              : "Bourdonnements",
    "boutons avec liquide"                          : "Éruption vésiculaire",
    "boutons groupés"                               : "Lésions groupées",
    "boutons sur les articulations des doigts"      : "Papules de Gottron",
    "boutons sur les pieds et mains"                : "Éruption palmoplantaire",
    "boutons épars"                                 : "Lésions dispersées",
    "bradycardie"                                   : "Bradycardie",
    "bradycardie relative"                          : "Bradycardie relative",
    "bradykinésie"                                  : "Lenteur de mouvement",
    "bradypsychie"                                  : "Ralentissement intellectuel",
    "bras douloureux"                               : "Douleur au bras/épaule",
    "bras et jambes faibles"                        : "Faiblesse des membres",
    "brouillard mental"                             : "Difficultés de concentration",
    "brouillard visuel léger"                       : "Vision floue légère",
    "bruit cardiaque anormal"                       : "Frottement péricardique",
    "bruit dans les oreilles"                       : "Bourdonnements",
    "bruit en inspirant"                            : "Stridor inspiratoire",
    "brûlure au creux du ventre"                    : "Brûlures épigastriques",
    "brûlure au soleil facile"                      : "Photosensibilité",
    "brûlure derrière le sternum"                   : "Sensation de brûlure rétrosternale",
    "brûlure interne"                               : "Sensation de brûlure",
    "brûlure électrique"                            : "Douleur neuropathique",
    "brûlures cutanées"                             : "Brûlures cutanées",
    "brûlures génitales"                            : "Brûlures génitales",
    "brûlures remontantes"                          : "Régurgitation acide",
    "brûlures urinaires"                            : "Brûlures urinaires",
    "brûlures épigastriques"                        : "Brûlures épigastriques",
    "cage thoracique élargie"                       : "Barrel chest",
    "caillot de sang"                               : "Thrombose",
    "calcinose"                                     : "Calcinose",
    "calculs biliaires"                             : "Lithiase biliaire",
    "calculs rénaux associés"                       : "Lithiase rénale associée",
    "candidose"                                     : "Candidose buccale",
    "caries"                                        : "Caries dentaires",
    "cercle blanc autour de l'iris"                 : "Arc cornéen",
    "cercles autour des lumières"                   : "Halos colorés",
    "cerveau qui fonctionne mal"                    : "Encéphalopathie",
    "cervicalgie"                                   : "Douleur au cou",
    "cervicite"                                     : "Cervicite",
    "chaleur"                                       : "Chaleur",
    "champ visuel réduit"                           : "Perte de vision périphérique",
    "champ visuel rétréci"                          : "Vision tunnel",
    "champignons dans la bouche"                    : "Candidose buccale",
    "chassie"                                       : "Yeux collants",
    "cheveux blancs localisés"                      : "Poliose",
    "cheveux cassants"                              : "Cheveux cassants",
    "cheveux fragiles"                              : "Cheveux cassants",
    "cheveux qui se cassent"                        : "Cheveux cassants",
    "cheveux secs"                                  : "Cheveux cassants",
    "choc"                                          : "Choc",
    "choc septique"                                 : "Choc septique",
    "cholestérol et triglycérides élevés"           : "Hyperlipidémie",
    "chute"                                         : "Chute",
    "chute des cheveux"                             : "Alopécie",
    "chutes par manque d'équilibre"                 : "Trouble de l'équilibre",
    "chutes répétées"                               : "Chute",
    "cicatrices"                                    : "Cicatrices",
    "cicatrisation difficile"                       : "Cicatrices",
    "cicatrisation lente"                           : "Plaies lentes à cicatriser",
    "cicatrisation pulmonaire"                      : "Fibrose pulmonaire",
    "claudication"                                  : "Claudication",
    "clignements involontaires"                     : "Blépharospasme",
    "coagulation anormale"                          : "Thrombose",
    "coeur qui s'accélère"                          : "Sensation d'accélération",
    "col de l'utérus infecté"                       : "Cervicite",
    "colique"                                       : "Douleur colique intense",
    "colique biliaire"                              : "Lithiase biliaire",
    "collapsus"                                     : "Choc",
    "colon irritable"                               : "Syndrome côlon irritable",
    "coloration mauve des paupières"                : "Héliotrope éruption",
    "communication anormale"                        : "Fistules",
    "complications neurologiques"                   : "Complications neurologiques",
    "comédons"                                      : "Points noirs",
    "conduite nocturne impossible"                  : "Difficultés à conduire la nuit",
    "condylome"                                     : "Verrue génitale",
    "condylomes acuminés"                           : "Verrues génitales",
    "confusion après crise"                         : "Confusion post-critique",
    "confusion mentale sévère"                      : "Encéphalopathie",
    "constipation avec selles dures"                : "Selles dures",
    "corps raide"                                   : "Rigidité",
    "corps étranger dans l'oeil"                    : "Sensation de corps étranger",
    "cou de taureau"                                : "Bosse de bison",
    "cou douloureux"                                : "Douleur au cou",
    "cou qui grossit"                               : "Gonflement thyroïde",
    "coup de pompe"                                 : "Fatigue soudaine",
    "crachats épais"                                : "Expectoration",
    "craquement mâchoire"                           : "Douleur à la mâchoire",
    "crevasses"                                     : "Crevasses",
    "crise articulaire soudaine"                    : "Douleur articulaire soudaine",
    "crise d'absence"                               : "Absence",
    "crise de vertiges"                             : "Vertige soudain",
    "crise hypoglycémique"                          : "Hypoglycémie",
    "croup"                                         : "Stridor inspiratoire",
    "croûtes"                                       : "Croûtes",
    "croûtes sur la peau"                           : "Croûtes",
    "cyanose"                                       : "Cyanose",
    "cyanose distale"                               : "Cyanose distale",
    "cyanose légère"                                : "Cyanose légère",
    "cystites à répétition"                         : "Infections urinaires",
    "cécité nocturne"                               : "Perte de vision nocturne",
    "céphalée en coup de tonnerre"                  : "Céphalées sévères",
    "céphalée intense"                              : "Céphalées sévères",
    "céphalée pulsatile"                            : "Pulsation céphalique",
    "céphalées diffuses"                            : "Maux de tête",
    "céphalées matinales"                           : "Maux de tête matinaux",
    "céphalées sévères"                             : "Céphalées sévères",
    "côlon pas vide"                                : "Sensation vidange incomplète",
    "cœur qui bat lentement"                        : "Bradycardie",
    "cœur rapide"                                   : "Tachycardie",
    "dent douloureuse"                              : "Douleur dentaire",
    "dents cariées"                                 : "Caries dentaires",
    "dents espacées"                                : "Espacement des dents",
    "dents qui s'écartent"                          : "Espacement des dents",
    "dents qui se gâtent"                           : "Caries dentaires",
    "depression"                                    : "Dépression",
    "diabète mal contrôlé"                          : "Déséquilibre glycémique",
    "diastème qui s'élargit"                        : "Espacement des dents",
    "difficultes a avaler"                          : "Difficultés à avaler",
    "difficulté d'écoulement urinaire"              : "Flux faible",
    "difficulté de lecture"                         : "Difficulté à lire",
    "difficulté à articuler"                        : "Dysarthrie",
    "difficulté à faire pipi"                       : "Difficulté à uriner",
    "difficulté à parler"                           : "Difficultés de langage",
    "difficulté à respirer brutale"                 : "Essoufflement soudain",
    "difficultés de concentration"                  : "Difficultés de concentration",
    "difficultés à conduire de nuit"                : "Difficultés à conduire la nuit",
    "difficultés à lire"                            : "Difficulté à lire",
    "difficultés à parler"                          : "Difficultés à parler",
    "difficultés à uriner"                          : "Difficulté à uriner",
    "digestion difficile"                           : "Indigestion",
    "diplopie"                                      : "Diplopie",
    "diplopie légère"                               : "Diplopie légère",
    "distorsion des lignes"                         : "Lignes ondulées",
    "diurèse diminuée"                              : "Oligurie",
    "doigts blancs puis bleus au froid"             : "Raynaud",
    "doigts bleus"                                  : "Cyanose distale",
    "doigts nécrosés"                               : "Gangrène distale",
    "doigts qui blanchissent"                       : "Raynaud",
    "dormir assis"                                  : "Orthopnée",
    "dormir mal"                                    : "Troubles du sommeil",
    "douleur"                                       : "Douleur",
    "douleur abdominale"                            : "Douleurs abdominales",
    "douleur abdominale droite"                     : "Douleur abdominale droite",
    "douleur améliorée par l'exercice"              : "Douleur améliorée par l'exercice",
    "douleur après fritures"                        : "Douleur après repas gras",
    "douleur après les graisses"                    : "Douleur après repas gras",
    "douleur articulaire"                           : "Douleur articulaire",
    "douleur articulaire brutale"                   : "Douleur articulaire soudaine",
    "douleur au bras"                               : "Douleur au bras/épaule",
    "douleur au cou"                                : "Douleur au cou",
    "douleur au milieu de la poitrine"              : "Douleur rétrosternale",
    "douleur au passage de l'urine"                 : "Dysurie",
    "douleur au périnée"                            : "Douleur périnéale",
    "douleur au testicule"                          : "Douleur testiculaire",
    "douleur aux bras et jambes"                    : "Douleur aux extrémités",
    "douleur aux jambes"                            : "Douleur aux extrémités",
    "douleur aux petites articulations"             : "Arthralgie périphérique",
    "douleur basse-ventre"                          : "Douleur pelvienne",
    "douleur brûlante estomac"                      : "Brûlures épigastriques",
    "douleur brûlante génitale"                     : "Brûlures génitales",
    "douleur cervicale postérieure"                 : "Douleur à la nuque",
    "douleur côté droit"                            : "Douleur abdominale droite",
    "douleur d'un côté seulement"                   : "Douleur unilatérale",
    "douleur dans la jambe"                         : "Douleur membre inférieur",
    "douleur dans le bassin"                        : "Douleur pelvienne",
    "douleur dans le dos en bas"                    : "Douleur costovertébrale",
    "douleur derrière le sternum"                   : "Douleur rétrosternale",
    "douleur des deux côtés"                        : "Douleur bilatérale",
    "douleur des doigts et orteils"                 : "Arthralgie périphérique",
    "douleur du ventre"                             : "Douleurs abdominales",
    "douleur en avalant"                            : "Douleur à la déglutition",
    "douleur en coup d'aiguille"                    : "Douleur neuropathique",
    "douleur en coup de couteau"                    : "Douleur colique intense",
    "douleur en marchant"                           : "Claudication",
    "douleur en montant les escaliers"              : "Douleur à l'effort",
    "douleur entre jambes"                          : "Douleur pelvipérinéale",
    "douleur estomac en haut"                       : "Douleur abdominale supérieure",
    "douleur et flou visuel"                        : "Névrite optique",
    "douleur flanc droit"                           : "Douleur abdominale droite",
    "douleur générale"                              : "Douleur",
    "douleur irradiante"                            : "Douleur irradiante",
    "douleur la nuit"                               : "Douleur nocturne",
    "douleur latérale"                              : "Douleur unilatérale",
    "douleur lombaire avec irradiation"             : "Douleur irradiant vers aine",
    "douleur musculaire"                            : "Douleur musculaire",
    "douleur nocturne"                              : "Douleur nocturne",
    "douleur par vagues"                            : "Douleur colique intense",
    "douleur pelvienne"                             : "Douleur pelvienne",
    "douleur pendant l'exercice"                    : "Douleur à l'effort",
    "douleur pendant le sexe"                       : "Dyspareunie",
    "douleur pendant les rapports"                  : "Douleur lors des rapports",
    "douleur pleurale"                              : "Pleurite",
    "douleur poitrine très forte"                   : "Douleur thoracique sévère",
    "douleur périnée"                               : "Douleur pelvipérinéale",
    "douleur qui augmente en respirant"             : "Douleur thoracique pleurétique",
    "douleur qui descend dans l'aine"               : "Douleur irradiant vers aine",
    "douleur qui monte dans le dos"                 : "Douleur irradiant dans le dos",
    "douleur qui part à jeun"                       : "Douleur à jeun",
    "douleur qui passe après défécation"            : "Douleur soulagée par défécation",
    "douleur qui passe en bougeant"                 : "Douleur améliorée par l'exercice",
    "douleur qui s'améliore penché en avant"        : "Douleur calmée penché en avant",
    "douleur qui se propage"                        : "Douleur irradiante",
    "douleur rayonnante"                            : "Douleur irradiante",
    "douleur rétrosternale"                         : "Douleur rétrosternale",
    "douleur soulagée par les selles"               : "Douleur soulagée par défécation",
    "douleur sous l'épaule droite"                  : "Douleur irradiant épaule droite",
    "douleur sous le sternum"                       : "Douleur abdominale supérieure",
    "douleur symétrique"                            : "Douleur bilatérale",
    "douleur thoracique intense"                    : "Douleur thoracique sévère",
    "douleur ventre très forte"                     : "Douleur abdominale sévère",
    "douleur à l'effort physique"                   : "Douleur à l'effort",
    "douleur à l'estomac à jeun"                    : "Douleur à jeun",
    "douleur à l'insertion du tendon"               : "Enthésite",
    "douleur à l'orgasme"                           : "Éjaculation douloureuse",
    "douleur à l'épaule"                            : "Douleur au bras/épaule",
    "douleur à la face"                             : "Douleur faciale",
    "douleur à la fosse iliaque droite"             : "Douleur abdominale droite",
    "douleur à la mâchoire"                         : "Douleur à la mâchoire",
    "douleur à la nuque"                            : "Douleur à la nuque",
    "douleur à la palpation"                        : "Sensibilité à la palpation",
    "douleur à la pression"                         : "Sensibilité articulaire",
    "douleur à la thyroïde"                         : "Douleur thyroïdienne",
    "douleur électrique"                            : "Douleur neuropathique",
    "douleur épigastrique"                          : "Douleur abdominale supérieure",
    "douleurs dans tous les muscles"                : "Douleurs musculaires diffuses",
    "douleurs la nuit"                              : "Douleurs nocturnes",
    "douleurs musculaires diffuses"                 : "Douleurs musculaires diffuses",
    "douleurs nocturnes"                            : "Douleurs nocturnes",
    "durillon douloureux"                           : "Verrue plantaire douloureuse",
    "dyspareunie"                                   : "Douleur lors des rapports",
    "dyspepsie"                                     : "Indigestion",
    "dysphagie de blocage"                          : "Sensation de blocage",
    "dyspnee"                                       : "Dyspnée",
    "dyspnée aiguë"                                 : "Essoufflement soudain",
    "décharge"                                      : "Écoulement",
    "déclin cognitif"                               : "Troubles cognitifs",
    "dédoublement de la vision"                     : "Diplopie",
    "défenses immunitaires basses"                  : "Infections fréquentes",
    "déformation qui empire"                        : "Déformation progressive",
    "déformation qui s'aggrave"                     : "Déformation progressive",
    "défécation difficile"                          : "Efforts pour défécation",
    "démangeaisons génitales"                       : "Démangeaisons génitales",
    "démangeaisons locales"                         : "Démangeaisons locales",
    "démangeaisons légères"                         : "Démangeaisons légères",
    "démangeaisons oculaires"                       : "Prurit oculaire",
    "démangeaisons urètre"                          : "Prurit urétral",
    "démarche instable"                             : "Trouble de la marche",
    "démence"                                       : "Démence",
    "dépendance"                                    : "Perte d'autonomie",
    "dépôts aux paupières"                          : "Dépôts lipidiques aux paupières",
    "dépôts calcaires sous la peau"                 : "Calcinose",
    "dépôts de graisses sous la peau"               : "Xanthomes",
    "dépôts graisseux sur les tendons"              : "Xanthomes tendineux",
    "déshydratation"                                : "Déshydratation",
    "désorientation après convulsion"               : "Confusion post-critique",
    "détérioration cognitive"                       : "Démence",
    "développement mammaire chez homme"             : "Gynécomastie",
    "eau dans le ventre"                            : "Ascite",
    "ecchymoses faciles"                            : "Ecchymoses faciles",
    "ecchymoses sans raison"                        : "Bleus faciles",
    "effort à la selle"                             : "Efforts pour défécation",
    "encore envie d'aller aux selles"               : "Sensation d'évacuation incomplète",
    "encéphalopathie"                               : "Encéphalopathie",
    "endormissement dans la journée"                : "Somnolence diurne",
    "enflure"                                       : "Gonflement",
    "engourdi"                                      : "Perte de sensibilité",
    "engourdissement du visage"                     : "Engourdissement facial",
    "enrouement"                                    : "Voix rauque",
    "enthésite"                                     : "Enthésite",
    "envie d'uriner souvent"                        : "Besoin fréquent d'uriner",
    "envie de dormir le jour"                       : "Somnolence diurne",
    "envie de sel"                                  : "Sel craving",
    "envie impérieuse de selles"                    : "Besoin impérieux de déféquer",
    "envie urgente d'uriner"                        : "Urgence urinaire",
    "essoufflement activité physique"               : "Essoufflement d'effort",
    "essoufflement après repas"                     : "Essoufflement postprandial",
    "essoufflement brutal"                          : "Essoufflement soudain",
    "essoufflement couché"                          : "Dyspnée de décubitus",
    "essoufflement la nuit"                         : "Dyspnée nocturne",
    "essoufflement progressif"                      : "Dyspnée progressive",
    "essoufflement à l'effort"                      : "Dyspnée d'effort",
    "estomac plein vite"                            : "Sensation de satiété rapide",
    "estomac qui pèse"                              : "Indigestion",
    "excroissance cutanée"                          : "Excroissance cutanée",
    "exophtalmie"                                   : "Yeux saillants",
    "exsudat pharyngé"                              : "Taches blanches pharyngées",
    "extrémités bleues"                             : "Cyanose distale",
    "extrémités douloureuses"                       : "Douleur aux extrémités",
    "extrémités rouges et douloureuses"             : "Érythromélalgie",
    "face bouffie"                                  : "Oedème facial",
    "face gonflée"                                  : "Gonflement facial",
    "faciès acromégalique"                          : "Grossissement du visage",
    "faiblesse ascendante"                          : "Faiblesse ascendante",
    "faiblesse brutale"                             : "Faiblesse soudaine",
    "faiblesse des membres"                         : "Faiblesse des membres",
    "faiblesse des pieds vers le haut"              : "Faiblesse ascendante",
    "faiblesse soudaine"                            : "Faiblesse soudaine",
    "faim douloureuse"                              : "Douleur à jeun",
    "fasciculations"                                : "Fasciculations",
    "fatigue après crise"                           : "Fatigue post-critique",
    "fatigue au réveil"                             : "Fatigue au réveil",
    "fatigue brutale"                               : "Fatigue soudaine",
    "fatigue chronique"                             : "Fatigue chronique",
    "fatigue oculaire"                              : "Fatigue oculaire",
    "fatigue persistante"                           : "Fatigue chronique",
    "fatigue soudaine"                              : "Fatigue soudaine",
    "fatigué dès le matin"                          : "Fatigue au réveil",
    "faux besoins"                                  : "Sensation d'évacuation incomplète",
    "faux croup"                                    : "Toux aboyante",
    "fermer les yeux partiellement"                 : "Yeux plissés",
    "fibromyalgie douleurs"                         : "Douleurs musculaires diffuses",
    "fibrose pulmonaire"                            : "Fibrose pulmonaire",
    "fissures aux mains"                            : "Crevasses",
    "fissures cutanées"                             : "Fissures cutanées",
    "fistules"                                      : "Fistules",
    "fièvre cyclique"                               : "Fièvre intermittente",
    "fièvre infectieuse"                            : "Infection",
    "fièvre par crises"                             : "Fièvre intermittente",
    "fièvre qui va et vient"                        : "Fièvre intermittente",
    "flanc costovertébral douloureux"               : "Douleur costovertébrale",
    "flou de loin"                                  : "Vision floue de loin",
    "flou de près"                                  : "Vision floue de près",
    "flou partout"                                  : "Vision floue à toutes distances",
    "flou vision proche"                            : "Flou proche",
    "floue au centre"                               : "Vision centrale floue",
    "flush"                                         : "Rougeur du visage",
    "flush facial"                                  : "Visage rouge",
    "fonte musculaire"                              : "Atrophie musculaire",
    "force d'urination réduite"                     : "Jet urinaire faible",
    "fourmis dans les jambes"                       : "Fourmillements",
    "fourmis dans les membres"                      : "Engourdissement",
    "fractures faciles"                             : "Fragilité osseuse",
    "frissons forts"                                : "Frissons intenses",
    "frissons violents"                             : "Frissons intenses",
    "frottement cardiaque"                          : "Frottement péricardique",
    "fréquence urinaire"                            : "Fréquence urinaire",
    "fuites urinaires"                              : "Incontinence",
    "ganglions dans plusieurs zones"                : "Lymphadénopathie",
    "ganglions généralisés"                         : "Lymphadénopathie",
    "gangrène"                                      : "Gangrène distale",
    "gencives fragiles"                             : "Saignement des gencives",
    "gencives qui saignent"                         : "Saignement des gencives",
    "germes dans les urines"                        : "Bactériurie",
    "gestes inconscients"                           : "Mouvements automatiques",
    "glaires rectales"                              : "Mucus dans les selles",
    "globe vésical"                                 : "Rétention urinaire",
    "glycémie basse"                                : "Hypoglycémie",
    "glycémie fluctuante"                           : "Déséquilibre glycémique",
    "gonflement"                                    : "Gonflement",
    "gonflement allergique"                         : "Angioedème",
    "gonflement du visage"                          : "Angioedème",
    "gonflement labial"                             : "Gonflement des lèvres",
    "gonflement lèvres yeux"                        : "Angioedème",
    "gorge avec plaques blanches"                   : "Amygdalite",
    "gorge douloureuse à la déglutition"            : "Douleur à la déglutition",
    "gorge rouge"                                   : "Rougeur pharyngée",
    "goutte dans le sang"                           : "Hyperuricémie",
    "goût diminué"                                  : "Perte de goût",
    "graisse dans le dos"                           : "Bosse de bison",
    "graisses élevées dans le sang"                 : "Hyperlipidémie",
    "granulome"                                     : "Nodules",
    "grossir rapidement"                            : "Prise de poids rapide",
    "grossissement des extrémités"                  : "Agrandissement des mains/pieds",
    "gynécomastie"                                  : "Gynécomastie",
    "gêne"                                          : "Inconfort",
    "halos colorés"                                 : "Halos colorés",
    "handicap fonctionnel"                          : "Limitation de l'activité",
    "hirsutisme"                                    : "Pilosité excessive",
    "hoarseness"                                    : "Voix rauque",
    "humeur changeante"                             : "Irritabilité",
    "hyperactivité"                                 : "Agitation",
    "hyperhidrose"                                  : "Transpiration excessive",
    "hyperkératose"                                 : "Peau épaissie",
    "hyperlipidémie"                                : "Hyperlipidémie",
    "hypermétropie"                                 : "Vision floue de près",
    "hypersensibilité"                              : "Irritabilité",
    "hypersomnie"                                   : "Somnolence diurne",
    "hypertension portale"                          : "Hypertension portale",
    "hyperthyroïdie transitoire"                    : "Hyperthyroïdie transitoire",
    "hypertonie"                                    : "Rigidité",
    "hypoacousie"                                   : "Perte d'audition",
    "hypoalbuminémie"                               : "Albuminémie basse",
    "hypoesthésie"                                  : "Engourdissement",
    "hypomimie"                                     : "Visage inexpressif",
    "hypérémie conjonctivale"                       : "Injection conjonctivale",
    "hémiface insensible"                           : "Engourdissement facial",
    "hémorragie"                                    : "Saignement",
    "hémorragie anormale"                           : "Saignement anormal",
    "hémorragie menstruelle"                        : "Ménorragie",
    "hémorragie oesophagienne"                      : "Varices oesophagiennes",
    "héméralopie"                                   : "Perte de vision nocturne",
    "ict"                                           : "AVC transitoire",
    "ictère discret"                                : "Légère jaunisse",
    "images tordues"                                : "Vision déformée",
    "immunodépression"                              : "Infections fréquentes",
    "impact psychologique"                          : "Impact psychologique",
    "impatience excessive"                          : "Irritabilité",
    "inconfort"                                     : "Inconfort",
    "incontinence"                                  : "Incontinence",
    "incontinence fécale"                           : "Urgence défécation",
    "incontinence urinaire"                         : "Incontinence",
    "indigestion"                                   : "Indigestion",
    "indisposition"                                 : "Malaise",
    "infection"                                     : "Infection",
    "infection des trompes"                         : "Salpingite",
    "infection du col"                              : "Cervicite",
    "infection grave avec choc"                     : "Choc septique",
    "infection secondaire"                          : "Infection secondaire",
    "infection urinaire"                            : "Bactériurie",
    "infections qui reviennent"                     : "Infections récurrentes",
    "infections urinaires répétées"                 : "Infections urinaires",
    "inflammation de la langue"                     : "Glossite",
    "inflammation de la plèvre"                     : "Pleurite",
    "inflammation des amygdales"                    : "Amygdalite",
    "inflammation des yeux"                         : "Conjonctivite",
    "inflammation intérieure de l'oeil"             : "Uvéite",
    "inflammation urètre"                           : "Urétrite",
    "instabilité végétative"                        : "Instabilité végétative",
    "instabilité à la marche"                       : "Chute",
    "intestin irritable"                            : "Syndrome côlon irritable",
    "intestin n'absorbe pas bien"                   : "Malabsorption",
    "intestins capricieux"                          : "Alternance diarrhée-constipation",
    "intolérance UV"                                : "Sensibilité solaire",
    "intolérance au soleil"                         : "Photosensibilité",
    "irradiation dorsale"                           : "Douleur irradiant dans le dos",
    "irradiation vers épaule droite"                : "Douleur irradiant épaule droite",
    "irritabilite"                                  : "Irritabilité",
    "irritabilité"                                  : "Irritabilité",
    "irritation cutanée"                            : "Irritation cutanée",
    "irritation génitale"                           : "Irritation génitale",
    "irritation throat"                             : "Mal de gorge",
    "ischémie cérébrale transitoire"                : "AVC transitoire",
    "jambe douloureuse"                             : "Douleur membre inférieur",
    "jambe gonflée"                                 : "Jambe gonflée",
    "jambes qui font mal à la marche"               : "Claudication",
    "jet d'urine réduit"                            : "Jet urinaire faible",
    "jet urinaire difficile"                        : "Difficulté à uriner",
    "jet urinaire faible"                           : "Flux faible",
    "joue douloureuse"                              : "Douleur faciale",
    "joues gonflées"                                : "Gonflement parotides",
    "joues rouges"                                  : "Rougeur du visage",
    "kilos qui arrivent vite"                       : "Prise de poids rapide",
    "koïlonychie"                                   : "Koïlonychie",
    "kystes"                                        : "Kystes",
    "kératite ulcéreuse"                            : "Ulcère cornéen",
    "kératoconjonctivite sèche"                     : "Sécheresse oculaire",
    "langage perturbé"                              : "Difficultés de langage",
    "langue douloureuse"                            : "Glossite",
    "langue rouge"                                  : "Glossite",
    "larynx douloureux"                             : "Douleur laryngée",
    "lecture difficile"                             : "Difficulté à lire",
    "lenteur des mouvements"                        : "Lenteur de mouvement",
    "leucodermie"                                   : "Leucodermie",
    "leucoplasie"                                   : "Points blancs",
    "lichénification"                               : "Lichénification",
    "lignes ondulées dans la vision"                : "Lignes ondulées",
    "limitation des activités"                      : "Limitation de l'activité",
    "limitation des mouvements"                     : "Restriction de mobilité",
    "liquide dans l'abdomen"                        : "Ascite",
    "liquide qui sort"                              : "Écoulement",
    "lithiase rénale associée"                      : "Lithiase rénale associée",
    "lumière trop forte"                            : "Sensibilité à la lumière",
    "lumières avant la crise"                       : "Aura",
    "lèvres bleues"                                 : "Cyanose",
    "lèvres enflées"                                : "Gonflement des lèvres",
    "lèvres gonflées"                               : "Gonflement des lèvres",
    "léger dédoublement visuel"                     : "Diplopie légère",
    "légère irritation cutanée"                     : "Démangeaisons légères",
    "légère teinte bleue"                           : "Cyanose légère",
    "légère température"                            : "Fièvre légère",
    "légèrement jaune"                              : "Légère jaunisse",
    "légèrement ça gratte"                          : "Prurit léger",
    "lésions en grappe"                             : "Lésions groupées",
    "lésions muqueuses"                             : "Lésions muqueuses",
    "lésions qui saignent"                          : "Saignement des plaques",
    "lésions sur les muqueuses"                     : "Ulcérations muqueuses",
    "lésions éparpillées"                           : "Lésions dispersées",
    "lésions érodées"                               : "Érosions",
    "mains et pieds qui grandissent"                : "Agrandissement des mains/pieds",
    "mains qui s'élargissent"                       : "Agrandissement des mains/pieds",
    "mal au ventre après repas gras"                : "Douleur après repas gras",
    "mal aux dents"                                 : "Douleur dentaire",
    "mal dans le cou"                               : "Douleur au cou",
    "mal entendre"                                  : "Difficulté à entendre",
    "mal perforant plantaire"                       : "Ulcères des pieds",
    "mal à avaler"                                  : "Difficultés à avaler",
    "mal à l'aise"                                  : "Inconfort",
    "mal à l'oreille"                               : "Otalgie",
    "mal à la gorge en parlant"                     : "Douleur laryngée",
    "mal à respirer allongé"                        : "Dyspnée de décubitus",
    "mal à respirer après avoir mangé"              : "Essoufflement postprandial",
    "mal à voir la nuit"                            : "Vision nocturne difficile",
    "malabsorption"                                 : "Malabsorption",
    "malade souvent"                                : "Infections fréquentes",
    "maladie qui revient"                           : "Récidives",
    "malaise sucre"                                 : "Hypoglycémie",
    "manger trop"                                   : "Faim excessive",
    "manque d'air en marchant"                      : "Dyspnée d'effort",
    "manque d'attention"                            : "Difficultés de concentration",
    "manque d'eau"                                  : "Déshydratation",
    "manque de globules rouges"                     : "Anémie",
    "manque de salive"                              : "Sécheresse buccale",
    "marche difficile"                              : "Difficultés à marcher",
    "marcher difficile"                             : "Trouble de la marche",
    "marques sur la peau"                           : "Cicatrices",
    "masque facial"                                 : "Visage inexpressif",
    "maux de tete diffus"                           : "Maux de tête",
    "maux de tête le matin"                         : "Maux de tête matinaux",
    "maux de tête sévère"                           : "Céphalées sévères",
    "membres engourdis"                             : "Engourdissement",
    "microbe dans le corps"                         : "Infection",
    "mictions fréquentes"                           : "Fréquence urinaire",
    "migraine pulsatile"                            : "Pulsation céphalique",
    "migraine sévère"                               : "Céphalées sévères",
    "mini avc"                                      : "AVC transitoire",
    "mobilité réduite"                              : "Restriction de mobilité",
    "moiteur froide"                                : "Sueurs froides",
    "molluscum"                                     : "Excroissance cutanée",
    "molluscum contagiosum"                         : "Petites bosses ombiliquées",
    "moral effondré"                                : "Dépression",
    "mouvements au ralenti"                         : "Lenteur de mouvement",
    "mouvements automatiques"                       : "Mouvements automatiques",
    "mucus dans les selles"                         : "Mucus dans les selles",
    "mucus expulsé"                                 : "Expectoration",
    "mucus nasal épais"                             : "Sécrétions nasales épaisses",
    "muguet"                                        : "Candidose buccale",
    "muscles accessoires pour respirer"             : "Utilisation muscles accessoires",
    "muscles contracturés"                          : "Spasticité",
    "muscles qui disparaissent"                     : "Atrophie musculaire",
    "muscles qui fondent"                           : "Atrophie musculaire",
    "muscles qui tressautent"                       : "Fasciculations",
    "muscles rigides"                               : "Rigidité",
    "mycose buccale"                                : "Candidose buccale",
    "myokymie"                                      : "Fasciculations",
    "myopie"                                        : "Vision floue de loin",
    "myxoedème"                                     : "Myxœdème",
    "mâchoire douloureuse"                          : "Douleur à la mâchoire",
    "mèche blanche"                                 : "Poliose",
    "mélancolie"                                    : "Dépression",
    "mélanodermie"                                  : "Taches sombres",
    "métamorphopsies"                               : "Lignes ondulées",
    "métrorragie"                                   : "Saignement intermenstruel",
    "météorisme"                                    : "Gaz",
    "ne peut pas dormir à plat"                     : "Orthopnée",
    "ne peut pas retenir l'urine"                   : "Urgence urinaire",
    "ne peut pas se concentrer"                     : "Difficultés de concentration",
    "ne peut pas se retenir"                        : "Incontinence",
    "ne peut pas se retenir pour déféquer"          : "Urgence défécation",
    "ne peut pas vider la vessie"                   : "Rétention urinaire",
    "ne peut plus bouger"                           : "Paralysie",
    "ne peut plus faire de sport"                   : "Dyspnée d'effort",
    "ne peut plus faire ses activités"              : "Limitation de l'activité",
    "ne peut plus goûter"                           : "Perte de goût",
    "ne peut plus lever les bras"                   : "Faiblesse des membres",
    "ne peut plus lire"                             : "Difficulté à lire",
    "ne peut plus manger beaucoup"                  : "Satiété précoce",
    "ne peut plus se débrouiller seul"              : "Perte d'autonomie",
    "ne peut plus sentir"                           : "Perte d'odorat",
    "ne plus entendre"                              : "Perte d'audition",
    "ne plus voir le contraste"                     : "Perte de contraste",
    "ne sait plus ce qu'il dit"                     : "Délire",
    "ne se sent pas bien"                           : "Malaise",
    "ne voit plus"                                  : "Perte de vision",
    "nerf optique enflammé"                         : "Névrite optique",
    "nerfs périphériques atteints"                  : "Névrite périphérique",
    "nerveux"                                       : "Agitation",
    "nervosite"                                     : "Irritabilité",
    "neuropathie"                                   : "Névrite périphérique",
    "neuropathie brûlante"                          : "Brûlures aux pieds",
    "nez avec mucus épais"                          : "Sécrétions nasales épaisses",
    "nez irrité"                                    : "Démangeaisons nasales",
    "nez qui gratte"                                : "Démangeaisons nasales",
    "nocturia"                                      : "Nocturia",
    "nodules"                                       : "Nodules",
    "nodules autour des articulations"              : "Nodules rhumatoïdes",
    "nodules cutanés"                               : "Nodules cutanés",
    "nodules rhumatoïdes"                           : "Nodules rhumatoïdes",
    "nuque douloureuse"                             : "Douleur à la nuque",
    "nuque tendue"                                  : "Tension nucale",
    "nutriments mal absorbés"                       : "Malabsorption",
    "nyctalopie"                                    : "Vision nocturne difficile",
    "néphrite"                                      : "Néphrite lupique",
    "névralgie"                                     : "Douleur neuropathique",
    "névralgie faciale"                             : "Douleur faciale",
    "névrite optique"                               : "Névrite optique",
    "névrite périphérique"                          : "Névrite périphérique",
    "objets ondulés"                                : "Métamorphopsies",
    "odeurs intolérables"                           : "Sensibilité aux odeurs",
    "odorat diminué"                                : "Perte d'odorat",
    "oedème blanc du visage"                        : "Myxœdème",
    "oedème de quincke"                             : "Angioedème",
    "oedème du visage"                              : "Oedème facial",
    "oedème unilatéral de la jambe"                 : "Jambe gonflée",
    "oeil enflammé"                                 : "Uvéite",
    "oeil qui brûle par sécheresse"                 : "Sécheresse oculaire",
    "oeil sec"                                      : "Œil sec",
    "ongles concaves"                               : "Koïlonychie",
    "ongles en cuillère"                            : "Koïlonychie",
    "orchialgie"                                    : "Douleur testiculaire",
    "oreille douloureuse"                           : "Otalgie",
    "oreille qui coule"                             : "Écoulement auriculaire",
    "oreillons"                                     : "Gonflement parotides",
    "organes génitaux irrités"                      : "Irritation génitale",
    "oropharynx érythémateux"                       : "Rougeur pharyngée",
    "orthopnée"                                     : "Orthopnée",
    "os fragiles"                                   : "Fragilité osseuse",
    "osmophobie"                                    : "Sensibilité aux odeurs",
    "ostéoporose"                                   : "Fragilité osseuse",
    "otorrhée"                                      : "Écoulement auriculaire",
    "pancréatite position antalgique"               : "Douleur calmée penché en avant",
    "papillon sur le visage"                        : "Éruption malaire",
    "papules"                                       : "Papules",
    "papules de gottron"                            : "Papules de Gottron",
    "papules gottron"                               : "Papules de Gottron",
    "paralysie"                                     : "Paralysie",
    "paralysie d'un côté du visage"                 : "Paralysie faciale",
    "paralysie qui monte"                           : "Faiblesse ascendante",
    "paresthésies"                                  : "Paresthésies",
    "parole embrouillée"                            : "Difficultés à parler",
    "parole mal articulée"                          : "Dysarthrie",
    "parotides gonflées"                            : "Gonflement parotides",
    "pas de réflexes"                               : "Réflexes abolis",
    "pas reposé le matin"                           : "Fatigue au réveil",
    "pas vidé après selles"                         : "Sensation vidange incomplète",
    "paumes rouges"                                 : "Érythème palmaire",
    "paupières jaunâtres"                           : "Dépôts lipidiques aux paupières",
    "paupières qui se ferment"                      : "Blépharospasme",
    "peau bleue"                                    : "Cyanose",
    "peau bouffie"                                  : "Myxœdème",
    "peau fissurée"                                 : "Crevasses",
    "peau foncée en certains endroits"              : "Hyperpigmentation",
    "peau fragile"                                  : "Fragilité cutanée",
    "peau grasse"                                   : "Peau grasse",
    "peau irritée"                                  : "Irritation cutanée",
    "peau légèrement jaunâtre"                      : "Légère jaunisse",
    "peau qui brûle"                                : "Brûlures cutanées",
    "peau qui durcit"                               : "Durcissement cutané",
    "peau qui se desquame"                          : "Squames",
    "peau qui se déchire"                           : "Fragilité cutanée",
    "peau qui se fissure"                           : "Fissures cutanées",
    "peau qui tire"                                 : "Sécheresse cutanée",
    "peau rouge"                                    : "Rougeur cutanée",
    "peau rugueuse"                                 : "Rugosité cutanée",
    "peau rugueuse et épaisse"                      : "Peau épaissie",
    "peau rêche"                                    : "Rugosité cutanée",
    "peau tendue et dure"                           : "Durcissement cutané",
    "peau épaissie"                                 : "Peau épaissie",
    "peau épaissie par grattage"                    : "Lichénification",
    "pellicules cutanées"                           : "Squames",
    "perdu dans l'espace"                           : "Désorientation",
    "perles cutanées"                               : "Petites bosses ombiliquées",
    "perte auditive"                                : "Difficulté à entendre",
    "perte d'autonomie"                             : "Perte d'autonomie",
    "perte de conscience"                           : "Évanouissement",
    "perte de force brusque"                        : "Faiblesse soudaine",
    "perte de sensibilité"                          : "Perte de sensibilité",
    "perte de vision"                               : "Perte de vision",
    "perte des cheveux"                             : "Alopécie",
    "perte des facultés mentales"                   : "Démence",
    "petit mal"                                     : "Absence",
    "petite jaunisse"                               : "Ictère léger",
    "petite écriture parkinson"                     : "Écriture micrographique",
    "petites bosses"                                : "Nodules",
    "petites bosses ombiliquées"                    : "Petites bosses ombiliquées",
    "petites bosses sous la peau"                   : "Nodules cutanés",
    "petites taches blanches dans la bouche"        : "Taches de Koplik",
    "petites taches roses"                          : "Rash rose",
    "petits boutons solides"                        : "Papules",
    "petits cailloux sous la peau"                  : "Calcinose",
    "petits mouvements musculaires involontaires"   : "Fasciculations",
    "pharynx rouge"                                 : "Rougeur pharyngée",
    "phlébite"                                      : "Phlébite",
    "photophobie légère"                            : "Éblouissement",
    "phénomène de raynaud"                          : "Raynaud",
    "picotements et fourmis"                        : "Paresthésies",
    "pierres dans la vésicule"                      : "Lithiase biliaire",
    "pipi brun ou foncé"                            : "Urine foncée",
    "pipi lent"                                     : "Flux faible",
    "pipi lent et faible"                           : "Jet urinaire faible",
    "pipi trouble"                                  : "Urine trouble",
    "piquer en faisant pipi"                        : "Brûlures urinaires",
    "plaie qui suinte"                              : "Suintement",
    "plaie sur la cornée"                           : "Ulcère cornéen",
    "plaies aux pieds"                              : "Ulcères des pieds",
    "plaies muqueuses"                              : "Ulcérations",
    "plaies plantaires"                             : "Ulcères des pieds",
    "plaies qui forment des croûtes"                : "Croûtes",
    "plaies qui ne guérissent pas"                  : "Plaies lentes à cicatriser",
    "plaies qui s'infectent"                        : "Plaies lentes à cicatriser",
    "plaies superficielles"                         : "Érosions",
    "plaies sur les muqueuses"                      : "Lésions muqueuses",
    "plaques blanches argentées"                    : "Squames argentées",
    "plaques blanches sur la gorge"                 : "Taches blanches pharyngées",
    "plaques graisseuses"                           : "Xanthomes",
    "plaques qui durent"                            : "Éruption chronique",
    "pleurite"                                      : "Pleurite",
    "pleurodynie"                                   : "Douleur thoracique pleurétique",
    "plisser les yeux"                              : "Plissement des yeux",
    "plégie"                                        : "Paralysie",
    "poches de liquide"                             : "Kystes",
    "poils anormaux"                                : "Pilosité excessive",
    "poils en excès"                                : "Pilosité excessive",
    "point aveugle"                                 : "Scotome",
    "point de côté respiratoire"                    : "Douleur thoracique pleurétique",
    "points blancs"                                 : "Points blancs",
    "poitrine chez l'homme"                         : "Gynécomastie",
    "poitrine gonflée"                              : "Barrel chest",
    "poliose"                                       : "Poliose",
    "pollakiurie"                                   : "Besoin fréquent d'uriner",
    "polyadénopathie"                               : "Lymphadénopathie",
    "polyphagie"                                    : "Faim excessive",
    "pouls lent"                                    : "Bradycardie",
    "pouls normal malgré fièvre"                    : "Bradycardie relative",
    "pouls rapide"                                  : "Tachycardie",
    "poumons qui se fibrosent"                      : "Fibrose pulmonaire",
    "pousser fort pour déféquer"                    : "Efforts pour défécation",
    "poussées répétées"                             : "Récidives",
    "presbytie"                                     : "Vision floue de près",
    "pression abdominale"                           : "Sensation de pression",
    "pression dans la tête"                         : "Sensation de pression",
    "pression dans la veine porte"                  : "Hypertension portale",
    "prise de poids rapide"                         : "Prise de poids rapide",
    "problème d'équilibre"                          : "Trouble de l'équilibre",
    "problème de marche"                            : "Difficultés à marcher",
    "problèmes de mémoire et attention"             : "Troubles cognitifs",
    "problèmes mentaux liés à la maladie"           : "Impact psychologique",
    "problèmes nerveux"                             : "Complications neurologiques",
    "problèmes pour uriner"                         : "Troubles urinaires",
    "problèmes respiratoires"                       : "Dyspnée",
    "propos incohérents"                            : "Délire",
    "prosodie absente"                              : "Voix monotone",
    "prosopoplégie"                                 : "Paralysie faciale",
    "protéines basses dans le sang"                 : "Albuminémie basse",
    "protéines dans les urines"                     : "Protéinurie",
    "prurit intense"                                : "Prurit sévère",
    "prurit localisé"                               : "Démangeaisons locales",
    "prurit léger"                                  : "Prurit léger",
    "prurit nasal"                                  : "Démangeaisons nasales",
    "prurit périnéal"                               : "Démangeaisons génitales",
    "prurit vulvaire"                               : "Démangeaisons génitales",
    "pré-hypertension"                              : "Hypertension légère",
    "psoriasis squameux"                            : "Squames argentées",
    "ptosis"                                        : "Yeux plissés",
    "pulsation dans la tête"                        : "Pulsation céphalique",
    "pus qui s'écoule"                              : "Écoulement purulent",
    "pyurie"                                        : "Urine trouble",
    "périnée douloureux"                            : "Douleur périnéale",
    "quelque chose qui bloque"                      : "Sensation de blocage",
    "rage de dents"                                 : "Douleur dentaire",
    "raideur articulaire"                           : "Restriction de mobilité",
    "raideur de nuque"                              : "Tension nucale",
    "raideur spastique"                             : "Spasticité",
    "ralentissement cognitif"                       : "Ralentissement intellectuel",
    "rapport sexuel douloureux"                     : "Dyspareunie",
    "rapports sexuels douloureux"                   : "Douleur lors des rapports",
    "rarement aller aux selles"                     : "Infrequence des selles",
    "rash avec démangeaisons"                       : "Éruption prurigineuse",
    "rash cutané"                                   : "Éruption",
    "rash photosensible"                            : "Rash photosensible",
    "rash rose"                                     : "Rash rose",
    "rassasiement précoce"                          : "Sensation de satiété rapide",
    "rassasié rapidement"                           : "Satiété précoce",
    "rechutes"                                      : "Récidives",
    "rechutes fréquentes"                           : "Infections récurrentes",
    "rectorragie"                                   : "Sang dans les selles",
    "rein attaqué par lupus"                        : "Néphrite lupique",
    "retentissement psychologique"                  : "Impact psychologique",
    "rhinorrhée"                                    : "Écoulement nasal",
    "rigidité"                                      : "Rigidité",
    "rigors"                                        : "Frissons intenses",
    "roséole"                                       : "Rash rose",
    "rot"                                           : "Rot",
    "rots acides"                                   : "Éructations",
    "rots fréquents"                                : "Rot",
    "rougeur"                                       : "Rougeur",
    "rougeur cutanée"                               : "Érythème",
    "rougeur violacée"                              : "Héliotrope éruption",
    "rougeurs en plaques"                           : "Plaques rouges",
    "rougissement cutané"                           : "Rougeur cutanée",
    "rythme cardiaque lent"                         : "Bradycardie",
    "règles qui durent longtemps"                   : "Ménorragie",
    "règles très abondantes"                        : "Ménorragie",
    "réaction cutanée à la lumière"                 : "Rash photosensible",
    "réflexes abolies"                              : "Réflexes abolis",
    "réflexes absents"                              : "Perte de réflexes",
    "réflexion plus lente"                          : "Ralentissement intellectuel",
    "régulation autonome perturbée"                 : "Instabilité végétative",
    "rétention d'urines"                            : "Rétention urinaire",
    "rétention urinaire partielle"                  : "Difficulté à uriner",
    "réveil avec mal de tête"                       : "Maux de tête matinaux",
    "réveil difficile à respirer"                   : "Dyspnée nocturne",
    "réveil douloureux"                             : "Douleurs nocturnes",
    "réveil par la toux"                            : "Toux nocturne",
    "réveillé par la douleur"                       : "Douleur nocturne",
    "sable dans les yeux"                           : "Sensation de corps étranger",
    "saignement"                                    : "Saignement",
    "saignement anormal"                            : "Saignement anormal",
    "saignement articulaire"                        : "Hémarthrose",
    "saignement dans l'oeil"                        : "Hémorragie rétinienne",
    "saignement des plaques"                        : "Saignement des plaques",
    "saignement digestif"                           : "Saignement digestif",
    "saignement gencives"                           : "Saignement gencives",
    "saignement gingival"                           : "Saignement des gencives",
    "saignement sans raison"                        : "Saignement anormal",
    "saignements"                                   : "Saignements",
    "saignements digestifs"                         : "Saignements digestifs",
    "saignements du rectum"                         : "Saignements rectaux",
    "saignements entre les règles"                  : "Saignement intermenstruel",
    "saignements menstruels abondants"              : "Ménorragie",
    "salpingite"                                    : "Salpingite",
    "sang dans l'articulation"                      : "Hémarthrose",
    "sang dans les intestins"                       : "Saignement digestif",
    "sang dans les selles ou vomissements"          : "Saignements digestifs",
    "sang pauvre"                                   : "Anémie",
    "sclérose cutanée"                              : "Durcissement cutané",
    "scotome"                                       : "Scotome",
    "scotome central"                               : "Scotome central",
    "se mordre la langue"                           : "Morsure de langue",
    "se sent vite rassasié"                         : "Satiété précoce",
    "seins chez l'homme"                            : "Gynécomastie",
    "selles acholiques"                             : "Selles pâles",
    "selles avec glaires"                           : "Mucus dans les selles",
    "selles blanches"                               : "Selles pâles",
    "selles décolorées"                             : "Selles pâles",
    "selles grises"                                 : "Selles pâles",
    "selles peu fréquentes"                         : "Infrequence des selles",
    "sensation de brûlure"                          : "Sensation de brûlure",
    "sensation de brûlure dans les pieds"           : "Brûlures aux pieds",
    "sensation de brûlure sur la peau"              : "Brûlures cutanées",
    "sensation de chaleur"                          : "Chaleur",
    "sensation de course cardiaque"                 : "Sensation d'accélération",
    "sensation de pesanteur"                        : "Sensation de pression",
    "sensation de soif"                             : "Soif",
    "sensations anormales"                          : "Paresthésies",
    "sensible au soleil"                            : "Sensibilité solaire",
    "sensible aux lumières vives"                   : "Éblouissement",
    "sensible aux odeurs"                           : "Sensibilité aux odeurs",
    "sensible quand on appuie"                      : "Sensibilité à la palpation",
    "sentiment de mal-être"                         : "Malaise",
    "sepsis sévère"                                 : "Choc septique",
    "sexe qui brûle"                                : "Brûlures génitales",
    "sexe qui gratte"                               : "Démangeaisons génitales",
    "sifflement bronchique"                         : "Wheezing",
    "sifflements dans les oreilles"                 : "Bourdonnements",
    "signe de la rougeole"                          : "Taches de Koplik",
    "signes avant-coureurs"                         : "Aura",
    "silencieux cliniquement"                       : "Souvent asymptomatique",
    "soif"                                          : "Soif",
    "souffle court à l'effort"                      : "Essoufflement d'effort",
    "souffle qui diminue avec le temps"             : "Dyspnée progressive",
    "souvent sans symptômes"                        : "Souvent asymptomatique",
    "spasme des paupières"                          : "Blépharospasme",
    "spasticité"                                    : "Spasticité",
    "spotting"                                      : "Saignement intermenstruel",
    "squames argentées"                             : "Squames argentées",
    "stridor"                                       : "Stridor inspiratoire",
    "stries cutanées"                               : "Vergetures",
    "striures de la peau"                           : "Vergetures",
    "subictère"                                     : "Ictère léger",
    "sucre bas"                                     : "Hypoglycémie",
    "sucre instable"                                : "Déséquilibre glycémique",
    "sueurs froides"                                : "Sueurs froides",
    "suintement"                                    : "Suintement",
    "suppuration"                                   : "Écoulement purulent",
    "surdité"                                       : "Perte d'audition",
    "surdité partielle"                             : "Difficulté à entendre",
    "surinfection"                                  : "Infection secondaire",
    "susceptibilité"                                : "Irritabilité",
    "syncope"                                       : "Évanouissement",
    "syncopes répétées"                             : "Évanouissements",
    "syndrome côlon irritable"                      : "Syndrome côlon irritable",
    "séborrhée"                                     : "Peau grasse",
    "sécheresse oculaire"                           : "Secheresse oculaire",
    "sécheresse oculaire sévère"                    : "Œil sec",
    "sécrétions nasales épaisses"                   : "Sécrétions nasales épaisses",
    "sécrétions oculaires"                          : "Yeux collants",
    "taches blanches"                               : "Points blancs",
    "taches blanches dans la bouche"                : "Candidose buccale",
    "taches blanches de dépigmentation"             : "Leucodermie",
    "taches blanches gorge"                         : "Taches blanches pharyngées",
    "taches brunes"                                 : "Hyperpigmentation",
    "taches de koplik"                              : "Taches de Koplik",
    "taches rouges dans la vue"                     : "Hémorragie rétinienne",
    "taches sombres"                                : "Taches sombres",
    "talons crevassés"                              : "Crevasses",
    "taux d'hémoglobine bas"                        : "Anémie",
    "teinte bleutée"                                : "Cyanose",
    "tendance aux ecchymoses"                       : "Ecchymoses faciles",
    "tendance hémorragique"                         : "Saignements",
    "tendon douloureux"                             : "Enthésite",
    "tenir la lecture à bout de bras"               : "Nécessité d'éloigner la lecture",
    "tension dans la nuque"                         : "Tension nucale",
    "tension légèrement élevée"                     : "Hypertension légère",
    "terrible céphalée"                             : "Céphalées sévères",
    "terrible mal de tête"                          : "Céphalées sévères",
    "testicule douloureux"                          : "Douleur testiculaire",
    "texte flou à la lecture"                       : "Difficulté à lire",
    "thorax en tonneau"                             : "Barrel chest",
    "thrombose"                                     : "Thrombose",
    "thrombose veineuse superficielle"              : "Phlébite",
    "thyroïde douloureuse"                          : "Douleur thyroïdienne",
    "thyroïde temporairement hyperactive"           : "Hyperthyroïdie transitoire",
    "tirer les muscles du cou"                      : "Utilisation muscles accessoires",
    "tissu mort aux extrémités"                     : "Gangrène distale",
    "tomber souvent"                                : "Chute",
    "tonsillite"                                    : "Amygdalite",
    "torticolis"                                    : "Douleur au cou",
    "toujours fatigué"                              : "Fatigue chronique",
    "toux chronique"                                : "Toux chronique",
    "toux d'aboiement"                              : "Toux aboyante",
    "toux de plus de 3 semaines"                    : "Toux chronique",
    "toux depuis des semaines"                      : "Toux persistante",
    "toux la nuit"                                  : "Toux nocturne",
    "toux persistante"                              : "Toux chronique",
    "toux qui dure"                                 : "Toux chronique",
    "toux qui ne part pas"                          : "Toux persistante",
    "toux rauque"                                   : "Toux aboyante",
    "traits qui s'élargissent"                      : "Grossissement du visage",
    "transit irrégulier"                            : "Alternance diarrhée-constipation",
    "transpiration"                                 : "Sueurs",
    "transpiration froide"                          : "Sueurs froides",
    "tristesse profonde"                            : "Dépression",
    "trompe infectée"                               : "Salpingite",
    "trou au centre de la vision"                   : "Scotome central",
    "trou au centre du regard"                      : "Vision centrale floue",
    "trou dans la vision"                           : "Scotome",
    "trouble de la marche"                          : "Trouble de la marche",
    "troubles auditifs"                             : "Perte d'audition",
    "troubles cognitifs"                            : "Troubles cognitifs",
    "troubles urinaires"                            : "Troubles urinaires",
    "très forte démangeaison"                       : "Prurit sévère",
    "tuméfaction"                                   : "Gonflement",
    "tunnel entre organes"                          : "Fistules",
    "ténesme"                                       : "Sensation d'évacuation incomplète",
    "tête douloureuse"                              : "Céphalées",
    "tête qui bat"                                  : "Pulsation céphalique",
    "ulcère cornéen"                                : "Ulcère cornéen",
    "ulcérations"                                   : "Ulcérations",
    "ulcérations muqueuses"                         : "Ulcérations muqueuses",
    "une seule jambe gonflée"                       : "Oedème unilatéral",
    "urge incontinence"                             : "Urgence urinaire",
    "urgence pour aller aux toilettes"              : "Besoin impérieux de déféquer",
    "urgence pour les selles"                       : "Urgence défécation",
    "uricémie élevée"                               : "Hyperuricémie",
    "urination douloureuse"                         : "Dysurie",
    "urine foncée"                                  : "Urine foncée",
    "uriner est difficile"                          : "Difficulté à uriner",
    "uriner fait mal et brûle"                      : "Brûlures urinaires",
    "uriner plusieurs fois"                         : "Fréquence urinaire",
    "uriner trop souvent"                           : "Besoin fréquent d'uriner",
    "urines infectées"                              : "Bactériurie",
    "urines nuageuses"                              : "Urine trouble",
    "urines peu abondantes"                         : "Oligurie",
    "urines sombres"                                : "Urine foncée",
    "urètre infecté"                                : "Urétrite",
    "urètre qui gratte"                             : "Prurit urétral",
    "urétrite"                                      : "Urétrite",
    "uvéite"                                        : "Uvéite",
    "vaginisme"                                     : "Dyspareunie",
    "vaisseaux visibles dans les yeux"              : "Injection conjonctivale",
    "varices oesophagiennes"                        : "Varices oesophagiennes",
    "veine douloureuse"                             : "Phlébite",
    "veines gonflées dans l'oesophage"              : "Varices oesophagiennes",
    "ventre plein de gaz"                           : "Gaz",
    "ventre qui gonfle d'eau"                       : "Ascite",
    "ventre très douloureux"                        : "Douleur abdominale sévère",
    "vergetures"                                    : "Vergetures",
    "verruca plantaris"                             : "Verrue plantaire douloureuse",
    "verrue"                                        : "Excroissance cutanée",
    "verrue génitale"                               : "Verrue génitale",
    "verrue sous le pied"                           : "Verrue plantaire douloureuse",
    "verrues génitales"                             : "Verrues génitales",
    "vertige aigu"                                  : "Vertige soudain",
    "vertige brutal"                                : "Vertige soudain",
    "visage engourdi"                               : "Engourdissement facial",
    "visage figé"                                   : "Visage inexpressif",
    "visage gonflé"                                 : "Oedème facial",
    "visage gras"                                   : "Peau grasse",
    "visage qui grossit"                            : "Grossissement du visage",
    "visage qui s'affaisse"                         : "Paralysie faciale",
    "visage rouge"                                  : "Visage rouge",
    "vision de près floue"                          : "Vision rapprochée floue",
    "vision distordue"                              : "Métamorphopsies",
    "vision double"                                 : "Diplopie",
    "vision du côté réduite"                        : "Perte de vision périphérique",
    "vision en tunnel"                              : "Vision tunnel",
    "vision jaune"                                  : "Vision jaunâtre",
    "vision légèrement floue"                       : "Vision floue légère",
    "vision nocturne mauvaise"                      : "Perte de vision nocturne",
    "vision qui baisse"                             : "Perte de vision progressive",
    "vision sans contraste"                         : "Perte de contraste",
    "vision tunnel"                                 : "Perte de vision périphérique",
    "voir déformé"                                  : "Vision déformée",
    "voir en double"                                : "Diplopie",
    "voir flou de près"                             : "Flou proche",
    "voir les objets déformés"                      : "Métamorphopsies",
    "voir mal la nuit"                              : "Difficulté nocturne",
    "voix basse anormale"                           : "Voix grave",
    "voix disparaît"                                : "Perte de voix",
    "voix grave"                                    : "Voix grave",
    "voix monocorde"                                : "Voix monotone",
    "voix pâteuse"                                  : "Dysarthrie",
    "voix sans intonation"                          : "Voix monotone",
    "voix éteinte"                                  : "Perte de voix",
    "vomissement de sang"                           : "Hémorragie digestive",
    "végétations vénériennes"                       : "Verrue génitale",
    "vésicule pleine de calculs"                    : "Lithiase biliaire",
    "xanthomes"                                     : "Xanthomes",
    "xanthomes tendineux"                           : "Xanthomes tendineux",
    "xanthopsie"                                    : "Vision jaunâtre",
    "xanthélasma"                                   : "Dépôts lipidiques aux paupières",
    "xérose"                                        : "Sécheresse cutanée",
    "xérostomie"                                    : "Sécheresse buccale",
    "xérostomie matinale"                           : "Bouche sèche au réveil",
    "yeux collants"                                 : "Yeux collants",
    "yeux collés le matin"                          : "Yeux collants",
    "yeux enflés"                                   : "Gonflement des paupières",
    "yeux irrités qui grattent"                     : "Prurit oculaire",
    "yeux plissés"                                  : "Yeux plissés",
    "yeux proéminents"                              : "Yeux saillants",
    "yeux qui collent"                              : "Conjonctivite",
    "yeux qui fatiguent vite"                       : "Fatigue oculaire",
    "yeux qui grattent"                             : "Prurit oculaire",
    "yeux qui se plissent"                          : "Plissement des yeux",
    "yeux qui sont rouges"                          : "Injection conjonctivale",
    "yeux qui sortent"                              : "Yeux saillants",
    "yeux roses"                                    : "Conjonctivite",
    "yeux secs"                                     : "Sécheresse oculaire",
    "zigzags visuels"                               : "Aura",
    "zone sensible au toucher"                      : "Sensibilité à la palpation",
    "zones d'hyperpigmentation"                     : "Taches sombres",
    "ça gratte à un endroit précis"                 : "Démangeaisons locales",
    "ça gratte énormément"                          : "Prurit sévère",
    "éblouissement"                                 : "Éblouissement",
    "écoulement"                                    : "Écoulement",
    "écoulement auriculaire"                        : "Écoulement auriculaire",
    "écoulement de plaie"                           : "Suintement",
    "écoulement purulent"                           : "Écoulement purulent",
    "écriture micrographique"                       : "Écriture micrographique",
    "écriture qui rapetisse"                        : "Écriture micrographique",
    "éjaculation douloureuse"                       : "Éjaculation douloureuse",
    "épanchement abdominal"                         : "Ascite",
    "épaule qui fait mal"                           : "Douleur au bras/épaule",
    "épigastralgie brûlante"                        : "Brûlures épigastriques",
    "épuisement chronique"                          : "Fatigue chronique",
    "épuisement post-convulsif"                     : "Fatigue post-critique",
    "érosions"                                      : "Érosions",
    "éructation"                                    : "Rot",
    "éructations"                                   : "Éructations",
    "éruption au soleil"                            : "Rash photosensible",
    "éruption avec vésicules"                       : "Éruption vésiculaire",
    "éruption chronique"                            : "Éruption chronique",
    "éruption du visage"                            : "Éruption malaire",
    "éruption qui gratte"                           : "Éruption prurigineuse",
    "éruption rapide"                               : "Rash",
    "éruption sur les paumes"                       : "Éruption palmoplantaire",
    "éruption violacée"                             : "Héliotrope éruption",
    "érythromélalgie"                               : "Érythromélalgie",
    "érythème"                                      : "Érythème",
    "érythème facial"                               : "Visage rouge",
    "érythème malaire"                              : "Éruption malaire",
    "érythème palmaire"                             : "Érythème palmaire",
    "état de choc"                                  : "Choc",
    "éternuements"                                  : "Éternuements",
    "éternuements fréquents"                        : "Éternuements",
    "éternuer souvent"                              : "Éternuements",
    "évanouissements"                               : "Évanouissements",
    "œdème"                                         : "Gonflement",
    "œdème d'un seul côté"                          : "Oedème unilatéral",
    "œdème palpébral"                               : "Gonflement des paupières",
}

_DATASET_CANDIDATES = [
    # Nouveau dataset enrichi (403 features)
    os.path.join("..", "les ressources dataset", _DATASET_FILENAME),
    os.path.join("..", "..", "les ressources dataset", _DATASET_FILENAME),
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "les ressources dataset",
        _DATASET_FILENAME,
    ),
    # Fallback vers l'ancien dataset (400 features)
    os.path.join("..", "les ressources dataset", _DATASET_FILENAME_FALLBACK),
    os.path.join("..", "..", "les ressources dataset", _DATASET_FILENAME_FALLBACK),
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "les ressources dataset",
        _DATASET_FILENAME_FALLBACK,
    ),
]


class ModelManager:
    """
    Singleton pour gérer le modèle ML
    Assure qu'un seul modèle est chargé en mémoire
    """

    _instance: Optional["ModelManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.preprocessor = DataPreprocessor()
        self.trainer = ModelTrainer()
        self.predictor: Optional[Predictor] = None
        self.model_loaded = False
        self.model_version = None
        self.model_metadata = {}
        self.normalization_params: Dict = {}
        self.dataset_means: Dict = {}
        self._initialized = True

        logger.info("🤖 ModelManager initialisé")

    # ------------------------------------------------------------------
    # Chargement du modèle
    # ------------------------------------------------------------------

    def load_latest_model(self, model_path: str = "./ml_models/") -> bool:
        """Charge le dernier modèle entraîné"""
        try:
            if not os.path.exists(model_path):
                logger.warning(f"⚠️ Dossier modèles introuvable: {model_path}")
                return False

            model_files = [f for f in os.listdir(model_path) if f.endswith(".joblib")]
            if not model_files:
                logger.warning("⚠️ Aucun modèle trouvé")
                return False

            model_files.sort(reverse=True)
            latest_model = os.path.join(model_path, model_files[0])

            self.trainer.load_model(latest_model)

            # Corriger le mojibake dans les noms de maladies UNIQUEMENT (output)
            # Ne PAS toucher feature_names — sklearn valide contre les noms d'entraînement
            def _fix_moji(s: str) -> str:
                try:
                    return s.encode("latin-1").decode("utf-8")
                except (UnicodeEncodeError, UnicodeDecodeError):
                    return s

            self.trainer.label_encoder.classes_ = np.array(
                [str(_fix_moji(c)) for c in self.trainer.label_encoder.classes_]
            )

            self.predictor = Predictor(
                model=self.trainer.model,
                label_encoder=self.trainer.label_encoder,
                feature_names=self.trainer.feature_names,
            )

            self.model_loaded = True
            self.model_version = model_files[0]
            self.model_metadata = dict(self.trainer.training_history)

            # Compléter les métriques manquantes depuis le fichier _metadata.json
            missing = [k for k in ("precision", "recall", "f1_score") if k not in self.model_metadata]
            if missing:
                json_path = latest_model.replace(".joblib", "_metadata.json")
                if os.path.exists(json_path):
                    try:
                        with open(json_path, "r", encoding="utf-8") as f:
                            saved = json.load(f)
                        hist = saved.get("training_history", {})
                        for k in missing:
                            if k in hist:
                                self.model_metadata[k] = hist[k]
                        logger.info(f"Metriques supplementaires chargees depuis {os.path.basename(json_path)}")
                    except Exception as e:
                        logger.warning(f"Impossible de lire {json_path}: {e}")

            # Récupérer les params de normalisation sauvegardés avec le modèle
            self.normalization_params = self.trainer.normalization_params
            self.dataset_means = self.trainer.dataset_means

            # Fallback : calculer depuis le dataset si manquants
            if not self.normalization_params:
                logger.info("📊 Params de normalisation absents — calcul depuis le dataset...")
                self._load_normalization_from_dataset()

            logger.info(f"✅ Modèle chargé: {self.model_version}")
            logger.info(f"   Paramètres de normalisation: {len(self.normalization_params)} colonnes")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle: {e}")
            return False

    # ------------------------------------------------------------------
    # Normalisation
    # ------------------------------------------------------------------

    def _find_dataset_path(self) -> Optional[str]:
        """Cherche le fichier CSV du dataset dans plusieurs emplacements"""
        for path in _DATASET_CANDIDATES:
            if os.path.exists(path):
                logger.info(f"✅ Dataset trouvé: {path}")
                return path
        logger.warning("⚠️ Dataset CSV introuvable dans les emplacements connus")
        return None

    def _load_normalization_from_dataset(self) -> bool:
        """
        Calcule les paramètres de normalisation (min/max) et les moyennes
        en chargeant le dataset CSV d'entraînement.
        Utilisé en fallback quand le modèle .joblib ne les contient pas.
        """
        try:
            dataset_path = self._find_dataset_path()
            if not dataset_path:
                logger.warning("⚠️ Utilisation de plages médicales par défaut pour la normalisation")
                self._use_default_normalization()
                return False

            logger.info(f"📂 Calcul normalisation depuis: {dataset_path}")
            df = self.preprocessor.load_dataset(dataset_path)
            df, _ = self.preprocessor.clean_data(df)
            # Pas besoin de create_features() : Vital_ et Lab_ sont déjà dans le CSV brut
            norm_cols = [c for c in df.columns if c.startswith("Vital_") or c.startswith("Lab_")]
            for col in norm_cols:
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    raw_min  = float(df[col].min())
                    raw_max  = float(df[col].max())
                    raw_mean = float(df[col].mean())
                    self.normalization_params[col] = {"min": raw_min, "max": raw_max}
                    # Stocker la moyenne NORMALISÉE pour l'utiliser directement comme défaut
                    if raw_max > raw_min:
                        self.dataset_means[col] = (raw_mean - raw_min) / (raw_max - raw_min)
                    else:
                        self.dataset_means[col] = 0.5

            # Moyennes pour les features non normalisées (valeurs brutes)
            for col in ["Age", "Duree_Symptomes_Jours", "nombre_symptomes"]:
                if col in df.columns:
                    self.dataset_means[col] = float(df[col].mean())

            logger.info(f"✅ Normalisation calculée: {len(self.normalization_params)} colonnes")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur calcul normalisation depuis dataset: {e}")
            self._use_default_normalization()
            return False

    def _use_default_normalization(self):
        """Plages médicales de référence en dernier recours"""
        defaults = {
            "Vital_Tension Systolique (mmHg)":       {"min": 60,   "max": 250},
            "Vital_Tension Diastolique (mmHg)":      {"min": 30,   "max": 150},
            "Vital_Fréquence Cardiaque (bpm)":       {"min": 30,   "max": 200},
            "Vital_Fréquence Respiratoire (resp/min)": {"min": 8,  "max": 40},
            "Vital_Température (°C)":                {"min": 34,   "max": 42},
            "Vital_Saturation O2 (%)":               {"min": 70,   "max": 100},
            "Vital_IMC (kg/m²)":                     {"min": 10,   "max": 60},
            "Lab_Hémoglobine (g/dL)":                {"min": 3,    "max": 20},
            "Lab_Hématocrite (%)":                   {"min": 10,   "max": 65},
            "Lab_Globules Rouges (M/µL)":            {"min": 1,    "max": 8},
            "Lab_Globules Blancs (K/µL)":            {"min": 1,    "max": 50},
            "Lab_Neutrophiles (%)":                  {"min": 10,   "max": 95},
            "Lab_Lymphocytes (%)":                   {"min": 5,    "max": 60},
            "Lab_Monocytes (%)":                     {"min": 1,    "max": 20},
            "Lab_Eosinophiles (%)":                  {"min": 0,    "max": 30},
            "Lab_Basophiles (%)":                    {"min": 0,    "max": 5},
            "Lab_Plaquettes (K/µL)":                 {"min": 50,   "max": 600},
            "Lab_VGM (fL)":                          {"min": 60,   "max": 110},
            "Lab_CCMH (g/dL)":                       {"min": 28,   "max": 38},
            "Lab_Glucose (mg/dL)":                   {"min": 50,   "max": 500},
            "Lab_Glucose à jeun (mg/dL)":            {"min": 50,   "max": 500},
            "Lab_Glucose post-prandial (mg/dL)":     {"min": 70,   "max": 500},
            "Lab_HbA1c (%)":                         {"min": 3,    "max": 15},
            "Lab_Cholestérol total (mg/dL)":         {"min": 100,  "max": 400},
            "Lab_Cholestérol HDL (mg/dL)":           {"min": 20,   "max": 120},
            "Lab_Cholestérol LDL (mg/dL)":           {"min": 30,   "max": 300},
            "Lab_Triglycérides (mg/dL)":             {"min": 30,   "max": 800},
            "Lab_Acide urique (mg/dL)":              {"min": 1,    "max": 15},
            "Lab_Créatinine (mg/dL)":                {"min": 0.3,  "max": 15},
            "Lab_Urée (mg/dL)":                      {"min": 10,   "max": 200},
            "Lab_TFG (mL/min/1.73m²)":               {"min": 5,    "max": 120},
            "Lab_Sodium (mEq/L)":                    {"min": 120,  "max": 160},
            "Lab_Potassium (mEq/L)":                 {"min": 2,    "max": 8},
            "Lab_Chlore (mEq/L)":                    {"min": 90,   "max": 120},
            "Lab_Calcium (mg/dL)":                   {"min": 6,    "max": 14},
            "Lab_Phosphore (mg/dL)":                 {"min": 1,    "max": 8},
            "Lab_Magnésium (mg/dL)":                 {"min": 0.5,  "max": 4},
            "Lab_ALT/SGPT (U/L)":                    {"min": 5,    "max": 500},
            "Lab_AST/SGOT (U/L)":                    {"min": 5,    "max": 500},
            "Lab_Bilirubine totale (mg/dL)":         {"min": 0.1,  "max": 20},
            "Lab_Bilirubine conjuguée (mg/dL)":      {"min": 0,    "max": 15},
            "Lab_Bilirubine non-conjuguée (mg/dL)":  {"min": 0,    "max": 15},
            "Lab_Phosphatase alcaline (U/L)":        {"min": 20,   "max": 500},
            "Lab_GGT (U/L)":                         {"min": 5,    "max": 500},
            "Lab_Albumine (g/dL)":                   {"min": 1,    "max": 6},
            "Lab_Protéine totale (g/dL)":            {"min": 3,    "max": 10},
            "Lab_Globulines (g/dL)":                 {"min": 1,    "max": 6},
            "Lab_Ratio A/G":                         {"min": 0.5,  "max": 3},
            "Lab_CK (U/L)":                          {"min": 10,   "max": 5000},
            "Lab_Myoglobine (ng/mL)":                {"min": 5,    "max": 1000},
            "Lab_Troponine (ng/mL)":                 {"min": 0,    "max": 10},
            "Lab_BNP (pg/mL)":                       {"min": 0,    "max": 5000},
            "Lab_ProBNP (pg/mL)":                    {"min": 0,    "max": 10000},
            "Lab_PT/INR":                            {"min": 0.5,  "max": 5},
            "Lab_aPTT (sec)":                        {"min": 20,   "max": 100},
            "Lab_TT (sec)":                          {"min": 10,   "max": 60},
            "Lab_Fibrinogène (mg/dL)":               {"min": 100,  "max": 800},
            "Lab_CRP (mg/L)":                        {"min": 0,    "max": 300},
            "Lab_ESR (mm/h)":                        {"min": 0,    "max": 120},
            "Lab_PSA (ng/mL)":                       {"min": 0,    "max": 50},
        }
        for feat, params in defaults.items():
            if feat not in self.normalization_params:
                self.normalization_params[feat] = params

    def _normalize_value(self, feature_name: str, raw_value: float) -> float:
        """Normalise une valeur entre 0 et 1 selon les paramètres du dataset"""
        if feature_name in self.normalization_params:
            p = self.normalization_params[feature_name]
            min_v, max_v = p["min"], p["max"]
            if max_v > min_v:
                return float(max(0.0, min(1.0, (raw_value - min_v) / (max_v - min_v))))
        return float(raw_value)

    def _get_default_lab_value(self, feature_name: str) -> float:
        """
        Valeur par défaut pour un examen de labo absent.
        dataset_means stocke déjà des valeurs normalisées (0-1) pour les Lab_.
        """
        if feature_name in self.dataset_means:
            return float(self.dataset_means[feature_name])
        return 0.5

    # ------------------------------------------------------------------
    # Normalisation des synonymes de symptômes
    # ------------------------------------------------------------------

    @staticmethod
    def _charger_synonymes_custom() -> dict:
        """Charge les synonymes générés dynamiquement par l'interface admin."""
        candidates = [
            "./ml_models/custom_synonymes.json",
            "../ml_models/custom_synonymes.json",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "..", "ml_models", "custom_synonymes.json"),
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
        return {}

    @staticmethod
    def _normaliser_symptomes(symptomes: List[str]) -> List[str]:
        """
        Remplace chaque synonyme par son terme canonique du dataset.
        Fusionne le dictionnaire statique + les synonymes custom ajoutés via l'admin.
        Le dictionnaire statique a la priorité en cas de conflit.
        """
        custom = ModelManager._charger_synonymes_custom()
        merged = {**custom, **SYNONYMES_SYMPTOMES}
        normalises = []
        for s in symptomes:
            s_clean = s.strip()
            canonique = merged.get(s_clean.lower())
            normalises.append(canonique if canonique else s_clean)
        return normalises

    # ------------------------------------------------------------------
    # Construction du vecteur de features
    # ------------------------------------------------------------------

    def _build_feature_vector(self, consultation_data: Dict) -> Dict:
        """
        Construit le vecteur complet des 400 features attendues par le modèle
        à partir des données brutes de consultation.

        Format attendu de consultation_data:
        {
            "age": int,
            "duree_symptomes_jours": int,
            "sexe": "M" | "F",
            "severite": "LEGER" | "MODERE" | "SEVERE",
            "vitaux": {
                "tension_systolique": float,       # mmHg
                "tension_diastolique": float,      # mmHg
                "frequence_cardiaque": float,      # bpm
                "frequence_respiratoire": float,   # /min
                "temperature": float,              # °C
                "saturation_oxygene": float,       # %
                "imc": float,                      # kg/m²
            },
            "symptomes": [list of str],  # noms des symptômes en français
            "examens": [
                {"nom": str, "valeur_numerique": float, "unite_mesure": str}
            ]
        }
        """
        features: Dict[str, float] = {}

        # --- Données démographiques ---
        age = float(consultation_data.get("age") or 40)
        features["Age"] = age
        features["Duree_Symptomes_Jours"] = float(consultation_data.get("duree_symptomes_jours") or 7)

        # --- Signes vitaux (normalisation 0-1) ---
        vitaux = consultation_data.get("vitaux") or {}

        # Calculer l'IMC si poids+taille fournis mais pas l'IMC directement
        imc = vitaux.get("imc")
        if imc is None:
            poids = vitaux.get("poids")
            taille = vitaux.get("taille")
            if poids and taille and taille > 0:
                imc = poids / ((taille / 100) ** 2)
            else:
                imc = 22.0

        vital_map = {
            "Vital_Tension Systolique (mmHg)":         vitaux.get("tension_systolique",     120),
            "Vital_Tension Diastolique (mmHg)":        vitaux.get("tension_diastolique",    80),
            "Vital_Fréquence Cardiaque (bpm)":         vitaux.get("frequence_cardiaque",    75),
            "Vital_Fréquence Respiratoire (resp/min)": vitaux.get("frequence_respiratoire", 16),
            "Vital_Température (°C)":                  vitaux.get("temperature",            37.0),
            "Vital_Saturation O2 (%)":                 vitaux.get("saturation_oxygene",     98.0),
            "Vital_IMC (kg/m²)":                       imc,
        }
        for feat, raw in vital_map.items():
            features[feat] = self._normalize_value(feat, float(raw or 0))

        # --- Analyses de laboratoire (normalisation 0-1, défaut = moyenne dataset) ---
        exam_lookup: Dict[str, float] = {}
        for exam in consultation_data.get("examens") or []:
            nom = (exam.get("nom") or "").strip()
            unite = (exam.get("unite_mesure") or "").strip()
            valeur = exam.get("valeur_numerique")
            if valeur is None or nom == "":
                continue
            
            matched = False
            # Essayer les formats de nommage du dataset
            for candidate in [
                f"Lab_{nom} ({unite})" if unite else None,
                f"Lab_{nom}",
            ]:
                if candidate and candidate in self.trainer.feature_names:
                    exam_lookup[candidate] = float(valeur)
                    matched = True
                    break
            
            # Log warning if exam was not matched to any model feature
            if not matched:
                logger.warning(
                    f"⚠️ Examen '{nom}' (unité: '{unite}') ne correspond à aucune feature du modèle et sera ignoré. "
                    f"Features lab disponibles: {[f for f in self.trainer.feature_names if f.startswith('Lab_')][:10]}..."
                )

        for feat in self.trainer.feature_names:
            if feat.startswith("Lab_"):
                if feat in exam_lookup:
                    features[feat] = self._normalize_value(feat, exam_lookup[feat])
                else:
                    features[feat] = self._get_default_lab_value(feat)

        # --- Symptômes (one-hot) ---
        symptome_names_raw: List[str] = consultation_data.get("symptomes") or []
        # Normaliser les synonymes avant tout traitement
        symptome_names: List[str] = self._normaliser_symptomes(symptome_names_raw)

        # Construire l'ensemble des feature-names de symptômes du patient
        # Inclut aussi la version mojibake pour compatibilité avec anciens modèles
        def _to_feat(nom: str) -> str:
            return "symptom_" + nom.strip().replace(" ", "_").replace("/", "_")

        def _to_mojibake_feat(nom: str) -> str:
            try:
                return "symptom_" + nom.strip().encode("utf-8").decode("latin-1").replace(" ", "_").replace("/", "_")
            except Exception:
                return ""

        patient_symptom_feats = set()
        for nom in symptome_names:
            if nom:
                patient_symptom_feats.add(_to_feat(nom))
                patient_symptom_feats.add(_to_mojibake_feat(nom))

        features["nombre_symptomes"] = float(len(symptome_names))

        for feat in self.trainer.feature_names:
            if feat.startswith("symptom_"):
                features[feat] = 1.0 if feat in patient_symptom_feats else 0.0

        # --- Features dérivées (valeurs brutes, sans normalisation) ---
        if age <= 12:
            features["categorie_age"] = 0.0
        elif age <= 18:
            features["categorie_age"] = 1.0
        elif age <= 60:
            features["categorie_age"] = 2.0
        else:
            features["categorie_age"] = 3.0

        fc_raw  = float(vitaux.get("frequence_cardiaque",  75)  or 75)
        o2_raw  = float(vitaux.get("saturation_oxygene",  98.0) or 98.0)
        temp_raw = float(vitaux.get("temperature",         37.0) or 37.0)

        features["ratio_fc_o2"] = fc_raw / (o2_raw + 1.0)
        features["score_risque"] = (
            (2.0 if temp_raw > 38.5 else 0.0)
            + (3.0 if o2_raw < 95.0 else 0.0)
            + float(len(symptome_names))
        )

        sexe = consultation_data.get("sexe") or "M"
        features["Sexe_encoded"] = 1.0 if sexe.upper() in ("M", "H") else 0.0

        sev_map = {
            "LEGER": 1.0, "Légère": 1.0, "légère": 1.0, "léger": 1.0,
            "MODERE": 2.0, "Modérée": 2.0, "modérée": 2.0, "modéré": 2.0,
            "SEVERE": 3.0, "Sévère": 3.0, "sévère": 3.0,
            "Critique": 4.0, "critique": 4.0, "CRITIQUE": 4.0,
        }
        severite = consultation_data.get("severite") or "MODERE"
        features["Severite_encoded"] = sev_map.get(severite, 2.0)

        return features

    # ------------------------------------------------------------------
    # Entraînement
    # ------------------------------------------------------------------

    def train_new_model(
        self,
        dataset_path: str,
        n_estimators: int = 100,
        max_depth: int = 20,
        save: bool = True,
    ) -> Dict:
        """Entraîne un nouveau modèle sur le dataset"""
        try:
            logger.info("🚀 Début entraînement nouveau modèle...")
            logger.info(f"   Dataset: {dataset_path}")

            # 1. Charger
            df = self.preprocessor.load_dataset(dataset_path)

            # 2. Nettoyage
            df, cleaning_log = self.preprocessor.clean_data(df)

            # 3. Feature engineering
            df = self.preprocessor.create_features(df)

            # 4. Normalisation des colonnes Vital_ et Lab_
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if "Maladie_Diagnostic" in numeric_cols:
                numeric_cols.remove("Maladie_Diagnostic")

            cols_to_normalize = [
                c for c in numeric_cols
                if c.startswith("Vital_") or c.startswith("Lab_")
            ]
            if cols_to_normalize:
                df, _ = self.preprocessor.normalize_data(df, cols_to_normalize)

            # Capturer les paramètres de normalisation (contiennent les min/max RAW)
            self.normalization_params = self.preprocessor.normalization_params.copy()
            # Après normalize_data(), les colonnes Vital_ et Lab_ sont déjà en 0-1
            # → leurs moyennes dans df sont déjà normalisées, on les stocke telles quelles
            for col in df.columns:
                if col != "Maladie_Diagnostic" and pd.api.types.is_numeric_dtype(df[col]):
                    self.dataset_means[col] = float(df[col].mean())

            # Transmettre au trainer pour la sauvegarde
            self.trainer.normalization_params = self.normalization_params
            self.trainer.dataset_means = self.dataset_means

            # 5. Garder seulement target + colonnes numériques
            cols_to_keep = ["Maladie_Diagnostic"] + [
                c for c in df.select_dtypes(include=[np.number]).columns
                if c != "Maladie_Diagnostic" and c != "ID"
            ]
            df = df[[c for c in cols_to_keep if c in df.columns]]

            # 6. Préparer X et y
            X, y = self.preprocessor.prepare_xy(df, target_column="Maladie_Diagnostic")

            # 7. Entraîner
            training_results = self.trainer.train(
                X, y, n_estimators=n_estimators, max_depth=max_depth
            )

            # 8. Évaluer
            from sklearn.model_selection import train_test_split

            y_encoded = self.trainer.label_encoder.transform(y)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y_encoded
            )
            evaluation_results = self.trainer.evaluate(X_test, y_test)

            # 9. Sauvegarder
            if save:
                model_path = self.trainer.save_model(version="1.0")
                training_results["model_path"] = model_path

            # 10. Activer le predictor
            self.predictor = Predictor(
                model=self.trainer.model,
                label_encoder=self.trainer.label_encoder,
                feature_names=self.trainer.feature_names,
            )
            self.model_loaded = True
            self.model_metadata = training_results

            logger.info("✅ Entraînement terminé avec succès!")
            return {"training": training_results, "evaluation": evaluation_results, "success": True}

        except Exception as e:
            logger.error(f"❌ Erreur entraînement: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Prédiction
    # ------------------------------------------------------------------

    def _apply_clinical_rules(self, proba: np.ndarray, consultation_data: Dict) -> np.ndarray:
        """
        Post-traitement clinique : booste les probabilités de certains diagnostics
        quand les signes vitaux dépassent des seuils reconnus.
        Préserve la somme = 1 (renormalisation après boost).
        """
        if self.predictor is None:
            return proba

        classes = list(self.predictor.label_encoder.classes_)
        proba = proba.copy()

        vitaux = consultation_data.get("vitaux") or {}
        sys_bp = vitaux.get("tension_systolique", 0) or 0
        dia_bp = vitaux.get("tension_diastolique", 0) or 0
        temp   = vitaux.get("temperature", 37.0) or 37.0
        spo2   = vitaux.get("saturation_oxygene", 98.0) or 98.0
        fc     = vitaux.get("frequence_cardiaque", 75) or 75
        fr     = vitaux.get("frequence_respiratoire", 16) or 16
        imc_val = vitaux.get("imc") or 0
        if not imc_val:
            poids = vitaux.get("poids") or 0
            taille = vitaux.get("taille") or 0
            imc_val = (poids / ((taille / 100) ** 2)) if (poids and taille > 0) else 22.0

        # Normaliser les synonymes AVANT d'appliquer les règles cliniques
        _symptomes_raw = consultation_data.get("symptomes") or []
        _symptomes_norm = self._normaliser_symptomes(_symptomes_raw)
        symptomes = set(s.strip().lower() for s in _symptomes_norm if s)

        def boost(diag: str, factor: float):
            if diag in classes:
                idx = classes.index(diag)
                proba[idx] *= factor

        # ================================================================
        # REGLES VITAUX
        # ================================================================

        # --- Cardiovasculaire ---
        if sys_bp >= 160 or dia_bp >= 100:
            boost("Hypertension", 6.0)
            boost("Insuffisance cardiaque", 1.5)
            boost("Infarctus du myocarde", 1.5)
            boost("Accident vasculaire cérébral", 1.5)
        elif sys_bp >= 140 or dia_bp >= 90:
            boost("Hypertension", 3.5)
            boost("Accident vasculaire cérébral", 1.2)
        if sys_bp < 90 or dia_bp < 60:
            boost("Hypotension", 3.5)
            boost("Infarctus du myocarde", 1.5)
            boost("Embolie pulmonaire", 1.5)
        if fc > 140:
            boost("Arythmie cardiaque", 4.0)
            boost("Embolie pulmonaire", 2.0)
        elif fc > 100:
            boost("Arythmie cardiaque", 2.0)
            boost("Hyperthyroïdie", 1.5)
            boost("Embolie pulmonaire", 1.3)
        if fc < 50:
            boost("Arythmie cardiaque", 2.5)
            boost("Hypothyroïdie", 1.5)

        # --- Respiratoire ---
        if spo2 < 88:
            boost("Embolie pulmonaire", 4.0)
            boost("Pneumonie", 3.0)
            boost("BPCO", 2.5)
        elif spo2 < 92:
            boost("Embolie pulmonaire", 3.0)
            boost("Pneumonie", 2.5)
            boost("BPCO", 2.0)
            boost("COVID-19", 2.0)
            boost("Asthme", 1.8)
        elif spo2 < 95:
            boost("Pneumonie", 1.8)
            boost("BPCO", 1.8)
            boost("COVID-19", 1.5)
            boost("Asthme", 1.5)
        if fr >= 30:
            boost("Embolie pulmonaire", 3.5)
            boost("Pneumonie", 2.5)
        elif fr > 25:
            boost("Pneumonie", 2.0)
            boost("Embolie pulmonaire", 2.0)
            boost("Asthme", 1.5)
            boost("COVID-19", 1.5)

        # --- Fièvre / Infectieux ---
        if temp >= 40.0:
            boost("Malaria", 3.0)
            boost("Typhoïde", 2.5)
            boost("Dengue", 2.0)
            boost("Pneumonie", 1.8)
        elif temp >= 39.5:
            boost("Malaria", 2.5)
            boost("Typhoïde", 2.0)
            boost("Dengue", 1.8)
            boost("Pneumonie", 1.8)
            boost("Grippe", 1.8)
            boost("COVID-19", 1.6)
        elif temp >= 38.5:
            boost("Grippe", 1.8)
            boost("COVID-19", 1.6)
            boost("Pneumonie", 1.6)
            boost("Malaria", 1.5)
            boost("Dengue", 1.5)
            boost("Tuberculose", 1.3)
        elif temp < 36.0:
            boost("Hypothyroïdie", 2.0)
            boost("Insuffisance cardiaque", 1.5)

        # --- Métabolique ---
        if imc_val >= 35:
            boost("Diabète Type 2", 2.0)
            boost("Apnée du sommeil", 2.5)
            boost("Hypertension", 1.5)
            boost("Stéatose hépatique", 2.0)
        elif imc_val >= 30:
            boost("Diabète Type 2", 1.5)
            boost("Apnée du sommeil", 2.0)
            boost("Hypertension", 1.3)

        # ================================================================
        # REGLES SYMPTOMES — très spécifiques (priorité haute)
        # ================================================================

        # COVID-19 : anosmie/agueusie = pathognomonique
        if "perte de goût" in symptomes or "perte d'odorat" in symptomes:
            boost("COVID-19", 8.0)

        # Infarctus du myocarde
        if "douleur thoracique sévère" in symptomes or "douleur thoracique" in symptomes:
            if fc > 100 or spo2 < 95:
                boost("Infarctus du myocarde", 4.0)
                boost("Angine de poitrine", 2.0)
            else:
                boost("Angine de poitrine", 3.0)
                boost("Infarctus du myocarde", 1.5)
        if "douleur au bras épaule" in symptomes or "douleur au bras" in symptomes:
            boost("Infarctus du myocarde", 2.5)
            boost("Angine de poitrine", 2.0)
        if "sueurs froides" in symptomes:
            boost("Infarctus du myocarde", 2.0)

        # AVC
        if "paralysie" in symptomes or "faiblesse soudaine" in symptomes:
            boost("Accident vasculaire cérébral", 5.0)
        if "difficulté à parler" in symptomes or "dysphagie" in symptomes:
            boost("Accident vasculaire cérébral", 3.0)
        if ("paralysie" in symptomes or "faiblesse soudaine" in symptomes) and (sys_bp >= 160 or dia_bp >= 100):
            boost("Accident vasculaire cérébral", 2.5)  # cumul

        # Tuberculose
        if "hémoptysie" in symptomes:
            boost("Tuberculose", 5.0)
        if "sueurs nocturnes" in symptomes and "perte de poids" in symptomes and "toux persistante" in symptomes:
            boost("Tuberculose", 4.0)
        elif "sueurs nocturnes" in symptomes and "toux persistante" in symptomes:
            boost("Tuberculose", 2.5)

        # Dengue
        if "douleur oculaire" in symptomes:
            boost("Dengue", 5.0)
        if "douleurs articulaires" in symptomes and "rash" in symptomes and temp >= 38.5:
            boost("Dengue", 3.5)

        # Sclérose en plaques
        if "engourdissement" in symptomes or "spasticité" in symptomes:
            boost("Sclérose en plaques", 4.0)
        if "vision floue" in symptomes and "faiblesse" in symptomes and "fatigue" in symptomes:
            boost("Sclérose en plaques", 3.0)
        if "difficulté à marcher" in symptomes and "engourdissement" in symptomes:
            boost("Sclérose en plaques", 2.5)

        # Diabète — glycémie très élevée ou symptômes typiques
        if "soif excessive" in symptomes or "fréquence urinaire" in symptomes:
            boost("Diabète Type 1", 2.5)
            boost("Diabète Type 2", 2.5)

        # Hépatique / ictère
        if "ictère" in symptomes or "jaunisse" in symptomes:
            boost("Hépatite A", 2.5)
            boost("Hépatite B", 2.5)
            boost("Cirrhose", 2.0)
        if "urine foncée" in symptomes and "selles pâles" in symptomes:
            boost("Hépatite B", 2.5)
            boost("Hépatite A", 2.0)
            boost("Cirrhose", 1.8)

        # Embolie pulmonaire
        if "essoufflement soudain" in symptomes and spo2 < 92:
            boost("Embolie pulmonaire", 3.0)
        if "syncope" in symptomes and (spo2 < 92 or fr >= 25):
            boost("Embolie pulmonaire", 2.5)

        # Anémie ferriprive : microcytose + symptômes
        if "pâleur" in symptomes and "cheveux cassants" in symptomes:
            boost("Anémie ferriprive", 3.0)
        if "pâleur" in symptomes and "vertiges" in symptomes and "palpitations" in symptomes:
            boost("Anémie ferriprive", 2.0)

        # Thrombose veineuse
        if "thrombose" in symptomes or "claudication" in symptomes:
            boost("Thrombose veineuse", 4.0)
        if "gonflement d'un membre" in symptomes and "chaleur" in symptomes and "rougeur cutanée" in symptomes:
            boost("Thrombose veineuse", 3.0)

        # Glaucome
        if "vision tunnel" in symptomes or "halos colorés" in symptomes:
            boost("Glaucome", 5.0)
        if "perte de vision progressive" in symptomes and "douleur oculaire" in symptomes:
            boost("Glaucome", 3.5)

        # Eczéma vs Conjonctivite
        if "vésicules" in symptomes or "crevasses" in symptomes or "sécheresse cutanée" in symptomes:
            boost("Eczéma", 4.0)
        if "éruption prurigineuse" in symptomes and "démangeaisons" in symptomes:
            boost("Eczéma", 2.5)
            boost("Urticaire", 1.5)

        # Urticaire
        if "angioedème" in symptomes or "gonflement des lèvres" in symptomes:
            boost("Urticaire", 5.0)
        if "histaminémie" in symptomes:
            boost("Urticaire", 4.0)

        # Cushing
        if "vergetures" in symptomes or "grossissement du visage" in symptomes:
            boost("Syndrome de Cushing", 6.0)
        if "prise de poids rapide" in symptomes and "hypertension" in symptomes:
            boost("Syndrome de Cushing", 3.0)

        # Lithiase rénale
        if "douleur colique intense" in symptomes and "hématurie" in symptomes:
            boost("Lithiase rénale", 5.0)

        # Cystite / Pyélonéphrite
        if "dysurie" in symptomes and "urgence urinaire" in symptomes:
            boost("Cystite", 4.0)
            boost("Pyélonéphrite", 2.0)

        # ----------------------------------------------------------------
        # INSUFFISANCE RÉNALE (aiguë & chronique)
        # ----------------------------------------------------------------
        symptomes_renaux = {
            "oligurie ou polyurie", "anurie", "hématurie", "urine foncée",
            "urine mousseuse", "nycturie", "oedèmes", "gonflement des chevilles",
            "démangeaisons", "prurit", "haleine urémique", "goût métallique",
            "crampes musculaires", "engourdissements", "peau sèche", "teint grisâtre",
            "prise de poids rapide",
        }
        nb_renaux = len(symptomes & symptomes_renaux)

        # Oligurie/anurie = signe cardinal de l'insuffisance rénale aiguë
        if "anurie" in symptomes:
            boost("Insuffisance rénale aiguë", 8.0)
            boost("Insuffisance rénale chronique", 3.0)
        elif "oligurie ou polyurie" in symptomes:
            boost("Insuffisance rénale aiguë", 5.0)
            boost("Insuffisance rénale chronique", 2.0)

        # Urine mousseuse = protéinurie → IRC très probable
        if "urine mousseuse" in symptomes:
            boost("Insuffisance rénale chronique", 4.0)
            boost("Syndrome néphrotique", 3.0)
            boost("Insuffisance rénale aiguë", 2.0)

        # Haleine urémique ou goût métallique = urémie → insuffisance rénale avancée
        if "haleine urémique" in symptomes or "goût métallique" in symptomes:
            boost("Insuffisance rénale aiguë", 5.0)
            boost("Insuffisance rénale chronique", 5.0)

        # Nycturie = symptôme classique IRC
        if "nycturie" in symptomes:
            boost("Insuffisance rénale chronique", 3.5)
            boost("Insuffisance rénale aiguë", 1.5)

        # Démangeaisons/prurit sans cause cutanée évidente = IRC
        if ("démangeaisons" in symptomes or "prurit" in symptomes) and nb_renaux >= 2:
            boost("Insuffisance rénale chronique", 3.0)

        # Teint grisâtre = anémie rénale (IRC)
        if "teint grisâtre" in symptomes:
            boost("Insuffisance rénale chronique", 3.0)

        # Cumul de signes rénaux : plus il y en a, plus c'est probable
        if nb_renaux >= 4:
            boost("Insuffisance rénale aiguë", 3.5)
            boost("Insuffisance rénale chronique", 3.5)
        elif nb_renaux >= 3:
            boost("Insuffisance rénale aiguë", 2.0)
            boost("Insuffisance rénale chronique", 2.0)
        elif nb_renaux >= 2:
            boost("Insuffisance rénale aiguë", 1.5)
            boost("Insuffisance rénale chronique", 1.5)

        # Hypertension + oedèmes + fatigue = triade rénale
        if ("hypertension" in symptomes and
                ("oedèmes" in symptomes or "gonflement des chevilles" in symptomes) and
                "fatigue" in symptomes):
            boost("Insuffisance rénale chronique", 2.5)
            boost("Insuffisance rénale aiguë", 2.0)

        # Hématurie + douleurs abdominales sans colique → rénale possible
        if "hématurie" in symptomes and "douleurs abdominales" in symptomes:
            if "douleur colique intense" not in symptomes:
                boost("Insuffisance rénale aiguë", 2.0)
                boost("Glomérulonéphrite", 2.5)

        # Convulsions + confusion + urémie = encéphalopathie urémique (IRA sévère)
        if "convulsions" in symptomes and "confusion" in symptomes and nb_renaux >= 2:
            boost("Insuffisance rénale aiguë", 4.0)

        # Données biologiques rénales critiques (si disponibles)
        examens = {
            (e.get("nom") or "").lower(): e.get("valeur_numerique")
            for e in (consultation_data.get("examens") or [])
            if e.get("valeur_numerique") is not None
        }
        creatinine = examens.get("créatinine") or examens.get("creatinine")
        tfg = examens.get("tfg") or examens.get("débit de filtration glomérulaire")
        uree = examens.get("urée") or examens.get("uree")
        potassium = examens.get("potassium")

        if creatinine is not None:
            if creatinine > 5.0:
                boost("Insuffisance rénale aiguë", 6.0)
                boost("Insuffisance rénale chronique", 4.0)
            elif creatinine > 2.0:
                boost("Insuffisance rénale aiguë", 3.0)
                boost("Insuffisance rénale chronique", 3.0)
            elif creatinine > 1.3:
                boost("Insuffisance rénale aiguë", 1.8)
                boost("Insuffisance rénale chronique", 1.8)

        if tfg is not None:
            if tfg < 15:
                boost("Insuffisance rénale chronique", 7.0)
                boost("Insuffisance rénale aiguë", 4.0)
            elif tfg < 30:
                boost("Insuffisance rénale chronique", 4.0)
                boost("Insuffisance rénale aiguë", 2.5)
            elif tfg < 60:
                boost("Insuffisance rénale chronique", 2.5)
                boost("Insuffisance rénale aiguë", 1.5)

        if uree is not None and uree > 100:
            boost("Insuffisance rénale aiguë", 3.0)
            boost("Insuffisance rénale chronique", 2.5)

        if potassium is not None and potassium > 5.5:
            boost("Insuffisance rénale aiguë", 2.5)
            boost("Insuffisance rénale chronique", 2.0)

        # Goutte
        if "tophi" in symptomes:
            boost("Goutte", 6.0)
        if "douleur articulaire soudaine" in symptomes and "chaleur" in symptomes and "rougeur" in symptomes:
            boost("Goutte", 3.5)

        # Lupus
        if "éruption malaire" in symptomes or "rash photosensible" in symptomes:
            boost("Lupus érythémateux systémique", 6.0)
        if "photosensibilité" in symptomes and "ulcères buccaux" in symptomes:
            boost("Lupus érythémateux systémique", 3.5)

        # Psoriasis
        if "plaques rouges squameuses" in symptomes or "desquamation" in symptomes:
            boost("Psoriasis", 5.0)
        if "saignement des plaques" in symptomes:
            boost("Psoriasis", 3.0)

        # Epilepsie
        if "convulsions" in symptomes:
            boost("Épilepsie", 6.0)

        # Parkinson
        if "lenteur de mouvement" in symptomes or "rigidité" in symptomes:
            boost("Parkinson", 4.0)
        if "tremblements" in symptomes and "rigidité" in symptomes:
            boost("Parkinson", 3.0)

        # Migraine
        if "photophobie" in symptomes and "phonophobie" in symptomes:
            boost("Migraine", 4.0)
        if "aura" in symptomes:
            boost("Migraine", 3.5)

        # Cirrhose
        if "ascite" in symptomes:
            boost("Cirrhose", 5.0)
        if "varices œsophagiennes" in symptomes or "hépatomégalie" in symptomes:
            boost("Cirrhose", 3.0)

        # Leucémie
        if "bleus faciles" in symptomes and "ganglions enflés" in symptomes and "douleurs osseuses" in symptomes:
            boost("Leucémie", 5.0)
        if "bleus faciles" in symptomes and "saignements" in symptomes:
            boost("Leucémie", 2.5)
            boost("Trouble de coagulation", 2.0)

        # RGO
        if "reflux gastro-esophagien" in symptomes or "régurgitation" in symptomes:
            boost("RGO", 5.0)
        if "difficulté à avaler" in symptomes and "brûlures d'estomac" in symptomes:
            boost("RGO", 2.5)
            boost("Hernie hiatale", 2.0)

        # ================================================================
        # REGLES SUPPLEMENTAIRES — maladies restantes
        # ================================================================

        # --- Infectieuses ---
        if "hémoptysie" not in symptomes:  # déjà géré plus haut
            pass
        if "taches de koplik" in symptomes:
            boost("Rougeole", 8.0)
        if "éruption vésiculaire" in symptomes or "vésicules" in symptomes:
            boost("Varicelle", 5.0)
            boost("Herpès génital", 3.0)
        if "rash rose" in symptomes and temp >= 38.5:
            boost("Typhoïde", 4.0)
        if "chancre" in symptomes:
            boost("Syphilis", 8.0)
        if ("rash" in symptomes or "lymphadénopathie" in symptomes) and "chancre" in symptomes:
            boost("Syphilis", 4.0)
        if "douleur oculaire" in symptomes and "douleurs articulaires" in symptomes:
            boost("Dengue", 3.0)
        if "fièvre intermittente" in symptomes:
            boost("Malaria", 4.0)
        if "toux aboyante" in symptomes or "stridor inspiratoire" in symptomes:
            boost("Trachéite", 6.0)
        if "perte de voix" in symptomes or "enrouement" in symptomes:
            boost("Laryngite", 5.0)
        if "otalgie" in symptomes or "écoulement auriculaire" in symptomes:
            boost("Otite", 6.0)
        if "douleur faciale" in symptomes and "congestion nasale" in symptomes:
            boost("Sinusite", 5.0)
        if "éternuements" in symptomes and "congestion nasale" in symptomes:
            boost("Rhinite allergique", 4.0)
            boost("Sinusite", 1.5)
        if "candidose buccale" in symptomes or "infections récurrentes" in symptomes:
            boost("VIH/SIDA", 4.0)
        if "ganglions enflés" in symptomes and "mal de gorge" in symptomes and temp >= 38.0:
            boost("Mononucléose", 4.0)
        if "démangeaisons" in symptomes and "éruption vésiculaire" in symptomes:
            boost("Varicelle", 3.0)
        if "crampes abdominales" in symptomes and "diarrhée" in symptomes and temp >= 38.0:
            boost("Salmonellose", 3.5)
            boost("Gastroentérite", 2.5)
        if "rougeur pharyngée" in symptomes or "taches blanches pharyngées" in symptomes:
            boost("Angine streptococcique", 5.0)
        if "écoulement urétral" in symptomes:
            boost("Gonorrhée", 5.0)
            boost("Chlamydia", 4.0)
            boost("Urétrite", 4.0)
        if "souvent asymptomatique" in symptomes or "cervicite" in symptomes:
            boost("Chlamydia", 3.0)
        if "verrues génitales" in symptomes:
            boost("Condylomes", 8.0)
        if "petites bosses ombiliquées" in symptomes:
            boost("Molluscum contagiosum", 8.0)
        if "excroissance cutanée" in symptomes or "verrue plantaire douloureuse" in symptomes:
            boost("Verrue", 6.0)
        if "récidives" in symptomes and ("vésicules" in symptomes or "brûlures génitales" in symptomes):
            boost("Herpès génital", 5.0)

        # --- Cardiovasculaires ---
        if "douleur au bras/épaule" in symptomes or "douleur à la mâchoire" in symptomes:
            boost("Angine de poitrine", 4.0)
            boost("Infarctus du myocarde", 2.0)
        if "frottement péricardique" in symptomes or "douleur calmée penché en avant" in symptomes:
            boost("Péricardite", 7.0)
        if "douleur thoracique pleurétique" in symptomes:
            boost("Péricardite", 4.0)
            boost("Embolie pulmonaire", 2.0)
        if "sensation d'accélération" in symptomes or "pouls irrégulier" in symptomes:
            boost("Arythmie cardiaque", 4.0)
        if "claudication" not in symptomes:
            pass
        if "érythromélalgie" in symptomes or "paresthésies" in symptomes:
            boost("Thrombocytémie", 4.0)
        if "thrombose" in symptomes and "rougeur cutanée" in symptomes:
            boost("Thrombocytémie", 3.0)
        if "visage rouge" in symptomes and "prurit" in symptomes and "vertiges" in symptomes:
            boost("Polyglobulie", 5.0)

        # --- Respiratoires ---
        if "barrel chest" in symptomes or "utilisation muscles accessoires" in symptomes:
            boost("Emphysème", 5.0)
            boost("BPCO", 3.0)
        if "ronflement" in symptomes and "somnolence diurne" in symptomes:
            boost("Apnée du sommeil", 6.0)
        if "maux de tête matinaux" in symptomes and "ronflement" in symptomes:
            boost("Apnée du sommeil", 4.0)
        if "crachats purulents" in symptomes or "expectorations" in symptomes:
            boost("Pneumonie", 2.5)
            boost("Bronchite", 2.0)
            boost("BPCO", 1.5)

        # --- Gastro-intestinales ---
        if "brûlures épigastriques" in symptomes or "douleur à jeun" in symptomes:
            boost("Ulcère gastro-duodénal", 5.0)
        if "méléna" in symptomes or "hématémèse" in symptomes:
            boost("Ulcère gastro-duodénal", 4.0)
            boost("Cirrhose", 2.0)
        if "diarrhée sanguinolente" in symptomes:
            boost("Colite ulcéreuse", 6.0)
            boost("Crohn", 3.0)
        if "besoin impérieux de déféquer" in symptomes:
            boost("Colite ulcéreuse", 3.0)
        if "fistules" in symptomes:
            boost("Crohn", 6.0)
        if ("diarrhée" in symptomes and "constipation" in symptomes) or "alternance diarrhée-constipation" in symptomes:
            boost("Syndrome du côlon irritable", 5.0)
        if "mucus dans les selles" in symptomes:
            boost("Syndrome du côlon irritable", 4.0)
            boost("Colite ulcéreuse", 2.0)
        if "selles dures" in symptomes and "efforts pour défécation" in symptomes:
            boost("Constipation chronique", 5.0)
        if "ballonnements" in symptomes and "brûlures d'estomac" in symptomes:
            boost("Gastrite", 3.0)
            boost("RGO", 2.0)
        if "douleur irradiant dans le dos" in symptomes and "nausées" in symptomes:
            boost("Pancréatite", 5.0)
        if "douleur après repas gras" in symptomes or "douleur irradiant épaule droite" in symptomes:
            boost("Cholécystite", 5.0)
        if "ictère" in symptomes and "fièvre" in symptomes and "douleur abdominale" in symptomes:
            boost("Cholangite", 5.0)
        if "gynécomastie" in symptomes or "érythème palmaire" in symptomes:
            boost("Cirrhose", 4.0)
        if "hépatomégalie" in symptomes and "souvent asymptomatique" in symptomes:
            boost("Stéatose hépatique", 4.0)

        # --- Endocriniennes ---
        if "agrandissement des mains/pieds" in symptomes or "grossissement du visage" in symptomes:
            boost("Acromégalie", 8.0)
        if "hyperpigmentation" in symptomes and "hypotension" in symptomes:
            boost("Maladie d'Addison", 7.0)
        if ("sal craving" in symptomes or "sel craving" in symptomes) and "hypotension" in symptomes:
            boost("Maladie d'Addison", 4.0)
        if "intolérance à la chaleur" in symptomes and "yeux saillants" in symptomes:
            boost("Hyperthyroïdie", 5.0)
        if "myxoedème" in symptomes or "voix rauque" in symptomes:
            boost("Hypothyroïdie", 4.0)
        if "engourdissement des pieds" in symptomes and "ulcères des pieds" in symptomes:
            boost("Neuropathie diabétique", 6.0)
        if "douleur neuropathique" in symptomes and "perte de réflexes" in symptomes:
            boost("Neuropathie diabétique", 5.0)
        if "brûlures aux pieds" in symptomes or "fourmillements" in symptomes:
            boost("Neuropathie diabétique", 3.0)
            boost("Diabète Type 2", 1.5)
        if "flotteurs" in symptomes or "hémorragie rétinienne" in symptomes:
            boost("Rétinopathie diabétique", 6.0)
        if "scotome central" in symptomes or "métamorphopsies" in symptomes:
            boost("Dégénérescence maculaire", 5.0)
        if "dépôts lipidiques aux paupières" in symptomes or "xanthomes" in symptomes:
            boost("Hypercholestérolémie", 6.0)
        if "douleur thyroïdienne" in symptomes or "gonflement thyroïde" in symptomes:
            boost("Thyroïdite", 6.0)
        if "bosse de bison" in symptomes or "vergetures" in symptomes:
            boost("Syndrome de Cushing", 5.0)

        # --- Neurologiques ---
        if "perte de mémoire" in symptomes and "désorientation" in symptomes:
            boost("Alzheimer", 6.0)
        if "comportement inapproprié" in symptomes and "perte de mémoire" in symptomes:
            boost("Alzheimer", 4.0)
        if "lenteur de mouvement" in symptomes and "écriture micrographique" in symptomes:
            boost("Parkinson", 5.0)
        if "faiblesse ascendante" in symptomes or "réflexes abolis" in symptomes:
            boost("Syndrome de Guillain-Barré", 7.0)
        if "fasciculations" in symptomes or "atrophie musculaire" in symptomes:
            boost("Sclérose latérale amyotrophique", 6.0)
        if "douleur unilatérale" in symptomes and "pulsation céphalique" in symptomes:
            boost("Migraine", 4.0)
        if "sensation de pression" in symptomes and "douleur bilatérale" in symptomes:
            boost("Céphale de tension", 5.0)
            boost("Céphalée de tension", 5.0)
        if "névrite optique" in symptomes:
            boost("Sclérose en plaques", 6.0)
        if "douleurs musculaires diffuses" in symptomes and "fatigue" in symptomes:
            boost("Fibromyalgie", 4.0)
        if "hyperesthésie" in symptomes:
            boost("Fibromyalgie", 5.0)

        # --- Rhumatologiques ---
        if "raideur matinale" in symptomes and "douleur articulaire" in symptomes:
            boost("Arthrite rhumatoïde", 4.0)
            boost("Spondylarthrite ankylosante", 3.0)
        if "nodules rhumatoïdes" in symptomes:
            boost("Arthrite rhumatoïde", 5.0)
        if "uvéite" in symptomes and "douleur lombaire" in symptomes:
            boost("Spondylarthrite ankylosante", 5.0)
        if "enthésite" in symptomes:
            boost("Spondylarthrite ankylosante", 6.0)
        if "sécheresse oculaire" in symptomes and "sécheresse buccale" in symptomes:
            boost("Syndrome de Sjögren", 7.0)
        if "gonflement parotides" in symptomes:
            boost("Syndrome de Sjögren", 5.0)
        if "papules de gottron" in symptomes or "héliotrope éruption" in symptomes:
            boost("Polymyosite/Dermatomyosite", 8.0)
        if "faiblesse musculaire" in symptomes and "rash photosensible" in symptomes:
            boost("Polymyosite/Dermatomyosite", 4.0)
        if "raynaud" in symptomes and "durcissement cutané" in symptomes:
            boost("Sclérodermie", 7.0)
        if "télangiectasies" in symptomes and "fibrose pulmonaire" in symptomes:
            boost("Sclérodermie", 5.0)
        if "douleurs musculaires diffuses" in symptomes and "raideur matinale" in symptomes:
            boost("Fibromyalgie", 3.0)

        # --- Dermatologiques ---
        if "comédones" in symptomes or "pustules" in symptomes:
            boost("Acné", 6.0)
        if "prurit sévère" in symptomes and "sécheresse cutanée" in symptomes:
            boost("Dermatite atopique", 5.0)
            boost("Eczéma", 3.0)
        if "taches blanches" in symptomes or "dépigmentation" in symptomes:
            boost("Vitiligo", 7.0)
        if "bulles" in symptomes and "érosions" in symptomes:
            boost("Pemphigus", 7.0)
        if "ulcérations" in symptomes and "bulles" in symptomes:
            boost("Pemphigus", 5.0)
        if "squames argentées" in symptomes or "plaques rouges squameuses" in symptomes:
            boost("Psoriasis", 5.0)

        # --- Ophtalmologiques ---
        if "vision tunnel" in symptomes or "perte de vision périphérique" in symptomes:
            boost("Glaucome", 5.0)
        if "vision jaunâtre" in symptomes or "diplopie monoculaire" in symptomes:
            boost("Cataracte", 5.0)
        if "halos autour des lumières" in symptomes:
            boost("Cataracte", 3.0)
            boost("Glaucome", 2.0)
        if "ulcère cornéen" in symptomes or "blépharospasme" in symptomes:
            boost("Kératite", 6.0)
        if "sensation de corps étranger" in symptomes and "douleur oculaire" in symptomes:
            boost("Kératite", 3.0)
        if "lignes ondulées" in symptomes or "métamorphopsies" in symptomes:
            boost("Dégénérescence maculaire", 5.0)
        if "vision floue de loin" in symptomes and "plissement des yeux" in symptomes:
            boost("Myopie", 5.0)
        if "vision floue de près" in symptomes or "vision rapprochée floue" in symptomes:
            boost("Hypermétropie", 4.0)
            boost("Presbytie", 3.0)
        if "difficulté de lecture" in symptomes and "fatigue oculaire" in symptomes:
            boost("Presbytie", 4.0)
        if "vision floue à toutes distances" in symptomes:
            boost("Astigmatisme", 5.0)
        if "rougeur oculaire" in symptomes and "larmoiement" in symptomes:
            boost("Conjonctivite", 4.0)
            boost("Kératite", 2.0)
        if "démangeaisons oculaires" in symptomes:
            boost("Conjonctivite", 3.0)
            boost("Rhinite allergique", 2.0)

        # --- Hématologiques ---
        if "adénopathie" in symptomes and "sueurs nocturnes" in symptomes and "perte de poids" in symptomes:
            boost("Lymphome", 6.0)
        if "splénomégalie" in symptomes and "adénopathie" in symptomes:
            boost("Lymphome", 3.0)
            boost("Leucémie", 2.0)
        if "épistaxis" in symptomes and "saignement gencives" in symptomes:
            boost("Anémie aplasique", 4.0)
            boost("Trouble de coagulation", 3.0)
        if "pétéchies" in symptomes or "purpura" in symptomes:
            boost("Trouble de coagulation", 4.0)
            boost("Anémie aplasique", 3.0)
        if "urines foncées" in symptomes and "ictère" in symptomes and "splénomégalie" in symptomes:
            boost("Anémie hémolytique", 5.0)
        if "ménorragie" in symptomes or "hémarthrose" in symptomes:
            boost("Trouble de coagulation", 4.0)
        if "céphalées" in symptomes and "visage rouge" in symptomes:
            boost("Polyglobulie", 3.0)

        # --- Rénales/Urinaires ---
        if "protéinurie" in symptomes and "oedèmes" in symptomes:
            boost("Syndrome néphrotique", 5.0)
            boost("Glomérulonéphrite", 3.0)
        if "albuminémie basse" in symptomes or "hyperlipidémie" in symptomes:
            boost("Syndrome néphrotique", 5.0)
        if "hématurie" in symptomes and "hypertension" in symptomes and "oedèmes" in symptomes:
            boost("Glomérulonéphrite", 5.0)
        if "nocturia" in symptomes or "nycturie" in symptomes:
            boost("Hypertrophie bénigne de prostate", 3.0)
            boost("Prostatite", 2.0)
        if "difficultés à uriner" in symptomes and "flux faible" in symptomes:
            boost("Hypertrophie bénigne de prostate", 5.0)
        if "éjaculation douloureuse" in symptomes or "douleur périnéale" in symptomes:
            boost("Prostatite", 6.0)
        if "douleur costovertébrale" in symptomes:
            boost("Pyélonéphrite", 4.0)
            boost("Lithiase rénale", 2.0)

        # --- Myocardite / Péricardite (compléments) ---
        if "fièvre" in symptomes and "douleur thoracique" in symptomes and fc > 100:
            boost("Myocardite", 3.0)
            boost("Péricardite", 2.0)

        # Arthrite rhumatoïde vs Goutte vs Lupus (triade articulaire)
        if "rougeur" in symptomes and "chaleur" in symptomes and "gonflement" in symptomes:
            boost("Goutte", 2.0)
            boost("Arthrite rhumatoïde", 1.5)

        # ----------------------------------------------------------------
        # CORRECTIONS SPECIFIQUES — maladies sous-détectées
        # ----------------------------------------------------------------

        # Insuffisance cardiaque : triade essoufflement + oedèmes + gonflement chevilles
        if ("essoufflement" in symptomes or "dyspnée de décubitus" in symptomes or "orthopnée" in symptomes):
            boost("Insuffisance cardiaque", 2.0)
        if ("toux nocturne" in symptomes or "dyspnée de décubitus" in symptomes) and \
                ("oedèmes" in symptomes or "gonflement des chevilles" in symptomes):
            boost("Insuffisance cardiaque", 4.0)
        if "prise de poids rapide" in symptomes and \
                ("essoufflement" in symptomes or "gonflement des chevilles" in symptomes):
            boost("Insuffisance cardiaque", 3.0)
        if "oedèmes" in symptomes and "essoufflement" in symptomes and "fatigue" in symptomes:
            boost("Insuffisance cardiaque", 3.5)

        # Cholécystite : douleur abdominale haute + fièvre + repas gras
        if "douleur après repas gras" in symptomes:
            boost("Cholécystite", 6.0)
        if "douleur irradiant épaule droite" in symptomes:
            boost("Cholécystite", 5.0)
        if "douleur abdominale supérieure" in symptomes and temp >= 38.0:
            boost("Cholécystite", 4.0)
        if "ictère léger" in symptomes and "fièvre" in symptomes and "nausées" in symptomes:
            boost("Cholécystite", 3.5)

        # Maladie d'Addison : hyperpigmentation + hypotension + sel craving
        if "hyperpigmentation" in symptomes:
            boost("Maladie d'Addison", 8.0)
        if (sys_bp < 100 or dia_bp < 65) and "fatigue" in symptomes and "nausées" in symptomes:
            boost("Maladie d'Addison", 4.0)
        if "hyperpigmentation" in symptomes and (sys_bp < 110 or "hypotension" in symptomes):
            boost("Maladie d'Addison", 5.0)

        # ── Règles cliniques dynamiques (maladies ajoutées via interface admin) ──
        custom_rules = self._load_custom_rules()
        for maladie_nom, rule in custom_rules.items():
            if maladie_nom not in classes:
                continue
            idx = classes.index(maladie_nom)
            boost_factor  = float(rule.get("boost_factor", 3.0))
            min_match     = int(rule.get("min_symptomes_match", 1))
            symp_rule = [s.lower().strip() for s in rule.get("symptomes_boost", [])]
            nb_match = sum(1 for s in symp_rule if s in symptomes)
            if nb_match >= min_match:
                proba[idx] *= boost_factor
                logger.debug(f"Custom boost {maladie_nom} ×{boost_factor} ({nb_match} symptômes)")

        # Renormaliser
        total = proba.sum()
        if total > 0:
            proba = proba / total
        return proba

    def _load_custom_rules(self) -> Dict:
        """Charge les règles cliniques dynamiques sauvegardées par l'admin."""
        candidates = [
            "./ml_models/custom_disease_rules.json",
            "../ml_models/custom_disease_rules.json",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "..", "ml_models", "custom_disease_rules.json"),
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
        return {}

    def predict(self, consultation_data: Dict) -> Dict:
        """
        Fait une prédiction à partir des données structurées de consultation.

        consultation_data: voir _build_feature_vector() pour le format attendu.
        """
        if not self.model_loaded or self.predictor is None:
            raise ValueError("Modèle non chargé. Appelez load_latest_model() d'abord.")

        try:
            features = self._build_feature_vector(consultation_data)

            df = pd.DataFrame([features])

            # Compléter les features manquantes avec 0.0
            for feat in self.trainer.feature_names:
                if feat not in df.columns:
                    df[feat] = 0.0

            # Ordonner selon l'ordre d'entraînement
            df = df[self.trainer.feature_names]

            # Prédiction brute du modèle ML
            y_pred_proba = self.predictor.model.predict_proba(df)[0]

            # Post-traitement clinique
            y_pred_proba = self._apply_clinical_rules(y_pred_proba, consultation_data)

            # Reconstruire la réponse — cast en str Python natif (évite np.str_)
            classes = [str(c) for c in self.predictor.label_encoder.classes_]
            top_idx = int(np.argmax(y_pred_proba))
            top_3_indices = np.argsort(y_pred_proba)[-3:][::-1]

            alternatives = [
                {"diagnostic": classes[i], "confiance": float(y_pred_proba[i])}
                for i in top_3_indices
            ]

            main_confidence = float(y_pred_proba[top_idx])
            if main_confidence >= 0.80:
                confidence_level, confidence_color = "high", "green"
            elif main_confidence >= 0.60:
                confidence_level, confidence_color = "medium", "yellow"
            else:
                confidence_level, confidence_color = "low", "red"

            def _display(name: str) -> str:
                return DISEASE_DISPLAY_NAMES.get(name, name)

            return {
                "diagnostic_propose": _display(classes[top_idx]),
                "confiance": main_confidence,
                "niveau_confiance": confidence_level,
                "couleur_confiance": confidence_color,
                "diagnostics_alternatifs": [
                    {"diagnostic": _display(a["diagnostic"]), "confiance": a["confiance"]}
                    for a in alternatives[1:]
                ],
                "temps_prediction_secondes": 0.0,
                "timestamp": datetime.now().isoformat(),
                "explication": None,
                "features_importantes": None,
            }

        except Exception as e:
            logger.error(f"❌ Erreur prédiction: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def explain_prediction(self, consultation_data: Dict) -> Dict:
        """Explique une prédiction (top features)"""
        if not self.model_loaded or self.predictor is None:
            raise ValueError("Modèle non chargé.")

        try:
            features = self._build_feature_vector(consultation_data)
            df = pd.DataFrame([features])

            for feat in self.trainer.feature_names:
                if feat not in df.columns:
                    df[feat] = 0.0

            df = df[self.trainer.feature_names]
            result = self.predictor.explain_prediction(df)
            if "diagnostic" in result:
                result["diagnostic"] = DISEASE_DISPLAY_NAMES.get(result["diagnostic"], result["diagnostic"])
            return result

        except Exception as e:
            logger.error(f"❌ Erreur explication: {e}")
            raise

    def get_model_info(self) -> Dict:
        return {
            "loaded": self.model_loaded,
            "version": self.model_version,
            "metadata": self.model_metadata,
            "n_features": len(self.trainer.feature_names) if self.trainer.feature_names else 0,
            "n_classes": len(self.trainer.label_encoder.classes_) if self.trainer.label_encoder and hasattr(self.trainer.label_encoder, 'classes_') else 0,
            "classes": self.trainer.label_encoder.classes_.tolist() if self.trainer.label_encoder and hasattr(self.trainer.label_encoder, 'classes_') else [],
            "normalization_loaded": len(self.normalization_params) > 0,
        }

    def get_supported_lab_features(self) -> List[str]:
        """
        Retourne la liste de toutes les features de laboratoire supportées par le modèle.
        
        Returns:
            List[str]: Liste des noms de features commençant par "Lab_"
        """
        if not self.trainer.feature_names:
            return []
        return [f for f in self.trainer.feature_names if f.startswith("Lab_")]

    def retrain_with_new_data(self, new_data_path: str) -> Dict:
        """Réentraîne le modèle avec de nouvelles données"""
        logger.info("🔄 Réentraînement avec nouvelles données...")
        results = self.train_new_model(new_data_path, save=True)
        if results["success"]:
            logger.info("✅ Réentraînement réussi!")
        return results


# Instance globale (singleton)
model_manager = ModelManager()
