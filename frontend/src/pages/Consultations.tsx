import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analyticsAPI, consultationsAPI } from '../services/api';
import type { Consultation } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
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
  const { isAdmin, user } = useAuth();
  const { showToast } = useToast();
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [medecins, setMedecins] = useState<Medecin[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('tous');
  const [view, setView] = useState<'grid' | 'table'>(() => (localStorage.getItem('sp_cons_view') as 'grid' | 'table') || 'grid');

  // Modal states
  const [affectModalOpen, setAffectModalOpen] = useState(false);
  const [currentConsultId, setCurrentConsultId] = useState<number | null>(null);
  const [selectedMedecinId, setSelectedMedecinId] = useState('');
  const [affectLoading, setAffectLoading] = useState(false);

  const [warningModalOpen, setWarningModalOpen] = useState(false);

  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [consultToDelete, setConsultToDelete] = useState<{id: number, name: string} | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Form Modal state
  const [formModalOpen, setFormModalOpen] = useState(false);
  const [formData, setFormData] = useState<Partial<Consultation>>({});
  const [formLoading, setFormLoading] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('sp_token');
      
      const [consultationsData, personnelData] = await Promise.all([
        analyticsAPI.getRecentConsultations(200),
        analyticsAPI.getPersonnelDisponible()
      ]);
      setConsultations(consultationsData);

      // Si admin, on récupère TOUS les médecins pour pouvoir réaffecter même à ceux non marqués "dispo"
      // ou simplement pour voir les noms de ceux déjà affectés mais occupés.
      if (isAdmin && token) {
        try {
          const allMedecins = await adminAPI.getMedecins(token);
          setMedecins(allMedecins.map(m => ({
            medecin_id: m.medecin_id,
            nom: m.nom,
            prenoms: m.prenoms,
            specialite: m.specialite,
            telephone: m.telephone,
            disponible: m.disponible
          })));
        } catch (adminErr) {
          console.error('Erreur lors du chargement de tous les médecins:', adminErr);
          // Fallback sur les dispos si l'appel admin échoue
          setMedecins((personnelData.medecins.liste || []).map((m: any) => ({
            medecin_id: m.id,
            nom: m.nom,
            prenoms: m.prenoms,
            specialite: m.specialite || '',
            telephone: m.telephone || '',
            disponible: true,
          })));
        }
      } else {
        setMedecins((personnelData.medecins.liste || []).map((m: any) => ({
          medecin_id: m.id,
          nom: m.nom,
          prenoms: m.prenoms,
          specialite: m.specialite || '',
          telephone: m.telephone || '',
          disponible: true,
        })));
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
      showToast('Impossible de charger les consultations', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
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

  const statusOrder: Record<string, number> = {
    'en attente': 1,
    'en_attente_medecin': 2,
    '': 2, // statut vide = en_attente_medecin (avant migration)
    'en cours': 3,
    'terminée': 4,
  };

  const filteredConsultations = consultations.filter(c => {
    if (!c) return false;
    const term = search.toLowerCase();
    const medName = (getMedecinName(c.medecin_id) || '').toLowerCase();
    const nomPatient = (c.nom_patient || '').toLowerCase();
    const motif = (c.motif || '').toLowerCase();
    const matchesSearch = nomPatient.includes(term) || motif.includes(term) || medName.includes(term);
    const effectiveStatut = (!c.statut || c.statut === '') ? 'en_attente_medecin' : c.statut;
    const matchesStatus = statusFilter === 'tous' || effectiveStatut === statusFilter;
    return matchesSearch && matchesStatus;
  }).sort((a, b) => {
    const orderA = statusOrder[a.statut] ?? 99;
    const orderB = statusOrder[b.statut] ?? 99;
    if (orderA !== orderB) return orderA - orderB;
    return new Date(b.date_heure || b.date || 0).getTime() - new Date(a.date_heure || a.date || 0).getTime();
  });

  // ─── Handlers (connectés au backend) ─────────────────────────────────────────

  const handleAffecter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentConsultId || !selectedMedecinId) return;
    setAffectLoading(true);
    try {
      await consultationsAPI.affecter(currentConsultId, Number(selectedMedecinId));
      setConsultations(prev => prev.map(c =>
        c.id === currentConsultId ? { ...c, medecin_id: Number(selectedMedecinId) } : c
      ));
      const med = medecins.find(m => m.medecin_id === Number(selectedMedecinId));
      showToast(`Médecin ${med ? `Dr. ${med.prenoms} ${med.nom}` : ''} affecté avec succès`, 'success');
      setAffectModalOpen(false);
      setSelectedMedecinId('');
    } catch (err: any) {
      showToast(err.detail || 'Erreur lors de l\'affectation', 'error');
    } finally {
      setAffectLoading(false);
    }
  };

  const handleStatutChange = async (id: number, newStatut: 'en cours' | 'terminée') => {
    try {
      await consultationsAPI.updateStatut(id, newStatut);
      setConsultations(prev => prev.map(c => c.id === id ? { ...c, statut: newStatut } : c));
      showToast(`Statut mis à jour : ${newStatut}`, 'success');
    } catch (err: any) {
      showToast(err.detail || 'Erreur lors du changement de statut', 'error');
    }
  };

  const handleDelete = async () => {
    if (!consultToDelete) return;
    setDeleteLoading(true);
    try {
      await consultationsAPI.delete(consultToDelete.id);
      setConsultations(prev => prev.filter(c => c.id !== consultToDelete.id));
      showToast('Consultation supprimée', 'success');
      setDeleteModalOpen(false);
    } catch (err: any) {
      showToast(err.detail || 'Erreur lors de la suppression', 'error');
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleSaveConsultation = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormLoading(true);
    try {
      if (formData.id) {
        // Modification d'une consultation existante
        await consultationsAPI.update(formData.id, {
          nom_patient: formData.nom_patient,
          motif: formData.motif,
          date_heure: formData.date_heure,
          medecin_id: formData.medecin_id ?? null,
          statut: formData.statut,
        });
        setConsultations(prev => prev.map(c => c.id === formData.id ? { ...c, ...formData } as Consultation : c));
        showToast('Consultation mise à jour', 'success');
      }
      setFormModalOpen(false);
    } catch (err: any) {
      showToast(err.detail || 'Erreur lors de l\'enregistrement', 'error');
    } finally {
      setFormLoading(false);
    }
  };

  const openForm = (consult: Consultation) => {
    setFormData(consult);
    setFormModalOpen(true);
  };

  const statusLabels: Record<string, string> = {
    'tous': 'Tous',
    'en attente': 'En attente',
    'en_attente_medecin': 'Att. médecin',
    'en cours': 'En cours',
    'terminée': 'Terminée',
  };

  const countByStatus = (s: string) => s === 'tous' ? consultations.length : consultations.filter(c => c.statut === s).length;

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
              <p className="sp-page-subtitle">{filteredConsultations.length} consultation(s) affichée(s)</p>
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              {(isAdmin || user?.role === 'medecin' || user?.role === 'infirmier') && (
                <Link to="/consultation/nouvelle" className="sp-btn sp-btn-primary">
                  <PlusCircle size={18} />
                  <span>Nouvelle consultation</span>
                </Link>
              )}
            </div>
          </div>

          <div className="sp-card sp-fade-in">
            <div className="sp-card-header">
              <div className="sp-card-title">
                <List size={20} />
                <span>Liste des consultations</span>
              </div>
              <div className="sp-toolbar">
                {/* Filtres statut */}
                <div style={{ display: 'flex', gap: '6px', marginRight: '8px' }}>
                  {['tous', 'en attente', 'en_attente_medecin', 'en cours', 'terminée'].map(s => {
                    const count = countByStatus(s);
                    const isActive = statusFilter === s;
                    const colors: Record<string, string> = {
                      'en attente': '#F59E0B',
                      'en_attente_medecin': '#6366F1',
                      'en cours': '#3B82F6',
                      'terminée': '#10B981',
                    };
                    return (
                      <button
                        key={s}
                        onClick={() => setStatusFilter(s)}
                        style={{
                          padding: '5px 10px',
                          fontSize: '12px',
                          borderRadius: '20px',
                          border: `1px solid ${isActive ? (colors[s] || '#4F46E5') : '#E5E7EB'}`,
                          background: isActive ? (colors[s] || '#4F46E5') : '#fff',
                          color: isActive ? '#fff' : '#6B7280',
                          cursor: 'pointer',
                          fontWeight: isActive ? 700 : 400,
                          whiteSpace: 'nowrap',
                          transition: 'all 0.15s',
                        }}
                      >
                        {statusLabels[s]} {count > 0 && <span style={{ opacity: 0.8 }}>({count})</span>}
                      </button>
                    );
                  })}
                </div>
                <div className="sp-search-box">
                  <Search size={18} />
                  <input
                    type="text"
                    placeholder="Rechercher patient, motif, médecin..."
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

            {/* VUE CARTE */}
            {view === 'grid' && (
              <div id="view-grid" style={{ padding: '20px' }}>
                {filteredConsultations.length === 0 ? (
                  <div className="sp-empty">
                    <FileText size={64} style={{ margin: '0 auto 1rem', color: 'var(--sp-gray-300)' }} />
                    <div className="sp-empty-title">Aucune consultation trouvée</div>
                    <div className="sp-empty-text">
                      {search ? `Aucun résultat pour « ${search} »` : "Commencez par ajouter une consultation."}
                    </div>
                  </div>
                ) : (
                  <div className="sp-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px', width: '100%' }}>
                    {filteredConsultations.map(c => {
                      const mName = getMedecinName(c.medecin_id);
                      const sc: Record<string, string> = { 'en attente': 'attente', 'en cours': 'cours', 'terminée': 'terminee', 'en_attente_medecin': 'attente' };
                      const cls = sc[c.statut] || 'attente';
                      const initiales = (c.nom_patient || '??').substring(0, 2).toUpperCase();
                      return (
                        <div className="sp-item-card" key={c.id} style={{ padding: '24px', position: 'relative', minHeight: '280px', display: 'flex', flexDirection: 'column' }}>
                          <div className="sp-item-card-header" style={{ marginBottom: '16px', display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
                            {(user?.role === 'admin' || user?.role === 'medecin') && c.patient_id ? (
                              <Link
                                to={`/dossier-patient/${c.patient_id}`}
                                style={{ width: '48px', height: '48px', fontSize: '18px', borderRadius: '12px', flexShrink: 0, cursor: 'pointer', transition: 'transform 0.2s, box-shadow 0.2s', textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, var(--sp-primary), var(--sp-accent))', color: '#fff', fontWeight: 700 }}
                                onMouseEnter={e => { e.currentTarget.style.transform = 'scale(1.05)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'; }}
                                onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.boxShadow = 'none'; }}
                                title="Voir le dossier patient"
                              >
                                {initiales}
                              </Link>
                            ) : (
                              <div className="sp-item-avatar" style={{ width: '48px', height: '48px', fontSize: '18px', borderRadius: '12px', flexShrink: 0 }}>
                                {initiales}
                              </div>
                            )}
                            <div style={{ flex: 1, minWidth: 0, paddingTop: '2px' }}>
                              {(user?.role === 'admin' || user?.role === 'medecin') && c.patient_id ? (
                                <Link
                                  to={`/dossier-patient/${c.patient_id}`}
                                  className="sp-item-name"
                                  style={{ fontSize: '16px', fontWeight: 700, marginBottom: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: '#4F46E5', textDecoration: 'none', cursor: 'pointer', display: 'block' }}
                                  onMouseEnter={e => { e.currentTarget.style.textDecoration = 'underline'; }}
                                  onMouseLeave={e => { e.currentTarget.style.textDecoration = 'none'; }}
                                  title="Voir le dossier patient"
                                >
                                  {c.nom_patient}
                                </Link>
                              ) : (
                                <div className="sp-item-name" style={{ fontSize: '16px', fontWeight: 700, marginBottom: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                  {c.nom_patient}
                                </div>
                              )}
                              <span className={`sp-badge ${cls}`} style={{ fontSize: '11px', padding: '3px 10px', borderRadius: '20px' }}>
                                {(!c.statut || (!c.statut || c.statut === 'en_attente_medecin')) ? 'att. médecin' : c.statut}
                              </span>
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--sp-gray-400)', position: 'absolute', top: '24px', right: '24px', fontWeight: 400, opacity: 0.8 }}>
                              #{String(c.id).padStart(4, '0')}
                            </div>
                          </div>

                          <div className="sp-item-details" style={{ gap: '12px', marginBottom: '20px', flex: 1 }}>
                            <div className="sp-item-detail-row" style={{ fontSize: '13px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                              <Calendar size={15} style={{ color: 'var(--sp-gray-400)' }} />
                              <span style={{ color: 'var(--sp-gray-700)' }}>
                                {new Date(c.date_heure || c.date).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }).replace(',', ' à')}
                              </span>
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
                            {(!c.statut || c.statut === 'en_attente_medecin') ? (
                              <div style={{ display: 'flex', gap: '8px', width: '100%', alignItems: 'center' }}>
                                {user?.role === 'medecin' && (
                                  c.medecin_id === user.medecin_id ? (
                                    <Link to={`/consultation/nouvelle?reprendre=${c.id}`} className="sp-btn sp-btn-primary" style={{ padding: '6px 14px', fontSize: '12px', height: '32px', borderRadius: '10px', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                      <Play size={14} /> Continuer
                                    </Link>
                                  ) : (
                                    <button 
                                      onClick={() => showToast(`Cette consultation est réservée au Dr. ${getMedecinName(c.medecin_id)}`, 'info')}
                                      className="sp-btn sp-btn-outline" 
                                      style={{ padding: '6px 14px', fontSize: '12px', height: '32px', borderRadius: '10px', display: 'flex', alignItems: 'center', gap: '6px', opacity: 0.7 }}
                                    >
                                      <Play size={14} /> Continuer
                                    </button>
                                  )
                                )}
                                {isAdmin && (
                                  <button 
                                    className="sp-btn sp-btn-outline sp-btn-sm" 
                                    style={{ padding: '6px 12px', fontSize: '12px', height: '32px', borderRadius: '10px' }} 
                                    onClick={() => { setCurrentConsultId(c.id); setSelectedMedecinId(c.medecin_id?.toString() || ''); setAffectModalOpen(true); }}
                                  >
                                    <UserPlus size={14} /> {c.medecin_id ? 'Réaffecter' : 'Affecter'}
                                  </button>
                                )}
                                {!isAdmin && <span style={{ fontSize: '11px', color: '#6366F1', fontStyle: 'italic' }}>En attente médecin</span>}
                                {isAdmin && (
                                  <div style={{ marginLeft: 'auto' }}>
                                    <button className="sp-btn sp-btn-ghost sp-btn-sm" style={{ color: 'var(--sp-danger)', padding: '6px' }} onClick={() => { setConsultToDelete({ id: c.id, name: c.nom_patient }); setDeleteModalOpen(true); }}>
                                      <Trash2 size={16} />
                                    </button>
                                  </div>
                                )}
                              </div>
                            ) : (c.statut === 'en attente' || c.statut === 'en cours') ? (
                              <>
                                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                                  {c.statut === 'en attente' && (
                                    <>
                                      <button className="sp-btn sp-btn-outline sp-btn-sm" style={{ padding: '6px 12px', fontSize: '12px', height: '32px', borderRadius: '10px' }} onClick={() => { setCurrentConsultId(c.id); setSelectedMedecinId(c.medecin_id?.toString() || ''); setAffectModalOpen(true); }}>
                                        <UserPlus size={14} /> {c.medecin_id ? 'Réaffecter' : 'Affecter'}
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
                                    <>
                                      {isAdmin && (
                                        <button className="sp-btn sp-btn-outline sp-btn-sm" style={{ padding: '6px 12px', fontSize: '12px', height: '32px', borderRadius: '10px' }} onClick={() => { setCurrentConsultId(c.id); setSelectedMedecinId(c.medecin_id?.toString() || ''); setAffectModalOpen(true); }}>
                                          <UserPlus size={14} /> Réaffecter
                                        </button>
                                      )}
                                      <button onClick={() => handleStatutChange(c.id, 'terminée')} className="sp-btn sp-btn-success sp-btn-sm" style={{ padding: '6px 12px', fontSize: '12px', height: '32px', borderRadius: '10px' }}>
                                        <Check size={14} /> Terminer
                                      </button>
                                    </>
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
                        const sc: Record<string, string> = { 'en attente': 'attente', 'en cours': 'cours', 'terminée': 'terminee', 'en_attente_medecin': 'attente' };
                        const cls = sc[c.statut] || 'attente';
                        return (
                          <tr key={c.id}>
                            <td style={{ color: 'var(--sp-gray-400)', fontSize: '12px' }}>#{String(c.id).padStart(4, '0')}</td>
                            <td>
                              <div style={{ fontWeight: 600 }}>{c.nom_patient}</div>
                            </td>
                            <td>{new Date(c.date_heure || c.date).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</td>
                            <td style={{ maxWidth: '200px' }}>
                              <span title={c.motif || ''}>
                                {(c.motif || '').length > 40 ? (c.motif || '').substring(0, 40) + '…' : (c.motif || '')}
                              </span>
                            </td>
                            <td>
                              {mName ? mName : <span style={{ color: 'var(--sp-gray-300)' }}>—</span>}
                            </td>
                            <td>
                              <span className={`sp-badge ${cls}`}>
                                {(!c.statut || (!c.statut || c.statut === 'en_attente_medecin')) ? 'att. médecin' : c.statut}
                              </span>
                            </td>
                            <td>
                              <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                                {(!c.statut || c.statut === 'en_attente_medecin') && user?.role === 'medecin' && (
                                  c.medecin_id === user.medecin_id ? (
                                    <Link to={`/consultation/nouvelle?reprendre=${c.id}`} className="sp-btn sp-btn-primary sp-btn-sm" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                      <Play size={14} /> Continuer
                                    </Link>
                                  ) : (
                                    <button 
                                      onClick={() => showToast(`Réservé au Dr. ${getMedecinName(c.medecin_id)}`, 'info')}
                                      className="sp-btn sp-btn-outline sp-btn-sm" 
                                      style={{ display: 'flex', alignItems: 'center', gap: '4px', opacity: 0.7 }}
                                    >
                                      <Play size={14} /> Continuer
                                    </button>
                                  )
                                )}
                                {c.statut === 'en attente' && (
                                  <>
                                    <button className="sp-btn sp-btn-outline sp-btn-sm" onClick={() => { setCurrentConsultId(c.id); setSelectedMedecinId(c.medecin_id?.toString() || ''); setAffectModalOpen(true); }}>
                                      <UserPlus size={14} /> {c.medecin_id ? 'Réaffecter' : 'Affecter'}
                                    </button>
                                    {!c.medecin_id ? (
                                      <button onClick={() => setWarningModalOpen(true)} className="sp-btn sp-btn-warning sp-btn-sm" style={{ opacity: 0.5, cursor: 'not-allowed' }} title="Affectation requise">
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
                                  <>
                                    {isAdmin && (
                                      <button className="sp-btn sp-btn-outline sp-btn-sm" onClick={() => { setCurrentConsultId(c.id); setSelectedMedecinId(c.medecin_id?.toString() || ''); setAffectModalOpen(true); }}>
                                        <UserPlus size={14} /> Réaffecter
                                      </button>
                                    )}
                                    <button onClick={() => handleStatutChange(c.id, 'terminée')} className="sp-btn sp-btn-success sp-btn-sm">
                                      <Check size={14} />
                                    </button>
                                  </>
                                )}
                                {(!c.statut || c.statut === 'en_attente_medecin') && isAdmin && (
                                   <button className="sp-btn sp-btn-outline sp-btn-sm" onClick={() => { setCurrentConsultId(c.id); setSelectedMedecinId(c.medecin_id?.toString() || ''); setAffectModalOpen(true); }}>
                                     <UserPlus size={14} /> {c.medecin_id ? 'Réaffecter' : 'Affecter'}
                                   </button>
                                )}
                                <button onClick={() => openForm(c)} className="sp-btn sp-btn-ghost sp-btn-sm">
                                  <Edit2 size={14} />
                                </button>
                                {isAdmin && (
                                  <button className="sp-btn sp-btn-ghost sp-btn-sm" style={{ color: 'var(--sp-danger)' }} onClick={() => { setConsultToDelete({ id: c.id, name: c.nom_patient }); setDeleteModalOpen(true); }}>
                                    <Trash2 size={14} />
                                  </button>
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
                    <label className="sp-form-label">
                      {isAdmin ? 'Sélectionner le nouveau médecin' : 'Choisir un médecin disponible'}
                    </label>
                    {medecins.length === 0 ? (
                      <p style={{ color: '#EF4444', fontSize: '13px' }}>Aucun médecin trouvé.</p>
                    ) : (
                      <select
                        className="sp-form-select"
                        required
                        value={selectedMedecinId}
                        onChange={e => setSelectedMedecinId(e.target.value)}
                      >
                        <option value="">Sélectionner...</option>
                        {medecins.map(m => (
                          <option key={m.medecin_id} value={m.medecin_id}>
                            Dr. {m.prenoms} {m.nom}{m.specialite ? ` (${m.specialite})` : ''} {!m.disponible && '(Indisponible)'}
                          </option>
                        ))}
                      </select>
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '1rem', marginTop: '20px', justifyContent: 'flex-end' }}>
                    <button type="button" className="sp-btn sp-btn-ghost" onClick={() => setAffectModalOpen(false)}>Annuler</button>
                    <button type="submit" className="sp-btn sp-btn-primary" disabled={affectLoading || !selectedMedecinId}>
                      {affectLoading ? 'Affectation...' : 'Confirmer'}
                    </button>
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
                  <button className="sp-btn sp-btn-danger" onClick={handleDelete} disabled={deleteLoading}>
                    <Trash2 size={16} /> {deleteLoading ? 'Suppression...' : 'Supprimer'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Form Modal (rapide + édition) */}
          {formModalOpen && (
            <div className="sp-modal-overlay open">
              <div className="sp-modal" style={{ maxWidth: '600px', padding: 0, overflow: 'hidden' }}>
                <div className="sp-card-header" style={{ padding: '20px 24px', borderBottom: '1px solid var(--sp-gray-100)' }}>
                  <div className="sp-card-title">
                    {formData.id ? <Edit2 size={20} /> : <Clipboard size={20} />}
                    {formData.id ? 'Modifier la consultation' : 'Détails de la consultation'}
                  </div>
                  <button className="sp-btn sp-btn-ghost sp-btn-sm" style={{ padding: '4px' }} onClick={() => setFormModalOpen(false)}>
                    <X size={18} />
                  </button>
                </div>
                <form onSubmit={handleSaveConsultation} style={{ padding: '24px' }}>
                  {/* Mode création : saisie structurée nom/prénoms/sexe */}
                  <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                    <label className="sp-form-label">Nom du patient <span style={{ color: '#EF4444' }}>*</span></label>
                    <div className="sp-input-icon-wrap">
                      <User size={18} className="sp-input-icon" />
                      <input type="text" className="sp-form-input" style={{ paddingLeft: '40px' }} required
                        placeholder="Nom complet du patient"
                        value={formData.nom_patient || ''}
                        onChange={e => setFormData({ ...formData, nom_patient: e.target.value })} />
                    </div>
                  </div>

                  <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                    <label className="sp-form-label">Date et Heure <span style={{ color: '#EF4444' }}>*</span></label>
                    <div className="sp-input-icon-wrap">
                      <Calendar size={18} className="sp-input-icon" />
                      <input
                        type="datetime-local"
                        className="sp-form-input"
                        style={{ paddingLeft: '40px' }}
                        required
                        max={new Date().toISOString().slice(0, 16)}
                        value={(formData.date_heure || '').slice(0, 16)}
                        onChange={e => setFormData({ ...formData, date_heure: e.target.value })}
                      />
                    </div>
                  </div>

                  <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                    <label className="sp-form-label">Motif de consultation <span style={{ color: '#EF4444' }}>*</span></label>
                    <textarea
                      className="sp-form-textarea"
                      required
                      placeholder="Décrivez le motif de la consultation..."
                      rows={4}
                      value={formData.motif || ''}
                      onChange={e => setFormData({ ...formData, motif: e.target.value })}
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
                            onChange={e => setFormData({ ...formData, medecin_id: e.target.value ? Number(e.target.value) : undefined })}
                          >
                            <option value="">-- Non affecté --</option>
                            {medecins.map(m => (
                              <option key={m.medecin_id} value={m.medecin_id}>Dr. {m.prenoms} {m.nom}{m.specialite ? ` — ${m.specialite}` : ''}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                        <label className="sp-form-label">Statut</label>
                        <select
                          className="sp-form-select"
                          value={formData.statut || 'en attente'}
                          onChange={e => setFormData({ ...formData, statut: e.target.value as Consultation['statut'] })}
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
                    <button type="submit" className="sp-btn sp-btn-primary" disabled={formLoading}>
                      <Save size={18} />
                      {formLoading ? 'Enregistrement...' : (formData.id ? 'Enregistrer les modifications' : 'Créer la consultation')}
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
