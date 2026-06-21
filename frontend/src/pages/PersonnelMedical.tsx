import React, { useState, useEffect, useCallback } from 'react';
import {
  UserCheck, Users, Phone, Mail, Stethoscope, Activity,
  Search, Plus, Edit2, Trash2, X, ToggleLeft, ToggleRight,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import { adminAPI, type AdminMedecin, type AdminMedecinCreate, type AdminInfirmier, type AdminInfirmierCreate } from '../services/api';

const EMPTY_MEDECIN: AdminMedecinCreate = { nom: '', prenoms: '', specialite: '', telephone: '', disponible: true };
const EMPTY_INFIRMIER: AdminInfirmierCreate = { nom: '', prenoms: '', telephone: '', email: '', disponible: true };

const SPECIALITES = [
  "Médecine Générale", "Cardiologie", "Pédiatrie", "Gynécologie-Obstétrique", 
  "Chirurgie Générale", "Neurologie", "Ophtalmologie", "Dermatologie", 
  "Radiologie", "Anesthésiologie", "Rhumatologie", "Urologie", "ORL", 
  "Psychiatrie", "Pneumologie", "Endocrinologie", "Infectiologie", 
  "Gastro-entérologie", "Hématologie", "Oncologie", "Néphrologie",
  "Médecine Interne", "Médecine d'Urgence", "Gériatrie", "Stomatologie",
  "Chirurgie Orthopédique", "Chirurgie Cardiaque", "Chirurgie Vasculaire",
  "Chirurgie Pédiatrique", "Chirurgie Plastique", "Neurochirurgie",
  "Allergologie", "Médecine du Travail", "Médecine Physique et Réadaptation",
  "Médecine Nucléaire", "Génétique Médicale", "Anatomopathologie",
  "Biologie Médicale", "Santé Publique", "Réanimation", "Addictologie"
];

const inputStyle: React.CSSProperties = {
  width: '100%', padding: '8px 10px', border: '1px solid #D1D5DB',
  borderRadius: 6, fontSize: 13, boxSizing: 'border-box',
};

const PersonnelMedical = () => {
  const { token, isLoading: authLoading } = useAuth();
  const { showToast } = useToast();
  const [medecins, setMedecins] = useState<AdminMedecin[]>([]);
  const [infirmiers, setInfirmiers] = useState<AdminInfirmier[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'medecins' | 'infirmiers'>('medecins');
  const [searchTerm, setSearchTerm] = useState('');

  // Create modal
  const [createModal, setCreateModal] = useState(false);
  const [createRole, setCreateRole] = useState<'medecin' | 'infirmier'>('medecin');
  const [createForm, setCreateForm] = useState<any>(EMPTY_MEDECIN);
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState('');

  // Edit modals
  const [editMedecin, setEditMedecin] = useState<AdminMedecin | null>(null);
  const [editInfirmier, setEditInfirmier] = useState<AdminInfirmier | null>(null);
  const [editMedecinForm, setEditMedecinForm] = useState<Partial<AdminMedecinCreate & { disponible: boolean }>>({});
  const [editInfirmierForm, setEditInfirmierForm] = useState<Partial<AdminInfirmierCreate & { disponible: boolean }>>({});
  const [editMedecinLoading, setEditMedecinLoading] = useState(false);
  const [editInfirmierLoading, setEditInfirmierLoading] = useState(false);

  // Delete modals
  const [deleteMedecinModal, setDeleteMedecinModal] = useState<{ id: number; name: string } | null>(null);
  const [deleteInfirmierModal, setDeleteInfirmierModal] = useState<{ id: number; name: string } | null>(null);

  const loadData = useCallback(async () => {
    if (!token) return;
    try {
      setLoading(true);
      const [meds, infs] = await Promise.all([
        adminAPI.getMedecins(token),
        adminAPI.getInfirmiers(token),
      ]);
      setMedecins(meds);
      setInfirmiers(infs);
    } catch (e) {
      console.error('Erreur chargement personnel:', e);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { if (!authLoading) loadData(); }, [loadData, authLoading]);

  // ── Médecins CRUD ──────────────────────────────────────────

  const handleCreatePersonnel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setCreateLoading(true);
    setCreateError('');
    try {
      if (createRole === 'medecin') {
        const m = await adminAPI.createMedecin(token, createForm as AdminMedecinCreate);
        setMedecins(prev => [...prev, m]);
      } else {
        const inf = await adminAPI.createInfirmier(token, createForm as AdminInfirmierCreate);
        setInfirmiers(prev => [...prev, inf]);
      }
      setCreateModal(false);
    } catch (e: any) {
      setCreateError(e.detail || 'Erreur lors de la création');
    } finally {
      setCreateLoading(false);
    }
  };
  const handleUpdateMedecin = async () => {
    if (!editMedecin || !token) return;
    setEditMedecinLoading(true);
    try {
      const updated = await adminAPI.updateMedecin(token, editMedecin.medecin_id, editMedecinForm);
      setMedecins(prev => prev.map(m => m.medecin_id === updated.medecin_id ? updated : m));
      setEditMedecin(null);
      showToast('Médecin mis à jour', 'success');
    } catch (e: any) {
      showToast(e.detail || 'Erreur lors de la mise à jour', 'error');
    } finally {
      setEditMedecinLoading(false);
    }
  };

  const handleDeleteMedecin = async () => {
    if (!deleteMedecinModal || !token) return;
    try {
      await adminAPI.deleteMedecin(token, deleteMedecinModal.id);
      setMedecins(prev => prev.filter(m => m.medecin_id !== deleteMedecinModal.id));
      setDeleteMedecinModal(null);
      showToast('Médecin supprimé', 'success');
    } catch (e: any) {
      showToast(e.detail || 'Erreur lors de la suppression', 'error');
    }
  };

  const handleToggleMedecin = async (m: AdminMedecin) => {
    if (!token) return;
    try {
      const updated = await adminAPI.updateMedecin(token, m.medecin_id, { disponible: !m.disponible });
      setMedecins(prev => prev.map(x => x.medecin_id === updated.medecin_id ? updated : x));
      showToast(updated.disponible ? 'Médecin marqué disponible' : 'Médecin marqué indisponible', 'success');
    } catch (e: any) {
      showToast(e.detail || 'Erreur', 'error');
    }
  };

  const handleUpdateInfirmier = async () => {
    if (!editInfirmier || !token) return;
    setEditInfirmierLoading(true);
    try {
      const updated = await adminAPI.updateInfirmier(token, editInfirmier.infirmier_id, editInfirmierForm);
      setInfirmiers(prev => prev.map(i => i.infirmier_id === updated.infirmier_id ? updated : i));
      setEditInfirmier(null);
      showToast('Infirmier mis à jour', 'success');
    } catch (e: any) {
      showToast(e.detail || 'Erreur lors de la mise à jour', 'error');
    } finally {
      setEditInfirmierLoading(false);
    }
  };

  const handleDeleteInfirmier = async () => {
    if (!deleteInfirmierModal || !token) return;
    try {
      await adminAPI.deleteInfirmier(token, deleteInfirmierModal.id);
      setInfirmiers(prev => prev.filter(i => i.infirmier_id !== deleteInfirmierModal.id));
      setDeleteInfirmierModal(null);
      showToast('Infirmier supprimé', 'success');
    } catch (e: any) {
      showToast(e.detail || 'Erreur lors de la suppression', 'error');
    }
  };

  const handleToggleInfirmier = async (inf: AdminInfirmier) => {
    if (!token) return;
    try {
      const updated = await adminAPI.updateInfirmier(token, inf.infirmier_id, { disponible: !inf.disponible });
      setInfirmiers(prev => prev.map(x => x.infirmier_id === updated.infirmier_id ? updated : x));
      showToast(updated.disponible ? 'Infirmier marqué disponible' : 'Infirmier marqué indisponible', 'success');
    } catch (e: any) {
      showToast(e.detail || 'Erreur', 'error');
    }
  };

  // ── Filtres ────────────────────────────────────────────────

  const filteredMedecins = medecins.filter(m =>
    m.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    m.prenoms.toLowerCase().includes(searchTerm.toLowerCase()) ||
    m.specialite.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredInfirmiers = infirmiers.filter(i =>
    i.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    i.prenoms.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const medecinsDispo = medecins.filter(m => m.disponible).length;
  const infirmiersDispo = infirmiers.filter(i => i.disponible).length;

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <Activity size={48} style={{ animation: 'spin 1s linear infinite', color: '#4F46E5' }} />
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <>
      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Personnel Médical</h1>
          <p className="sp-page-subtitle">
            {medecins.length} médecin(s) · {infirmiers.length} infirmier(s)
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="sp-btn sp-btn-primary" onClick={() => { setCreateRole('medecin'); setCreateForm(EMPTY_MEDECIN); setCreateModal(true); setCreateError(''); }}>
            <Plus size={18} /> Ajouter personnel
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="sp-stats-grid sp-fade-in" style={{ marginBottom: '24px', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
        <div className="sp-stat-card" style={{ '--card-accent': '#4F46E5' } as React.CSSProperties}>
          <div className="sp-stat-icon" style={{ background: '#eef2ff', borderRadius: '14px', width: '54px', height: '54px' }}>
            <Stethoscope style={{ color: '#4F46E5', width: '24px', height: '24px' }} />
          </div>
          <div>
            <div className="sp-stat-value" style={{ fontSize: '38px', fontWeight: 900, color: '#0f172a' }}>{medecinsDispo}</div>
            <div className="sp-stat-label">Médecins Disponibles</div>
          </div>
        </div>
        <div className="sp-stat-card" style={{ '--card-accent': '#10B981' } as React.CSSProperties}>
          <div className="sp-stat-icon" style={{ background: '#d1fae5', borderRadius: '14px', width: '54px', height: '54px' }}>
            <UserCheck style={{ color: '#10B981', width: '24px', height: '24px' }} />
          </div>
          <div>
            <div className="sp-stat-value" style={{ fontSize: '38px', fontWeight: 900, color: '#0f172a' }}>{infirmiersDispo}</div>
            <div className="sp-stat-label">Infirmiers Disponibles</div>
          </div>
        </div>
        <div className="sp-stat-card" style={{ '--card-accent': '#8B5CF6' } as React.CSSProperties}>
          <div className="sp-stat-icon" style={{ background: '#ede9fe', borderRadius: '14px', width: '54px', height: '54px' }}>
            <Users style={{ color: '#8B5CF6', width: '24px', height: '24px' }} />
          </div>
          <div>
            <div className="sp-stat-value" style={{ fontSize: '38px', fontWeight: 900, color: '#0f172a' }}>{medecins.length}</div>
            <div className="sp-stat-label">Total Médecins</div>
          </div>
        </div>
        <div className="sp-stat-card" style={{ '--card-accent': '#06B6D4' } as React.CSSProperties}>
          <div className="sp-stat-icon" style={{ background: '#cffafe', borderRadius: '14px', width: '54px', height: '54px' }}>
            <Users style={{ color: '#06B6D4', width: '24px', height: '24px' }} />
          </div>
          <div>
            <div className="sp-stat-value" style={{ fontSize: '38px', fontWeight: 900, color: '#0f172a' }}>{infirmiers.length}</div>
            <div className="sp-stat-label">Total Infirmiers</div>
          </div>
        </div>
      </div>

      {/* Tabs and Search */}
      <div className="sp-card sp-fade-in" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px' }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setActiveTab('medecins')}
              className={`sp-btn ${activeTab === 'medecins' ? 'sp-btn-primary' : 'sp-btn-outline'}`}
            >
              <Stethoscope size={18} /> Médecins ({medecins.length})
            </button>
            <button
              onClick={() => setActiveTab('infirmiers')}
              className={`sp-btn ${activeTab === 'infirmiers' ? 'sp-btn-primary' : 'sp-btn-outline'}`}
            >
              <UserCheck size={18} /> Infirmiers ({infirmiers.length})
            </button>
          </div>
          <div style={{ position: 'relative', width: '300px' }}>
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
            <input
              type="text"
              placeholder="Rechercher..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              style={{ width: '100%', padding: '10px 12px 10px 40px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px' }}
            />
          </div>
        </div>
      </div>

      {/* Liste */}
      <div className="sp-card sp-fade-in">
        <div className="sp-card-header">
          <div className="sp-card-title">
            {activeTab === 'medecins' ? <Stethoscope size={20} /> : <UserCheck size={20} />}
            {activeTab === 'medecins' ? 'Liste des Médecins' : 'Liste des Infirmiers'}
          </div>
        </div>

        <div style={{ padding: 0 }}>
          {activeTab === 'medecins' ? (
            <div style={{ display: 'grid', gap: '1px', background: '#E5E7EB' }}>
              {filteredMedecins.map(m => (
                <div
                  key={m.medecin_id}
                  style={{ display: 'flex', alignItems: 'center', gap: '20px', padding: '20px', background: '#fff', transition: 'background 0.2s', opacity: m.disponible ? 1 : 0.65 }}
                  onMouseEnter={e => (e.currentTarget.style.background = '#F9FAFB')}
                  onMouseLeave={e => (e.currentTarget.style.background = '#fff')}
                >
                  <div style={{ width: '56px', height: '56px', borderRadius: '12px', background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '20px', fontWeight: 700, flexShrink: 0 }}>
                    {m.nom[0]}{m.prenoms[0]}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '16px', color: '#1F2937', marginBottom: '4px' }}>Dr. {m.prenoms} {m.nom}</div>
                    <span style={{ display: 'inline-block', padding: '2px 8px', background: '#EEF2FF', color: '#4F46E5', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                      {m.specialite}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#6B7280', fontSize: '14px' }}>
                    <Phone size={16} /> {m.telephone}
                  </div>
                  <button
                    onClick={() => handleToggleMedecin(m)}
                    title={m.disponible ? 'Marquer indisponible' : 'Marquer disponible'}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: m.disponible ? '#10B981' : '#9CA3AF' }}
                  >
                    {m.disponible ? <ToggleRight size={22} /> : <ToggleLeft size={22} />}
                  </button>
                  <span className={`sp-badge ${m.disponible ? 'available' : ''}`} style={{ fontSize: '11px', minWidth: 80, textAlign: 'center', background: m.disponible ? undefined : '#F3F4F6', color: m.disponible ? undefined : '#9CA3AF' }}>
                    {m.disponible ? 'Disponible' : 'Indisponible'}
                  </span>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <button
                      onClick={() => { setEditMedecin(m); setEditMedecinForm({ nom: m.nom, prenoms: m.prenoms, specialite: m.specialite, telephone: m.telephone, disponible: m.disponible }); }}
                      className="sp-btn sp-btn-outline sp-btn-sm"
                    >
                      <Edit2 size={14} />
                    </button>
                    <button
                      onClick={() => setDeleteMedecinModal({ id: m.medecin_id, name: `Dr. ${m.prenoms} ${m.nom}` })}
                      className="sp-btn sp-btn-ghost sp-btn-sm"
                      style={{ color: '#DC2626' }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
              {filteredMedecins.length === 0 && (
                <div style={{ padding: '40px', textAlign: 'center', background: '#fff' }}>
                  <p style={{ color: '#9CA3AF' }}>Aucun médecin trouvé</p>
                </div>
              )}
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '1px', background: '#E5E7EB' }}>
              {filteredInfirmiers.map(inf => (
                <div
                  key={inf.infirmier_id}
                  style={{ display: 'flex', alignItems: 'center', gap: '20px', padding: '20px', background: '#fff', transition: 'background 0.2s', opacity: inf.disponible ? 1 : 0.65 }}
                  onMouseEnter={e => (e.currentTarget.style.background = '#F9FAFB')}
                  onMouseLeave={e => (e.currentTarget.style.background = '#fff')}
                >
                  <div style={{ width: '56px', height: '56px', borderRadius: '12px', background: 'linear-gradient(135deg,#10B981,#059669)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '20px', fontWeight: 700, flexShrink: 0 }}>
                    {inf.nom[0]}{inf.prenoms[0]}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '16px', color: '#1F2937', marginBottom: '4px' }}>{inf.prenoms} {inf.nom}</div>
                    {inf.email && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#6B7280', fontSize: '13px' }}>
                        <Mail size={14} /> {inf.email}
                      </div>
                    )}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#6B7280', fontSize: '14px' }}>
                    <Phone size={16} /> {inf.telephone}
                  </div>
                  <button
                    onClick={() => handleToggleInfirmier(inf)}
                    title={inf.disponible ? 'Marquer indisponible' : 'Marquer disponible'}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: inf.disponible ? '#10B981' : '#9CA3AF' }}
                  >
                    {inf.disponible ? <ToggleRight size={22} /> : <ToggleLeft size={22} />}
                  </button>
                  <span className={`sp-badge ${inf.disponible ? 'available' : ''}`} style={{ fontSize: '11px', minWidth: 80, textAlign: 'center', background: inf.disponible ? undefined : '#F3F4F6', color: inf.disponible ? undefined : '#9CA3AF' }}>
                    {inf.disponible ? 'Disponible' : 'Indisponible'}
                  </span>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <button
                      onClick={() => { setEditInfirmier(inf); setEditInfirmierForm({ nom: inf.nom, prenoms: inf.prenoms, telephone: inf.telephone, email: inf.email || '', disponible: inf.disponible }); }}
                      className="sp-btn sp-btn-outline sp-btn-sm"
                    >
                      <Edit2 size={14} />
                    </button>
                    <button
                      onClick={() => setDeleteInfirmierModal({ id: inf.infirmier_id, name: `${inf.prenoms} ${inf.nom}` })}
                      className="sp-btn sp-btn-ghost sp-btn-sm"
                      style={{ color: '#DC2626' }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
              {filteredInfirmiers.length === 0 && (
                <div style={{ padding: '40px', textAlign: 'center', background: '#fff' }}>
                  <p style={{ color: '#9CA3AF' }}>Aucun infirmier trouvé</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ── Modal Créer Personnel ─────────────────────────────── */}
      {createModal && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ maxWidth: 440 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>
                {createRole === 'medecin' ? 'Nouveau médecin' : 'Nouvel infirmier'}
              </h3>
              <button onClick={() => setCreateModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}><X size={20} /></button>
            </div>
            <form onSubmit={handleCreatePersonnel}>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Rôle *</label>
                <select 
                  required 
                  value={createRole} 
                  onChange={e => {
                    const newRole = e.target.value as 'medecin' | 'infirmier';
                    setCreateRole(newRole);
                    setCreateForm(newRole === 'medecin' ? EMPTY_MEDECIN : EMPTY_INFIRMIER);
                  }} 
                  style={inputStyle}
                >
                  <option value="medecin">Médecin</option>
                  <option value="infirmier">Infirmier</option>
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Nom *</label>
                  <input required value={createForm.nom} onChange={e => setCreateForm((f: any) => ({ ...f, nom: e.target.value }))} style={inputStyle} />
                </div>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Prénoms *</label>
                  <input required value={createForm.prenoms} onChange={e => setCreateForm((f: any) => ({ ...f, prenoms: e.target.value }))} style={inputStyle} />
                </div>
              </div>

              {createRole === 'medecin' && (
                <div style={{ marginBottom: 12 }}>
                  <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Spécialité *</label>
                  <select 
                    required 
                    value={createForm.specialite} 
                    onChange={e => setCreateForm((f: any) => ({ ...f, specialite: e.target.value }))} 
                    style={inputStyle}
                  >
                    <option value="" disabled>Sélectionner une spécialité</option>
                    {SPECIALITES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
              )}

              <div style={{ marginBottom: createRole === 'infirmier' ? 12 : 20 }}>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Téléphone *</label>
                <input required value={createForm.telephone} onChange={e => setCreateForm((f: any) => ({ ...f, telephone: e.target.value }))} style={inputStyle} />
              </div>

              {createRole === 'infirmier' && (
                <div style={{ marginBottom: 20 }}>
                  <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Email (optionnel)</label>
                  <input type="email" value={createForm.email || ''} onChange={e => setCreateForm((f: any) => ({ ...f, email: e.target.value }))} style={inputStyle} />
                </div>
              )}

              {createError && <p style={{ color: '#DC2626', fontSize: 12, marginBottom: 12 }}>{createError}</p>}
              <div className="sp-modal-actions">
                <button type="button" className="sp-btn sp-btn-ghost" onClick={() => setCreateModal(false)}>Annuler</button>
                <button type="submit" className="sp-btn sp-btn-primary" disabled={createLoading}>
                  <Plus size={16} /> {createLoading ? 'Ajout...' : 'Ajouter'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Modal éditer médecin ──────────────────────────────── */}
      {editMedecin && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ maxWidth: 440 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Modifier Dr. {editMedecin.prenoms} {editMedecin.nom}</h3>
              <button onClick={() => setEditMedecin(null)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}><X size={20} /></button>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Nom</label>
                <input value={editMedecinForm.nom || ''} onChange={e => setEditMedecinForm(f => ({ ...f, nom: e.target.value }))} style={inputStyle} />
              </div>
              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Prénoms</label>
                <input value={editMedecinForm.prenoms || ''} onChange={e => setEditMedecinForm(f => ({ ...f, prenoms: e.target.value }))} style={inputStyle} />
              </div>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Spécialité</label>
              <select 
                value={editMedecinForm.specialite || ''} 
                onChange={e => setEditMedecinForm(f => ({ ...f, specialite: e.target.value }))} 
                style={inputStyle}
              >
                <option value="" disabled>Sélectionner une spécialité</option>
                {SPECIALITES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div style={{ marginBottom: 20 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Téléphone</label>
              <input value={editMedecinForm.telephone || ''} onChange={e => setEditMedecinForm(f => ({ ...f, telephone: e.target.value }))} style={inputStyle} />
            </div>
            <div className="sp-modal-actions">
              <button className="sp-btn sp-btn-ghost" onClick={() => setEditMedecin(null)}>Annuler</button>
              <button className="sp-btn sp-btn-primary" onClick={handleUpdateMedecin} disabled={editMedecinLoading}>
                {editMedecinLoading ? 'Enregistrement...' : 'Enregistrer'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Modal éditer infirmier ────────────────────────────── */}
      {editInfirmier && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ maxWidth: 440 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Modifier {editInfirmier.prenoms} {editInfirmier.nom}</h3>
              <button onClick={() => setEditInfirmier(null)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}><X size={20} /></button>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Nom</label>
                <input value={editInfirmierForm.nom || ''} onChange={e => setEditInfirmierForm(f => ({ ...f, nom: e.target.value }))} style={inputStyle} />
              </div>
              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Prénoms</label>
                <input value={editInfirmierForm.prenoms || ''} onChange={e => setEditInfirmierForm(f => ({ ...f, prenoms: e.target.value }))} style={inputStyle} />
              </div>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Téléphone</label>
              <input value={editInfirmierForm.telephone || ''} onChange={e => setEditInfirmierForm(f => ({ ...f, telephone: e.target.value }))} style={inputStyle} />
            </div>
            <div style={{ marginBottom: 20 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Email</label>
              <input type="email" value={editInfirmierForm.email || ''} onChange={e => setEditInfirmierForm(f => ({ ...f, email: e.target.value }))} style={inputStyle} />
            </div>
            <div className="sp-modal-actions">
              <button className="sp-btn sp-btn-ghost" onClick={() => setEditInfirmier(null)}>Annuler</button>
              <button className="sp-btn sp-btn-primary" onClick={handleUpdateInfirmier} disabled={editInfirmierLoading}>
                {editInfirmierLoading ? 'Enregistrement...' : 'Enregistrer'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Modal supprimer médecin ───────────────────────────── */}
      {deleteMedecinModal && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ textAlign: 'center' }}>
            <div className="sp-modal-icon"><Trash2 size={26} /></div>
            <h3>Supprimer ce médecin ?</h3>
            <p><strong>{deleteMedecinModal.name}</strong> sera définitivement supprimé.</p>
            <div className="sp-modal-actions">
              <button className="sp-btn sp-btn-ghost" onClick={() => setDeleteMedecinModal(null)}>Annuler</button>
              <button className="sp-btn sp-btn-danger" onClick={handleDeleteMedecin}><Trash2 size={16} /> Supprimer</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Modal supprimer infirmier ─────────────────────────── */}
      {deleteInfirmierModal && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ textAlign: 'center' }}>
            <div className="sp-modal-icon"><Trash2 size={26} /></div>
            <h3>Supprimer cet infirmier ?</h3>
            <p><strong>{deleteInfirmierModal.name}</strong> sera définitivement supprimé.</p>
            <div className="sp-modal-actions">
              <button className="sp-btn sp-btn-ghost" onClick={() => setDeleteInfirmierModal(null)}>Annuler</button>
              <button className="sp-btn sp-btn-danger" onClick={handleDeleteInfirmier}><Trash2 size={16} /> Supprimer</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default PersonnelMedical;
