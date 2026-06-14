import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Server, Brain, Trash2, RefreshCw, Play, CheckCircle,
  XCircle, FileText, Cpu, Terminal, ChevronDown, ChevronUp,
  Activity, Wrench,
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

// ─── Charte ──────────────────────────────────────────────────────────────────
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

const Badge = ({ ok, label }: { ok: boolean; label: string }) => (
  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '3px 10px', borderRadius: 99, background: ok ? C.successSoft : C.dangerSoft, color: ok ? '#065F46' : '#991B1B', fontSize: 12, fontWeight: 700 }}>
    {ok ? <CheckCircle size={12} /> : <XCircle size={12} />}{label}
  </span>
);

const Stat = ({ label, value, unit = '' }: { label: string; value: any; unit?: string }) => (
  <div style={{ background: C.bg, borderRadius: 12, padding: '14px 12px', border: `1px solid ${C.border}`, textAlign: 'center' }}>
    <div style={{ fontSize: 19, fontWeight: 800, color: C.text }}>{value ?? '—'}{unit}</div>
    <div style={{ fontSize: 11.5, color: C.textSoft, fontWeight: 600, marginTop: 3 }}>{label}</div>
  </div>
);

const ProgressBar = ({ pct, color = C.primary }: { pct: number; color?: string }) => (
  <div style={{ background: C.bg, borderRadius: 99, height: 8, overflow: 'hidden' }}>
    <div style={{ width: `${Math.min(100, pct)}%`, height: '100%', background: color, transition: 'width .4s ease', borderRadius: 99 }} />
  </div>
);

type Tab = 'system' | 'maintenance';

// ─── Composant principal ─────────────────────────────────────────────────────

