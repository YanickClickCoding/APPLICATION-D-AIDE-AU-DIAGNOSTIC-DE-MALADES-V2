import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../components/Toast';
import {
  User, Activity, Stethoscope, Brain, CheckCircle,
  ArrowRight, ArrowLeft, X, AlertCircle, Thermometer,
  Heart, Wind, Droplet, Weight, Ruler, FlaskConical,
  Pill, Calendar, Plus, Lightbulb, RefreshCw, ClipboardList
} from 'lucide-react';

// ─── Types ────────────────────────────────────────────────────────────────────

interface PatientData {
  nom: string; prenoms: string; date_naissance: string;
  sexe: 'M' | 'F'; telephone?: string; email?: string;
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

// ─── Exam suggestion engine ───────────────────────────────────────────────────

const EXAM_DEFAULTS: Record<string, { valeur_numerique?: number; unite_mesure?: string }> = {
  'NFS (Numération Formule Sanguine)':    { valeur_numerique: 13.0,  unite_mesure: 'g/dL'   },
  'CRP (Protéine C-réactive)':            { valeur_numerique: 5.0,   unite_mesure: 'mg/L'   },
  'Frottis sanguin + GE':                 {                           unite_mesure: 'résultat' },
  'TDR Paludisme':                        {                           unite_mesure: 'résultat' },
  'Radiographie thoracique':              {                           unite_mesure: 'rapport'  },
  'BAAR (crachat)':                       {                           unite_mesure: 'résultat' },
  'Hémoculture':                          {                           unite_mesure: 'résultat' },
  'Widal':                                { valeur_numerique: 80,    unite_mesure: 'titre'  },
  'Bilan hépatique (ASAT/ALAT/GGT)':      { valeur_numerique: 35,    unite_mesure: 'UI/L'   },
  'Bilirubine totale':                    { valeur_numerique: 10.0,  unite_mesure: 'µmol/L' },
  'Glycémie à jeun':                      { valeur_numerique: 5.0,   unite_mesure: 'mmol/L' },
  'HbA1c':                                { valeur_numerique: 5.5,   unite_mesure: '%'      },
  'ECG 12 dérivations':                   {                           unite_mesure: 'rapport'  },
  'Troponine I/T':                        { valeur_numerique: 0.01,  unite_mesure: 'ng/mL'  },
  'Créatinine + Urée':                    { valeur_numerique: 80,    unite_mesure: 'µmol/L' },
  'ECBU':                                 {                           unite_mesure: 'résultat' },
  'Bilan martial (fer + ferritine)':      { valeur_numerique: 50,    unite_mesure: 'µg/L'   },
  'Coproculture':                         {                           unite_mesure: 'résultat' },
};

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

  add({ type: 'BIOLOGIE', nom: 'NFS (Numération Formule Sanguine)', description: 'Bilan sanguin de base' });
  add({ type: 'BIOLOGIE', nom: 'CRP (Protéine C-réactive)', description: 'Marqueur inflammatoire' });

