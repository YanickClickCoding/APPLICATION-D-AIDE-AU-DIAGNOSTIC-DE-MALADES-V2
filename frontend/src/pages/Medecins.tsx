import React, { useState } from 'react';
import { getMedecins, saveMedecins } from '../db';
import type { Medecin } from '../types';
import { useAuth } from '../context/AuthContext';
import { PlusCircle, Search, Edit2, Trash2, Grid, List, Activity, Phone, Hash, UserCheck, X, User, Save, CheckCircle, AlertCircle, UserX } from 'lucide-react';

const SPECIALITES = [
  "Médecine Générale", "Cardiologie", "Pédiatrie", "Gynécologie-Obstétrique", 
  "Chirurgie Générale", "Neurologie", "Ophtalmologie", "Dermatologie", 
  "Radiologie", "Anesthésiologie", "Rhumatologie", "Urologie", "ORL", 
  "Psychiatrie", "Pneumologie", "Endocrinologie", "Infectiologie", 
  "Gastro-entérologie", "Hématologie", "Oncologie"
];

const Medecins = () => {
  const { isAdmin } = useAuth();
  const [medecins, setMedecins] = useState<Medecin[]>(() => {
    const raw = getMedecins();
    return Array.isArray(raw) ? raw.filter(m => m && m.medecin_id) : [];
  });
  const [search, setSearch] = useState('');
  const [view, setView] = useState<'grid' | 'table'>(() => (localStorage.getItem('sp_med_view') as 'grid' | 'table') || 'grid');
  
  // Modals
  const [formModalOpen, setFormModalOpen] = useState(false);
  const [formData, setFormData] = useState<Partial<Medecin>>({});
  
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [medToDelete, setMedToDelete] = useState<{id: number, name: string} | null>(null);

  const [notification, setNotification] = useState<{msg: string, type: 'success' | 'error'} | null>(null);

  const showToast = (msg: string, type: 'success' | 'error' = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const handleViewChange = (v: 'grid' | 'table') => {
    setView(v);
    localStorage.setItem('sp_med_view', v);
  };

  const filtered = medecins.filter(m => {
    if (!m) return false;
    const term = search.toLowerCase();
    return (m.nom || '').toLowerCase().includes(term) || 
           (m.prenoms || '').toLowerCase().includes(term) || 
           (m.specialite || '').toLowerCase().includes(term) ||
           (m.telephone || '').includes(term);
  });

  const toggleDisponibilite = (id: number) => {
    setMedecins(prev => {
      const updated = prev.map(m => 
        (m && m.medecin_id === id) ? { ...m, disponible: !m.disponible } : m
      );
      const isNowDisp = updated.find(m => m.medecin_id === id)?.disponible;
      saveMedecins(updated);
      showToast(`Médecin marqué comme ${isNowDisp ? 'disponible' : 'indisponible'}`);
      return updated;
    });
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    const isEditing = !!formData.medecin_id;
    setMedecins(prev => {
      let updated: Medecin[];
      if (isEditing) {
        updated = prev.map(m => m.medecin_id === formData.medecin_id ? { ...m, ...formData } as Medecin : m);
      } else {
        updated = [...prev, {
          medecin_id: Date.now(),
          nom: formData.nom || '',
          prenoms: formData.prenoms || '',
          specialite: formData.specialite || '',
          telephone: formData.telephone || '',
          disponible: formData.disponible ?? true,
          created_at: new Date().toISOString()
        }];
      }
      saveMedecins(updated);
      showToast(isEditing ? 'Informations du médecin mises à jour' : 'Nouveau médecin ajouté avec succès');
      return updated;
    });
    setFormModalOpen(false);
  };

  const handleDelete = () => {
    if (!medToDelete) return;
    setMedecins(prev => {
      const updated = prev.filter(m => m && m.medecin_id !== medToDelete.id);
      saveMedecins(updated);
      showToast('Médecin retiré du système');
      return updated;
    });
    setDeleteModalOpen(false);
  };

  const openForm = (med?: Medecin) => {
    setFormData(med || { disponible: true });
    setFormModalOpen(true);
  };

  return (
    <div>
      {/* Toast Notification */}
      {notification && (
        <div id="flash-msg" className={`sp-alert ${notification.type}`} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', minWidth: '350px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <CheckCircle size={20} />
            <span style={{ fontWeight: 500 }}>{notification.msg}</span>
          </div>
          <X size={16} style={{ cursor: 'pointer', opacity: 0.6 }} onClick={() => setNotification(null)} />
        </div>
      )}

      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Médecins</h1>
          <p className="sp-page-subtitle">{filtered.length} médecin(s) enregistré(s)</p>
        </div>
        {isAdmin && (
          <button onClick={() => openForm()} className="sp-btn sp-btn-primary">
            <PlusCircle size={18} /> Ajouter un médecin
          </button>
        )}
      </div>

      <div className="sp-card sp-fade-in">
        <div className="sp-card-header">
          <div className="sp-card-title">
            <UserCheck size={20} /> Liste des médecins
          </div>
          <div className="sp-toolbar">
              <div className="sp-search-box">
                <Search size={18} />
                <input 
                  type="text" 
                  placeholder="Rechercher nom, spécialité..." 
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
                {search && <X size={14} style={{cursor:'pointer'}} onClick={() => setSearch('')} />}
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

        {/* VUE CARTE */}
        {view === 'grid' && (
          <div id="view-grid" style={{padding:'20px'}}>
            {filtered.length === 0 ? (
              <div className="sp-empty">
                <UserX size={48} style={{margin:'0 auto 1rem', opacity:0.3}} />
                <div className="sp-empty-title">Aucun médecin trouvé</div>
              </div>
            ) : (
              <div className="sp-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
                {filtered.map(m => {
                  const initiales = ((m.prenoms || '?').substring(0, 1) + (m.nom || '?').substring(0, 1)).toUpperCase();
                  const dispo = m.disponible;
                  return (
                    <div className="sp-item-card" key={m.medecin_id} style={{ padding: '24px', position: 'relative', minHeight: '320px', display: 'flex', flexDirection: 'column' }}>
                      <div className="sp-item-card-header" style={{ marginBottom: '18px', display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
                        <div className="sp-item-avatar" style={{ width: '54px', height: '54px', fontSize: '20px', borderRadius: '14px', flexShrink: 0, background: dispo ? '' : 'linear-gradient(135deg,#94a3b8,#64748b)' }}>
                          {initiales}
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div className="sp-item-name" style={{ fontSize: '18px', fontWeight: 700, lineHeight: '1.3', marginBottom: '8px', color: '#001b3d' }}>
                            Dr. {m.prenoms}<br />{m.nom}
                          </div>
                          <div className="sp-item-meta" style={{ fontSize: '13px', display: 'flex', gap: '6px', alignItems: 'flex-start', color: '#64748b' }}>
                            <Activity size={14} style={{ marginTop: '3px' }} />
                            <span>{m.specialite}</span>
                          </div>
                        </div>
                        <span className={`sp-badge ${dispo ? 'available' : 'unavailable'}`} style={{ fontSize: '11px', padding: '4px 12px', borderRadius: '20px' }}>
                          <span>{dispo ? 'Disponible' : 'Indisponible'}</span>
                        </span>
                      </div>

                      <div className="sp-item-details" style={{ gap: '14px', marginBottom: '20px', flex: 1, paddingLeft: '4px' }}>
                        <div className="sp-item-detail-row" style={{ fontSize: '14px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                          <Phone size={15} style={{ color: '#94a3b8' }} />
                          <span style={{ color: '#475569' }}>{m.telephone}</span>
                        </div>
                        <div className="sp-item-detail-row" style={{ fontSize: '14px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                          <Hash size={15} style={{ color: '#94a3b8' }} />
                          <span style={{ color: '#475569' }}>ID #{String(m.medecin_id).padStart(4, '0')}</span>
                        </div>
                      </div>

                      <div className="sp-item-actions" style={{ paddingTop: '16px', borderTop: '1px solid var(--sp-gray-100)', display: 'flex', gap: '10px', alignItems: 'center' }}>
                        <button onClick={() => openForm(m)} className="sp-btn sp-btn-outline sp-btn-sm" style={{ padding: '8px 16px', fontSize: '13px', height: '40px', borderRadius: '10px', flex: 1, fontWeight: 600 }}>
                            <Edit2 size={16} /> Modifier
                        </button>
                        <button 
                            onClick={() => toggleDisponibilite(m.medecin_id)}
                            className={`sp-btn sp-btn-sm ${dispo ? 'sp-btn-warning' : 'sp-btn-success'}`}
                            style={{ padding: '8px 16px', fontSize: '13px', height: '40px', borderRadius: '10px', flex: 1.5, fontWeight: 600, background: dispo ? '#f59e0b' : '#10b981' }}
                        >
                            <span style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
                              {dispo ? <AlertCircle size={16} key="off" /> : <UserCheck size={16} key="on" />}
                              <span>{dispo ? 'Désactiver' : 'Activer'}</span>
                            </span>
                        </button>
                        <button 
                          className="sp-btn sp-btn-ghost sp-btn-sm" 
                          style={{ color: '#ef4444', padding: '8px', marginLeft: '8px' }}
                          onClick={() => { setMedToDelete({ id: m.medecin_id, name: `Dr. ${m.prenoms} ${m.nom}` }); setDeleteModalOpen(true); }}
                        >
                          <Trash2 size={18} />
                        </button>
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
          <div id="view-table">
            <div className="sp-table-wrap">
              <table className="sp-table">
                <thead>
                  <tr>
                    <th>#ID</th>
                    <th>Médecin</th>
                    <th>Spécialité</th>
                    <th>Téléphone</th>
                    <th>Disponibilité</th>
                    {isAdmin && <th>Actions</th>}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(m => (
                    <tr key={m.medecin_id}>
                      <td style={{ color: 'var(--sp-gray-400)', fontSize: '12px' }}>#{String(m.medecin_id).padStart(4, '0')}</td>
                      <td>
                        <div style={{ fontWeight: 600 }}>Dr. {m.prenoms} {m.nom}</div>
                      </td>
                      <td>{m.specialite}</td>
                      <td>{m.telephone}</td>
                      <td>
                        <span className={`sp-badge ${m.disponible ? 'available' : 'unavailable'}`}>
                          <span>{m.disponible ? 'Disponible' : 'Indisponible'}</span>
                        </span>
                      </td>
                      {isAdmin && (
                        <td>
                          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                            <button onClick={() => openForm(m)} className="sp-btn sp-btn-outline sp-btn-sm">
                              <Edit2 size={14} />
                            </button>
                            <button 
                              onClick={() => toggleDisponibilite(m.medecin_id)}
                              className={`sp-btn sp-btn-sm ${m.disponible ? 'sp-btn-warning' : 'sp-btn-success'}`}
                            >
                              <span style={{ display: 'flex', alignItems: 'center' }}>
                                {m.disponible ? <AlertCircle size={14} key="tab-off" /> : <UserCheck size={14} key="tab-on" />}
                              </span>
                            </button>
                            <button 
                              className="sp-btn sp-btn-ghost sp-btn-sm" 
                              style={{ color: 'var(--sp-danger)' }}
                              onClick={() => { setMedToDelete({ id: m.medecin_id, name: `Dr. ${m.prenoms} ${m.nom}` }); setDeleteModalOpen(true); }}
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                  {filtered.length === 0 && (
                    <tr>
                      <td colSpan={isAdmin ? 6 : 5} className="sp-no-results">Aucun médecin trouvé.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Form Modal */}
      {formModalOpen && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ maxWidth: '650px', padding: 0, overflow: 'hidden' }}>
            <div className="sp-card-header" style={{ padding: '24px 32px', borderBottom: '1px solid var(--sp-gray-100)' }}>
              <div className="sp-card-title" style={{ fontSize: '18px' }}>
                {formData.medecin_id ? <Edit2 size={22} style={{ color: 'var(--sp-primary)' }} /> : <PlusCircle size={22} style={{ color: 'var(--sp-primary)' }} />}
                {formData.medecin_id ? 'Modifier les informations' : 'Ajouter un médecin'}
              </div>
            </div>
            <form onSubmit={handleSave} style={{ padding: '32px' }}>
              <div className="sp-form-grid" style={{ marginBottom: '24px' }}>
                <div className="sp-form-group">
                  <label className="sp-form-label">Nom <span className="required">*</span></label>
                  <div className="sp-input-group">
                    <User size={18} />
                    <input 
                      type="text" 
                      className="sp-form-input" 
                      required 
                      value={formData.nom || ''} 
                      onChange={e => setFormData({...formData, nom: e.target.value})} 
                      placeholder="Nom de famille"
                    />
                  </div>
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">Prénom(s) <span className="required">*</span></label>
                  <div className="sp-input-group">
                    <User size={18} />
                    <input 
                      type="text" 
                      className="sp-form-input" 
                      required 
                      value={formData.prenoms || ''} 
                      onChange={e => setFormData({...formData, prenoms: e.target.value})} 
                      placeholder="Prénoms"
                    />
                  </div>
                </div>
              </div>

              <div className="sp-form-grid" style={{ marginBottom: '24px' }}>
                <div className="sp-form-group">
                  <label className="sp-form-label">Spécialité <span className="required">*</span></label>
                  <div className="sp-input-group">
                    <Activity size={18} />
                    <select 
                      className="sp-form-select" 
                      required 
                      value={formData.specialite || ''} 
                      onChange={e => setFormData({...formData, specialite: e.target.value})}
                    >
                      <option value="" disabled>Sélectionner une spécialité</option>
                      {SPECIALITES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">Téléphone <span className="required">*</span></label>
                  <div className="sp-input-group">
                    <Phone size={18} />
                    <input 
                      type="text" 
                      className="sp-form-input" 
                      required 
                      value={formData.telephone || ''} 
                      onChange={e => setFormData({...formData, telephone: e.target.value})} 
                      placeholder="+229 00 00 00 00"
                    />
                  </div>
                </div>
              </div>

              <div className="sp-form-group" style={{ marginBottom: '32px' }}>
                <label className="sp-form-label">Disponibilité</label>
                <div className="sp-radio-group">
                  <label className="sp-radio-item available">
                    <input 
                      type="radio" 
                      name="disponible" 
                      checked={formData.disponible === true} 
                      onChange={() => setFormData({...formData, disponible: true})} 
                    />
                    <span className="sp-badge available">
                      <CheckCircle size={14} /> Disponible
                    </span>
                  </label>
                  <label className="sp-radio-item unavailable">
                    <input 
                      type="radio" 
                      name="disponible" 
                      checked={formData.disponible === false} 
                      onChange={() => setFormData({...formData, disponible: false})} 
                    />
                    <span className="sp-badge unavailable">
                      <AlertCircle size={14} /> Indisponible
                    </span>
                  </label>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center', marginTop: '40px' }}>
                <button type="submit" className="sp-btn sp-btn-primary" style={{ padding: '12px 24px', borderRadius: '12px' }}>
                  <Save size={18} /> Enregistrer les modifications
                </button>
                <button type="button" className="sp-btn sp-btn-ghost" onClick={() => setFormModalOpen(false)} style={{ fontWeight: 500 }}>
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Modal */}
      {deleteModalOpen && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ textAlign: 'center' }}>
            <div className="sp-modal-icon">
              <Trash2 size={26} />
            </div>
            <h3>Supprimer ce médecin ?</h3>
            <p>Le médecin <strong>{medToDelete?.name}</strong> sera définitivement retiré du système.</p>
            <div className="sp-modal-actions">
              <button className="sp-btn sp-btn-ghost" onClick={() => setDeleteModalOpen(false)}>Annuler</button>
              <button className="sp-btn sp-btn-danger" onClick={handleDelete}><Trash2 size={16} /> Supprimer</button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default Medecins;
