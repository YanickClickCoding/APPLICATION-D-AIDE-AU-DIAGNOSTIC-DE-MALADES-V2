import { useState, useEffect, useCallback } from 'react';
import {
  Database, FlaskConical, RefreshCw, CheckCircle, XCircle,
  AlertTriangle, Plus, X, Package, Zap, Download, Trash2,
  LayoutGrid, PencilLine, Search,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface DatasetStats {
  total_maladies: number;
  total_cas: number;
}
interface DiseaseDetails {
  n_cas: number;
  symptomes: Array<{ nom: string; frequence: number }>;
  custom_rules?: { boost_factor?: number };
}
interface ModelFile {
  name: string;
  size_mb: number | null;
  modified: string | null;
}
interface MaladieItem { nom: string; cas: number; }

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

// ── Primitives UI ──
const inputStyle: React.CSSProperties = {
  width: '100%', padding: '11px 14px', borderRadius: 10,
  border: `1.5px solid ${C.border}`, fontSize: 14, color: C.text,
  background: '#fff', outline: 'none', boxSizing: 'border-box',
};
const labelStyle: React.CSSProperties = {
  fontSize: 13, fontWeight: 600, color: '#334155', display: 'block', marginBottom: 7,
};
const Req = () => <span style={{ color: C.danger }}> *</span>;

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

const CATEGORIES = [
  'Infectieuses', 'Cardiovasculaires', 'Respiratoires', 'Gastro-intestinales',
  'Endocriniennes / Métaboliques', 'Hépatiques', 'Neurologiques', 'Rhumatologiques',
  'Dermatologiques', 'Ophtalmologiques', 'Hématologiques', 'Rénales / Urinaires', 'Autres',
];

type Tab = 'overview' | 'add' | 'edit';

export default function AdminDataset() {
  const { token } = useAuth();
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [tab, setTab] = useState<Tab>('overview');

  // ── Dataset stats & listes ──
  const [datasetStats, setDatasetStats] = useState<DatasetStats | null>(null);
  const [maladies, setMaladies] = useState<MaladieItem[]>([]);
  const [maladiesNoms, setMaladiesNoms] = useState<string[]>([]);
  const [maladiesExistantes, setMaladiesExistantes] = useState<string[]>([]);
  const [modelFiles, setModelFiles] = useState<ModelFile[]>([]);
  const [datasetInfo, setDatasetInfo] = useState<{ found: boolean; path: string | null; size_mb: number | null } | null>(null);
  const [symptomesConnus, setSymptomesConnus] = useState<string[]>([]);
  const [maladieSearch, setMaladieSearch] = useState('');

  const [downloadingFile, setDownloadingFile] = useState<string | null>(null);

  // ── Ajouter une maladie ──
  const [newDiseaseName, setNewDiseaseName] = useState('');
  const [newDiseaseCateg, setNewDiseaseCateg] = useState('Infectieuses');
  const [newDiseaseSymptomes, setNewDiseaseSymptomes] = useState<string[]>([]);
  const [newSymptomeInput, setNewSymptomeInput] = useState('');
  const [newDiseaseNCas, setNewDiseaseNCas] = useState(80);
  const [newDiseaseReentrainer, setNewDiseaseReentrainer] = useState(true);
  const [addDiseaseLoading, setAddDiseaseLoading] = useState(false);
  const [addDiseaseResult, setAddDiseaseResult] = useState<{ success: boolean; message: string; total?: number } | null>(null);

  // ── Suppression ──
  const [deleteLoading, setDeleteLoading] = useState(false);

  // ── Modifier une maladie ──
  const [updateDiseaseName, setUpdateDiseaseName] = useState('');
  const [updateDiseaseSymptomes, setUpdateDiseaseSymptomes] = useState<string[]>([]);
  const [updateSymptomeInput, setUpdateSymptomeInput] = useState('');
  const [updateNCasSupp, setUpdateNCasSupp] = useState(0);
  const [updateRemplaceExistants, setUpdateRemplaceExistants] = useState(false);
  const [updateBoostFactor, setUpdateBoostFactor] = useState(4.0);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [updateLoadingDetails, setUpdateLoadingDetails] = useState(false);
  const [updateResult, setUpdateResult] = useState<{ success: boolean; message: string } | null>(null);
  const [updateDiseaseDetails, setUpdateDiseaseDetails] = useState<DiseaseDetails | null>(null);

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 4000);
  };

  const handleDownloadModel = async (filename: string) => {
    if (!token) return;
    let fileHandle: any = null;
    if ('showSaveFilePicker' in window) {
      try {
        fileHandle = await (window as any).showSaveFilePicker({
          suggestedName: filename,
          types: [{ description: 'Modèle ML', accept: { 'application/octet-stream': ['.joblib'] } }],
        });
      } catch (err: any) {
        if (err.name === 'AbortError') return;
        fileHandle = null;
      }
    }
    setDownloadingFile(filename);
    try {
      const res = await fetch(`http://localhost:8000/api/admin/models/download/${encodeURIComponent(filename)}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Téléchargement échoué');
      const blob = await res.blob();
      if (fileHandle) {
        const writable = await fileHandle.createWritable();
        await writable.write(blob);
        await writable.close();
      } else {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = filename;
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
      showToast(`"${filename}" sauvegardé`);
    } catch (e: any) {
      showToast(e.message || 'Erreur lors du téléchargement', false);
    } finally {
      setDownloadingFile(null);
    }
  };

  const fetchAll = useCallback(async () => {
    if (!token) return;
    try {
      const [listRes, statusRes] = await Promise.all([
        fetch('http://localhost:8000/api/admin/dataset/maladies', { headers: { Authorization: `Bearer ${token}` } }),
        fetch('http://localhost:8000/api/admin/status', { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      if (listRes.ok) {
        const d = await listRes.json();
        setDatasetStats({ total_maladies: d.total_maladies, total_cas: d.total_cas });
        const items = (d.maladies as MaladieItem[]).map(m => ({ nom: m.nom.trim(), cas: m.cas }));
        setMaladies(items);
        const noms = items.map(m => m.nom);
        setMaladiesNoms(noms);
        setMaladiesExistantes(noms.map(n => n.toLowerCase()));
      }
      if (statusRes.ok) {
        const s = await statusRes.json();
        setDatasetInfo(s.dataset ?? null);
        setModelFiles(s.model_files ?? []);
      }
      try {
        const symRes = await fetch('http://localhost:8000/api/ml/symptomes');
        if (symRes.ok) {
          const sd = await symRes.json();
          if (Array.isArray(sd.symptomes)) setSymptomesConnus(sd.symptomes);
        }
      } catch { /* non bloquant */ }
    } catch { /* silencieux */ }
  }, [token]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const diseaseAlreadyExists = maladiesExistantes.includes(newDiseaseName.trim().toLowerCase());
  const symInconnu = newSymptomeInput.trim().length >= 2 && symptomesConnus.length > 0 &&
    !symptomesConnus.some(s => s.toLowerCase() === newSymptomeInput.trim().toLowerCase());

  // ── Handlers ──
  const handleAddSymptome = () => {
    const s = newSymptomeInput.trim();
    if (s && !newDiseaseSymptomes.includes(s)) setNewDiseaseSymptomes(prev => [...prev, s]);
    setNewSymptomeInput('');
  };

  const handleAddDisease = async () => {
    if (!token) return;
    if (!newDiseaseName.trim()) { showToast('Nom de la maladie requis', false); return; }
    if (diseaseAlreadyExists) { showToast(`"${newDiseaseName}" existe déjà dans le dataset`, false); return; }
    if (newDiseaseSymptomes.length < 2) { showToast('Ajoutez au moins 2 symptômes', false); return; }
    setAddDiseaseLoading(true);
    setAddDiseaseResult(null);
    try {
      const res = await fetch('http://localhost:8000/api/admin/dataset/add-disease', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ nom_maladie: newDiseaseName.trim(), categorie: newDiseaseCateg, symptomes: newDiseaseSymptomes, n_cas: newDiseaseNCas, reentrainer: newDiseaseReentrainer }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erreur serveur');
      setAddDiseaseResult({ success: true, message: data.message, total: data.total_dataset });
      setNewDiseaseName(''); setNewDiseaseSymptomes([]); setNewDiseaseNCas(80);
      fetchAll();
      try {
        await fetch('http://localhost:8000/api/admin/symptomes/refresh', {
          method: 'POST', headers: { Authorization: `Bearer ${token}` },
        });
      } catch { /* non bloquant */ }
      if (data.reentrainement_lance) {
        showToast(`"${data.maladie}" ajoutée — réentraînement en cours (page Modèle IA)`);
      } else {
        showToast(`"${data.maladie}" ajoutée — ${data.cas_ajoutes} cas générés`);
      }
    } catch (e: any) {
      setAddDiseaseResult({ success: false, message: e.message });
      showToast(e.message, false);
    } finally { setAddDiseaseLoading(false); }
  };

  const handleLoadDiseaseDetails = async (nom?: string) => {
    const cible = (nom ?? updateDiseaseName).trim();
    if (!token || !cible) return;
    setUpdateDiseaseName(cible);
    setUpdateLoadingDetails(true);
    setUpdateDiseaseDetails(null);
    setUpdateDiseaseSymptomes([]);
    setUpdateResult(null);
    try {
      const res = await fetch(`http://localhost:8000/api/admin/dataset/maladies/${encodeURIComponent(cible)}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const d = await res.json();
      if (!res.ok) throw new Error(d.detail || 'Maladie introuvable');
      setUpdateDiseaseDetails(d);
      setUpdateDiseaseSymptomes((d.symptomes as Array<{ nom: string }>).slice(0, 10).map(s => s.nom));
      if (d.custom_rules?.boost_factor) setUpdateBoostFactor(d.custom_rules.boost_factor);
    } catch (e: any) { showToast(e.message, false); }
    finally { setUpdateLoadingDetails(false); }
  };

  const handleUpdateDisease = async () => {
    if (!token) return;
    if (!updateDiseaseName.trim()) { showToast('Sélectionnez une maladie', false); return; }
    if (updateDiseaseSymptomes.length < 1) { showToast('Ajoutez au moins 1 symptôme', false); return; }
    setUpdateLoading(true);
    setUpdateResult(null);
    try {
      const res = await fetch(`http://localhost:8000/api/admin/dataset/update-disease/${encodeURIComponent(updateDiseaseName.trim())}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ symptomes: updateDiseaseSymptomes, n_cas_supplementaires: updateNCasSupp, remplacer_cas_existants: updateRemplaceExistants, boost_factor: updateBoostFactor }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erreur serveur');
      setUpdateResult({ success: true, message: data.message });
      fetchAll();
      try {
        await fetch('http://localhost:8000/api/admin/symptomes/refresh', {
          method: 'POST', headers: { Authorization: `Bearer ${token}` },
        });
      } catch { /* non bloquant */ }
      showToast(`"${data.maladie}" mise à jour`);
    } catch (e: any) {
      setUpdateResult({ success: false, message: e.message });
      showToast(e.message, false);
    } finally { setUpdateLoading(false); }
  };

  const handleDeleteDisease = async () => {
    if (!token || !updateDiseaseName.trim()) return;
    const nom = updateDiseaseName.trim();
    if (!window.confirm(`Supprimer définitivement la maladie « ${nom} » et tous ses cas du dataset ?\n\nUn réentraînement sera nécessaire pour la retirer du modèle.`)) return;
    setDeleteLoading(true);
    setUpdateResult(null);
    try {
      const res = await fetch(`http://localhost:8000/api/admin/dataset/maladies/${encodeURIComponent(nom)}`, {
        method: 'DELETE', headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erreur serveur');
      setUpdateResult({ success: true, message: data.message });
      setUpdateDiseaseName(''); setUpdateDiseaseDetails(null); setUpdateDiseaseSymptomes([]);
      fetchAll();
      showToast(`« ${data.maladie} » supprimée — ${data.cas_supprimes} cas retirés`);
    } catch (e: any) {
      setUpdateResult({ success: false, message: e.message });
      showToast(e.message, false);
    } finally { setDeleteLoading(false); }
  };

  // Referme le formulaire d'édition sans rien modifier
  const closeEdit = () => {
    setUpdateDiseaseName('');
    setUpdateDiseaseDetails(null);
    setUpdateDiseaseSymptomes([]);
    setUpdateSymptomeInput('');
    setUpdateNCasSupp(0);
    setUpdateRemplaceExistants(false);
    setUpdateResult(null);
  };

  const TabBtn = ({ id, label, icon: Icon }: { id: Tab; label: string; icon: any }) => {
    const active = tab === id;
    return (
      <button onClick={() => setTab(id)}
        style={{
          display: 'flex', alignItems: 'center', gap: 8, padding: '10px 18px',
          border: 'none', borderBottom: `2.5px solid ${active ? C.primary : 'transparent'}`,
          background: 'none', cursor: 'pointer', fontSize: 14,
          fontWeight: active ? 700 : 600, color: active ? C.primary : C.textSoft,
          transition: 'color .15s',
        }}>
        <Icon size={16} /> {label}
      </button>
    );
  };

  const maladiesFiltrees = maladies.filter(m =>
    m.nom.toLowerCase().includes(maladieSearch.trim().toLowerCase()));

  const primaryBtn = (disabled: boolean): React.CSSProperties => ({
    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
    padding: '12px 20px', borderRadius: 10, border: 'none',
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
          <h1 style={{ fontSize: 26, fontWeight: 800, color: C.text, margin: 0 }}>Dataset &amp; Maladies</h1>
          <p style={{ color: C.textSoft, marginTop: 4, fontSize: 14 }}>
            Gérez le dataset d'entraînement : ajoutez, modifiez ou supprimez des maladies
          </p>
        </div>
        <button onClick={fetchAll} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '9px 16px', borderRadius: 9, border: `1px solid ${C.border}`, background: 'white', cursor: 'pointer', fontSize: 13, fontWeight: 600, color: '#334155' }}>
          <RefreshCw size={14} /> Actualiser
        </button>
      </div>

      {/* Onglets */}
      <div style={{ display: 'flex', gap: 4, borderBottom: `1px solid ${C.border}`, marginBottom: 24 }}>
        <TabBtn id="overview" label="Vue d'ensemble" icon={LayoutGrid} />
        <TabBtn id="add" label="Ajouter une maladie" icon={Plus} />
        <TabBtn id="edit" label="Modifier / Supprimer" icon={PencilLine} />
      </div>

      {/* ════════ ONGLET VUE D'ENSEMBLE ════════ */}
      {tab === 'overview' && (
        <>
          {/* KPIs */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 20 }}>
            {[
              { label: 'Maladies', val: datasetStats?.total_maladies ?? '—', icon: FlaskConical },
              { label: "Cas d'entraînement", val: datasetStats ? datasetStats.total_cas.toLocaleString('fr-FR') : '—', icon: Database },
              { label: 'Taille du dataset', val: datasetInfo?.size_mb != null ? `${datasetInfo.size_mb} Mo` : '—', icon: Package },
              { label: 'Modèles sauvegardés', val: modelFiles.length || '—', icon: Zap },
            ].map(k => (
              <div key={k.label} style={{ background: '#fff', borderRadius: 14, border: `1px solid ${C.border}`, padding: '18px 20px', display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{ background: C.primarySoft, borderRadius: 10, padding: 10, display: 'flex' }}>
                  <k.icon size={20} style={{ color: C.primary }} />
                </div>
                <div>
                  <div style={{ fontSize: 24, fontWeight: 800, color: C.text, lineHeight: 1.1 }}>{k.val}</div>
                  <div style={{ fontSize: 12.5, color: C.textSoft, marginTop: 2 }}>{k.label}</div>
                </div>
              </div>
            ))}
          </div>

          {datasetInfo && !datasetInfo.found && (
            <div style={{ background: C.dangerSoft, border: `1px solid #FECACA`, borderRadius: 12, padding: '14px 18px', marginBottom: 20, fontSize: 13, color: '#991B1B', display: 'flex', gap: 10 }}>
              <XCircle size={16} style={{ flexShrink: 0, marginTop: 1 }} />
              Dataset introuvable. Placez le fichier dans <code>les ressources dataset/</code>.
            </div>
          )}

          {/* Liste des maladies */}
          <Section title="Maladies du dataset" desc="Nombre de cas par maladie — repérez les maladies sous-représentées" icon={Database}>
            <div style={{ position: 'relative', marginBottom: 14 }}>
              <Search size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: C.textSoft }} />
              <input placeholder="Rechercher une maladie…" value={maladieSearch} onChange={e => setMaladieSearch(e.target.value)}
                style={{ ...inputStyle, paddingLeft: 36 }} />
            </div>
            <div style={{ maxHeight: 360, overflowY: 'auto', borderRadius: 10, border: `1px solid ${C.border}` }}>
              {maladiesFiltrees.length === 0 ? (
                <div style={{ padding: 24, textAlign: 'center', color: C.textSoft, fontSize: 13 }}>Aucune maladie.</div>
              ) : maladiesFiltrees.map((m, i) => {
                const faible = m.cas < 40;
                return (
                  <div key={m.nom} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '11px 16px', borderBottom: i < maladiesFiltrees.length - 1 ? `1px solid ${C.bg}` : 'none', background: i % 2 ? '#FCFDFE' : '#fff' }}>
                    <span style={{ flex: 1, fontSize: 14, color: C.text, fontWeight: 500 }}>{m.nom}</span>
                    <span style={{ fontSize: 12, fontWeight: 700, color: faible ? '#92400E' : C.primary, background: faible ? C.warningSoft : C.primarySoft, padding: '3px 10px', borderRadius: 99 }}>
                      {m.cas} cas{faible ? ' ⚠' : ''}
                    </span>
                    <button onClick={() => { setTab('edit'); handleLoadDiseaseDetails(m.nom); }}
                      title="Modifier" style={{ background: 'none', border: 'none', cursor: 'pointer', color: C.textSoft, display: 'flex', padding: 4 }}>
                      <PencilLine size={15} />
                    </button>
                  </div>
                );
              })}
            </div>
          </Section>

          {/* Modèles */}
          {modelFiles.length > 0 && (
            <Section title="Fichiers modèles sauvegardés" desc="Le modèle le plus récent est actif" icon={Package}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {modelFiles.map((f, i) => (
                  <div key={f.name} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '11px 14px', borderRadius: 10, background: i === 0 ? C.primarySoft : C.bg, border: `1px solid ${i === 0 ? '#BBD4EE' : C.border}`, fontSize: 13 }}>
                    <Zap size={14} style={{ color: i === 0 ? C.primary : '#94A3B8', flexShrink: 0 }} />
                    <span style={{ flex: 1, fontFamily: 'monospace', fontSize: 12, color: '#334155', wordBreak: 'break-all' }}>{f.name}</span>
                    {f.size_mb != null && <span style={{ color: C.textSoft, fontSize: 12, flexShrink: 0 }}>{f.size_mb} Mo</span>}
                    {i === 0 && <span style={{ background: C.primary, color: 'white', padding: '2px 9px', borderRadius: 99, fontSize: 10, fontWeight: 700, flexShrink: 0 }}>ACTIF</span>}
                    <button onClick={() => handleDownloadModel(f.name)} disabled={downloadingFile === f.name}
                      style={{ display: 'flex', alignItems: 'center', gap: 5, padding: '6px 11px', borderRadius: 8, border: `1px solid ${C.border}`, background: 'white', cursor: downloadingFile === f.name ? 'not-allowed' : 'pointer', fontSize: 11, fontWeight: 600, color: '#334155', flexShrink: 0, opacity: downloadingFile === f.name ? 0.6 : 1 }}>
                      {downloadingFile === f.name ? <RefreshCw size={12} style={{ animation: 'spin 1s linear infinite' }} /> : <Download size={12} />}
                      {downloadingFile === f.name ? 'Export…' : 'Exporter'}
                    </button>
                  </div>
                ))}
              </div>
            </Section>
          )}
        </>
      )}

      {/* ════════ ONGLET AJOUTER ════════ */}
      {tab === 'add' && (
        <Section title="Ajouter une maladie au dataset" desc="Génère des cas synthétiques à partir des symptômes caractéristiques" icon={FlaskConical}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18, marginBottom: 20 }}>
            <div>
              <label style={labelStyle}>Nom de la maladie<Req /></label>
              <input type="text" placeholder="Ex : Leishmaniose, Bilharziose…"
                value={newDiseaseName}
                onChange={e => { setNewDiseaseName(e.target.value); setAddDiseaseResult(null); }}
                style={{ ...inputStyle, borderColor: diseaseAlreadyExists ? C.danger : C.border }} />
              {diseaseAlreadyExists && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 7, fontSize: 12, color: '#B91C1C', fontWeight: 600 }}>
                  <XCircle size={13} /> Cette maladie existe déjà — utilisez l'onglet « Modifier ».
                </div>
              )}
              {!diseaseAlreadyExists && newDiseaseName.trim().length >= 2 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 7, fontSize: 12, color: '#047857', fontWeight: 600 }}>
                  <CheckCircle size={13} /> Nom disponible.
                </div>
              )}
            </div>
            <div>
              <label style={labelStyle}>Catégorie médicale<Req /></label>
              <select value={newDiseaseCateg} onChange={e => setNewDiseaseCateg(e.target.value)} style={inputStyle}>
                {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={labelStyle}>
              Symptômes caractéristiques<Req />
              <span style={{ fontWeight: 400, color: C.textSoft, marginLeft: 8 }}>({newDiseaseSymptomes.length} ajouté{newDiseaseSymptomes.length > 1 ? 's' : ''} — minimum 2)</span>
            </label>
            <div style={{ display: 'flex', gap: 8 }}>
              <input type="text" placeholder="Saisissez puis Entrée — choisissez dans la liste pour éviter les fautes"
                list="symptomes-connus" value={newSymptomeInput}
                onChange={e => setNewSymptomeInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleAddSymptome(); } }}
                style={{ ...inputStyle, flex: 1 }} />
              <datalist id="symptomes-connus">{symptomesConnus.map(s => <option key={s} value={s} />)}</datalist>
              <button type="button" onClick={handleAddSymptome} disabled={!newSymptomeInput.trim()}
                style={{ ...primaryBtn(!newSymptomeInput.trim()), padding: '0 18px', flexShrink: 0 }}>
                <Plus size={15} /> Ajouter
              </button>
            </div>
            {symInconnu && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 8, padding: '7px 11px', background: C.warningSoft, borderRadius: 8, border: '1px solid #FDE68A' }}>
                <AlertTriangle size={13} style={{ color: C.warning, flexShrink: 0 }} />
                <span style={{ fontSize: 12, color: '#92400E' }}>Nouveau symptôme (absent du dataset) — vérifiez l'orthographe.</span>
              </div>
            )}
            {newDiseaseSymptomes.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 12 }}>
                {newDiseaseSymptomes.map(s => (
                  <span key={s} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: C.primarySoft, color: C.primary, borderRadius: 99, padding: '5px 12px', fontSize: 13, fontWeight: 600 }}>
                    {s}
                    <button type="button" onClick={() => setNewDiseaseSymptomes(prev => prev.filter(x => x !== s))}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: C.primary, display: 'flex', padding: 0 }}>
                      <X size={13} />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={labelStyle}>Nombre de cas synthétiques : <strong style={{ color: C.primary }}>{newDiseaseNCas}</strong></label>
            <input type="range" min={20} max={300} step={10} value={newDiseaseNCas}
              onChange={e => setNewDiseaseNCas(Number(e.target.value))}
              style={{ width: '100%', accentColor: C.primary }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#94A3B8', marginTop: 2 }}>
              <span>20 (minimal)</span><span>80 (recommandé)</span><span>300 (maximum)</span>
            </div>
          </div>

          <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer', fontSize: 13.5, fontWeight: 600, color: '#334155', marginBottom: 20, padding: '13px 16px', background: C.primarySoft, border: '1px solid #BBD4EE', borderRadius: 10 }}>
            <input type="checkbox" checked={newDiseaseReentrainer} onChange={e => setNewDiseaseReentrainer(e.target.checked)} style={{ width: 16, height: 16, accentColor: C.primary }} />
            Réentraîner automatiquement le modèle après l'ajout
            <span style={{ fontWeight: 400, color: C.textSoft, fontSize: 12.5 }}>(la maladie sera aussitôt détectable)</span>
          </label>

          {addDiseaseResult && (
            <div style={{ padding: '12px 16px', borderRadius: 10, marginBottom: 18, background: addDiseaseResult.success ? C.successSoft : C.dangerSoft, border: `1px solid ${addDiseaseResult.success ? '#A7F3D0' : '#FECACA'}`, display: 'flex', gap: 10 }}>
              {addDiseaseResult.success ? <CheckCircle size={16} style={{ color: C.success, flexShrink: 0, marginTop: 1 }} /> : <XCircle size={16} style={{ color: C.danger, flexShrink: 0, marginTop: 1 }} />}
              <p style={{ fontSize: 12.5, color: addDiseaseResult.success ? '#047857' : '#B91C1C', margin: 0 }}>
                {addDiseaseResult.message}{addDiseaseResult.total ? ` — Dataset total : ${addDiseaseResult.total.toLocaleString('fr-FR')} cas` : ''}
              </p>
            </div>
          )}

          <button onClick={handleAddDisease}
            disabled={addDiseaseLoading || !newDiseaseName.trim() || newDiseaseSymptomes.length < 2 || diseaseAlreadyExists}
            style={{ ...primaryBtn(addDiseaseLoading || !newDiseaseName.trim() || newDiseaseSymptomes.length < 2 || diseaseAlreadyExists), width: '100%' }}>
            {addDiseaseLoading
              ? <><RefreshCw size={15} style={{ animation: 'spin 1s linear infinite' }} /> Génération en cours…</>
              : <><FlaskConical size={15} /> Ajouter la maladie au dataset</>}
          </button>
        </Section>
      )}

      {/* ════════ ONGLET MODIFIER / SUPPRIMER ════════ */}
      {tab === 'edit' && (
        <Section title="Modifier ou supprimer une maladie" desc="Ajustez les symptômes caractéristiques et le boost clinique, ou retirez la maladie" icon={PencilLine}>
          <div style={{ marginBottom: 20 }}>
            <label style={labelStyle}>Maladie à modifier<Req /></label>
            <div style={{ display: 'flex', gap: 10 }}>
              <select value={updateDiseaseName}
                onChange={e => { setUpdateDiseaseName(e.target.value); setUpdateDiseaseDetails(null); setUpdateDiseaseSymptomes([]); setUpdateResult(null); }}
                style={{ ...inputStyle, flex: 1 }}>
                <option value="">— Choisir une maladie —</option>
                {[...maladiesNoms].sort((a, b) => a.localeCompare(b, 'fr')).map(m => <option key={m} value={m}>{m}</option>)}
              </select>
              <button onClick={() => handleLoadDiseaseDetails()} disabled={!updateDiseaseName || updateLoadingDetails}
                style={{ ...primaryBtn(!updateDiseaseName || updateLoadingDetails), padding: '0 18px', flexShrink: 0 }}>
                {updateLoadingDetails ? <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <Database size={14} />}
                Charger
              </button>
            </div>
          </div>

          {updateDiseaseDetails && (
            <>
              <div style={{ background: C.primarySoft, border: '1px solid #BBD4EE', borderRadius: 10, padding: '11px 15px', marginBottom: 20, fontSize: 13, color: C.primary, display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ flex: 1 }}>
                  <strong>{updateDiseaseName}</strong> — {updateDiseaseDetails.n_cas} cas dans le dataset · {updateDiseaseDetails.symptomes.length} symptômes distincts recensés
                </span>
                <button onClick={closeEdit} title="Fermer sans modifier"
                  style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(255,255,255,.7)', border: '1px solid #BBD4EE', borderRadius: 8, padding: '4px 10px', cursor: 'pointer', color: C.primary, fontSize: 12, fontWeight: 600, flexShrink: 0 }}>
                  <X size={13} /> Fermer
                </button>
              </div>

              <div style={{ marginBottom: 20 }}>
                <label style={labelStyle}>Symptômes caractéristiques<Req />
                  <span style={{ fontWeight: 400, color: C.textSoft, marginLeft: 8 }}>(boostent la probabilité à la prédiction)</span>
                </label>
                <div style={{ display: 'flex', gap: 8 }}>
                  <input type="text" value={updateSymptomeInput} list="symptomes-connus"
                    onChange={e => setUpdateSymptomeInput(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); const s = updateSymptomeInput.trim(); if (s && !updateDiseaseSymptomes.includes(s)) setUpdateDiseaseSymptomes(prev => [...prev, s]); setUpdateSymptomeInput(''); } }}
                    placeholder="Ajouter un symptôme (Entrée pour valider)"
                    style={{ ...inputStyle, flex: 1 }} />
                  <button onClick={() => { const s = updateSymptomeInput.trim(); if (s && !updateDiseaseSymptomes.includes(s)) setUpdateDiseaseSymptomes(prev => [...prev, s]); setUpdateSymptomeInput(''); }}
                    style={{ ...primaryBtn(false), padding: '0 18px', flexShrink: 0 }}>
                    <Plus size={15} /> Ajouter
                  </button>
                </div>
                {updateDiseaseSymptomes.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 12 }}>
                    {updateDiseaseSymptomes.map(s => (
                      <span key={s} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: C.primarySoft, color: C.primary, borderRadius: 99, padding: '5px 12px', fontSize: 13, fontWeight: 600 }}>
                        {s}
                        <button onClick={() => setUpdateDiseaseSymptomes(prev => prev.filter(x => x !== s))}
                          style={{ background: 'none', border: 'none', cursor: 'pointer', color: C.primary, display: 'flex', padding: 0 }}>
                          <X size={13} />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1.3fr', gap: 14, marginBottom: 20 }}>
                <div>
                  <label style={labelStyle}>Cas supplémentaires</label>
                  <input type="number" min={0} max={300} value={updateNCasSupp}
                    onChange={e => setUpdateNCasSupp(Number(e.target.value))} style={inputStyle} />
                  <p style={{ fontSize: 11, color: '#94A3B8', marginTop: 4 }}>0 = aucun ajout</p>
                </div>
                <div>
                  <label style={labelStyle}>Boost IA (facteur)</label>
                  <input type="number" min={1.0} max={10.0} step={0.5} value={updateBoostFactor}
                    onChange={e => setUpdateBoostFactor(Number(e.target.value))} style={inputStyle} />
                  <p style={{ fontSize: 11, color: '#94A3B8', marginTop: 4 }}>Défaut = 4.0</p>
                </div>
                <label style={{ display: 'flex', alignItems: 'flex-start', gap: 9, cursor: 'pointer', fontSize: 13, fontWeight: 600, color: '#334155', paddingTop: 26 }}>
                  <input type="checkbox" checked={updateRemplaceExistants} onChange={e => setUpdateRemplaceExistants(e.target.checked)} style={{ width: 16, height: 16, marginTop: 1, accentColor: C.primary }} />
                  <span>Remplacer les cas existants
                    <span style={{ display: 'block', fontWeight: 400, color: '#94A3B8', fontSize: 11, marginTop: 2 }}>Régénère avec les nouveaux symptômes</span>
                  </span>
                </label>
              </div>

              {updateResult && (
                <div style={{ background: updateResult.success ? C.successSoft : C.dangerSoft, border: `1px solid ${updateResult.success ? '#86EFAC' : '#FECACA'}`, borderRadius: 10, padding: '11px 15px', marginBottom: 16, fontSize: 13, color: updateResult.success ? '#166534' : '#B91C1C', display: 'flex', alignItems: 'center', gap: 8 }}>
                  {updateResult.success ? <CheckCircle size={14} /> : <XCircle size={14} />}{updateResult.message}
                </div>
              )}

              <div style={{ display: 'flex', gap: 12 }}>
                <button onClick={handleUpdateDisease}
                  disabled={updateLoading || deleteLoading || updateDiseaseSymptomes.length < 1}
                  style={{ ...primaryBtn(updateLoading || deleteLoading || updateDiseaseSymptomes.length < 1), flex: 1 }}>
                  {updateLoading
                    ? <><RefreshCw size={15} style={{ animation: 'spin 1s linear infinite' }} /> Mise à jour…</>
                    : <><RefreshCw size={15} /> Mettre à jour la maladie</>}
                </button>
                <button onClick={handleDeleteDisease} disabled={updateLoading || deleteLoading}
                  title="Supprimer cette maladie du dataset"
                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, padding: '12px 20px', borderRadius: 10, background: C.dangerSoft, color: C.danger, border: '1px solid #FECACA', fontSize: 14, fontWeight: 600, cursor: (updateLoading || deleteLoading) ? 'not-allowed' : 'pointer', opacity: (updateLoading || deleteLoading) ? 0.5 : 1 }}>
                  {deleteLoading ? <RefreshCw size={15} style={{ animation: 'spin 1s linear infinite' }} /> : <><Trash2 size={15} /> Supprimer</>}
                </button>
                <button onClick={closeEdit} disabled={updateLoading || deleteLoading}
                  title="Annuler et fermer le formulaire"
                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, padding: '12px 20px', borderRadius: 10, background: '#fff', color: '#334155', border: `1px solid ${C.border}`, fontSize: 14, fontWeight: 600, cursor: (updateLoading || deleteLoading) ? 'not-allowed' : 'pointer', opacity: (updateLoading || deleteLoading) ? 0.5 : 1 }}>
                  Annuler
                </button>
              </div>
            </>
          )}

          {!updateDiseaseDetails && (
            <div style={{ padding: '28px 20px', textAlign: 'center', color: C.textSoft, fontSize: 13, background: C.bg, borderRadius: 10 }}>
              Choisissez une maladie puis cliquez sur <strong>Charger</strong> pour afficher le formulaire d'édition.
            </div>
          )}
        </Section>
      )}

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
