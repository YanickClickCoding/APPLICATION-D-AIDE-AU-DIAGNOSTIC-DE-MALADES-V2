import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useToast } from '../components/Toast';
import { useAuth } from '../context/AuthContext';
import {
  User, Activity, Stethoscope, Brain, CheckCircle,
  ArrowRight, ArrowLeft, X, AlertCircle, Thermometer,
  Heart, Wind, Droplet, Weight, Ruler, FlaskConical,
  Pill, Calendar, Plus, Lightbulb, RefreshCw, ClipboardList,
  UserCheck, Send, Search
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
}
interface SuiviData {
  date_prochain_rdv: string; instructions_patient: string; notes_medecin: string;
}

// ─── Symptom autocomplete list ────────────────────────────────────────────────

// Liste complète des 332 symptômes supportés par le modèle ML (extraits du metadata)
const SYMPTOMES_SUPPORTES = [
  "Adénopathie", "Agrandissement des mains pieds", "Albuminémie basse", "Anémie", "Angioedème", "Anorexie", "Anxiété", "Apnée du sommeil", "Arthralgie", "Ascite", "Atrophie musculaire", "Aucun symptôme", "Aucun symptôme habituellement", "Aura", "Ballonnements", "Besoin fréquent d'uriner", "Besoin impérieux de déféquer", "Bleus faciles", "Brûlures d'estomac", "Bulles", "Céphalées", "Cervicite", "Chaleur", "Chancre", "Cheveux cassants", "Choc", "Chute", "Cicatrices", "Cicatrisation lente", "Claudication", "Comédones", "Complications neuro", "Comportement inapproprié", "Confusion", "Congestion nasale", "Constipation", "Convulsions", "Crampes", "Crampes abdominales", "Crevasses", "Cyanose", "Déformation progressive", "Délirium", "Démangeaisons", "Démangeaisons nasales", "Démence", "Dépigmentation", "Dépôts lipidiques aux paupières", "Dépression", "Désorientaton", "Desquamation", "Diarrhée", "Diarrhée sanguinolente", "Difficulté à avaler", "Difficulté à parler", "Difficulté à respirer", "Difficulté de lecture", "Difficulté nocturne", "Difficultés à avaler", "Difficultés à parler", "Difficultés à uriner", "Difficultés de langage", "Difficultés de vision", "Douleur", "Douleur à l'effort", "Douleur abdominale", "Douleur abdominale supérieure", "Douleur articulaire soudaine", "Douleur au bras", "Douleur au bras épaule", "Douleur au repas", "Douleur auriculaire", "Douleur colique intense", "Douleur épigastrique", "Douleur faciale", "Douleur lombaire", "Douleur neuropathique", "Douleur oculaire", "Douleur pelvienne", "Douleur pelvi-périnéale", "Douleur périnéale", "Douleur testiculaire", "Douleur thoracique", "Douleur thoracique pleurétique", "Douleur thoracique sévère", "Douleur thyroïdienne", "Douleurs abdominales", "Douleurs articulaires", "Douleurs musculaires", "Douleurs musculaires diffuses", "Douleurs osseuses", "Durcissement cutané", "Dysarthrie", "Dysparéunie", "Dysphagie", "Dyspnée", "Dysurie", "Ecchymoses", "Écoulement", "Écoulement auriculaire", "Écoulement nasal", "Écoulement puriforme", "Écoulement urétral", "Efforts pour déféquer", "Éjaculation douloureuse", "Encéphalopathie", "Engourdissement", "Engourdissement des pieds", "Epistaxis", "Épistaxis", "Érosions", "Éruption", "Éruption cutanée", "Éruption malaire", "Éruption prurigineuse", "Essoufflement", "Essoufflement soudain", "Éternuements", "Évanouissement", "Évanouissements", "Excroissance cutanée", "Faiblesse", "Faiblesse ascendante", "Faiblesse musculaire", "Faiblesse soudaine", "Fatigue", "Fatigue oculaire", "Fatigue post-critique", "Fièvre", "Fièvre élevée", "Fièvre intermittente", "Fistules", "Flotteurs", "Flux faible", "Fragilité osseuse", "Fréquence urinaire", "Frissons", "Froid excessif", "Frottement péricardique", "Ganglions enflés", "Gaz", "Généralement sans symptôme", "Gonflement", "Gonflement des chevilles", "Gonflement des lèvres", "Gonflement d'un membre", "Grossissement du visage", "Groupées ou dispersées", "Halos colorés", "Hématurie", "Hémoptysie", "Hémorragie digestive", "Hépatomégalie", "Histaminémie", "Hoarseness", "Hypercholangiite", "Hyperlipidémie", "Hyperpigmentation", "Hypertension", "Hypertension portale", "Hypotension", "Ictère", "Impact psychologique", "Incontinence", "Infection", "Infections", "Infections fréquentes", "Infections urinaires", "Infectiosus", "Infectiosus secondaires", "Infrequence des selles", "Injection conjonctivale", "Insomnie", "Intolérance à la chaleur", "Irritabilité", "Jaunisse", "Keratitis", "Larmoiement", "Lenteur de mouvement", "Lignes ondulées", "Lymphadénopathie", "Mal de gorge", "Mal de tête", "Malabsorption", "Malaise", "Malaise général", "Maux de tête", "Maux de tête diffus", "Maux de tête matinaux", "Maux de tête sévère", "Maux de tête sévères", "Mélæna", "Mucus dans les selles", "Nausées", "Nervosité", "Nocturia", "Nodules", "Nycturie", "Œdème pulmonaire", "Œdèmes", "Oligurie ou polyurie", "Oppression thoracique", "Otalgie", "Pâleur", "Palpitations", "Papules", "Paralysie", "Paresthésies", "Peau sèche", "Pérachie", "Perte d'appétit", "Perte d'audition", "Perte d'autonomie", "Perte de conscience", "Perte de goût", "Perte de mémoire", "Perte de poids", "Perte de réflexes", "Perte de vision", "Perte de vision progressive", "Perte de voix", "Perte d'odorat", "Petites bosses ombiliquées", "Phonophobie", "Photophobie", "Photosensibilité", "Plaques rouges squameuses", "Plissement des yeux", "Prise de poids", "Prise de poids rapide", "Production d'expectorations", "Protéinurie", "Prurit", "Prurit sévère", "Pustules", "Raideur matinale", "Ralentissement intellectuel", "Rash", "Rash photosensible", "Rash rose", "Raucité", "Raynaud", "Récidives", "Reflux gastro-esophagien", "Régurgitation", "Respiration sifflante", "Restriction de mobilité", "Rigidité", "Ronflement", "Rot", "Rougeur", "Rougeur cutanée", "Rougeur oculaire", "Rougeur pharyngée", "Saignement", "Saignement des plaques", "Saignement digestif", "Saignements", "Saignements de nez", "Saignements prolongés", "Salpingite", "Scotome central", "Sécheresse", "Sécheresse buccale", "Sécheresse cutanée", "Sécheresse oculaire", "Selles dures", "Selles pâles", "Sensation d'accélération", "Sensation de ballonnement", "Sensation de blocage", "Sensation de pressure", "Sensation de satiété rapide", "Sensibilité à la lumière", "Sensibilité à la palpation", "Soif excessive", "Somnolence diurne", "Souvent asymptomatique", "Spasticité", "Splenomégalie", "Splénomégalie", "Stridor inspiratoire", "Sueurs", "Sueurs froides", "Sueurs nocturnes", "Syncope", "Taches blanches", "Taches de Koplik", "Taches sombres", "Tachycardie", "Thrombose", "Tophi", "Toux", "Toux aboyante", "Toux avec expectorations", "Toux persistante", "Toux sèche", "Tremblements", "Trouble de l'équilibre", "Trouble du sommeil", "Troubles cognitifs", "Troubles du sommeil", "Ulcérations", "Ulcères buccaux", "Ulcères des pieds", "Urétrite", "Urgence urinaire", "Urination fréquente", "Urine foncée", "Urines foncées", "Uveite", "Varices œsophagiennes", "Vergetures", "Verrue génitale", "Verrue plantaire douloureuse", "Verrues génitales", "Vertige", "Vertiges", "Vésicules", "Visage rouge", "Vision centrale floue", "Vision floue", "Vision floue à toutes distances", "Vision floue de loin", "Vision floue de près", "Vision jaunâtre", "Vision rapprochée floue", "Vision tunnel", "Vomissements", "Xanthomes", "Yeux rouges", "Yeux saillants"
];

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

