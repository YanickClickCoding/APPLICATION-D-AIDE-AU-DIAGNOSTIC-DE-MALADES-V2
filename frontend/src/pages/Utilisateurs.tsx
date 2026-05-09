import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { adminAPI, type AdminUser, type AdminUserCreate } from '../services/api';
import {
  Users, Search, Trash2, Shield, User, Grid, List,
  Mail, Calendar, Lock, X, Plus, Edit2, ToggleLeft, ToggleRight,
} from 'lucide-react';

const EMPTY_CREATE: AdminUserCreate = { nom: '', prenoms: '', email: '', password: '', role: 'medecin', specialite: '', telephone: '' };

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

const Utilisateurs = () => {
  const { user: currentUser, token, isLoading: authLoading } = useAuth();
  const [utilisateurs, setUtilisateurs] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [view, setView] = useState<'grid' | 'table'>(
    () => (localStorage.getItem('sp_usr_view') as 'grid' | 'table') || 'grid'
  );

  // Modals
  const [deleteModal, setDeleteModal] = useState<{ id: number; name: string } | null>(null);
  const [createModal, setCreateModal] = useState(false);
  const [editModal, setEditModal] = useState<AdminUser | null>(null);

  // Create form
  const [createForm, setCreateForm] = useState<AdminUserCreate>(EMPTY_CREATE);
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState('');

  // Edit form
  const [editRole, setEditRole] = useState<'admin' | 'medecin' | 'infirmier'>('medecin');
  const [editLoading, setEditLoading] = useState(false);

  const loadUsers = useCallback(async () => {
    if (!token) return;
    try {
      setLoading(true);
      const users = await adminAPI.getUsers(token);
      setUtilisateurs(users);
      setError(null);
    } catch (e: any) {
      setError(e.detail || 'Erreur lors du chargement des utilisateurs');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { if (!authLoading) loadUsers(); }, [loadUsers, authLoading]);

  const handleViewChange = (v: 'grid' | 'table') => {
    setView(v);
    localStorage.setItem('sp_usr_view', v);
  };

  const filtered = utilisateurs.filter(u => {
    const term = search.toLowerCase();
    return (
      (u.nom || '').toLowerCase().includes(term) ||
      (u.prenoms || '').toLowerCase().includes(term) ||
      (u.email || '').toLowerCase().includes(term)
    );
  });

  const handleDelete = async () => {
    if (!deleteModal || !token) return;
    try {
      await adminAPI.deleteUser(token, deleteModal.id);
      setUtilisateurs(prev => prev.filter(u => u.utilisateur_id !== deleteModal.id));
      setDeleteModal(null);
    } catch (e: any) {
      alert(e.detail || 'Erreur lors de la suppression');
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setCreateLoading(true);
    setCreateError('');
    try {
      const newUser = await adminAPI.createUser(token, createForm);
      setUtilisateurs(prev => [...prev, newUser]);
      setCreateModal(false);
      setCreateForm(EMPTY_CREATE);
    } catch (e: any) {
      setCreateError(e.detail || 'Erreur lors de la création');
    } finally {
      setCreateLoading(false);
    }
  };

  const handleEditSave = async () => {
    if (!editModal || !token) return;
    setEditLoading(true);
    try {
      const updated = await adminAPI.updateUser(token, editModal.utilisateur_id, { role: editRole });
      setUtilisateurs(prev => prev.map(u => u.utilisateur_id === updated.utilisateur_id ? updated : u));
      setEditModal(null);
    } catch (e: any) {
      alert(e.detail || 'Erreur lors de la mise à jour');
    } finally {
      setEditLoading(false);
    }
  };

  const handleToggleActif = async (u: AdminUser) => {
    if (!token) return;
    try {
      const updated = await adminAPI.updateUser(token, u.utilisateur_id, { actif: !u.actif });
      setUtilisateurs(prev => prev.map(x => x.utilisateur_id === updated.utilisateur_id ? updated : x));
    } catch (e: any) {
      alert(e.detail || 'Erreur');
    }
  };

  const getRoleLabel = (role: string) => {
    if (role === 'admin') return 'Administrateur';
    if (role === 'medecin') return 'Médecin';
    if (role === 'infirmier') return 'Infirmier';
    return role;
  };

  const inputStyle: React.CSSProperties = {
    width: '100%', padding: '8px 10px', border: '1px solid #D1D5DB',
    borderRadius: 6, fontSize: 13, boxSizing: 'border-box',
  };

  return (
    <div>
      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Utilisateurs</h1>
          <p className="sp-page-subtitle">{filtered.length} compte(s) enregistré(s)</p>
        </div>
        <button className="sp-btn sp-btn-primary" onClick={() => setCreateModal(true)}>
          <Plus size={18} /> Nouvel utilisateur
        </button>
      </div>

      {error && (
        <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 8, padding: '12px 16px', marginBottom: 16, color: '#991B1B', fontSize: 13 }}>
          {error}
        </div>
      )}

      <div className="sp-card sp-fade-in">
        <div className="sp-card-header">
          <div className="sp-card-title">
            <Users size={20} /> Gestion des comptes
          </div>
          <div className="sp-toolbar">
            <div className="sp-search-box">
              <Search size={18} />
              <input
                type="text"
                placeholder="Rechercher nom, email..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
              {search && <X size={14} style={{ cursor: 'pointer' }} onClick={() => setSearch('')} />}
            </div>
            <div className="sp-view-toggle">
              <button className={`sp-view-btn ${view === 'grid' ? 'active' : ''}`} onClick={() => handleViewChange('grid')} title="Vue cartes">
                <Grid size={18} />
              </button>
              <button className={`sp-view-btn ${view === 'table' ? 'active' : ''}`} onClick={() => handleViewChange('table')} title="Vue tableau">
                <List size={18} />
              </button>
            </div>
          </div>
        </div>

        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#9CA3AF' }}>Chargement...</div>
        ) : (
          <>
            {/* VUE CARTE */}
            {view === 'grid' && (
              <div style={{ padding: '20px' }}>
                {filtered.length === 0 ? (
                  <div className="sp-empty">
                    <Users size={48} style={{ margin: '0 auto 1rem', opacity: 0.3 }} />
                    <div className="sp-empty-title">Aucun utilisateur trouvé</div>
                  </div>
                ) : (
                  <div className="sp-grid" style={{ gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }}>
                    {filtered.map(u => {
                      const initiales = ((u.prenoms || '?')[0] + (u.nom || '?')[0]).toUpperCase();
                      const isAdminRole = u.role === 'admin';
                      const isCurrentUser = u.utilisateur_id === currentUser?.utilisateur_id;
                      return (
                        <div className="sp-item-card" key={u.utilisateur_id} style={{ padding: '16px', position: 'relative', opacity: u.actif ? 1 : 0.6 }}>
                          <div className="sp-item-card-header" style={{ marginBottom: '12px', display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                            <div className="sp-item-avatar" style={{ width: '38px', height: '38px', fontSize: '13px', borderRadius: '8px', flexShrink: 0, background: isAdminRole ? 'linear-gradient(135deg, #0A4B8C, #00B4D8)' : 'linear-gradient(135deg, #7C3AED, #A78BFA)' }}>
                              {initiales}
                            </div>
                            <div style={{ flex: 1, minWidth: 0 }}>
                              <div className="sp-item-name" style={{ fontSize: '14px', fontWeight: 700, marginBottom: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {u.prenoms} {u.nom}
                                {isCurrentUser && <span style={{ fontSize: '9px', background: '#dbeafe', color: 'var(--sp-primary)', padding: '1px 5px', borderRadius: '4px', fontWeight: 600, marginLeft: '4px' }}>Vous</span>}
                              </div>
                              <div className="sp-item-meta" style={{ fontSize: '10.5px' }}>
                                <Mail size={11} />
                                <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', display: 'block' }}>{u.email}</span>
                              </div>
                            </div>
                            <span className={`sp-role-badge ${isAdminRole ? 'admin' : 'operator'}`} style={{ fontSize: '9px', position: 'absolute', top: '16px', right: '16px' }}>
                              {getRoleLabel(u.role)}
                            </span>
                          </div>

                          <div className="sp-item-details" style={{ gap: '6px', marginBottom: '14px' }}>
                            <div className="sp-item-detail-row" style={{ fontSize: '11.5px' }}>
                              <Calendar size={12} style={{ color: 'var(--sp-gray-400)' }} />
                              <span>Inscrit le {new Date(u.created_at).toLocaleDateString('fr-FR')}</span>
                            </div>
                            <div className="sp-item-detail-row" style={{ fontSize: '11.5px' }}>
                              <Shield size={12} style={{ color: 'var(--sp-gray-400)' }} />
                              <span style={{ color: u.actif ? '#059669' : '#DC2626', fontWeight: 600 }}>{u.actif ? 'Actif' : 'Inactif'}</span>
                            </div>
                          </div>

                          <div className="sp-item-actions" style={{ paddingTop: '14px', borderTop: '1px solid var(--sp-gray-100)', display: 'flex', gap: '8px', alignItems: 'center' }}>
                            {!isCurrentUser ? (
                              <>
                                <button
                                  onClick={() => { setEditModal(u); setEditRole(u.role); }}
                                  className="sp-btn sp-btn-outline sp-btn-sm"
                                  style={{ padding: '6px 10px', fontSize: '12px', height: '32px' }}
                                >
                                  <Edit2 size={13} /> Rôle
                                </button>
                                <button
                                  onClick={() => handleToggleActif(u)}
                                  className="sp-btn sp-btn-ghost sp-btn-sm"
                                  title={u.actif ? 'Désactiver' : 'Activer'}
                                  style={{ padding: '6px', color: u.actif ? '#F59E0B' : '#10B981' }}
                                >
                                  {u.actif ? <ToggleRight size={16} /> : <ToggleLeft size={16} />}
                                </button>
                                <button
                                  className="sp-btn sp-btn-ghost sp-btn-sm"
                                  style={{ color: 'var(--sp-danger)', padding: '6px', marginLeft: 'auto' }}
                                  onClick={() => setDeleteModal({ id: u.utilisateur_id, name: `${u.prenoms} ${u.nom}` })}
                                >
                                  <Trash2 size={14} />
                                </button>
                              </>
                            ) : (
                              <div style={{ padding: '4px 0', fontSize: '12px', color: 'var(--sp-gray-400)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <Lock size={12} /> Compte courant
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* VUE TABLEAU */}
            {view === 'table' && (
              <div className="sp-table-wrap">
                <table className="sp-table">
                  <thead>
                    <tr>
                      <th>#ID</th>
                      <th>Utilisateur</th>
                      <th>Email</th>
                      <th>Rôle</th>
                      <th>Statut</th>
                      <th>Date inscription</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map(u => {
                      const isAdminRole = u.role === 'admin';
                      const isCurrentUser = u.utilisateur_id === currentUser?.utilisateur_id;
                      return (
                        <tr key={u.utilisateur_id} style={{ opacity: u.actif ? 1 : 0.6 }}>
                          <td style={{ color: 'var(--sp-gray-400)', fontSize: '12px' }}>#{String(u.utilisateur_id).padStart(4, '0')}</td>
                          <td>
                            <div style={{ fontWeight: 600 }}>
                              {u.prenoms} {u.nom}
                              {isCurrentUser && <span style={{ fontSize: '10px', background: '#dbeafe', color: 'var(--sp-primary)', padding: '2px 7px', borderRadius: '10px', fontWeight: 600, marginLeft: '4px' }}>Vous</span>}
                            </div>
                          </td>
                          <td style={{ color: 'var(--sp-gray-500)' }}>{u.email}</td>
                          <td>
                            <span className={`sp-role-badge ${isAdminRole ? 'admin' : 'operator'}`} style={{ fontSize: '10.5px' }}>
                              {getRoleLabel(u.role)}
                            </span>
                          </td>
                          <td>
                            <span style={{ fontSize: 12, fontWeight: 600, color: u.actif ? '#059669' : '#DC2626' }}>
                              {u.actif ? 'Actif' : 'Inactif'}
                            </span>
                          </td>
                          <td>{new Date(u.created_at).toLocaleDateString('fr-FR')}</td>
                          <td>
                            {!isCurrentUser ? (
                              <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                                <button
                                  onClick={() => { setEditModal(u); setEditRole(u.role); }}
                                  className="sp-btn sp-btn-outline sp-btn-sm"
                                  title="Modifier le rôle"
                                >
                                  <Edit2 size={14} />
                                </button>
                                <button
                                  onClick={() => handleToggleActif(u)}
                                  className="sp-btn sp-btn-ghost sp-btn-sm"
                                  title={u.actif ? 'Désactiver' : 'Activer'}
                                  style={{ color: u.actif ? '#F59E0B' : '#10B981' }}
                                >
                                  {u.actif ? <ToggleRight size={14} /> : <ToggleLeft size={14} />}
                                </button>
                                <button
                                  className="sp-btn sp-btn-ghost sp-btn-sm"
                                  style={{ color: 'var(--sp-danger)' }}
                                  onClick={() => setDeleteModal({ id: u.utilisateur_id, name: `${u.prenoms} ${u.nom}` })}
                                >
                                  <Trash2 size={14} />
                                </button>
                              </div>
                            ) : (
                              <span style={{ fontSize: '11.5px', color: 'var(--sp-gray-300)' }}>—</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                    {filtered.length === 0 && (
                      <tr>
                        <td colSpan={7} className="sp-no-results">Aucun utilisateur trouvé.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>

      {/* ── Modal Créer utilisateur ─────────────────────────────── */}
      {createModal && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ maxWidth: 460 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Nouvel utilisateur</h3>
              <button onClick={() => { setCreateModal(false); setCreateForm(EMPTY_CREATE); setCreateError(''); }} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4 }}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleCreate}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Nom *</label>
                  <input required value={createForm.nom} onChange={e => setCreateForm(f => ({ ...f, nom: e.target.value }))} style={inputStyle} />
                </div>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Prénoms *</label>
                  <input required value={createForm.prenoms} onChange={e => setCreateForm(f => ({ ...f, prenoms: e.target.value }))} style={inputStyle} />
                </div>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Email *</label>
                <input type="email" required value={createForm.email} onChange={e => setCreateForm(f => ({ ...f, email: e.target.value }))} style={inputStyle} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Mot de passe * (min. 6 caractères)</label>
                <input type="password" required minLength={6} value={createForm.password} onChange={e => setCreateForm(f => ({ ...f, password: e.target.value }))} style={inputStyle} />
              </div>
              <div style={{ marginBottom: createForm.role === 'medecin' ? 12 : 20 }}>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Rôle *</label>
                <select value={createForm.role} onChange={e => setCreateForm(f => ({ ...f, role: e.target.value as any }))} style={inputStyle}>
                  <option value="medecin">Médecin</option>
                  <option value="infirmier">Infirmier</option>
                  <option value="admin">Administrateur</option>
                </select>
              </div>

              {createForm.role === 'medecin' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 20 }}>
                  <div>
                    <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Spécialité *</label>
                    <select 
                      required 
                      value={createForm.specialite} 
                      onChange={e => setCreateForm(f => ({ ...f, specialite: e.target.value }))} 
                      style={inputStyle}
                    >
                      <option value="" disabled>Sélectionner</option>
                      {SPECIALITES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                  <div>
                    <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Téléphone *</label>
                    <input 
                      required 
                      placeholder="+229..."
                      value={createForm.telephone} 
                      onChange={e => setCreateForm(f => ({ ...f, telephone: e.target.value }))} 
                      style={inputStyle} 
                    />
                  </div>
                </div>
              )}
              {createError && <p style={{ color: '#DC2626', fontSize: 12, marginBottom: 12 }}>{createError}</p>}
              <div className="sp-modal-actions">
                <button type="button" className="sp-btn sp-btn-ghost" onClick={() => { setCreateModal(false); setCreateForm(EMPTY_CREATE); setCreateError(''); }}>Annuler</button>
                <button type="submit" className="sp-btn sp-btn-primary" disabled={createLoading}>
                  <Plus size={16} /> {createLoading ? 'Création...' : 'Créer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Modal Modifier rôle ─────────────────────────────────── */}
      {editModal && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ maxWidth: 360 }}>
            <h3 style={{ margin: '0 0 16px', fontSize: 18, fontWeight: 700 }}>
              Modifier : {editModal.prenoms} {editModal.nom}
            </h3>
            <div style={{ marginBottom: 20 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Rôle</label>
              <select value={editRole} onChange={e => setEditRole(e.target.value as any)} style={inputStyle}>
                <option value="medecin">Médecin</option>
                <option value="infirmier">Infirmier</option>
                <option value="admin">Administrateur</option>
              </select>
            </div>
            <div className="sp-modal-actions">
              <button className="sp-btn sp-btn-ghost" onClick={() => setEditModal(null)}>Annuler</button>
              <button className="sp-btn sp-btn-primary" onClick={handleEditSave} disabled={editLoading}>
                <User size={16} /> {editLoading ? 'Enregistrement...' : 'Enregistrer'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Modal Supprimer ─────────────────────────────────────── */}
      {deleteModal && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ textAlign: 'center' }}>
            <div className="sp-modal-icon"><Trash2 size={26} /></div>
            <h3>Supprimer cet utilisateur ?</h3>
            <p>Le compte de <strong>{deleteModal.name}</strong> sera définitivement supprimé. Cette action est irréversible.</p>
            <div className="sp-modal-actions">
              <button className="sp-btn sp-btn-ghost" onClick={() => setDeleteModal(null)}>Annuler</button>
              <button className="sp-btn sp-btn-danger" onClick={handleDelete}><Trash2 size={16} /> Supprimer</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Utilisateurs;
