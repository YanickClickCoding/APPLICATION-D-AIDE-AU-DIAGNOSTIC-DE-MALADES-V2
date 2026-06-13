import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Brain, RefreshCw, Play, CheckCircle, XCircle, Sliders,
  AlertTriangle, Activity, History, TrendingUp,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { adminAPI, type IAConfig } from '../services/api';

interface ModelPerformance {
  available: boolean;
  model_version?: string;
  metrics?: {
    accuracy: number; precision: number; recall: number; f1_score: number;
    n_samples?: number; n_features?: number; n_classes?: number; duration_s?: number;
  };
  feature_importance?: { features: string[]; importances: number[] };
  message?: string;
}
interface AIStats {
  total_predictions: number;
  avg_confidence_pct: number;
  confidence_distribution: { HIGH: number; MEDIUM: number; LOW: number };
  top_diseases: Array<{ disease: string; count: number }>;
}
interface TrainingSession {
  date: string; accuracy: number; precision: number; recall: number;
  f1_score: number; n_samples?: number; n_features?: number; n_classes?: number;
  duration_s?: number; n_estimators?: number; max_depth?: number;
}
interface TrainingState {
  status: 'idle' | 'running' | 'success' | 'error';
  started_at: string | null; finished_at: string | null;
  message: string;
  results: { accuracy: number; precision: number; recall: number; f1_score: number; n_samples: number; n_features: number; n_classes: number; duration_s: number; model_path: string } | null;
  error: string | null;
}

