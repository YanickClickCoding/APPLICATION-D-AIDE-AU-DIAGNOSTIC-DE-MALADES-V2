import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Brain, RefreshCw, Play, CheckCircle, XCircle, Sliders,
  Activity, History, TrendingUp,
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

// ── Charte du projet ──
const C = {
  primary: '#0A4B8C',
  primaryLight: '#1565C0',
  primarySoft: '#E8F0FA',
  border: '#E2E8F0',
  bg: '#F8FAFC',
  text: '#1E293B',
  textSoft: '#64748B',
  success: '#10B981',
  successSoft: '#ECFDF5',
  danger: '#EF4444',
  dangerSoft: '#FEF2F2',
  warning: '#F59E0B',
  warningSoft: '#FFFBEB',
};

const inputStyle: React.CSSProperties = {
  width: '100%', padding: '11px 14px', borderRadius: 10,
  border: `1.5px solid ${C.border}`, fontSize: 14, color: C.text,
  background: '#fff', outline: 'none', boxSizing: 'border-box',
};
const labelStyle: React.CSSProperties = {
  fontSize: 13, fontWeight: 600, color: '#334155', display: 'block', marginBottom: 7,
};

const Section = ({ title, desc, icon: Icon, children }: any) => (
  <div style={{ background: '#fff', borderRadius: 16, border: `1px solid ${C.border}`, boxShadow: '0 1px 3px rgba(15,23,42,.04)', overflow: 'hidden', marginBottom: 20 }}>
    <div style={{ padding: '18px 24px', borderBottom: `1px solid ${C.border}`, display: 'flex', alignItems: 'center', gap: 12, background: '#FCFDFE' }}>
      <div style={{ background: C.primarySoft, borderRadius: 10, padding: 9, display: 'flex' }}>
        <Icon size={19} style={{ color: C.primary }} />
      </div>
      <div>
        <h2 style={{ fontSize: 16, fontWeight: 700, color: C.text, margin: 0 }}>{title}</h2>
        {desc && <p style={{ fontSize: 13, color: C.textSoft, margin: '2px 0 0' }}>{desc}</p>}
      </div>
    </div>
    <div style={{ padding: 24 }}>{children}</div>
  </div>
);

const ProgressBar = ({ pct, color = C.primary }: { pct: number; color?: string }) => (
  <div style={{ background: C.bg, borderRadius: 99, height: 8, overflow: 'hidden' }}>
    <div style={{ width: `${Math.min(100, pct)}%`, height: '100%', background: color, transition: 'width .4s ease', borderRadius: 99 }} />
  </div>
);

type Tab = 'train' | 'perf' | 'config' | 'history';