export default function AdminSystem() {
  const { token, isLoading: authLoading } = useAuth();
  const [tab, setTab] = useState<Tab>('system');
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [training, setTraining] = useState<TrainingState | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [logsOpen, setLogsOpen] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [loadingCleanModels, setLoadingCleanModels] = useState(false);
  const [loadingCleanLogs, setLoadingCleanLogs] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

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
          }
        } catch { /* ignore */ }
      }, 3000);
    }
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [training?.status, fetchStatus, token]);

  useEffect(() => {
    if (!authLoading) fetchStatus();
  }, [fetchStatus, authLoading]);

  useEffect(() => { if (logsOpen) fetchLogs(); }, [logsOpen, fetchLogs]);

  const cleanModels = async () => {
    if (!token) return;
    setLoadingCleanModels(true);
    try {
      const data = await adminAPI.cleanupModels(token);
      showToast(data.message ?? 'Nettoyage effectué');
      fetchStatus();
    } catch {
      showToast('Erreur lors du nettoyage', false);
    } finally { setLoadingCleanModels(false); }
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
    } finally { setLoadingCleanLogs(false); }
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
        }}>
        <Icon size={16} /> {label}
      </button>
    );
  };

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
          <h1 style={{ fontSize: 26, fontWeight: 800, color: C.text, margin: 0 }}>Administration Système</h1>
          <p style={{ color: C.textSoft, marginTop: 4, fontSize: 14 }}>
            Serveur, ressources, modèle, nettoyage et logs
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {status && <Badge ok label="En ligne" />}
          <button onClick={() => { setLoadingStatus(true); fetchStatus(); }}
            style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '9px 16px', borderRadius: 9, border: `1px solid ${C.border}`, background: 'white', cursor: 'pointer', fontSize: 13, fontWeight: 600, color: '#334155' }}>
            <RefreshCw size={14} style={{ animation: loadingStatus ? 'spin 1s linear infinite' : 'none' }} /> Actualiser
          </button>
        </div>
      </div>

      {/* Bannière modèle non entraîné */}
      {status && !status.model.loaded && (
        <div style={{ marginBottom: 24, padding: '16px 20px', borderRadius: 12, background: C.warningSoft, border: `1px solid #FDE68A`, display: 'flex', alignItems: 'flex-start', gap: 14 }}>
          <Brain size={22} style={{ color: '#B45309', flexShrink: 0, marginTop: 2 }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: 14.5, color: '#92400E', marginBottom: 4 }}>Aucun modèle d'IA entraîné</div>
            <div style={{ fontSize: 13, color: '#78350F', lineHeight: 1.5 }}>
              Rendez-vous sur la page <strong>Modèle IA</strong> pour lancer l'entraînement.
              {status.dataset.found ? ` Dataset prêt (${status.dataset.size_mb} Mo).` : ' Dataset introuvable.'}
            </div>
          </div>
        </div>
      )}

      {/* Onglets */}
      <div style={{ display: 'flex', gap: 4, borderBottom: `1px solid ${C.border}`, marginBottom: 24 }}>
        <TabBtn id="system" label="Système" icon={Server} />
        <TabBtn id="maintenance" label="Maintenance & Logs" icon={Wrench} />
      </div>

      {/* Chargement */}
      {loadingStatus && (
        <div style={{ padding: 40, textAlign: 'center', color: C.textSoft, fontSize: 14 }}>
          <RefreshCw size={28} style={{ animation: 'spin 1s linear infinite', marginBottom: 12 }} />
          <br />Chargement des données système…
        </div>
      )}

      {/* Erreur backend */}
      {!status && !loadingStatus && (
        <div style={{ padding: 20, background: C.dangerSoft, borderRadius: 12, color: '#991B1B', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <XCircle size={24} style={{ flexShrink: 0 }} />
          <span style={{ flex: 1 }}>
            {fetchError?.includes('connecter au serveur')
              ? <>Serveur FastAPI injoignable — lancez-le avec : <code style={{ fontFamily: 'monospace', fontSize: 13, background: '#fff', padding: '2px 8px', borderRadius: 4 }}>cd backend &amp;&amp; python start_server_auto.py</code></>
              : fetchError || 'Erreur de connexion au backend'}
          </span>
          <button onClick={() => { setLoadingStatus(true); fetchStatus(); }} style={{ padding: '7px 16px', borderRadius: 8, border: 'none', background: C.danger, color: 'white', cursor: 'pointer', fontWeight: 600, fontSize: 13, flexShrink: 0 }}>
            Réessayer
          </button>
        </div>
      )}

      {/* ════════ ONGLET SYSTÈME ════════ */}
      {status && tab === 'system' && (
        <>
          <Section title="Serveur FastAPI" desc="État et accès du backend" icon={Server}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 14, marginBottom: 16 }}>
              <Stat label="Statut" value="En ligne" />
              <Stat label="Port" value={status.server.uvicorn_port} />
              <Stat label="Python" value={status.server.python_version} />
              <Stat label="Plateforme" value={status.server.platform} />
            </div>
            <div style={{ fontSize: 12.5, color: C.textSoft, borderTop: `1px solid ${C.bg}`, paddingTop: 14, display: 'flex', gap: 20, flexWrap: 'wrap' }}>
              <span>API : <a href="http://localhost:8000" target="_blank" rel="noreferrer" style={{ color: C.primary, fontWeight: 600 }}>http://localhost:8000</a></span>
              <span>Docs : <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" style={{ color: C.primary, fontWeight: 600 }}>/docs</a></span>
              <span>{new Date(status.server.timestamp).toLocaleString('fr-FR')}</span>
            </div>
          </Section>

          {status.resources.cpu_percent !== undefined && (
            <Section title="Ressources système" desc="Charge CPU, mémoire et disque" icon={Cpu}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 14, marginBottom: status.resources.ram_percent !== undefined ? 18 : 0 }}>
                <Stat label="CPU" value={status.resources.cpu_percent?.toFixed(1)} unit=" %" />
                <Stat label="RAM utilisée" value={status.resources.ram_used_gb} unit=" Go" />
                <Stat label="RAM totale" value={status.resources.ram_total_gb} unit=" Go" />
                <Stat label="Disque libre" value={status.resources.disk_free_gb} unit=" Go" />
              </div>
              {status.resources.ram_percent !== undefined && (
                <div>
                  <div style={{ fontSize: 12, color: C.textSoft, marginBottom: 5 }}>Utilisation RAM : {status.resources.ram_percent} %</div>
                  <ProgressBar pct={status.resources.ram_percent} color={status.resources.ram_percent > 80 ? C.danger : C.primary} />
                </div>
              )}
              {status.resources.note && (
                <p style={{ fontSize: 12, color: '#94A3B8', marginTop: 12, marginBottom: 0, fontStyle: 'italic' }}>{status.resources.note}</p>
              )}
            </Section>
          )}

          <Section title="Modèle Machine Learning" desc="État du modèle actuellement chargé" icon={Brain}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 14, marginBottom: 16 }}>
              <Stat label="Statut" value={status.model.loaded ? 'Chargé' : 'Non chargé'} />
              <Stat label="Features" value={status.model.n_features || '—'} />
              <Stat label="Classes" value={status.model.n_classes || '—'} />
              <Stat label="Normalisation" value={status.model.normalization_loaded ? 'OK' : 'Manquante'} />
            </div>
            {status.model.version && (
              <div style={{ fontSize: 12.5, color: C.textSoft, marginBottom: 12 }}>
                Fichier actif : <code style={{ background: C.bg, padding: '2px 8px', borderRadius: 4, fontSize: 12 }}>{status.model.version}</code>
              </div>
            )}
            <div style={{ background: C.primarySoft, border: '1px solid #BBD4EE', borderRadius: 10, padding: '11px 15px', fontSize: 13, color: C.primary, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Activity size={15} style={{ flexShrink: 0 }} />
              L'entraînement et la configuration de l'IA se gèrent depuis la page <strong>Modèle IA</strong>.
              {trainingRunning && <span style={{ marginLeft: 'auto', fontWeight: 700 }}>⏳ Entraînement en cours…</span>}
            </div>
          </Section>
        </>
      )}

      {/* ════════ ONGLET MAINTENANCE ════════ */}
      {status && tab === 'maintenance' && (
        <>
          <Section title="Nettoyage" desc="Libérez de l'espace en supprimant les anciens fichiers" icon={Trash2}>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <button onClick={cleanModels} disabled={loadingCleanModels || status.model_files.length <= 1}
                style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '11px 18px', borderRadius: 10, border: '1px solid #FECACA', background: C.dangerSoft, color: C.danger, cursor: status.model_files.length <= 1 ? 'not-allowed' : 'pointer', fontWeight: 600, fontSize: 13.5, opacity: status.model_files.length <= 1 ? 0.5 : 1 }}>
                {loadingCleanModels ? <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <Trash2 size={14} />}
                Supprimer anciens modèles ({Math.max(0, status.model_files.length - 1)})
              </button>
              <button onClick={cleanLogs} disabled={loadingCleanLogs || !status.logs.exists}
                style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '11px 18px', borderRadius: 10, border: '1px solid #FDE68A', background: C.warningSoft, color: '#C2410C', cursor: !status.logs.exists ? 'not-allowed' : 'pointer', fontWeight: 600, fontSize: 13.5, opacity: !status.logs.exists ? 0.5 : 1 }}>
                {loadingCleanLogs ? <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <FileText size={14} />}
                Vider les logs {status.logs.size_kb ? `(${status.logs.size_kb} Ko)` : ''}
              </button>
            </div>
            <p style={{ fontSize: 12, color: '#94A3B8', marginTop: 12, marginBottom: 0 }}>La suppression des anciens modèles conserve uniquement le plus récent.</p>
          </Section>

          <Section title="Logs système" desc={status.logs.path} icon={Terminal}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: logsOpen ? 14 : 0 }}>
              <Badge ok={status.logs.exists} label={status.logs.exists ? `${status.logs.size_kb} Ko` : 'Aucun log'} />
              <div style={{ display: 'flex', gap: 8 }}>
                {logsOpen && (
                  <button onClick={fetchLogs} style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '6px 12px', borderRadius: 8, border: `1px solid ${C.border}`, background: 'white', cursor: 'pointer', fontSize: 12, fontWeight: 600, color: '#334155' }}>
                    <RefreshCw size={12} /> Rafraîchir
                  </button>
                )}
                <button onClick={() => setLogsOpen(o => !o)} style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '6px 12px', borderRadius: 8, border: `1px solid ${C.border}`, background: 'white', cursor: 'pointer', fontSize: 12, fontWeight: 600, color: '#334155' }}>
                  {logsOpen ? <><ChevronUp size={14} /> Masquer</> : <><ChevronDown size={14} /> Afficher</>}
                </button>
              </div>
            </div>
            {logsOpen && (
              <div style={{ background: '#0F172A', borderRadius: 10, padding: 16, maxHeight: 420, overflowY: 'auto', fontFamily: 'monospace', fontSize: 11.5, lineHeight: 1.6, color: '#94A3B8' }}>
                {logs.length === 0 && <span style={{ color: '#475569' }}>— Aucune ligne —</span>}
                {logs.map((line, i) => {
                  const isError = line.toLowerCase().includes('error') || line.includes('❌');
                  const isWarn = line.toLowerCase().includes('warn') || line.includes('⚠');
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
          </Section>

          <Section title="Commandes de référence" desc="Cliquez pour copier" icon={Terminal}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                { label: 'Lancer le backend', cmd: 'cd backend && python start_server_auto.py' },
                { label: 'Lancer le frontend', cmd: 'cd frontend && npm run dev' },
                { label: 'Entraîner le modèle (script)', cmd: 'cd backend && python train_initial_model.py' },
                { label: 'Voir les logs en temps réel', cmd: 'cd backend && tail -f logs/app.log' },
                { label: 'Dépendances backend', cmd: 'cd backend && pip install -r requirements.txt' },
                { label: 'Dépendances frontend', cmd: 'cd frontend && npm install' },
              ].map(({ label, cmd }) => (
                <div key={cmd} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px', background: C.bg, borderRadius: 10, border: `1px solid ${C.border}`, flexWrap: 'wrap' }}>
                  <span style={{ fontSize: 12.5, color: '#334155', fontWeight: 600, minWidth: 180 }}>{label}</span>
                  <code style={{ flex: 1, fontSize: 12, color: C.primary, fontFamily: 'monospace', background: C.primarySoft, padding: '5px 9px', borderRadius: 6, minWidth: 200 }}>{cmd}</code>
                  <button onClick={() => { navigator.clipboard.writeText(cmd); showToast('Copié !'); }} style={{ padding: '5px 12px', borderRadius: 7, border: `1px solid ${C.border}`, background: 'white', cursor: 'pointer', fontSize: 11.5, fontWeight: 600, color: C.textSoft, whiteSpace: 'nowrap' }}>
                    Copier
                  </button>
                </div>
              ))}
            </div>
          </Section>
        </>
      )}

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:.5 } }
      `}</style>
    </div>
  );
}
