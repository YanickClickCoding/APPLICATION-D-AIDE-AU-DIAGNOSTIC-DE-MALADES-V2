"""
Script d'enrichissement du dictionnaire de synonymes SYNONYMES_SYMPTOMES.
Ajoute les termes courants (langage patient + médecin généraliste) pour
toutes les 122 maladies du dataset.

Usage : python enrichir_synonymes.py
"""
import re, sys, os
sys.stdout.reconfigure(encoding='utf-8')

# ══════════════════════════════════════════════════════════════════════════════
# DICTIONNAIRE ENRICHI — langage courant → terme canonique du dataset
# Organisation par catégorie médicale
# ══════════════════════════════════════════════════════════════════════════════

NOUVEAUX_SYNONYMES: dict[str, str] = {

    # ── GÉNÉRAUX / CONSTITUTIONNELS ──────────────────────────────────────────
    "corps chaud":                      "Fièvre",
    "chaud":                            "Fièvre",
    "température":                      "Fièvre",
    "avoir de la fièvre":               "Fièvre",
    "fébrilité":                        "Fièvre",
    "fièvre légère":                    "Fièvre",
    "subfébrile":                       "Fièvre",
    "chaleur corporelle":               "Fièvre",
    "corps qui brûle":                  "Fièvre",
    "hyperthermie":                     "Fièvre élevée",
    "très forte fièvre":                "Fièvre élevée",
    "fièvre forte":                     "Fièvre élevée",
    "fièvre à 40":                      "Fièvre élevée",
    "39 degrés":                        "Fièvre élevée",
    "40 degrés":                        "Fièvre élevée",

    "très fatigué":                     "Fatigue",
    "épuisé":                           "Fatigue",
    "sans énergie":                     "Fatigue",
    "pas d'énergie":                    "Fatigue",
    "se sent faible":                   "Fatigue",
    "affaibli":                         "Fatigue",
    "asthénie":                         "Fatigue",
    "manque d'énergie":                 "Fatigue",
    "épuisement":                       "Fatigue",
    "lassitude":                        "Fatigue",
    "abattement":                       "Fatigue",

    "frissons":                         "Frissons",
    "avoir froid":                      "Frissons",
    "grelotter":                        "Frissons",
    "trembler de froid":                "Frissons",
    "froid dans le dos":                "Frissons",
    "chair de poule":                   "Frissons",

    "perte d'appétit":                  "Anorexie",
    "pas faim":                         "Anorexie",
    "ne mange plus":                    "Anorexie",
    "plus d'appétit":                   "Anorexie",
    "refus de manger":                  "Anorexie",
    "manque d'appétit":                 "Anorexie",
    "dégoût pour la nourriture":        "Anorexie",

    "perte de poids":                   "Perte de poids",
    "amaigrissement":                   "Perte de poids",
    "maigrir":                          "Perte de poids",
    "amaigrissement rapide":            "Perte de poids",
    "cachexie":                         "Perte de poids",

    "sueurs":                           "Sueurs nocturnes",
    "sueurs la nuit":                   "Sueurs nocturnes",
    "transpirer la nuit":               "Sueurs nocturnes",
    "nuit mouillée":                    "Sueurs nocturnes",
    "draps mouillés":                   "Sueurs nocturnes",
    "diaphorèse":                       "Sueurs nocturnes",

    "mal partout":                      "Douleurs musculaires",
    "douleurs dans tout le corps":      "Douleurs musculaires",
    "corps douloureux":                 "Courbatures",
    "courbaturé":                       "Courbatures",
    "muscles douloureux":               "Douleurs musculaires",
    "myalgies":                         "Douleurs musculaires",
    "douleurs diffuses":                "Courbatures",

    # ── TÊTE / NEUROLOGIQUES ─────────────────────────────────────────────────
    "mal à la tête":                    "Maux de tête",
    "mal de tête":                      "Maux de tête",
    "tête qui fait mal":                "Maux de tête",
    "céphalée":                         "Maux de tête",
    "céphalées":                        "Maux de tête",
    "migraine":                         "Maux de tête",
    "douleur à la tête":                "Maux de tête",
    "douleur crânienne":                "Maux de tête",
    "tête lourde":                      "Maux de tête",

    "tête qui tourne":                  "Vertiges",
    "vertiges":                         "Vertiges",
    "étourdissement":                   "Vertiges",
    "tournis":                          "Vertiges",
    "sensation de tourner":             "Vertiges",
    "instabilité":                      "Vertiges",
    "déséquilibre":                     "Vertiges",

    "crise d'épilepsie":                "Convulsions",
    "convulsion":                       "Convulsions",
    "tremblement involontaire":         "Convulsions",
    "spasmes":                          "Convulsions",
    "seizure":                          "Convulsions",

    "perte de connaissance":            "Syncope",
    "évanouissement":                   "Syncope",
    "s'est évanoui":                    "Syncope",
    "malaise":                          "Syncope",
    "lipothymie":                       "Syncope",

    "ne sait plus où il est":           "Confusion",
    "désorienté":                       "Confusion",
    "confus":                           "Confusion",
    "désorientation":                   "Confusion",
    "esprit embrouillé":                "Confusion",

    "ne parle plus bien":               "Troubles de la parole",
    "parole difficile":                 "Troubles de la parole",
    "dysarthrie":                       "Troubles de la parole",
    "aphasie":                          "Troubles de la parole",
    "bégaiement soudain":               "Troubles de la parole",

    "mémoire qui baisse":               "Perte de mémoire",
    "oubli":                            "Perte de mémoire",
    "amnésie":                          "Perte de mémoire",
    "troubles de la mémoire":           "Perte de mémoire",

    "tremblement des mains":            "Tremblements",
    "mains qui tremblent":              "Tremblements",
    "trembler":                         "Tremblements",
    "tremblement au repos":             "Tremblements",

    "nuque raide":                      "Raideur de la nuque",
    "raideur du cou":                   "Raideur de la nuque",
    "cou raide":                        "Raideur de la nuque",
    "méningisme":                       "Raideur de la nuque",
    "rigidité cervicale":               "Raideur de la nuque",

    "sensible à la lumière":            "Photophobie",
    "lumière douloureuse":              "Photophobie",
    "yeux sensibles à la lumière":      "Photophobie",
    "intolérance à la lumière":         "Photophobie",

    "sensible au bruit":                "Phonophobie",
    "bruit insupportable":              "Phonophobie",
    "intolérance au bruit":             "Phonophobie",

    # ── GORGE / ORL ──────────────────────────────────────────────────────────
    "mal à la gorge":                   "Mal de gorge",
    "gorge qui fait mal":               "Mal de gorge",
    "gorge irritée":                    "Mal de gorge",
    "gorge qui gratte":                 "Mal de gorge",
    "gorge douloureuse":                "Mal de gorge",
    "douleur à la gorge":               "Mal de gorge",
    "gorge en feu":                     "Mal de gorge",
    "mal en avalant":                   "Difficultés à avaler",
    "difficulté à avaler":              "Difficultés à avaler",
    "avaler est douloureux":            "Difficultés à avaler",
    "odynophagie":                      "Difficultés à avaler",
    "dysphagie":                        "Dysphagie",
    "blocage en avalant":               "Dysphagie",

    "nez bouché":                       "Congestion nasale",
    "nez encombré":                     "Congestion nasale",
    "obstruction nasale":               "Congestion nasale",
    "rhume":                            "Congestion nasale",
    "nez qui coule":                    "Rhinorrhée",
    "écoulement nasal":                 "Rhinorrhée",
    "morve":                            "Rhinorrhée",
    "rhinite":                          "Rhinorrhée",

    "voix qui change":                  "Enrouement",
    "voix rauque":                      "Enrouement",
    "voix cassée":                      "Enrouement",
    "dysphonie":                        "Enrouement",
    "voix éraillée":                    "Enrouement",

    "ganglions au cou":                 "Ganglions enflés",
    "ganglions gonflés":                "Ganglions enflés",
    "adénopathie":                      "Ganglions enflés",
    "boule au cou":                     "Ganglions enflés",
    "ganglions douloureux":             "Ganglions enflés",
    "lymphadénopathie":                 "Ganglions enflés",
    "ganglions au niveau des aisselles": "Ganglions enflés",
    "ganglions inguinaux":              "Ganglions enflés",

    "saignement de nez":                "Épistaxis",
    "nez qui saigne":                   "Épistaxis",
    "saignement nasal":                 "Épistaxis",

    "mal aux oreilles":                 "Douleur auriculaire",
    "oreille qui fait mal":             "Douleur auriculaire",
    "otalgie":                          "Douleur auriculaire",
    "douleur à l'oreille":              "Douleur auriculaire",

    "oreille bouchée":                  "Acouphènes",
    "sifflement dans les oreilles":     "Acouphènes",
    "bourdonnements":                   "Acouphènes",
    "tinnitus":                         "Acouphènes",

    # ── RESPIRATOIRES ────────────────────────────────────────────────────────
    "toux":                             "Toux",
    "tousser":                          "Toux",
    "toux sèche":                       "Toux sèche",
    "toux sans crachat":                "Toux sèche",
    "toux grasse":                      "Toux grasse",
    "toux avec crachats":               "Toux grasse",
    "toux avec mucus":                  "Toux grasse",
    "crachat":                          "Crachats",
    "expectoration":                    "Crachats",
    "glaires":                          "Crachats",
    "mucus dans les poumons":           "Crachats",
    "crachats sanglants":               "Hémoptysie",
    "sang dans les crachats":           "Hémoptysie",
    "cracher du sang":                  "Hémoptysie",

    "mal à respirer":                   "Essoufflement",
    "difficultés à respirer":           "Essoufflement",
    "respiration difficile":            "Essoufflement",
    "manque d'air":                     "Essoufflement",
    "souffle court":                    "Essoufflement",
    "dyspnée":                          "Essoufflement",
    "ne peut pas respirer":             "Essoufflement",
    "oppression respiratoire":          "Essoufflement",
    "s'essouffle vite":                 "Essoufflement",
    "haleter":                          "Essoufflement",

    "respiration sifflante":            "Sibilances",
    "sifflement respiratoire":          "Sibilances",
    "wheezing":                         "Sibilances",
    "bronchospasme":                    "Sibilances",

    "douleur en respirant":             "Douleur pleurale",
    "côte qui fait mal en respirant":   "Douleur pleurale",
    "point de côté":                    "Douleur pleurale",

    # ── CARDIAQUES / CARDIOVASCULAIRES ───────────────────────────────────────
    "coeur qui bat vite":               "Palpitations",
    "cœur qui s'emballe":               "Palpitations",
    "palpitations":                     "Palpitations",
    "tachycardie":                      "Palpitations",
    "battements forts":                 "Palpitations",
    "coeur irrégulier":                 "Pouls irrégulier",
    "arythmie":                         "Pouls irrégulier",
    "fibrillation":                     "Pouls irrégulier",

    "douleur dans la poitrine":         "Douleurs thoraciques",
    "mal à la poitrine":                "Douleurs thoraciques",
    "poitrine qui fait mal":            "Douleurs thoraciques",
    "douleur thoracique":               "Douleurs thoraciques",
    "oppression thoracique":            "Douleurs thoraciques",
    "pression dans la poitrine":        "Douleurs thoraciques",
    "angine":                           "Douleurs thoraciques",
    "douleur dans le bras gauche":      "Douleurs thoraciques",
    "étau dans la poitrine":            "Douleurs thoraciques",

    "tension artérielle élevée":        "Hypertension",
    "pression artérielle haute":        "Hypertension",
    "hta":                              "Hypertension",
    "tension haute":                    "Hypertension",
    "hypertendu":                       "Hypertension",

    "tension basse":                    "Hypotension",
    "pression artérielle basse":        "Hypotension",
    "hypotendu":                        "Hypotension",

    "jambes gonflées":                  "Gonflement des chevilles",
    "chevilles gonflées":               "Gonflement des chevilles",
    "pieds gonflés":                    "Gonflement des chevilles",
    "oedème des membres inférieurs":    "Gonflement des chevilles",
    "oedème":                           "Gonflement des chevilles",
    "rétention d'eau":                  "Gonflement des chevilles",

    # ── DIGESTIFS / GASTRO ───────────────────────────────────────────────────
    "mal au ventre":                    "Douleurs abdominales",
    "douleur au ventre":                "Douleurs abdominales",
    "ventre qui fait mal":              "Douleurs abdominales",
    "crampes au ventre":                "Douleurs abdominales",
    "abdomen douloureux":               "Douleurs abdominales",
    "coliques":                         "Douleurs abdominales",
    "tranchées":                        "Douleurs abdominales",

    "nausée":                           "Nausées",
    "envie de vomir":                   "Nausées",
    "coeur au bord des lèvres":         "Nausées",
    "mal au coeur":                     "Nausées",
    "barbouillé":                       "Nausées",
    "sensation de nausée":              "Nausées",

    "vomir":                            "Vomissements",
    "vomi":                             "Vomissements",
    "régurgitation":                    "Vomissements",
    "émèse":                            "Vomissements",

    "diarrhée":                         "Diarrhée",
    "selles liquides":                  "Diarrhée",
    "selles molles":                    "Diarrhée",
    "ventre qui dérange":               "Diarrhée",
    "transit accéléré":                 "Diarrhée",
    "selles fréquentes":                "Diarrhée",

    "constipé":                         "Constipation",
    "ne peut pas aller à la selle":     "Constipation",
    "difficulté à déféquer":            "Constipation",
    "selles dures":                     "Constipation",
    "ne va pas à la selle":             "Constipation",

    "brûlures à l'estomac":             "Brûlures gastriques",
    "acidité":                          "Brûlures gastriques",
    "remontées acides":                 "Reflux",
    "reflux":                           "Reflux",
    "pyrosis":                          "Brûlures gastriques",
    "aigreurs":                         "Brûlures gastriques",

    "sang dans les selles":             "Rectorragie",
    "selles noires":                    "Méléna",
    "selles sanglantes":                "Rectorragie",

    "ventre gonflé":                    "Ballonnements",
    "ballonnements":                    "Ballonnements",
    "abdomen distendu":                 "Ballonnements",
    "gaz":                              "Ballonnements",
    "flatulences":                      "Flatulences",

    "jaunisse":                         "Jaunisse",
    "peau jaune":                       "Jaunisse",
    "yeux jaunes":                      "Jaunisse",
    "ictère":                           "Jaunisse",
    "coloration jaune":                 "Jaunisse",

    "plaies dans la bouche":            "Ulcères buccaux",
    "plaies sur la langue":             "Ulcères buccaux",
    "aphtes":                           "Ulcères buccaux",
    "plaies buccales":                  "Ulcères buccaux",
    "ulcérations buccales":             "Ulcères buccaux",
    "bouche douloureuse":               "Ulcères buccaux",
    "stomatite":                        "Ulcères buccaux",

    "foie gros":                        "Hépatomégalie",
    "foie grossi":                      "Hépatomégalie",
    "grossissement du foie":            "Hépatomégalie",
    "rate grosse":                      "Splénomégalie",
    "rate gonflée":                     "Splénomégalie",

    # ── URINAIRES / RÉNAUX ───────────────────────────────────────────────────
    "brûlure en urinant":               "Brûlures mictionnelles",
    "piquer en urinant":                "Brûlures mictionnelles",
    "douleur en urinant":               "Brûlures mictionnelles",
    "uriner fait mal":                  "Brûlures mictionnelles",
    "dysurie":                          "Brûlures mictionnelles",
    "cystalgie":                        "Brûlures mictionnelles",

    "uriner souvent":                   "Pollakiurie",
    "envie fréquente d'uriner":         "Pollakiurie",
    "besoins urinaires fréquents":      "Pollakiurie",
    "urines fréquentes":                "Pollakiurie",
    "envie impérieuse d'uriner":        "Pollakiurie",

    "ne fait plus pipi":                "Anurie",
    "pas d'urine":                      "Anurie",
    "plus d'urine":                     "Anurie",
    "absence d'urines":                 "Anurie",
    "suppression urinaire":             "Anurie",

    "sang dans les urines":             "Hématurie",
    "urines rouges":                    "Hématurie",
    "urines sanglantes":                "Hématurie",
    "hématurie":                        "Hématurie",

    "urines mousseuses":                "Urine mousseuse",
    "pipi mousseux":                    "Urine mousseuse",
    "protéinurie":                      "Urine mousseuse",

    "mal dans le dos en bas":           "Douleur lombaire",
    "douleur dans le dos":              "Douleur lombaire",
    "mal aux reins":                    "Douleur lombaire",
    "douleur rénale":                   "Douleur lombaire",
    "douleur flanc":                    "Douleur lombaire",
    "lombalgie":                        "Douleur lombaire",

    "odeur bizarre dans la bouche":     "Haleine urémique",
    "mauvaise haleine":                 "Haleine urémique",
    "haleine d'urine":                  "Haleine urémique",
    "halitose":                         "Haleine urémique",

    "urines foncées":                   "Urines foncées",
    "urines marrons":                   "Urines foncées",
    "urines couleur thé":               "Urines foncées",
    "pipi marron":                      "Urines foncées",

    # ── CUTANÉS / DERMATOLOGIQUES ────────────────────────────────────────────
    "boutons":                          "Éruption cutanée",
    "éruption":                         "Éruption cutanée",
    "rash":                             "Éruption cutanée",
    "plaques rouges":                   "Éruption cutanée",
    "peau qui rougit":                  "Éruption cutanée",
    "rougeurs":                         "Éruption cutanée",
    "dermatose":                        "Éruption cutanée",
    "lésions cutanées":                 "Éruption cutanée",

    "peau qui gratte":                  "Prurit",
    "démangeaisons":                    "Prurit",
    "grattage":                         "Prurit",
    "prurit":                           "Prurit",
    "ça gratte":                        "Prurit",

    "peau sèche":                       "Peau sèche",
    "peau qui pèle":                    "Desquamation",
    "pelure":                           "Desquamation",
    "squames":                          "Desquamation",
    "desquamation":                     "Desquamation",

    "ampoules":                         "Vésicules",
    "cloques":                          "Vésicules",
    "vésicules":                        "Vésicules",
    "bulles":                           "Bulles",

    "urticaire":                        "Urticaire",
    "plaques qui gonflent":             "Urticaire",
    "plaques urticariennes":            "Urticaire",

    "taches blanches sur la peau":      "Vitiligo",
    "dépigmentation":                   "Vitiligo",
    "peau dépigmentée":                 "Vitiligo",

    "points noirs":                     "Comédons",
    "acné":                             "Acné",
    "boutons de jeunesse":              "Acné",
    "peau grasse avec boutons":         "Acné",

    "écailles sur la peau":             "Plaques rouges squameuses",
    "psoriasis":                        "Plaques rouges squameuses",
    "peau épaissie rouge":              "Plaques rouges squameuses",

    # ── ARTICULAIRES / MUSCULAIRES ───────────────────────────────────────────
    "mal aux articulations":            "Arthralgie",
    "articulations douloureuses":       "Arthralgie",
    "douleur dans les joints":          "Arthralgie",
    "rhumatisme":                       "Arthralgie",
    "polyarthralgie":                   "Arthralgie",
    "douleur dans les genoux":          "Arthralgie",

    "articulations gonflées":           "Arthrite",
    "gonflement des articulations":     "Arthrite",
    "arthrite":                         "Arthrite",
    "joint chaud et gonflé":            "Arthrite",

    "raideur le matin":                 "Raideur matinale",
    "difficultés à se lever":           "Raideur matinale",
    "corps raide au réveil":            "Raideur matinale",
    "raideur au réveil":                "Raideur matinale",

    "douleur dans les muscles":         "Douleurs musculaires",
    "muscles qui font mal":             "Douleurs musculaires",
    "myalgie":                          "Douleurs musculaires",

    "muscles qui s'affaiblissent":      "Faiblesse musculaire",
    "faiblesse dans les bras":          "Faiblesse musculaire",
    "faiblesse dans les jambes":        "Faiblesse musculaire",
    "muscles qui lâchent":              "Faiblesse musculaire",
    "parésie":                          "Faiblesse musculaire",
    "paralysie partielle":              "Faiblesse musculaire",

    "crampes dans les jambes":          "Crampes musculaires",
    "crampes":                          "Crampes musculaires",
    "crampes nocturnes":                "Crampes musculaires",

    "gros orteil rouge et gonflé":      "Tophi",
    "gros orteil douloureux":           "Tophi",
    "dépôt sous la peau":               "Tophi",

    # ── ENDOCRINIENS / MÉTABOLIQUES ──────────────────────────────────────────
    "soif intense":                     "Polydipsie",
    "boire beaucoup":                   "Polydipsie",
    "très soif":                        "Polydipsie",
    "soif excessive":                   "Polydipsie",
    "soif inextinguible":               "Polydipsie",

    "uriner beaucoup":                  "Polyurie",
    "faire beaucoup de pipi":           "Polyurie",
    "mictions abondantes":              "Polyurie",
    "diurèse abondante":                "Polyurie",

    "faim tout le temps":               "Polyphagie",
    "manger beaucoup":                  "Polyphagie",
    "appétit excessif":                 "Polyphagie",
    "faim excessive":                   "Polyphagie",

    "sucrerie dans le sang":            "Hyperglycémie",
    "glycémie élevée":                  "Hyperglycémie",
    "sucre dans le sang":               "Hyperglycémie",
    "diabète":                          "Hyperglycémie",

    "thyroïde gonflée":                 "Goître",
    "boule à la gorge":                 "Goître",
    "cou gonflé":                       "Goître",
    "goitre":                           "Goître",

    "prendre du poids":                 "Prise de poids",
    "grossir sans raison":              "Prise de poids",
    "obésité":                          "Prise de poids",
    "poids qui augmente":               "Prise de poids",

    "cheveux qui tombent":              "Chute de cheveux",
    "perte de cheveux":                 "Chute de cheveux",
    "alopécie":                         "Chute de cheveux",
    "calvitie":                         "Chute de cheveux",

    "ongles cassants":                  "Ongles dystrophiques",
    "ongles qui se cassent":            "Ongles dystrophiques",
    "ongles fragiles":                  "Ongles dystrophiques",

    "peau sèche et froide":             "Peau sèche",
    "intolérance au froid":             "Intolérance au froid",
    "toujours froid":                   "Intolérance au froid",
    "frilosité":                        "Intolérance au froid",

    "chaleur excessive":                "Intolérance à la chaleur",
    "toujours chaud":                   "Intolérance à la chaleur",
    "transpiration excessive":          "Sudation excessive",
    "beaucoup transpirer":              "Sudation excessive",
    "hypersudation":                    "Sudation excessive",

    # ── OPHTALMOLOGIQUES ─────────────────────────────────────────────────────
    "voir flou":                        "Vision floue",
    "vision trouble":                   "Vision floue",
    "flou visuel":                      "Vision floue",
    "yeux qui brouillent":              "Vision floue",
    "trouble de la vision":             "Vision floue",

    "yeux rouges":                      "Yeux rouges",
    "conjonctivite":                    "Yeux rouges",
    "yeux irrités":                     "Yeux rouges",
    "yeux injectés":                    "Yeux rouges",

    "yeux qui coulent":                 "Larmoiement",
    "larmoiement":                      "Larmoiement",
    "yeux larmoyants":                  "Larmoiement",

    "yeux gonflés":                     "Paupières gonflées",
    "paupières gonflées":               "Paupières gonflées",
    "œdème des paupières":              "Paupières gonflées",

    "douleur à l'oeil":                 "Douleur oculaire",
    "mal aux yeux":                     "Douleur oculaire",
    "yeux douloureux":                  "Douleur oculaire",

    "ne voit plus bien de loin":        "Myopie",
    "mal voir de loin":                 "Myopie",

    "ne voit plus bien de près":        "Hypermétropie",
    "mal voir de près":                 "Hypermétropie",

    "halos autour des lumières":        "Halos autour des lumières",
    "cercles autour des lampes":        "Halos autour des lumières",

    # ── HÉMATOLOGIQUES ───────────────────────────────────────────────────────
    "peau pâle":                        "Pâleur",
    "teint pâle":                       "Pâleur",
    "pâleur":                           "Pâleur",
    "anémié":                           "Pâleur",

    "ecchymoses":                       "Ecchymoses",
    "bleus sans raison":                "Ecchymoses",
    "hématomes spontanés":              "Ecchymoses",
    "se fait des bleus facilement":     "Ecchymoses",

    "saignement qui ne s'arrête pas":   "Saignements prolongés",
    "saignement excessif":              "Saignements prolongés",
    "troubles de la coagulation":       "Saignements prolongés",

    "ganglions partout":                "Adénopathie",
    "grosseur dans le cou":             "Adénopathie",
    "grosseurs sous les bras":          "Adénopathie",

    "petites taches rouges":            "Pétéchies",
    "petits points rouges":             "Pétéchies",
    "purpura":                          "Purpura",
    "taches violettes":                 "Purpura",

    # ── INFECTIEUX / IST ─────────────────────────────────────────────────────
    "plaie génitale":                   "Ulcère génital",
    "plaie sur le sexe":                "Ulcère génital",
    "chancre":                          "Chancre",
    "ulcération génitale":              "Ulcère génital",

    "pertes vaginales":                 "Pertes vaginales anormales",
    "écoulement vaginal":               "Pertes vaginales anormales",
    "pertes anormales":                 "Pertes vaginales anormales",
    "leucorrhée":                       "Pertes vaginales anormales",

    "écoulement urétral":               "Écoulement urétral",
    "pus du pénis":                     "Écoulement urétral",
    "pertes du pénis":                  "Écoulement urétral",

    "éruption autour des parties":      "Éruption génitale",
    "vésicules génitales":              "Éruption génitale",
    "herpès":                           "Éruption génitale",

    "boutons de fièvre":                "Herpès labial",
    "feu sauvage":                      "Herpès labial",
    "vésicules sur les lèvres":         "Herpès labial",

    "verrues":                          "Verrues",
    "condylomes":                       "Condylomes",
    "végétations":                      "Condylomes",
    "crêtes de coq":                    "Condylomes",

    # ── RESPIRATOIRES CHRONIQUES ─────────────────────────────────────────────
    "ronflements":                      "Ronflements",
    "ronfler":                          "Ronflements",
    "apnée pendant le sommeil":         "Apnées du sommeil",
    "arrêt de respirer pendant le sommeil": "Apnées du sommeil",
    "sommeil agité":                    "Apnées du sommeil",

    "emphysème":                        "Emphysème",
    "poumons abîmés":                   "Emphysème",
    "bpco":                             "Obstruction bronchique",
    "bronchite chronique":              "Obstruction bronchique",

    # ── PSYCHIATRIQUES / COMPORTEMENTAUX ─────────────────────────────────────
    "anxiété":                          "Anxiété",
    "angoisse":                         "Anxiété",
    "inquiétude excessive":             "Anxiété",
    "stress":                           "Anxiété",
    "nervosité":                        "Anxiété",

    "tristesse":                        "Dépression",
    "déprime":                          "Dépression",
    "moral bas":                        "Dépression",
    "idées noires":                     "Dépression",

    "comportement bizarre":             "Comportement inapproprié",
    "délire":                           "Comportement inapproprié",
    "hallucinations":                   "Hallucinations",
    "entendre des voix":                "Hallucinations",

    "troubles du sommeil":              "Insomnie",
    "ne dort pas":                      "Insomnie",
    "insomnie":                         "Insomnie",
    "difficultés à dormir":             "Insomnie",

    # ── DIVERS / SIGNES GÉNÉRAUX ─────────────────────────────────────────────
    "altération de la conscience":      "Altération de la conscience",
    "conscience altérée":               "Altération de la conscience",
    "semi-coma":                        "Altération de la conscience",
    "somnolent":                        "Altération de la conscience",
    "difficile à réveiller":            "Altération de la conscience",

    "prise de sang anormale":           "Bilan sanguin anormal",
    "bilan perturbé":                   "Bilan sanguin anormal",

    "douleur dans le dos":              "Douleur dorsale",
    "mal dans le dos":                  "Douleur dorsale",
    "dorsalgie":                        "Douleur dorsale",
    "douleur inter-scapulaire":         "Douleur dorsale",

    "douleur au niveau du sein":        "Mastalgie",
    "sein douloureux":                  "Mastalgie",
    "seins sensibles":                  "Mastalgie",
}


