import { useState, useEffect, useMemo, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { registerNavigationGuard, unregisterNavigationGuard } from '../utils/navigationGuard';
import { useToast } from '../components/Toast';
import { useAuth } from '../context/AuthContext';
import { MedicalDisclaimerBanner } from '../components/MedicalDisclaimerBanner';
import {
  User, Activity, Stethoscope, Brain, CheckCircle,
  ArrowRight, ArrowLeft, X, AlertCircle, Thermometer,
  Heart, Wind, Droplet, Weight, Ruler, FlaskConical,
  Pill, Calendar, Plus, Lightbulb, RefreshCw, ClipboardList,
  UserCheck, Send, Search, UserX, UserPlus
} from 'lucide-react';

// ─── Types ────────────────────────────────────────────────────────────────────

interface PatientData {
  nom: string; prenoms: string; date_naissance: string;
  sexe: 'M' | 'F'; telephone?: string; email?: string;
  groupe_sanguin?: string;
}
interface Symptome {
  nom: string; severite: 'Légère' | 'Modérée' | 'Sévère';
  duree_jours: number; description?: string;
}
interface SignesVitaux {
  tension_systolique: number; tension_diastolique: number;
  frequence_cardiaque: number; frequence_respiratoire: number;
  temperature: number; saturation_o2: number; poids?: number; taille?: number;
}
interface Examen {
  type: 'CLINIQUE' | 'IMAGERIE' | 'BIOLOGIE' | 'ELECTROCARDIOGRAMME';
  nom: string; description?: string; resultats?: string;
  valeur_numerique?: number; unite_mesure?: string;
  date_examen?: string; isSuggested?: boolean;
}
interface Prediction { maladie: string; probabilite: number; }
interface AnalyseIA {
  maladie_predite: string; confiance: number;
  top_predictions: Prediction[];
}
interface MedicamentOrdonnance {
  nom: string; dosage: string; frequence: string;
  duree_jours: number; instructions?: string;
  forme?: string; voie_administration?: string; denomination_commune?: string; quantite?: number;
}
interface SuiviData {
  date_prochain_rdv: string; instructions_patient: string; notes_medecin: string;
}
interface PatientSearchResult {
  patient_id: number;
  nom: string;
  prenoms: string;
  sexe: string;
  date_naissance?: string;
  derniere_consultation_id?: number;
  derniere_consultation_statut?: string;
  derniere_consultation_date?: string;
  consultation_en_attente_id?: number;
  consultation_en_attente_medecin_id?: number | null;
}

// ─── Symptom autocomplete list ────────────────────────────────────────────────

// Symptômes exclusivement masculins (anatomie mâle)
const SYMPTOMES_HOMME_SEULEMENT = [
  "Douleur testiculaire",
  "Éjaculation douloureuse",
];

// Symptômes exclusivement féminins (anatomie femelle)
const SYMPTOMES_FEMME_SEULEMENT = [
  "Cervicite",
  "Dysparéunie",
  "Salpingite",
];

// Symptômes communs aux deux sexes (tous les autres)
const SYMPTOMES_COMMUNS = [
  "Adénopathie", "Agrandissement des mains pieds", "Albuminémie basse", "Alternance diarrhée-constipation",
  "Anémie", "Angioedème", "Anurie", "Anorexie", "Anxiété", "Apnée du sommeil", "Arthralgie", "Ascite",
  "Atrophie musculaire", "Aucun symptôme", "Aucun symptôme habituellement", "Aura",
  // Variantes / synonymes (normalisés côté backend vers le terme canonique)
  "Absence d'urine", "Acidité", "Ampoules",
  "Articulations douloureuses", "Avoir froid",
  "Bactériurie", "Ballonnements", "Ballonnement", "Barrel chest", "Battements irréguliers",
  "Besoin fréquent d'uriner", "Besoin impérieux de déféquer", "Boutons",
  "Blépharospasme", "Bleus faciles", "Bosse de bison", "Brûlures d'estomac", "Brûlures épigastriques",
  "Brûlures génitales", "Brûlures mictionnelles", "Bulles",
  "Candidose buccale", "Céphalée", "Céphalées", "Chaleur", "Chancre", "Cheveux cassants",
  "Choc", "Chute", "Cicatrices", "Cicatrisation lente", "Cloques", "Claudication",
  "Comédones", "Complications neuro", "Comportement inapproprié", "Confusion",
  "Congestion nasale", "Constipation", "Convulsions",
  "Courbatures", "Crachat", "Crachats", "Crampes", "Crampes abdominales", "Crampes musculaires",
  "Crachats purulents", "Crevasses", "Crise convulsive", "Cyanose",
  "Déformation progressive", "Délirium", "Démangeaisons", "Démangeaisons nasales", "Démangeaisons oculaires",
  "Démence", "Dépigmentation", "Dépôts lipidiques aux paupières", "Dépression", "Désorientaton",
  "Desquamation", "Désorientation", "Diarrhée", "Diarrhée sanguinolente",
  "Difficulté à avaler", "Difficulté à parler", "Difficulté à respirer",
  "Difficulté de lecture", "Difficulté nocturne", "Difficultés à avaler",
  "Difficultés à parler", "Difficultés à uriner", "Difficultés à déféquer",
  "Difficultés de langage", "Difficultés de vision",
  "Diplopie monoculaire", "Double vision",
  "Douleur", "Douleur à jeun", "Douleur à l'effort", "Douleur abdominale",
  "Douleur abdominale supérieure", "Douleur articulaire soudaine", "Douleur au bras",
  "Douleur au bras épaule", "Douleur au dos", "Douleur au flanc", "Douleur au rein",
  "Douleur au repas", "Douleur auriculaire", "Douleur calmée penché en avant",
  "Douleur colique intense", "Douleur costovertébrale", "Douleur dans le dos",
  "Douleur dans la poitrine", "Douleur épigastrique", "Douleur faciale",
  "Douleur irradiant dans le dos", "Douleur irradiant épaule droite", "Douleur irradiant vers aine",
  "Douleur lombaire", "Douleur neuropathique", "Douleur oculaire", "Douleur pelvienne",
  "Douleur pelvi-périnéale", "Douleur périnéale", "Douleur thoracique", "Douleur thoracique pleurétique",
  "Douleur thoracique sévère", "Douleur thyroïdienne", "Douleur à la mâchoire",
  "Douleurs abdominales", "Douleurs articulaires", "Douleurs dans les muscles",
  "Douleurs dans les os", "Douleurs musculaires", "Douleurs musculaires diffuses",
  "Douleurs osseuses", "Durcissement cutané", "Dysarthrie", "Dysphagie", "Dyspnée",
  "Dyspnée nocturne", "Dysurie",
  "Ecchymoses", "Écoulement", "Écoulement auriculaire", "Écoulement nasal", "Écoulement puriforme",
  "Écoulement urétral", "Écriture micrographique", "Efforts pour déféquer", "Encéphalopathie",
  "Engourdissement", "Engourdissement des pieds", "Enthésite", "Envie de vomir",
  "Envies fréquentes d'uriner", "Epistaxis", "Épistaxis", "Épuisement", "Étourdissements",
  "Érosions", "Éruption", "Éruption cutanée", "Éruption malaire", "Éruption prurigineuse", "Éruption vésiculaire",
  "Essoufflement", "Essoufflement soudain", "Éternuements", "Évanouissement", "Évanouissements",
  "Excroissance cutanée", "Expectorations",
  "Faiblesse", "Faiblesse ascendante", "Faiblesse musculaire", "Faiblesse soudaine",
  "Fasciculations", "Fatigue", "Fatigue intense", "Fatigue oculaire", "Fatigue post-critique",
  "Fièvre", "Fièvre élevée", "Fièvre intermittente", "Fistules", "Flotteurs", "Flux faible",
  "Fourmillements", "Fourmillements dans les membres", "Fourmillements dans les pieds",
  "Fragilité osseuse", "Fréquence urinaire", "Frissons", "Froid excessif", "Frottement péricardique",
  "Ganglions", "Ganglions gonflés", "Ganglions enflés", "Gaz", "Généralement sans symptôme",
  "Goût amer", "Goût métallique", "Arrière-goût métallique", "Gonflement",
  "Gonflement des membres inférieurs", "Gonflement des pieds", "Jambes gonflées",
  "Pieds gonflés", "Chevilles gonflées",
  "Gonflement des chevilles", "Gonflement des lèvres", "Gonflement d'un membre", "Gonflement parotides",
  "Gonflement thyroïde", "Grossissement du visage", "Groupées ou dispersées",
  "Haleine ammoniacale", "Haleine urémique", "Halos colorés", "Halos autour des lumières", "Hématémèse",
  "Hémarthrose", "Hématurie", "Hémoptysie", "Hémorragie digestive", "Hémorragie rétinienne",
  "Hépatomégalie", "Héliotrope éruption", "Histaminémie", "Hoarseness", "Hypercholangiite",
  "Hyperesthésie", "Hyperlipidémie", "Hyperpigmentation", "Hypertension", "Hypertension portale",
  "Hypoglycémie", "Hypotension",
  "Ictère", "Impact psychologique", "Incontinence", "Infection", "Infections", "Infections fréquentes",
  "Infections récurrentes", "Infections urinaires", "Infectiosus", "Infectiosus secondaires",
  "Infrequence des selles", "Injection conjonctivale", "Insomnie", "Intolérance à la chaleur", "Irritabilité",
  "Jaunisse",
  "Keratitis",
  "Larmoiement", "Lenteur de mouvement", "Lignes ondulées", "Lymphadénopathie",
  "Mal de gorge", "Mal de tête", "Malabsorption", "Malaise", "Malaise général",
  "Maux de tête", "Maux de tête diffus", "Maux de tête matinaux", "Maux de tête sévère", "Maux de tête sévères",
  "Méléna", "Mélæna", "Ménorragie", "Métamorphopsies", "Mucus dans les selles", "Myxoedème",
  "Mal au cœur", "Mal au ventre", "Mal de dos", "Mal de tête", "Mal à la tête",
  "Manque d'air", "Manque d'appétit", "Mauvaise haleine",
  "Nausée", "Nausées", "Nervosité", "Nez qui saigne", "Nocturia", "Nodules", "Nodules rhumatoïdes", "Nycturie",
  "Œdème pulmonaire", "Œdèmes", "Oedèmes", "Oligurie ou polyurie", "Oppression thoracique",
  "Orthopnée", "Otalgie",
  "Odeur d'urine dans l'haleine", "Odeur ammoniaque", "Oligurie", "Oublis fréquents",
  "Pâleur", "Palpitations", "Papules", "Papules de Gottron", "Paralysie", "Paresthésies",
  "Pas d'appétit", "Pas d'urine", "Pas uriner", "Peau décolorée", "Peau grise",
  "Peau qui démange", "Peau qui gratte", "Peau qui pèle", "Peau qui s'écaille",
  "Peau sèche", "Pérachie", "Perte d'appétit", "Perte d'audition", "Perte d'autonomie",
  "Perte de conscience", "Perte de goût", "Perte de mémoire", "Perte de poids", "Perte de réflexes",
  "Perte de vision", "Perte de vision progressive", "Perte de voix", "Perte d'odorat",
  "Petites bosses ombiliquées", "Pétéchies", "Phonophobie", "Photophobie", "Photosensibilité",
  "Plaques rouges squameuses", "Plissement des yeux", "Pollakiurie", "Pouls irrégulier",
  "Prise de poids", "Prise de poids rapide", "Production d'expectorations", "Protéinurie",
  "Prurit", "Prurit oculaire", "Prurit sévère", "Purpura", "Pustules",
  "Raideur matinale", "Ralentissement intellectuel", "Rash", "Rash photosensible", "Rash rose",
  "Raucité", "Raynaud", "Récidives", "Reflux", "Reflux acide", "Reflux gastro-esophagien",
  "Régurgitation", "Remontées acides", "Remontées gastriques",
  "Réflexes abolis", "Respiration sifflante", "Restriction de mobilité", "Rétention d'eau",
  "Rétention hydrique", "Rétention urinaire",
  "Rigidité", "Ronflement", "Ronflement fort", "Rot", "Rougeur", "Rougeur cutanée", "Rougeur oculaire", "Rougeur pharyngée",
  "Rougeurs cutanées", "Rythme cardiaque irrégulier",
  "Saignement", "Saignement des plaques", "Saignement digestif", "Saignements",
  "Saignements de nez", "Saignements prolongés", "Scotome central", "Sécheresse",
  "Sécheresse buccale", "Sécheresse cutanée", "Sécheresse oculaire", "Selles dures", "Selles pâles",
  "Sensation d'accélération", "Sensation de ballonnement", "Sensation de blocage",
  "Sensation de pressure", "Sensation de satiété rapide", "Sensation vidange incomplète",
  "Sensibilité à la lumière", "Sensibilité à la palpation", "Soif excessive",
  "Somnolence diurne", "Souvent asymptomatique", "Spasticité", "Splénomégalie",
  "Stridor inspiratoire", "Sueurs", "Sueurs froides", "Sueurs nocturnes", "Syncope",
  "Sang dans les selles", "Sang dans les urines", "Selles liquides", "Selles noires",
  "Selles sanglantes", "Se lever la nuit pour uriner", "Soif anormale", "Soif intense", "Souffle court",
  "Taches blanches", "Taches blanches pharyngées", "Taches blanches sur la peau",
  "Taches de Koplik", "Taches sombres",
  "Tachycardie", "Teint grisâtre", "Teint pâle", "Teint pâle grisâtre",
  "Température élevée", "Tension artérielle élevée", "Tension haute",
  "Télangiectasies", "Thrombose", "Tophi", "Transpiration nocturne", "Tremblements des mains",
  "Trous de mémoire",
  "Toux", "Toux aboyante", "Toux avec expectorations", "Toux nocturne", "Toux persistante",
  "Toux productive", "Toux sèche", "Tremblements", "Trouble de l'équilibre", "Trouble du sommeil",
  "Troubles cognitifs", "Troubles du sommeil",
  "Ulcère cornéen", "Ulcérations", "Ulcères buccaux", "Ulcères des pieds",
  "Urétrite", "Urgence urinaire", "Urination fréquente", "Uriner la nuit", "Uriner souvent",
  "Urine abondante", "Urine avec mousse", "Urine écumeuse", "Urine foncée", "Urine mousseuse",
  "Urine rare", "Urine trouble", "Urines foncées", "Urines rouges", "Urines roses",
  "Uvéite", "Uveite",
  "Varices œsophagiennes", "Vergetures", "Verrue génitale", "Verrue plantaire douloureuse",
  "Verrues génitales", "Vertige", "Vertiges", "Vésicules", "Visage rouge",
  "Vision centrale floue", "Vision floue", "Vision floue à toutes distances",
  "Vision floue de loin", "Vision floue de près", "Vision jaunâtre", "Vision rapprochée floue",
  "Vision tunnel", "Voix rauque", "Vomissement", "Vomissements", "Vomir", "Vomir du sang",
  "Vue brouillée", "Voir double", "Voir flou", "Ventre gonflé", "Ventre qui fait mal",
  "Xanthomes", "Yeux jaunes", "Yeux qui brûlent", "Yeux qui coulent",
  "Yeux qui piquent", "Yeux rouges", "Yeux saillants",
];

function getSymptomesDisponibles(sexe: 'M' | 'F'): string[] {
  if (sexe === 'M') return [...SYMPTOMES_COMMUNS, ...SYMPTOMES_HOMME_SEULEMENT].sort((a, b) => a.localeCompare(b, 'fr'));
  if (sexe === 'F') return [...SYMPTOMES_COMMUNS, ...SYMPTOMES_FEMME_SEULEMENT].sort((a, b) => a.localeCompare(b, 'fr'));
  return [...SYMPTOMES_COMMUNS, ...SYMPTOMES_HOMME_SEULEMENT, ...SYMPTOMES_FEMME_SEULEMENT].sort((a, b) => a.localeCompare(b, 'fr'));
}

const ALL_SYMPTOMES_SET = new Set([...SYMPTOMES_COMMUNS, ...SYMPTOMES_HOMME_SEULEMENT, ...SYMPTOMES_FEMME_SEULEMENT]);

// ─── Exam suggestion engine ───────────────────────────────────────────────────

// Liste des examens de laboratoire supportés par le modèle ML (63 features - incluant 3 nouveaux examens TB)
const EXAMENS_SUPPORTES = [
  // Hématologie
  'Hémoglobine',
  'Hématocrite',
  'Globules Rouges',
  'Globules Blancs',
  'Neutrophiles',
  'Lymphocytes',
  'Monocytes',
  'Eosinophiles',
  'Basophiles',
  'Plaquettes',
  'VGM',
  'CCMH',
  // Métabolisme Glucidique
  'Glucose',
  'Glucose à jeun',
  'Glucose post-prandial',
  'HbA1c',
  // Lipides
  'Cholestérol total',
  'Cholestérol HDL',
  'Cholestérol LDL',
  'Triglycérides',
  'Acide urique',
  // Fonction Rénale
  'Créatinine',
  'Urée',
  'TFG',
  // Électrolytes
  'Sodium',
  'Potassium',
  'Chlore',
  'Calcium',
  'Phosphore',
  'Magnésium',
  // Fonction Hépatique
  'ALT/SGPT',
  'AST/SGOT',
  'Bilirubine totale',
  'Bilirubine conjuguée',
  'Bilirubine non-conjuguée',
  'Phosphatase alcaline',
  'GGT',
  'Albumine',
  'Protéine totale',
  'Globulines',
  'Ratio A/G',
  // Marqueurs Cardiaques
  'CK',
  'Myoglobine',
  'Troponine',
  'BNP',
  'ProBNP',
  // Coagulation
  'PT/INR',
  'aPTT',
  'TT',
  'Fibrinogène',
  // Marqueurs Inflammatoires
  'CRP',
  'ESR',
  // Autres
  'PSA',
  // Microbiologie (Nouveaux examens pour Tuberculose)
  'BAAR (résultat)',
  'Culture Mycobactéries (résultat)',
  'Test Xpert MTB/RIF (résultat)',
];

const EXAM_DEFAULTS: Record<string, { valeur_numerique?: number; unite_mesure?: string }> = {
  'Hémoglobine':                      { valeur_numerique: 13.0,  unite_mesure: 'g/dL'   },
  'CRP':                              { valeur_numerique: 5.0,   unite_mesure: 'mg/L'   },
  'ALT/SGPT':                         { valeur_numerique: 35,    unite_mesure: 'U/L'   },
  'AST/SGOT':                         { valeur_numerique: 35,    unite_mesure: 'U/L'   },
  'Bilirubine totale':                { valeur_numerique: 10.0,  unite_mesure: 'mg/dL' },
  'Glucose à jeun':                   { valeur_numerique: 5.0,   unite_mesure: 'mmol/L' },
  'HbA1c':                            { valeur_numerique: 5.5,   unite_mesure: '%'      },
  'Troponine':                        { valeur_numerique: 0.01,  unite_mesure: 'ng/mL'  },
  'Créatinine':                       { valeur_numerique: 80,    unite_mesure: 'µmol/L' },
  'Urée':                             { valeur_numerique: 30,    unite_mesure: 'mg/dL' },
  'Fer':                              { valeur_numerique: 50,    unite_mesure: 'µg/L'   },
  'Ferritine':                        { valeur_numerique: 100,   unite_mesure: 'ng/mL'   },
  'ESR':                              { valeur_numerique: 10,    unite_mesure: 'mm/h' },
  'Globules Blancs':                  { valeur_numerique: 7.0,   unite_mesure: 'K/µL' },
  'Lymphocytes':                      { valeur_numerique: 30,    unite_mesure: '%' },
  'Neutrophiles':                     { valeur_numerique: 60,    unite_mesure: '%' },
  'Globules Rouges':                  { valeur_numerique: 4.5,   unite_mesure: 'M/µL' },
  'Plaquettes':                       { valeur_numerique: 250,   unite_mesure: 'K/µL' },
  'Albumine':                         { valeur_numerique: 4.0,   unite_mesure: 'g/dL' },
  'CK':                               { valeur_numerique: 100,   unite_mesure: 'U/L' },
  'Myoglobine':                       { valeur_numerique: 50,    unite_mesure: 'ng/mL' },
  'BNP':                              { valeur_numerique: 100,   unite_mesure: 'pg/mL' },
  'TFG':                              { valeur_numerique: 90,    unite_mesure: 'mL/min/1.73m²' },
  'Potassium':                        { valeur_numerique: 4.0,   unite_mesure: 'mEq/L' },
  'Hématocrite':                      { valeur_numerique: 40,    unite_mesure: '%' },
  'VGM':                              { valeur_numerique: 90,    unite_mesure: 'fL' },
  'Sodium':                           { valeur_numerique: 140,   unite_mesure: 'mEq/L' },
  'Cholestérol total':                { valeur_numerique: 200,   unite_mesure: 'mg/dL' },
  // Nouveaux examens microbiologiques pour Tuberculose
  'BAAR (résultat)':                  { valeur_numerique: 0,     unite_mesure: 'résultat' }, // 0=NÉGATIF, 1=POSITIF
  'Culture Mycobactéries (résultat)': { valeur_numerique: 0,     unite_mesure: 'résultat' }, // 0=NÉGATIF, 1=POSITIF
  'Test Xpert MTB/RIF (résultat)':    { valeur_numerique: 0,     unite_mesure: 'résultat' }, // 0=NÉGATIF, 1=POSITIF
};

const UNITES_EXAMEN = [
  'g/dL', 'g/L', 'mg/L', 'mg/dL', 'µmol/L', 'mmol/L', 'UI/L', 'U/L', 
  'ng/mL', 'µg/L', 'K/µL', 'M/µL', 'fL', '%', 'mm', 'mm/h', 'titre', 
  'résultat', 'rapport', 'positif/négatif', 'indices', 'copies/mL', 
  'pg/mL', 'sec', 'mEq/L', 'mL/min/1.73m²', 'resp/min', 'Autre'
];

function suggestExams(predictions: Prediction[]): Examen[] {
  const today = new Date().toISOString().split('T')[0];
  const added = new Set<string>();
  const list: Examen[] = [];

  const add = (e: Omit<Examen, 'isSuggested'>) => {
    if (!added.has(e.nom)) {
      added.add(e.nom);
      const def = EXAM_DEFAULTS[e.nom] || {};
      list.push({
        ...e,
        resultats: '',
        isSuggested: true,
        date_examen: today,
        valeur_numerique: def.valeur_numerique,
        unite_mesure: def.unite_mesure ?? '',
      });
    }
  };

  add({ type: 'BIOLOGIE', nom: 'Hémoglobine', description: 'Bilan sanguin de base' });
  add({ type: 'BIOLOGIE', nom: 'CRP', description: 'Marqueur inflammatoire' });

  predictions.slice(0, 3).forEach(({ maladie }) => {
    const m = maladie.toLowerCase();
    if (m.includes('malaria') || m.includes('paludisme'))
      { // Paludisme : utiliser marqueurs inflammatoires et hématologie
        add({ type: 'BIOLOGIE', nom: 'Globules Rouges', description: 'Anémie hémolytique' });
        add({ type: 'BIOLOGIE', nom: 'Plaquettes', description: 'Thrombocytopénie' });
        add({ type: 'BIOLOGIE', nom: 'Bilirubine totale', description: 'Hémolyse' }); }
    if (m.includes('tuberc') || m.includes(' tb'))
      { // Tuberculose : marqueurs inflammatoires, hématologie et tests microbiologiques
        add({ type: 'BIOLOGIE', nom: 'BAAR (résultat)', description: 'Test de référence pour TB' });
        add({ type: 'BIOLOGIE', nom: 'ESR', description: 'Vitesse de sédimentation élevée' });
        add({ type: 'BIOLOGIE', nom: 'Globules Blancs', description: 'Numération leucocytaire' });
        add({ type: 'BIOLOGIE', nom: 'Lymphocytes', description: 'Lymphocytose relative' });
        add({ type: 'BIOLOGIE', nom: 'Albumine', description: 'Dénutrition' });
        add({ type: 'BIOLOGIE', nom: 'Culture Mycobactéries (résultat)', description: 'Confirmation TB' }); }
    if (m.includes('typhoid') || m.includes('typhoïde') || m.includes('salmonel'))
      { // Typhoïde : marqueurs hépatiques et inflammatoires
        add({ type: 'BIOLOGIE', nom: 'ALT/SGPT', description: 'Atteinte hépatique' });
        add({ type: 'BIOLOGIE', nom: 'AST/SGOT', description: 'Atteinte hépatique' });
        add({ type: 'BIOLOGIE', nom: 'Globules Blancs', description: 'Leucopénie' }); }
    if (m.includes('hepat'))
      { add({ type: 'BIOLOGIE', nom: 'ALT/SGPT', description: 'Transaminase hépatique' });
        add({ type: 'BIOLOGIE', nom: 'AST/SGOT', description: 'Transaminase hépatique' });
        add({ type: 'BIOLOGIE', nom: 'Bilirubine totale', description: 'Évaluation ictère' });
        add({ type: 'BIOLOGIE', nom: 'Albumine', description: 'Fonction de synthèse' }); }
    if (m.includes('diabet') || m.includes('glucose') || m.includes('glyc'))
      { add({ type: 'BIOLOGIE', nom: 'Glucose à jeun', description: 'Glucose sanguin' });
        add({ type: 'BIOLOGIE', nom: 'HbA1c', description: 'Hémoglobine glyquée' });
        add({ type: 'BIOLOGIE', nom: 'Créatinine', description: 'Fonction rénale' });
        add({ type: 'BIOLOGIE', nom: 'Cholestérol total', description: 'Bilan lipidique' }); }
    if (m.includes('cardia') || m.includes('heart') || m.includes('coeur') || m.includes('infarct'))
      { // Cardiaque : marqueurs cardiaques
        add({ type: 'BIOLOGIE', nom: 'Troponine', description: 'Nécrose myocardique' });
        add({ type: 'BIOLOGIE', nom: 'CK', description: 'Créatine kinase' });
        add({ type: 'BIOLOGIE', nom: 'Myoglobine', description: 'Marqueur précoce' });
        add({ type: 'BIOLOGIE', nom: 'BNP', description: 'Insuffisance cardiaque' }); }
    if (m.includes('renal') || m.includes('rein') || m.includes('nephro') || m.includes('kidney'))
      { add({ type: 'BIOLOGIE', nom: 'Créatinine', description: 'Fonction rénale' });
        add({ type: 'BIOLOGIE', nom: 'Urée', description: 'Fonction rénale' });
        add({ type: 'BIOLOGIE', nom: 'TFG', description: 'Filtration glomérulaire' });
        add({ type: 'BIOLOGIE', nom: 'Potassium', description: 'Équilibre électrolytique' }); }
    if (m.includes('anemi') || m.includes('anémie'))
      { add({ type: 'BIOLOGIE', nom: 'Hémoglobine', description: 'Taux d\'hémoglobine' });
        add({ type: 'BIOLOGIE', nom: 'Hématocrite', description: 'Volume globulaire' });
        add({ type: 'BIOLOGIE', nom: 'VGM', description: 'Volume globulaire moyen' });
        add({ type: 'BIOLOGIE', nom: 'Fer', description: 'Carence en fer' });
        add({ type: 'BIOLOGIE', nom: 'Ferritine', description: 'Réserves en fer' }); }
    if (m.includes('cholera') || m.includes('diarrhee') || m.includes('diarrhée') || m.includes('gastro'))
      { // Gastro : électrolytes et fonction rénale
        add({ type: 'BIOLOGIE', nom: 'Sodium', description: 'Déshydratation' });
        add({ type: 'BIOLOGIE', nom: 'Potassium', description: 'Hypokaliémie' });
        add({ type: 'BIOLOGIE', nom: 'Créatinine', description: 'Insuffisance rénale aiguë' });
        add({ type: 'BIOLOGIE', nom: 'Urée', description: 'Déshydratation' }); }
    if (m.includes('pneumon') || m.includes('pulmon') || m.includes('bronch'))
      { // Pneumonie/Bronchite : marqueurs inflammatoires
        add({ type: 'BIOLOGIE', nom: 'CRP', description: 'Inflammation' });
        add({ type: 'BIOLOGIE', nom: 'Globules Blancs', description: 'Infection' });
        add({ type: 'BIOLOGIE', nom: 'Neutrophiles', description: 'Infection bactérienne' }); }
  });

  return list.slice(0, 6);
}

// ─── Component ────────────────────────────────────────────────────────────────

const TOTAL = 8;

const steps = [
  { num: 1, title: 'Patient',            icon: User,          role: 'Accueil' },
  { num: 2, title: 'Symptômes & Vitaux', icon: Activity,      role: 'Infirmier' },
  { num: 3, title: 'Analyse IA',         icon: Brain,         role: 'IA',      special: true },
  { num: 4, title: 'Examens',            icon: FlaskConical,  role: 'Médecin' },
  { num: 5, title: 'Diagnostic IA',      icon: Brain,         role: 'IA',      special: true },
  { num: 6, title: 'Validation',         icon: CheckCircle,   role: 'Médecin' },
  { num: 7, title: 'Ordonnance',         icon: Pill,          role: 'Médecin' },
  { num: 8, title: 'Suivi',             icon: Calendar,      role: 'Médecin' },
];

const roleBadge = (role: string, special?: boolean) => (
  <span style={{
    display: 'inline-block', padding: '3px 10px',
    background: special ? 'linear-gradient(135deg,#4F46E5,#7C3AED)' : '#F3F4F6',
    color: special ? '#fff' : '#6B7280',
    borderRadius: '12px', fontSize: '11px', fontWeight: 600
  }}>
    {special ? '🤖 ' : ''}{role}
  </span>
);

const VitalBadge = ({ label, value, unit, icon: Icon, alert }: any) => (
  <div style={{ padding: '12px 16px', background: alert ? '#FEF3C7' : '#F9FAFB', borderRadius: '10px', border: `1px solid ${alert ? '#FCD34D' : '#E5E7EB'}` }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
      <Icon size={12} />{label}
    </div>
    <div style={{ fontWeight: 700, fontSize: '16px', color: alert ? '#92400E' : '#1F2937' }}>
      {value} <span style={{ fontSize: '11px', fontWeight: 400, color: '#9CA3AF' }}>{unit}</span>
    </div>
  </div>
);


// Helper function to include authorization token
const apiFetch = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('sp_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };
  return fetch(url, { ...options, headers });
};

export default function ConsultationWorkflow() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();

  const reprendreId = searchParams.get('reprendre');
  const directPatientId = searchParams.get('patientId'); // Nouveau: patient depuis dossier
  const isInfirmier = user?.role === 'infirmier';
  const isAdmin = user?.role === 'admin';
  const isMedecin = user?.role === 'medecin';

  // Bloquer l'accès aux administrateurs dès le montage
  useEffect(() => {
    if (isAdmin) {
      navigate('/dashboard');
    }
  }, [isAdmin, navigate]);

  // doctorMode: 'reprendre' = patient trouvé avec consultation en attente
  //             'nouveau'   = patient introuvable ou sans consultation en attente
  type DoctorMode = 'reprendre' | 'nouveau';
  const [doctorPhase, setDoctorPhase] = useState<'search' | 'workflow'>(
    isMedecin && !reprendreId && !directPatientId ? 'search' : 'workflow'
  );
  const [doctorMode, setDoctorMode] = useState<DoctorMode | null>(
    reprendreId ? 'reprendre' : directPatientId ? 'nouveau' : null
  );

  // Phase de recherche patient pour l'infirmier
  const [infirmierPhase, setInfirmierPhase] = useState<'search' | 'workflow'>(
    isInfirmier && !reprendreId && !directPatientId ? 'search' : 'workflow'
  );

  // Consultation active (peut venir de l'URL ou de la recherche)
  const [activeConsultationId, setActiveConsultationId] = useState<number | null>(
    reprendreId ? parseInt(reprendreId) : null
  );

  const isReprendre = doctorMode === 'reprendre';

  // Flag pour éviter l'exécution multiple du useEffect de chargement patient
  const patientLoadedRef = useRef(false);

  // Recherche patient (médecin)
  const [patientSearchQuery, setPatientSearchQuery] = useState('');
  const [patientSearchResults, setPatientSearchResults] = useState<PatientSearchResult[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectLoading, setSelectLoading] = useState(false);
  const [forceNewPatient, setForceNewPatient] = useState(false);


  const [manualAge, setManualAge] = useState<number | null>(null);

  // Quick-start : champs nom/prénoms éditables (découpe intelligente)
  const [quickStartNom, setQuickStartNom] = useState('');
  const [quickStartPrenoms, setQuickStartPrenoms] = useState('');
  const [quickStartAge, setQuickStartAge] = useState<number | ''>('');
  const [quickStartSexe, setQuickStartSexe] = useState<'M' | 'F'>('M');
  const [quickStartMotif, setQuickStartMotif] = useState('');

  const [step, setStep] = useState(reprendreId ? 0 : 1);
  const [loading, setLoading] = useState(false);
  const [draftConsultationId, setDraftConsultationId] = useState<number | null>(null);
  const [_createdPatientId, _setCreatedPatientId] = useState<number | null>(null);

  // État infirmier/admin
  const [medecinId, setMedecinId] = useState<number | null>(null);
  const [medecinSearch, setMedecinSearch] = useState('');
  const [medecins, setMedecins] = useState<{ id: number; nom: string; prenoms: string; specialite?: string }[]>([]);
  const [infirmierSubmitted, setInfirmierSubmitted] = useState(false);
  const [showDonneesModal, setShowDonneesModal] = useState(false);

  // ── Persistance de brouillon ───────────────────────────────────────────────
  const [showResumeModal, setShowResumeModal] = useState(false);
  const [savedDraft, setSavedDraft] = useState<any>(null);
  const [draftSavedAt, setDraftSavedAt] = useState<string | null>(null);
  const [pendingDrafts, setPendingDrafts] = useState<any[]>([]);
  const [needsMotif, setNeedsMotif] = useState(false);
  const [backendLoadComplete, setBackendLoadComplete] = useState(false);
  const autoSaveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Auto-affectation si le compte est un médecin
  useEffect(() => {
    if (user?.role === 'medecin' && user.medecin_id) {
      setMedecinId(user.medecin_id);
    }
  }, [user]);

  // State par étape
  const [patient, setPatient] = useState<PatientData>({ nom: '', prenoms: '', date_naissance: '', sexe: 'M', groupe_sanguin: '' });
  const [motif, setMotif] = useState('');
  const [symptomes, setSymptomes] = useState<Symptome[]>([]);
  const [openSymptomIdx, setOpenSymptomIdx] = useState<number | null>(null);
  const [vitaux, setVitaux] = useState<SignesVitaux>({ tension_systolique: 120, tension_diastolique: 80, frequence_cardiaque: 70, frequence_respiratoire: 16, temperature: 37.0, saturation_o2: 98 });
  const [analysePreliminaire, setAnalysePreliminaire] = useState<AnalyseIA | null>(null);
  const [examens, setExamens] = useState<Examen[]>([]);
  const [analyseFinale, setAnalyseFinale] = useState<AnalyseIA | null>(null);
  const [validationDecision, setValidationDecision] = useState<'confirme' | 'rejete' | null>(null);
  const [diagnosticFinal, setDiagnosticFinal] = useState('');
  const [diagnosticCorrection, setDiagnosticCorrection] = useState('');
  const [notesValidation, setNotesValidation] = useState('');
  const [ordonnance, setOrdonnance] = useState<MedicamentOrdonnance[]>([]);
  const [suivi, setSuivi] = useState<SuiviData>({ date_prochain_rdv: '', instructions_patient: '', notes_medecin: '' });
  const [catalogueMeds, setCatalogueMeds] = useState<Array<{
    id: number; nom_commercial: string; denomination_commune: string | null;
    dosage: string | null; frequence: string | null;
    duree_jours: number | null; quantite: number | null;
  }>>([]);
  const [catalogueLoading, setCatalogueLoading] = useState(false);

  // Navigation guard
  const [leaveModalOpen, setLeaveModalOpen] = useState(false);
  const [pendingNavTo, setPendingNavTo] = useState<string | number | null>(null);

  const filteredMedecins = medecins.filter(m => {
    const term = medecinSearch.toLowerCase();
    return (m.nom.toLowerCase().includes(term) || m.prenoms.toLowerCase().includes(term) || (m.specialite || '').toLowerCase().includes(term));
  });

  // ── helpers ────────────────────────────────────────────────────────────────

  const splitNameSmart = (query: string): { nom: string; prenoms: string } => {
    const parts = query.trim().split(/\s+/).filter(Boolean);
    if (parts.length === 0) return { nom: '', prenoms: '' };
    // Convention : premier mot = nom de famille, le reste = prénoms
    return { nom: parts[0].toUpperCase(), prenoms: parts.slice(1).join(' ') };
  };

  const isDirty = (isInfirmier ? infirmierPhase === 'workflow' : doctorPhase === 'workflow') && !infirmierSubmitted;

  // ── Helpers persistance ────────────────────────────────────────────────────
  const _getDraftKey = (): string | null => {
    if (isInfirmier) return 'sp_draft_infirmier';
    const id = activeConsultationId || draftConsultationId;
    return id ? `sp_draft_med_${id}` : null;
  };

  const clearDraftStorage = (consultationId?: number | null) => {
    // Annuler d'abord le timer d'auto-sauvegarde pour éviter qu'il re-sauvegarde après le clear
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current);
      autoSaveTimerRef.current = null;
    }
    localStorage.removeItem('sp_draft_infirmier');
    const id = consultationId ?? activeConsultationId ?? draftConsultationId;
    if (id) localStorage.removeItem(`sp_draft_med_${id}`);
    setDraftSavedAt(null);
  };

  // Réinitialise TOUT l'état du formulaire pour repartir d'une page vierge
  const resetFormState = (consultationId?: number | null) => {
    clearDraftStorage(consultationId);
    // Phases
    setInfirmierPhase('search');
    setDoctorPhase('search');
    setDoctorMode(null);
    // Identifiants
    setDraftConsultationId(null);
    _setCreatedPatientId(null);
    setActiveConsultationId(null);
    // Formulaire patient
    setPatient({ nom: '', prenoms: '', date_naissance: '', sexe: 'M', groupe_sanguin: '' });
    setMotif('');
    setMedecinId(null);
    // Quick-start fields
    setQuickStartNom('');
    setQuickStartPrenoms('');
    setQuickStartAge('');
    setQuickStartSexe('M');
    setQuickStartMotif('');
    // Données cliniques
    setSymptomes([]);
    setVitaux({ tension_systolique: 120, tension_diastolique: 80, frequence_cardiaque: 70, frequence_respiratoire: 16, temperature: 37.0, saturation_o2: 98 });
    setExamens([]);
    setAnalysePreliminaire(null);
    setAnalyseFinale(null);
    setDiagnosticFinal('');
    setDiagnosticCorrection('');
    setOrdonnance([]);
    setSuivi({ date_prochain_rdv: '', instructions_patient: '', notes_medecin: '' });
    // État de soumission
    setInfirmierSubmitted(false);
    setStep(1);
    // Recherche
    setPatientSearchQuery('');
    setPatientSearchResults([]);
    setHasSearched(false);
    setForceNewPatient(false);
    // Modals et brouillons
    setShowResumeModal(false);
    setSavedDraft(null);
    setPendingDrafts([]);
  };

  const formatDraftAge = (iso: string) => {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'à l\'instant';
    if (mins < 60) return `il y a ${mins} min`;
    const h = Math.floor(mins / 60);
    if (h < 24) return `il y a ${h}h`;
    return `il y a ${Math.floor(h / 24)} jour(s)`;
  };

  const STEP_LABELS: Record<number, string> = {
    1: 'Informations patient', 2: 'Symptômes & Signes Vitaux',
    3: 'Analyse IA préliminaire', 4: 'Examens médicaux',
    5: 'Résultats & Analyse finale', 6: 'Validation du diagnostic',
    7: 'Ordonnance', 8: 'Suivi du patient',
  };

  const applyDraft = (draft: any, mode: 'full' | 'medecin-only' = 'full') => {
    if (typeof draft.step === 'number') setStep(draft.step);
    if (mode === 'full') {
      if (isInfirmier) {
        if (draft.infirmierPhase) setInfirmierPhase(draft.infirmierPhase as 'search' | 'workflow');
        if (draft.consultationId) setDraftConsultationId(draft.consultationId);
      } else {
        if (draft.doctorPhase) setDoctorPhase(draft.doctorPhase as 'search' | 'workflow');
        if (draft.doctorMode) setDoctorMode(draft.doctorMode as 'reprendre' | 'nouveau');
        if (draft.consultationId) { setDraftConsultationId(draft.consultationId); setActiveConsultationId(draft.consultationId); }
      }
      if (draft.patient?.nom) setPatient(draft.patient);
      if (draft.motif !== undefined) setMotif(draft.motif);
      if (typeof draft.medecinId === 'number') setMedecinId(draft.medecinId);
      if (Array.isArray(draft.symptomes) && draft.symptomes.length > 0)
      setSymptomes(draft.symptomes.filter((s: any) => ALL_SYMPTOMES_SET.has(s.nom)));
      if (draft.vitaux) setVitaux(v => ({ ...v, ...draft.vitaux }));
      if (draft.analysePreliminaire) setAnalysePreliminaire(draft.analysePreliminaire);
    }
    if (Array.isArray(draft.examens) && draft.examens.length > 0) setExamens(draft.examens);
    if (draft.analyseFinale) setAnalyseFinale(draft.analyseFinale);
    if (draft.validationDecision) setValidationDecision(draft.validationDecision);
    if (draft.diagnosticFinal) setDiagnosticFinal(draft.diagnosticFinal);
    if (draft.diagnosticCorrection) setDiagnosticCorrection(draft.diagnosticCorrection);
    if (draft.notesValidation) setNotesValidation(draft.notesValidation);
    if (Array.isArray(draft.ordonnance) && draft.ordonnance.length > 0) setOrdonnance(draft.ordonnance);
    if (draft.suivi) setSuivi(v => ({ ...v, ...draft.suivi }));
    setShowResumeModal(false);
    setSavedDraft(null);
    const draftMotif = draft.motif?.trim() ?? '';
    if (draftMotif === '' || draftMotif === 'Consultation médicale') {
      setNeedsMotif(true);
    }
    showToast('Consultation restaurée — vous reprenez là où vous en étiez', 'success');
  };

  const safeNavigate = (to: string) => {
    if (isDirty) { setPendingNavTo(to); setLeaveModalOpen(true); }
    else navigate(to);
  };

  const isQuickStart = !patient.date_naissance || patient.date_naissance === '';

  const buildPayload = (withExams: boolean) => {
    const computedAge = patient.date_naissance
      ? Math.floor((Date.now() - new Date(patient.date_naissance).getTime()) / (365.25 * 24 * 3600 * 1000))
      : null;
    const age = manualAge ?? computedAge ?? 40;
    const sevMap: Record<string, string> = { 'Légère': 'LEGER', 'Modérée': 'MODERE', 'Sévère': 'SEVERE' };
    const sevOrd: Record<string, number> = { 'Légère': 1, 'Modérée': 2, 'Sévère': 3 };
    const maxSev = symptomes.length > 0
      ? symptomes.reduce((m, s) => sevOrd[s.severite] > sevOrd[m] ? s.severite : m, symptomes[0].severite)
      : 'Modérée';
    const maxDuree = symptomes.length > 0 ? Math.max(...symptomes.map(s => s.duree_jours || 1)) : 7;
    const imc = vitaux.poids && vitaux.taille ? vitaux.poids / ((vitaux.taille / 100) ** 2) : 22.0;

    return {
      age, duree_symptomes_jours: maxDuree, sexe: patient.sexe,
      severite: sevMap[maxSev] || 'MODERE',
      vitaux: {
        tension_systolique: vitaux.tension_systolique, tension_diastolique: vitaux.tension_diastolique,
        frequence_cardiaque: vitaux.frequence_cardiaque, frequence_respiratoire: vitaux.frequence_respiratoire,
        temperature: vitaux.temperature, saturation_oxygene: vitaux.saturation_o2, imc,
      },
      symptomes: symptomes.map(s => s.nom).filter(n => n.trim()),
      examens: withExams
        ? examens.filter(e => e.valeur_numerique != null && e.nom.trim()).map(e => ({ nom: e.nom, valeur_numerique: e.valeur_numerique, unite_mesure: e.unite_mesure || '' }))
        : [],
    };
  };

  const callIA = async (withExams: boolean): Promise<AnalyseIA> => {
    const res = await apiFetch('http://localhost:8000/api/ml/predict-direct', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(buildPayload(withExams)),
    });
    if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || `Erreur ${res.status}`); }
    const d = await res.json();
    const alts: Prediction[] = (d.diagnostics_alternatifs || []).map((a: any) => ({ maladie: a.diagnostic, probabilite: a.confiance }));
    return {
      maladie_predite: d.diagnostic_propose, confiance: d.confiance,
      top_predictions: [{ maladie: d.diagnostic_propose, probabilite: d.confiance }, ...alts],
    };
  };

  // ── Effects ────────────────────────────────────────────────────────────────

  // Bloquer le scroll de la page quand la modal données est ouverte
  useEffect(() => {
    document.body.style.overflow = showDonneesModal ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [showDonneesModal]);

  // Infirmier : charger la liste des médecins
  useEffect(() => {
    if (!isInfirmier) return;
    apiFetch('http://localhost:8000/api/analytics/personnel/disponible')
      .then(r => r.json())
      .then(d => setMedecins((d.medecins?.liste || []).map((m: any) => ({ id: m.id, nom: m.nom, prenoms: m.prenoms, specialite: m.specialite }))))
      .catch(() => {});
  }, [isInfirmier]);

  // Médecin : charger automatiquement le patient depuis le dossier (directPatientId)
  useEffect(() => {
    if (!directPatientId || !isMedecin || patientLoadedRef.current) return;
    
    // Marquer comme chargé pour éviter les exécutions multiples
    patientLoadedRef.current = true;
    
    const loadPatientAndCreateConsultation = async () => {
      try {
        setLoading(true);
        // Charger les données du patient
        const patientRes = await apiFetch(`http://localhost:8000/api/patients/${directPatientId}`);
        if (!patientRes.ok) throw new Error('Patient non trouvé');
        
        const patientData = await patientRes.json();
        
        // Pré-remplir les données du patient
        setPatient({
          nom: patientData.nom,
          prenoms: patientData.prenoms,
          date_naissance: patientData.date_naissance || '',
          sexe: (patientData.sexe as 'M' | 'F') || 'M',
          telephone: patientData.telephone,
          email: patientData.email,
          groupe_sanguin: patientData.groupe_sanguin || ''
        });
        
        // Créer une nouvelle consultation pour ce patient EXISTANT
        const consultationRes = await apiFetch('http://localhost:8000/api/consultations/init', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            patient_id: patientData.patient_id,  // IMPORTANT: Utiliser le patient existant
            patient: {
              nom: patientData.nom,
              prenoms: patientData.prenoms,
              date_naissance: patientData.date_naissance || '',
              sexe: patientData.sexe || 'M'
            },
            motif: 'Consultation médicale',
            medecin_id: user?.medecin_id
          })
        });
        
        if (!consultationRes.ok) throw new Error('Erreur création consultation');
        
        const consultationData = await consultationRes.json();
        setActiveConsultationId(consultationData.consultation_id);
        
        // Aller directement à l'étape 2 (symptômes et signes vitaux)
        setStep(2);
        setDoctorPhase('workflow');
        
        showToast(`Nouvelle consultation créée pour ${patientData.prenoms} ${patientData.nom}`, 'success');
      } catch (error) {
        showToast('Erreur lors du chargement du patient', 'error');
        navigate('/consultations');
      } finally {
        setLoading(false);
      }
    };
    
    loadPatientAndCreateConsultation();
  }, [directPatientId, isMedecin, user?.medecin_id]);

  // Infirmier/Admin : pré-remplir le formulaire avec les données du patient connu (sans créer de consultation)
  useEffect(() => {
    if (!directPatientId || isMedecin || patientLoadedRef.current) return;
    patientLoadedRef.current = true;

    apiFetch(`http://localhost:8000/api/patients/${directPatientId}`)
      .then(r => r.json())
      .then(pd => {
        setPatient({
          nom: pd.nom || '',
          prenoms: pd.prenoms || '',
          date_naissance: pd.date_naissance || '',
          sexe: (pd.sexe as 'M' | 'F') || 'M',
          telephone: pd.telephone || '',
          email: pd.email || '',
          groupe_sanguin: pd.groupe_sanguin || '',
        });
      })
      .catch(() => {});
  }, [directPatientId, isMedecin]);

  // Charger une consultation à reprendre (depuis URL ou depuis la recherche)
  useEffect(() => {
    if (!activeConsultationId) return;
    // Ne pas charger si on vient de créer une consultation depuis directPatientId
    if (directPatientId) return;
    
    apiFetch(`http://localhost:8000/api/consultations/${activeConsultationId}/donnees-resume`)
      .then(r => r.json())
      .then(d => {
        if (user?.role === 'medecin' && user.medecin_id && d.medecin_id && user.medecin_id !== d.medecin_id) {
          showToast("Désolé, vous n'êtes pas le médecin affecté à cette consultation.", 'error');
          navigate('/consultations');
          return;
        }
        if (d.patient) setPatient(p => ({ ...p, ...d.patient }));
        if (d.motif) setMotif(d.motif);
        if (d.symptomes?.length) {
          const rev: Record<string, string> = { LEGER: 'Légère', MODERE: 'Modérée', SEVERE: 'Sévère' };
          setSymptomes(
            d.symptomes
              .filter((s: any) => ALL_SYMPTOMES_SET.has(s.nom))
              .map((s: any) => ({ nom: s.nom, severite: rev[s.severite] || 'Modérée', duree_jours: s.duree_jours, description: s.description || '' }))
          );
        }
        if (d.signes_vitaux) setVitaux(v => ({ ...v, ...d.signes_vitaux }));
        if (d.analyse_preliminaire) {
          setAnalysePreliminaire(d.analyse_preliminaire);
          setExamens(suggestExams(d.analyse_preliminaire.top_predictions || []));
        }
        if (isInfirmier) {
          // Infirmier reprend son brouillon → symptômes/vitaux
          setDraftConsultationId(activeConsultationId);
          if (d.medecin_id) setMedecinId(d.medecin_id);
          setStep(2);
        } else {
          // Médecin : détermine le mode selon les données sauvegardées en base
          if (d.symptomes?.length > 0) {
            // Symptômes sauvegardés par l'infirmier → dossier préparé, reprendre à Analyse IA
            setDoctorMode('reprendre');
            setStep(d.analyse_preliminaire ? 4 : 3);
          } else {
            // Aucun symptôme en base → consultation créée directement par le médecin
            setDoctorMode('nouveau');
            setDraftConsultationId(activeConsultationId);
            setStep(2);
          }
        }
        setDoctorPhase('workflow');
        setBackendLoadComplete(true);
      })
      .catch(() => showToast('Impossible de charger la consultation', 'error'));
  }, [activeConsultationId]);

  // ── Recherche patient (médecin) — auto-search avec debounce ──────────────
  useEffect(() => {
    const q = patientSearchQuery.trim();
    if (!q) {
      setPatientSearchResults([]);
      setHasSearched(false);
      setSearchLoading(false);
      setForceNewPatient(false);
      return;
    }
    setForceNewPatient(false);
    setSearchLoading(true);
    const timer = setTimeout(async () => {
      try {
        const res = await apiFetch(`http://localhost:8000/api/patients/search?q=${encodeURIComponent(q)}`);
        if (!res.ok) throw new Error();
        const data: PatientSearchResult[] = await res.json();
        
        // Dédupliquer les résultats par patient_id (garder le premier de chaque patient)
        const uniquePatients = data.reduce((acc: PatientSearchResult[], current) => {
          const exists = acc.find(p => p.patient_id === current.patient_id);
          if (!exists) {
            acc.push(current);
          }
          return acc;
        }, []);
        
        setPatientSearchResults(uniquePatients);
        setHasSearched(true);
      } catch {
        setHasSearched(true);
      } finally {
        setSearchLoading(false);
      }
    }, 500);
    return () => { clearTimeout(timer); setSearchLoading(false); };
  }, [patientSearchQuery]);


  // Découpe nom/prénoms automatique quand patient introuvable ou création forcée
  useEffect(() => {
    if (hasSearched && (patientSearchResults.length === 0 || forceNewPatient) && patientSearchQuery.trim()) {
      const { nom, prenoms } = splitNameSmart(patientSearchQuery);
      setQuickStartNom(nom);
      setQuickStartPrenoms(prenoms);
    }
  }, [hasSearched, patientSearchResults.length, patientSearchQuery, forceNewPatient]);

  // Garde de navigation — fermeture/actualisation navigateur + liens sidebar
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (isDirty) { e.preventDefault(); e.returnValue = ''; }
    };
    window.addEventListener('beforeunload', handler);

    if (isDirty) {
      registerNavigationGuard((path) => {
        setPendingNavTo(path);
        setLeaveModalOpen(true);
      });
    } else {
      unregisterNavigationGuard();
    }

    return () => {
      window.removeEventListener('beforeunload', handler);
      unregisterNavigationGuard();
    };
  }, [isDirty]);

  // ── Détection brouillon au montage ────────────────────────────────────────
  useEffect(() => {
    // Infirmier sans reprendreId : afficher le brouillon inline (comme le médecin, sans modal bloquant)
    if (isInfirmier && !reprendreId && !directPatientId) {
      const raw = localStorage.getItem('sp_draft_infirmier');
      if (raw) {
        try {
          const draft = JSON.parse(raw);
          const age = Date.now() - new Date(draft.savedAt).getTime();
          if (age < 48 * 3600 * 1000 && draft.patient?.nom) {
            setPendingDrafts([{ ...draft, _key: 'sp_draft_infirmier' }]);
          } else {
            localStorage.removeItem('sp_draft_infirmier');
          }
        } catch { localStorage.removeItem('sp_draft_infirmier'); }
      }
    }
    // Médecin sans reprendreId : collecter TOUS les brouillons valides (sans modal bloquant)
    if (isMedecin && !reprendreId && !directPatientId) {
      const found: any[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (!key?.startsWith('sp_draft_med_')) continue;
        const raw = localStorage.getItem(key);
        if (!raw) continue;
        try {
          const draft = JSON.parse(raw);
          const age = Date.now() - new Date(draft.savedAt).getTime();
          if (age < 48 * 3600 * 1000 && draft.patient?.nom) {
            found.push({ ...draft, _key: key });
          } else {
            localStorage.removeItem(key);
          }
        } catch { localStorage.removeItem(key); }
      }
      // Trier du plus récent au plus ancien
      found.sort((a, b) => new Date(b.savedAt).getTime() - new Date(a.savedAt).getTime());
      if (found.length > 0) setPendingDrafts(found);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Après chargement backend (médecin reprendre) : proposer brouillon local ──
  useEffect(() => {
    if (!backendLoadComplete || !isMedecin || !activeConsultationId) return;
    const key = `sp_draft_med_${activeConsultationId}`;
    const raw = localStorage.getItem(key);
    if (!raw) return;
    try {
      const draft = JSON.parse(raw);
      const age = Date.now() - new Date(draft.savedAt).getTime();
      if (age < 48 * 3600 * 1000 && draft.step > 3) {
        setSavedDraft({ ...draft, _medecin_only: true });
        setShowResumeModal(true);
      } else {
        localStorage.removeItem(key);
      }
    } catch { localStorage.removeItem(key); }
  }, [backendLoadComplete]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Auto-save (debounce 1.5 s) ────────────────────────────────────────────
  useEffect(() => {
    const isActive = (isInfirmier ? infirmierPhase === 'workflow' : doctorPhase === 'workflow') && !infirmierSubmitted;
    if (!isActive) return;
    const id = activeConsultationId || draftConsultationId;
    const key = isInfirmier ? 'sp_draft_infirmier' : (id ? `sp_draft_med_${id}` : null);
    if (!key) return;
    if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);
    autoSaveTimerRef.current = setTimeout(() => {
      try {
        localStorage.setItem(key, JSON.stringify({
          role: user?.role, step, consultationId: id,
          infirmierPhase, doctorPhase, doctorMode,
          patient, motif, medecinId,
          symptomes, vitaux, analysePreliminaire,
          examens, analyseFinale,
          validationDecision, diagnosticFinal, diagnosticCorrection, notesValidation,
          ordonnance, suivi,
          savedAt: new Date().toISOString(),
        }));
        setDraftSavedAt(new Date().toISOString());
      } catch { /* localStorage plein */ }
    }, 1500);
    return () => { if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current); };
  }, [isInfirmier, infirmierPhase, doctorPhase, infirmierSubmitted, step, patient, motif, medecinId,
      draftConsultationId, activeConsultationId, symptomes, vitaux, analysePreliminaire,
      examens, analyseFinale, validationDecision, diagnosticFinal, diagnosticCorrection,
      notesValidation, ordonnance, suivi, doctorMode, user?.role]); // eslint-disable-line react-hooks/exhaustive-deps

  // Médecin sélectionne un patient trouvé
  const handleSelectPatient = async (result: PatientSearchResult) => {
    setShowResumeModal(false);
    setSavedDraft(null);
    setSelectLoading(true);
    try {
      if (result.consultation_en_attente_id) {
        // Consultation préparée par infirmier → reprendre au step 4
        setActiveConsultationId(result.consultation_en_attente_id);
        setDraftConsultationId(result.consultation_en_attente_id);
        setDoctorMode('reprendre');
        // L'effect sur activeConsultationId va charger les données
      } else {
        // Patient connu mais pas de consultation en attente → nouveau dossier
        setPatient({ nom: result.nom, prenoms: result.prenoms, date_naissance: result.date_naissance || '', sexe: (result.sexe as 'M' | 'F') || 'M', groupe_sanguin: '' });
        const res = await apiFetch('http://localhost:8000/api/consultations/init', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            patient_id: result.patient_id,  // IMPORTANT: Envoyer le patient_id pour éviter les doublons
            patient: { 
              nom: result.nom, 
              prenoms: result.prenoms, 
              date_naissance: result.date_naissance || '', 
              sexe: result.sexe || 'M' 
            }, 
            motif: 'Consultation médicale', 
            medecin_id: user?.medecin_id 
          }),
        });
        if (!res.ok) throw new Error('Erreur création consultation');
        const data = await res.json();
        setDraftConsultationId(data.consultation_id);
        setDoctorMode('nouveau');
        setStep(2);
        setDoctorPhase('workflow');
      }
    } catch {
      showToast('Erreur lors du chargement du dossier', 'error');
    } finally {
      setSelectLoading(false);
    }
  };

  // Infirmier sélectionne un patient trouvé — crée le brouillon et va directement à l'étape 2
  const handleInfirmierSelectPatient = async (result: PatientSearchResult) => {
    setSelectLoading(true);
    try {
      setPatient({
        nom: result.nom,
        prenoms: result.prenoms,
        date_naissance: result.date_naissance || '',
        sexe: (result.sexe as 'M' | 'F') || 'M',
        groupe_sanguin: '',
      });
      setMotif('Consultation médicale');
      const res = await apiFetch('http://localhost:8000/api/consultations/init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: result.patient_id,
          patient: { nom: result.nom, prenoms: result.prenoms, date_naissance: result.date_naissance || '', sexe: result.sexe || 'M' },
          motif: 'Consultation médicale',
          medecin_id: medecinId,
        }),
      });
      if (!res.ok) throw new Error('Erreur création consultation');
      const data = await res.json();
      setDraftConsultationId(data.consultation_id);
      setInfirmierPhase('workflow');
      setStep(2);
    } catch {
      showToast('Erreur lors de la sélection du patient', 'error');
    } finally {
      setSelectLoading(false);
    }
  };

  // Infirmier — nouveau patient introuvable → va directement à l'étape 1 (formulaire complet)
  // La création en DB se fait au "Suivant" de l'étape 1 avec toutes les infos remplies
  const handleInfirmierQuickStart = () => {
    if (!medecinId) { showToast('Veuillez sélectionner un médecin avant de continuer', 'error'); return; }
    // Pré-remplir le nom depuis la recherche
    const nom = patientSearchQuery.trim().toUpperCase();
    setPatient({ nom, prenoms: '', date_naissance: '', sexe: 'M', groupe_sanguin: '' });
    setInfirmierPhase('workflow');
    setStep(1);
  };

  // Médecin démarre directement sans dossier trouvé — utilise les champs nom/prénoms saisis
  const handleQuickStart = async () => {
    setShowResumeModal(false);
    setSavedDraft(null);
    const nom = quickStartNom.trim();
    const prenoms = quickStartPrenoms.trim() || nom;
    if (!nom) { showToast('Veuillez renseigner au moins le nom du patient', 'error'); return; }
    const ageNum = typeof quickStartAge === 'number' && !isNaN(quickStartAge) ? quickStartAge : null;
    const date_naissance = ageNum !== null ? `${new Date().getFullYear() - ageNum}-01-01` : '';
    const sexe = quickStartSexe;
    setLoading(true);
    try {
      const res = await apiFetch('http://localhost:8000/api/consultations/init', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient: { nom, prenoms, date_naissance, sexe }, motif: quickStartMotif.trim() || 'Consultation médicale', medecin_id: user?.medecin_id }),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Erreur ${res.status}`);
      }
      const data = await res.json();
      setDraftConsultationId(data.consultation_id);
      setPatient({ nom, prenoms, date_naissance, sexe, groupe_sanguin: '' });
      setMotif(quickStartMotif.trim() || 'Consultation médicale');
      setDoctorMode('nouveau');
      setStep(2);
      setDoctorPhase('workflow');
    } catch (err: any) {
      console.error('handleQuickStart error:', err);
      showToast(err?.message || 'Erreur lors de la création du dossier', 'error');
    } finally {
      setLoading(false);
    }
  };

  // ── Step actions ───────────────────────────────────────────────────────────

  // Étape 1 → 2 : enregistre le patient + crée la consultation draft
  const handleNextStep = async () => {
    if (!patient.nom.trim() || !patient.prenoms.trim() || !patient.date_naissance || !motif.trim()) {
      showToast('Veuillez remplir les champs obligatoires (nom, prénoms, date de naissance, motif)', 'error');
      return;
    }
    // Brouillon déjà créé (retour en arrière) → juste avancer
    if (draftConsultationId) {
      setStep(2);
      return;
    }
    setLoading(true);
    try {
      const res = await apiFetch('http://localhost:8000/api/consultations/init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient,
          motif,
          medecin_id: medecinId,
          // Si on arrive depuis "Mes Patients", utiliser le patient existant (évite les doublons)
          ...(directPatientId ? { patient_id: parseInt(directPatientId) } : {}),
        }),
      });
      if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || 'Erreur serveur'); }
      const result = await res.json();
      setDraftConsultationId(result.consultation_id);
      showToast('Patient enregistré avec succès', 'success');
      setStep(2);
    } catch (e: any) {
      showToast(e.message || 'Erreur lors de l\'enregistrement du patient', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalysePreliminaire = async () => {
    setLoading(true);
    try {
      const result = await callIA(false);
      setAnalysePreliminaire(result);
      const suggestions = suggestExams(result.top_predictions);
      setExamens(suggestions);
      showToast('Analyse préliminaire effectuée — examens suggérés ci-dessous', 'success');
      // On reste sur l'étape 3 pour visualiser les résultats avant de passer aux examens
      // setStep(4);
    } catch (e: any) { showToast(e.message || 'Erreur IA', 'error'); }
    finally { setLoading(false); }
  };

  const handleAnalyseFinale = async () => {
    setLoading(true);
    try {
      const result = await callIA(true);
      setAnalyseFinale(result);
      setValidationDecision(null); setDiagnosticFinal(''); setDiagnosticCorrection('');
      showToast('Diagnostic IA final généré', 'success');
      setStep(6);
    } catch (e: any) { showToast(e.message || 'Erreur IA', 'error'); }
    finally { setLoading(false); }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const finalDiag = validationDecision === 'rejete' ? diagnosticCorrection : diagnosticFinal;
      const res = await apiFetch('http://localhost:8000/api/consultations/workflow', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient, motif, symptomes, signes_vitaux: vitaux, examens,
          analyse_preliminaire: analysePreliminaire, analyse_finale: analyseFinale,
          diagnostic_final: finalDiag, validation_type: validationDecision,
          notes_validation: notesValidation, ordonnance, suivi,
          consultation_id: draftConsultationId,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Erreur serveur ${res.status}`);
      }
      const data = await res.json();
      clearDraftStorage(draftConsultationId);
      showToast('Consultation clôturée avec succès !', 'success');
      setTimeout(() => navigate(`/dossier-patient/${data.patient_id}`), 1500);
    } catch (e: any) {
      showToast(e.message || 'Erreur lors de l\'enregistrement', 'error');
    } finally { setLoading(false); }
  };

  // Infirmier ou Admin soumet les étapes 1-3 et notifie le médecin
  const handleSubmitInfirmier = async () => {
    if (!medecinId) { showToast('Veuillez sélectionner un médecin', 'error'); return; }
    setLoading(true);
    try {
      const res = await apiFetch('http://localhost:8000/api/consultations/workflow-partiel', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient, motif, symptomes, signes_vitaux: vitaux, analyse_preliminaire: analysePreliminaire, medecin_id: medecinId, consultation_id: draftConsultationId }),
      });
      if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || 'Erreur serveur'); }
      // Effacer le draft AVANT setInfirmierSubmitted pour éviter toute re-sauvegarde
      clearDraftStorage(draftConsultationId);
      setInfirmierSubmitted(true);
      showToast('Consultation envoyée au médecin avec succès', 'success');
    } catch (e: any) { showToast(e.message || 'Erreur', 'error'); }
    finally { setLoading(false); }
  };

  // Médecin finalise une consultation reprise (étapes 4-9)
  const handleSubmitComplet = async () => {
    setLoading(true);
    try {
      const finalDiag = validationDecision === 'rejete' ? diagnosticCorrection : diagnosticFinal;
      const res = await apiFetch(`http://localhost:8000/api/consultations/${activeConsultationId}/workflow-complet`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ examens, analyse_finale: analyseFinale, diagnostic_final: finalDiag, validation_type: validationDecision, notes_validation: notesValidation, ordonnance, suivi }),
      });
      if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || 'Erreur serveur'); }
      const result = await res.json();
      clearDraftStorage(activeConsultationId);
      showToast('Consultation clôturée avec succès !', 'success');
      setTimeout(() => navigate(`/patients/${result.patient_id}/dossier`), 1500);
    } catch (e: any) { showToast(e.message || 'Erreur', 'error'); }
    finally { setLoading(false); }
  };

  // ── Symptômes helpers ──────────────────────────────────────────────────────
  const invalidateAnalyse = () => {
    if (analysePreliminaire) { setAnalysePreliminaire(null); setExamens([]); }
    if (analyseFinale)       { setAnalyseFinale(null); }
  };

  const addSymptome = () => { invalidateAnalyse(); setSymptomes([...symptomes, { nom: '', severite: 'Modérée', duree_jours: 1 }]); };
  const removeSymptome = (i: number) => { invalidateAnalyse(); setSymptomes(symptomes.filter((_, idx) => idx !== i)); };
  const editSymptome = (i: number, f: keyof Symptome, v: any) => {
    if (f === 'nom' && typeof v === 'string' && v.trim()) {
      const déjàSaisi = symptomes.some((s, idx) => idx !== i && s.nom.trim().toLowerCase() === v.trim().toLowerCase());
      if (déjàSaisi) showToast(`"${v.trim()}" a déjà été saisi`, 'error');
    }
    if (f === 'nom') invalidateAnalyse();
    const u = [...symptomes]; u[i] = { ...u[i], [f]: v }; setSymptomes(u);
  };

  // ── Examens helpers ────────────────────────────────────────────────────────
  const addExamen = () => setExamens([...examens, { type: 'BIOLOGIE', nom: '', resultats: '' }]);
  const removeExamen = (i: number) => setExamens(examens.filter((_, idx) => idx !== i));
  const editExamen = (i: number, f: keyof Examen, v: any) => { 
    const u = [...examens]; 
    u[i] = { ...u[i], [f]: v };
    
    // Auto-remplir l'unité de mesure et la valeur par défaut quand un examen est sélectionné
    if (f === 'nom' && v && EXAM_DEFAULTS[v]) {
      const defaults = EXAM_DEFAULTS[v];
      if (defaults.unite_mesure) {
        u[i].unite_mesure = defaults.unite_mesure;
      }
      if (defaults.valeur_numerique && !u[i].valeur_numerique) {
        u[i].valeur_numerique = defaults.valeur_numerique;
      }
    }
    
    setExamens(u); 
  };

  // ── Ordonnance helpers ─────────────────────────────────────────────────────
  const addMed = () => setOrdonnance([...ordonnance, { nom: '', dosage: '', frequence: '1×/jour', duree_jours: 7 }]);
  const removeMed = (i: number) => setOrdonnance(ordonnance.filter((_, idx) => idx !== i));
  const editMed = (i: number, f: keyof MedicamentOrdonnance, v: any) => { const u = [...ordonnance]; u[i] = { ...u[i], [f]: v }; setOrdonnance(u); };

  const addMedFromCatalogue = (med: typeof catalogueMeds[0]) => {
    setOrdonnance(prev => [...prev, {
      nom: med.nom_commercial,
      denomination_commune: med.denomination_commune || '',
      dosage: med.dosage || '',
      frequence: med.frequence || '1×/jour',
      duree_jours: med.duree_jours || 7,
      forme: (med as any).forme || 'COMPRIME',
      voie_administration: (med as any).voie_administration || 'ORALE',
      quantite: (med as any).quantite || 1,
    }]);
  };

  // Charge le catalogue dès que le médecin arrive à l'étape ordonnance
  useEffect(() => {
    const maladie = validationDecision === 'rejete' ? diagnosticCorrection : diagnosticFinal;
    if (step !== 7 || !maladie) return;
    setCatalogueLoading(true);
    apiFetch(`http://localhost:8000/api/consultations/catalogue-medicaments?maladie=${encodeURIComponent(maladie)}`)
      .then(r => r.json())
      .then(data => { if (Array.isArray(data)) setCatalogueMeds(data); })
      .catch(() => {})
      .finally(() => setCatalogueLoading(false));
  }, [step, diagnosticFinal, diagnosticCorrection, validationDecision]);

  // ── Stepper ────────────────────────────────────────────────────────────────
  const visibleSteps = useMemo(() => {
    if (isInfirmier) return steps.slice(0, 2);                        // Patient, Symptômes & Vitaux
    if (doctorMode === 'reprendre') return steps.slice(2);            // Analyse IA → Suivi
    if (doctorMode === 'nouveau') return steps.slice(1);              // Symptômes & Vitaux → Suivi
    return steps;
  }, [isInfirmier, doctorMode]);

  const stepMin = visibleSteps[0]?.num ?? 1;
  const stepMax = visibleSteps[visibleSteps.length - 1]?.num ?? TOTAL;
  const progress = stepMax > stepMin ? ((step - stepMin) / (stepMax - stepMin)) * 100 : 100;

  const AICard = ({ analyse, label }: { analyse: AnalyseIA; label: string }) => {
    const pct = analyse.confiance <= 1 ? analyse.confiance * 100 : analyse.confiance;
    const isHigh   = pct >= 70;
    const isMedium = pct >= 50 && pct < 70;
    const barColor = isHigh ? 'linear-gradient(90deg,#10B981,#059669)'
                   : isMedium ? 'linear-gradient(90deg,#F59E0B,#D97706)'
                   : 'linear-gradient(90deg,#EF4444,#DC2626)';
    const textColor = isHigh ? '#059669' : isMedium ? '#D97706' : '#DC2626';
    const badge = isHigh
      ? { label: 'Diagnostic fiable', bg: '#D1FAE5', color: '#065F46' }
      : isMedium
      ? { label: 'À vérifier cliniquement', bg: '#FEF3C7', color: '#92400E' }
      : { label: 'Suggestion exploratoire', bg: '#FEE2E2', color: '#991B1B' };

    return (
      <div style={{ marginBottom: '20px' }}>
        <div style={{ padding: '20px', background: 'linear-gradient(135deg,#EEF2FF,#F5F3FF)', borderRadius: '12px 12px 0 0', border: '2px solid #C7D2FE', borderBottom: 'none' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
            <div style={{ fontSize: '11px', fontWeight: 700, color: '#6366F1', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              🤖 {label}
            </div>
            <span style={{ fontSize: '11px', fontWeight: 700, padding: '3px 10px', borderRadius: '999px', background: badge.bg, color: badge.color }}>
              {badge.label}
            </span>
          </div>
          <div style={{ fontSize: '22px', fontWeight: 800, color: '#3730A3', marginBottom: '10px' }}>{analyse.maladie_predite}</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <span style={{ fontSize: '13px', color: '#6B7280' }}>Confiance IA :</span>
            <div style={{ flex: 1, height: '8px', background: '#E5E7EB', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${pct}%`, background: barColor, transition: 'width 0.6s ease' }} />
            </div>
            <strong style={{ color: textColor }}>{pct.toFixed(1)}%</strong>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {analyse.top_predictions.slice(0, 3).map((p, i) => {
              const pp = p.probabilite <= 1 ? p.probabilite * 100 : p.probabilite;
              return (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: i === 0 ? 'rgba(79,70,229,0.08)' : '#fff', borderRadius: '8px', border: `1px solid ${i === 0 ? '#C7D2FE' : '#E5E7EB'}` }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ width: '24px', height: '24px', borderRadius: '50%', background: i === 0 ? '#4F46E5' : '#E5E7EB', color: i === 0 ? '#fff' : '#6B7280', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 700 }}>{i + 1}</div>
                    <span style={{ fontWeight: i === 0 ? 700 : 500, color: '#1F2937', fontSize: '14px' }}>{p.maladie}</span>
                  </div>
                  <span style={{ fontWeight: 700, color: '#4F46E5', fontSize: '14px' }}>{pp.toFixed(1)}%</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  // ── Render ─────────────────────────────────────────────────────────────────

  // ── Écran de recherche patient (médecin) ───────────────────────────────────
  if (isMedecin && doctorPhase === 'search') {
    return (
      <div style={{ maxWidth: '700px', margin: '0 auto' }}>
        <div className="sp-page-header sp-fade-in">
          <div>
            <h1 className="sp-page-title">Nouvelle Consultation — Médecin</h1>
            <p className="sp-page-subtitle">Recherchez le dossier du patient préparé par l'infirmier</p>
          </div>
        </div>

        <div className="sp-card sp-fade-in">
          <div style={{ padding: '32px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#1F2937', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Search size={20} style={{ color: '#4F46E5' }} /> Recherche du dossier patient
            </h2>
            <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '24px' }}>
              Saisissez le nom ou le prénom du patient. Si le dossier a été préparé par l'infirmier, vous pourrez reprendre directement à l'étape Analyse IA.
            </p>

            {/* Barre de recherche */}
            <div style={{ position: 'relative', marginBottom: '24px' }}>
              {searchLoading
                ? <RefreshCw size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#4F46E5', animation: 'spin 1s linear infinite' }} />
                : <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
              }
              <input
                type="text"
                className="sp-form-input"
                style={{ paddingLeft: '38px', width: '100%' }}
                placeholder="Rechercher avec nom prénom"
                value={patientSearchQuery}
                onChange={e => setPatientSearchQuery(e.target.value)}
                autoFocus
              />
            </div>

            {/* ── Brouillons filtrés ── */}
            {(() => {
              const q = patientSearchQuery.trim().toLowerCase();
              const visible = pendingDrafts.filter(d => {
                if (!q) return true;
                const full = `${d.patient?.prenoms ?? ''} ${d.patient?.nom ?? ''}`.toLowerCase();
                return full.includes(q);
              });
              if (visible.length === 0) return null;
              return (
                <div style={{ marginBottom: '16px' }}>
                  <p style={{ fontSize: '12px', fontWeight: 700, color: '#92400E', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <ClipboardList size={13} style={{ color: '#D97706' }} />
                    Consultation{visible.length > 1 ? 's' : ''} non terminée{visible.length > 1 ? 's' : ''}
                  </p>
                  {visible.map((draft, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px', background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: '10px', marginBottom: '8px' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                          <span style={{ fontWeight: 700, color: '#1F2937', fontSize: '15px' }}>
                            {draft.patient?.prenoms} {draft.patient?.nom}
                          </span>
                          <span style={{ fontSize: '11px', background: '#FEF3C7', color: '#92400E', padding: '2px 8px', borderRadius: '6px', fontWeight: 700 }}>
                            Brouillon
                          </span>
                        </div>
                        <div style={{ fontSize: '12px', color: '#78350F', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                          <span>Étape {draft.step ?? 1} — {draft.motif || 'Consultation médicale'}</span>
                          <span>· Sauvegardé {formatDraftAge(draft.savedAt)}</span>
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
                        <button
                          className="sp-btn sp-btn-primary"
                          style={{ padding: '6px 16px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}
                          onClick={() => { applyDraft(draft, 'full'); setPendingDrafts([]); }}
                        >
                          <ArrowRight size={14} /> Reprendre
                        </button>
                        <button
                          className="sp-btn sp-btn-ghost"
                          style={{ padding: '6px 10px', fontSize: '13px', color: '#9CA3AF' }}
                          title="Supprimer ce brouillon"
                          onClick={() => { localStorage.removeItem(draft._key); setPendingDrafts(prev => prev.filter((_, i) => i !== idx)); }}
                        >
                          <X size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              );
            })()}

            {/* Résultats serveur */}
            {hasSearched && patientSearchResults.length > 0 && (
              <div style={{ marginBottom: '24px' }}>
                <p style={{ fontSize: '13px', fontWeight: 600, color: '#374151', marginBottom: '10px' }}>
                  {patientSearchResults.length} patient(s) trouvé(s)
                </p>
                {patientSearchResults.map(r => {
                  let age = null;
                  if (r.date_naissance && !r.date_naissance.startsWith('1900-01-01')) {
                    const today = new Date();
                    const birth = new Date(r.date_naissance);
                    age = today.getFullYear() - birth.getFullYear();
                    const monthDiff = today.getMonth() - birth.getMonth();
                    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) age--;
                  }

                  // Vérifier si le dossier en attente est assigné au médecin connecté
                  const pendingMedecinId = r.consultation_en_attente_medecin_id;
                  const reserveAutreDoc = r.consultation_en_attente_id &&
                    pendingMedecinId != null &&
                    pendingMedecinId !== user?.medecin_id;
                  const disponiblePourMoi = r.consultation_en_attente_id &&
                    (pendingMedecinId == null || pendingMedecinId === user?.medecin_id);

                  return (
                  <div key={r.patient_id} style={{
                    padding: '16px',
                    background: disponiblePourMoi ? '#F0FDF4' : '#F9FAFB',
                    borderRadius: '10px',
                    border: `1px solid ${disponiblePourMoi ? '#86EFAC' : '#E5E7EB'}`,
                    marginBottom: '10px',
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <div style={{ fontWeight: 700, color: '#1F2937', fontSize: '15px' }}>
                          {r.prenoms} {r.nom}
                        </div>
                        <span style={{ fontSize: '11px', color: '#6B7280', background: '#E5E7EB', padding: '2px 8px', borderRadius: '6px', fontWeight: 600 }}>
                          ID #{r.patient_id.toString().padStart(4, '0')}
                        </span>
                      </div>
                      <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '3px', display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                        {age !== null ? <span>{age} ans ({r.date_naissance})</span> : <span>Date de naissance non renseignée</span>}
                        <span>• {r.sexe === 'M' ? '♂ Masculin' : '♀ Féminin'}</span>
                      </div>
                      {disponiblePourMoi ? (
                        <div style={{ fontSize: '12px', color: '#059669', marginTop: '4px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <CheckCircle size={12} /> Dossier préparé par l'infirmier — Prêt pour l'analyse IA
                        </div>
                      ) : reserveAutreDoc ? (
                        <div style={{ fontSize: '12px', color: '#DC2626', marginTop: '4px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <AlertCircle size={12} /> Dossier réservé à un autre médecin
                        </div>
                      ) : r.derniere_consultation_id ? (
                        <div style={{ fontSize: '12px', color: '#D97706', marginTop: '4px' }}>
                          Dernière consultation : {r.derniere_consultation_statut} · {r.derniere_consultation_date?.slice(0, 10)}
                        </div>
                      ) : (
                        <div style={{ fontSize: '12px', color: '#9CA3AF', marginTop: '4px' }}>Aucune consultation antérieure</div>
                      )}
                    </div>

                    {reserveAutreDoc ? (
                      // Dossier assigné à un autre médecin — bouton bloqué
                      <button
                        disabled
                        className="sp-btn sp-btn-ghost"
                        style={{ minWidth: '130px', opacity: 0.45, cursor: 'not-allowed' }}
                        title="Ce dossier est assigné à un autre médecin"
                      >
                        <Brain size={14} /> Réservé
                      </button>
                    ) : (
                      <button
                        onClick={() => handleSelectPatient(r)}
                        disabled={selectLoading}
                        className={`sp-btn ${disponiblePourMoi ? 'sp-btn-success' : 'sp-btn-primary'}`}
                        style={{ minWidth: '130px' }}
                      >
                        {selectLoading
                          ? <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} />
                          : disponiblePourMoi
                            ? <><Brain size={14} /> Analyse IA</>
                            : <><ArrowRight size={14} /> Nouvelle consult.</>}
                      </button>
                    )}
                  </div>
                  );
                })}

                {/* Bouton homonyme — créer un nouveau patient malgré les résultats */}
                {!forceNewPatient && (
                  <button
                    onClick={() => setForceNewPatient(true)}
                    className="sp-btn sp-btn-ghost"
                    style={{ width: '100%', justifyContent: 'center', fontSize: '13px', color: '#6B7280', border: '1px dashed #D1D5DB', borderRadius: '8px', padding: '10px' }}
                  >
                    <UserPlus size={14} style={{ marginRight: '6px' }} />
                    Aucun de ces patients — Créer un nouveau dossier
                  </button>
                )}
              </div>
            )}

            {/* Patient introuvable ou création forcée — mini-formulaire avec découpe intelligente */}
            {hasSearched && (patientSearchResults.length === 0 || forceNewPatient) && (
              <div style={{ padding: '20px', background: '#EFF6FF', borderRadius: '10px', border: '1px solid #BFDBFE', marginBottom: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '10px', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <UserX size={20} style={{ color: '#2563EB', flexShrink: 0 }} />
                    <div>
                      <div style={{ fontWeight: 700, color: '#1E3A8A', fontSize: '15px' }}>
                        {forceNewPatient ? 'Nouveau patient homonyme' : 'Patient introuvable'}
                      </div>
                      <div style={{ fontSize: '13px', color: '#1D4ED8' }}>
                        {forceNewPatient
                          ? 'Vérifiez le nom/prénom ci-dessous puis créez un nouveau dossier.'
                          : `Aucun dossier pour « ${patientSearchQuery} ». Vérifiez et corrigez le nom/prénom ci-dessous, puis démarrez la consultation.`}
                      </div>
                    </div>
                  </div>
                  {forceNewPatient && (
                    <button
                      onClick={() => setForceNewPatient(false)}
                      className="sp-btn sp-btn-ghost sp-btn-sm"
                      style={{ flexShrink: 0, fontSize: '12px', color: '#6B7280' }}
                      title="Revenir aux résultats"
                    >
                      <X size={14} /> Annuler
                    </button>
                  )}
                </div>

                {/* Ligne 1 : Nom ⇄ Prénoms */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '8px', alignItems: 'end', marginBottom: '12px' }}>
                  <div className="sp-form-group" style={{ margin: 0 }}>
                    <label className="sp-form-label" style={{ color: '#1E40AF', fontWeight: 700 }}>Nom de famille <span style={{ color: '#EF4444' }}>*</span></label>
                    <input
                      type="text"
                      className="sp-form-input"
                      value={quickStartNom}
                      onChange={e => setQuickStartNom(e.target.value.toUpperCase())}
                      placeholder="DUPONT"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      const newNom = quickStartPrenoms.toUpperCase();
                      const newPrenoms = quickStartNom.charAt(0).toUpperCase() + quickStartNom.slice(1).toLowerCase();
                      setQuickStartNom(newNom);
                      setQuickStartPrenoms(newPrenoms);
                    }}
                    title="Inverser nom et prénom"
                    style={{ background: '#DBEAFE', border: '1px solid #93C5FD', borderRadius: '8px', padding: '8px 10px', cursor: 'pointer', color: '#1D4ED8', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1px', fontSize: '16px' }}
                  >
                    ⇄
                  </button>
                  <div className="sp-form-group" style={{ margin: 0 }}>
                    <label className="sp-form-label" style={{ color: '#1E40AF', fontWeight: 700 }}>Prénoms</label>
                    <input
                      type="text"
                      className="sp-form-input"
                      value={quickStartPrenoms}
                      onChange={e => {
                        const v = e.target.value;
                        setQuickStartPrenoms(v.charAt(0).toUpperCase() + v.slice(1).toLowerCase());
                      }}
                      placeholder="Jean"
                    />
                  </div>
                </div>

                {/* Ligne 2 : Âge + Sexe */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                  <div className="sp-form-group" style={{ margin: 0 }}>
                    <label className="sp-form-label" style={{ color: '#1E40AF', fontWeight: 700 }}>Âge (années)</label>
                    <input
                      type="number"
                      className="sp-form-input"
                      value={quickStartAge}
                      onChange={e => setQuickStartAge(e.target.value === '' ? '' : parseInt(e.target.value))}
                      placeholder="ex: 35"
                      min={0}
                      max={130}
                    />
                  </div>
                  <div className="sp-form-group" style={{ margin: 0 }}>
                    <label className="sp-form-label" style={{ color: '#1E40AF', fontWeight: 700 }}>Sexe</label>
                    <select
                      className="sp-form-input"
                      value={quickStartSexe}
                      onChange={e => setQuickStartSexe(e.target.value as 'M' | 'F')}
                    >
                      <option value="M">♂ Masculin</option>
                      <option value="F">♀ Féminin</option>
                    </select>
                  </div>
                </div>

                <div className="sp-form-group" style={{ margin: '0 0 16px' }}>
                  <label className="sp-form-label" style={{ color: '#1E40AF', fontWeight: 700 }}>Motif de consultation</label>
                  <input
                    type="text"
                    className="sp-form-input"
                    value={quickStartMotif}
                    onChange={e => setQuickStartMotif(e.target.value)}
                    placeholder="Ex : douleur thoracique, fièvre, suivi diabète…"
                    maxLength={200}
                  />
                </div>

                <button onClick={handleQuickStart} disabled={loading || !quickStartNom.trim()} className="sp-btn sp-btn-outline" style={{ color: '#2563EB', borderColor: '#2563EB', opacity: !quickStartNom.trim() ? 0.5 : 1 }}>
                  {loading
                    ? <><RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> Création...</>
                    : <><Plus size={15} /> Démarrer la consultation</>}
                </button>
              </div>
            )}

            {/* Lien retour */}
            <div style={{ borderTop: '1px solid #E5E7EB', paddingTop: '16px', textAlign: 'center' }}>
              <button onClick={() => navigate('/consultations')} className="sp-btn sp-btn-outline" style={{ fontSize: '13px' }}>
                <ArrowLeft size={14} /> Retour aux consultations
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Écran de recherche patient (infirmier) ─────────────────────────────────
  if (isInfirmier && infirmierPhase === 'search') {
    return (
      <div style={{ maxWidth: '700px', margin: '0 auto' }}>
        <div className="sp-page-header sp-fade-in">
          <div>
            <h1 className="sp-page-title">Nouvelle Consultation — Infirmier</h1>
            <p className="sp-page-subtitle">Recherchez le dossier du patient ou créez-en un nouveau</p>
          </div>
        </div>

        <div className="sp-card sp-fade-in">
          <div style={{ padding: '32px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#1F2937', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Search size={20} style={{ color: '#4F46E5' }} /> Recherche du dossier patient
            </h2>
            <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '24px' }}>
              Saisissez le nom ou le prénom du patient. S'il existe déjà, ses informations seront pré-remplies automatiquement.
            </p>

            {/* Sélecteur de médecin — obligatoire dans les deux branches */}
            <div style={{ marginBottom: '24px', padding: '16px', background: '#EEF2FF', borderRadius: '10px', border: '1px solid #C7D2FE' }}>
              <label className="sp-form-label" style={{ color: '#4338CA', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                <UserCheck size={14} /> Médecin assigné <span style={{ color: '#EF4444' }}>*</span>
              </label>
              <div style={{ position: 'relative', marginBottom: '10px' }}>
                <Search size={14} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
                <input
                  type="text"
                  className="sp-form-input"
                  style={{ paddingLeft: '34px', height: '36px', fontSize: '13px' }}
                  placeholder="Rechercher par nom ou spécialité..."
                  value={medecinSearch}
                  onChange={e => setMedecinSearch(e.target.value)}
                />
              </div>
              <select
                className="sp-form-select"
                value={medecinId || ''}
                onChange={e => setMedecinId(Number(e.target.value) || null)}
              >
                <option value="">— {filteredMedecins.length === 0 ? 'Aucun médecin trouvé' : 'Sélectionner un médecin'} —</option>
                {filteredMedecins.map(m => (
                  <option key={m.id} value={m.id}>Dr. {m.prenoms} {m.nom}{m.specialite ? ` — ${m.specialite}` : ''}</option>
                ))}
              </select>
              <p style={{ fontSize: '12px', color: '#6366F1', margin: '8px 0 0' }}>
                Ce médecin sera notifié pour continuer et finaliser la consultation.
              </p>
            </div>

            {/* Barre de recherche patient */}
            <div style={{ position: 'relative', marginBottom: '24px' }}>
              {searchLoading
                ? <RefreshCw size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#4F46E5', animation: 'spin 1s linear infinite' }} />
                : <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
              }
              <input
                type="text"
                className="sp-form-input"
                style={{ paddingLeft: '38px', width: '100%' }}
                placeholder="Rechercher par nom ou prénom..."
                value={patientSearchQuery}
                onChange={e => setPatientSearchQuery(e.target.value)}
                autoFocus
              />
            </div>

            {/* ── Brouillons infirmier (même style que médecin) ── */}
            {(() => {
              const q = patientSearchQuery.trim().toLowerCase();
              const visible = pendingDrafts.filter(d => {
                if (!q) return true;
                const full = `${d.patient?.prenoms ?? ''} ${d.patient?.nom ?? ''}`.toLowerCase();
                return full.includes(q);
              });
              if (visible.length === 0) return null;
              return (
                <div style={{ marginBottom: '16px' }}>
                  <p style={{ fontSize: '12px', fontWeight: 700, color: '#92400E', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <ClipboardList size={13} style={{ color: '#D97706' }} />
                    Consultation{visible.length > 1 ? 's' : ''} non terminée{visible.length > 1 ? 's' : ''}
                  </p>
                  {visible.map((draft, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px', background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: '10px', marginBottom: '8px' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                          <span style={{ fontWeight: 700, color: '#1F2937', fontSize: '15px' }}>
                            {draft.patient?.prenoms} {draft.patient?.nom}
                          </span>
                          <span style={{ fontSize: '11px', background: '#FEF3C7', color: '#92400E', padding: '2px 8px', borderRadius: '6px', fontWeight: 700 }}>
                            Brouillon
                          </span>
                        </div>
                        <div style={{ fontSize: '12px', color: '#78350F', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                          <span>Étape {draft.step ?? 1} — {draft.motif || 'Consultation médicale'}</span>
                          <span>· Sauvegardé {formatDraftAge(draft.savedAt)}</span>
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
                        <button
                          className="sp-btn sp-btn-primary"
                          style={{ padding: '6px 16px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}
                          onClick={() => { applyDraft(draft, 'full'); setPendingDrafts([]); }}
                        >
                          <ArrowRight size={14} /> Reprendre
                        </button>
                        <button
                          className="sp-btn sp-btn-ghost"
                          style={{ padding: '6px 10px', fontSize: '13px', color: '#9CA3AF' }}
                          title="Supprimer ce brouillon"
                          onClick={() => {
                            localStorage.removeItem(draft._key);
                            setPendingDrafts(prev => prev.filter((_, i) => i !== idx));
                          }}
                        >
                          <X size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              );
            })()}

            {/* Résultats */}
            {hasSearched && patientSearchResults.length > 0 && (
              <div style={{ marginBottom: '24px' }}>
                <p style={{ fontSize: '13px', fontWeight: 600, color: '#374151', marginBottom: '10px' }}>
                  {patientSearchResults.length} patient(s) trouvé(s)
                </p>
                {patientSearchResults.map(r => {
                  let age = null;
                  if (r.date_naissance && !r.date_naissance.startsWith('1900-01-01')) {
                    const today = new Date();
                    const birth = new Date(r.date_naissance);
                    age = today.getFullYear() - birth.getFullYear();
                    const monthDiff = today.getMonth() - birth.getMonth();
                    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) age--;
                  }
                  const hasPending = !!r.consultation_en_attente_id;

                  return (
                    <div key={r.patient_id} style={{
                      padding: '16px',
                      background: '#F9FAFB',
                      borderRadius: '10px',
                      border: '1px solid #E5E7EB',
                      marginBottom: '10px',
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                          <div style={{ fontWeight: 700, color: '#1F2937', fontSize: '15px' }}>
                            {r.prenoms} {r.nom}
                          </div>
                          <span style={{ fontSize: '11px', color: '#6B7280', background: '#E5E7EB', padding: '2px 8px', borderRadius: '6px', fontWeight: 600 }}>
                            ID #{r.patient_id.toString().padStart(4, '0')}
                          </span>
                        </div>
                        <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '3px', display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                          {age !== null ? <span>{age} ans ({r.date_naissance})</span> : <span>Date de naissance non renseignée</span>}
                          <span>• {r.sexe === 'M' ? '♂ Masculin' : '♀ Féminin'}</span>
                        </div>
                        {hasPending ? (
                          <div style={{ fontSize: '12px', color: '#D97706', marginTop: '4px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <AlertCircle size={12} /> Consultation en attente chez le médecin
                          </div>
                        ) : r.derniere_consultation_id ? (
                          <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                            Dernière consultation : {r.derniere_consultation_statut} · {r.derniere_consultation_date?.slice(0, 10)}
                          </div>
                        ) : (
                          <div style={{ fontSize: '12px', color: '#9CA3AF', marginTop: '4px' }}>Aucune consultation antérieure</div>
                        )}
                      </div>
                      <button
                        onClick={() => handleInfirmierSelectPatient(r)}
                        disabled={selectLoading || !medecinId}
                        className="sp-btn sp-btn-primary"
                        style={{ minWidth: '130px', opacity: !medecinId ? 0.5 : 1 }}
                        title={!medecinId ? 'Sélectionnez d\'abord un médecin' : ''}
                      >
                        {selectLoading
                          ? <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} />
                          : <><UserCheck size={14} /> Sélectionner</>}
                      </button>
                    </div>
                  );
                })}

                {!forceNewPatient && (
                  <button
                    onClick={() => setForceNewPatient(true)}
                    className="sp-btn sp-btn-ghost"
                    style={{ width: '100%', justifyContent: 'center', fontSize: '13px', color: '#6B7280', border: '1px dashed #D1D5DB', borderRadius: '8px', padding: '10px' }}
                  >
                    <UserPlus size={14} style={{ marginRight: '6px' }} />
                    Aucun de ces patients — Créer un nouveau dossier
                  </button>
                )}
              </div>
            )}

            {/* Patient introuvable → bouton pour aller directement au formulaire complet */}
            {hasSearched && (patientSearchResults.length === 0 || forceNewPatient) && (
              <div style={{ padding: '20px', background: '#EFF6FF', borderRadius: '10px', border: '1px solid #BFDBFE', marginBottom: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                  <UserX size={22} style={{ color: '#2563EB', flexShrink: 0 }} />
                  <div>
                    <div style={{ fontWeight: 700, color: '#1E3A8A', fontSize: '15px' }}>
                      {forceNewPatient ? 'Nouveau patient homonyme' : `Aucun dossier trouvé pour « ${patientSearchQuery} »`}
                    </div>
                    <div style={{ fontSize: '13px', color: '#1D4ED8', marginTop: '2px' }}>
                      Créez un nouveau dossier patient en remplissant le formulaire complet.
                    </div>
                  </div>
                  {forceNewPatient && (
                    <button onClick={() => setForceNewPatient(false)} className="sp-btn sp-btn-ghost sp-btn-sm" style={{ marginLeft: 'auto', fontSize: '12px', color: '#6B7280' }}>
                      <X size={14} /> Annuler
                    </button>
                  )}
                </div>
                <button
                  onClick={handleInfirmierQuickStart}
                  disabled={!medecinId}
                  className="sp-btn sp-btn-primary"
                  style={{ width: '100%', opacity: !medecinId ? 0.5 : 1 }}
                  title={!medecinId ? 'Sélectionnez d\'abord un médecin' : ''}
                >
                  <UserPlus size={15} /> Démarrer la consultation — nouveau patient
                </button>
              </div>
            )}

            <div style={{ borderTop: '1px solid #E5E7EB', paddingTop: '16px', textAlign: 'center' }}>
              <button onClick={() => navigate('/consultations')} className="sp-btn sp-btn-outline" style={{ fontSize: '13px' }}>
                <ArrowLeft size={14} /> Retour aux consultations
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Écran de confirmation infirmier après soumission ────────────────────────
  if (infirmierSubmitted) {
    return (
      <div style={{ maxWidth: '600px', margin: '60px auto' }}>
        <div className="sp-card sp-fade-in">
          <div style={{ padding: '60px 40px', textAlign: 'center' }}>
            <div style={{ width: '80px', height: '80px', margin: '0 auto 24px', background: 'linear-gradient(135deg,#059669,#10B981)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <CheckCircle size={40} style={{ color: '#fff' }} />
            </div>
            <h2 style={{ fontSize: '22px', fontWeight: 700, color: '#065F46', marginBottom: '12px' }}>Consultation transmise !</h2>
            <p style={{ color: '#6B7280', marginBottom: '8px', fontSize: '15px' }}>
              Les données ont été enregistrées et le médecin assigné a été notifié.
            </p>
            <p style={{ color: '#9CA3AF', marginBottom: '36px', fontSize: '13px' }}>
              Le médecin pourra continuer directement à partir de l'Analyse IA pour finaliser le diagnostic.
            </p>
            <button onClick={() => navigate('/consultations')} className="sp-btn sp-btn-primary">
              Retour aux consultations
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
    {/* ── Modal de reprise de brouillon ── */}
    {showResumeModal && savedDraft && (
      <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10000 }}>
        <div style={{ background: '#fff', borderRadius: '20px', padding: '36px 32px', maxWidth: '460px', width: '92%', boxShadow: '0 24px 72px rgba(0,0,0,0.25)', animation: 'fadeIn .2s ease' }}>
          <div style={{ textAlign: 'center', marginBottom: '20px' }}>
            <div style={{ width: '64px', height: '64px', margin: '0 auto 16px', background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ClipboardList size={28} style={{ color: '#fff' }} />
            </div>
            <h3 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937', margin: '0 0 8px' }}>Consultation non terminée</h3>
            <p style={{ color: '#6B7280', fontSize: '14px', margin: 0 }}>
              Une consultation a été sauvegardée automatiquement. Souhaitez-vous reprendre là où vous en étiez ?
            </p>
          </div>

          <div style={{ background: '#F9FAFB', borderRadius: '12px', padding: '16px', marginBottom: '24px', border: '1px solid #E5E7EB' }}>
            {savedDraft.patient?.nom && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                <User size={14} style={{ color: '#6366F1', flexShrink: 0 }} />
                <span style={{ fontWeight: 700, color: '#111827', fontSize: '15px' }}>
                  {savedDraft.patient.prenoms} {savedDraft.patient.nom}
                </span>
              </div>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <ArrowRight size={14} style={{ color: '#6366F1', flexShrink: 0 }} />
              <span style={{ color: '#374151', fontSize: '13px', fontWeight: 600 }}>
                {STEP_LABELS[savedDraft.step] || `Étape ${savedDraft.step}`}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle size={14} style={{ color: '#10B981', flexShrink: 0 }} />
              <span style={{ color: '#6B7280', fontSize: '12px' }}>
                Sauvegardé {formatDraftAge(savedDraft.savedAt)}
              </span>
            </div>
            {savedDraft.motif && (
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#9CA3AF', fontStyle: 'italic' }}>
                Motif : {savedDraft.motif}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '12px', flexDirection: 'column' }}>
            <button
              onClick={() => resetFormState(savedDraft?.consultationId)}
              className="sp-btn sp-btn-primary"
              style={{ flex: 1, fontWeight: 700, background: '#10B981', borderColor: '#10B981' }}
            >
              <RefreshCw size={15} /> Nouvelle consultation (recommencer)
            </button>
            <button
              onClick={() => applyDraft(savedDraft, savedDraft._medecin_only ? 'medecin-only' : 'full')}
              className="sp-btn sp-btn-outline"
              style={{ flex: 1, fontSize: '13px' }}
            >
              <ArrowRight size={15} /> Reprendre la consultation précédente
            </button>
          </div>
        </div>
      </div>
    )}

    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <style>{`@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}`}</style>

      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">
            {isReprendre ? `Continuer la consultation` : 'Nouvelle Consultation'}
          </h1>
          <p className="sp-page-subtitle">
            {isInfirmier ? 'Saisie initiale · Étapes 1–2' : isMedecin ? `Workflow médecin assisté par IA · Étape ${step - stepMin + 1}/${visibleSteps.length}` : `Workflow assisté par IA · Étape ${step}/${TOTAL}`}
          </p>
        </div>
      </div>

      <MedicalDisclaimerBanner compact />

      {/* ── Stepper ── */}
      <div className="sp-card sp-fade-in" style={{ marginBottom: '20px', padding: '24px 28px' }}>
        <div style={{ position: 'relative' }}>
          <div style={{ position: 'absolute', top: '18px', left: '18px', right: '18px', height: '3px', background: '#E5E7EB', zIndex: 0 }}>
            <div style={{ height: '100%', background: 'linear-gradient(90deg,#4F46E5,#7C3AED)', width: `${progress}%`, transition: 'width 0.4s ease' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', position: 'relative', zIndex: 1 }}>
            {visibleSteps.map(s => {
              const Icon = s.icon;
              const done = step > s.num;
              const active = step === s.num;
              return (
                <div key={s.num} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.3s', background: done ? 'linear-gradient(135deg,#4F46E5,#7C3AED)' : active ? (s.special ? 'linear-gradient(135deg,#7C3AED,#EC4899)' : '#4F46E5') : '#E5E7EB', border: active ? '3px solid #EEF2FF' : 'none', boxShadow: active ? '0 0 0 3px rgba(79,70,229,0.2)' : 'none' }}>
                    <Icon size={16} style={{ color: done || active ? '#fff' : '#9CA3AF' }} />
                  </div>
                  <span style={{ fontSize: '10px', fontWeight: active ? 700 : 500, color: active ? '#4F46E5' : done ? '#6B7280' : '#9CA3AF', textAlign: 'center', maxWidth: '60px', lineHeight: 1.3 }}>{s.title}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Indicateur de sauvegarde automatique */}
      {draftSavedAt && (
        <div style={{ textAlign: 'right', fontSize: '11px', color: '#10B981', marginBottom: '6px', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '4px' }}>
          <CheckCircle size={11} />
          <span>Sauvegardé automatiquement {formatDraftAge(draftSavedAt)}</span>
        </div>
      )}

      {/* ── Bandeau motif manquant (brouillon repris sans motif) ── */}
      {needsMotif && step > 1 && (
        <div style={{ marginBottom: '12px', padding: '14px 18px', background: '#FFF7ED', border: '1px solid #FED7AA', borderRadius: '10px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <AlertCircle size={18} style={{ color: '#EA580C', flexShrink: 0 }} />
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: '12px', fontWeight: 700, color: '#C2410C', display: 'block', marginBottom: '6px' }}>
              Motif de consultation manquant
            </label>
            <input
              type="text"
              className="sp-form-input"
              style={{ marginBottom: 0, height: '34px', fontSize: '13px' }}
              value={motif === 'Consultation médicale' ? '' : motif}
              onChange={e => setMotif(e.target.value)}
              onBlur={() => { if (motif.trim() && motif.trim() !== 'Consultation médicale') setNeedsMotif(false); }}
              placeholder="Ex : douleur thoracique, fièvre, suivi diabète…"
              autoFocus
              maxLength={200}
            />
          </div>
        </div>
      )}

      {/* ── Content ── */}
      <div className="sp-card sp-fade-in">
        <div style={{ padding: '32px' }}>

          {/* Chargement en cours (reprendre via URL, en attente de l'effect) */}
          {step < stepMin && (
            <div style={{ textAlign: 'center', padding: '60px 20px', color: '#6B7280' }}>
              <RefreshCw size={32} style={{ animation: 'spin 1s linear infinite', margin: '0 auto 12px' }} />
              <p>Chargement du dossier patient...</p>
            </div>
          )}

          {/* Étape 1 — Patient */}
          {step === 1 && step >= stepMin && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>Informations du Patient</h2>
                {roleBadge('Accueil')}
              </div>

              <div className="sp-form-group" style={{ marginBottom: '16px' }}>
                <label className="sp-form-label">Motif de consultation <span style={{ color: '#EF4444' }}>*</span></label>
                <textarea className="sp-form-textarea" rows={2} value={motif} onChange={e => setMotif(e.target.value)} placeholder="Raison de la visite aujourd'hui..." />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                {/* Patient fields loop */}
                {[
                  { label: 'Nom', key: 'nom', type: 'text', required: true },
                  { label: 'Prénoms', key: 'prenoms', type: 'text', required: true },
                  { label: 'Date de naissance', key: 'date_naissance', type: 'date', required: true },
                  { label: 'Téléphone', key: 'telephone', type: 'tel' },
                  { label: 'Email', key: 'email', type: 'email' },
                ].map(f => (
                  <div key={f.key} className="sp-form-group">
                    <label className="sp-form-label">{f.label} {f.required && <span style={{ color: '#EF4444' }}>*</span>}</label>
                    <input 
                      type={f.type} 
                      className="sp-form-input" 
                      max={f.type === 'date' ? new Date().toISOString().split('T')[0] : undefined}
                      value={(patient as any)[f.key] || ''} 
                      onChange={e => setPatient({ ...patient, [f.key]: e.target.value })} 
                    />
                  </div>
                ))}
                <div className="sp-form-group">
                  <label className="sp-form-label">Sexe <span style={{ color: '#EF4444' }}>*</span></label>
                  <select className="sp-form-select" value={patient.sexe} onChange={e => setPatient({ ...patient, sexe: e.target.value as 'M' | 'F' })}>
                    <option value="M">♂ Masculin</option><option value="F">♀ Féminin</option>
                  </select>
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">Groupe sanguin</label>
                  <select className="sp-form-select" value={patient.groupe_sanguin || ''} onChange={e => setPatient({ ...patient, groupe_sanguin: e.target.value || undefined })}>
                    <option value="">— Non renseigné —</option>
                    <option value="A+">A+</option><option value="A-">A-</option>
                    <option value="B+">B+</option><option value="B-">B-</option>
                    <option value="AB+">AB+</option><option value="AB-">AB-</option>
                    <option value="O+">O+</option><option value="O-">O-</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Étape 2 — Symptômes */}
          {step === 2 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>Symptômes & Signes Vitaux</h2>
              </div>

              {/* Sélecteur médecin — toujours visible à l'étape 2 pour l'infirmier */}
              {isInfirmier && (
                <div style={{ marginBottom: '24px', padding: '16px', background: '#EEF2FF', borderRadius: '10px', border: '1px solid #C7D2FE' }}>
                  <label className="sp-form-label" style={{ color: '#4338CA', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                    <UserCheck size={14} /> Médecin assigné <span style={{ color: '#EF4444' }}>*</span>
                  </label>
                  <div style={{ position: 'relative', marginBottom: '10px' }}>
                    <Search size={14} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
                    <input type="text" className="sp-form-input" style={{ paddingLeft: '34px', height: '36px', fontSize: '13px' }}
                      placeholder="Rechercher par nom ou spécialité..."
                      value={medecinSearch} onChange={e => setMedecinSearch(e.target.value)} />
                  </div>
                  <select className="sp-form-select" value={medecinId || ''} onChange={e => setMedecinId(Number(e.target.value) || null)}>
                    <option value="">— {filteredMedecins.length === 0 ? 'Aucun médecin trouvé' : 'Sélectionner un médecin'} —</option>
                    {filteredMedecins.map(m => (
                      <option key={m.id} value={m.id}>Dr. {m.prenoms} {m.nom}{m.specialite ? ` — ${m.specialite}` : ''}</option>
                    ))}
                  </select>
                  <p style={{ fontSize: '12px', color: '#6366F1', margin: '8px 0 0' }}>
                    Ce médecin sera notifié pour continuer et finaliser la consultation.
                  </p>
                </div>
              )}

              {/* Symptômes */}
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#374151', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Activity size={15} style={{ color: '#4F46E5' }} /> Symptômes
              </h3>
              {symptomes.map((s, i) => (
                <div key={i} style={{ padding: '18px', background: '#F9FAFB', borderRadius: '12px', marginBottom: '12px', border: '1px solid #E5E7EB' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ fontWeight: 600, color: '#374151' }}>Symptôme {i + 1}</span>
                    <button type="button" onClick={() => removeSymptome(i)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#EF4444' }}><X size={18} /></button>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '12px' }}>
                    <div className="sp-form-group" style={{ position: 'relative' }}>
                      <label className="sp-form-label">Symptôme</label>
                      <input
                        type="text"
                        className="sp-form-input"
                        value={s.nom}
                        onChange={e => { editSymptome(i, 'nom', e.target.value); setOpenSymptomIdx(i); }}
                        onFocus={() => setOpenSymptomIdx(i)}
                        onBlur={() => {
                          setTimeout(() => setOpenSymptomIdx(null), 200);
                          const val = s.nom.trim();
                          if (val && !ALL_SYMPTOMES_SET.has(val)) {
                            editSymptome(i, 'nom', '');
                            showToast(`"${val}" n'est pas dans la liste des symptômes disponibles`, 'error');
                          }
                        }}
                        placeholder="Rechercher un symptôme..."
                        autoComplete="off"
                        style={s.nom.trim() && symptomes.some((o, idx) => idx !== i && o.nom.trim().toLowerCase() === s.nom.trim().toLowerCase()) ? { borderColor: '#EF4444', background: '#FEF2F2' } : undefined}
                      />
                      {openSymptomIdx === i && (
                        <div style={{
                          position: 'absolute', top: 'calc(100% + 4px)', left: 0, right: 0, zIndex: 300,
                          background: '#fff', border: '1px solid #E5E7EB', borderRadius: '12px',
                          padding: '10px 12px', boxShadow: '0 8px 24px rgba(0,0,0,0.13)',
                          maxHeight: '210px', overflowY: 'auto',
                        }}>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                            {(() => {
                              const filtered = getSymptomesDisponibles(patient.sexe)
                                .filter(sym => !s.nom.trim() || sym.toLowerCase().includes(s.nom.toLowerCase()));
                              if (filtered.length === 0)
                                return <span style={{ color: '#9CA3AF', fontSize: '13px' }}>Aucun symptôme trouvé</span>;
                              return filtered.map((sym, idx) => (
                                <button
                                  key={idx}
                                  type="button"
                                  onMouseDown={e => { e.preventDefault(); editSymptome(i, 'nom', sym); setOpenSymptomIdx(null); }}
                                  style={{
                                    padding: '4px 12px', borderRadius: '999px', cursor: 'pointer',
                                    border: `1px solid ${s.nom === sym ? '#4F46E5' : '#E5E7EB'}`,
                                    background: s.nom === sym ? '#EEF2FF' : '#F9FAFB',
                                    color: s.nom === sym ? '#4F46E5' : '#374151',
                                    fontSize: '12px', fontWeight: s.nom === sym ? 600 : 400,
                                    whiteSpace: 'nowrap', transition: 'all 0.15s',
                                  }}
                                >
                                  {sym}
                                </button>
                              ));
                            })()}
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Sévérité</label>
                      <select className="sp-form-select" value={s.severite} onChange={e => editSymptome(i, 'severite', e.target.value)}>
                        <option>Légère</option><option>Modérée</option><option>Sévère</option>
                      </select>
                    </div>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Durée (j)</label>
                      <input type="number" min={1} className="sp-form-input" value={s.duree_jours} onChange={e => editSymptome(i, 'duree_jours', parseInt(e.target.value))} />
                    </div>
                  </div>
                  <div className="sp-form-group" style={{ marginTop: '8px' }}>
                    <label className="sp-form-label">Description</label>
                    <textarea className="sp-form-textarea" rows={2} value={s.description || ''} onChange={e => editSymptome(i, 'description', e.target.value)} placeholder="Détails..." />
                  </div>
                </div>
              ))}
              <button type="button" onClick={addSymptome} className="sp-btn sp-btn-outline" style={{ width: '100%', marginBottom: '28px' }}>
                <Plus size={16} /> Ajouter un symptôme
              </button>

              {/* Signes Vitaux */}
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#374151', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Stethoscope size={15} style={{ color: '#4F46E5' }} /> Signes Vitaux
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                {[
                  { label: 'Tension systolique (mmHg)', key: 'tension_systolique', icon: Heart, step: 0.1 },
                  { label: 'Tension diastolique (mmHg)', key: 'tension_diastolique', icon: Heart, step: 0.1 },
                  { label: 'Fréquence cardiaque (bpm)', key: 'frequence_cardiaque', icon: Activity, step: 0.1 },
                  { label: 'Fréquence respiratoire (rpm)', key: 'frequence_respiratoire', icon: Wind, step: 0.1 },
                  { label: 'Température (°C)', key: 'temperature', icon: Thermometer, step: 0.1 },
                  { label: 'Saturation O₂ (%)', key: 'saturation_o2', icon: Droplet, step: 0.1 },
                  { label: 'Poids (kg) — optionnel', key: 'poids', icon: Weight, step: 0.1 },
                  { label: 'Taille (cm) — optionnel', key: 'taille', icon: Ruler, step: 0.1 },
                ].map(f => (
                  <div key={f.key} className="sp-form-group">
                    <label className="sp-form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <f.icon size={13} style={{ color: '#9CA3AF' }} />{f.label}
                    </label>
                    <input type="number" step={f.step} className="sp-form-input"
                      value={(vitaux as any)[f.key] || ''}
                      onChange={e => { invalidateAnalyse(); setVitaux({ ...vitaux, [f.key]: parseFloat(e.target.value) || undefined }); }} />
                  </div>
                ))}
              </div>
              {vitaux.poids && vitaux.taille && (
                <div style={{ marginTop: '16px', padding: '14px 18px', background: '#EEF2FF', borderRadius: '8px', border: '1px solid #C7D2FE' }}>
                  <strong style={{ color: '#4F46E5' }}>IMC :</strong>{' '}
                  <span style={{ fontSize: '18px', fontWeight: 700, color: '#1F2937' }}>
                    {(vitaux.poids / Math.pow(vitaux.taille / 100, 2)).toFixed(1)} kg/m²
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Étape 3 — Analyse IA Préliminaire */}
          {step === 3 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>Analyse IA Préliminaire</h2>
                {roleBadge('IA + Médecin', true)}
              </div>
              <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '24px' }}>
                L'IA analyse les symptômes et signes vitaux pour formuler des hypothèses diagnostiques et recommander les examens à réaliser.
              </p>

              {/* Mini-formulaire âge/sexe pour consultation démarrée sans dossier complet */}
              {isQuickStart && (
                <div style={{ padding: '16px', background: '#FFF7ED', borderRadius: '10px', border: '1px solid #FED7AA', marginBottom: '20px', display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'flex-end' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '100%', marginBottom: '4px' }}>
                    <AlertCircle size={15} style={{ color: '#EA580C' }} />
                    <span style={{ fontSize: '13px', fontWeight: 700, color: '#9A3412' }}>Âge et sexe requis pour l'analyse IA</span>
                    <span style={{ fontSize: '12px', color: '#C2410C' }}>— dossier patient non renseigné</span>
                  </div>
                  <div>
                    <label style={{ fontSize: '12px', fontWeight: 600, color: '#6B7280', display: 'block', marginBottom: '4px' }}>Âge du patient *</label>
                    <input
                      type="number" min={0} max={120} className="sp-form-input"
                      style={{ width: '110px', fontSize: '14px' }}
                      placeholder="Ex : 35"
                      value={manualAge ?? ''}
                      onChange={e => setManualAge(e.target.value ? parseInt(e.target.value) : null)}
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: '12px', fontWeight: 600, color: '#6B7280', display: 'block', marginBottom: '4px' }}>Sexe *</label>
                    <select className="sp-form-select" style={{ fontSize: '14px', width: '140px' }} value={patient.sexe} onChange={e => setPatient({ ...patient, sexe: e.target.value as 'M' | 'F' })}>
                      <option value="M">♂ Masculin</option>
                      <option value="F">♀ Féminin</option>
                    </select>
                  </div>
                </div>
              )}

              {/* Récap données saisies */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '24px' }}>
                <VitalBadge label="Symptômes" value={symptomes.filter(s => s.nom.trim()).length} unit="saisis" icon={Activity} />
                <VitalBadge label="Température" value={`${vitaux.temperature}°C`} unit="" icon={Thermometer} alert={vitaux.temperature >= 38.5} />
                <VitalBadge label="FC" value={vitaux.frequence_cardiaque} unit="bpm" icon={Heart} alert={vitaux.frequence_cardiaque > 100} />
                <VitalBadge label="TA" value={`${vitaux.tension_systolique}/${vitaux.tension_diastolique}`} unit="mmHg" icon={Activity} alert={vitaux.tension_systolique > 140} />
                <VitalBadge label="SpO₂" value={`${vitaux.saturation_o2}%`} unit="" icon={Droplet} alert={vitaux.saturation_o2 < 94} />
                <VitalBadge label="FR" value={vitaux.frequence_respiratoire} unit="rpm" icon={Wind} alert={vitaux.frequence_respiratoire > 20} />
              </div>

              {analysePreliminaire ? (
                <div>
                  <AICard analyse={analysePreliminaire} label="Hypothèses diagnostiques (basé sur symptômes + signes vitaux)" />
                  <button
                    onClick={() => setShowDonneesModal(true)}
                    className="sp-btn sp-btn-outline"
                    style={{ marginBottom: '16px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}
                  >
                    <ClipboardList size={15} /> Voir les symptômes &amp; signes vitaux du patient
                  </button>
                  <div style={{ padding: '14px 18px', background: '#ECFDF5', borderRadius: '8px', border: '1px solid #6EE7B7', display: 'flex', gap: '10px', marginBottom: '20px' }}>
                    <Lightbulb size={18} style={{ color: '#059669', flexShrink: 0, marginTop: '2px' }} />
                    <div style={{ fontSize: '13px', color: '#065F46' }}>
                      <strong>Examens suggérés :</strong> {examens.length} examen(s) ont été pré-remplis selon les hypothèses de l'IA. Vous pouvez les visualiser et les compléter à l'étape suivante.
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                  <div style={{ width: '72px', height: '72px', margin: '0 auto 16px', background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Brain size={36} style={{ color: '#fff' }} />
                  </div>
                  <h3 style={{ fontSize: '17px', fontWeight: 600, marginBottom: '8px' }}>Prêt pour l'analyse préliminaire</h3>
                  <p style={{ color: '#6B7280', marginBottom: '24px', fontSize: '14px' }}>
                    L'IA va formuler des hypothèses diagnostiques et vous suggérer les examens les plus pertinents à réaliser.
                  </p>
                  <button
                    onClick={handleAnalysePreliminaire}
                    disabled={loading || symptomes.filter(s => s.nom.trim()).length === 0 || (isQuickStart && !manualAge)}
                    className="sp-btn sp-btn-primary"
                    style={{ minWidth: '220px' }}
                  >
                    {loading ? <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Analyse en cours...</> : <><Brain size={16} /> Lancer l'analyse préliminaire</>}
                  </button>
                  {symptomes.filter(s => s.nom.trim()).length === 0 && (
                    <p style={{ color: '#EF4444', fontSize: '12px', marginTop: '10px' }}>⚠ Veuillez saisir au moins un symptôme</p>
                  )}
                  {isQuickStart && !manualAge && (
                    <p style={{ color: '#EA580C', fontSize: '12px', marginTop: '6px' }}>⚠ Veuillez renseigner l'âge du patient</p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Étape 4 — Examens */}
          {step === 4 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>Examens Complémentaires</h2>
                {roleBadge('Médecin')}
              </div>
              <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '20px' }}>
                Les examens ci-dessous ont été suggérés par l'IA. Complétez les résultats, ajoutez ou supprimez des examens selon votre jugement clinique.
              </p>

              {examens.length > 0 && (
                <div style={{ marginBottom: '16px', padding: '12px 16px', background: '#FFFBEB', borderRadius: '8px', border: '1px solid #FCD34D', display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                  <Lightbulb size={16} style={{ color: '#D97706', flexShrink: 0, marginTop: '2px' }} />
                  <div style={{ fontSize: '13px', color: '#92400E' }}>
                    <strong>{examens.filter(e => e.isSuggested).length} examen(s)</strong> ont été pré-remplis par l'IA. Saisissez leurs résultats ou ajoutez d'autres examens.
                  </div>
                </div>
              )}

              {examens.map((ex, i) => (
                <div key={i} style={{ padding: '18px', background: ex.isSuggested ? '#F0FDF4' : '#F9FAFB', borderRadius: '12px', marginBottom: '12px', border: `1px solid ${ex.isSuggested ? '#86EFAC' : '#E5E7EB'}`, position: 'relative' }}>
                  {ex.isSuggested && (
                    <div style={{ 
                      position: 'absolute', 
                      top: '-10px', 
                      left: '16px', 
                      background: 'linear-gradient(135deg, #10B981, #059669)', 
                      color: '#fff', 
                      padding: '4px 12px', 
                      borderRadius: '12px', 
                      fontSize: '11px', 
                      fontWeight: 700,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      boxShadow: '0 2px 8px rgba(16, 185, 129, 0.3)'
                    }}>
                      <Brain size={12} />
                      SUGGESTION IA
                    </div>
                  )}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', marginTop: ex.isSuggested ? '8px' : '0' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 600, color: '#374151' }}>Examen {i + 1}</span>
                    </div>
                    <button type="button" onClick={() => removeExamen(i)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#EF4444' }}><X size={18} /></button>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '12px', marginBottom: '12px' }}>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Type</label>
                      <select className="sp-form-select" value={ex.type} onChange={e => editExamen(i, 'type', e.target.value)}>
                        <option value="BIOLOGIE">Biologie</option>
                        <option value="IMAGERIE">Imagerie</option>
                        <option value="ELECTROCARDIOGRAMME">ECG</option>
                        <option value="CLINIQUE">Clinique</option>
                      </select>
                    </div>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Nom de l'examen</label>
                      <select 
                        className="sp-form-select" 
                        value={ex.nom} 
                        onChange={e => editExamen(i, 'nom', e.target.value)}
                      >
                        <option value="">-- Sélectionner un examen --</option>
                        <optgroup label="🩸 Hématologie">
                          <option value="Hémoglobine">Hémoglobine (g/dL)</option>
                          <option value="Hématocrite">Hématocrite (%)</option>
                          <option value="Globules Rouges">Globules Rouges (M/µL)</option>
                          <option value="Globules Blancs">Globules Blancs (K/µL)</option>
                          <option value="Neutrophiles">Neutrophiles (%)</option>
                          <option value="Lymphocytes">Lymphocytes (%)</option>
                          <option value="Monocytes">Monocytes (%)</option>
                          <option value="Eosinophiles">Eosinophiles (%)</option>
                          <option value="Basophiles">Basophiles (%)</option>
                          <option value="Plaquettes">Plaquettes (K/µL)</option>
                          <option value="VGM">VGM (fL)</option>
                          <option value="CCMH">CCMH (g/dL)</option>
                        </optgroup>
                        <optgroup label="🍬 Métabolisme Glucidique">
                          <option value="Glucose">Glucose (mg/dL)</option>
                          <option value="Glucose à jeun">Glucose à jeun (mg/dL)</option>
                          <option value="Glucose post-prandial">Glucose post-prandial (mg/dL)</option>
                          <option value="HbA1c">HbA1c (%)</option>
                        </optgroup>
                        <optgroup label="💧 Lipides">
                          <option value="Cholestérol total">Cholestérol total (mg/dL)</option>
                          <option value="Cholestérol HDL">Cholestérol HDL (mg/dL)</option>
                          <option value="Cholestérol LDL">Cholestérol LDL (mg/dL)</option>
                          <option value="Triglycérides">Triglycérides (mg/dL)</option>
                          <option value="Acide urique">Acide urique (mg/dL)</option>
                        </optgroup>
                        <optgroup label="🫘 Fonction Rénale">
                          <option value="Créatinine">Créatinine (mg/dL)</option>
                          <option value="Urée">Urée (mg/dL)</option>
                          <option value="TFG">TFG (mL/min/1.73m²)</option>
                        </optgroup>
                        <optgroup label="⚡ Électrolytes">
                          <option value="Sodium">Sodium (mEq/L)</option>
                          <option value="Potassium">Potassium (mEq/L)</option>
                          <option value="Chlore">Chlore (mEq/L)</option>
                          <option value="Calcium">Calcium (mg/dL)</option>
                          <option value="Phosphore">Phosphore (mg/dL)</option>
                          <option value="Magnésium">Magnésium (mg/dL)</option>
                        </optgroup>
                        <optgroup label="🫀 Fonction Hépatique">
                          <option value="ALT/SGPT">ALT/SGPT (U/L)</option>
                          <option value="AST/SGOT">AST/SGOT (U/L)</option>
                          <option value="Bilirubine totale">Bilirubine totale (mg/dL)</option>
                          <option value="Bilirubine conjuguée">Bilirubine conjuguée (mg/dL)</option>
                          <option value="Bilirubine non-conjuguée">Bilirubine non-conjuguée (mg/dL)</option>
                          <option value="Phosphatase alcaline">Phosphatase alcaline (U/L)</option>
                          <option value="GGT">GGT (U/L)</option>
                          <option value="Albumine">Albumine (g/dL)</option>
                          <option value="Protéine totale">Protéine totale (g/dL)</option>
                          <option value="Globulines">Globulines (g/dL)</option>
                          <option value="Ratio A/G">Ratio A/G</option>
                        </optgroup>
                        <optgroup label="❤️ Marqueurs Cardiaques">
                          <option value="CK">CK (U/L)</option>
                          <option value="Myoglobine">Myoglobine (ng/mL)</option>
                          <option value="Troponine">Troponine (ng/mL)</option>
                          <option value="BNP">BNP (pg/mL)</option>
                          <option value="ProBNP">ProBNP (pg/mL)</option>
                        </optgroup>
                        <optgroup label="🩹 Coagulation">
                          <option value="PT/INR">PT/INR</option>
                          <option value="aPTT">aPTT (sec)</option>
                          <option value="TT">TT (sec)</option>
                          <option value="Fibrinogène">Fibrinogène (mg/dL)</option>
                        </optgroup>
                        <optgroup label="🔥 Marqueurs Inflammatoires">
                          <option value="CRP">CRP (mg/L)</option>
                          <option value="ESR">ESR (mm/h)</option>
                        </optgroup>
                        <optgroup label="🦠 Microbiologie">
                          <option value="BAAR (résultat)">BAAR - Test Tuberculose (0=NÉGATIF, 1=POSITIF)</option>
                          <option value="Culture Mycobactéries (résultat)">Culture Mycobactéries (0=NÉGATIF, 1=POSITIF)</option>
                          <option value="Test Xpert MTB/RIF (résultat)">Test Xpert MTB/RIF (0=NÉGATIF, 1=POSITIF)</option>
                        </optgroup>
                        <optgroup label="🔬 Autres">
                          <option value="PSA">PSA (ng/mL)</option>
                        </optgroup>
                      </select>
                    </div>
                  </div>
                  {ex.description && <p style={{ fontSize: '12px', color: '#6B7280', marginBottom: '12px', fontStyle: 'italic' }}>💡 {ex.description}</p>}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Valeur numérique</label>
                      <input type="number" step="0.01" className="sp-form-input" value={ex.valeur_numerique || ''} onChange={e => editExamen(i, 'valeur_numerique', e.target.value ? parseFloat(e.target.value) : undefined)} placeholder="12.5" />
                    </div>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Unité</label>
                      <select 
                        className="sp-form-select" 
                        value={ex.unite_mesure || ''} 
                        onChange={e => editExamen(i, 'unite_mesure', e.target.value)}
                      >
                        <option value="">-- Unité --</option>
                        {UNITES_EXAMEN.map(u => (
                          <option key={u} value={u}>{u}</option>
                        ))}
                      </select>
                    </div>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Date examen</label>
                      <input type="date" className="sp-form-input" value={ex.date_examen || ''} onChange={e => editExamen(i, 'date_examen', e.target.value)} />
                    </div>
                  </div>
                  <div className="sp-form-group">
                    <label className="sp-form-label">Résultats / Interprétation</label>
                    <textarea className="sp-form-textarea" rows={2} value={ex.resultats || ''} onChange={e => editExamen(i, 'resultats', e.target.value)} placeholder="Normal / Anormal — description des résultats..." />
                  </div>
                </div>
              ))}
              <button type="button" onClick={addExamen} className="sp-btn sp-btn-outline" style={{ width: '100%' }}>
                <Plus size={16} /> Ajouter un examen
              </button>
            </div>
          )}

          {/* Étape 5 — Diagnostic IA Final */}
          {step === 5 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>Diagnostic IA Final</h2>
                {roleBadge('IA', true)}
              </div>
              <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '24px' }}>
                L'IA effectue maintenant l'analyse complète : symptômes + signes vitaux + <strong>résultats des examens</strong> pour un diagnostic de précision optimale.
              </p>

              {analysePreliminaire && (
                <div style={{ padding: '14px 18px', background: '#F3F4F6', borderRadius: '8px', marginBottom: '20px', border: '1px solid #E5E7EB' }}>
                  <div style={{ fontSize: '11px', color: '#6B7280', fontWeight: 600, marginBottom: '6px' }}>HYPOTHÈSE PRÉLIMINAIRE (étape 3)</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontWeight: 600, color: '#374151' }}>{analysePreliminaire.maladie_predite}</span>
                    <span style={{ color: '#6B7280' }}>{(analysePreliminaire.confiance * 100).toFixed(1)}%</span>
                  </div>
                </div>
              )}

              {analyseFinale ? (
                <AICard analyse={analyseFinale} label="Diagnostic final (symptômes + signes vitaux + résultats examens)" />
              ) : (
                <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                  <div style={{ width: '72px', height: '72px', margin: '0 auto 16px', background: 'linear-gradient(135deg,#7C3AED,#EC4899)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Brain size={36} style={{ color: '#fff' }} />
                  </div>
                  <h3 style={{ fontSize: '17px', fontWeight: 600, marginBottom: '8px' }}>Analyse finale avec données complètes</h3>
                  <p style={{ color: '#6B7280', marginBottom: '8px', fontSize: '14px' }}>
                    {examens.filter(e => e.nom.trim()).length} examen(s) enregistré(s) — {examens.filter(e => e.valeur_numerique).length} avec valeur numérique
                  </p>
                  <p style={{ color: '#6B7280', marginBottom: '24px', fontSize: '13px' }}>
                    L'IA intègre tous les résultats d'examens pour affiner le diagnostic.
                  </p>
                  <button onClick={handleAnalyseFinale} disabled={loading} className="sp-btn sp-btn-primary" style={{ minWidth: '220px', background: 'linear-gradient(135deg,#7C3AED,#EC4899)', border: 'none' }}>
                    {loading ? <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Analyse finale...</> : <><Brain size={16} /> Lancer le diagnostic final</>}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Étape 6 — Validation */}
          {step === 6 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>Validation Médicale</h2>
                {roleBadge('Médecin')}
              </div>
              <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '24px' }}>Validez ou corrigez le diagnostic de l'IA. Votre jugement clinique a la priorité.</p>

              {analyseFinale && <AICard analyse={analyseFinale} label="Diagnostic proposé par l'IA — à valider" />}

              <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
                <button onClick={() => { setValidationDecision('confirme'); setDiagnosticFinal(analyseFinale?.maladie_predite || ''); }}
                  style={{ flex: 1, padding: '14px', background: validationDecision === 'confirme' ? '#059669' : '#fff', color: validationDecision === 'confirme' ? '#fff' : '#059669', border: '2px solid #059669', borderRadius: '10px', fontWeight: 700, fontSize: '14px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                  <CheckCircle size={18} /> Confirmer le diagnostic IA
                </button>
                <button onClick={() => { setValidationDecision('rejete'); setDiagnosticFinal(''); }}
                  style={{ flex: 1, padding: '14px', background: validationDecision === 'rejete' ? '#DC2626' : '#fff', color: validationDecision === 'rejete' ? '#fff' : '#DC2626', border: '2px solid #DC2626', borderRadius: '10px', fontWeight: 700, fontSize: '14px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                  <X size={18} /> Rejeter et corriger
                </button>
              </div>

              {validationDecision === 'confirme' && (
                <div style={{ padding: '14px 18px', background: '#ECFDF5', border: '1px solid #6EE7B7', borderRadius: '8px', marginBottom: '16px', color: '#065F46', fontWeight: 600, fontSize: '14px' }}>
                  ✓ Diagnostic confirmé : <strong>{diagnosticFinal}</strong>
                </div>
              )}
              {validationDecision === 'rejete' && (
                <div className="sp-form-group" style={{ marginBottom: '16px' }}>
                  <label className="sp-form-label">Diagnostic correct <span style={{ color: '#EF4444' }}>*</span></label>
                  <input className="sp-form-input" type="text" value={diagnosticCorrection} onChange={e => setDiagnosticCorrection(e.target.value)} placeholder="Saisissez votre diagnostic..." autoFocus />
                </div>
              )}

              <div className="sp-form-group">
                <label className="sp-form-label">Notes de validation (observations cliniques)</label>
                <textarea className="sp-form-textarea" rows={3} value={notesValidation} onChange={e => setNotesValidation(e.target.value)} placeholder="Observations, justification, commentaires cliniques..." />
              </div>

            </div>
          )}

          {/* Étape 7 — Ordonnance */}
          {step === 7 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>Ordonnance & Traitement</h2>
                {roleBadge('Médecin')}
              </div>
              <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '8px' }}>
                Diagnostic retenu : <strong style={{ color: '#4F46E5' }}>{validationDecision === 'rejete' ? diagnosticCorrection : diagnosticFinal}</strong>
              </p>
              <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '16px' }}>Prescrivez les médicaments et définissez le plan de traitement.</p>

              {/* Suggestions du catalogue par maladie — affichées comme chips/pills */}
              {catalogueLoading && (
                <div style={{ padding: '12px', background: '#EFF6FF', borderRadius: '8px', marginBottom: '16px', fontSize: '13px', color: '#3B82F6', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} />
                  Chargement des médicaments suggérés…
                </div>
              )}
              {!catalogueLoading && catalogueMeds.length > 0 && (() => {
                const diagLabel = validationDecision === 'rejete' ? diagnosticCorrection : diagnosticFinal;
                const catLabels: Record<string, string> = {
                  PREMIERE_INTENTION: '1ère intention',
                  DEUXIEME_INTENTION: '2ème intention',
                  ADJUVANT: 'Adjuvant',
                  SYMPTOMATIQUE: 'Symptomatique',
                };
                const catColors: Record<string, { dot: string; label: string; chipBg: string; chipBorder: string; chipText: string }> = {
                  PREMIERE_INTENTION: { dot: '#16A34A', label: '#15803D', chipBg: '#F0FDF4', chipBorder: '#86EFAC', chipText: '#166534' },
                  DEUXIEME_INTENTION: { dot: '#D97706', label: '#B45309', chipBg: '#FFFBEB', chipBorder: '#FCD34D', chipText: '#92400E' },
                  ADJUVANT:           { dot: '#2563EB', label: '#1D4ED8', chipBg: '#EFF6FF', chipBorder: '#93C5FD', chipText: '#1E40AF' },
                  SYMPTOMATIQUE:      { dot: '#7C3AED', label: '#6D28D9', chipBg: '#F5F3FF', chipBorder: '#C4B5FD', chipText: '#4C1D95' },
                };
                return (
                  <div style={{ marginBottom: '20px', border: '1px solid #C7D2FE', borderRadius: '12px', overflow: 'hidden' }}>
                    <div style={{ background: 'linear-gradient(135deg, #EEF2FF, #F5F3FF)', padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid #C7D2FE' }}>
                      <Lightbulb size={15} style={{ color: '#4F46E5' }} />
                      <span style={{ fontWeight: 700, fontSize: '13px', color: '#3730A3' }}>
                        Médicaments suggérés pour « {diagLabel} »
                      </span>
                      <span style={{ marginLeft: 'auto', fontSize: '11px', color: '#6B7280' }}>
                        Cliquez sur un médicament pour l'ajouter à l'ordonnance
                      </span>
                    </div>
                    <div style={{ padding: '16px', background: '#fff', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                      {(['PREMIERE_INTENTION', 'DEUXIEME_INTENTION', 'ADJUVANT', 'SYMPTOMATIQUE'] as const).map(cat => {
                        const meds = catalogueMeds.filter(m => (m as any).categorie === cat);
                        if (!meds.length) return null;
                        const col = catColors[cat];
                        return (
                          <div key={cat}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: col.dot, flexShrink: 0 }} />
                              <span style={{ fontSize: '11px', fontWeight: 700, color: col.label, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                                {catLabels[cat]}
                              </span>
                            </div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                              {meds.map(med => {
                                const dejaPrescrit = ordonnance.some(o => o.nom === med.nom_commercial);
                                return (
                                  <button
                                    key={med.id}
                                    type="button"
                                    onMouseDown={e => { e.preventDefault(); if (!dejaPrescrit) addMedFromCatalogue(med); }}
                                    title={[med.denomination_commune, med.dosage, med.frequence, med.duree_jours ? `${med.duree_jours} j` : ''].filter(Boolean).join(' · ')}
                                    style={{
                                      padding: '6px 14px',
                                      borderRadius: '999px',
                                      cursor: dejaPrescrit ? 'default' : 'pointer',
                                      border: `1px solid ${dejaPrescrit ? '#6EE7B7' : col.chipBorder}`,
                                      background: dejaPrescrit ? '#D1FAE5' : col.chipBg,
                                      color: dejaPrescrit ? '#065F46' : col.chipText,
                                      fontSize: '12px',
                                      fontWeight: 600,
                                      display: 'inline-flex',
                                      alignItems: 'center',
                                      gap: '5px',
                                      transition: 'all 0.15s',
                                      whiteSpace: 'nowrap',
                                    }}
                                  >
                                    {dejaPrescrit
                                      ? <CheckCircle size={12} style={{ flexShrink: 0 }} />
                                      : <Plus size={12} style={{ flexShrink: 0 }} />
                                    }
                                    {med.nom_commercial}
                                    {med.dosage && (
                                      <span style={{ fontWeight: 400, color: dejaPrescrit ? '#6EE7B7' : col.label, fontSize: '11px', opacity: 0.8 }}>
                                        {med.dosage}
                                      </span>
                                    )}
                                  </button>
                                );
                              })}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })()}

              {ordonnance.map((med, i) => (
                <div key={i} style={{ padding: '18px', background: '#F9FAFB', borderRadius: '12px', marginBottom: '12px', border: '1px solid #E5E7EB' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ fontWeight: 600, color: '#374151', display: 'flex', alignItems: 'center', gap: '6px' }}><Pill size={16} style={{ color: '#4F46E5' }} /> Médicament {i + 1}</span>
                    <button type="button" onClick={() => removeMed(i)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#EF4444' }}><X size={18} /></button>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Médicament <span style={{ color: '#EF4444' }}>*</span></label>
                      <input type="text" className="sp-form-input" value={med.nom} onChange={e => editMed(i, 'nom', e.target.value)} placeholder="Amoxicilline, Paracétamol..." />
                    </div>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Dosage</label>
                      <input type="text" className="sp-form-input" value={med.dosage} onChange={e => editMed(i, 'dosage', e.target.value)} placeholder="500mg, 1g..." />
                    </div>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Fréquence</label>
                      <select className="sp-form-select" value={med.frequence} onChange={e => editMed(i, 'frequence', e.target.value)}>
                        <optgroup label="Fréquence quotidienne">
                          <option>1×/jour</option>
                          <option>2×/jour</option>
                          <option>3×/jour</option>
                          <option>4×/jour</option>
                        </optgroup>
                        <optgroup label="Fréquence hebdomadaire">
                          <option>1×/2 jours</option>
                          <option>1×/3 jours</option>
                          <option>1×/semaine</option>
                          <option>2×/semaine</option>
                          <option>3×/semaine</option>
                        </optgroup>
                        <optgroup label="Fréquence mensuelle">
                          <option>1×/2 semaines</option>
                          <option>1×/3 semaines</option>
                          <option>1×/21 jours</option>
                          <option>1×/mois</option>
                        </optgroup>
                        <optgroup label="Horaires spécifiques">
                          <option>Toutes les 4 heures</option>
                          <option>Toutes les 6 heures</option>
                          <option>Toutes les 8 heures</option>
                          <option>Toutes les 12 heures</option>
                        </optgroup>
                        <optgroup label="Moments de la journée">
                          <option>Le matin</option>
                          <option>Le soir</option>
                          <option>Matin et soir</option>
                          <option>Matin, midi et soir</option>
                          <option>Au coucher</option>
                        </optgroup>
                        <optgroup label="Relation avec les repas">
                          <option>Avant les repas</option>
                          <option>Pendant les repas</option>
                          <option>Après les repas</option>
                        </optgroup>
                        <optgroup label="Autres">
                          <option>Si besoin (PRN)</option>
                          <option>En continu (perfusion)</option>
                          <option>En une seule prise</option>
                          <option>Au besoin</option>
                        </optgroup>
                      </select>
                    </div>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Durée (jours)</label>
                      <input type="number" min={1} className="sp-form-input" value={med.duree_jours} onChange={e => editMed(i, 'duree_jours', parseInt(e.target.value))} />
                    </div>
                  </div>
                  <div className="sp-form-group">
                    <label className="sp-form-label">Instructions / Précautions</label>
                    <textarea className="sp-form-textarea" rows={2} value={med.instructions || ''} onChange={e => editMed(i, 'instructions', e.target.value)} placeholder="À prendre pendant les repas, éviter l'alcool..." />
                  </div>
                </div>
              ))}
              <button type="button" onClick={addMed} className="sp-btn sp-btn-outline" style={{ width: '100%' }}>
                <Plus size={16} /> Ajouter un médicament
              </button>

              {ordonnance.length === 0 && (
                <div style={{ marginTop: '16px', padding: '14px', background: '#EFF6FF', borderRadius: '8px', border: '1px solid #BFDBFE', fontSize: '13px', color: '#1E40AF' }}>
                  <strong>Optionnel :</strong> Vous pouvez passer cette étape si aucune prescription n'est nécessaire.
                </div>
              )}
            </div>
          )}

          {/* Étape 8 — Suivi & Clôture */}
          {step === 8 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>Suivi & Clôture</h2>
                {roleBadge('Médecin')}
              </div>
              <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '24px' }}>Planifiez le suivi et finalisez la consultation.</p>

              {/* Récapitulatif final */}
              <div style={{ padding: '20px', background: 'linear-gradient(135deg,#F0FDF4,#ECFDF5)', borderRadius: '12px', border: '1px solid #86EFAC', marginBottom: '24px' }}>
                <div style={{ fontWeight: 700, color: '#166534', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ClipboardList size={18} /> Récapitulatif de la consultation
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  {[
                    { label: 'Patient', value: `${patient.prenoms} ${patient.nom}` },
                    { label: 'Diagnostic', value: validationDecision === 'rejete' ? diagnosticCorrection : diagnosticFinal },
                    { label: 'Symptômes', value: `${symptomes.filter(s => s.nom.trim()).length} saisis` },
                    { label: 'Examens', value: `${examens.filter(e => e.nom.trim()).length} réalisés` },
                    { label: 'Médicaments', value: `${ordonnance.filter(m => m.nom.trim()).length} prescrits` },
                    { label: 'Validation', value: validationDecision === 'confirme' ? '✓ Diagnostic IA confirmé' : '↩ Diagnostic corrigé' },
                  ].map(r => (
                    <div key={r.label} style={{ padding: '10px 14px', background: '#fff', borderRadius: '8px' }}>
                      <div style={{ fontSize: '11px', color: '#6B7280', fontWeight: 600, marginBottom: '3px' }}>{r.label.toUpperCase()}</div>
                      <div style={{ fontWeight: 600, color: '#1F2937', fontSize: '14px' }}>{r.value || '—'}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <div className="sp-form-group">
                  <label className="sp-form-label"><Calendar size={13} style={{ display: 'inline', marginRight: '5px' }} />Date prochain rendez-vous</label>
                  <input type="date" className="sp-form-input" value={suivi.date_prochain_rdv} onChange={e => setSuivi({ ...suivi, date_prochain_rdv: e.target.value })} />
                </div>
              </div>
              <div className="sp-form-group" style={{ marginBottom: '16px' }}>
                <label className="sp-form-label">Instructions pour le patient</label>
                <textarea className="sp-form-textarea" rows={3} value={suivi.instructions_patient} onChange={e => setSuivi({ ...suivi, instructions_patient: e.target.value })} placeholder="Repos, régime alimentaire, signes d'alarme à surveiller..." />
              </div>
              <div className="sp-form-group">
                <label className="sp-form-label">Notes de clôture (usage interne)</label>
                <textarea className="sp-form-textarea" rows={3} value={suivi.notes_medecin} onChange={e => setSuivi({ ...suivi, notes_medecin: e.target.value })} placeholder="Observations, éléments à surveiller, transmissions..." />
              </div>
            </div>
          )}

          {/* ── Navigation ── */}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '36px', paddingTop: '20px', borderTop: '1px solid #E5E7EB' }}>
            {/* Précédent : limité par stepMin */}
            <button
              onClick={() => {
                if (step <= stepMin && isMedecin) {
                  if (reprendreId) { safeNavigate('/consultations'); } else { isDirty ? (setPendingNavTo('search'), setLeaveModalOpen(true)) : setDoctorPhase('search'); }
                  return;
                }
                if (step <= stepMin && isInfirmier) {
                  isDirty ? (setPendingNavTo('infirmier-search'), setLeaveModalOpen(true)) : setInfirmierPhase('search');
                  return;
                }
                setStep(s => {
                  const next = Math.max(stepMin, s - 1);
                  // Retour avant l'analyse préliminaire → réinitialiser pour forcer un nouveau calcul
                  if (next < 3 && analysePreliminaire) {
                    setAnalysePreliminaire(null);
                    setExamens([]);
                  }
                  // Retour avant l'analyse finale → réinitialiser
                  if (next < 5 && analyseFinale) {
                    setAnalyseFinale(null);
                  }
                  return next;
                });
              }}
              disabled={step === stepMin && !isMedecin && !isInfirmier}
              className="sp-btn sp-btn-outline"
              style={{ opacity: step === stepMin && !isMedecin && !isInfirmier ? 0.4 : 1 }}
            >
              <ArrowLeft size={16} /> {step === stepMin && isMedecin ? (reprendreId ? 'Consultations' : 'Recherche') : step === stepMin && isInfirmier ? 'Recherche' : 'Précédent'}
            </button>

            {/* ── Étape 1 : Suivant pour infirmier/admin ou médecin nouveau ── */}
            {step === 1 && isInfirmier && (
              <button onClick={handleNextStep} disabled={loading} className="sp-btn sp-btn-primary" style={{ opacity: loading ? 0.7 : 1 }}>
                {loading ? <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Enregistrement...</> : <>Suivant <ArrowRight size={16} /></>}
              </button>
            )}

            {/* ── Étape 2 : admin & infirmier → envoyer au médecin ── */}
            {step === 2 && isInfirmier && (
              <button onClick={handleSubmitInfirmier} disabled={loading || !medecinId} className="sp-btn sp-btn-success" style={{ opacity: !medecinId ? 0.5 : 1 }}>
                {loading ? <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Envoi en cours...</> : <><Send size={16} /> Envoyer au médecin</>}
              </button>
            )}

            {/* ── Étape 2 : médecin nouveau patient → vers analyse IA ── */}
            {step === 2 && isMedecin && doctorMode === 'nouveau' && (
              <button
                onClick={() => {
                  if (symptomes.filter(s => s.nom.trim()).length === 0) {
                    showToast('Veuillez saisir au moins un symptôme avant de continuer', 'error');
                    return;
                  }
                  setStep(3);
                }}
                className="sp-btn sp-btn-primary"
              >
                Suivant <ArrowRight size={16} />
              </button>
            )}

            {/* ── Étape 3 : Analyse IA préliminaire ── */}
            {step === 3 && !analysePreliminaire && null}
            {step === 3 && analysePreliminaire && (
              <button onClick={() => setStep(4)} className="sp-btn sp-btn-primary">
                Saisir les examens <ArrowRight size={16} />
              </button>
            )}

            {/* ── Étape 4 → 5 ── */}
            {step === 4 && (
              <button onClick={() => setStep(5)} className="sp-btn sp-btn-primary">
                Lancer diagnostic final <ArrowRight size={16} />
              </button>
            )}

            {/* ── Étape 5 : Diagnostic IA final ── */}
            {step === 5 && !analyseFinale && null}
            {step === 5 && analyseFinale && (
              <button onClick={() => setStep(6)} className="sp-btn sp-btn-primary">
                Valider le diagnostic <ArrowRight size={16} />
              </button>
            )}

            {/* ── Étape 6 → 7 ── */}
            {step === 6 && (
              <button onClick={() => setStep(7)} disabled={!validationDecision || (validationDecision === 'rejete' && !diagnosticCorrection.trim())} className="sp-btn sp-btn-primary" style={{ opacity: !validationDecision || (validationDecision === 'rejete' && !diagnosticCorrection.trim()) ? 0.4 : 1 }}>
                Rédiger l'ordonnance <ArrowRight size={16} />
              </button>
            )}

            {/* ── Étape 7 → 8 ── */}
            {step === 7 && (
              <button onClick={() => setStep(8)} className="sp-btn sp-btn-primary">
                Planifier le suivi <ArrowRight size={16} />
              </button>
            )}

            {/* ── Étape 8 : soumission finale ── */}
            {step === 8 && (
              <button onClick={isReprendre ? handleSubmitComplet : handleSubmit} disabled={loading} className="sp-btn sp-btn-success">
                {loading ? <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Enregistrement...</> : <><CheckCircle size={16} /> Clôturer la consultation</>}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>

    {/* ── Modal confirmation quitter ── */}
    {leaveModalOpen && (
      <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ background: '#fff', borderRadius: '16px', padding: '32px', maxWidth: '440px', width: '90%', boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '50%', background: '#FEF3C7', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <AlertCircle size={22} style={{ color: '#D97706' }} />
            </div>
            <h3 style={{ fontSize: '17px', fontWeight: 700, color: '#1F2937', margin: 0 }}>Quitter la consultation ?</h3>
          </div>
          <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '12px', lineHeight: 1.6 }}>
            Vous allez quitter la consultation en cours.
          </p>
          {draftSavedAt ? (
            <div style={{ background: '#F0FDF4', border: '1px solid #86EFAC', borderRadius: '8px', padding: '10px 14px', marginBottom: '20px', fontSize: '13px', color: '#166534', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle size={14} style={{ flexShrink: 0 }} />
              <span>Vos données ont été sauvegardées automatiquement {formatDraftAge(draftSavedAt)}. Vous pourrez reprendre là où vous en étiez.</span>
            </div>
          ) : (
            <div style={{ background: '#FEF3C7', border: '1px solid #FCD34D', borderRadius: '8px', padding: '10px 14px', marginBottom: '20px', fontSize: '13px', color: '#92400E', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertCircle size={14} style={{ flexShrink: 0 }} />
              <span>Les données saisies mais non encore sauvegardées seront perdues.</span>
            </div>
          )}
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={() => { setLeaveModalOpen(false); setPendingNavTo(null); }}
              className="sp-btn sp-btn-outline"
              style={{ flex: 1 }}
            >
              Rester sur la page
            </button>
            <button
              onClick={() => {
                setLeaveModalOpen(false);
                if (pendingNavTo === 'search') { setDoctorPhase('search'); }
                else if (pendingNavTo === 'infirmier-search') { setInfirmierPhase('search'); }
                else if (pendingNavTo === -1) { navigate(-1); }
                else if (pendingNavTo) { navigate(pendingNavTo as string); }
                setPendingNavTo(null);
              }}
              className="sp-btn"
              style={{ flex: 1, background: '#EF4444', color: '#fff', border: 'none', borderRadius: '10px', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
            >
              Quitter quand même
            </button>
          </div>
        </div>
      </div>
    )}

    {/* ── Modal Symptômes & Signes Vitaux ── */}
    {showDonneesModal && (
      <div
        style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px' }}
        onClick={() => setShowDonneesModal(false)}
      >
        <div
          style={{ background: '#fff', borderRadius: '24px', width: '100%', maxWidth: '560px', maxHeight: '85vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }}
          onClick={e => e.stopPropagation()}
        >
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '20px 24px', borderBottom: '1px solid #E5E7EB', flexShrink: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ClipboardList size={18} style={{ color: '#fff' }} />
              </div>
              <div>
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: '#1F2937' }}>Données cliniques du patient</h3>
                <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>{patient.prenoms} {patient.nom}</p>
              </div>
            </div>
            <button onClick={() => setShowDonneesModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6B7280', padding: '4px' }}>
              <X size={20} />
            </button>
          </div>

          <div style={{ padding: '24px', overflowY: 'auto', flex: 1 }}>
            {/* Symptômes */}
            <div style={{ marginBottom: '24px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#4F46E5', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Activity size={14} /> Symptômes ({symptomes.filter(s => s.nom.trim()).length})
              </h4>
              {symptomes.filter(s => s.nom.trim()).length === 0 ? (
                <p style={{ color: '#9CA3AF', fontSize: '13px', fontStyle: 'italic' }}>Aucun symptôme saisi</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {symptomes.filter(s => s.nom.trim()).map((s, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: '#F9FAFB', borderRadius: '16px', border: '1px solid #E5E7EB' }}>
                      <div>
                        <span style={{ fontWeight: 600, color: '#1F2937', fontSize: '14px' }}>{s.nom}</span>
                        {s.description && <p style={{ margin: '2px 0 0', fontSize: '12px', color: '#6B7280' }}>{s.description}</p>}
                      </div>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexShrink: 0 }}>
                        <span style={{
                          padding: '2px 8px', borderRadius: '10px', fontSize: '11px', fontWeight: 600,
                          background: s.severite === 'Sévère' ? '#FEE2E2' : s.severite === 'Modérée' ? '#FEF3C7' : '#D1FAE5',
                          color: s.severite === 'Sévère' ? '#991B1B' : s.severite === 'Modérée' ? '#92400E' : '#065F46',
                        }}>{s.severite}</span>
                        <span style={{ fontSize: '12px', color: '#6B7280' }}>{s.duree_jours}j</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Signes vitaux */}
            <div>
              <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#4F46E5', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Heart size={14} /> Signes Vitaux
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                {[
                  { label: 'Tension artérielle', value: `${vitaux.tension_systolique}/${vitaux.tension_diastolique}`, unit: 'mmHg', alert: vitaux.tension_systolique > 140 || vitaux.tension_diastolique > 90 },
                  { label: 'Fréquence cardiaque', value: vitaux.frequence_cardiaque, unit: 'bpm', alert: vitaux.frequence_cardiaque > 100 || vitaux.frequence_cardiaque < 60 },
                  { label: 'Température', value: `${vitaux.temperature}`, unit: '°C', alert: vitaux.temperature >= 38.5 },
                  { label: 'Saturation O₂', value: `${vitaux.saturation_o2}`, unit: '%', alert: vitaux.saturation_o2 < 94 },
                  { label: 'Fréquence respiratoire', value: vitaux.frequence_respiratoire, unit: 'rpm', alert: vitaux.frequence_respiratoire > 20 },
                  ...(vitaux.poids ? [{ label: 'Poids', value: vitaux.poids, unit: 'kg', alert: false }] : []),
                  ...(vitaux.taille ? [{ label: 'Taille', value: vitaux.taille, unit: 'cm', alert: false }] : []),
                ].map((v, i) => (
                  <div key={i} style={{ padding: '12px 14px', background: v.alert ? '#FEF3C7' : '#F9FAFB', borderRadius: '16px', border: `1px solid ${v.alert ? '#FCD34D' : '#E5E7EB'}` }}>
                    <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>{v.label}</div>
                    <div style={{ fontWeight: 700, fontSize: '18px', color: v.alert ? '#92400E' : '#1F2937' }}>
                      {v.value} <span style={{ fontSize: '12px', fontWeight: 400, color: '#9CA3AF' }}>{v.unit}</span>
                    </div>
                    {v.alert && <div style={{ fontSize: '11px', color: '#D97706', marginTop: '2px', fontWeight: 600 }}>⚠ Valeur anormale</div>}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    )}
    </>
  );
}
