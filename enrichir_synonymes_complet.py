"""
Script d'enrichissement COMPLET du dictionnaire de synonymes.
Couvre les 444 symptômes sans synonymes pour toutes les 122 maladies du dataset.
Usage : python enrichir_synonymes_complet.py
"""
import re, sys, os
sys.stdout.reconfigure(encoding='utf-8')

SYNONYMES_COMPLETS: dict[str, str] = {

    # ══ A ══════════════════════════════════════════════════════════════════════
    "avc transitoire":                      "AVC transitoire",
    "mini avc":                             "AVC transitoire",
    "attaque cérébrale passagère":          "AVC transitoire",
    "ischémie cérébrale transitoire":       "AVC transitoire",
    "ict":                                  "AVC transitoire",

    "absence":                              "Absence",
    "petit mal":                            "Absence",
    "crise d'absence":                      "Absence",

    "agitation":                            "Agitation",
    "agité":                                "Agitation",
    "nerveux":                              "Agitation",
    "hyperactivité":                        "Agitation",

    "mains et pieds qui grandissent":       "Agrandissement des mains/pieds",
    "grossissement des extrémités":         "Agrandissement des mains/pieds",
    "mains qui s'élargissent":              "Agrandissement des mains/pieds",
    "acromégalie des extrémités":          "Agrandissement des mains/pieds",

    "albumine basse":                       "Albuminémie basse",
    "hypoalbuminémie":                      "Albuminémie basse",
    "protéines basses dans le sang":        "Albuminémie basse",

    "alopécie":                             "Alopécie",
    "perte des cheveux":                    "Alopécie",
    "calvitie":                             "Alopécie",
    "chute des cheveux":                    "Alopécie",

    "alternance constipation diarrhée":     "Alternance diarrhée-constipation",
    "transit irrégulier":                   "Alternance diarrhée-constipation",
    "intestins capricieux":                 "Alternance diarrhée-constipation",

    "amygdales gonflées":                   "Amygdalite",
    "angine":                               "Amygdalite",
    "gorge avec plaques blanches":          "Amygdalite",
    "tonsillite":                           "Amygdalite",
    "inflammation des amygdales":           "Amygdalite",

    "angioedème":                           "Angioedème",
    "gonflement du visage":                 "Angioedème",
    "gonflement lèvres yeux":               "Angioedème",
    "oedème de quincke":                    "Angioedème",
    "gonflement allergique":                "Angioedème",

    "anxiety":                              "Anxiété",

    "anémie":                               "Anémie",
    "sang pauvre":                          "Anémie",
    "manque de globules rouges":            "Anémie",
    "taux d'hémoglobine bas":               "Anémie",

    "arc cornéen":                          "Arc cornéen",
    "anneau blanc dans l'oeil":             "Arc cornéen",
    "cercle blanc autour de l'iris":        "Arc cornéen",

    "arthralgie périphérique":              "Arthralgie périphérique",
    "douleur aux petites articulations":    "Arthralgie périphérique",
    "douleur des doigts et orteils":        "Arthralgie périphérique",

    "ascite":                               "Ascite",
    "eau dans le ventre":                   "Ascite",
    "ventre qui gonfle d'eau":              "Ascite",
    "épanchement abdominal":                "Ascite",
    "liquide dans l'abdomen":               "Ascite",

    "atrophie musculaire":                  "Atrophie musculaire",
    "muscles qui fondent":                  "Atrophie musculaire",
    "fonte musculaire":                     "Atrophie musculaire",
    "muscles qui disparaissent":            "Atrophie musculaire",
    "amyotrophie":                          "Atrophie musculaire",

    "aura":                                 "Aura",
    "lumières avant la crise":              "Aura",
    "zigzags visuels":                      "Aura",
    "signes avant-coureurs":                "Aura",

    # ══ B ══════════════════════════════════════════════════════════════════════
    "infection urinaire":                   "Bactériurie",
    "germes dans les urines":               "Bactériurie",
    "urines infectées":                     "Bactériurie",

    "barrel chest":                         "Barrel chest",
    "thorax en tonneau":                    "Barrel chest",
    "poitrine gonflée":                     "Barrel chest",
    "cage thoracique élargie":              "Barrel chest",

    "envie d'uriner souvent":              "Besoin fréquent d'uriner",
    "uriner trop souvent":                  "Besoin fréquent d'uriner",
    "pollakiurie":                          "Besoin fréquent d'uriner",

    "envie impérieuse de selles":           "Besoin impérieux de déféquer",
    "urgence pour aller aux toilettes":     "Besoin impérieux de déféquer",
    "ne peut pas se retenir":              "Besoin impérieux de déféquer",

    "ecchymoses sans raison":              "Bleus faciles",
    "se fait des bleus facilement":        "Bleus faciles",
    "bleus spontanés":                     "Bleus faciles",

    "blépharospasme":                       "Blépharospasme",
    "paupières qui se ferment":             "Blépharospasme",
    "spasme des paupières":                 "Blépharospasme",
    "clignements involontaires":            "Blépharospasme",

    "bosse de bison":                       "Bosse de bison",
    "bosse dans le dos":                    "Bosse de bison",
    "cou de taureau":                       "Bosse de bison",
    "graisse dans le dos":                  "Bosse de bison",

    "bouche sèche au lever":                "Bouche sèche au réveil",
    "bouche desséchée le matin":            "Bouche sèche au réveil",
    "xérostomie matinale":                  "Bouche sèche au réveil",

    "bourdonnements dans les oreilles":     "Bourdonnements",
    "acouphènes":                           "Bourdonnements",
    "sifflements dans les oreilles":        "Bourdonnements",
    "tinnitus":                             "Bourdonnements",
    "bruit dans les oreilles":              "Bourdonnements",

    "pouls lent":                           "Bradycardie",
    "cœur qui bat lentement":              "Bradycardie",
    "rythme cardiaque lent":                "Bradycardie",
    "bradycardie":                          "Bradycardie",

    "bradycardie relative":                 "Bradycardie relative",
    "pouls normal malgré fièvre":           "Bradycardie relative",

    "pieds qui brûlent":                    "Brûlures aux pieds",
    "sensation de brûlure dans les pieds":  "Brûlures aux pieds",
    "neuropathie brûlante":                 "Brûlures aux pieds",

    "brûlures cutanées":                    "Brûlures cutanées",
    "peau qui brûle":                       "Brûlures cutanées",
    "sensation de brûlure sur la peau":     "Brûlures cutanées",

    "brûlures génitales":                   "Brûlures génitales",
    "sexe qui brûle":                       "Brûlures génitales",
    "douleur brûlante génitale":            "Brûlures génitales",

    "brûlures urinaires":                   "Brûlures urinaires",
    "piquer en faisant pipi":               "Brûlures urinaires",
    "uriner fait mal et brûle":             "Brûlures urinaires",

    "brûlures épigastriques":               "Brûlures épigastriques",
    "brûlure au creux du ventre":           "Brûlures épigastriques",
    "douleur brûlante estomac":             "Brûlures épigastriques",
    "épigastralgie brûlante":               "Brûlures épigastriques",

    # ══ C ══════════════════════════════════════════════════════════════════════
    "calcinose":                            "Calcinose",
    "dépôts calcaires sous la peau":        "Calcinose",
    "petits cailloux sous la peau":         "Calcinose",

    "candidose":                            "Candidose buccale",
    "champignons dans la bouche":           "Candidose buccale",
    "muguet":                               "Candidose buccale",
    "taches blanches dans la bouche":       "Candidose buccale",
    "mycose buccale":                       "Candidose buccale",

    "caries":                               "Caries dentaires",
    "dents cariées":                        "Caries dentaires",
    "dents qui se gâtent":                  "Caries dentaires",

    "cervicite":                            "Cervicite",
    "col de l'utérus infecté":             "Cervicite",
    "infection du col":                     "Cervicite",

    "chaleur":                              "Chaleur",
    "sensation de chaleur":                 "Chaleur",
    "bouffées de chaleur":                  "Chaleur",

    "cheveux cassants":                     "Cheveux cassants",
    "cheveux qui se cassent":               "Cheveux cassants",
    "cheveux fragiles":                     "Cheveux cassants",
    "cheveux secs":                         "Cheveux cassants",

    "choc":                                 "Choc",
    "état de choc":                         "Choc",
    "collapsus":                            "Choc",

    "choc septique":                        "Choc septique",
    "infection grave avec choc":            "Choc septique",
    "sepsis sévère":                        "Choc septique",

    "chute":                                "Chute",
    "tomber souvent":                       "Chute",
    "chutes répétées":                      "Chute",
    "instabilité à la marche":              "Chute",

    "cicatrices":                           "Cicatrices",
    "marques sur la peau":                  "Cicatrices",
    "cicatrisation difficile":              "Cicatrices",

    "claudication":                         "Claudication",
    "douleur en marchant":                  "Claudication",
    "jambes qui font mal à la marche":      "Claudication",
    "boiter":                               "Claudication",

    "complications neurologiques":          "Complications neurologiques",
    "problèmes nerveux":                    "Complications neurologiques",
    "atteinte du système nerveux":          "Complications neurologiques",

    "confusion après crise":               "Confusion post-critique",
    "désorientation après convulsion":      "Confusion post-critique",

    "conjonctivite":                        "Conjonctivite",
    "yeux roses":                           "Conjonctivite",
    "inflammation des yeux":               "Conjonctivite",
    "yeux qui collent":                     "Conjonctivite",

    "crevasses":                            "Crevasses",
    "peau fissurée":                        "Crevasses",
    "fissures aux mains":                   "Crevasses",
    "talons crevassés":                     "Crevasses",

    "croûtes":                              "Croûtes",
    "croûtes sur la peau":                  "Croûtes",
    "plaies qui forment des croûtes":       "Croûtes",

    "cyanose":                              "Cyanose",
    "lèvres bleues":                        "Cyanose",
    "peau bleue":                           "Cyanose",
    "teinte bleutée":                       "Cyanose",
    "bleu autour des lèvres":               "Cyanose",

    "cyanose distale":                      "Cyanose distale",
    "doigts bleus":                         "Cyanose distale",
    "extrémités bleues":                    "Cyanose distale",

    "cyanose légère":                       "Cyanose légère",
    "légère teinte bleue":                  "Cyanose légère",

    "céphalées":                            "Céphalées",
    "mal de tête":                          "Céphalées",
    "tête douloureuse":                     "Céphalées",

    "céphalées sévères":                    "Céphalées sévères",
    "migraine sévère":                      "Céphalées sévères",
    "terrible mal de tête":                 "Céphalées sévères",
    "céphalée en coup de tonnerre":         "Céphalées sévères",

    # ══ D ══════════════════════════════════════════════════════════════════════
    "depression":                           "Dépression",
    "déprime":                              "Dépression",
    "tristesse profonde":                   "Dépression",
    "mélancolie":                           "Dépression",
    "moral effondré":                       "Dépression",

    "difficultes a avaler":                 "Difficultés à avaler",
    "mal à avaler":                         "Difficultés à avaler",
    "avaler est difficile":                 "Difficultés à avaler",

    "difficulté de lecture":                "Difficulté à lire",
    "ne peut plus lire":                    "Difficulté à lire",
    "texte flou à la lecture":              "Difficulté à lire",

    "voir mal la nuit":                     "Difficulté nocturne",
    "héméralopie":                          "Difficulté nocturne",
    "cécité nocturne":                      "Difficulté nocturne",

    "mal entendre":                         "Difficulté à entendre",
    "surdité partielle":                    "Difficulté à entendre",
    "perte auditive":                       "Difficulté à entendre",
    "hypoacousie":                          "Difficulté à entendre",

    "difficultés à lire":                   "Difficulté à lire",
    "presbytie":                            "Difficulté à lire",
    "lecture difficile":                    "Difficulté à lire",

    "marche difficile":                     "Difficultés à marcher",
    "boitera":                              "Difficultés à marcher",
    "problème de marche":                   "Difficultés à marcher",
    "ataxie":                               "Difficultés à marcher",

    "difficulté à faire pipi":              "Difficulté à uriner",
    "jet urinaire difficile":               "Difficulté à uriner",
    "uriner est difficile":                 "Difficulté à uriner",
    "dysurie":                              "Difficulté à uriner",
    "rétention urinaire partielle":         "Difficulté à uriner",

    "difficultés de concentration":         "Difficultés de concentration",
    "ne peut pas se concentrer":            "Difficultés de concentration",
    "manque d'attention":                   "Difficultés de concentration",
    "brouillard mental":                    "Difficultés de concentration",

    "difficulté à parler":                  "Difficultés de langage",
    "parole difficile":                     "Difficultés de langage",
    "aphasie":                              "Difficultés de langage",
    "langage perturbé":                     "Difficultés de langage",

    "difficultés à conduire de nuit":       "Difficultés à conduire la nuit",
    "conduite nocturne impossible":         "Difficultés à conduire la nuit",

    "difficultés à parler":                 "Difficultés à parler",
    "dysarthrie":                           "Difficultés à parler",
    "parole embrouillée":                   "Difficultés à parler",

    "difficultés à respirer":               "Dyspnée",
    "problèmes respiratoires":              "Dyspnée",
    "respiration difficile":                "Dyspnée",

    "difficultés à uriner":                 "Difficulté à uriner",

    "vision double":                        "Diplopie",
    "voir en double":                       "Diplopie",
    "diplopie":                             "Diplopie",
    "dédoublement de la vision":            "Diplopie",

    "diplopie légère":                      "Diplopie légère",
    "léger dédoublement visuel":            "Diplopie légère",

    "douleur":                              "Douleur",
    "avoir mal":                            "Douleur",
    "douleur générale":                     "Douleur",

    "douleur abdominale":                   "Douleurs abdominales",
    "douleur du ventre":                    "Douleurs abdominales",

    "douleur abdominale droite":            "Douleur abdominale droite",
    "douleur côté droit":                   "Douleur abdominale droite",
    "douleur flanc droit":                  "Douleur abdominale droite",
    "douleur à la fosse iliaque droite":    "Douleur abdominale droite",

    "douleur estomac en haut":              "Douleur abdominale supérieure",
    "douleur épigastrique":                 "Douleur abdominale supérieure",
    "douleur sous le sternum":              "Douleur abdominale supérieure",

    "douleur ventre très forte":            "Douleur abdominale sévère",
    "ventre très douloureux":               "Douleur abdominale sévère",
    "abdomen en planche":                   "Douleur abdominale sévère",

    "douleur améliorée par l'exercice":     "Douleur améliorée par l'exercice",
    "douleur qui passe en bougeant":        "Douleur améliorée par l'exercice",

    "douleur après les graisses":           "Douleur après repas gras",
    "mal au ventre après repas gras":       "Douleur après repas gras",
    "douleur après fritures":               "Douleur après repas gras",

    "douleur articulaire":                  "Douleur articulaire",
    "mal aux articulations":                "Douleur articulaire",
    "articulation douloureuse":             "Douleur articulaire",

    "douleur articulaire brutale":          "Douleur articulaire soudaine",
    "crise articulaire soudaine":           "Douleur articulaire soudaine",

    "douleur au bras":                      "Douleur au bras/épaule",
    "douleur à l'épaule":                   "Douleur au bras/épaule",
    "bras douloureux":                      "Douleur au bras/épaule",
    "épaule qui fait mal":                  "Douleur au bras/épaule",

    "douleur au cou":                       "Douleur au cou",
    "cou douloureux":                       "Douleur au cou",
    "cervicalgie":                          "Douleur au cou",
    "mal dans le cou":                      "Douleur au cou",
    "torticolis":                           "Douleur au cou",

    "douleur aux jambes":                   "Douleur aux extrémités",
    "douleur aux bras et jambes":           "Douleur aux extrémités",
    "extrémités douloureuses":              "Douleur aux extrémités",

    "douleur des deux côtés":               "Douleur bilatérale",
    "douleur symétrique":                   "Douleur bilatérale",

    "douleur qui s'améliore penché en avant": "Douleur calmée penché en avant",
    "pancréatite position antalgique":      "Douleur calmée penché en avant",

    "colique":                              "Douleur colique intense",
    "douleur en coup de couteau":           "Douleur colique intense",
    "douleur par vagues":                   "Douleur colique intense",

    "douleur dans le dos en bas":           "Douleur costovertébrale",
    "flanc costovertébral douloureux":      "Douleur costovertébrale",
    "angle costo-vertébral sensible":       "Douleur costovertébrale",

    "mal aux dents":                        "Douleur dentaire",
    "dent douloureuse":                     "Douleur dentaire",
    "rage de dents":                        "Douleur dentaire",

    "douleur à la face":                    "Douleur faciale",
    "joue douloureuse":                     "Douleur faciale",
    "névralgie faciale":                    "Douleur faciale",

    "douleur qui monte dans le dos":        "Douleur irradiant dans le dos",
    "irradiation dorsale":                  "Douleur irradiant dans le dos",

    "douleur qui descend dans l'aine":      "Douleur irradiant vers aine",
    "douleur lombaire avec irradiation":    "Douleur irradiant vers aine",

    "douleur sous l'épaule droite":         "Douleur irradiant épaule droite",
    "irradiation vers épaule droite":       "Douleur irradiant épaule droite",

    "douleur irradiante":                   "Douleur irradiante",
    "douleur qui se propage":               "Douleur irradiante",
    "douleur rayonnante":                   "Douleur irradiante",

    "mal à la gorge en parlant":            "Douleur laryngée",
    "larynx douloureux":                    "Douleur laryngée",

    "douleur pendant les rapports":         "Douleur lors des rapports",
    "dyspareunie":                          "Douleur lors des rapports",
    "rapports sexuels douloureux":          "Douleur lors des rapports",

    "douleur dans la jambe":                "Douleur membre inférieur",
    "jambe douloureuse":                    "Douleur membre inférieur",

    "douleur musculaire":                   "Douleur musculaire",
    "muscles douloureux":                   "Douleur musculaire",

    "douleur électrique":                   "Douleur neuropathique",
    "douleur en coup d'aiguille":           "Douleur neuropathique",
    "brûlure électrique":                   "Douleur neuropathique",
    "névralgie":                            "Douleur neuropathique",

    "douleur la nuit":                      "Douleur nocturne",
    "douleur nocturne":                     "Douleur nocturne",
    "réveillé par la douleur":              "Douleur nocturne",

    "douleur dans le bassin":               "Douleur pelvienne",
    "douleur basse-ventre":                 "Douleur pelvienne",
    "douleur pelvienne":                    "Douleur pelvienne",

    "douleur périnée":                      "Douleur pelvipérinéale",
    "douleur entre jambes":                 "Douleur pelvipérinéale",

    "douleur au périnée":                   "Douleur périnéale",
    "périnée douloureux":                   "Douleur périnéale",

    "douleur derrière le sternum":          "Douleur rétrosternale",
    "douleur rétrosternale":                "Douleur rétrosternale",
    "douleur au milieu de la poitrine":     "Douleur rétrosternale",

    "douleur soulagée par les selles":      "Douleur soulagée par défécation",
    "douleur qui passe après défécation":   "Douleur soulagée par défécation",

    "testicule douloureux":                 "Douleur testiculaire",
    "douleur au testicule":                 "Douleur testiculaire",
    "orchialgie":                           "Douleur testiculaire",

    "point de côté respiratoire":           "Douleur thoracique pleurétique",
    "douleur qui augmente en respirant":    "Douleur thoracique pleurétique",
    "pleurodynie":                          "Douleur thoracique pleurétique",

    "douleur poitrine très forte":          "Douleur thoracique sévère",
    "douleur thoracique intense":           "Douleur thoracique sévère",
    "angine de poitrine sévère":            "Douleur thoracique sévère",

    "douleur à la thyroïde":                "Douleur thyroïdienne",
    "thyroïde douloureuse":                 "Douleur thyroïdienne",

    "douleur d'un côté seulement":          "Douleur unilatérale",
    "douleur latérale":                     "Douleur unilatérale",

    "douleur à l'estomac à jeun":           "Douleur à jeun",
    "faim douloureuse":                     "Douleur à jeun",
    "douleur qui part à jeun":              "Douleur à jeun",

    "douleur à l'effort physique":          "Douleur à l'effort",
    "douleur pendant l'exercice":           "Douleur à l'effort",
    "douleur en montant les escaliers":     "Douleur à l'effort",

    "douleur en avalant":                   "Douleur à la déglutition",
    "gorge douloureuse à la déglutition":   "Douleur à la déglutition",
    "odynophagie":                          "Douleur à la déglutition",

    "mâchoire douloureuse":                 "Douleur à la mâchoire",
    "douleur à la mâchoire":                "Douleur à la mâchoire",
    "craquement mâchoire":                  "Douleur à la mâchoire",

    "douleur à la nuque":                   "Douleur à la nuque",
    "nuque douloureuse":                    "Douleur à la nuque",
    "douleur cervicale postérieure":        "Douleur à la nuque",

    "douleurs musculaires diffuses":        "Douleurs musculaires diffuses",
    "douleurs dans tous les muscles":       "Douleurs musculaires diffuses",
    "fibromyalgie douleurs":                "Douleurs musculaires diffuses",

    "douleurs nocturnes":                   "Douleurs nocturnes",
    "douleurs la nuit":                     "Douleurs nocturnes",
    "réveil douloureux":                    "Douleurs nocturnes",

    "peau qui durcit":                      "Durcissement cutané",
    "sclérose cutanée":                     "Durcissement cutané",
    "peau tendue et dure":                  "Durcissement cutané",

    "parole mal articulée":                 "Dysarthrie",
    "difficulté à articuler":               "Dysarthrie",
    "voix pâteuse":                         "Dysarthrie",

    "rapport sexuel douloureux":            "Dyspareunie",
    "douleur pendant le sexe":              "Dyspareunie",
    "vaginisme":                            "Dyspareunie",

    "dyspnee":                              "Dyspnée",
    "dyspnée":                              "Dyspnée",
    "respiration difficile":                "Dyspnée",
    "manque d'air":                         "Dyspnée",

    "essoufflement à l'effort":             "Dyspnée d'effort",
    "manque d'air en marchant":             "Dyspnée d'effort",
    "ne peut plus faire de sport":          "Dyspnée d'effort",

    "essoufflement couché":                 "Dyspnée de décubitus",
    "mal à respirer allongé":               "Dyspnée de décubitus",
    "orthopnée":                            "Dyspnée de décubitus",

    "essoufflement la nuit":                "Dyspnée nocturne",
    "réveil difficile à respirer":          "Dyspnée nocturne",

    "essoufflement progressif":             "Dyspnée progressive",
    "souffle qui diminue avec le temps":    "Dyspnée progressive",

    "brûlure en urinant":                   "Dysurie",
    "urination douloureuse":                "Dysurie",
    "douleur au passage de l'urine":        "Dysurie",

    "déformation qui empire":               "Déformation progressive",
    "déformation qui s'aggrave":            "Déformation progressive",

    "délire":                               "Délire",
    "propos incohérents":                   "Délire",
    "ne sait plus ce qu'il dit":            "Délire",

    "démangeaisons génitales":              "Démangeaisons génitales",
    "sexe qui gratte":                      "Démangeaisons génitales",
    "prurit vulvaire":                      "Démangeaisons génitales",
    "prurit périnéal":                      "Démangeaisons génitales",

    "démangeaisons locales":                "Démangeaisons locales",
    "ça gratte à un endroit précis":        "Démangeaisons locales",
    "prurit localisé":                      "Démangeaisons locales",

    "démangeaisons légères":                "Démangeaisons légères",
    "légère irritation cutanée":            "Démangeaisons légères",

    "nez qui gratte":                       "Démangeaisons nasales",
    "nez irrité":                           "Démangeaisons nasales",
    "prurit nasal":                         "Démangeaisons nasales",

    "démence":                              "Démence",
    "perte des facultés mentales":          "Démence",
    "détérioration cognitive":              "Démence",

    "dépôts aux paupières":                 "Dépôts lipidiques aux paupières",
    "xanthélasma":                          "Dépôts lipidiques aux paupières",
    "paupières jaunâtres":                  "Dépôts lipidiques aux paupières",

    "déshydratation":                       "Déshydratation",
    "manque d'eau":                         "Déshydratation",
    "bouche sèche et soif intense":         "Déshydratation",

    "désorientation":                       "Désorientation",
    "perdu dans l'espace":                  "Désorientation",
    "ne sait plus où il est":              "Désorientation",

    "sucre instable":                       "Déséquilibre glycémique",
    "glycémie fluctuante":                  "Déséquilibre glycémique",
    "diabète mal contrôlé":                 "Déséquilibre glycémique",

    # ══ E ══════════════════════════════════════════════════════════════════════
    "ecchymoses faciles":                   "Ecchymoses faciles",
    "tendance aux ecchymoses":              "Ecchymoses faciles",

    "pousser fort pour déféquer":           "Efforts pour défécation",
    "défécation difficile":                 "Efforts pour défécation",
    "effort à la selle":                    "Efforts pour défécation",

    "encéphalopathie":                      "Encéphalopathie",
    "cerveau qui fonctionne mal":           "Encéphalopathie",
    "atteinte cérébrale":                   "Encéphalopathie",
    "confusion mentale sévère":             "Encéphalopathie",

    "engourdissement":                      "Engourdissement",
    "membres engourdis":                    "Engourdissement",
    "fourmis dans les membres":             "Engourdissement",
    "hypoesthésie":                         "Engourdissement",

    "engourdissement du visage":            "Engourdissement facial",
    "visage engourdi":                      "Engourdissement facial",
    "hémiface insensible":                  "Engourdissement facial",

    "enthésite":                            "Enthésite",
    "douleur à l'insertion du tendon":      "Enthésite",
    "tendon douloureux":                    "Enthésite",

    "dents qui s'écartent":                 "Espacement des dents",
    "diastème qui s'élargit":               "Espacement des dents",
    "dents espacées":                       "Espacement des dents",

    "essoufflement activité physique":      "Essoufflement d'effort",
    "souffle court à l'effort":             "Essoufflement d'effort",

    "essoufflement après repas":            "Essoufflement postprandial",
    "mal à respirer après avoir mangé":     "Essoufflement postprandial",

    "essoufflement brutal":                 "Essoufflement soudain",
    "dyspnée aiguë":                        "Essoufflement soudain",
    "difficulté à respirer brutale":        "Essoufflement soudain",

    "excroissance cutanée":                 "Excroissance cutanée",
    "bosse sur la peau":                    "Excroissance cutanée",
    "verrue":                               "Excroissance cutanée",
    "molluscum":                            "Excroissance cutanée",

    "expectoration":                        "Expectoration",
    "crachat":                              "Expectoration",
    "crachats épais":                       "Expectoration",
    "mucus expulsé":                        "Expectoration",

    # ══ F ══════════════════════════════════════════════════════════════════════
    "faiblesse ascendante":                 "Faiblesse ascendante",
    "paralysie qui monte":                  "Faiblesse ascendante",
    "faiblesse des pieds vers le haut":     "Faiblesse ascendante",

    "faiblesse des membres":                "Faiblesse des membres",
    "bras et jambes faibles":               "Faiblesse des membres",
    "ne peut plus lever les bras":          "Faiblesse des membres",

    "faiblesse brutale":                    "Faiblesse soudaine",
    "faiblesse soudaine":                   "Faiblesse soudaine",
    "perte de force brusque":               "Faiblesse soudaine",

    "faim tout le temps":                   "Faim excessive",
    "polyphagie":                           "Faim excessive",
    "manger trop":                          "Faim excessive",

    "fasciculations":                       "Fasciculations",
    "muscles qui tressautent":              "Fasciculations",
    "petits mouvements musculaires involontaires": "Fasciculations",
    "myokymie":                             "Fasciculations",

    "fatigue au réveil":                    "Fatigue au réveil",
    "fatigué dès le matin":                 "Fatigue au réveil",
    "pas reposé le matin":                  "Fatigue au réveil",

    "fatigue chronique":                    "Fatigue chronique",
    "fatigue persistante":                  "Fatigue chronique",
    "toujours fatigué":                     "Fatigue chronique",
    "épuisement chronique":                 "Fatigue chronique",

    "fatigue oculaire":                     "Fatigue oculaire",
    "yeux qui fatiguent vite":              "Fatigue oculaire",
    "asthénopie":                           "Fatigue oculaire",

    "fatigue après crise":                  "Fatigue post-critique",
    "épuisement post-convulsif":            "Fatigue post-critique",

    "fatigue soudaine":                     "Fatigue soudaine",
    "coup de pompe":                        "Fatigue soudaine",
    "fatigue brutale":                      "Fatigue soudaine",

    "fibrose pulmonaire":                   "Fibrose pulmonaire",
    "poumons qui se fibrosent":             "Fibrose pulmonaire",
    "cicatrisation pulmonaire":             "Fibrose pulmonaire",

    "fissures cutanées":                    "Fissures cutanées",
    "peau qui se fissure":                  "Fissures cutanées",

    "fistules":                             "Fistules",
    "tunnel entre organes":                 "Fistules",
    "communication anormale":               "Fistules",

    "fièvre par crises":                    "Fièvre intermittente",
    "fièvre qui va et vient":               "Fièvre intermittente",
    "fièvre cyclique":                      "Fièvre intermittente",

    "fièvre légère":                        "Fièvre légère",
    "légère température":                   "Fièvre légère",
    "37.5 degrés":                          "Fièvre légère",
    "subfébrile":                           "Fièvre légère",

    "flou vision proche":                   "Flou proche",
    "voir flou de près":                    "Flou proche",

    "pipi lent":                            "Flux faible",
    "jet urinaire faible":                  "Flux faible",
    "difficulté d'écoulement urinaire":     "Flux faible",

    "fourmillements":                       "Fourmillements",
    "picotements":                          "Fourmillements",
    "fourmis dans les jambes":              "Fourmillements",
    "paresthésies":                         "Fourmillements",

    "peau fragile":                         "Fragilité cutanée",
    "peau qui se déchire":                  "Fragilité cutanée",

    "os fragiles":                          "Fragilité osseuse",
    "fractures faciles":                    "Fragilité osseuse",
    "ostéoporose":                          "Fragilité osseuse",

    "frissons forts":                       "Frissons intenses",
    "frissons violents":                    "Frissons intenses",
    "rigors":                               "Frissons intenses",

    "frottement cardiaque":                 "Frottement péricardique",
    "bruit cardiaque anormal":              "Frottement péricardique",

    "fréquence urinaire":                   "Fréquence urinaire",
    "uriner plusieurs fois":                "Fréquence urinaire",
    "mictions fréquentes":                  "Fréquence urinaire",

    # ══ G ══════════════════════════════════════════════════════════════════════
    "gangrène":                             "Gangrène distale",
    "tissu mort aux extrémités":            "Gangrène distale",
    "doigts nécrosés":                      "Gangrène distale",

    "gaz":                                  "Gaz",
    "flatulences":                          "Gaz",
    "ventre plein de gaz":                  "Gaz",
    "météorisme":                           "Gaz",

    "langue rouge":                         "Glossite",
    "langue douloureuse":                   "Glossite",
    "inflammation de la langue":            "Glossite",

    "gonflement":                           "Gonflement",
    "enflure":                              "Gonflement",
    "tuméfaction":                          "Gonflement",
    "œdème":                                "Gonflement",

    "lèvres gonflées":                      "Gonflement des lèvres",
    "gonflement labial":                    "Gonflement des lèvres",
    "lèvres enflées":                       "Gonflement des lèvres",

    "paupières gonflées":                   "Gonflement des paupières",
    "yeux enflés":                          "Gonflement des paupières",
    "œdème palpébral":                      "Gonflement des paupières",

    "visage gonflé":                        "Gonflement facial",
    "face gonflée":                         "Gonflement facial",
    "bouffissure du visage":                "Gonflement facial",

    "joues gonflées":                       "Gonflement parotides",
    "parotides gonflées":                   "Gonflement parotides",
    "oreillons":                            "Gonflement parotides",

    "thyroïde gonflée":                     "Gonflement thyroïde",
    "goitre":                               "Gonflement thyroïde",
    "cou qui grossit":                      "Gonflement thyroïde",

    "visage qui grossit":                   "Grossissement du visage",
    "traits qui s'élargissent":             "Grossissement du visage",
    "faciès acromégalique":                 "Grossissement du visage",

    "seins chez l'homme":                   "Gynécomastie",
    "poitrine chez l'homme":                "Gynécomastie",
    "développement mammaire chez homme":    "Gynécomastie",
    "gynécomastie":                         "Gynécomastie",

    # ══ H ══════════════════════════════════════════════════════════════════════
    "mauvaise haleine":                     "Haleine désagréable",
    "halitose":                             "Haleine désagréable",
    "bouche qui sent mauvais":              "Haleine désagréable",

    "halos autour des lumières":            "Halos colorés",
    "halos colorés":                        "Halos colorés",
    "cercles autour des lumières":          "Halos colorés",

    "hyperlipidémie":                       "Hyperlipidémie",
    "graisses élevées dans le sang":        "Hyperlipidémie",
    "cholestérol et triglycérides élevés":  "Hyperlipidémie",

    "peau foncée en certains endroits":     "Hyperpigmentation",
    "taches brunes":                        "Hyperpigmentation",
    "mélanodermie":                         "Hyperpigmentation",

    "tension légèrement élevée":            "Hypertension légère",
    "pré-hypertension":                     "Hypertension légère",

    "hypertension portale":                 "Hypertension portale",
    "pression dans la veine porte":         "Hypertension portale",

    "hyperthyroïdie transitoire":           "Hyperthyroïdie transitoire",
    "thyroïde temporairement hyperactive":  "Hyperthyroïdie transitoire",

    "acide urique élevé":                   "Hyperuricémie",
    "uricémie élevée":                      "Hyperuricémie",
    "goutte dans le sang":                  "Hyperuricémie",

    "glycémie basse":                       "Hypoglycémie",
    "sucre bas":                            "Hypoglycémie",
    "malaise sucre":                        "Hypoglycémie",
    "crise hypoglycémique":                 "Hypoglycémie",

    "éruption violacée":                    "Héliotrope éruption",
    "rougeur violacée":                     "Héliotrope éruption",
    "coloration mauve des paupières":       "Héliotrope éruption",

    "saignement articulaire":               "Hémarthrose",
    "sang dans l'articulation":             "Hémarthrose",
    "articulation gonflée de sang":         "Hémarthrose",

    "saignement digestif":                  "Hémorragie digestive",
    "sang dans les intestins":              "Hémorragie digestive",
    "vomissement de sang":                  "Hémorragie digestive",

    "saignement dans l'oeil":               "Hémorragie rétinienne",
    "taches rouges dans la vue":            "Hémorragie rétinienne",

    # ══ I ══════════════════════════════════════════════════════════════════════
    "légèrement jaune":                     "Ictère léger",
    "petite jaunisse":                      "Ictère léger",
    "subictère":                            "Ictère léger",

    "impact psychologique":                 "Impact psychologique",
    "retentissement psychologique":         "Impact psychologique",
    "problèmes mentaux liés à la maladie":  "Impact psychologique",

    "inconfort":                            "Inconfort",
    "mal à l'aise":                         "Inconfort",
    "gêne":                                 "Inconfort",

    "incontinence":                         "Incontinence",
    "fuites urinaires":                     "Incontinence",
    "ne peut pas se retenir":               "Incontinence",
    "incontinence urinaire":                "Incontinence",

    "indigestion":                          "Indigestion",
    "digestion difficile":                  "Indigestion",
    "dyspepsie":                            "Indigestion",
    "estomac qui pèse":                     "Indigestion",

    "infection":                            "Infection",
    "microbe dans le corps":                "Infection",
    "fièvre infectieuse":                   "Infection",

    "infection secondaire":                 "Infection secondaire",
    "surinfection":                         "Infection secondaire",

    "malade souvent":                       "Infections fréquentes",
    "défenses immunitaires basses":         "Infections fréquentes",
    "immunodépression":                     "Infections fréquentes",

    "rechutes fréquentes":                  "Infections récurrentes",
    "infections qui reviennent":            "Infections récurrentes",

    "cystites à répétition":                "Infections urinaires",
    "infections urinaires répétées":        "Infections urinaires",
    "pyurie":                               "Infections urinaires",

    "rarement aller aux selles":            "Infrequence des selles",
    "selles peu fréquentes":                "Infrequence des selles",

    "yeux qui sont rouges":                 "Injection conjonctivale",
    "vaisseaux visibles dans les yeux":     "Injection conjonctivale",
    "hypérémie conjonctivale":              "Injection conjonctivale",

    "instabilité végétative":               "Instabilité végétative",
    "régulation autonome perturbée":        "Instabilité végétative",

    "irritabilité":                         "Irritabilité",
    "irritabilite":                         "Irritabilité",
    "nervosite":                            "Irritabilité",
    "nervosité":                            "Irritabilité",
    "impatience excessive":                 "Irritabilité",
    "humeur changeante":                    "Irritabilité",
    "hypersensibilité":                     "Irritabilité",
    "susceptibilité":                       "Irritabilité",

    "irritation cutanée":                   "Irritation cutanée",
    "peau irritée":                         "Irritation cutanée",

    "irritation génitale":                  "Irritation génitale",
    "organes génitaux irrités":             "Irritation génitale",

    "irritation throat":                    "Mal de gorge",
    "gorge irritée":                        "Mal de gorge",

    # ══ J ══════════════════════════════════════════════════════════════════════
    "jambe gonflée":                        "Jambe gonflée",
    "une seule jambe gonflée":              "Jambe gonflée",
    "oedème unilatéral de la jambe":        "Jambe gonflée",

    "pipi lent et faible":                  "Jet urinaire faible",
    "jet d'urine réduit":                   "Jet urinaire faible",
    "force d'urination réduite":            "Jet urinaire faible",

    # ══ K ══════════════════════════════════════════════════════════════════════
    "koïlonychie":                          "Koïlonychie",
    "ongles en cuillère":                   "Koïlonychie",
    "ongles concaves":                      "Koïlonychie",

    "kystes":                               "Kystes",
    "poches de liquide":                    "Kystes",
    "boules sous la peau":                  "Kystes",

    # ══ L ══════════════════════════════════════════════════════════════════════
    "lenteur des mouvements":               "Lenteur de mouvement",
    "bradykinésie":                         "Lenteur de mouvement",
    "mouvements au ralenti":                "Lenteur de mouvement",

    "leucodermie":                          "Leucodermie",
    "taches blanches de dépigmentation":    "Leucodermie",

    "lichénification":                      "Lichénification",
    "peau épaissie par grattage":           "Lichénification",

    "lignes ondulées dans la vision":       "Lignes ondulées",
    "distorsion des lignes":                "Lignes ondulées",
    "métamorphopsies":                      "Lignes ondulées",

    "limitation des activités":             "Limitation de l'activité",
    "ne peut plus faire ses activités":     "Limitation de l'activité",
    "handicap fonctionnel":                 "Limitation de l'activité",

    "calculs biliaires":                    "Lithiase biliaire",
    "pierres dans la vésicule":             "Lithiase biliaire",
    "vésicule pleine de calculs":           "Lithiase biliaire",
    "colique biliaire":                     "Lithiase biliaire",

    "lithiase rénale associée":             "Lithiase rénale associée",
    "calculs rénaux associés":              "Lithiase rénale associée",

    "ganglions dans plusieurs zones":       "Lymphadénopathie",
    "polyadénopathie":                      "Lymphadénopathie",
    "ganglions généralisés":                "Lymphadénopathie",

    "légèrement jaune":                     "Légère jaunisse",
    "ictère discret":                       "Légère jaunisse",
    "peau légèrement jaunâtre":             "Légère jaunisse",

    "lésions éparpillées":                  "Lésions dispersées",
    "boutons épars":                        "Lésions dispersées",

    "lésions en grappe":                    "Lésions groupées",
    "boutons groupés":                      "Lésions groupées",

    "lésions muqueuses":                    "Lésions muqueuses",
    "plaies sur les muqueuses":             "Lésions muqueuses",

    # ══ M ══════════════════════════════════════════════════════════════════════
    "malabsorption":                        "Malabsorption",
    "intestin n'absorbe pas bien":          "Malabsorption",
    "nutriments mal absorbés":              "Malabsorption",

    "malaise":                              "Malaise",
    "ne se sent pas bien":                  "Malaise",
    "indisposition":                        "Malaise",
    "sentiment de mal-être":                "Malaise",

    "maux de tete diffus":                  "Maux de tête",
    "céphalées diffuses":                   "Maux de tête",

    "maux de tête le matin":                "Maux de tête matinaux",
    "céphalées matinales":                  "Maux de tête matinaux",
    "réveil avec mal de tête":              "Maux de tête matinaux",

    "maux de tête sévère":                  "Céphalées sévères",
    "céphalée intense":                     "Céphalées sévères",
    "terrible céphalée":                    "Céphalées sévères",

    "se mordre la langue":                  "Morsure de langue",
    "blessure langue pendant crise":        "Morsure de langue",

    "mouvements automatiques":              "Mouvements automatiques",
    "automatismes":                         "Mouvements automatiques",
    "gestes inconscients":                  "Mouvements automatiques",

    "mucus dans les selles":                "Mucus dans les selles",
    "selles avec glaires":                  "Mucus dans les selles",
    "glaires rectales":                     "Mucus dans les selles",

    "myxoedème":                            "Myxœdème",
    "peau bouffie":                         "Myxœdème",
    "oedème blanc du visage":               "Myxœdème",

    "saignements menstruels abondants":     "Ménorragie",
    "règles très abondantes":              "Ménorragie",
    "hémorragie menstruelle":               "Ménorragie",
    "règles qui durent longtemps":          "Ménorragie",

    "voir les objets déformés":             "Métamorphopsies",
    "vision distordue":                     "Métamorphopsies",
    "objets ondulés":                       "Métamorphopsies",

    # ══ N ══════════════════════════════════════════════════════════════════════
    "nocturia":                             "Nocturia",
    "uriner la nuit":                       "Nocturia",
    "se lever la nuit pour uriner":         "Nocturia",

    "nodules":                              "Nodules",
    "petites bosses":                       "Nodules",
    "granulome":                            "Nodules",

    "nodules cutanés":                      "Nodules cutanés",
    "petites bosses sous la peau":          "Nodules cutanés",

    "nodules rhumatoïdes":                  "Nodules rhumatoïdes",
    "nodules autour des articulations":     "Nodules rhumatoïdes",

    "besoin de tenir le livre loin":        "Nécessité d'éloigner la lecture",
    "tenir la lecture à bout de bras":      "Nécessité d'éloigner la lecture",
    "presbytie":                            "Nécessité d'éloigner la lecture",

    "néphrite":                             "Néphrite lupique",
    "rein attaqué par lupus":               "Néphrite lupique",
    "atteinte rénale du lupus":             "Néphrite lupique",

    "névrite optique":                      "Névrite optique",
    "nerf optique enflammé":                "Névrite optique",
    "douleur et flou visuel":               "Névrite optique",

    "névrite périphérique":                 "Névrite périphérique",
    "nerfs périphériques atteints":         "Névrite périphérique",
    "neuropathie":                          "Névrite périphérique",

    # ══ O ══════════════════════════════════════════════════════════════════════
    "visage gonflé":                        "Oedème facial",
    "oedème du visage":                     "Oedème facial",
    "face bouffie":                         "Oedème facial",

    "une seule jambe gonflée":              "Oedème unilatéral",
    "œdème d'un seul côté":                "Oedème unilatéral",

    "urines peu abondantes":                "Oligurie",
    "peu d'urine":                          "Oligurie",
    "diurèse diminuée":                     "Oligurie",

    "ongles cassants":                      "Ongles cassants",
    "ongles qui se cassent":                "Ongles cassants",
    "ongles fragiles":                      "Ongles cassants",

    "orthopnée":                            "Orthopnée",
    "dormir assis":                         "Orthopnée",
    "ne peut pas dormir à plat":            "Orthopnée",

    "otalgie":                              "Otalgie",
    "oreille douloureuse":                  "Otalgie",
    "mal à l'oreille":                      "Otalgie",

    # ══ P ══════════════════════════════════════════════════════════════════════
    "papules":                              "Papules",
    "petits boutons solides":               "Papules",

    "papules de gottron":                   "Papules de Gottron",
    "papules gottron":                      "Papules de Gottron",
    "boutons sur les articulations des doigts": "Papules de Gottron",

    "paralysie":                            "Paralysie",
    "ne peut plus bouger":                  "Paralysie",
    "plégie":                               "Paralysie",

    "paralysie d'un côté du visage":        "Paralysie faciale",
    "visage qui s'affaisse":                "Paralysie faciale",
    "bouche de travers":                    "Paralysie faciale",
    "prosopoplégie":                        "Paralysie faciale",

    "paresthésies":                         "Paresthésies",
    "sensations anormales":                 "Paresthésies",
    "picotements et fourmis":               "Paresthésies",

    "arrêt de respiration pendant sommeil": "Pauses respiratoires nocturnes",
    "apnée du sommeil":                     "Pauses respiratoires nocturnes",

    "peau grasse":                          "Peau grasse",
    "séborrhée":                            "Peau grasse",
    "visage gras":                          "Peau grasse",

    "peau épaissie":                        "Peau épaissie",
    "peau rugueuse et épaisse":             "Peau épaissie",
    "hyperkératose":                        "Peau épaissie",

    "ne plus entendre":                     "Perte d'audition",
    "surdité":                              "Perte d'audition",
    "troubles auditifs":                    "Perte d'audition",
    "hypoacousie":                          "Perte d'audition",

    "perte d'autonomie":                    "Perte d'autonomie",
    "ne peut plus se débrouiller seul":     "Perte d'autonomie",
    "dépendance":                           "Perte d'autonomie",

    "ne peut plus sentir":                  "Perte d'odorat",
    "anosmie":                              "Perte d'odorat",
    "odorat diminué":                       "Perte d'odorat",

    "ne plus voir le contraste":            "Perte de contraste",
    "vision sans contraste":                "Perte de contraste",

    "ne peut plus goûter":                  "Perte de goût",
    "agueusie":                             "Perte de goût",
    "goût diminué":                         "Perte de goût",

    "réflexes absents":                     "Perte de réflexes",
    "aréflexie":                            "Perte de réflexes",

    "engourdi":                             "Perte de sensibilité",
    "perte de sensibilité":                 "Perte de sensibilité",
    "anesthésie partielle":                 "Perte de sensibilité",

    "perte de vision":                      "Perte de vision",
    "baisse d'acuité visuelle":             "Perte de vision",
    "ne voit plus":                         "Perte de vision",

    "vision nocturne mauvaise":             "Perte de vision nocturne",
    "cécité nocturne":                      "Perte de vision nocturne",
    "héméralopie":                          "Perte de vision nocturne",

    "vision qui baisse":                    "Perte de vision progressive",
    "baisse progressive de la vue":         "Perte de vision progressive",

    "vision du côté réduite":               "Perte de vision périphérique",
    "vision tunnel":                        "Perte de vision périphérique",
    "champ visuel réduit":                  "Perte de vision périphérique",

    "voix disparaît":                       "Perte de voix",
    "aphonie":                              "Perte de voix",
    "voix éteinte":                         "Perte de voix",

    "petites bosses ombiliquées":           "Petites bosses ombiliquées",
    "molluscum contagiosum":                "Petites bosses ombiliquées",
    "perles cutanées":                      "Petites bosses ombiliquées",

    "phlébite":                             "Phlébite",
    "veine douloureuse":                    "Phlébite",
    "thrombose veineuse superficielle":     "Phlébite",

    "sensible au soleil":                   "Photosensibilité",
    "brûlure au soleil facile":             "Photosensibilité",
    "intolérance au soleil":                "Photosensibilité",

    "poils en excès":                       "Pilosité excessive",
    "hirsutisme":                           "Pilosité excessive",
    "poils anormaux":                       "Pilosité excessive",

    "plaies qui ne guérissent pas":         "Plaies lentes à cicatriser",
    "cicatrisation lente":                  "Plaies lentes à cicatriser",
    "plaies qui s'infectent":               "Plaies lentes à cicatriser",

    "plaques rouges":                       "Plaques rouges",
    "rougeurs en plaques":                  "Plaques rouges",

    "pleurite":                             "Pleurite",
    "douleur pleurale":                     "Pleurite",
    "inflammation de la plèvre":            "Pleurite",

    "plisser les yeux":                     "Plissement des yeux",
    "yeux qui se plissent":                 "Plissement des yeux",

    "points blancs":                        "Points blancs",
    "taches blanches":                      "Points blancs",
    "leucoplasie":                          "Points blancs",

    "points noirs":                         "Points noirs",
    "comédons":                             "Points noirs",

    "poliose":                              "Poliose",
    "cheveux blancs localisés":             "Poliose",
    "mèche blanche":                        "Poliose",

    "grossir rapidement":                   "Prise de poids rapide",
    "prise de poids rapide":                "Prise de poids rapide",
    "kilos qui arrivent vite":              "Prise de poids rapide",

    "protéines dans les urines":            "Protéinurie",
    "albumine dans les urines":             "Protéinurie",
    "urines mousseuses":                    "Protéinurie",

    "prurit léger":                         "Prurit léger",
    "légèrement ça gratte":                 "Prurit léger",

    "yeux qui grattent":                    "Prurit oculaire",
    "démangeaisons oculaires":              "Prurit oculaire",
    "yeux irrités qui grattent":            "Prurit oculaire",

    "très forte démangeaison":              "Prurit sévère",
    "ça gratte énormément":                 "Prurit sévère",
    "prurit intense":                       "Prurit sévère",

    "urètre qui gratte":                    "Prurit urétral",
    "démangeaisons urètre":                 "Prurit urétral",

    "pulsation dans la tête":               "Pulsation céphalique",
    "tête qui bat":                         "Pulsation céphalique",
    "migraine pulsatile":                   "Pulsation céphalique",
    "céphalée pulsatile":                   "Pulsation céphalique",

    # ══ R ══════════════════════════════════════════════════════════════════════
    "ralentissement cognitif":              "Ralentissement intellectuel",
    "réflexion plus lente":                 "Ralentissement intellectuel",
    "bradypsychie":                         "Ralentissement intellectuel",

    "rash":                                 "Rash",
    "éruption rapide":                      "Rash",
    "rougeurs cutanées":                    "Rash",

    "rash photosensible":                   "Rash photosensible",
    "éruption au soleil":                   "Rash photosensible",
    "réaction cutanée à la lumière":        "Rash photosensible",

    "rash rose":                            "Rash rose",
    "petites taches roses":                 "Rash rose",
    "roséole":                              "Rash rose",

    "phénomène de raynaud":                 "Raynaud",
    "doigts qui blanchissent":              "Raynaud",
    "doigts blancs puis bleus au froid":    "Raynaud",

    "mobilité réduite":                     "Restriction de mobilité",
    "raideur articulaire":                  "Restriction de mobilité",
    "limitation des mouvements":            "Restriction de mobilité",

    "rigidité":                             "Rigidité",
    "muscles rigides":                      "Rigidité",
    "hypertonie":                           "Rigidité",
    "corps raide":                          "Rigidité",

    "rot":                                  "Rot",
    "éructation":                           "Rot",
    "rots fréquents":                       "Rot",

    "rougeur":                              "Rougeur",
    "érythème":                             "Rougeur",

    "peau rouge":                           "Rougeur cutanée",
    "rougissement cutané":                  "Rougeur cutanée",

    "joues rouges":                         "Rougeur du visage",
    "visage rouge":                         "Rougeur du visage",
    "flush":                                "Rougeur du visage",

    "gorge rouge":                          "Rougeur pharyngée",
    "pharynx rouge":                        "Rougeur pharyngée",
    "oropharynx érythémateux":              "Rougeur pharyngée",

    "peau rugueuse":                        "Rugosité cutanée",
    "peau rêche":                           "Rugosité cutanée",

    "rechutes":                             "Récidives",
    "maladie qui revient":                  "Récidives",
    "poussées répétées":                    "Récidives",

    "réflexes abolies":                     "Réflexes abolis",
    "pas de réflexes":                      "Réflexes abolis",
    "aréflexie":                            "Réflexes abolis",

    "remontées acides":                     "Régurgitation acide",
    "brûlures remontantes":                 "Régurgitation acide",
    "pyrosis":                              "Régurgitation acide",

    "rétention d'urines":                   "Rétention urinaire",
    "ne peut pas vider la vessie":          "Rétention urinaire",
    "globe vésical":                        "Rétention urinaire",

    # ══ S ══════════════════════════════════════════════════════════════════════
    "saignement":                           "Saignement",
    "hémorragie":                           "Saignement",

    "saignement anormal":                   "Saignement anormal",
    "saignement sans raison":               "Saignement anormal",
    "hémorragie anormale":                  "Saignement anormal",

    "gencives qui saignent":                "Saignement des gencives",
    "saignement gingival":                  "Saignement des gencives",
    "gencives fragiles":                    "Saignement des gencives",

    "saignement des plaques":               "Saignement des plaques",
    "lésions qui saignent":                 "Saignement des plaques",

    "saignement digestif":                  "Saignement digestif",
    "sang dans les intestins":              "Saignement digestif",

    "saignement gencives":                  "Saignement gencives",

    "saignements entre les règles":         "Saignement intermenstruel",
    "spotting":                             "Saignement intermenstruel",
    "métrorragie":                          "Saignement intermenstruel",

    "saignements":                          "Saignements",
    "tendance hémorragique":                "Saignements",

    "saignements digestifs":                "Saignements digestifs",
    "sang dans les selles ou vomissements": "Saignements digestifs",

    "saignements du rectum":                "Saignements rectaux",
    "rectorragie":                          "Saignements rectaux",

    "salpingite":                           "Salpingite",
    "trompe infectée":                      "Salpingite",
    "infection des trompes":                "Salpingite",

    "sang dans les selles":                 "Sang dans les selles",
    "selles sanglantes":                    "Sang dans les selles",
    "rectorragie":                          "Sang dans les selles",

    "se sent vite rassasié":                "Satiété précoce",
    "rassasié rapidement":                  "Satiété précoce",
    "ne peut plus manger beaucoup":         "Satiété précoce",

    "scotome":                              "Scotome",
    "point aveugle":                        "Scotome",
    "trou dans la vision":                  "Scotome",

    "scotome central":                      "Scotome central",
    "trou au centre de la vision":          "Scotome central",

    "sécheresse oculaire":                  "Sécheresse oculaire",
    "yeux secs":                            "Sécheresse oculaire",
    "oeil qui brûle par sécheresse":        "Sécheresse oculaire",

    "sécheresse oculaire":                  "Secheresse oculaire",
    "oeil sec":                             "Secheresse oculaire",

    "envie de sel":                         "Sel craving",
    "besoin de sel":                        "Sel craving",
    "addiction au sel":                     "Sel craving",

    "selles dures":                         "Selles dures",
    "constipation avec selles dures":       "Selles dures",

    "selles décolorées":                    "Selles pâles",
    "selles blanches":                      "Selles pâles",
    "selles grises":                        "Selles pâles",
    "selles acholiques":                    "Selles pâles",

    "coeur qui s'accélère":                "Sensation d'accélération",
    "sensation de course cardiaque":        "Sensation d'accélération",

    "encore envie d'aller aux selles":      "Sensation d'évacuation incomplète",
    "faux besoins":                         "Sensation d'évacuation incomplète",
    "ténesme":                              "Sensation d'évacuation incomplète",

    "quelque chose qui bloque":             "Sensation de blocage",
    "blocage gorge ou intestin":            "Sensation de blocage",
    "dysphagie de blocage":                 "Sensation de blocage",

    "sensation de brûlure":                 "Sensation de brûlure",
    "brûlure interne":                      "Sensation de brûlure",

    "brûlure derrière le sternum":          "Sensation de brûlure rétrosternale",
    "pyrosis":                              "Sensation de brûlure rétrosternale",

    "corps étranger dans l'oeil":           "Sensation de corps étranger",
    "sable dans les yeux":                  "Sensation de corps étranger",

    "pression abdominale":                  "Sensation de pression",
    "pression dans la tête":                "Sensation de pression",
    "sensation de pesanteur":               "Sensation de pression",

    "estomac plein vite":                   "Sensation de satiété rapide",
    "rassasiement précoce":                 "Sensation de satiété rapide",

    "pas vidé après selles":                "Sensation vidange incomplète",
    "côlon pas vide":                       "Sensation vidange incomplète",

    "articulations sensibles":              "Sensibilité articulaire",
    "douleur à la pression":                "Sensibilité articulaire",

    "sensible aux odeurs":                  "Sensibilité aux odeurs",
    "osmophobie":                           "Sensibilité aux odeurs",
    "odeurs intolérables":                  "Sensibilité aux odeurs",

    "sensible au soleil":                   "Sensibilité solaire",
    "intolérance UV":                       "Sensibilité solaire",

    "sensible à la lumière":                "Sensibilité à la lumière",
    "lumière trop forte":                   "Sensibilité à la lumière",

    "douleur à la palpation":               "Sensibilité à la palpation",
    "zone sensible au toucher":             "Sensibilité à la palpation",
    "sensible quand on appuie":             "Sensibilité à la palpation",

    "sifflement respiratoire":              "Sifflement respiratoire",
    "wheezing":                             "Sifflement respiratoire",
    "bronchospasme":                        "Sifflement respiratoire",

    "soif":                                 "Soif",
    "avoir soif":                           "Soif",
    "sensation de soif":                    "Soif",

    "endormissement dans la journée":       "Somnolence diurne",
    "somnolent":                            "Somnolence diurne",
    "envie de dormir le jour":              "Somnolence diurne",
    "hypersomnie":                          "Somnolence diurne",

    "souvent sans symptômes":               "Souvent asymptomatique",
    "silencieux cliniquement":              "Souvent asymptomatique",

    "spasticité":                           "Spasticité",
    "muscles contracturés":                 "Spasticité",
    "raideur spastique":                    "Spasticité",

    "squames":                              "Squames",
    "peau qui se desquame":                 "Squames",
    "pellicules cutanées":                  "Squames",

    "squames argentées":                    "Squames argentées",
    "plaques blanches argentées":           "Squames argentées",
    "psoriasis squameux":                   "Squames argentées",

    "stridor":                              "Stridor inspiratoire",
    "bruit en inspirant":                   "Stridor inspiratoire",
    "croup":                                "Stridor inspiratoire",

    "sueurs":                               "Sueurs",
    "transpiration":                        "Sueurs",

    "sueurs froides":                       "Sueurs froides",
    "transpiration froide":                 "Sueurs froides",
    "moiteur froide":                       "Sueurs froides",

    "suintement":                           "Suintement",
    "plaie qui suinte":                     "Suintement",
    "écoulement de plaie":                  "Suintement",

    "syndrome côlon irritable":             "Syndrome côlon irritable",
    "colon irritable":                      "Syndrome côlon irritable",
    "intestin irritable":                   "Syndrome côlon irritable",

    "bouche sèche":                         "Sécheresse buccale",
    "xérostomie":                           "Sécheresse buccale",
    "manque de salive":                     "Sécheresse buccale",

    "peau sèche":                           "Sécheresse cutanée",
    "xérose":                               "Sécheresse cutanée",
    "peau qui tire":                        "Sécheresse cutanée",

    "yeux secs":                            "Sécheresse oculaire",
    "kératoconjonctivite sèche":            "Sécheresse oculaire",

    "sécrétions nasales épaisses":          "Sécrétions nasales épaisses",
    "mucus nasal épais":                    "Sécrétions nasales épaisses",
    "nez avec mucus épais":                 "Sécrétions nasales épaisses",

    # ══ T ══════════════════════════════════════════════════════════════════════
    "taches blanches gorge":                "Taches blanches pharyngées",
    "plaques blanches sur la gorge":        "Taches blanches pharyngées",
    "exsudat pharyngé":                     "Taches blanches pharyngées",

    "taches de koplik":                     "Taches de Koplik",
    "petites taches blanches dans la bouche": "Taches de Koplik",
    "signe de la rougeole":                 "Taches de Koplik",

    "taches sombres":                       "Taches sombres",
    "mélanodermie":                         "Taches sombres",
    "zones d'hyperpigmentation":            "Taches sombres",

    "tachycardie":                          "Tachycardie",
    "cœur rapide":                         "Tachycardie",
    "pouls rapide":                         "Tachycardie",
    "coeur qui bat vite":                   "Tachycardie",

    "tension dans la nuque":                "Tension nucale",
    "nuque tendue":                         "Tension nucale",
    "raideur de nuque":                     "Tension nucale",

    "thrombose":                            "Thrombose",
    "caillot de sang":                      "Thrombose",
    "coagulation anormale":                 "Thrombose",

    "toux d'aboiement":                     "Toux aboyante",
    "toux rauque":                          "Toux aboyante",
    "faux croup":                           "Toux aboyante",

    "toux chronique":                       "Toux chronique",
    "toux qui dure":                        "Toux chronique",
    "toux persistante":                     "Toux chronique",
    "toux de plus de 3 semaines":           "Toux chronique",

    "toux la nuit":                         "Toux nocturne",
    "réveil par la toux":                   "Toux nocturne",

    "toux qui ne part pas":                 "Toux persistante",
    "toux depuis des semaines":             "Toux persistante",

    "transpiration excessive":              "Transpiration excessive",
    "hyperhidrose":                         "Transpiration excessive",
    "beaucoup de sueur":                    "Transpiration excessive",

    "problème d'équilibre":                 "Trouble de l'équilibre",
    "chutes par manque d'équilibre":        "Trouble de l'équilibre",
    "ataxie vestibulaire":                  "Trouble de l'équilibre",

    "trouble de la marche":                 "Trouble de la marche",
    "marcher difficile":                    "Trouble de la marche",
    "démarche instable":                    "Trouble de la marche",

    "troubles cognitifs":                   "Troubles cognitifs",
    "problèmes de mémoire et attention":    "Troubles cognitifs",
    "déclin cognitif":                      "Troubles cognitifs",

    "troubles du sommeil":                  "Troubles du sommeil",
    "dormir mal":                           "Troubles du sommeil",
    "insomnie":                             "Troubles du sommeil",

    "troubles urinaires":                   "Troubles urinaires",
    "problèmes pour uriner":                "Troubles urinaires",

    # ══ U ══════════════════════════════════════════════════════════════════════
    "ulcère cornéen":                       "Ulcère cornéen",
    "plaie sur la cornée":                  "Ulcère cornéen",
    "kératite ulcéreuse":                   "Ulcère cornéen",

    "plaies aux pieds":                     "Ulcères des pieds",
    "plaies plantaires":                    "Ulcères des pieds",
    "mal perforant plantaire":              "Ulcères des pieds",

    "ulcérations":                          "Ulcérations",
    "plaies muqueuses":                     "Ulcérations",
    "érosions":                             "Ulcérations",

    "ulcérations muqueuses":                "Ulcérations muqueuses",
    "lésions sur les muqueuses":            "Ulcérations muqueuses",

    "urgence pour les selles":              "Urgence défécation",
    "ne peut pas se retenir pour déféquer": "Urgence défécation",
    "incontinence fécale":                  "Urgence défécation",

    "envie urgente d'uriner":               "Urgence urinaire",
    "urge incontinence":                    "Urgence urinaire",
    "ne peut pas retenir l'urine":          "Urgence urinaire",

    "urine foncée":                         "Urine foncée",
    "pipi brun ou foncé":                   "Urine foncée",
    "urines sombres":                       "Urine foncée",

    "urine trouble":                        "Urine trouble",
    "pipi trouble":                         "Urine trouble",
    "pyurie":                               "Urine trouble",
    "urines nuageuses":                     "Urine trouble",

    "urétrite":                             "Urétrite",
    "urètre infecté":                       "Urétrite",
    "inflammation urètre":                  "Urétrite",

    "muscles accessoires pour respirer":    "Utilisation muscles accessoires",
    "tirer les muscles du cou":             "Utilisation muscles accessoires",

    "uvéite":                               "Uvéite",
    "oeil enflammé":                        "Uvéite",
    "inflammation intérieure de l'oeil":    "Uvéite",

    # ══ V ══════════════════════════════════════════════════════════════════════
    "varices oesophagiennes":               "Varices oesophagiennes",
    "veines gonflées dans l'oesophage":     "Varices oesophagiennes",
    "hémorragie oesophagienne":             "Varices oesophagiennes",

    "vergetures":                           "Vergetures",
    "stries cutanées":                      "Vergetures",
    "striures de la peau":                  "Vergetures",

    "verrue génitale":                      "Verrue génitale",
    "condylome":                            "Verrue génitale",
    "végétations vénériennes":              "Verrue génitale",

    "verrue sous le pied":                  "Verrue plantaire douloureuse",
    "durillon douloureux":                  "Verrue plantaire douloureuse",
    "verruca plantaris":                    "Verrue plantaire douloureuse",

    "verrues génitales":                    "Verrues génitales",
    "condylomes acuminés":                  "Verrues génitales",

    "vertige brutal":                       "Vertige soudain",
    "vertige aigu":                         "Vertige soudain",
    "crise de vertiges":                    "Vertige soudain",

    "visage figé":                          "Visage inexpressif",
    "masque facial":                        "Visage inexpressif",
    "hypomimie":                            "Visage inexpressif",

    "visage rouge":                         "Visage rouge",
    "flush facial":                         "Visage rouge",
    "érythème facial":                      "Visage rouge",

    "floue au centre":                      "Vision centrale floue",
    "trou au centre du regard":             "Vision centrale floue",

    "voir déformé":                         "Vision déformée",
    "images tordues":                       "Vision déformée",

    "flou de loin":                         "Vision floue de loin",
    "myopie":                               "Vision floue de loin",

    "flou de près":                         "Vision floue de près",
    "hypermétropie":                        "Vision floue de près",
    "presbytie":                            "Vision floue de près",

    "vision légèrement floue":              "Vision floue légère",
    "brouillard visuel léger":              "Vision floue légère",

    "flou partout":                         "Vision floue à toutes distances",
    "acuité visuelle réduite":              "Vision floue à toutes distances",

    "vision jaune":                         "Vision jaunâtre",
    "xanthopsie":                           "Vision jaunâtre",

    "mal à voir la nuit":                   "Vision nocturne difficile",
    "nyctalopie":                           "Vision nocturne difficile",

    "vision de près floue":                 "Vision rapprochée floue",

    "vision en tunnel":                     "Vision tunnel",
    "champ visuel rétréci":                 "Vision tunnel",

    "voix grave":                           "Voix grave",
    "voix basse anormale":                  "Voix grave",

    "voix monocorde":                       "Voix monotone",
    "voix sans intonation":                 "Voix monotone",
    "prosodie absente":                     "Voix monotone",

    "voix rauque":                          "Voix rauque",
    "enrouement":                           "Voix rauque",
    "dysphonie":                            "Voix rauque",
    "hoarseness":                           "Voix rauque",

    "wheezing":                             "Wheezing",
    "sifflement bronchique":                "Wheezing",
    "asthme sifflant":                      "Wheezing",

    # ══ X ══════════════════════════════════════════════════════════════════════
    "xanthomes":                            "Xanthomes",
    "dépôts de graisses sous la peau":      "Xanthomes",
    "plaques graisseuses":                  "Xanthomes",

    "xanthomes tendineux":                  "Xanthomes tendineux",
    "dépôts graisseux sur les tendons":     "Xanthomes tendineux",

    # ══ Y ══════════════════════════════════════════════════════════════════════
    "yeux collants":                        "Yeux collants",
    "yeux collés le matin":                 "Yeux collants",
    "sécrétions oculaires":                 "Yeux collants",
    "chassie":                              "Yeux collants",

    "yeux plissés":                         "Yeux plissés",
    "fermer les yeux partiellement":        "Yeux plissés",
    "ptosis":                               "Yeux plissés",

    "yeux qui sortent":                     "Yeux saillants",
    "exophtalmie":                          "Yeux saillants",
    "yeux proéminents":                     "Yeux saillants",

    # ══ É/Œ ═══════════════════════════════════════════════════════════════════
    "éblouissement":                        "Éblouissement",
    "sensible aux lumières vives":          "Éblouissement",
    "photophobie légère":                   "Éblouissement",

    "écoulement":                           "Écoulement",
    "liquide qui sort":                     "Écoulement",
    "décharge":                             "Écoulement",

    "écoulement auriculaire":               "Écoulement auriculaire",
    "oreille qui coule":                    "Écoulement auriculaire",
    "otorrhée":                             "Écoulement auriculaire",

    "écoulement nasal":                     "Écoulement nasal",
    "nez qui coule":                        "Écoulement nasal",
    "rhinorrhée":                           "Écoulement nasal",

    "écoulement purulent":                  "Écoulement purulent",
    "pus qui s'écoule":                     "Écoulement purulent",
    "suppuration":                          "Écoulement purulent",

    "écriture micrographique":              "Écriture micrographique",
    "écriture qui rapetisse":               "Écriture micrographique",
    "petite écriture parkinson":            "Écriture micrographique",

    "éjaculation douloureuse":              "Éjaculation douloureuse",
    "douleur à l'orgasme":                  "Éjaculation douloureuse",

    "érosions":                             "Érosions",
    "plaies superficielles":                "Érosions",
    "lésions érodées":                      "Érosions",

    "éructations":                          "Éructations",
    "rots acides":                          "Éructations",

    "éruption":                             "Éruption",
    "rash cutané":                          "Éruption",

    "éruption chronique":                   "Éruption chronique",
    "plaques qui durent":                   "Éruption chronique",

    "éruption du visage":                   "Éruption malaire",
    "papillon sur le visage":               "Éruption malaire",
    "érythème malaire":                     "Éruption malaire",

    "éruption sur les paumes":              "Éruption palmoplantaire",
    "boutons sur les pieds et mains":       "Éruption palmoplantaire",

    "éruption qui gratte":                  "Éruption prurigineuse",
    "rash avec démangeaisons":              "Éruption prurigineuse",

    "éruption avec vésicules":              "Éruption vésiculaire",
    "boutons avec liquide":                 "Éruption vésiculaire",

    "érythromélalgie":                      "Érythromélalgie",
    "extrémités rouges et douloureuses":    "Érythromélalgie",

    "érythème":                             "Érythème",
    "rougeur cutanée":                      "Érythème",

    "érythème palmaire":                    "Érythème palmaire",
    "paumes rouges":                        "Érythème palmaire",

    "éternuements":                         "Éternuements",
    "éternuer souvent":                     "Éternuements",
    "éternuements fréquents":               "Éternuements",

    "évanouissement":                       "Évanouissement",
    "perte de conscience":                  "Évanouissement",
    "syncope":                              "Évanouissement",

    "évanouissements":                      "Évanouissements",
    "syncopes répétées":                    "Évanouissements",

    "oeil sec":                             "Œil sec",
    "sécheresse oculaire sévère":           "Œil sec",
}