def enrichir_model_manager():
    """Fusionne les nouveaux synonymes dans le fichier model_manager.py."""
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "backend", "app", "ml", "model_manager.py"
    )
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Trouver la fin du dictionnaire SYNONYMES_SYMPTOMES
    start_marker = "SYNONYMES_SYMPTOMES: dict[str, str] = {"
    end_marker = "\n}\n"
    start_idx = content.index(start_marker)
    end_idx = content.index(end_marker, start_idx) + len(end_marker)

    bloc_actuel = content[start_idx:end_idx]

    # Extraire les clés déjà présentes
    cles_existantes = set(re.findall(r'"([^"]+)"\s*:', bloc_actuel))

    # Construire le bloc de nouveaux synonymes à ajouter
    nouveaux_filtres = {k: v for k, v in NOUVEAUX_SYNONYMES.items()
                        if k.lower() not in {c.lower() for c in cles_existantes}}

    print(f"Synonymes existants : {len(cles_existantes)}")
    print(f"Nouveaux à ajouter  : {len(nouveaux_filtres)}")

    if not nouveaux_filtres:
        print("Rien à ajouter — dictionnaire déjà à jour.")
        return

    # Regrouper par catégorie (basé sur les commentaires existants)
    ajout = "\n    # ── SYNONYMES ENRICHIS (langage courant → terme médical) ──────────────\n"
    for k, v in sorted(nouveaux_filtres.items()):
        # Alignement sur 44 chars
        pad = max(1, 44 - len(f'"{k}"'))
        ajout += f'    "{k}"{" " * pad}: "{v}",\n'

    # Insérer avant la dernière accolade
    nouveau_bloc = bloc_actuel.rstrip("}\n") + ajout + "}\n"
    new_content = content[:start_idx] + nouveau_bloc + content[end_idx:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ model_manager.py mis à jour — {len(nouveaux_filtres)} synonymes ajoutés.")


def generer_synonymes_pour_maladie(nom_maladie: str, symptomes: list[str]) -> dict:
    """
    Génère automatiquement des synonymes de base pour une nouvelle maladie.
    Appelé depuis l'interface admin lors de l'ajout d'une maladie.

    Retourne un dict {synonyme_courant: terme_canonique} prêt à être fusionné.
    """
    # Correspondances de base symptôme médical → variantes courantes
    PATTERNS = {
        "fièvre":       ["corps chaud", "chaud", "température", "fébrilité", "avoir de la fièvre"],
        "toux":         ["tousser", "toux sèche", "toux grasse"],
        "dyspnée":      ["mal à respirer", "essoufflement", "difficultés à respirer", "manque d'air"],
        "céphalées":    ["mal de tête", "mal à la tête", "maux de tête"],
        "nausées":      ["nausée", "envie de vomir", "mal au coeur", "barbouillé"],
        "vomissements": ["vomir", "vomi"],
        "diarrhée":     ["selles liquides", "ventre qui dérange"],
        "douleurs abdominales": ["mal au ventre", "ventre qui fait mal", "coliques"],
        "fatigue":      ["très fatigué", "épuisé", "asthénie", "sans énergie"],
        "arthralgie":   ["mal aux articulations", "rhumatisme", "douleur dans les joints"],
        "prurit":       ["démangeaisons", "ça gratte", "peau qui gratte"],
        "éruption cutanée": ["boutons", "rash", "plaques rouges", "rougeurs"],
    }

    synonymes_auto = {}
    for symptome in symptomes:
        s_lower = symptome.lower()
        for terme_cle, variantes in PATTERNS.items():
            if terme_cle in s_lower:
                for var in variantes:
                    if var.lower() not in synonymes_auto:
                        synonymes_auto[var.lower()] = symptome

    return synonymes_auto


if __name__ == "__main__":
    enrichir_model_manager()

    # Afficher un aperçu
    print("\n=== Aperçu des synonymes ajoutés ===")
    exemples = [
        ("mal à la gorge", NOUVEAUX_SYNONYMES.get("mal à la gorge")),
        ("corps chaud", NOUVEAUX_SYNONYMES.get("corps chaud")),
        ("plaies sur la langue", NOUVEAUX_SYNONYMES.get("plaies sur la langue")),
        ("jambes gonflées", NOUVEAUX_SYNONYMES.get("jambes gonflées")),
        ("vomir", NOUVEAUX_SYNONYMES.get("vomir")),
        ("jaunisse", NOUVEAUX_SYNONYMES.get("jaunisse")),
    ]
    for k, v in exemples:
        print(f"  '{k}' → '{v}'")