  predictions.slice(0, 3).forEach(({ maladie }) => {
    const m = maladie.toLowerCase();
    if (m.includes('malaria') || m.includes('paludisme'))
      { add({ type: 'BIOLOGIE', nom: 'Frottis sanguin + GE', description: 'Recherche Plasmodium' });
        add({ type: 'BIOLOGIE', nom: 'TDR Paludisme', description: 'Test rapide antigènes Plasmodium' }); }
    if (m.includes('pneumon') || m.includes('pulmon') || m.includes('bronch') || m.includes('tuberc'))
      { add({ type: 'IMAGERIE', nom: 'Radiographie thoracique', description: 'Condensation, épanchement, lésions' }); }
    if (m.includes('tuberc') || m.includes(' tb'))
      { add({ type: 'BIOLOGIE', nom: 'BAAR (crachat)', description: 'Recherche Bacilles de Koch' }); }
    if (m.includes('typhoid') || m.includes('typhoïde') || m.includes('salmonel'))
      { add({ type: 'BIOLOGIE', nom: 'Hémoculture', description: 'Culture bactérienne du sang' });
        add({ type: 'BIOLOGIE', nom: 'Widal', description: 'Sérologie anti-Salmonella' }); }
    if (m.includes('hepat'))
      { add({ type: 'BIOLOGIE', nom: 'Bilan hépatique (ASAT/ALAT/GGT)', description: 'Fonction hépatique' });
        add({ type: 'BIOLOGIE', nom: 'Bilirubine totale', description: 'Évaluation ictère' }); }
    if (m.includes('diabet') || m.includes('glucose') || m.includes('glyc'))
      { add({ type: 'BIOLOGIE', nom: 'Glycémie à jeun', description: 'Glucose sanguin' });
        add({ type: 'BIOLOGIE', nom: 'HbA1c', description: 'Hémoglobine glyquée' }); }
    if (m.includes('cardia') || m.includes('heart') || m.includes('coeur') || m.includes('infarct'))
      { add({ type: 'ELECTROCARDIOGRAMME', nom: 'ECG 12 dérivations', description: 'Rythme et conduction' });
        add({ type: 'BIOLOGIE', nom: 'Troponine I/T', description: 'Nécrose myocardique' }); }
    if (m.includes('renal') || m.includes('rein') || m.includes('nephro') || m.includes('kidney'))
      { add({ type: 'BIOLOGIE', nom: 'Créatinine + Urée', description: 'Fonction rénale' });
        add({ type: 'BIOLOGIE', nom: 'ECBU', description: 'Examen cytobactériologique des urines' }); }
    if (m.includes('anemi') || m.includes('anémie'))
      { add({ type: 'BIOLOGIE', nom: 'Bilan martial (fer + ferritine)', description: 'Carence en fer' }); }
    if (m.includes('cholera') || m.includes('diarrhee') || m.includes('diarrhée') || m.includes('gastro'))
      { add({ type: 'BIOLOGIE', nom: 'Coproculture', description: 'Recherche agent pathogène fécal' }); }
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
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // State par étape
  const [patient, setPatient] = useState<PatientData>({ nom: '', prenoms: '', date_naissance: '', sexe: 'M' });
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

  // ── Step actions ───────────────────────────────────────────────────────────

  const handleAnalysePreliminaire = async () => {
    setLoading(true);
    try {
      const result = await callIA(false);
      setAnalysePreliminaire(result);
      const suggestions = suggestExams(result.top_predictions);
      setExamens(suggestions);
      showToast('Analyse préliminaire effectuée — examens suggérés ci-dessous', 'success');
      setStep(5);
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
      await fetch('http://localhost:8000/api/consultations/workflow', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient, motif, symptomes, signes_vitaux: vitaux, examens,
          analyse_preliminaire: analysePreliminaire, analyse_finale: analyseFinale,
          diagnostic_final: finalDiag, validation_type: validationDecision,
          notes_validation: notesValidation, ordonnance, suivi,
        }),
      });
      showToast('Consultation enregistrée avec succès !', 'success');
      setTimeout(() => navigate('/consultations'), 1500);
    } catch { showToast('Erreur lors de l\'enregistrement', 'error'); }
    finally { setLoading(false); }
  };

  // ── Symptômes helpers ──────────────────────────────────────────────────────
  const addSymptome = () => setSymptomes([...symptomes, { nom: '', severite: 'Modérée', duree_jours: 1 }]);
  const removeSymptome = (i: number) => setSymptomes(symptomes.filter((_, idx) => idx !== i));
  const editSymptome = (i: number, f: keyof Symptome, v: any) => { const u = [...symptomes]; u[i] = { ...u[i], [f]: v }; setSymptomes(u); };

  // ── Examens helpers ────────────────────────────────────────────────────────
  const addExamen = () => setExamens([...examens, { type: 'BIOLOGIE', nom: '', resultats: '' }]);
  const removeExamen = (i: number) => setExamens(examens.filter((_, idx) => idx !== i));
  const editExamen = (i: number, f: keyof Examen, v: any) => { const u = [...examens]; u[i] = { ...u[i], [f]: v }; setExamens(u); };

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
  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <style>{`@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}`}</style>

      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Nouvelle Consultation</h1>
          <p className="sp-page-subtitle">Workflow assisté par IA · Étape {step}/{TOTAL}</p>
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
                {roleBadge('Accueil')}
              </div>
              <div className="sp-form-group" style={{ marginBottom: '16px' }}>
                <label className="sp-form-label">Motif de consultation <span style={{ color: '#EF4444' }}>*</span></label>
                <textarea className="sp-form-textarea" rows={2} value={motif} onChange={e => setMotif(e.target.value)} placeholder="Raison de la visite aujourd'hui..." />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                {[
                  { label: 'Nom', key: 'nom', type: 'text', required: true },
                  { label: 'Prénoms', key: 'prenoms', type: 'text', required: true },
                  { label: 'Date de naissance', key: 'date_naissance', type: 'date', required: true },
                  { label: 'Téléphone', key: 'telephone', type: 'tel' },
                  { label: 'Email', key: 'email', type: 'email' },
                ].map(f => (
                  <div key={f.key} className="sp-form-group">
                    <label className="sp-form-label">{f.label} {f.required && <span style={{ color: '#EF4444' }}>*</span>}</label>
                    <input type={f.type} className="sp-form-input" value={(patient as any)[f.key] || ''} onChange={e => setPatient({ ...patient, [f.key]: e.target.value })} />
                  </div>
                ))}
                <div className="sp-form-group">
                  <label className="sp-form-label">Sexe <span style={{ color: '#EF4444' }}>*</span></label>
                  <select className="sp-form-select" value={patient.sexe} onChange={e => setPatient({ ...patient, sexe: e.target.value as 'M' | 'F' })}>
                    <option value="M">Masculin</option><option value="F">Féminin</option>
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
                      <input type="text" className="sp-form-input" value={s.nom} onChange={e => editSymptome(i, 'nom', e.target.value)} placeholder="Fièvre, Toux, Céphalées..." />
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
                  { label: 'Tension systolique (mmHg)', key: 'tension_systolique', icon: Heart, step: 1 },
                  { label: 'Tension diastolique (mmHg)', key: 'tension_diastolique', icon: Heart, step: 1 },
                  { label: 'Fréquence cardiaque (bpm)', key: 'frequence_cardiaque', icon: Activity, step: 1 },
                  { label: 'Fréquence respiratoire (rpm)', key: 'frequence_respiratoire', icon: Wind, step: 1 },
                  { label: 'Température (°C)', key: 'temperature', icon: Thermometer, step: 0.1 },
                  { label: 'Saturation O₂ (%)', key: 'saturation_o2', icon: Droplet, step: 1 },
                  { label: 'Poids (kg) — optionnel', key: 'poids', icon: Weight, step: 0.1 },
                  { label: 'Taille (cm) — optionnel', key: 'taille', icon: Ruler, step: 1 },
                ].map(f => (
                  <div key={f.key} className="sp-form-group">
                    <label className="sp-form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <f.icon size={13} style={{ color: '#9CA3AF' }} />{f.label}
                    </label>
                    <input type="number" step={f.step} className="sp-form-input"
                      value={(vitaux as any)[f.key] || ''}
                      onChange={e => setVitaux({ ...vitaux, [f.key]: f.step < 1 ? parseFloat(e.target.value) : e.target.value ? parseInt(e.target.value) : undefined })} />
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
                  <div style={{ padding: '14px 18px', background: '#ECFDF5', borderRadius: '8px', border: '1px solid #6EE7B7', display: 'flex', gap: '10px' }}>
                    <Lightbulb size={18} style={{ color: '#059669', flexShrink: 0, marginTop: '2px' }} />
                    <div style={{ fontSize: '13px', color: '#065F46' }}>
                      <strong>Examens suggérés :</strong> {examens.length} examen(s) ont été pré-remplis à l'étape suivante selon les hypothèses de l'IA. Le médecin peut les modifier.
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
                <div key={i} style={{ padding: '18px', background: ex.isSuggested ? '#F0FDF4' : '#F9FAFB', borderRadius: '12px', marginBottom: '12px', border: `1px solid ${ex.isSuggested ? '#86EFAC' : '#E5E7EB'}` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 600, color: '#374151' }}>Examen {i + 1}</span>
                      {ex.isSuggested && <span style={{ fontSize: '10px', background: '#DCFCE7', color: '#166534', padding: '2px 8px', borderRadius: '10px', fontWeight: 600 }}>Suggéré par IA</span>}
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
                      <input type="text" className="sp-form-input" value={ex.nom} onChange={e => editExamen(i, 'nom', e.target.value)} placeholder="NFS, CRP, Radio thorax..." />
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
                      <input type="text" className="sp-form-input" value={ex.unite_mesure || ''} onChange={e => editExamen(i, 'unite_mesure', e.target.value)} placeholder="g/L, mmol/L..." />
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
                        <option>1×/jour</option><option>2×/jour</option><option>3×/jour</option>
                        <option>4×/jour</option><option>1×/semaine</option><option>Au besoin</option>
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

            {/* Étapes normales : bouton Suivant */}
            {step < 4 && (
              <button onClick={() => setStep(s => s + 1)} className="sp-btn sp-btn-primary">
                Suivant <ArrowRight size={16} />
              </button>
            )}

            {/* Étape 4 : déclenchement IA préliminaire */}
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

            {/* Étape 9 : soumission finale */}
            {step === 9 && (
              <button onClick={handleSubmit} disabled={loading} className="sp-btn sp-btn-success">
                {loading ? <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Enregistrement...</> : <><CheckCircle size={16} /> Clôturer la consultation</>}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