def enrichir_model_manager():
    """Fusionne dans SYNONYMES_SYMPTOMES de model_manager.py."""
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "backend", "app", "ml", "model_manager.py"
    )
    with open(path, encoding="utf-8") as f:
        content = f.read()

    start_marker = "SYNONYMES_SYMPTOMES: dict[str, str] = {"
    end_marker = "\n}\n"
    start_idx = content.index(start_marker)
    end_idx = content.index(end_marker, start_idx) + len(end_marker)
    bloc = content[start_idx:end_idx]

    cles_existantes = set(re.findall(r'"([^"]+)"\s*:', bloc))
    nouveaux = {k: v for k, v in SYNONYMES_COMPLETS.items()
                if k.lower() not in {c.lower() for c in cles_existantes}}

    print(f"Synonymes existants : {len(cles_existantes)}")
    print(f"Nouveaux à ajouter  : {len(nouveaux)}")

    if not nouveaux:
        print("Rien à ajouter.")
        return

    ajout = "\n    # ── SYNONYMES COMPLETS — 444 symptômes couverts ─────────────────────────\n"
    for k, v in sorted(nouveaux.items()):
        pad = max(1, 48 - len(f'"{k}"'))
        ajout += f'    "{k}"{" " * pad}: "{v}",\n'

    nouveau_bloc = bloc.rstrip("}\n") + ajout + "}\n"
    new_content = content[:start_idx] + nouveau_bloc + content[end_idx:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ {len(nouveaux)} synonymes ajoutés dans model_manager.py")


if __name__ == "__main__":
    enrichir_model_manager()
