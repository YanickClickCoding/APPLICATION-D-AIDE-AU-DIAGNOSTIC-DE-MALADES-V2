import { useState, useEffect, useCallback } from 'react';
import {
  Database, FlaskConical, RefreshCw, CheckCircle, XCircle,
  AlertTriangle, Plus, X, Package, Zap, Download, Activity,
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

const CATEGORIES = [
  'Infectieuses', 'Cardiovasculaires', 'Respiratoires', 'Gastro-intestinales',
  'Endocriniennes / Métaboliques', 'Hépatiques', 'Neurologiques', 'Rhumatologiques',
  'Dermatologiques', 'Ophtalmologiques', 'Hématologiques', 'Rénales / Urinaires', 'Autres',
];

export default function AdminDataset() {
  const { token } = useAuth();
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  // ── Dataset stats & listes ──────────────────────────────────────────────────
  const [datasetStats, setDatasetStats] = useState<DatasetStats | null>(null);
  const [maladiesNoms, setMaladiesNoms] = useState<string[]>([]);
  const [maladiesExistantes, setMaladiesExistantes] = useState<string[]>([]);
  const [modelFiles, setModelFiles] = useState<ModelFile[]>([]);
  const [datasetInfo, setDatasetInfo] = useState<{ found: boolean; path: string | null; size_mb: number | null } | null>(null);

  // ── Export modèles ──────────────────────────────────────────────────────────
  const [downloadingFile, setDownloadingFile] = useState<string | null>(null);

  // ── Refresh symptômes ───────────────────────────────────────────────────────
  const [refreshingSymptomes, setRefreshingSymptomes] = useState(false);

  const handleRefreshSymptomes = async () => {
    if (!token) return;
    setRefreshingSymptomes(true);
    try {
      const res = await fetch('http://localhost:8000/api/admin/symptomes/refresh', {
        method: 'POST', headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erreur');
      showToast(`Cache symptômes mis à jour — ${data.total} symptômes disponibles en consultation`);
    } catch (e: any) {
      showToast(e.message || 'Erreur lors du refresh', false);
    } finally {
      setRefreshingSymptomes(false);
    }
  };

  // ── Ajouter une maladie ─────────────────────────────────────────────────────
  const [newDiseaseName, setNewDiseaseName] = useState('');
  const [newDiseaseCateg, setNewDiseaseCateg] = useState('Infectieuses');
  const [newDiseaseSymptomes, setNewDiseaseSymptomes] = useState<string[]>([]);
  const [newSymptomeInput, setNewSymptomeInput] = useState('');
  const [newDiseaseNCas, setNewDiseaseNCas] = useState(80);
  const [addDiseaseLoading, setAddDiseaseLoading] = useState(false);
  const [addDiseaseResult, setAddDiseaseResult] = useState<{ success: boolean; message: string; total?: number } | null>(null);

  // ── Modifier une maladie ────────────────────────────────────────────────────
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

    // Étape 1 : ouvrir le dialogue "Enregistrer sous" AVANT tout téléchargement
    let fileHandle: any = null;
    if ('showSaveFilePicker' in window) {
      try {
        fileHandle = await (window as any).showSaveFilePicker({
          suggestedName: filename,
          types: [{ description: 'Modèle ML', accept: { 'application/octet-stream': ['.joblib'] } }],
        });
      } catch (err: any) {
        // L'utilisateur a annulé → on s'arrête ici, aucun téléchargement
        if (err.name === 'AbortError') return;
        // showSaveFilePicker non supporté ou autre erreur → fallback classique
        fileHandle = null;
      }
    }

    // Étape 2 : l'emplacement est choisi (ou fallback), on télécharge depuis le backend
    setDownloadingFile(filename);
    try {
      const res = await fetch(`http://localhost:8000/api/admin/models/download/${encodeURIComponent(filename)}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Téléchargement échoué');
      const blob = await res.blob();

      if (fileHandle) {
        // Écrire directement dans le fichier choisi
        const writable = await fileHandle.createWritable();
        await writable.write(blob);
        await writable.close();
      } else {
        // Fallback : téléchargement classique vers le dossier Téléchargements
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
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
        const noms = (d.maladies as { nom: string }[]).map(m => m.nom.trim());
        setMaladiesNoms(noms);
        setMaladiesExistantes(noms.map(n => n.toLowerCase()));
      }
      if (statusRes.ok) {
        const s = await statusRes.json();
        setDatasetInfo(s.dataset ?? null);
        setModelFiles(s.model_files ?? []);
      }
    } catch { /* silencieux */ }
  }, [token]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const diseaseAlreadyExists = maladiesExistantes.includes(newDiseaseName.trim().toLowerCase());

  // ── Handlers ajout ──────────────────────────────────────────────────────────
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
        body: JSON.stringify({ nom_maladie: newDiseaseName.trim(), categorie: newDiseaseCateg, symptomes: newDiseaseSymptomes, n_cas: newDiseaseNCas }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erreur serveur');
      setAddDiseaseResult({ success: true, message: data.message, total: data.total_dataset });
      setNewDiseaseName(''); setNewDiseaseSymptomes([]); setNewDiseaseNCas(80);
      fetchAll();
      // Refresh automatique du cache de symptômes pour la consultation
      try {
        await fetch('http://localhost:8000/api/admin/symptomes/refresh', {
          method: 'POST', headers: { Authorization: `Bearer ${token}` },
        });
        showToast(`"${data.maladie}" ajoutée — ${data.cas_ajoutes} cas générés, symptômes disponibles en consultation`);
      } catch {
        showToast(`${data.cas_ajoutes} cas ajoutés pour "${data.maladie}" !`);
      }
    } catch (e: any) {
      setAddDiseaseResult({ success: false, message: e.message });
      showToast(e.message, false);
    } finally { setAddDiseaseLoading(false); }
  };

  // ── Handlers modification ───────────────────────────────────────────────────
  const handleLoadDiseaseDetails = async () => {
    if (!token || !updateDiseaseName.trim()) return;
    setUpdateLoadingDetails(true);
    setUpdateDiseaseDetails(null);
    setUpdateDiseaseSymptomes([]);
    try {
      const res = await fetch(`http://localhost:8000/api/admin/dataset/maladies/${encodeURIComponent(updateDiseaseName.trim())}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const d = await res.json();
      if (!res.ok) throw new Error(d.detail || 'Maladie introuvable');
      setUpdateDiseaseDetails(d);
      setUpdateDiseaseSymptomes((d.symptomes as Array<{ nom: string }>).slice(0, 10).map(s => s.nom));
      if (d.custom_rules?.boost_factor) setUpdateBoostFactor(d.custom_rules.boost_factor);
      showToast(`${d.n_cas} cas trouvés — symptômes pré-remplis`);
    } catch (e: any) { showToast(e.message, false); }
    finally { setUpdateLoadingDetails(false); }
  };

  const handleUpdateDisease = async () => {
    if (!token) return;
    if (!updateDiseaseName.trim()) { showToast('Sélectionnez une maladie', false); return; }
    if (!maladiesNoms.some(m => m.toLowerCase() === updateDiseaseName.trim().toLowerCase())) {
      showToast(`"${updateDiseaseName}" n'existe pas`, false); return;
    }
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
      // Refresh automatique du cache de symptômes pour la consultation
      try {
        await fetch('http://localhost:8000/api/admin/symptomes/refresh', {
          method: 'POST', headers: { Authorization: `Bearer ${token}` },
        });
        showToast(`"${data.maladie}" mise à jour — symptômes disponibles en consultation`);
      } catch {
        showToast(`Maladie "${data.maladie}" mise à jour !`);
      }
    } catch (e: any) {
      setUpdateResult({ success: false, message: e.message });
      showToast(e.message, false);
    } finally { setUpdateLoading(false); }
  };

  return (
    <div style={{ maxWidth: 960, margin: '0 auto' }}>
      {/* Toast */}
      {toast && (
        <div style={{ position: 'fixed', top: 24, right: 24, zIndex: 9999, padding: '12px 20px', borderRadius: 10, color: 'white', background: toast.ok ? '#059669' : '#DC2626', boxShadow: '0 4px 20px rgba(0,0,0,.15)', display: 'flex', alignItems: 'center', gap: 8, fontSize: 14, fontWeight: 600 }}>
          {toast.ok ? <CheckCircle size={16} /> : <XCircle size={16} />}{toast.msg}
        </div>
      )}

      {/* En-tête */}
      <div style={{ marginBottom: 28, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 900, color: '#111827', margin: 0 }}>Dataset & Maladies</h1>
          <p style={{ color: '#6B7280', marginTop: 4, fontSize: 14 }}>
            Gérez le dataset d'entraînement, ajoutez et modifiez les maladies
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={handleRefreshSymptomes}
            disabled={refreshingSymptomes}
            title="Reconstruire la liste des symptômes disponibles en consultation"
            style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px', borderRadius: 8, border: '1px solid #A7F3D0', background: '#ECFDF5', cursor: refreshingSymptomes ? 'not-allowed' : 'pointer', fontSize: 13, fontWeight: 600, color: '#065F46', opacity: refreshingSymptomes ? 0.7 : 1 }}>
            <Activity size={14} style={{ animation: refreshingSymptomes ? 'spin 1s linear infinite' : 'none' }} />
            {refreshingSymptomes ? 'Actualisation…' : 'Actualiser les symptômes'}
          </button>
          <button onClick={fetchAll} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px', borderRadius: 8, border: '1px solid #E5E7EB', background: 'white', cursor: 'pointer', fontSize: 13, fontWeight: 600, color: '#374151' }}>
            <RefreshCw size={14} /> Actualiser
          </button>
        </div>
      </div>

      {/* ─── Dataset info ─── */}
      {datasetInfo && (
        <Card title="Dataset d'entraînement" icon={Database} accent="#0D9488">
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap', marginBottom: datasetStats ? 16 : 0 }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '3px 10px', borderRadius: 99, background: datasetInfo.found ? '#ECFDF5' : '#FEF2F2', color: datasetInfo.found ? '#065F46' : '#991B1B', fontSize: 12, fontWeight: 700 }}>
              {datasetInfo.found ? <CheckCircle size={12} /> : <XCircle size={12} />}
              {datasetInfo.found ? 'Trouvé' : 'Introuvable'}
            </span>
            {datasetInfo.found && (
              <>
                <span style={{ fontSize: 13, color: '#374151' }}>
                  <strong>{datasetInfo.size_mb} Mo</strong>
                </span>
                <code style={{ fontSize: 11, color: '#6B7280', background: '#F9FAFB', padding: '3px 8px', borderRadius: 4, wordBreak: 'break-all' }}>
                  {datasetInfo.path}
                </code>
              </>
            )}
            {!datasetInfo.found && (
              <span style={{ fontSize: 12, color: '#991B1B' }}>
                Placez le fichier dans <code>les ressources dataset/dataset_medical_robust_10000_cas.csv</code>
              </span>
            )}
          </div>
          {datasetStats && (
            <div style={{ display: 'flex', gap: 16 }}>
              <div style={{ flex: 1, background: '#F5F3FF', borderRadius: 10, padding: '12px 16px', textAlign: 'center' }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: '#7C3AED' }}>{datasetStats.total_maladies}</div>
                <div style={{ fontSize: 12, color: '#6B7280', marginTop: 2 }}>Maladies dans le dataset</div>
              </div>
              <div style={{ flex: 1, background: '#EDE9FE', borderRadius: 10, padding: '12px 16px', textAlign: 'center' }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: '#6D28D9' }}>{datasetStats.total_cas.toLocaleString('fr-FR')}</div>
                <div style={{ fontSize: 12, color: '#6B7280', marginTop: 2 }}>Cas d'entraînement total</div>
              </div>
            </div>
          )}
        </Card>
      )}

      {/* ─── Fichiers modèles ─── */}
      {modelFiles.length > 0 && (
        <Card title="Fichiers modèles sauvegardés" icon={Package} accent="#D97706">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {modelFiles.map((f, i) => (
              <div key={f.name} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px', borderRadius: 8, background: i === 0 ? '#FFFBEB' : '#F9FAFB', border: `1px solid ${i === 0 ? '#FCD34D' : '#E5E7EB'}`, fontSize: 13 }}>
                <Zap size={14} style={{ color: i === 0 ? '#D97706' : '#9CA3AF', flexShrink: 0 }} />
                <span style={{ flex: 1, fontFamily: 'monospace', fontSize: 12, color: '#374151' }}>{f.name}</span>
                <span style={{ color: '#6B7280', fontSize: 12, flexShrink: 0 }}>{f.size_mb} Mo</span>
                {f.modified && <span style={{ color: '#9CA3AF', fontSize: 11, flexShrink: 0 }}>{new Date(f.modified).toLocaleString('fr-FR')}</span>}
                {i === 0 && <span style={{ background: '#D97706', color: 'white', padding: '1px 8px', borderRadius: 99, fontSize: 10, fontWeight: 700, flexShrink: 0 }}>ACTIF</span>}
                <button
                  onClick={() => handleDownloadModel(f.name)}
                  disabled={downloadingFile === f.name}
                  title={`Télécharger ${f.name}`}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 5,
                    padding: '5px 10px', borderRadius: 6,
                    border: '1px solid #D1D5DB', background: 'white',
                    cursor: downloadingFile === f.name ? 'not-allowed' : 'pointer',
                    fontSize: 11, fontWeight: 600, color: '#374151',
                    flexShrink: 0, opacity: downloadingFile === f.name ? 0.6 : 1,
                    transition: 'background 0.15s',
                  }}
                  onMouseEnter={e => { if (downloadingFile !== f.name) (e.currentTarget as HTMLButtonElement).style.background = '#F3F4F6'; }}
                  onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.background = 'white'; }}
                >
                  {downloadingFile === f.name
                    ? <RefreshCw size={12} style={{ animation: 'spin 1s linear infinite' }} />
                    : <Download size={12} />}
                  {downloadingFile === f.name ? 'Export…' : 'Exporter'}
                </button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* ─── Ajouter une maladie ─── */}
      <Card title="Ajouter une maladie au dataset" icon={FlaskConical} accent="#7C3AED">
        <div style={{ background: '#FFF7ED', border: '1px solid #FED7AA', borderRadius: 10, padding: '12px 16px', marginBottom: 20, display: 'flex', gap: 10 }}>
          <AlertTriangle size={16} style={{ color: '#D97706', flexShrink: 0, marginTop: 1 }} />
          <p style={{ fontSize: 13, color: '#92400E', margin: 0 }}>
            Après l'ajout, lancez un <strong>réentraînement</strong> depuis la page "Modèle IA" pour que la nouvelle maladie soit détectable.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
          <div>
            <label style={{ fontSize: 13, fontWeight: 700, color: '#374151', display: 'block', marginBottom: 6 }}>
              Nom de la maladie <span style={{ color: '#EF4444' }}>*</span>
            </label>
            <input
              type="text"
              className="sp-form-input"
              placeholder="Ex : Leishmaniose, Bilharziose…"
              value={newDiseaseName}
              onChange={e => { setNewDiseaseName(e.target.value); setAddDiseaseResult(null); }}
              style={{ borderColor: diseaseAlreadyExists ? '#EF4444' : undefined }}
            />
            {diseaseAlreadyExists && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 6, padding: '6px 10px', background: '#FEF2F2', borderRadius: 6, border: '1px solid #FECACA' }}>
                <XCircle size={14} style={{ color: '#DC2626', flexShrink: 0 }} />
                <span style={{ fontSize: 12, color: '#B91C1C', fontWeight: 600 }}>
                  Cette maladie existe déjà — utilisez "Modifier" ci-dessous.
                </span>
              </div>
            )}
            {!diseaseAlreadyExists && newDiseaseName.trim().length >= 2 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 6, padding: '6px 10px', background: '#ECFDF5', borderRadius: 6, border: '1px solid #A7F3D0' }}>
                <CheckCircle size={14} style={{ color: '#059669', flexShrink: 0 }} />
                <span style={{ fontSize: 12, color: '#047857', fontWeight: 600 }}>Nom disponible.</span>
              </div>
            )}
          </div>
          <div>
            <label style={{ fontSize: 13, fontWeight: 700, color: '#374151', display: 'block', marginBottom: 6 }}>
              Catégorie médicale <span style={{ color: '#EF4444' }}>*</span>
            </label>
            <select className="sp-form-select" value={newDiseaseCateg} onChange={e => setNewDiseaseCateg(e.target.value)}>
              {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ fontSize: 13, fontWeight: 700, color: '#374151', display: 'block', marginBottom: 6 }}>
            Nombre de cas synthétiques : <strong style={{ color: '#7C3AED' }}>{newDiseaseNCas}</strong>
          </label>
          <input type="range" min={20} max={300} step={10} value={newDiseaseNCas}
            onChange={e => setNewDiseaseNCas(Number(e.target.value))}
            style={{ width: '100%', accentColor: '#7C3AED' }} />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#9CA3AF', marginTop: 2 }}>
            <span>20 (minimal)</span><span>80 (recommandé)</span><span>300 (maximum)</span>
          </div>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ fontSize: 13, fontWeight: 700, color: '#374151', display: 'block', marginBottom: 6 }}>
            Symptômes caractéristiques <span style={{ color: '#EF4444' }}>*</span>
            <span style={{ fontWeight: 400, color: '#6B7280', marginLeft: 8 }}>({newDiseaseSymptomes.length} ajouté{newDiseaseSymptomes.length > 1 ? 's' : ''})</span>
          </label>
          <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
            <input
              type="text" className="sp-form-input"
              placeholder="Ex : Fièvre, Douleurs articulaires…"
              value={newSymptomeInput}
              onChange={e => setNewSymptomeInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleAddSymptome(); } }}
              style={{ flex: 1 }}
            />
            <button type="button" onClick={handleAddSymptome} disabled={!newSymptomeInput.trim()}
              className="sp-btn sp-btn-primary"
              style={{ padding: '0 16px', background: '#7C3AED', opacity: !newSymptomeInput.trim() ? 0.5 : 1 }}>
              <Plus size={14} /> Ajouter
            </button>
          </div>
          {newDiseaseSymptomes.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {newDiseaseSymptomes.map(s => (
                <span key={s} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: '#EDE9FE', color: '#5B21B6', borderRadius: 99, padding: '4px 12px', fontSize: 13, fontWeight: 600 }}>
                  {s}
                  <button type="button" onClick={() => setNewDiseaseSymptomes(prev => prev.filter(x => x !== s))}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#7C3AED', display: 'flex', padding: 0 }}>
                    <X size={12} />
                  </button>
                </span>
              ))}
            </div>
          )}
          {newDiseaseSymptomes.length === 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 10px', background: '#FFF7ED', borderRadius: 6, border: '1px solid #FED7AA' }}>
              <AlertTriangle size={13} style={{ color: '#D97706', flexShrink: 0 }} />
              <span style={{ fontSize: 12, color: '#92400E' }}>Minimum 2 symptômes requis. Appuyez sur <strong>Entrée</strong> pour ajouter.</span>
            </div>
          )}
        </div>

        {addDiseaseResult && (
          <div style={{ padding: '12px 16px', borderRadius: 10, marginBottom: 16, background: addDiseaseResult.success ? '#ECFDF5' : '#FEF2F2', border: `1px solid ${addDiseaseResult.success ? '#A7F3D0' : '#FECACA'}`, display: 'flex', alignItems: 'flex-start', gap: 10 }}>
            {addDiseaseResult.success ? <CheckCircle size={16} style={{ color: '#059669', flexShrink: 0, marginTop: 1 }} /> : <XCircle size={16} style={{ color: '#DC2626', flexShrink: 0, marginTop: 1 }} />}
            <div>
              <p style={{ fontSize: 13, fontWeight: 600, color: addDiseaseResult.success ? '#065F46' : '#991B1B', margin: '0 0 2px' }}>
                {addDiseaseResult.success ? 'Maladie ajoutée avec succès' : 'Erreur'}
              </p>
              <p style={{ fontSize: 12, color: addDiseaseResult.success ? '#047857' : '#B91C1C', margin: 0 }}>
                {addDiseaseResult.message}{addDiseaseResult.total && ` — Dataset total : ${addDiseaseResult.total.toLocaleString('fr-FR')} cas`}
              </p>
            </div>
          </div>
        )}

        <button onClick={handleAddDisease}
          disabled={addDiseaseLoading || !newDiseaseName.trim() || newDiseaseSymptomes.length < 2 || diseaseAlreadyExists}
          className="sp-btn sp-btn-primary"
          style={{ width: '100%', justifyContent: 'center', background: '#7C3AED', opacity: (addDiseaseLoading || !newDiseaseName.trim() || newDiseaseSymptomes.length < 2 || diseaseAlreadyExists) ? 0.6 : 1 }}>
          {addDiseaseLoading
            ? <><RefreshCw size={15} style={{ animation: 'spin 1s linear infinite' }} /> Génération en cours…</>
            : <><FlaskConical size={15} /> Ajouter la maladie au dataset</>}
        </button>
      </Card>

      {/* ─── Modifier une maladie ─── */}
      <Card title="Modifier une maladie existante" icon={RefreshCw} accent="#0369A1">
        <div style={{ background: '#EFF6FF', border: '1px solid #BFDBFE', borderRadius: 10, padding: '12px 16px', marginBottom: 20, display: 'flex', gap: 10 }}>
          <AlertTriangle size={16} style={{ color: '#1D4ED8', flexShrink: 0, marginTop: 1 }} />
          <p style={{ fontSize: 13, color: '#1E40AF', margin: 0 }}>
            Modifiez les <strong>symptômes caractéristiques</strong> et le <strong>boost clinique</strong> d'une maladie existante. Un <strong>réentraînement</strong> est nécessaire pour appliquer les changements au modèle.
          </p>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ fontSize: 13, fontWeight: 700, color: '#374151', display: 'block', marginBottom: 6 }}>
            Maladie à modifier <span style={{ color: '#EF4444' }}>*</span>
          </label>
          <div style={{ display: 'flex', gap: 10 }}>
            <select
              value={updateDiseaseName}
              onChange={e => { setUpdateDiseaseName(e.target.value); setUpdateDiseaseDetails(null); setUpdateDiseaseSymptomes([]); setUpdateResult(null); }}
              style={{ flex: 1, padding: '9px 12px', border: '1.5px solid #D1D5DB', borderRadius: 8, fontSize: 14, background: 'white' }}
            >
              <option value="">— Choisir une maladie —</option>
              {[...maladiesNoms].sort((a, b) => a.localeCompare(b, 'fr')).map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
            <button onClick={handleLoadDiseaseDetails} disabled={!updateDiseaseName || updateLoadingDetails}
              className="sp-btn" style={{ background: '#0369A1', color: 'white', padding: '8px 16px', fontSize: 13, opacity: (!updateDiseaseName || updateLoadingDetails) ? 0.6 : 1 }}>
              {updateLoadingDetails ? <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <Database size={14} />}
              {updateLoadingDetails ? 'Chargement…' : 'Charger'}
            </button>
          </div>
        </div>

        {updateDiseaseDetails && (
          <div style={{ background: '#F0F9FF', border: '1px solid #BAE6FD', borderRadius: 8, padding: '10px 14px', marginBottom: 16, fontSize: 13, color: '#0C4A6E' }}>
            <strong>{updateDiseaseName}</strong> — {updateDiseaseDetails.n_cas} cas dans le dataset —{' '}
            {updateDiseaseDetails.symptomes.length} symptômes distincts recensés
          </div>
        )}

        <div style={{ marginBottom: 16 }}>
          <label style={{ fontSize: 13, fontWeight: 700, color: '#374151', display: 'block', marginBottom: 6 }}>
            Symptômes caractéristiques <span style={{ color: '#EF4444' }}>*</span>
            <span style={{ fontWeight: 400, color: '#6B7280', marginLeft: 8 }}>(boostent la probabilité à la prédiction)</span>
          </label>
          <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
            <input type="text" value={updateSymptomeInput}
              onChange={e => setUpdateSymptomeInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); const s = updateSymptomeInput.trim(); if (s && !updateDiseaseSymptomes.includes(s)) setUpdateDiseaseSymptomes(prev => [...prev, s]); setUpdateSymptomeInput(''); } }}
              placeholder="Ajouter un symptôme (Entrée pour valider)"
              style={{ flex: 1, padding: '9px 12px', border: '1.5px solid #D1D5DB', borderRadius: 8, fontSize: 13 }} />
            <button onClick={() => { const s = updateSymptomeInput.trim(); if (s && !updateDiseaseSymptomes.includes(s)) setUpdateDiseaseSymptomes(prev => [...prev, s]); setUpdateSymptomeInput(''); }}
              className="sp-btn" style={{ background: '#0369A1', color: 'white', padding: '8px 14px', fontSize: 13 }}>
              <Plus size={14} /> Ajouter
            </button>
          </div>
          {updateDiseaseSymptomes.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {updateDiseaseSymptomes.map(s => (
                <span key={s} style={{ display: 'inline-flex', alignItems: 'center', gap: 4, background: '#DBEAFE', color: '#1E40AF', borderRadius: 99, padding: '3px 10px', fontSize: 12, fontWeight: 600 }}>
                  {s}
                  <button onClick={() => setUpdateDiseaseSymptomes(prev => prev.filter(x => x !== s))}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#1E40AF', lineHeight: 1 }}>
                    <X size={11} />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 16 }}>
          <div>
            <label style={{ fontSize: 12, fontWeight: 700, color: '#374151', display: 'block', marginBottom: 4 }}>Cas supplémentaires</label>
            <input type="number" min={0} max={300} value={updateNCasSupp}
              onChange={e => setUpdateNCasSupp(Number(e.target.value))}
              style={{ width: '100%', padding: '8px 10px', border: '1.5px solid #D1D5DB', borderRadius: 8, fontSize: 13 }} />
            <p style={{ fontSize: 11, color: '#9CA3AF', marginTop: 3 }}>0 = aucun ajout</p>
          </div>
          <div>
            <label style={{ fontSize: 12, fontWeight: 700, color: '#374151', display: 'block', marginBottom: 4 }}>Boost IA (facteur)</label>
            <input type="number" min={1.0} max={10.0} step={0.5} value={updateBoostFactor}
              onChange={e => setUpdateBoostFactor(Number(e.target.value))}
              style={{ width: '100%', padding: '8px 10px', border: '1.5px solid #D1D5DB', borderRadius: 8, fontSize: 13 }} />
            <p style={{ fontSize: 11, color: '#9CA3AF', marginTop: 3 }}>Défaut = 4.0</p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 13, fontWeight: 600, color: '#374151' }}>
              <input type="checkbox" checked={updateRemplaceExistants} onChange={e => setUpdateRemplaceExistants(e.target.checked)} style={{ width: 16, height: 16 }} />
              Remplacer les cas existants
            </label>
            <p style={{ fontSize: 11, color: '#9CA3AF', marginTop: 4 }}>Supprime les anciens cas et en régénère avec les nouveaux symptômes</p>
          </div>
        </div>

        {updateResult && (
          <div style={{ background: updateResult.success ? '#F0FDF4' : '#FEF2F2', border: `1px solid ${updateResult.success ? '#86EFAC' : '#FECACA'}`, borderRadius: 8, padding: '10px 14px', marginBottom: 14, fontSize: 13, color: updateResult.success ? '#166534' : '#B91C1C' }}>
            {updateResult.success ? <CheckCircle size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} /> : <XCircle size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />}
            {updateResult.message}
          </div>
        )}

        <button onClick={handleUpdateDisease}
          disabled={updateLoading || !updateDiseaseName || updateDiseaseSymptomes.length < 1}
          className="sp-btn sp-btn-primary"
          style={{ width: '100%', justifyContent: 'center', background: '#0369A1', opacity: (updateLoading || !updateDiseaseName || updateDiseaseSymptomes.length < 1) ? 0.6 : 1 }}>
          {updateLoading
            ? <><RefreshCw size={15} style={{ animation: 'spin 1s linear infinite' }} /> Mise à jour en cours…</>
            : <><RefreshCw size={15} /> Mettre à jour la maladie</>}
        </button>
      </Card>

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
