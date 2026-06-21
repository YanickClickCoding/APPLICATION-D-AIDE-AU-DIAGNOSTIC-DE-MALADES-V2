import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analyticsAPI, consultationsAPI, adminAPI } from '../services/api';
import type { Consultation } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import {
  Search, Grid, List, PlusCircle, Calendar, FileText, UserCheck,
  Play, Check, Edit2, Trash2, UserPlus, AlertTriangle, User, Save,
  Clipboard, X, Activity, Users
} from 'lucide-react';

interface Medecin {
  medecin_id: number;
  nom: string;
  prenoms: string;
  specialite: string;
  telephone: string;
  disponible: boolean;
}

type ViewMode = 'grid' | 'table';

const Consultations = () => {
  const { isAdmin, user } = useAuth();
  const isInfirmier = user?.role === 'infirmier';
  const { showToast } = useToast();
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [medecins, setMedecins] = useState<Medecin[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('tous');
  const [view, setView] = useState<ViewMode>(
    () => (localStorage.getItem('sp_cons_view') as ViewMode) || 'grid'
  );

  // Modal states
  const [affectModalOpen, setAffectModalOpen] = useState(false);
  const [currentConsultId, setCurrentConsultId] = useState<number | null>(null);
  const [selectedMedecinId, setSelectedMedecinId] = useState('');
  const [affectLoading, setAffectLoading] = useState(false);

  const [warningModalOpen, setWarningModalOpen] = useState(false);

  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [consultToDelete, setConsultToDelete] = useState<{id: number, name: string} | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const [formModalOpen, setFormModalOpen] = useState(false);
  const [formData, setFormData] = useState<Partial<Consultation>>({});
  const [formLoading, setFormLoading] = useState(false);

  // Modal "Voir les X consultations" d'un patient
  const [consultListModal, setConsultListModal] = useState<{
    patientName: string;
    consultations: Consultation[];
  } | null>(null);
  const [hoveredConsultId, setHoveredConsultId] = useState<number | null>(null);

  useEffect(() => {
    document.body.style.overflow = consultListModal ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [consultListModal]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('sp_token');

      const [consultationsData, personnelData] = await Promise.all([
        analyticsAPI.getRecentConsultations(200),
        analyticsAPI.getPersonnelDisponible()
      ]);
      setConsultations(consultationsData);

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
        } catch {
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
    } catch {
      showToast('Impossible de charger les consultations', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const getMedecinName = (id: number | null | undefined) => {
    if (!id) return null;
    const m = medecins.find(med => med && med.medecin_id === id);
    return m ? `Dr. ${m.prenoms} ${m.nom}` : null;
  };

  const handleViewChange = (v: ViewMode) => {
    setView(v);
    localStorage.setItem('sp_cons_view', v);
  };

  const statusOrder: Record<string, number> = {
    'en attente': 1,
    'en_attente_medecin': 2,
    'en cours': 3,
    'terminée': 4,
  };

  const filteredConsultations = consultations.filter(c => {
    if (!c) return false;
    const term = search.toLowerCase();
    const medName = (getMedecinName(c.medecin_id) || '').toLowerCase();
    const nomPatient = (c.nom_patient || '').toLowerCase();
    const motif = (c.motif || '').toLowerCase();
    // Recherche par ID patient / ID consultation : on retire « # » et les zéros de tête
    const idToken = term.replace(/^#/, '').replace(/^0+/, '');
    const matchesId = idToken !== '' && /^\d+$/.test(idToken) && (
      String(c.patient_id ?? '') === idToken || String(c.id) === idToken
    );
    const matchesSearch = nomPatient.includes(term) || motif.includes(term) || medName.includes(term) || matchesId;
    const effectiveStatut = !c.statut ? 'en_attente_medecin' : c.statut;
    const matchesStatus = statusFilter === 'tous' || effectiveStatut === statusFilter;
    return matchesSearch && matchesStatus;
  }).sort((a, b) => {
    const orderA = statusOrder[a.statut] ?? 99;
    const orderB = statusOrder[b.statut] ?? 99;
    if (orderA !== orderB) return orderA - orderB;
    return new Date(b.date_heure || b.date || 0).getTime() - new Date(a.date_heure || a.date || 0).getTime();
  });

  // Groupement par nom de patient (insensible à la casse) pour éviter les doublons visuels
  const patientGroups = (() => {
    const groups = new Map<string, Consultation[]>();
    filteredConsultations.forEach(c => {
      const key = (c.nom_patient || '').trim().toLowerCase() || `solo-${c.id}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key)!.push(c);
    });
    return Array.from(groups.values()).map(consults => {
      const sorted = [...consults].sort((a, b) =>
        new Date(b.date_heure || b.date || 0).getTime() - new Date(a.date_heure || a.date || 0).getTime()
      );
      return { consultations: sorted, latest: sorted[0] };
    }).sort((a, b) =>
      new Date(b.latest?.date_heure || b.latest?.date || 0).getTime() -
      new Date(a.latest?.date_heure || a.latest?.date || 0).getTime()
    );
  })();

  // ─── Handlers ────────────────────────────────────────────────────────────────

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

  const countByStatus = (s: string) =>
    s === 'tous'
      ? consultations.length
      : consultations.filter(c => c.statut === s).length;

  const formatDate = (dateStr: string | undefined) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleString('fr-FR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    }).replace(',', ' à');
  };

  const getStatutBadge = (statut: string) => {
    const sc: Record<string, string> = {
      'en attente': 'attente',
      'en cours': 'cours',
      'terminée': 'terminee',
      'en_attente_medecin': 'attente',
      '': 'attente',
    };
    const label: Record<string, string> = {
      'en attente': 'en attente',
      'en cours': 'en cours',
      'terminée': 'terminée',
      'en_attente_medecin': 'att. médecin',
      '': 'att. médecin',
    };
    return { cls: sc[statut] || 'attente', text: label[statut] || statut };
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
          {/* ── En-tête page ── */}
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

          {/* ── Carte principale ── */}
          <div className="sp-card sp-fade-in">
            {/* ── Toolbar ── */}
            <div className="sp-card-header">
              <div className="sp-card-title">
                <List size={20} />
                <span>Liste des consultations</span>
              </div>
              <div className="sp-toolbar">
                {/* Filtres statut */}
                <div style={{ display: 'flex', gap: '6px', marginRight: '8px', flexWrap: 'wrap' }}>
                  {(['tous', 'en attente', 'en_attente_medecin', 'en cours', 'terminée'] as const).map(s => {
                    const count = countByStatus(s);
                    const isActive = statusFilter === s;
                    return (
                      <button
                        key={s}
                        onClick={() => setStatusFilter(s)}
                        style={{
                          padding: '5px 12px',
                          fontSize: '12px',
                          borderRadius: '20px',
                          border: 'none',
                          background: isActive ? '#0B2545' : 'transparent',
                          color: isActive ? '#fff' : '#6B7280',
                          cursor: 'pointer',
                          fontWeight: isActive ? 700 : 400,
                          whiteSpace: 'nowrap',
                          transition: 'all 0.15s',
                        }}
                      >
                        {statusLabels[s]} {count > 0 && <span style={{ opacity: 0.85 }}>({count})</span>}
                      </button>
                    );
                  })}
                </div>

                {/* Recherche */}
                <div className="sp-search-box">
                  <Search size={15} />
                  <input
                    type="text"
                    placeholder="Rechercher patient, ID patient (#0001), motif..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                  />
                  {search && <X size={14} style={{ cursor: 'pointer' }} onClick={() => setSearch('')} />}
                </div>

                {/* Toggle vue */}
                <div className="sp-view-toggle">
                  <button
                    className={`sp-view-btn ${view === 'grid' ? 'active' : ''}`}
                    onClick={() => handleViewChange('grid')}
                    title="Vue cartes"
                  >
                    <Grid size={16} />
                  </button>
                  <button
                    className={`sp-view-btn ${view === 'table' ? 'active' : ''}`}
                    onClick={() => handleViewChange('table')}
                    title="Vue tableau"
                  >
                    <List size={16} />
                  </button>
                </div>
              </div>
            </div>

            {/* ══════════════════════════════════════════════════════════════
                VUE CARTES — groupée par patient
            ══════════════════════════════════════════════════════════════ */}
            {view === 'grid' && (
              <div style={{ padding: '20px', background: '#EEF2F7' }}>
                {patientGroups.length === 0 ? (
                  <div className="sp-empty">
                    <FileText size={64} style={{ margin: '0 auto 1rem', color: 'var(--sp-gray-300)' }} />
                    <div className="sp-empty-title">Aucune consultation trouvée</div>
                    <div className="sp-empty-text">
                      {search ? `Aucun résultat pour « ${search} »` : 'Commencez par ajouter une consultation.'}
                    </div>
                  </div>
                ) : (
                  <div
                    className="sp-grid"
                    style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(min(100%, 280px), 1fr))', gap: '20px', padding: 0 }}
                  >
                    {patientGroups.map(({ consultations: groupConsults, latest: c }) => {
                      const mName = getMedecinName(c.medecin_id);
                      const count = groupConsults.length;
                      const initiales = (c.nom_patient || '??').substring(0, 2).toUpperCase();
                      const { cls, text: statutText } = getStatutBadge(c.statut || '');

                      return (
                        <div
                          className="sp-item-card"
                          key={c.patient_id ? `p-${c.patient_id}` : `c-${c.id}`}
                          style={{ padding: '20px', display: 'flex', flexDirection: 'column', minHeight: '260px' }}
                        >
                          {/* ── En-tête carte ── */}
                          <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', marginBottom: '14px' }}>
                            {/* Avatar */}
                            <div
                              className="sp-item-avatar"
                              style={{ width: '46px', height: '46px', fontSize: '16px', borderRadius: '10px', flexShrink: 0 }}
                            >
                              {initiales}
                            </div>

                            {/* Nom + badges */}
                            <div style={{ flex: 1, minWidth: 0 }}>
                              {isInfirmier && (!c.statut || c.statut === 'en_attente_medecin') ? (
                                <Link
                                  to={`/consultation/nouvelle?reprendre=${c.id}`}
                                  title="Modifier les symptômes ou les informations du patient, puis renvoyer au médecin"
                                  style={{
                                    fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '15px',
                                    color: 'var(--sp-primary)', textDecoration: 'none', display: 'block',
                                    marginBottom: '5px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                                  }}
                                >
                                  {c.nom_patient}
                                </Link>
                              ) : (user?.role === 'admin' || user?.role === 'medecin') && c.patient_id ? (
                                <Link
                                  to={`/dossier-patient/${c.patient_id}`}
                                  style={{
                                    fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '15px',
                                    color: 'var(--sp-primary)', textDecoration: 'none', display: 'block',
                                    marginBottom: '5px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                                  }}
                                >
                                  {c.nom_patient}
                                </Link>
                              ) : (
                                <div
                                  style={{
                                    fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '15px',
                                    color: 'var(--sp-gray-900)', marginBottom: '5px',
                                    whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                                  }}
                                >
                                  {c.nom_patient}
                                </div>
                              )}
                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                                <span className={`sp-badge ${cls}`} style={{ fontSize: '11px', padding: '2px 10px' }}>
                                  {statutText}
                                </span>
                                {count > 1 && (
                                  <span style={{ fontSize: '12px', color: 'var(--sp-gray-400)', fontWeight: 500 }}>
                                    {count} consultations
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>

                          {/* ── Label "Dernière consultation :" ── */}
                          <div style={{ fontSize: '12.5px', color: 'var(--sp-gray-500)', marginBottom: '10px' }}>
                            Dernière consultation :
                          </div>

                          {/* ── Détails ── */}
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px' }}>
                              <Calendar size={14} style={{ color: 'var(--sp-gray-400)', flexShrink: 0 }} />
                              <span style={{ color: 'var(--sp-gray-700)' }}>{formatDate(c.date_heure || c.date)}</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px' }}>
                              <FileText size={14} style={{ color: 'var(--sp-gray-400)', flexShrink: 0 }} />
                              <span
                                style={{ color: 'var(--sp-gray-700)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
                                title={c.motif || ''}
                              >
                                {c.motif || 'Consultation médicale'}
                              </span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px' }}>
                              <User size={14} style={{ color: 'var(--sp-gray-400)', flexShrink: 0 }} />
                              <span style={{ color: 'var(--sp-gray-700)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {mName || <em style={{ color: 'var(--sp-gray-300)', fontStyle: 'italic' }}>Non affecté</em>}
                              </span>
                            </div>
                          </div>

                          {/* ── Actions ── */}
                          <div
                            style={{
                              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                              paddingTop: '14px', marginTop: '14px', borderTop: '1px solid var(--sp-gray-100)'
                            }}
                          >
                            {/* Bouton gauche : "Voir les X" ou "Continuer" pour att. médecin */}
                            {c.statut === 'en_attente_medecin' && user?.role === 'medecin' ? (
                              c.medecin_id === user.medecin_id ? (
                                <Link
                                  to={`/consultation/nouvelle?reprendre=${c.id}`}
                                  className="sp-btn sp-btn-outline"
                                  style={{ padding: '6px 14px', fontSize: '12px', height: '34px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '6px', textDecoration: 'none' }}
                                >
                                  <Play size={14} /> Continuer
                                </Link>
                              ) : (
                                <button
                                  className="sp-btn sp-btn-outline"
                                  style={{ padding: '6px 14px', fontSize: '12px', height: '34px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '6px', opacity: 0.45, cursor: 'not-allowed' }}
                                  onClick={() => showToast(`Ce dossier est réservé au Dr. ${getMedecinName(c.medecin_id)}`, 'info')}
                                >
                                  <Play size={14} /> Continuer
                                </button>
                              )
                            ) : c.statut === 'en attente' && isInfirmier ? (
                                <Link
                                  to={`/consultation/nouvelle?reprendre=${c.id}`}
                                  className="sp-btn sp-btn-outline"
                                  style={{ padding: '6px 14px', fontSize: '12px', height: '34px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '6px', textDecoration: 'none' }}
                                >
                                  <Play size={14} /> Continuer
                                </Link>
                            ) : (!c.statut || c.statut === 'en_attente_medecin') && isInfirmier ? (
                                <Link
                                  to={`/consultation/nouvelle?reprendre=${c.id}`}
                                  className="sp-btn sp-btn-outline sp-actions-hover"
                                  title="Modifier les symptômes ou les informations du patient, puis renvoyer au médecin"
                                  style={{ padding: '6px 14px', fontSize: '12px', height: '34px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '6px', textDecoration: 'none' }}
                                >
                                  <Edit2 size={14} /> Modifier
                                </Link>
                            ) : count > 1 ? (
                              <button
                                className="sp-btn sp-btn-outline"
                                style={{ padding: '6px 14px', fontSize: '12px', height: '34px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}
                                onClick={() => setConsultListModal({ patientName: c.nom_patient || '', consultations: groupConsults })}
                              >
                                <List size={14} />
                                Voir les {count}
                              </button>
                            ) : (
                              <div />
                            )}

                            {/* Bouton Dossier */}
                            {!isInfirmier && (
                              c.patient_id ? (
                                <Link
                                  to={`/dossier-patient/${c.patient_id}`}
                                  className="sp-btn sp-btn-primary"
                                  style={{
                                    padding: '6px 16px', fontSize: '12px', height: '34px', borderRadius: '8px',
                                    textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px'
                                  }}
                                >
                                  <Clipboard size={14} />
                                  Dossier
                                </Link>
                              ) : (
                                <button
                                  className="sp-btn sp-btn-primary"
                                  style={{ padding: '6px 16px', fontSize: '12px', height: '34px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}
                                  onClick={() => openForm(c)}
                                >
                                  <Clipboard size={14} />
                                  Dossier
                                </button>
                              )
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* ══════════════════════════════════════════════════════════════
                VUE TABLEAU
            ══════════════════════════════════════════════════════════════ */}
            {view === 'table' && (
              <div>
                <div className="sp-table-wrap">
                  <table className="sp-table">
                    <thead>
                      <tr>
                        <th>#ID</th>
                        <th>ID Patient</th>
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
                            <td style={{ fontSize: '12px', fontWeight: 600, color: 'var(--sp-primary)' }}>{c.patient_id ? `#${String(c.patient_id).padStart(4, '0')}` : '—'}</td>
                            <td><div style={{ fontWeight: 600 }}>{c.nom_patient}</div></td>
                            <td>{formatDate(c.date_heure || c.date)}</td>
                            <td style={{ maxWidth: '200px' }}>
                              <span title={c.motif || ''}>{(c.motif || '').length > 40 ? (c.motif || '').substring(0, 40) + '…' : (c.motif || '')}</span>
                            </td>
                            <td>{mName ? mName : <span style={{ color: 'var(--sp-gray-300)' }}>—</span>}</td>
                            <td>
                              <span className={`sp-badge ${cls}`}>
                                {(!c.statut || c.statut === 'en_attente_medecin') ? 'att. médecin' : c.statut}
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
                                    <button onClick={() => showToast(`Réservé au Dr. ${getMedecinName(c.medecin_id)}`, 'info')} className="sp-btn sp-btn-outline sp-btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '4px', opacity: 0.7 }}>
                                      <Play size={14} /> Continuer
                                    </button>
                                  )
                                )}
                                {c.statut === 'en attente' && !isInfirmier && (
                                  <>
                                    <button className="sp-btn sp-btn-outline sp-btn-sm" onClick={() => { setCurrentConsultId(c.id); setSelectedMedecinId(c.medecin_id?.toString() || ''); setAffectModalOpen(true); }}>
                                      <UserPlus size={14} /> {c.medecin_id ? 'Réaffecter' : 'Affecter'}
                                    </button>
                                    {!c.medecin_id ? (
                                      <button onClick={() => setWarningModalOpen(true)} className="sp-btn sp-btn-warning sp-btn-sm" style={{ opacity: 0.5, cursor: 'not-allowed' }}>
                                        <Play size={14} />
                                      </button>
                                    ) : (
                                      <button onClick={() => handleStatutChange(c.id, 'en cours')} className="sp-btn sp-btn-warning sp-btn-sm">
                                        <Play size={14} />
                                      </button>
                                    )}
                                  </>
                                )}
                                {c.statut === 'en attente' && isInfirmier && (
                                  <Link to={`/consultation/nouvelle?reprendre=${c.id}`} className="sp-btn sp-btn-primary sp-btn-sm" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    <Play size={14} /> Continuer
                                  </Link>
                                )}
                                {(!c.statut || c.statut === 'en_attente_medecin') && isInfirmier && (
                                  <Link to={`/consultation/nouvelle?reprendre=${c.id}`} className="sp-btn sp-btn-outline sp-btn-sm" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }} title="Modifier les symptômes ou les informations du patient, puis renvoyer au médecin">
                                    <Edit2 size={14} /> Modifier
                                  </Link>
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

          {/* ══════════════════════════════════════════════════════════════
              MODAL — Liste des consultations d'un patient
          ══════════════════════════════════════════════════════════════ */}
          {consultListModal && (
            <div className="sp-modal-overlay open">
              <div className="sp-modal" style={{ maxWidth: '520px', padding: 0, overflow: 'hidden' }}>
                <div className="sp-card-header" style={{ padding: '18px 24px' }}>
                  <div className="sp-card-title">
                    <Users size={18} />
                    <span>{consultListModal.patientName}</span>
                  </div>
                  <button className="sp-btn sp-btn-ghost sp-btn-sm" style={{ padding: '4px' }} onClick={() => setConsultListModal(null)}>
                    <X size={18} />
                  </button>
                </div>
                <div style={{ padding: '16px 24px 24px', display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '400px', overflowY: 'auto' }}>
                  {consultListModal.consultations.map((c, idx) => {
                    const mName = getMedecinName(c.medecin_id);
                    const { cls, text: statutText } = getStatutBadge(c.statut || '');
                    const isEnAttente = c.statut === 'en attente' || c.statut === 'en_attente_medecin';
                    const isHovered = hoveredConsultId === c.id;
                    return (
                      <div
                        key={c.id}
                        onMouseEnter={() => setHoveredConsultId(c.id)}
                        onMouseLeave={() => setHoveredConsultId(null)}
                        style={{ position: 'relative', background: isHovered ? '#fff' : 'var(--sp-gray-50)', borderRadius: '10px', padding: '14px 16px', border: `1px solid ${isHovered ? 'var(--sp-primary-200, #C7D2FE)' : 'var(--sp-gray-100)'}`, transition: 'background 0.15s, border-color 0.15s' }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                          <span style={{ fontSize: '12px', color: 'var(--sp-gray-400)', fontWeight: 600 }}>
                            #{String(c.id).padStart(4, '0')} — Consultation {idx + 1}
                          </span>
                          <span className={`sp-badge ${cls}`} style={{ fontSize: '11px' }}>{statutText}</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', fontSize: '13px', color: 'var(--sp-gray-700)' }}>
                            <Calendar size={13} style={{ color: 'var(--sp-gray-400)', flexShrink: 0 }} />
                            {formatDate(c.date_heure || c.date)}
                          </div>
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', fontSize: '13px', color: 'var(--sp-gray-700)' }}>
                            <FileText size={13} style={{ color: 'var(--sp-gray-400)', flexShrink: 0 }} />
                            {c.motif || 'Consultation médicale'}
                          </div>
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', fontSize: '13px', color: 'var(--sp-gray-700)' }}>
                            <User size={13} style={{ color: 'var(--sp-gray-400)', flexShrink: 0 }} />
                            {mName || <em style={{ color: 'var(--sp-gray-300)' }}>Non affecté</em>}
                          </div>
                        </div>
                        {isEnAttente && isHovered && (
                          <Link
                            to={`/consultation/nouvelle?reprendre=${c.id}`}
                            className="sp-btn sp-btn-primary"
                            style={{ position: 'absolute', bottom: '10px', right: '12px', padding: '4px 12px', fontSize: '12px', height: '28px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '6px', textDecoration: 'none' }}
                            onClick={() => setConsultListModal(null)}
                          >
                            <Play size={13} /> Reprendre
                          </Link>
                        )}
                      </div>
                    );
                  })}
                </div>
                <div style={{ padding: '14px 24px', borderTop: '1px solid var(--sp-gray-100)', display: 'flex', justifyContent: 'flex-end' }}>
                  <button className="sp-btn sp-btn-ghost" onClick={() => setConsultListModal(null)}>Fermer</button>
                </div>
              </div>
            </div>
          )}

          {/* ── Modal Affectation ── */}
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
                      <select className="sp-form-select" required value={selectedMedecinId} onChange={e => setSelectedMedecinId(e.target.value)}>
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

          {/* ── Modal Avertissement ── */}
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

          {/* ── Modal Suppression ── */}
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

          {/* ── Modal Édition ── */}
          {formModalOpen && (
            <div className="sp-modal-overlay open">
              <div className="sp-modal" style={{ maxWidth: '600px', padding: 0, overflow: 'hidden' }}>
                <div className="sp-card-header" style={{ padding: '20px 24px', borderBottom: '1px solid var(--sp-gray-100)' }}>
                  <div className="sp-card-title">
                    <Edit2 size={20} />
                    Modifier la consultation
                  </div>
                  <button className="sp-btn sp-btn-ghost sp-btn-sm" style={{ padding: '4px' }} onClick={() => setFormModalOpen(false)}>
                    <X size={18} />
                  </button>
                </div>
                <form onSubmit={handleSaveConsultation} style={{ padding: '24px' }}>
                  <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                    <label className="sp-form-label">Nom du patient <span style={{ color: '#EF4444' }}>*</span></label>
                    <div className="sp-input-icon-wrap">
                      <User size={18} className="sp-input-icon" />
                      <input type="text" className="sp-form-input" required
                        placeholder="Nom complet du patient"
                        value={formData.nom_patient || ''}
                        readOnly={isInfirmier}
                        onChange={e => { if (!isInfirmier) setFormData({ ...formData, nom_patient: e.target.value }); }}
                        style={{ paddingLeft: '40px', ...(isInfirmier ? { background: '#F3F4F6', cursor: 'not-allowed', color: '#6B7280', borderColor: '#E5E7EB' } : {}) }} />
                    </div>
                  </div>
                  <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                    <label className="sp-form-label">Date et Heure <span style={{ color: '#EF4444' }}>*</span></label>
                    <div className="sp-input-icon-wrap">
                      <Calendar size={18} className="sp-input-icon" />
                      <input type="datetime-local" className="sp-form-input" style={{ paddingLeft: '40px' }} required
                        max={new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16)}
                        value={(formData.date_heure || '').slice(0, 16)}
                        onChange={e => setFormData({ ...formData, date_heure: e.target.value })} />
                    </div>
                  </div>
                  <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                    <label className="sp-form-label">Motif <span style={{ color: '#EF4444' }}>*</span></label>
                    <textarea className="sp-form-textarea" required placeholder="Motif de la consultation..." rows={4}
                      value={formData.motif || ''}
                      onChange={e => setFormData({ ...formData, motif: e.target.value })} />
                  </div>
                  {formData.id && (
                    <>
                      <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                        <label className="sp-form-label">Médecin</label>
                        <div className="sp-input-icon-wrap">
                          <UserCheck size={18} className="sp-input-icon" />
                          <select className="sp-form-select" style={{ paddingLeft: '40px' }}
                            value={formData.medecin_id || ''}
                            onChange={e => setFormData({ ...formData, medecin_id: e.target.value ? Number(e.target.value) : undefined })}>
                            <option value="">-- Non affecté --</option>
                            {medecins.map(m => (
                              <option key={m.medecin_id} value={m.medecin_id}>Dr. {m.prenoms} {m.nom}{m.specialite ? ` — ${m.specialite}` : ''}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      <div className="sp-form-group" style={{ marginBottom: '18px' }}>
                        <label className="sp-form-label">Statut</label>
                        <select className="sp-form-select"
                          value={formData.statut || 'en attente'}
                          onChange={e => setFormData({ ...formData, statut: e.target.value as Consultation['statut'] })}>
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
                      {formLoading ? 'Enregistrement...' : 'Enregistrer'}
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