const Badge = ({ ok, label }: { ok: boolean; label: string }) => (
  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '3px 10px', borderRadius: 99, background: ok ? '#ECFDF5' : '#FEF2F2', color: ok ? '#065F46' : '#991B1B', fontSize: 12, fontWeight: 700 }}>
    {ok ? <CheckCircle size={12} /> : <XCircle size={12} />}{label}
  </span>
);
const ProgressBar = ({ pct, color = '#4F46E5' }: { pct: number; color?: string }) => (
  <div style={{ background: '#F3F4F6', borderRadius: 99, height: 8, overflow: 'hidden' }}>
    <div style={{ width: `${Math.min(100, pct)}%`, height: '100%', background: color, transition: 'width .4s ease', borderRadius: 99 }} />
  </div>
);
const Card = ({ title, icon: Icon, accent = '#4F46E5', children }: any) => (
  <div style={{ background: 'white', borderRadius: 16, padding: 24, border: '1px solid #E5E7EB', boxShadow: '0 1px 4px rgba(0,0,0,.05)', marginBottom: 20 }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
      <div style={{ background: accent + '18', borderRadius: 10, padding: 8 }}>
        <Icon size={20} style={{ color: accent }} />
      </div>
      <h2 style={{ fontSize: 16, fontWeight: 700, color: '#111827', margin: 0 }}>{title}</h2>
    </div>
    {children}
  </div>
);

export default function AdminML() {
  const { token } = useAuth();
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [showTrainWarning, setShowTrainWarning] = useState(false);
  const [loadingTrain, setLoadingTrain] = useState(false);
  const [training, setTraining] = useState<TrainingState | null>(null);
  const [nEstimators, setNEstimators] = useState(200);
  const [maxDepth, setMaxDepth] = useState(30);
  const [iaConfig, setIaConfig] = useState<IAConfig>({ seuil_confiance_min: 0.60, seuil_alerte_bas: 0.40, n_estimators: 200, max_depth: 30 });
  const [iaConfigDraft, setIaConfigDraft] = useState<IAConfig>({ seuil_confiance_min: 0.60, seuil_alerte_bas: 0.40, n_estimators: 200, max_depth: 30 });
  const [savingIA, setSavingIA] = useState(false);
  const [iaConfigDirty, setIaConfigDirty] = useState(false);
  const [modelPerf, setModelPerf] = useState<ModelPerformance | null>(null);
  const [aiStats, setAIStats] = useState<AIStats | null>(null);
  const [trainingHistory, setTrainingHistory] = useState<TrainingSession[]>([]);
  const [modelLoaded, setModelLoaded] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 4000);
  };

  const fetchAll = useCallback(async () => {
    if (!token) return;
    try {
      const [status, perf, stats, hist] = await Promise.all([
        adminAPI.getStatus(token),
        adminAPI.getModelPerformance(token),
        adminAPI.getAIStats(token),
        adminAPI.getTrainingHistory(token),
      ]);
      setModelLoaded(status.model?.loaded ?? false);
      setTraining(status.training);
      if (status.ia_config) {
        setIaConfig(status.ia_config);
        setIaConfigDraft(status.ia_config);
        setNEstimators(status.ia_config.n_estimators);
        setMaxDepth(status.ia_config.max_depth);
        setIaConfigDirty(false);
      }
      setModelPerf(perf);
      setAIStats(stats);
      setTrainingHistory(hist.sessions || []);
    } catch { /* silencieux */ }
  }, [token]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  useEffect(() => {
    if (training?.status === 'running') {
      pollRef.current = setInterval(async () => {
        if (!token) return;
        try {
          const data: TrainingState = await adminAPI.getTrainingStatus(token);
          setTraining(data);
          if (data.status !== 'running') {
            clearInterval(pollRef.current!);
            fetchAll();
            if (data.status === 'success') showToast('Entraînement terminé avec succès !');
            else showToast(data.error ?? 'Entraînement échoué', false);
          }
        } catch { /* ignore */ }
      }, 3000);
    }
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [training?.status, fetchAll, token]);

  const startTraining = async () => {
    if (!token) return;
    setLoadingTrain(true);
    try {
      await adminAPI.startTraining(token, nEstimators, maxDepth);
      setTraining({ status: 'running', started_at: new Date().toISOString(), finished_at: null, message: 'Initialisation…', results: null, error: null });
      showToast('Entraînement démarré en arrière-plan');
    } catch (e: any) {
      showToast(e.detail ?? e.message ?? 'Erreur', false);
    } finally {
      setLoadingTrain(false);
    }
  };

  const saveIAConfig = async () => {
    if (!token) return;
    setSavingIA(true);
    try {
      const updated = await adminAPI.updateIAConfig(token, iaConfigDraft);
      setIaConfig(updated); setIaConfigDraft(updated); setIaConfigDirty(false);
      showToast('Configuration IA sauvegardée');
    } catch (e: any) {
      showToast(e.detail ?? 'Erreur lors de la sauvegarde', false);
    } finally { setSavingIA(false); }
  };

  const updateDraft = (key: keyof IAConfig, value: number) => {
    setIaConfigDraft(prev => ({ ...prev, [key]: value }));
    setIaConfigDirty(true);
  };

  const trainingRunning = training?.status === 'running';

  return (
    <div style={{ maxWidth: 960, margin: '0 auto' }}>
      {/* Toast */}
      {toast && (
        <div style={{ position: 'fixed', top: 24, right: 24, zIndex: 9999, padding: '12px 20px', borderRadius: 10, color: 'white', background: toast.ok ? '#059669' : '#DC2626', boxShadow: '0 4px 20px rgba(0,0,0,.15)', display: 'flex', alignItems: 'center', gap: 8, fontSize: 14, fontWeight: 600 }}>
          {toast.ok ? <CheckCircle size={16} /> : <XCircle size={16} />}{toast.msg}
        </div>
      )}

      {/* Modal avertissement */}
      {showTrainWarning && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 10000, background: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}
          onClick={() => setShowTrainWarning(false)}>
          <div style={{ background: '#fff', borderRadius: 16, padding: '32px 36px', maxWidth: 540, width: '100%', boxShadow: '0 20px 60px rgba(0,0,0,0.25)' }}
            onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 20 }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: '#FEF3C7', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <AlertTriangle size={24} style={{ color: '#D97706' }} />
              </div>
              <div>
                <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: '#1F2937' }}>Avant de réentraîner</h2>
                <p style={{ margin: 0, fontSize: 13, color: '#6B7280' }}>Lire les informations importantes ci-dessous</p>
              </div>
            </div>
            <div style={{ background: '#F0FDF4', border: '1px solid #86EFAC', borderRadius: 10, padding: '12px 16px', marginBottom: 16 }}>
              <p style={{ margin: '0 0 6px', fontSize: 13, fontWeight: 700, color: '#166534' }}>Performances actuelles du modèle</p>
              <div style={{ display: 'flex', gap: 20 }}>
                <span style={{ fontSize: 13, color: '#15803D' }}>✓ Top-1 : <strong>90 %</strong> (45/50 maladies)</span>
                <span style={{ fontSize: 13, color: '#15803D' }}>✓ Top-3 : <strong>98 %</strong> (49/50 maladies)</span>
              </div>
            </div>
            <div style={{ background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: 10, padding: '12px 16px', marginBottom: 16 }}>
              <p style={{ margin: '0 0 8px', fontSize: 13, fontWeight: 700, color: '#92400E' }}>⚠️ Réentraîner sans modifier le dataset ne changera pas les résultats</p>
              <p style={{ margin: 0, fontSize: 12, color: '#78350F', lineHeight: 1.6 }}>
                Le modèle atteint déjà 84 % d'accuracy sur ses données de test. Les maladies ambiguës (DT1/DT2, HépA/HépB, RGO/Hernie) ne peuvent être distinguées sans sérologie.
              </p>
            </div>
            <div style={{ background: '#EFF6FF', border: '1px solid #BFDBFE', borderRadius: 10, padding: '12px 16px', marginBottom: 24 }}>
              <p style={{ margin: '0 0 6px', fontSize: 13, fontWeight: 700, color: '#1E40AF' }}>Ce qui améliorerait réellement le modèle</p>
              <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, color: '#1E3A8A', lineHeight: 1.8 }}>
                <li>Ajouter des features binaires dans le dataset (seuils HTA, anosmie, etc.)</li>
                <li>Augmenter le nombre de cas par maladie ambiguë (page Dataset)</li>
                <li>Inclure les résultats de sérologie comme feature discriminante</li>
              </ul>
            </div>
            <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
              <button onClick={() => setShowTrainWarning(false)} style={{ padding: '10px 20px', borderRadius: 8, border: '1px solid #D1D5DB', background: '#fff', color: '#374151', fontWeight: 600, fontSize: 14, cursor: 'pointer' }}>
                Annuler
              </button>
              <button onClick={() => { setShowTrainWarning(false); startTraining(); }} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 20px', borderRadius: 8, border: 'none', background: 'linear-gradient(135deg,#7C3AED,#4F46E5)', color: '#fff', fontWeight: 700, fontSize: 14, cursor: 'pointer' }}>
                <Play size={15} /> Lancer quand même
              </button>
            </div>
          </div>
        </div>
      )}

      {/* En-tête */}
      <div style={{ marginBottom: 28, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 900, color: '#111827', margin: 0 }}>Modèle IA & Entraînement</h1>
          <p style={{ color: '#6B7280', marginTop: 4, fontSize: 14 }}>
            Entraînez le modèle, ajustez la configuration IA, consultez performances et historique
          </p>
        </div>
        <button onClick={fetchAll} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px', borderRadius: 8, border: '1px solid #E5E7EB', background: 'white', cursor: 'pointer', fontSize: 13, fontWeight: 600, color: '#374151' }}>
          <RefreshCw size={14} /> Actualiser
        </button>
      </div>

      {/* ─── Entraîner le modèle ─── */}
      <Card title="Entraîner le modèle ML" icon={Brain} accent="#7C3AED">
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end', flexWrap: 'wrap', marginBottom: 12 }}>
          <div>
            <label style={{ fontSize: 11, color: '#6B7280', fontWeight: 600, display: 'block', marginBottom: 4 }}>Nombre d'arbres</label>
            <input type="number" value={nEstimators} min={50} max={500} step={50}
              onChange={e => setNEstimators(+e.target.value)}
              style={{ width: 100, padding: '6px 10px', borderRadius: 6, border: '1px solid #D1D5DB', fontSize: 13 }}
              disabled={trainingRunning} />
          </div>
          <div>
            <label style={{ fontSize: 11, color: '#6B7280', fontWeight: 600, display: 'block', marginBottom: 4 }}>Profondeur max</label>
            <input type="number" value={maxDepth} min={5} max={60} step={5}
              onChange={e => setMaxDepth(+e.target.value)}
              style={{ width: 100, padding: '6px 10px', borderRadius: 6, border: '1px solid #D1D5DB', fontSize: 13 }}
              disabled={trainingRunning} />
          </div>
          <button
            onClick={() => setShowTrainWarning(true)}
            disabled={trainingRunning || loadingTrain}
            style={{
              display: 'flex', alignItems: 'center', gap: 8,
              padding: '9px 20px', borderRadius: 8, border: 'none',
              cursor: trainingRunning ? 'not-allowed' : 'pointer',
              background: trainingRunning ? '#E5E7EB' : 'linear-gradient(135deg,#7C3AED,#4F46E5)',
              color: trainingRunning ? '#9CA3AF' : 'white', fontWeight: 700, fontSize: 14,
              opacity: trainingRunning ? 0.7 : 1,
            }}
          >
            {trainingRunning
              ? <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Entraînement en cours…</>
              : <><Play size={16} /> {modelLoaded ? 'Réentraîner le modèle' : 'Entraîner le modèle'}</>}
          </button>
        </div>

        {training && training.status !== 'idle' && (
          <div style={{
            marginTop: 12, padding: 16, borderRadius: 10,
            background: training.status === 'success' ? '#ECFDF5' : training.status === 'error' ? '#FEF2F2' : '#EEF2FF',
            border: `1px solid ${training.status === 'success' ? '#6EE7B7' : training.status === 'error' ? '#FECACA' : '#C7D2FE'}`,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              {training.status === 'running' && <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite', color: '#4F46E5' }} />}
              {training.status === 'success' && <CheckCircle size={14} style={{ color: '#059669' }} />}
              {training.status === 'error' && <XCircle size={14} style={{ color: '#DC2626' }} />}
              <span style={{ fontSize: 13, fontWeight: 600, color: training.status === 'success' ? '#065F46' : training.status === 'error' ? '#991B1B' : '#3730A3' }}>
                {training.message}
              </span>
            </div>
            {training.status === 'running' && (
              <div style={{ overflow: 'hidden', borderRadius: 99, background: '#C7D2FE', height: 6 }}>
                <div style={{ height: '100%', width: '40%', background: '#4F46E5', animation: 'pulse 2s infinite', borderRadius: 99 }} />
              </div>
            )}
            {training.status === 'error' && <p style={{ fontSize: 12, color: '#991B1B', margin: 0 }}>{training.error}</p>}
            {training.results && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginTop: 12 }}>
                {([['Précision', training.results.accuracy, '%'], ['F1-Score', training.results.f1_score, '%'], ['Classes', training.results.n_classes, ''], ['Durée', training.results.duration_s, 's']] as [string, any, string][]).map(([label, val, unit]) => (
                  <div key={label} style={{ textAlign: 'center', background: 'white', borderRadius: 8, padding: '8px 4px' }}>
                    <div className="sp-number sp-number-sm" style={{ color: '#065F46' }}>{val}{unit}</div>
                    <div style={{ fontSize: 10, color: '#6B7280', fontWeight: 600 }}>{label}</div>
                  </div>
                ))}
              </div>
            )}
            {training.started_at && (
              <div style={{ fontSize: 11, color: '#9CA3AF', marginTop: 10 }}>
                Démarré : {new Date(training.started_at).toLocaleString('fr-FR')}
                {training.finished_at && ` — Terminé : ${new Date(training.finished_at).toLocaleString('fr-FR')}`}
              </div>
            )}
          </div>
        )}
      </Card>

      {/* ─── Config IA ─── */}
      <Card title="Configuration de l'IA" icon={Sliders} accent="#0891B2">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 20, marginBottom: 20 }}>
          {([
            ['seuil_confiance_min', 'Seuil confiance minimum', 0, 1, 0.05, '#0891B2', 'En-dessous, le diagnostic est marqué incertain', v => `${Math.round(v * 100)}%`],
            ['seuil_alerte_bas', 'Seuil alerte basse confiance', 0, 0.8, 0.05, '#DC2626', 'En-dessous, une alerte rouge est affichée', v => `${Math.round(v * 100)}%`],
            ['n_estimators', 'Arbres pour le prochain entraînement', 50, 500, 50, '#7C3AED', 'Plus = meilleure précision, mais plus lent', v => `${v}`],
            ['max_depth', 'Profondeur max des arbres', 5, 60, 5, '#059669', 'Plus élevé = peut sur-apprendre', v => `${v}`],
          ] as [keyof IAConfig, string, number, number, number, string, string, (v: number) => string][]).map(([key, label, min, max, step, color, desc, fmt]) => (
            <div key={key}>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>
                {label}
                <span style={{ float: 'right', color, fontWeight: 700 }}>{fmt(iaConfigDraft[key] as number)}</span>
              </label>
              <input type="range" min={min} max={max} step={step}
                value={iaConfigDraft[key] as number}
                onChange={e => updateDraft(key, key === 'n_estimators' || key === 'max_depth' ? parseInt(e.target.value) : parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: color }} />
              <p style={{ fontSize: 11, color: '#6B7280', margin: '4px 0 0' }}>{desc}</p>
            </div>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 16, padding: '10px 14px', background: '#F0F9FF', borderRadius: 8, border: '1px solid #BAE6FD' }}>
          <span style={{ fontSize: 12, color: '#0369A1', fontWeight: 600 }}>Actuels :</span>
          <span style={{ fontSize: 12, color: '#374151' }}>Confiance min : <strong>{Math.round(iaConfig.seuil_confiance_min * 100)}%</strong></span>
          <span style={{ fontSize: 12, color: '#374151' }}>Alerte : <strong>{Math.round(iaConfig.seuil_alerte_bas * 100)}%</strong></span>
          <span style={{ fontSize: 12, color: '#374151' }}>Arbres : <strong>{iaConfig.n_estimators}</strong></span>
          <span style={{ fontSize: 12, color: '#374151' }}>Profondeur : <strong>{iaConfig.max_depth}</strong></span>
        </div>
        <button onClick={saveIAConfig} disabled={!iaConfigDirty || savingIA}
          style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '9px 20px', borderRadius: 8, border: 'none', cursor: !iaConfigDirty || savingIA ? 'not-allowed' : 'pointer', background: iaConfigDirty ? 'linear-gradient(135deg,#0891B2,#0369A1)' : '#E5E7EB', color: iaConfigDirty ? 'white' : '#9CA3AF', fontWeight: 700, fontSize: 14, opacity: !iaConfigDirty ? 0.6 : 1 }}>
          {savingIA ? <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <CheckCircle size={16} />}
          {savingIA ? 'Sauvegarde...' : iaConfigDirty ? 'Sauvegarder la configuration' : 'Configuration à jour'}
        </button>
      </Card>

      {/* ─── Performances ─── */}
      {modelPerf?.available && modelPerf.metrics && (
        <Card title="Performances du modèle (dernière session)" icon={TrendingUp} accent="#059669">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 24 }}>
            {([['Accuracy', modelPerf.metrics.accuracy, '#4F46E5'], ['Précision', modelPerf.metrics.precision, '#059669'], ['Rappel', modelPerf.metrics.recall, '#D97706'], ['F1-Score', modelPerf.metrics.f1_score, '#DB2777']] as [string, number, string][]).map(([label, val, color]) => (
              <div key={label} style={{ background: '#F9FAFB', borderRadius: 12, padding: '14px 16px', border: '1px solid #E5E7EB' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ fontSize: 12, fontWeight: 600, color: '#374151' }}>{label}</span>
                  <span style={{ fontSize: 15, fontWeight: 800, color }}>{val?.toFixed(2)} %</span>
                </div>
                <ProgressBar pct={val ?? 0} color={color} />
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 20 }}>
            {[['Observations', modelPerf.metrics.n_samples?.toLocaleString('fr-FR')], ['Features', modelPerf.metrics.n_features], ['Classes', modelPerf.metrics.n_classes], ['Durée', modelPerf.metrics.duration_s != null ? `${modelPerf.metrics.duration_s} s` : '—']].map(([lbl, val]) => val != null && (
              <span key={lbl as string} style={{ fontSize: 12, color: '#374151', background: '#EEF2FF', padding: '4px 10px', borderRadius: 6, fontWeight: 600 }}>
                {lbl} : <strong>{val}</strong>
              </span>
            ))}
          </div>
          {modelPerf.feature_importance && modelPerf.feature_importance.features.length > 0 && (
            <>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#374151', marginBottom: 12, borderTop: '1px solid #E5E7EB', paddingTop: 16 }}>
                Top {modelPerf.feature_importance.features.length} Features — Impact sur la décision IA
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {modelPerf.feature_importance.features.map((feat, i) => {
                  const imp = modelPerf.feature_importance!.importances[i];
                  const maxImp = modelPerf.feature_importance!.importances[0];
                  const pct = maxImp > 0 ? (imp / maxImp) * 100 : 0;
                  const shortName = feat.replace(/^(Lab_|Vital_|SYM_)/, '').replace(/_/g, ' ').substring(0, 40);
                  const isSym = feat.startsWith('SYM_');
                  return (
                    <div key={feat} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ fontSize: 10, fontWeight: 700, padding: '1px 6px', borderRadius: 4, background: isSym ? '#DBEAFE' : '#D1FAE5', color: isSym ? '#1D4ED8' : '#065F46', minWidth: 38, textAlign: 'center', flexShrink: 0 }}>
                        {isSym ? 'SYM' : 'LAB'}
                      </span>
                      <span style={{ fontSize: 11, color: '#374151', minWidth: 180, maxWidth: 220, flexShrink: 0 }}>{shortName}</span>
                      <div style={{ flex: 1, background: '#F3F4F6', borderRadius: 99, height: 8, overflow: 'hidden' }}>
                        <div style={{ width: `${pct}%`, height: '100%', background: isSym ? '#3B82F6' : '#10B981', borderRadius: 99, transition: 'width .4s' }} />
                      </div>
                      <span style={{ fontSize: 10, color: '#9CA3AF', minWidth: 50, textAlign: 'right' }}>{(imp * 100).toFixed(3)} %</span>
                    </div>
                  );
                })}
              </div>
              <div style={{ display: 'flex', gap: 16, marginTop: 10, fontSize: 11, color: '#6B7280' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ background: '#3B82F6', width: 10, height: 10, borderRadius: 2, display: 'inline-block' }} /> Symptôme</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ background: '#10B981', width: 10, height: 10, borderRadius: 2, display: 'inline-block' }} /> Paramètre biologique</span>
              </div>
            </>
          )}
        </Card>
      )}

      {/* ─── Stats IA ─── */}
      {aiStats && (
        <Card title="Statistiques d'utilisation de l'IA" icon={Activity} accent="#7C3AED">
          {aiStats.total_predictions === 0 ? (
            <p style={{ fontSize: 13, color: '#9CA3AF', fontStyle: 'italic' }}>Aucun diagnostic IA effectué pour l'instant.</p>
          ) : (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 16, marginBottom: 20 }}>
                <div style={{ textAlign: 'center', background: '#F9FAFB', borderRadius: 12, padding: '14px 8px', border: '1px solid #E5E7EB' }}>
                  <div style={{ fontSize: 26, fontWeight: 900, color: '#7C3AED' }}>{aiStats.total_predictions.toLocaleString('fr-FR')}</div>
                  <div style={{ fontSize: 11, color: '#6B7280', fontWeight: 600, marginTop: 2 }}>Diagnostics IA effectués</div>
                </div>
                <div style={{ textAlign: 'center', background: '#F9FAFB', borderRadius: 12, padding: '14px 8px', border: '1px solid #E5E7EB' }}>
                  <div style={{ fontSize: 26, fontWeight: 900, color: '#059669' }}>{aiStats.avg_confidence_pct} %</div>
                  <div style={{ fontSize: 11, color: '#6B7280', fontWeight: 600, marginTop: 2 }}>Confiance moyenne</div>
                </div>
              </div>
              <div style={{ marginBottom: 20 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: '#374151', marginBottom: 10 }}>Distribution des niveaux de confiance</div>
                <div style={{ display: 'flex', gap: 8 }}>
                  {([['HIGH', aiStats.confidence_distribution.HIGH, '#059669', '#ECFDF5', 'Élevée ≥ 70%'], ['MEDIUM', aiStats.confidence_distribution.MEDIUM, '#D97706', '#FFFBEB', 'Moyenne 40–70%'], ['LOW', aiStats.confidence_distribution.LOW, '#DC2626', '#FEF2F2', 'Basse < 40%']] as [string, number, string, string, string][]).map(([key, count, color, bg, label]) => {
                    const pct = Math.round((count / (aiStats.total_predictions || 1)) * 100);
                    return (
                      <div key={key} style={{ flex: 1, background: bg, border: `1px solid ${color}30`, borderRadius: 10, padding: '12px 10px', textAlign: 'center' }}>
                        <div style={{ fontSize: 20, fontWeight: 800, color }}>{count.toLocaleString('fr-FR')}</div>
                        <div style={{ fontSize: 10, fontWeight: 700, color, marginTop: 2 }}>{pct} %</div>
                        <div style={{ fontSize: 10, color: '#6B7280', marginTop: 2 }}>{label}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
              {aiStats.top_diseases.length > 0 && (
                <div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: '#374151', marginBottom: 10 }}>Top 5 maladies prédites</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {aiStats.top_diseases.map((d, i) => {
                      const maxCount = aiStats.top_diseases[0].count;
                      const pct = maxCount > 0 ? (d.count / maxCount) * 100 : 0;
                      const rankColors = ['#4F46E5', '#7C3AED', '#0891B2', '#059669', '#D97706'];
                      return (
                        <div key={d.disease} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <span style={{ fontSize: 11, fontWeight: 800, color: 'white', background: rankColors[i], borderRadius: 99, width: 20, height: 20, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>{i + 1}</span>
                          <span style={{ fontSize: 12, color: '#374151', minWidth: 160 }}>{d.disease}</span>
                          <div style={{ flex: 1, background: '#F3F4F6', borderRadius: 99, height: 7, overflow: 'hidden' }}>
                            <div style={{ width: `${pct}%`, height: '100%', background: rankColors[i], borderRadius: 99 }} />
                          </div>
                          <span style={{ fontSize: 11, color: '#6B7280', minWidth: 36, textAlign: 'right' }}>{d.count}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </>
          )}
        </Card>
      )}

      {/* ─── Historique ─── */}
      {trainingHistory.length > 0 && (
        <Card title="Historique des entraînements" icon={History} accent="#0891B2">
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
              <thead>
                <tr style={{ background: '#F9FAFB', borderBottom: '2px solid #E5E7EB' }}>
                  {['Date', 'Accuracy', 'Précision', 'Rappel', 'F1-Score', 'Obs.', 'Arbres', 'Durée'].map(h => (
                    <th key={h} style={{ padding: '8px 12px', textAlign: 'left', fontSize: 11, fontWeight: 700, color: '#6B7280', whiteSpace: 'nowrap' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {trainingHistory.map((s, i) => (
                  <tr key={s.date} style={{ borderBottom: '1px solid #F3F4F6', background: i === 0 ? '#F0FDF4' : 'white' }}>
                    <td style={{ padding: '8px 12px', color: '#374151', whiteSpace: 'nowrap' }}>
                      {i === 0 && <span style={{ background: '#059669', color: 'white', fontSize: 9, fontWeight: 700, padding: '1px 5px', borderRadius: 3, marginRight: 5 }}>ACTIF</span>}
                      {s.date ? new Date(s.date).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—'}
                    </td>
                    {[s.accuracy, s.precision, s.recall, s.f1_score].map((v, j) => (
                      <td key={j} style={{ padding: '8px 12px', fontWeight: 700, color: v >= 90 ? '#059669' : v >= 70 ? '#D97706' : '#DC2626' }}>{v?.toFixed(2)} %</td>
                    ))}
                    <td style={{ padding: '8px 12px', color: '#6B7280' }}>{s.n_samples?.toLocaleString('fr-FR') ?? '—'}</td>
                    <td style={{ padding: '8px 12px', color: '#6B7280' }}>{s.n_estimators ?? '—'}</td>
                    <td style={{ padding: '8px 12px', color: '#6B7280' }}>{s.duration_s != null ? `${s.duration_s} s` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