export default function AdminML() {
  const { token } = useAuth();
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [tab, setTab] = useState<Tab>('train');
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

  const TabBtn = ({ id, label, icon: Icon }: { id: Tab; label: string; icon: any }) => {
    const active = tab === id;
    return (
      <button onClick={() => setTab(id)}
        style={{
          display: 'flex', alignItems: 'center', gap: 8, padding: '10px 18px',
          border: 'none', borderBottom: `2.5px solid ${active ? C.primary : 'transparent'}`,
          background: 'none', cursor: 'pointer', fontSize: 14,
          fontWeight: active ? 700 : 600, color: active ? C.primary : C.textSoft,
          transition: 'color .15s', position: 'relative',
        }}>
        <Icon size={16} /> {label}
        {id === 'train' && trainingRunning && (
          <span style={{ width: 8, height: 8, borderRadius: 99, background: C.warning, animation: 'pulse 1.5s infinite' }} />
        )}
      </button>
    );
  };

  const primaryBtn = (disabled: boolean): React.CSSProperties => ({
    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
    padding: '12px 22px', borderRadius: 10, border: 'none',
    background: C.primary, color: '#fff', fontSize: 14, fontWeight: 600,
    cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.55 : 1,
  });

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      {/* Toast */}
      {toast && (
        <div style={{ position: 'fixed', top: 24, right: 24, zIndex: 9999, padding: '12px 20px', borderRadius: 10, color: 'white', background: toast.ok ? C.success : C.danger, boxShadow: '0 4px 20px rgba(0,0,0,.15)', display: 'flex', alignItems: 'center', gap: 8, fontSize: 14, fontWeight: 600 }}>
          {toast.ok ? <CheckCircle size={16} /> : <XCircle size={16} />}{toast.msg}
        </div>
      )}

      {/* En-tête */}
      <div style={{ marginBottom: 22, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 800, color: C.text, margin: 0 }}>Modèle IA &amp; Entraînement</h1>
          <p style={{ color: C.textSoft, marginTop: 4, fontSize: 14 }}>
            Entraînez le modèle, ajustez la configuration et consultez les performances
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '5px 12px', borderRadius: 99, background: modelLoaded ? C.successSoft : C.dangerSoft, color: modelLoaded ? '#065F46' : '#991B1B', fontSize: 12, fontWeight: 700 }}>
            {modelLoaded ? <CheckCircle size={12} /> : <XCircle size={12} />}{modelLoaded ? 'Modèle chargé' : 'Aucun modèle'}
          </span>
          <button onClick={fetchAll} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '9px 16px', borderRadius: 9, border: `1px solid ${C.border}`, background: 'white', cursor: 'pointer', fontSize: 13, fontWeight: 600, color: '#334155' }}>
            <RefreshCw size={14} /> Actualiser
          </button>
        </div>
      </div>

      {/* Onglets */}
      <div style={{ display: 'flex', gap: 4, borderBottom: `1px solid ${C.border}`, marginBottom: 24, flexWrap: 'wrap' }}>
        <TabBtn id="train" label="Entraînement" icon={Brain} />
        <TabBtn id="perf" label="Performances" icon={TrendingUp} />
        <TabBtn id="config" label="Configuration" icon={Sliders} />
        <TabBtn id="history" label="Historique" icon={History} />
      </div>

      {/* ════════ ENTRAÎNEMENT ════════ */}
      {tab === 'train' && (
        <Section title="Entraîner le modèle ML" desc="Lancez un entraînement (ou réentraînement) avec les paramètres choisis" icon={Brain}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18, marginBottom: 20 }}>
            <div>
              <label style={labelStyle}>Nombre d'arbres</label>
              <input type="number" value={nEstimators} min={50} max={500} step={50}
                onChange={e => setNEstimators(+e.target.value)} disabled={trainingRunning}
                style={inputStyle} />
              <p style={{ fontSize: 11.5, color: '#94A3B8', marginTop: 5 }}>Plus = meilleure précision, mais plus lent</p>
            </div>
            <div>
              <label style={labelStyle}>Profondeur maximale</label>
              <input type="number" value={maxDepth} min={5} max={60} step={5}
                onChange={e => setMaxDepth(+e.target.value)} disabled={trainingRunning}
                style={inputStyle} />
              <p style={{ fontSize: 11.5, color: '#94A3B8', marginTop: 5 }}>Trop élevé = risque de sur-apprentissage</p>
            </div>
          </div>

          <button onClick={() => startTraining()} disabled={trainingRunning || loadingTrain}
            style={{ ...primaryBtn(trainingRunning || loadingTrain), width: '100%' }}>
            {trainingRunning
              ? <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Entraînement en cours…</>
              : <><Play size={16} /> {modelLoaded ? 'Réentraîner le modèle' : 'Entraîner le modèle'}</>}
          </button>

          {training && training.status !== 'idle' && (
            <div style={{
              marginTop: 20, padding: 18, borderRadius: 12,
              background: training.status === 'success' ? C.successSoft : training.status === 'error' ? C.dangerSoft : C.primarySoft,
              border: `1px solid ${training.status === 'success' ? '#A7F3D0' : training.status === 'error' ? '#FECACA' : '#BBD4EE'}`,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: training.status === 'running' || training.results ? 12 : 0 }}>
                {training.status === 'running' && <RefreshCw size={15} style={{ animation: 'spin 1s linear infinite', color: C.primary }} />}
                {training.status === 'success' && <CheckCircle size={15} style={{ color: C.success }} />}
                {training.status === 'error' && <XCircle size={15} style={{ color: C.danger }} />}
                <span style={{ fontSize: 13.5, fontWeight: 600, color: training.status === 'success' ? '#065F46' : training.status === 'error' ? '#991B1B' : C.primary }}>
                  {training.message}
                </span>
              </div>
              {training.status === 'running' && (
                <div style={{ overflow: 'hidden', borderRadius: 99, background: '#BBD4EE', height: 6 }}>
                  <div style={{ height: '100%', width: '40%', background: C.primary, animation: 'pulse 2s infinite', borderRadius: 99 }} />
                </div>
              )}
              {training.status === 'error' && training.error && <p style={{ fontSize: 12.5, color: '#991B1B', margin: '6px 0 0' }}>{training.error}</p>}
              {training.results && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(90px, 1fr))', gap: 12 }}>
                  {([['Précision', training.results.accuracy, '%'], ['F1-Score', training.results.f1_score, '%'], ['Classes', training.results.n_classes, ''], ['Durée', training.results.duration_s, 's']] as [string, any, string][]).map(([label, val, unit]) => (
                    <div key={label} style={{ textAlign: 'center', background: 'white', borderRadius: 10, padding: '10px 4px', border: `1px solid ${C.border}` }}>
                      <div style={{ fontSize: 18, fontWeight: 800, color: '#065F46' }}>{val}{unit}</div>
                      <div style={{ fontSize: 11, color: C.textSoft, fontWeight: 600, marginTop: 2 }}>{label}</div>
                    </div>
                  ))}
                </div>
              )}
              {training.started_at && (
                <div style={{ fontSize: 11.5, color: '#94A3B8', marginTop: 12 }}>
                  Démarré : {new Date(training.started_at).toLocaleString('fr-FR')}
                  {training.finished_at && ` — Terminé : ${new Date(training.finished_at).toLocaleString('fr-FR')}`}
                </div>
              )}
            </div>
          )}
        </Section>
      )}

      {/* ════════ PERFORMANCES ════════ */}
      {tab === 'perf' && (
        <>
          {modelPerf?.available && modelPerf.metrics ? (
            <Section title="Performances du modèle (dernière session)" desc={modelPerf.model_version ? `Version : ${modelPerf.model_version}` : undefined} icon={TrendingUp}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: 16, marginBottom: 22 }}>
                {([['Accuracy', modelPerf.metrics.accuracy], ['Précision', modelPerf.metrics.precision], ['Rappel', modelPerf.metrics.recall], ['F1-Score', modelPerf.metrics.f1_score]] as [string, number][]).map(([label, val]) => (
                  <div key={label} style={{ background: C.bg, borderRadius: 12, padding: '14px 16px', border: `1px solid ${C.border}` }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <span style={{ fontSize: 12.5, fontWeight: 600, color: '#334155' }}>{label}</span>
                      <span style={{ fontSize: 15, fontWeight: 800, color: C.primary }}>{val?.toFixed(2)} %</span>
                    </div>
                    <ProgressBar pct={val ?? 0} />
                  </div>
                ))}
              </div>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: modelPerf.feature_importance?.features.length ? 22 : 0 }}>
                {[['Observations', modelPerf.metrics.n_samples?.toLocaleString('fr-FR')], ['Features', modelPerf.metrics.n_features], ['Classes', modelPerf.metrics.n_classes], ['Durée', modelPerf.metrics.duration_s != null ? `${modelPerf.metrics.duration_s} s` : '—']].map(([lbl, val]) => val != null && (
                  <span key={lbl as string} style={{ fontSize: 12.5, color: '#334155', background: C.primarySoft, padding: '5px 11px', borderRadius: 8, fontWeight: 600 }}>
                    {lbl} : <strong>{val}</strong>
                  </span>
                ))}
              </div>
              {modelPerf.feature_importance && modelPerf.feature_importance.features.length > 0 && (
                <>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#334155', marginBottom: 12, borderTop: `1px solid ${C.border}`, paddingTop: 18 }}>
                    Top {modelPerf.feature_importance.features.length} features — impact sur la décision
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {modelPerf.feature_importance.features.map((feat, i) => {
                      const imp = modelPerf.feature_importance!.importances[i];
                      const maxImp = modelPerf.feature_importance!.importances[0];
                      const pct = maxImp > 0 ? (imp / maxImp) * 100 : 0;
                      const shortName = feat.replace(/^(Lab_|Vital_|SYM_|symptom_)/, '').replace(/_/g, ' ').substring(0, 40);
                      const isSym = feat.startsWith('SYM_') || feat.startsWith('symptom_');
                      return (
                        <div key={feat} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <span style={{ fontSize: 10, fontWeight: 700, padding: '1px 6px', borderRadius: 4, background: isSym ? C.primarySoft : C.successSoft, color: isSym ? C.primary : '#065F46', minWidth: 38, textAlign: 'center', flexShrink: 0 }}>
                            {isSym ? 'SYM' : 'LAB'}
                          </span>
                          <span style={{ fontSize: 11.5, color: '#334155', minWidth: 180, maxWidth: 220, flexShrink: 0 }}>{shortName}</span>
                          <div style={{ flex: 1, background: C.bg, borderRadius: 99, height: 8, overflow: 'hidden' }}>
                            <div style={{ width: `${pct}%`, height: '100%', background: isSym ? C.primaryLight : C.success, borderRadius: 99, transition: 'width .4s' }} />
                          </div>
                          <span style={{ fontSize: 10, color: '#94A3B8', minWidth: 52, textAlign: 'right' }}>{(imp * 100).toFixed(3)} %</span>
                        </div>
                      );
                    })}
                  </div>
                  <div style={{ display: 'flex', gap: 16, marginTop: 12, fontSize: 11.5, color: C.textSoft }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ background: C.primaryLight, width: 10, height: 10, borderRadius: 2, display: 'inline-block' }} /> Symptôme</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ background: C.success, width: 10, height: 10, borderRadius: 2, display: 'inline-block' }} /> Paramètre biologique</span>
                  </div>
                </>
              )}
            </Section>
          ) : (
            <Section title="Performances du modèle" icon={TrendingUp}>
              <div style={{ padding: '24px 20px', textAlign: 'center', color: C.textSoft, fontSize: 13, background: C.bg, borderRadius: 10 }}>
                Aucune performance disponible. Lancez un entraînement depuis l'onglet « Entraînement ».
              </div>
            </Section>
          )}

          {aiStats && (
            <Section title="Statistiques d'utilisation de l'IA" desc="Diagnostics réalisés par les médecins" icon={Activity}>
              {aiStats.total_predictions === 0 ? (
                <div style={{ padding: '20px', textAlign: 'center', color: C.textSoft, fontSize: 13, background: C.bg, borderRadius: 10 }}>
                  Aucun diagnostic IA effectué pour l'instant.
                </div>
              ) : (
                <>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 16, marginBottom: 22 }}>
                    <div style={{ textAlign: 'center', background: C.bg, borderRadius: 12, padding: '16px 8px', border: `1px solid ${C.border}` }}>
                      <div style={{ fontSize: 26, fontWeight: 800, color: C.primary }}>{aiStats.total_predictions.toLocaleString('fr-FR')}</div>
                      <div style={{ fontSize: 11.5, color: C.textSoft, fontWeight: 600, marginTop: 2 }}>Diagnostics effectués</div>
                    </div>
                    <div style={{ textAlign: 'center', background: C.bg, borderRadius: 12, padding: '16px 8px', border: `1px solid ${C.border}` }}>
                      <div style={{ fontSize: 26, fontWeight: 800, color: C.success }}>{aiStats.avg_confidence_pct} %</div>
                      <div style={{ fontSize: 11.5, color: C.textSoft, fontWeight: 600, marginTop: 2 }}>Confiance moyenne</div>
                    </div>
                  </div>
                  <div style={{ marginBottom: aiStats.top_diseases.length ? 22 : 0 }}>
                    <div style={{ fontSize: 12.5, fontWeight: 700, color: '#334155', marginBottom: 10 }}>Distribution des niveaux de confiance</div>
                    <div style={{ display: 'flex', gap: 8 }}>
                      {([['HIGH', aiStats.confidence_distribution.HIGH, C.success, C.successSoft, 'Élevée ≥ 70%'], ['MEDIUM', aiStats.confidence_distribution.MEDIUM, C.warning, C.warningSoft, 'Moyenne 40–70%'], ['LOW', aiStats.confidence_distribution.LOW, C.danger, C.dangerSoft, 'Basse < 40%']] as [string, number, string, string, string][]).map(([key, count, color, bg, label]) => {
                        const pct = Math.round((count / (aiStats.total_predictions || 1)) * 100);
                        return (
                          <div key={key} style={{ flex: 1, background: bg, border: `1px solid ${color}30`, borderRadius: 10, padding: '12px 10px', textAlign: 'center' }}>
                            <div style={{ fontSize: 20, fontWeight: 800, color }}>{count.toLocaleString('fr-FR')}</div>
                            <div style={{ fontSize: 10, fontWeight: 700, color, marginTop: 2 }}>{pct} %</div>
                            <div style={{ fontSize: 10, color: C.textSoft, marginTop: 2 }}>{label}</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  {aiStats.top_diseases.length > 0 && (
                    <div>
                      <div style={{ fontSize: 12.5, fontWeight: 700, color: '#334155', marginBottom: 10 }}>Top maladies prédites</div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                        {aiStats.top_diseases.map((d, i) => {
                          const maxCount = aiStats.top_diseases[0].count;
                          const pct = maxCount > 0 ? (d.count / maxCount) * 100 : 0;
                          return (
                            <div key={d.disease} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                              <span style={{ fontSize: 11, fontWeight: 800, color: 'white', background: C.primary, borderRadius: 99, width: 20, height: 20, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>{i + 1}</span>
                              <span style={{ fontSize: 12.5, color: '#334155', minWidth: 160 }}>{d.disease}</span>
                              <div style={{ flex: 1, background: C.bg, borderRadius: 99, height: 7, overflow: 'hidden' }}>
                                <div style={{ width: `${pct}%`, height: '100%', background: C.primaryLight, borderRadius: 99 }} />
                              </div>
                              <span style={{ fontSize: 11, color: C.textSoft, minWidth: 36, textAlign: 'right' }}>{d.count}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </>
              )}
            </Section>
          )}
        </>
      )}

      {/* ════════ CONFIGURATION ════════ */}
      {tab === 'config' && (
        <Section title="Configuration de l'IA" desc="Seuils de confiance et paramètres du prochain entraînement" icon={Sliders}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 22, marginBottom: 22 }}>
            {([
              ['seuil_confiance_min', 'Seuil confiance minimum', 0, 1, 0.05, 'En-dessous, le diagnostic est marqué incertain', (v: number) => `${Math.round(v * 100)}%`],
              ['seuil_alerte_bas', 'Seuil alerte basse confiance', 0, 0.8, 0.05, 'En-dessous, une alerte rouge est affichée', (v: number) => `${Math.round(v * 100)}%`],
              ['n_estimators', 'Arbres (prochain entraînement)', 50, 500, 50, 'Plus = meilleure précision, mais plus lent', (v: number) => `${v}`],
              ['max_depth', 'Profondeur max des arbres', 5, 60, 5, 'Plus élevé = peut sur-apprendre', (v: number) => `${v}`],
            ] as [keyof IAConfig, string, number, number, number, string, (v: number) => string][]).map(([key, label, min, max, step, desc, fmt]) => (
              <div key={key}>
                <label style={{ fontSize: 12.5, fontWeight: 600, color: '#334155', display: 'block', marginBottom: 6 }}>
                  {label}
                  <span style={{ float: 'right', color: C.primary, fontWeight: 700 }}>{fmt(iaConfigDraft[key] as number)}</span>
                </label>
                <input type="range" min={min} max={max} step={step}
                  value={iaConfigDraft[key] as number}
                  onChange={e => updateDraft(key, key === 'n_estimators' || key === 'max_depth' ? parseInt(e.target.value) : parseFloat(e.target.value))}
                  style={{ width: '100%', accentColor: C.primary }} />
                <p style={{ fontSize: 11.5, color: '#94A3B8', margin: '4px 0 0' }}>{desc}</p>
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 18, padding: '11px 15px', background: C.primarySoft, borderRadius: 10, border: '1px solid #BBD4EE' }}>
            <span style={{ fontSize: 12.5, color: C.primary, fontWeight: 700 }}>Valeurs actuelles :</span>
            <span style={{ fontSize: 12.5, color: '#334155' }}>Confiance min : <strong>{Math.round(iaConfig.seuil_confiance_min * 100)}%</strong></span>
            <span style={{ fontSize: 12.5, color: '#334155' }}>Alerte : <strong>{Math.round(iaConfig.seuil_alerte_bas * 100)}%</strong></span>
            <span style={{ fontSize: 12.5, color: '#334155' }}>Arbres : <strong>{iaConfig.n_estimators}</strong></span>
            <span style={{ fontSize: 12.5, color: '#334155' }}>Profondeur : <strong>{iaConfig.max_depth}</strong></span>
          </div>
          <button onClick={saveIAConfig} disabled={!iaConfigDirty || savingIA}
            style={{ ...primaryBtn(!iaConfigDirty || savingIA), width: '100%' }}>
            {savingIA ? <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <CheckCircle size={16} />}
            {savingIA ? 'Sauvegarde…' : iaConfigDirty ? 'Sauvegarder la configuration' : 'Configuration à jour'}
          </button>
        </Section>
      )}

      {/* ════════ HISTORIQUE ════════ */}
      {tab === 'history' && (
        <Section title="Historique des entraînements" desc="Sessions passées — la plus récente est active" icon={History}>
          {trainingHistory.length === 0 ? (
            <div style={{ padding: '24px 20px', textAlign: 'center', color: C.textSoft, fontSize: 13, background: C.bg, borderRadius: 10 }}>
              Aucun entraînement enregistré pour l'instant.
            </div>
          ) : (
            <div style={{ overflowX: 'auto', borderRadius: 10, border: `1px solid ${C.border}` }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
                <thead>
                  <tr style={{ background: C.bg }}>
                    {['Date', 'Accuracy', 'Précision', 'Rappel', 'F1-Score', 'Obs.', 'Arbres', 'Durée'].map(h => (
                      <th key={h} style={{ padding: '11px 14px', textAlign: 'left', fontSize: 11.5, fontWeight: 700, color: C.textSoft, whiteSpace: 'nowrap', borderBottom: `1px solid ${C.border}` }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {trainingHistory.map((s, i) => (
                    <tr key={s.date} style={{ borderBottom: `1px solid ${C.bg}`, background: i === 0 ? C.successSoft : 'white' }}>
                      <td style={{ padding: '10px 14px', color: '#334155', whiteSpace: 'nowrap' }}>
                        {i === 0 && <span style={{ background: C.success, color: 'white', fontSize: 9, fontWeight: 700, padding: '1px 5px', borderRadius: 3, marginRight: 5 }}>ACTIF</span>}
                        {s.date ? new Date(s.date).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—'}
                      </td>
                      {[s.accuracy, s.precision, s.recall, s.f1_score].map((v, j) => (
                        <td key={j} style={{ padding: '10px 14px', fontWeight: 700, color: v >= 90 ? C.success : v >= 70 ? C.warning : C.danger }}>{v?.toFixed(2)} %</td>
                      ))}
                      <td style={{ padding: '10px 14px', color: C.textSoft }}>{s.n_samples?.toLocaleString('fr-FR') ?? '—'}</td>
                      <td style={{ padding: '10px 14px', color: C.textSoft }}>{s.n_estimators ?? '—'}</td>
                      <td style={{ padding: '10px 14px', color: C.textSoft }}>{s.duration_s != null ? `${s.duration_s} s` : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Section>
      )}

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } } @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: .4; } }`}</style>
    </div>
  );
}