const TOTAL = 9;

const steps = [
  { num: 1, title: 'Patient',       icon: User,          role: 'Accueil' },
  { num: 2, title: 'Symptômes',     icon: Activity,      role: 'Infirmier' },
  { num: 3, title: 'Signes Vitaux', icon: Stethoscope,   role: 'Infirmier' },
  { num: 4, title: 'Analyse IA',    icon: Brain,         role: 'IA',      special: true },
  { num: 5, title: 'Examens',       icon: FlaskConical,  role: 'Médecin' },
  { num: 6, title: 'Diagnostic IA', icon: Brain,         role: 'IA',      special: true },
  { num: 7, title: 'Validation',    icon: CheckCircle,   role: 'Médecin' },
  { num: 8, title: 'Ordonnance',    icon: Pill,          role: 'Médecin' },
  { num: 9, title: 'Suivi',         icon: Calendar,      role: 'Médecin' },
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

export default function ConsultationWorkflow() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();

  const reprendreId = searchParams.get('reprendre');
  const isInfirmier = user?.role === 'infirmier';
  const isAdmin = user?.role === 'admin';
  const isReprendre = !!reprendreId && !isInfirmier && !isAdmin;

  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [draftConsultationId, setDraftConsultationId] = useState<number | null>(null);

  // État infirmier
  const [medecinId, setMedecinId] = useState<number | null>(null);
  const [medecinSearch, setMedecinSearch] = useState('');
  const [medecins, setMedecins] = useState<{ id: number; nom: string; prenoms: string; specialite?: string }[]>([]);
  const [infirmierSubmitted, setInfirmierSubmitted] = useState(false);

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

  const filteredMedecins = medecins.filter(m => {
    const term = medecinSearch.toLowerCase();
    return (m.nom.toLowerCase().includes(term) || m.prenoms.toLowerCase().includes(term) || (m.specialite || '').toLowerCase().includes(term));
  });

  // ── helpers ────────────────────────────────────────────────────────────────

  const buildPayload = (withExams: boolean) => {
    const age = patient.date_naissance
      ? Math.floor((Date.now() - new Date(patient.date_naissance).getTime()) / (365.25 * 24 * 3600 * 1000))
      : 40;
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
    const res = await fetch('http://localhost:8000/api/ml/predict-direct', {
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

  // Infirmier ou Admin : charger la liste des médecins
  useEffect(() => {
    if (!isInfirmier && !isAdmin) return;
    fetch('http://localhost:8000/api/analytics/personnel/disponible')
      .then(r => r.json())
      .then(d => setMedecins((d.medecins?.liste || []).map((m: any) => ({ id: m.id, nom: m.nom, prenoms: m.prenoms, specialite: m.specialite }))))
      .catch(() => {});
  }, [isInfirmier, isAdmin]);

  // Médecin reprend une consultation existante
  useEffect(() => {
    if (!reprendreId || isInfirmier) return;
    fetch(`http://localhost:8000/api/consultations/${reprendreId}/donnees-resume`)
      .then(r => r.json())
      .then(d => {
        // Vérification de sécurité : Seul le médecin affecté peut reprendre
        if (user?.role === 'medecin' && user.medecin_id !== d.medecin_id) {
          showToast("Désolé, vous n'êtes pas le médecin affecté à cette consultation.", 'error');
          navigate('/consultations');
          return;
        }
        
        if (d.patient) setPatient(p => ({ ...p, ...d.patient }));
        if (d.motif) setMotif(d.motif);
        if (d.symptomes?.length) {
          const rev: Record<string, string> = { LEGER: 'Légère', MODERE: 'Modérée', SEVERE: 'Sévère' };
          setSymptomes(d.symptomes.map((s: any) => ({ nom: s.nom, severite: rev[s.severite] || 'Modérée', duree_jours: s.duree_jours, description: s.description || '' })));
        }
        if (d.signes_vitaux) setVitaux(v => ({ ...v, ...d.signes_vitaux }));
        if (d.analyse_preliminaire) {
          setAnalysePreliminaire(d.analyse_preliminaire);
          setExamens(suggestExams(d.analyse_preliminaire.top_predictions || []));
        }
        setStep(4);
      })
      .catch(() => showToast('Impossible de charger la consultation', 'error'));
  }, [reprendreId]);

  // ── Step actions ───────────────────────────────────────────────────────────

  // Étape 1 → 2 : enregistre le patient + crée la consultation draft
  const handleNextStep = async () => {
    if (!patient.nom.trim() || !patient.prenoms.trim() || !patient.date_naissance || !motif.trim()) {
      showToast('Veuillez remplir les champs obligatoires (nom, prénoms, date de naissance, motif)', 'error');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/consultations/init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient, motif, medecin_id: medecinId }),
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
      // On reste sur l'étape 4 pour visualiser les résultats avant de passer aux examens
      // setStep(5);
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
      setStep(7);
    } catch (e: any) { showToast(e.message || 'Erreur IA', 'error'); }
    finally { setLoading(false); }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const finalDiag = validationDecision === 'rejete' ? diagnosticCorrection : diagnosticFinal;
      const res = await fetch('http://localhost:8000/api/consultations/workflow', {
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
      showToast('Consultation enregistrée ! Affichage des diagnostics IA...', 'success');
      setTimeout(() => navigate('/diagnostics'), 1500);
    } catch (e: any) {
      showToast(e.message || 'Erreur lors de l\'enregistrement', 'error');
    } finally { setLoading(false); }
  };

  // Infirmier ou Admin soumet les étapes 1-3 et notifie le médecin
  const handleSubmitInfirmier = async () => {
    if (!medecinId) { showToast('Veuillez sélectionner un médecin', 'error'); return; }
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/consultations/workflow-partiel', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient, motif, symptomes, signes_vitaux: vitaux, analyse_preliminaire: analysePreliminaire, medecin_id: medecinId, consultation_id: draftConsultationId }),
      });
      if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || 'Erreur serveur'); }
      setInfirmierSubmitted(true);
      showToast('Consultation envoyée au médecin avec succès', 'success');
    } catch (e: any) { showToast(e.message || 'Erreur', 'error'); }
    finally { setLoading(false); }
  };

  // Médecin finalise une consultation reprise (étapes 5-9)
  const handleSubmitComplet = async () => {
    setLoading(true);
    try {
      const finalDiag = validationDecision === 'rejete' ? diagnosticCorrection : diagnosticFinal;
      const res = await fetch(`http://localhost:8000/api/consultations/${reprendreId}/workflow-complet`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ examens, analyse_finale: analyseFinale, diagnostic_final: finalDiag, validation_type: validationDecision, notes_validation: notesValidation, ordonnance, suivi }),
      });
      if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || 'Erreur serveur'); }
      showToast('Consultation complétée avec succès !', 'success');
      setTimeout(() => navigate('/consultations'), 1500);
    } catch (e: any) { showToast(e.message || 'Erreur', 'error'); }
    finally { setLoading(false); }
  };

  // ── Symptômes helpers ──────────────────────────────────────────────────────
  const addSymptome = () => setSymptomes([...symptomes, { nom: '', severite: 'Modérée', duree_jours: 1 }]);
  const removeSymptome = (i: number) => setSymptomes(symptomes.filter((_, idx) => idx !== i));
  const editSymptome = (i: number, f: keyof Symptome, v: any) => { const u = [...symptomes]; u[i] = { ...u[i], [f]: v }; setSymptomes(u); };

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

  // ── Stepper ────────────────────────────────────────────────────────────────
  const progress = ((step - 1) / (TOTAL - 1)) * 100;

  const AICard = ({ analyse, label }: { analyse: AnalyseIA; label: string }) => (
    <div style={{ padding: '20px', background: 'linear-gradient(135deg,#EEF2FF,#F5F3FF)', borderRadius: '12px', border: '2px solid #C7D2FE', marginBottom: '20px' }}>
      <div style={{ fontSize: '11px', fontWeight: 700, color: '#6366F1', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>
        🤖 {label}
      </div>
      <div style={{ fontSize: '22px', fontWeight: 800, color: '#3730A3', marginBottom: '10px' }}>{analyse.maladie_predite}</div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <span style={{ fontSize: '13px', color: '#6B7280' }}>Confiance :</span>
        <div style={{ flex: 1, height: '8px', background: '#E5E7EB', borderRadius: '4px', overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${analyse.confiance * 100}%`, background: analyse.confiance >= 0.7 ? 'linear-gradient(90deg,#10B981,#059669)' : analyse.confiance >= 0.5 ? 'linear-gradient(90deg,#F59E0B,#D97706)' : 'linear-gradient(90deg,#EF4444,#DC2626)', transition: 'width 0.6s ease' }} />
        </div>
        <strong style={{ color: analyse.confiance >= 0.7 ? '#059669' : analyse.confiance >= 0.5 ? '#D97706' : '#DC2626' }}>
          {(analyse.confiance * 100).toFixed(1)}%
        </strong>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {analyse.top_predictions.slice(0, 3).map((p, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: i === 0 ? 'rgba(79,70,229,0.08)' : '#fff', borderRadius: '8px', border: `1px solid ${i === 0 ? '#C7D2FE' : '#E5E7EB'}` }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ width: '24px', height: '24px', borderRadius: '50%', background: i === 0 ? '#4F46E5' : '#E5E7EB', color: i === 0 ? '#fff' : '#6B7280', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 700 }}>{i + 1}</div>
              <span style={{ fontWeight: i === 0 ? 700 : 500, color: '#1F2937', fontSize: '14px' }}>{p.maladie}</span>
            </div>
            <span style={{ fontWeight: 700, color: '#4F46E5', fontSize: '14px' }}>{(p.probabilite * 100).toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );

  // ── Render ─────────────────────────────────────────────────────────────────

  // Écran de confirmation infirmier après soumission
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
              Le médecin pourra continuer à partir de l'étape {isAdmin || isInfirmier ? 'Examens' : 'Symptômes'} pour finaliser le diagnostic.
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
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <style>{`@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}`}</style>

      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">
            {isReprendre ? `Continuer la consultation #${reprendreId}` : 'Nouvelle Consultation'}
          </h1>
          <p className="sp-page-subtitle">
            {isAdmin || isInfirmier ? 'Saisie initiale · Étapes 1–3' : `Workflow assisté par IA · Étape ${step}/${TOTAL}`}
          </p>
        </div>
      </div>

      {/* ── Stepper ── */}
      <div className="sp-card sp-fade-in" style={{ marginBottom: '20px', padding: '24px 28px' }}>
        <div style={{ position: 'relative' }}>
          <div style={{ position: 'absolute', top: '18px', left: '18px', right: '18px', height: '3px', background: '#E5E7EB', zIndex: 0 }}>
            <div style={{ height: '100%', background: 'linear-gradient(90deg,#4F46E5,#7C3AED)', width: `${progress}%`, transition: 'width 0.4s ease' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', position: 'relative', zIndex: 1 }}>
            {steps.map(s => {
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

      {/* ── Content ── */}
      <div className="sp-card sp-fade-in">
        <div style={{ padding: '32px' }}>

          {/* Étape 1 — Patient */}
          {step === 1 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>Informations du Patient</h2>
                {roleBadge(isAdmin ? 'Administrateur' : 'Accueil')}
              </div>
              {/* Sélecteur médecin — infirmier ou admin */}
              {(isInfirmier || isAdmin) && (
                <div style={{ marginBottom: '20px', padding: '16px', background: '#EEF2FF', borderRadius: '10px', border: '1px solid #C7D2FE' }}>
                  <label className="sp-form-label" style={{ color: '#4338CA', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                    <UserCheck size={14} />Médecin assigné <span style={{ color: '#EF4444' }}>*</span>
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

                  <select className="sp-form-select" value={medecinId || ''} onChange={e => setMedecinId(Number(e.target.value) || null)}>
                    <option value="">— {filteredMedecins.length === 0 ? 'Aucun médecin trouvé' : 'Sélectionner un médecin'} —</option>
                    {filteredMedecins.map(m => (
                      <option key={m.id} value={m.id}>Dr. {m.prenoms} {m.nom}{m.specialite ? ` — ${m.specialite}` : ''}</option>
                    ))}
                  </select>
                  <p style={{ fontSize: '12px', color: '#6366F1', margin: '8px 0 0' }}>
                    Ce médecin sera notifié pour continuer et finaliser la consultation à partir des examens.
                  </p>
                </div>
              )}

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
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>Saisie des Symptômes</h2>
                {roleBadge('Infirmier')}
              </div>
              {symptomes.map((s, i) => (
                <div key={i} style={{ padding: '18px', background: '#F9FAFB', borderRadius: '12px', marginBottom: '12px', border: '1px solid #E5E7EB' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ fontWeight: 600, color: '#374151' }}>Symptôme {i + 1}</span>
                    <button type="button" onClick={() => removeSymptome(i)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#EF4444' }}><X size={18} /></button>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '12px' }}>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Symptôme</label>
                      <input 
                        type="text" 
                        className="sp-form-input" 
                        value={s.nom} 
                        onChange={e => editSymptome(i, 'nom', e.target.value)} 
                        placeholder="Fièvre, Toux, Céphalées..." 
                        list="symptomes-datalist"
                        autoComplete="off"
                      />
                      <datalist id="symptomes-datalist">
                        {SYMPTOMES_SUPPORTES.map((symptome, idx) => (
                          <option key={idx} value={symptome} />
                        ))}
                      </datalist>
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
              <button type="button" onClick={addSymptome} className="sp-btn sp-btn-outline" style={{ width: '100%' }}>
                <Plus size={16} /> Ajouter un symptôme
              </button>
            </div>
          )}

          {/* Étape 3 — Signes Vitaux */}
          {step === 3 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>Mesure des Signes Vitaux</h2>
                {roleBadge('Infirmier')}
              </div>
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
                      onChange={e => setVitaux({ ...vitaux, [f.key]: parseFloat(e.target.value) || undefined })} />
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

          {/* Étape 4 — Analyse IA Préliminaire */}
          {step === 4 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>Analyse IA Préliminaire</h2>
                {roleBadge('IA + Médecin', true)}
              </div>
              <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '24px' }}>
                L'IA analyse les symptômes et signes vitaux pour formuler des hypothèses diagnostiques et recommander les examens à réaliser.
              </p>

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
                  <button onClick={handleAnalysePreliminaire} disabled={loading || symptomes.filter(s => s.nom.trim()).length === 0} className="sp-btn sp-btn-primary" style={{ minWidth: '220px' }}>
                    {loading ? <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Analyse en cours...</> : <><Brain size={16} /> Lancer l'analyse préliminaire</>}
                  </button>
                  {symptomes.filter(s => s.nom.trim()).length === 0 && (
                    <p style={{ color: '#EF4444', fontSize: '12px', marginTop: '10px' }}>⚠ Veuillez saisir au moins un symptôme</p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Étape 5 — Examens */}
          {step === 5 && (
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

          {/* Étape 6 — Diagnostic IA Final */}
          {step === 6 && (
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
                  <div style={{ fontSize: '11px', color: '#6B7280', fontWeight: 600, marginBottom: '6px' }}>HYPOTHÈSE PRÉLIMINAIRE (étape 4)</div>
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

          {/* Étape 7 — Validation */}
          {step === 7 && (
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

              <div style={{ padding: '14px 18px', background: '#FEF3C7', borderRadius: '8px', border: '1px solid #FCD34D', display: 'flex', gap: '10px', marginTop: '16px' }}>
                <AlertCircle size={18} style={{ color: '#D97706', flexShrink: 0, marginTop: '2px' }} />
                <div style={{ fontSize: '13px', color: '#92400E' }}>
                  <strong>Note :</strong> Le diagnostic final est sous votre responsabilité médicale. L'IA est un outil d'aide à la décision.
                </div>
              </div>
            </div>
          )}

          {/* Étape 8 — Ordonnance */}
          {step === 8 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>Ordonnance & Traitement</h2>
                {roleBadge('Médecin')}
              </div>
              <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '8px' }}>
                Diagnostic retenu : <strong style={{ color: '#4F46E5' }}>{validationDecision === 'rejete' ? diagnosticCorrection : diagnosticFinal}</strong>
              </p>
              <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '24px' }}>Prescrivez les médicaments et définissez le plan de traitement.</p>

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

          {/* Étape 9 — Suivi & Clôture */}
          {step === 9 && (
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
            <button onClick={() => setStep(s => Math.max(1, s - 1))} disabled={step === 1} className="sp-btn sp-btn-outline" style={{ opacity: step === 1 ? 0.4 : 1 }}>
              <ArrowLeft size={16} /> Précédent
            </button>

            {/* Étapes 1-2 : bouton Suivant pour tous */}
            {step < 3 && (
              <button
                onClick={step === 1 ? handleNextStep : () => setStep(s => s + 1)}
                disabled={step === 1 && loading}
                className="sp-btn sp-btn-primary"
                style={{ opacity: step === 1 && loading ? 0.7 : 1 }}
              >
                {step === 1 && loading
                  ? <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Enregistrement...</>
                  : <>Suivant <ArrowRight size={16} /></>}
              </button>
            )}

            {/* Étape 3 : infirmier soumet → médecin continue vers étape 4 */}
            {step === 3 && isInfirmier && (
              <button
                onClick={handleSubmitInfirmier}
                disabled={loading || !medecinId}
                className="sp-btn sp-btn-success"
                style={{ opacity: !medecinId ? 0.5 : 1 }}
              >
                {loading
                  ? <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Envoi en cours...</>
                  : <><Send size={16} /> Envoyer au médecin</>}
              </button>
            )}
            {step === 3 && !isInfirmier && (
              <button onClick={() => setStep(4)} className="sp-btn sp-btn-primary">
                Suivant <ArrowRight size={16} />
              </button>
            )}

            {/* Étape 4 : après analyse IA préliminaire → médecin saisit les examens */}
            {step === 4 && !analysePreliminaire && null}
            {step === 4 && analysePreliminaire && (
              <button onClick={() => setStep(5)} className="sp-btn sp-btn-primary">
                Saisir les examens <ArrowRight size={16} />
              </button>
            )}

            {/* Étape 5 → 6 */}
            {step === 5 && (
              <button onClick={() => setStep(6)} className="sp-btn sp-btn-primary">
                Lancer diagnostic final <ArrowRight size={16} />
              </button>
            )}

            {/* Étape 6 : déclenchement IA finale */}
            {step === 6 && !analyseFinale && null}
            {step === 6 && analyseFinale && (
              <button onClick={() => setStep(7)} className="sp-btn sp-btn-primary">
                Valider le diagnostic <ArrowRight size={16} />
              </button>
            )}

            {/* Étape 7 → 8 */}
            {step === 7 && (
              <button
                onClick={() => setStep(8)}
                disabled={!validationDecision || (validationDecision === 'rejete' && !diagnosticCorrection.trim())}
                className="sp-btn sp-btn-primary"
                style={{ opacity: !validationDecision || (validationDecision === 'rejete' && !diagnosticCorrection.trim()) ? 0.4 : 1 }}>
                Rédiger l'ordonnance <ArrowRight size={16} />
              </button>
            )}

            {/* Étape 8 → 9 */}
            {step === 8 && (
              <button onClick={() => setStep(9)} className="sp-btn sp-btn-primary">
                Planifier le suivi <ArrowRight size={16} />
              </button>
            )}

            {/* Étape 9 : soumission finale (reprendre = médecin complète, sinon workflow normal) */}
            {step === 9 && (
              <button onClick={isReprendre ? handleSubmitComplet : handleSubmit} disabled={loading} className="sp-btn sp-btn-success">
                {loading ? <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Enregistrement...</> : <><CheckCircle size={16} /> Clôturer la consultation</>}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
