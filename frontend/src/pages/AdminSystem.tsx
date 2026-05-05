import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Server, Brain, Database, Trash2, RefreshCw, Play, CheckCircle,
  XCircle, FileText, Cpu, Clock, ChevronDown,
  ChevronUp, Terminal, Package, Zap, Sliders,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { adminAPI, type IAConfig } from '../services/api';

// ─── Types ───────────────────────────────────────────────────────────────────

interface SystemStatus {
  server: { status: string; timestamp: string; platform: string; python_version: string; uvicorn_port: number };
  model: { loaded: boolean; version: string | null; n_features: number; n_classes: number; normalization_loaded: boolean; metadata: any };
  ia_config: IAConfig;
  training: TrainingState;
  dataset: { found: boolean; path: string | null; size_mb: number | null };
  model_files: Array<{ name: string; size_mb: number | null; modified: string | null }>;
  resources: { cpu_percent?: number; ram_used_gb?: number; ram_total_gb?: number; ram_percent?: number; disk_free_gb?: number; note?: string };
  logs: { exists: boolean; path: string; size_kb: number | null };
}

interface TrainingState {
  status: 'idle' | 'running' | 'success' | 'error';
  started_at: string | null;
  finished_at: string | null;
  message: string;
  results: { accuracy: number; precision: number; recall: number; f1_score: number; n_samples: number; n_features: number; n_classes: number; duration_s: number; model_path: string } | null;
  error: string | null;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const Badge = ({ ok, label }: { ok: boolean; label: string }) => (
  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '3px 10px', borderRadius: 99, background: ok ? '#ECFDF5' : '#FEF2F2', color: ok ? '#065F46' : '#991B1B', fontSize: 12, fontWeight: 700 }}>
    {ok ? <CheckCircle size={12} /> : <XCircle size={12} />}
    {label}
  </span>
);

