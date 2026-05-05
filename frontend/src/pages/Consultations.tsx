import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analyticsAPI } from '../services/api';
import type { Consultation } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Search, Grid, List, PlusCircle, Calendar, FileText, UserCheck, Play, Check, Edit2, Trash2, UserPlus, AlertTriangle, User, Save, Clipboard, X, Activity } from 'lucide-react';

interface Medecin {
  medecin_id: number;
  nom: string;
  prenoms: string;
  specialite: string;
  telephone: string;
  disponible: boolean;
}

const Consultations = () => {
  const { isAdmin } = useAuth();
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [medecins, setMedecins] = useState<Medecin[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [view, setView] = useState<'grid' | 'table'>(() => (localStorage.getItem('sp_cons_view') as 'grid' | 'table') || 'grid');
  
  // Modal states
  const [affectModalOpen, setAffectModalOpen] = useState(false);
  const [currentConsultId, setCurrentConsultId] = useState<number | null>(null);
  const [selectedMedecinId, setSelectedMedecinId] = useState('');
  
  const [warningModalOpen, setWarningModalOpen] = useState(false);
  
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [consultToDelete, setConsultToDelete] = useState<{id: number, name: string} | null>(null);

  // Form Modal state
  const [formModalOpen, setFormModalOpen] = useState(false);
  const [formData, setFormData] = useState<Partial<Consultation>>({});

  // Charger les données depuis le backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [consultationsData, personnelData] = await Promise.all([
          analyticsAPI.getRecentConsultations(100), // Charger toutes les consultations
          analyticsAPI.getPersonnelDisponible()
        ]);
        setConsultations(consultationsData);
        setMedecins(personnelData.medecins.liste as any);
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getMedecinName = (id: number | null | undefined) => {
    if (!id) return null;
    const m = medecins.find(med => med && med.medecin_id === id);
    return m ? `Dr. ${m.prenoms} ${m.nom}` : null;
  };

  const handleViewChange = (v: 'grid' | 'table') => {
    setView(v);
    localStorage.setItem('sp_cons_view', v);
  };

  const filteredConsultations = consultations.filter(c => {
    if (!c) return false;
    const term = search.toLowerCase();
    const medName = (getMedecinName(c.medecin_id) || '').toLowerCase();
    const nomPatient = (c.nom_patient || '').toLowerCase();
    const motif = (c.motif || '').toLowerCase();
    
    return nomPatient.includes(term) || 
           motif.includes(term) ||
           medName.includes(term);
  }).sort((a, b) => {
    const statusOrder: Record<string, number> = { 'en attente': 1, 'en cours': 2, 'terminée': 3 };
    const orderA = statusOrder[a.statut] || 99;
    const orderB = statusOrder[b.statut] || 99;
    
    if (orderA !== orderB) {
      return orderA - orderB;
    }
    const dateA = new Date(a.date_heure || 0).getTime();
    const dateB = new Date(b.date_heure || 0).getTime();
    return dateA - dateB;
  });

  const availableMedecins = medecins.filter(m => m.disponible);

  const handleAffecter = (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentConsultId || !selectedMedecinId) return;
    
    // TODO: Appeler l'API backend pour affecter le médecin
    const updated = consultations.map(c => {
      if (c.id === currentConsultId) {
        return { ...c, medecin_id: Number(selectedMedecinId) };
      }
      return c;
    });
    
    setConsultations(updated);
    setAffectModalOpen(false);
  };

  const handleStatutChange = (id: number, newStatut: 'en cours' | 'terminée') => {
    // TODO: Appeler l'API backend pour changer le statut
    const updated = consultations.map(c => {
      if (c.id === id) {
        return { ...c, statut: newStatut };
      }
      return c;
    });
    setConsultations(updated);
  };

  const handleDelete = () => {
    if (!consultToDelete) return;
    // TODO: Appeler l'API backend pour supprimer
    const updated = consultations.filter(c => c.id !== consultToDelete.id);
    setConsultations(updated);
    setDeleteModalOpen(false);
  };

  const handleSaveConsultation = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Appeler l'API backend pour sauvegarder
    alert('Fonctionnalité à implémenter avec le backend');
    setFormModalOpen(false);
  };

  const openForm = (consult?: Consultation) => {
    if (consult) {
      setFormData(consult);
    } else {
      setFormData({
        statut: 'en attente',
        date_heure: new Date().toISOString().slice(0, 16)
      });
    }
    setFormModalOpen(true);
  };

  return (
    <>
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
          <div style={{ textAlign: 'center' }}>
            <Activity size={48} style={{ animation: 'spin 1s linear infinite', color: '#4F46E5' }} />
            <p style={{ marginTop: '16px', color: '#6B7280' }}>Chargement des consultations...</p>
          </div>
        </div>
      ) : (
        <>
      <div className="sp-page-header sp-fade-in">
          <div>
              <h1 className="sp-page-title">Consultations</h1>
              <p className="sp-page-subtitle">{filteredConsultations.length} consultation(s) trouvée(s)</p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button onClick={() => openForm()} className="sp-btn sp-btn-outline">
                <PlusCircle size={18} />
                <span>Consultation rapide</span>
            </button>
            <Link to="/consultation/nouvelle" className="sp-btn sp-btn-primary">
                <PlusCircle size={18} />
                <span>Nouvelle consultation complète</span>
            </Link>
          </div>
      </div>

      <div className="sp-card sp-fade-in">
          <div className="sp-card-header">
              <div className="sp-card-title">
                  <List size={20} />
                  <span>Liste des consultations</span>
              </div>
              <div className="sp-toolbar">
                  <div className="sp-search-box">
                      <Search size={18} />
                      <input 
                        type="text" 
                        placeholder="Rechercher patient, motif, médecin..." 
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
                {filteredConsultations.length === 0 ? (
                  <div className="sp-empty">
                      <FileText size={64} style={{margin:'0 auto 1rem', color:'var(--sp-gray-300)'}} />
                      <div className="sp-empty-title">Aucune consultation trouvée</div>
                      <div className="sp-empty-text">
                          {search ? `Aucun résultat pour « ${search} »` : "Commencez par ajouter une consultation."}
                      </div>
                  </div>
                ) : (
                  <div className="sp-grid" id="cards-container" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px', width: '100%' }}>
                      {filteredConsultations.map(c => {
                          const mName = getMedecinName(c.medecin_id);
                          const sc: Record<string, string> = { 'en attente': 'attente', 'en cours': 'cours', 'terminée': 'terminee' };
                          const cls = sc[c.statut] || 'attente';
                          const initiales = (c.nom_patient || '??').substring(0, 2).toUpperCase();

                          return (
                            <div className="sp-item-card" key={c.id} style={{ padding: '24px', position: 'relative', minHeight: '280px', display: 'flex', flexDirection: 'column' }}>
                                <div className="sp-item-card-header" style={{ marginBottom: '16px', display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
                                    <div className="sp-item-avatar" style={{ width: '48px', height: '48px', fontSize: '18px', borderRadius: '12px', flexShrink: 0 }}>
                                        {initiales}
                                    </div>
                                    <div style={{ flex: 1, minWidth: 0, paddingTop: '2px' }}>
                                        <div className="sp-item-name" style={{ fontSize: '16px', fontWeight: 700, marginBottom: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.nom_patient}</div>
                                        <span className={`sp-badge ${cls}`} style={{ fontSize: '11px', padding: '3px 10px', borderRadius: '20px' }}>{c.statut}</span>
                                    </div>
                                    <div style={{ fontSize: '11px', color: 'var(--sp-gray-400)', position: 'absolute', top: '24px', right: '24px', fontWeight: 400, opacity: 0.8 }}>
                                        #{String(c.id).length > 6 ? '...' + String(c.id).slice(-4) : String(c.id).padStart(4, '0')}
                                    </div>
                                </div>

                                <div className="sp-item-details" style={{ gap: '12px', marginBottom: '20px', flex: 1 }}>
                                    <div className="sp-item-detail-row" style={{ fontSize: '13px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                                        <Calendar size={15} style={{ color: 'var(--sp-gray-400)' }} />
                                        <span style={{ color: 'var(--sp-gray-700)' }}>{new Date(c.date_heure || c.date).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }).replace(',', ' à')}</span>
                                    </div>
                                    <div className="sp-item-detail-row" style={{ fontSize: '13px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                                        <FileText size={15} style={{ color: 'var(--sp-gray-400)' }} />
                                        <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: 'var(--sp-gray-700)' }} title={c.motif}>
                                            {c.motif}
                                        </span>
                                    </div>
                                    <div className="sp-item-detail-row" style={{ fontSize: '13px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                                        <User size={15} style={{ color: 'var(--sp-gray-400)' }} />
                                        <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                            {mName ? mName : <em style={{ color: 'var(--sp-gray-300)', fontStyle: 'italic' }}>Non affecté</em>}
                                        </span>
                                    </div>
                                </div>

                                <div className="sp-item-actions" style={{ paddingTop: '15px', borderTop: '1px solid var(--sp-gray-100)', display: 'flex', gap: '8px', alignItems: 'center', marginTop: 'auto' }}>
                                    {(c.statut === 'en attente' || c.statut === 'en cours') ? (
                                        <>
                                            <div style={{ display: 'flex', gap: '8px' }}>
                                                {c.statut === 'en attente' && (
                                                    <>
                                                        <button className="sp-btn sp-btn-outline sp-btn-sm" style={{ padding: '6px 12px', fontSize: '12px', height: '32px', borderRadius: '10px' }} onClick={() => { setCurrentConsultId(c.id); setAffectModalOpen(true); }}>
                                                            <UserPlus size={14} /> Affecter
                                                        </button>
                                                        {!c.medecin_id ? (
                                                            <button onClick={() => setWarningModalOpen(true)} className="sp-btn sp-btn-warning sp-btn-sm" style={{ opacity: 0.5, cursor: 'not-allowed', padding: '6px 12px', fontSize: '12px', height: '32px', borderRadius: '10px', background: '#fbc05d' }}>
                                                                <Play size={14} /> Démarrer
                                                            </button>
                                                        ) : (
                                                            <button onClick={() => handleStatutChange(c.id, 'en cours')} className="sp-btn sp-btn-warning sp-btn-sm" style={{ padding: '6px 12px', fontSize: '12px', height: '32px', borderRadius: '10px', background: '#fbc05d' }}>
                                                                <Play size={14} /> Démarrer
                                                            </button>
                                                        )}
                                                    </>
                                                )}
                                                {c.statut === 'en cours' && (
                                                    <button onClick={() => handleStatutChange(c.id, 'terminée')} className="sp-btn sp-btn-success sp-btn-sm" style={{ padding: '6px 12px', fontSize: '12px', height: '32px', borderRadius: '10px' }}>
                                                        <Check size={14} /> Terminer
                                                    </button>
                                                )}
                                            </div>
                                            <div style={{ marginLeft: 'auto', display: 'flex', gap: '4px' }}>
                                                <button onClick={() => openForm(c)} className="sp-btn sp-btn-ghost sp-btn-sm" style={{ padding: '6px', color: 'var(--sp-gray-400)' }}>
                                                    <Edit2 size={16} />
                                                </button>
                                                {isAdmin && (
                                                    <button className="sp-btn sp-btn-ghost sp-btn-sm" style={{ color: 'var(--sp-danger)', padding: '6px' }} onClick={() => { setConsultToDelete({ id: c.id, name: c.nom_patient }); setDeleteModalOpen(true); }}>
                                                        <Trash2 size={16} />
                                                    </button>
                                                )}
                                            </div>
                                        </>
                                    ) : (
                                        <div style={{ display: 'flex', gap: '8px', width: '100%', justifyContent: 'flex-start' }}>
                                            <button onClick={() => openForm(c)} className="sp-btn sp-btn-ghost sp-btn-sm" style={{ padding: '6px', color: 'var(--sp-gray-400)' }}>
                                                <Edit2 size={16} />
                                            </button>
                                            {isAdmin && (
                                                <button className="sp-btn sp-btn-ghost sp-btn-sm" style={{ color: 'var(--sp-danger)', padding: '6px' }} onClick={() => { setConsultToDelete({ id: c.id, name: c.nom_patient }); setDeleteModalOpen(true); }}>
                                                    <Trash2 size={16} />
                                                </button>
                                            )}
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
            <div id="view-table">
                <div className="sp-table-wrap">
                    <table className="sp-table">
                        <thead>
                            <tr>
                                <th>#ID</th>
                                <th>Patient</th>
                                <th>Date & Heure</th>
                                <th>Motif</th>
                                <th>Médecin</th>
                                <th>Statut</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                                {filteredConsultations.map(c => {
                                    const mName = getMedecinName(c.medecin_id);
                                    const sc: Record<string, string> = { 'en attente': 'attente', 'en cours': 'cours', 'terminée': 'terminee' };
                                    const cls = sc[c.statut] || 'attente';

                                return (
                                    <tr key={c.id}>
                                        <td style={{color:'var(--sp-gray-400)', fontSize:'12px'}}>#{String(c.id).padStart(4, '0')}</td>
                                        <td>
                                            <div style={{fontWeight:600}}>{c.nom_patient}</div>
                                        </td>
                                        <td>{new Date(c.date_heure || c.date).toLocaleString('fr-FR', {day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'})}</td>
                                        <td style={{maxWidth:'200px'}}>
                                            <span title={c.motif || ''}>
                                                {(c.motif || '').length > 40 ? (c.motif || '').substring(0, 40) + '…' : (c.motif || '')}
                                            </span>
                                        </td>
                                        <td>
                                            {mName ? mName : <span style={{color:'var(--sp-gray-300)'}}>—</span>}
                                        </td>
                                        <td><span className={`sp-badge ${cls}`}>{c.statut}</span></td>
                                        <td>
                                            <div style={{display:'flex', gap:'6px', alignItems:'center'}}>
                                                {c.statut === 'en attente' && (
                                                    <>
                                                        <button className="sp-btn sp-btn-outline sp-btn-sm" onClick={() => { setCurrentConsultId(c.id); setAffectModalOpen(true); }}>
                                                            <UserPlus size={14} />
                                                        </button>
                                                        {!c.medecin_id ? (
                                                            <button onClick={() => setWarningModalOpen(true)} className="sp-btn sp-btn-warning sp-btn-sm" style={{opacity:0.5, cursor:'not-allowed'}} title="Affectation requise">
                                                                <Play size={14} />
                                                            </button>
                                                        ) : (
                                                            <button onClick={() => handleStatutChange(c.id, 'en cours')} className="sp-btn sp-btn-warning sp-btn-sm">
                                                                <Play size={14} />
                                                            </button>
                                                        )}
                                                    </>
                                                )}
                                                {c.statut === 'en cours' && (
                                                    <button onClick={() => handleStatutChange(c.id, 'terminée')} className="sp-btn sp-btn-success sp-btn-sm">
                                                        <Check size={14} />
                                                    </button>
                                                )}
                                                {isAdmin && (
                                                    <>
                                                        <button onClick={() => openForm(c)} className="sp-btn sp-btn-ghost sp-btn-sm">
                                                            <Edit2 size={14} />
                                                        </button>
                                                        <button className="sp-btn sp-btn-ghost sp-btn-sm" style={{color:'var(--sp-danger)'}} onClick={() => { setConsultToDelete({id: c.id, name: c.nom_patient}); setDeleteModalOpen(true); }}>
                                                            <Trash2 size={14} />
                                                        </button>
                                                    </>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
          )}
      </div>

      {/* Modal Affectation */}
      {affectModalOpen && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal">
            <h3 style={{ marginBottom: '1rem' }}>Affecter un médecin</h3>
            <form onSubmit={handleAffecter}>
              <div className="sp-form-group">
                <label className="sp-form-label">Choisir un médecin disponible</label>
                <select 
                  className="sp-form-select" 
                  required 
                  value={selectedMedecinId} 
                  onChange={e => setSelectedMedecinId(e.target.value)}
                >
                  <option value="">Sélectionner...</option>
                  {availableMedecins.map(m => (
                    <option key={m.medecin_id} value={m.medecin_id}>Dr. {m.prenoms} {m.nom} ({m.specialite})</option>
                  ))}
                </select>
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '20px', justifyContent: 'flex-end' }}>
                <button type="button" className="sp-btn sp-btn-ghost" onClick={() => setAffectModalOpen(false)}>Annuler</button>
                <button type="submit" className="sp-btn sp-btn-primary">Confirmer</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Warning Modal */}
      {warningModalOpen && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ textAlign: 'center' }}>
            <div style={{ width: 60, height: 60, background: '#fffbeb', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
              <AlertTriangle size={30} style={{ color: '#d97706' }} />
            </div>
            <h3>Médecin non affecté</h3>
            <p style={{ marginBottom: '24px' }}>Veuillez d'abord affecter un médecin à cette consultation avant de la démarrer.</p>
            <button className="sp-btn sp-btn-primary" onClick={() => setWarningModalOpen(false)}>Compris</button>
          </div>
        </div>
      )}

      {/* Delete Modal */}
      {deleteModalOpen && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal">
            <div style={{ width: 60, height: 60, background: 'var(--sp-danger-light)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
              <Trash2 size={30} style={{ color: 'var(--sp-danger)' }} />
            </div>
            <h3 style={{ textAlign: 'center' }}>Supprimer la consultation ?</h3>
            <p style={{ textAlign: 'center', marginBottom: '24px' }}>La consultation de <strong>{consultToDelete?.name}</strong> sera supprimée définitivement.</p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <button className="sp-btn sp-btn-ghost" onClick={() => setDeleteModalOpen(false)}>Annuler</button>
              <button className="sp-btn sp-btn-danger" onClick={handleDelete}><Trash2 size={16} /> Supprimer</button>
            </div>
          </div>
        </div>
      )}

      {/* Form Modal */}
      {formModalOpen && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ maxWidth: '600px', padding: 0, overflow: 'hidden' }}>
            <div className="sp-card-header" style={{ padding: '20px 24px', borderBottom: '1px solid var(--sp-gray-100)' }}>
              <div className="sp-card-title">
                {formData.id ? <Edit2 size={20} /> : <Clipboard size={20} />}
                {formData.id ? 'Modifier la consultation' : 'Nouvelle consultation'}
              </div>
            </div>
            <form onSubmit={handleSaveConsultation} style={{ padding: '24px' }}>
              <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                <label className="sp-form-label">Nom du patient <span className="required">*</span></label>
                <div className="sp-input-icon-wrap">
                  <User size={18} className="sp-input-icon" />
                  <input 
                    type="text" 
                    className="sp-form-input" 
                    style={{ paddingLeft: '40px' }}
                    required 
                    placeholder="Nom complet du patient"
                    value={formData.nom_patient || ''} 
                    onChange={e => setFormData({...formData, nom_patient: e.target.value})} 
                  />
                </div>
              </div>

              <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                <label className="sp-form-label">Date et Heure <span className="required">*</span></label>
                <div className="sp-input-icon-wrap">
                  <Calendar size={18} className="sp-input-icon" />
                  <input 
                    type="datetime-local" 
                    className="sp-form-input" 
                    style={{ paddingLeft: '40px' }}
                    required 
                    value={(formData.date_heure || '').slice(0, 16)} 
                    onChange={e => setFormData({...formData, date_heure: e.target.value})} 
                  />
                </div>
              </div>

              <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                <label className="sp-form-label">Motif de consultation <span className="required">*</span></label>
                <textarea 
                  className="sp-form-textarea" 
                  required 
                  placeholder="Décrivez le motif de la consultation..."
                  rows={4}
                  value={formData.motif || ''} 
                  onChange={e => setFormData({...formData, motif: e.target.value})} 
                />
              </div>

              {formData.id && (
                <>
                  <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                    <label className="sp-form-label">Médecin</label>
                    <div className="sp-input-icon-wrap">
                      <UserCheck size={18} className="sp-input-icon" />
                      <select 
                        className="sp-form-select" 
                        style={{ paddingLeft: '40px' }}
                        value={formData.medecin_id || ''} 
                        onChange={e => setFormData({...formData, medecin_id: e.target.value ? Number(e.target.value) : undefined})}
                      >
                        <option value="">-- Non affecté --</option>
                        {medecins.map(m => (
                          <option key={m.medecin_id} value={m.medecin_id}>Dr. {m.prenoms} {m.nom} — {m.specialite}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                    <label className="sp-form-label">Statut</label>
                    <select 
                      className="sp-form-select" 
                      value={formData.statut || 'en attente'} 
                      onChange={e => setFormData({...formData, statut: e.target.value as Consultation['statut']})}
                    >
                      <option value="en attente">En attente</option>
                      <option value="en cours">En cours</option>
                      <option value="terminée">Terminée</option>
                    </select>
                  </div>
                </>
              )}

              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '24px' }}>
                <button type="button" className="sp-btn sp-btn-ghost" onClick={() => setFormModalOpen(false)}>Annuler</button>
                <button type="submit" className="sp-btn sp-btn-primary">
                  <Save size={18} />
                  {formData.id ? 'Enregistrer les modifications' : 'Enregistrer la consultation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
        </>
      )}
    </>
  );
};

export default Consultations;