const Stat = ({ label, value, unit = '' }: { label: string; value: any; unit?: string }) => (
  <div style={{ textAlign: 'center' }}>
    <div style={{ fontSize: 22, fontWeight: 800, color: '#1E1B4B' }}>{value ?? '—'}{unit}</div>
    <div style={{ fontSize: 11, color: '#6B7280', fontWeight: 600, marginTop: 2 }}>{label}</div>
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

const ProgressBar = ({ pct, color = '#4F46E5' }: { pct: number; color?: string }) => (
  <div style={{ background: '#F3F4F6', borderRadius: 99, height: 8, overflow: 'hidden' }}>
    <div style={{ width: `${Math.min(100, pct)}%`, height: '100%', background: color, transition: 'width .4s ease', borderRadius: 99 }} />
  </div>
);

// ─── Composant principal ─────────────────────────────────────────────────────

export default function AdminSystem() {
  const { token, isLoading: authLoading } = useAuth();
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [training, setTraining] = useState<TrainingState | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [logsOpen, setLogsOpen] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [loadingTrain, setLoadingTrain] = useState(false);
  const [loadingCleanModels, setLoadingCleanModels] = useState(false);
  const [loadingCleanLogs, setLoadingCleanLogs] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [nEstimators, setNEstimators] = useState(200);
  const [maxDepth, setMaxDepth] = useState(30);

  // IA Config
  const [iaConfig, setIaConfig] = useState<IAConfig>({ seuil_confiance_min: 0.60, seuil_alerte_bas: 0.40, n_estimators: 200, max_depth: 30 });
  const [iaConfigDraft, setIaConfigDraft] = useState<IAConfig>({ seuil_confiance_min: 0.60, seuil_alerte_bas: 0.40, n_estimators: 200, max_depth: 30 });
  const [savingIA, setSavingIA] = useState(false);
  const [iaConfigDirty, setIaConfigDirty] = useState(false);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 4000);
  };

  const fetchStatus = useCallback(async () => {
    if (!token) return;
    try {
      setFetchError(null);
      const data: SystemStatus = await adminAPI.getStatus(token);
      setStatus(data);
      setTraining(data.training);
      if (data.ia_config) {
        setIaConfig(data.ia_config);
        setIaConfigDraft(data.ia_config);
        setNEstimators(data.ia_config.n_estimators);
        setMaxDepth(data.ia_config.max_depth);
        setIaConfigDirty(false);
      }
    } catch (e: any) {
      setStatus(null);
      setFetchError(e?.detail || e?.message || 'Erreur inconnue');
    } finally {
      setLoadingStatus(false);
    }
  }, [token]);

  const fetchLogs = useCallback(async () => {
    if (!token) return;
    try {
      const data = await adminAPI.getLogs(token, 200);
      setLogs(data.lines ?? []);
      setTimeout(() => logsEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 50);
    } catch {
      setLogs(['Impossible de lire les logs.']);
    }
  }, [token]);

  // Poll training status when running
  useEffect(() => {
    if (training?.status === 'running') {
      pollRef.current = setInterval(async () => {
        if (!token) return;
        try {
          const data: TrainingState = await adminAPI.getTrainingStatus(token);
          setTraining(data);
          if (data.status !== 'running') {
            clearInterval(pollRef.current!);
            fetchStatus();
            if (data.status === 'success') showToast('Entraînement terminé avec succès !');
            else showToast(data.error ?? 'Entraînement échoué', false);
          }
        } catch {
          // ignore
        }
      }, 3000);
    }
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [training?.status, fetchStatus, token]);

  useEffect(() => {
    if (!authLoading) fetchStatus();
  }, [fetchStatus, authLoading]);
  useEffect(() => { if (logsOpen) fetchLogs(); }, [logsOpen, fetchLogs]);

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

  const cleanModels = async () => {
    if (!token) return;
    setLoadingCleanModels(true);
    try {
      const data = await adminAPI.cleanupModels(token);
      showToast(data.message ?? 'Nettoyage effectué');
      fetchStatus();
    } catch {
      showToast('Erreur lors du nettoyage', false);
    } finally {
      setLoadingCleanModels(false);
    }
  };

  const cleanLogs = async () => {
    if (!token) return;
    setLoadingCleanLogs(true);
    try {
      const data = await adminAPI.cleanupLogs(token);
      showToast(data.message ?? 'Logs vidés');
      if (logsOpen) fetchLogs();
      fetchStatus();
    } catch {
      showToast('Erreur lors du nettoyage des logs', false);
    } finally {
      setLoadingCleanLogs(false);
    }
  };

  const saveIAConfig = async () => {
    if (!token) return;
    setSavingIA(true);
    try {
      const updated = await adminAPI.updateIAConfig(token, iaConfigDraft);
      setIaConfig(updated);
      setIaConfigDraft(updated);
      setIaConfigDirty(false);
      showToast('Configuration IA sauvegardée');
    } catch (e: any) {
      showToast(e.detail ?? 'Erreur lors de la sauvegarde', false);
    } finally {
      setSavingIA(false);
    }
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
          {toast.ok ? <CheckCircle size={16} /> : <XCircle size={16} />}
          {toast.msg}
        </div>
      )}

      {/* En-tête */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 26, fontWeight: 900, color: '#111827', margin: 0 }}>Administration Système</h1>
        <p style={{ color: '#6B7280', marginTop: 4, fontSize: 14 }}>
          Gérez le serveur FastAPI, le modèle ML, les logs et le nettoyage
        </p>
      </div>

      {/* Bouton actualiser */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
        <button
          onClick={() => { setLoadingStatus(true); fetchStatus(); }}
          style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px', borderRadius: 8, border: '1px solid #E5E7EB', background: 'white', cursor: 'pointer', fontSize: 13, fontWeight: 600, color: '#374151' }}
        >
          <RefreshCw size={14} style={{ animation: loadingStatus ? 'spin 1s linear infinite' : 'none' }} />
          Actualiser
        </button>
      </div>

      {loadingStatus && (
        <div style={{ padding: 40, textAlign: 'center', color: '#6B7280', fontSize: 14 }}>
          <RefreshCw size={28} style={{ animation: 'spin 1s linear infinite', marginBottom: 12 }} />
          <br />Chargement des données système...
        </div>
      )}

      {!status && !loadingStatus && (
        <div style={{ padding: 32, textAlign: 'center', background: '#FEF2F2', borderRadius: 12, color: '#991B1B', fontWeight: 600 }}>
          <XCircle size={32} style={{ margin: '0 auto 8px' }} />
          {fetchError === 'Impossible de se connecter au serveur. Vérifiez que le backend est démarré sur http://localhost:8000'
            ? <>Serveur FastAPI injoignable — lancez-le avec :<br />
               <code style={{ fontFamily: 'monospace', fontSize: 13, background: '#fff', padding: '4px 10px', borderRadius: 6, marginTop: 8, display: 'inline-block' }}>
                 cd backend &amp;&amp; python start_server_auto.py
               </code></>
            : <>{fetchError || 'Erreur de connexion au backend'}<br />
               <button onClick={() => { setLoadingStatus(true); fetchStatus(); }} style={{ marginTop: 12, padding: '8px 20px', borderRadius: 8, border: 'none', background: '#DC2626', color: 'white', cursor: 'pointer', fontWeight: 600, fontSize: 13 }}>
                 Réessayer
               </button></>
          }
        </div>
      )}

      {status && (
        <>
          {/* ─── Serveur ─────────────────────────────────────────────── */}
          <Card title="Serveur FastAPI" icon={Server} accent="#4F46E5">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 20, marginBottom: 16 }}>
              <Stat label="Statut" value={<Badge ok label="En ligne" />} />
              <Stat label="Port" value={status.server.uvicorn_port} />
              <Stat label="Python" value={status.server.python_version} />
              <Stat label="Plateforme" value={status.server.platform} />
            </div>
            <div style={{ fontSize: 12, color: '#9CA3AF', borderTop: '1px solid #F3F4F6', paddingTop: 12, display: 'flex', gap: 20, flexWrap: 'wrap' }}>
              <span>📍 API : <a href="http://localhost:8000" target="_blank" rel="noreferrer" style={{ color: '#4F46E5' }}>http://localhost:8000</a></span>
              <span>📚 Docs : <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" style={{ color: '#4F46E5' }}>http://localhost:8000/docs</a></span>
              <span>🕐 {new Date(status.server.timestamp).toLocaleString('fr-FR')}</span>
            </div>
          </Card>

          {/* ─── Ressources ──────────────────────────────────────────── */}
          {status.resources.cpu_percent !== undefined && (
            <Card title="Ressources système" icon={Cpu} accent="#0EA5E9">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 20, marginBottom: 16 }}>
                <Stat label="CPU" value={status.resources.cpu_percent?.toFixed(1)} unit="%" />
                <Stat label="RAM utilisée" value={status.resources.ram_used_gb} unit=" Go" />
                <Stat label="RAM totale" value={status.resources.ram_total_gb} unit=" Go" />
                <Stat label="Disque libre" value={status.resources.disk_free_gb} unit=" Go" />
              </div>
              {status.resources.ram_percent !== undefined && (
                <div>
                  <div style={{ fontSize: 11, color: '#6B7280', marginBottom: 4 }}>Utilisation RAM : {status.resources.ram_percent}%</div>
                  <ProgressBar pct={status.resources.ram_percent} color={status.resources.ram_percent > 80 ? '#EF4444' : '#0EA5E9'} />
                </div>
              )}
            </Card>
          )}
          {status.resources.note && (
            <div style={{ fontSize: 12, color: '#9CA3AF', marginBottom: 12, fontStyle: 'italic' }}>
              ℹ️ {status.resources.note}
            </div>
          )}

          {/* ─── Modèle ML ───────────────────────────────────────────── */}
          <Card title="Modèle Machine Learning" icon={Brain} accent="#7C3AED">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 20, marginBottom: 20 }}>
              <Stat label="Statut" value={<Badge ok={status.model.loaded} label={status.model.loaded ? 'Chargé' : 'Non chargé'} />} />
              <Stat label="Features" value={status.model.n_features || '—'} />
              <Stat label="Classes" value={status.model.n_classes || '—'} />
              <Stat label="Normalisation" value={<Badge ok={status.model.normalization_loaded} label={status.model.normalization_loaded ? 'OK' : 'Manquante'} />} />
            </div>
            {status.model.version && (
              <div style={{ fontSize: 12, color: '#6B7280', marginBottom: 16 }}>
                Fichier actif : <code style={{ background: '#F3F4F6', padding: '2px 6px', borderRadius: 4 }}>{status.model.version}</code>
              </div>
            )}

            {/* Paramètres d'entraînement */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end', flexWrap: 'wrap', marginBottom: 12 }}>
              <div>
                <label style={{ fontSize: 11, color: '#6B7280', fontWeight: 600, display: 'block', marginBottom: 4 }}>Nombre d'arbres</label>
                <input
                  type="number" value={nEstimators} min={50} max={500} step={50}
                  onChange={e => setNEstimators(+e.target.value)}
                  style={{ width: 100, padding: '6px 10px', borderRadius: 6, border: '1px solid #D1D5DB', fontSize: 13 }}
                  disabled={trainingRunning}
                />
              </div>
              <div>
                <label style={{ fontSize: 11, color: '#6B7280', fontWeight: 600, display: 'block', marginBottom: 4 }}>Profondeur max</label>
                <input
                  type="number" value={maxDepth} min={5} max={60} step={5}
                  onChange={e => setMaxDepth(+e.target.value)}
                  style={{ width: 100, padding: '6px 10px', borderRadius: 6, border: '1px solid #D1D5DB', fontSize: 13 }}
                  disabled={trainingRunning}
                />
              </div>
              <button
                onClick={startTraining}
                disabled={trainingRunning || loadingTrain}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  padding: '9px 20px', borderRadius: 8, border: 'none', cursor: trainingRunning ? 'not-allowed' : 'pointer',
                  background: trainingRunning ? '#E5E7EB' : 'linear-gradient(135deg,#7C3AED,#4F46E5)',
                  color: trainingRunning ? '#9CA3AF' : 'white', fontWeight: 700, fontSize: 14,
                  opacity: trainingRunning ? 0.7 : 1,
                }}
              >
                {trainingRunning
                  ? <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Entraînement en cours…</>
                  : <><Play size={16} /> {status.model.loaded ? 'Réentraîner le modèle' : 'Entraîner le modèle'}</>
                }
              </button>
            </div>

            {/* Bloc entraînement */}
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
                        <div style={{ fontSize: 18, fontWeight: 800, color: '#065F46' }}>{val}{unit}</div>
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

          {/* ─── Config IA ───────────────────────────────────────────── */}
          <Card title="Configuration de l'IA" icon={Sliders} accent="#0891B2">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 20, marginBottom: 20 }}>

              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>
                  Seuil confiance minimum
                  <span style={{ float: 'right', color: '#0891B2', fontWeight: 700 }}>{Math.round(iaConfigDraft.seuil_confiance_min * 100)}%</span>
                </label>
                <input
                  type="range" min={0} max={1} step={0.05}
                  value={iaConfigDraft.seuil_confiance_min}
                  onChange={e => updateDraft('seuil_confiance_min', parseFloat(e.target.value))}
                  style={{ width: '100%', accentColor: '#0891B2' }}
                />
                <p style={{ fontSize: 11, color: '#6B7280', margin: '4px 0 0' }}>
                  En-dessous, le diagnostic est marqué comme incertain
                </p>
              </div>

              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>
                  Seuil alerte basse confiance
                  <span style={{ float: 'right', color: '#DC2626', fontWeight: 700 }}>{Math.round(iaConfigDraft.seuil_alerte_bas * 100)}%</span>
                </label>
                <input
                  type="range" min={0} max={0.8} step={0.05}
                  value={iaConfigDraft.seuil_alerte_bas}
                  onChange={e => updateDraft('seuil_alerte_bas', parseFloat(e.target.value))}
                  style={{ width: '100%', accentColor: '#DC2626' }}
                />
                <p style={{ fontSize: 11, color: '#6B7280', margin: '4px 0 0' }}>
                  En-dessous de ce seuil, une alerte rouge est affichée
                </p>
              </div>

              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>
                  Arbres pour le prochain entraînement
                  <span style={{ float: 'right', color: '#7C3AED', fontWeight: 700 }}>{iaConfigDraft.n_estimators}</span>
                </label>
                <input
                  type="range" min={50} max={500} step={50}
                  value={iaConfigDraft.n_estimators}
                  onChange={e => updateDraft('n_estimators', parseInt(e.target.value))}
                  style={{ width: '100%', accentColor: '#7C3AED' }}
                />
                <p style={{ fontSize: 11, color: '#6B7280', margin: '4px 0 0' }}>
                  Plus = meilleure précision, mais plus lent
                </p>
              </div>

              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>
                  Profondeur max des arbres
                  <span style={{ float: 'right', color: '#059669', fontWeight: 700 }}>{iaConfigDraft.max_depth}</span>
                </label>
                <input
                  type="range" min={5} max={60} step={5}
                  value={iaConfigDraft.max_depth}
                  onChange={e => updateDraft('max_depth', parseInt(e.target.value))}
                  style={{ width: '100%', accentColor: '#059669' }}
                />
                <p style={{ fontSize: 11, color: '#6B7280', margin: '4px 0 0' }}>
                  Plus élevé = peut sur-apprendre
                </p>
              </div>
            </div>

            {/* Valeurs actuelles sauvegardées */}
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 16, padding: '10px 14px', background: '#F0F9FF', borderRadius: 8, border: '1px solid #BAE6FD' }}>
              <span style={{ fontSize: 12, color: '#0369A1', fontWeight: 600 }}>Actuels :</span>
              <span style={{ fontSize: 12, color: '#374151' }}>Confiance min : <strong>{Math.round(iaConfig.seuil_confiance_min * 100)}%</strong></span>
              <span style={{ fontSize: 12, color: '#374151' }}>Alerte : <strong>{Math.round(iaConfig.seuil_alerte_bas * 100)}%</strong></span>
              <span style={{ fontSize: 12, color: '#374151' }}>Arbres : <strong>{iaConfig.n_estimators}</strong></span>
              <span style={{ fontSize: 12, color: '#374151' }}>Profondeur : <strong>{iaConfig.max_depth}</strong></span>
            </div>

            <button
              onClick={saveIAConfig}
              disabled={!iaConfigDirty || savingIA}
              style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '9px 20px', borderRadius: 8, border: 'none',
                cursor: !iaConfigDirty || savingIA ? 'not-allowed' : 'pointer',
                background: iaConfigDirty ? 'linear-gradient(135deg,#0891B2,#0369A1)' : '#E5E7EB',
                color: iaConfigDirty ? 'white' : '#9CA3AF',
                fontWeight: 700, fontSize: 14,
                opacity: !iaConfigDirty ? 0.6 : 1,
              }}
            >
              {savingIA ? <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <CheckCircle size={16} />}
              {savingIA ? 'Sauvegarde...' : iaConfigDirty ? 'Sauvegarder la configuration' : 'Configuration à jour'}
            </button>
          </Card>

          {/* ─── Dataset ─────────────────────────────────────────────── */}
          <Card title="Dataset d'entraînement" icon={Database} accent="#0D9488">
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
              <Badge ok={status.dataset.found} label={status.dataset.found ? 'Trouvé' : 'Introuvable'} />
              {status.dataset.found && (
                <>
                  <span style={{ fontSize: 13, color: '#374151' }}>
                    <strong>{status.dataset.size_mb} Mo</strong> — 10 000 cas, 121 maladies
                  </span>
                  <code style={{ fontSize: 11, color: '#6B7280', background: '#F9FAFB', padding: '3px 8px', borderRadius: 4, wordBreak: 'break-all' }}>
                    {status.dataset.path}
                  </code>
                </>
              )}
              {!status.dataset.found && (
                <span style={{ fontSize: 12, color: '#991B1B' }}>
                  Placez le fichier dans <code>les ressources dataset/dataset_medical_robust_10000_cas.csv</code>
                </span>
              )}
            </div>
          </Card>

          {/* ─── Fichiers modèles ─────────────────────────────────────── */}
          <Card title="Fichiers modèles sauvegardés" icon={Package} accent="#D97706">
            {status.model_files.length === 0 ? (
              <p style={{ color: '#9CA3AF', fontSize: 13 }}>Aucun modèle sauvegardé. Lancez un entraînement.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {status.model_files.map((f, i) => (
                  <div key={f.name} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px', borderRadius: 8, background: i === 0 ? '#FFFBEB' : '#F9FAFB', border: `1px solid ${i === 0 ? '#FCD34D' : '#E5E7EB'}`, fontSize: 13 }}>
                    <Zap size={14} style={{ color: i === 0 ? '#D97706' : '#9CA3AF', flexShrink: 0 }} />
                    <span style={{ flex: 1, fontFamily: 'monospace', fontSize: 12, color: '#374151' }}>{f.name}</span>
                    <span style={{ color: '#6B7280', fontSize: 12 }}>{f.size_mb} Mo</span>
                    {f.modified && <span style={{ color: '#9CA3AF', fontSize: 11 }}>{new Date(f.modified).toLocaleString('fr-FR')}</span>}
                    {i === 0 && <span style={{ background: '#D97706', color: 'white', padding: '1px 8px', borderRadius: 99, fontSize: 10, fontWeight: 700 }}>ACTIF</span>}
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* ─── Nettoyage ───────────────────────────────────────────── */}
          <Card title="Nettoyage" icon={Trash2} accent="#DC2626">
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <button
                onClick={cleanModels}
                disabled={loadingCleanModels || status.model_files.length <= 1}
                style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 18px', borderRadius: 8, border: '1px solid #FECACA', background: '#FEF2F2', color: '#DC2626', cursor: status.model_files.length <= 1 ? 'not-allowed' : 'pointer', fontWeight: 600, fontSize: 13, opacity: status.model_files.length <= 1 ? 0.5 : 1 }}
              >
                {loadingCleanModels ? <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <Trash2 size={14} />}
                Supprimer anciens modèles ({Math.max(0, status.model_files.length - 1)} à supprimer)
              </button>
              <button
                onClick={cleanLogs}
                disabled={loadingCleanLogs || !status.logs.exists}
                style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 18px', borderRadius: 8, border: '1px solid #FED7AA', background: '#FFF7ED', color: '#C2410C', cursor: !status.logs.exists ? 'not-allowed' : 'pointer', fontWeight: 600, fontSize: 13, opacity: !status.logs.exists ? 0.5 : 1 }}
              >
                {loadingCleanLogs ? <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <FileText size={14} />}
                Vider les logs {status.logs.size_kb ? `(${status.logs.size_kb} Ko)` : ''}
              </button>
            </div>
            <p style={{ fontSize: 12, color: '#9CA3AF', marginTop: 10 }}>
              La suppression des anciens modèles conserve uniquement le plus récent.
            </p>
          </Card>

          {/* ─── Logs ────────────────────────────────────────────────── */}
          <Card title="Logs système" icon={Terminal} accent="#374151">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: logsOpen ? 12 : 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <Badge ok={status.logs.exists} label={status.logs.exists ? `${status.logs.size_kb} Ko` : 'Aucun log'} />
                <span style={{ fontSize: 12, color: '#6B7280' }}>{status.logs.path}</span>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                {logsOpen && (
                  <button onClick={fetchLogs} style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '5px 10px', borderRadius: 6, border: '1px solid #E5E7EB', background: 'white', cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
                    <RefreshCw size={12} /> Rafraîchir
                  </button>
                )}
                <button
                  onClick={() => setLogsOpen(o => !o)}
                  style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '5px 12px', borderRadius: 6, border: '1px solid #E5E7EB', background: 'white', cursor: 'pointer', fontSize: 12, fontWeight: 600 }}
                >
                  {logsOpen ? <><ChevronUp size={14} /> Masquer</> : <><ChevronDown size={14} /> Afficher</>}
                </button>
              </div>
            </div>
            {logsOpen && (
              <div style={{ background: '#0F172A', borderRadius: 10, padding: 16, maxHeight: 420, overflowY: 'auto', fontFamily: 'monospace', fontSize: 11.5, lineHeight: 1.6, color: '#94A3B8' }}>
                {logs.length === 0 && <span style={{ color: '#475569' }}>— Aucune ligne —</span>}
                {logs.map((line, i) => {
                  const isError = line.toLowerCase().includes('error') || line.toLowerCase().includes('❌');
                  const isWarn = line.toLowerCase().includes('warn') || line.toLowerCase().includes('⚠');
                  const isOk = line.includes('✅') || line.includes('SUCCESS');
                  return (
                    <div key={i} style={{ color: isError ? '#F87171' : isWarn ? '#FBBF24' : isOk ? '#34D399' : '#94A3B8', borderBottom: '1px solid #1E293B', padding: '1px 0' }}>
                      {line || ' '}
                    </div>
                  );
                })}
                <div ref={logsEndRef} />
              </div>
            )}
          </Card>

          {/* ─── Commandes de référence ──────────────────────────────── */}
          <Card title="Commandes de référence" icon={Clock} accent="#6B7280">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                { label: 'Lancer le backend', cmd: 'cd backend && python start_server_auto.py' },
                { label: 'Lancer le frontend', cmd: 'cd frontend && npm run dev' },
                { label: 'Entraîner le modèle (script)', cmd: 'cd backend && python train_initial_model.py' },
                { label: 'Voir les logs en temps réel', cmd: 'cd backend && tail -f logs/app.log' },
                { label: 'Installer les dépendances backend', cmd: 'cd backend && pip install -r requirements.txt' },
                { label: 'Installer les dépendances frontend', cmd: 'cd frontend && npm install' },
              ].map(({ label, cmd }) => (
                <div key={cmd} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px', background: '#F9FAFB', borderRadius: 8, border: '1px solid #E5E7EB' }}>
                  <span style={{ fontSize: 12, color: '#374151', fontWeight: 600, minWidth: 220 }}>{label}</span>
                  <code style={{ flex: 1, fontSize: 12, color: '#4F46E5', fontFamily: 'monospace', background: '#EEF2FF', padding: '4px 8px', borderRadius: 4 }}>{cmd}</code>
                  <button
                    onClick={() => { navigator.clipboard.writeText(cmd); showToast('Copié !'); }}
                    style={{ padding: '4px 10px', borderRadius: 6, border: '1px solid #E5E7EB', background: 'white', cursor: 'pointer', fontSize: 11, fontWeight: 600, color: '#6B7280', whiteSpace: 'nowrap' }}
                  >
                    Copier
                  </button>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:.5 } }
      `}</style>
    </div>
  );
}
