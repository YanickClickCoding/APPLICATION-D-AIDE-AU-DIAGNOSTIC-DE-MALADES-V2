import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, User, Phone, Mail, Calendar, Activity, AlertCircle, PlusCircle, Edit2, Trash2, Grid, List, X, Save, Clipboard } from 'lucide-react';
import { patientsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';

interface Patient {
  patient_id: number;
  nom: string;
  prenoms: string;
  date_naissance: string;
  sexe: 'M' | 'F';
  telephone?: string;
  email?: string;
  groupe_sanguin?: string;
  created_at: string;
}

const MesPatients = () => {
  const { isAdmin } = useAuth();
  const { showToast } = useToast();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [filtered, setFiltered] = useState<Patient[]>([]);
  const [search, setSearch] = useState('');
  const [sexFilter, setSexFilter] = useState<'all' | 'M' | 'F'>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<'grid' | 'table'>(() => (localStorage.getItem('sp_patients_view') as 'grid' | 'table') || 'grid');

  const [formModalOpen, setFormModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [currentPatient, setCurrentPatient] = useState<Partial<Patient> | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await patientsAPI.list(0, 200);
      setPatients(data);
      setFiltered(data);
    } catch (err: any) {
      setError(err.message || 'Impossible de charger les patients');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPatients(); }, []);

  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(
      patients.filter(p =>
        (sexFilter === 'all' || p.sexe === sexFilter) &&
        (p.nom.toLowerCase().includes(q) ||
          p.prenoms.toLowerCase().includes(q) ||
          (p.telephone ?? '').includes(q) ||
          (p.email ?? '').toLowerCase().includes(q))
      )
    );
  }, [search, sexFilter, patients]);

  const handleViewChange = (v: 'grid' | 'table') => {
    setView(v);
    localStorage.setItem('sp_patients_view', v);
  };

  const handleSavePatient = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentPatient) return;
    setFormLoading(true);
    try {
      if (currentPatient.patient_id) {
        await patientsAPI.update(currentPatient.patient_id, currentPatient);
        showToast('Patient mis à jour avec succès', 'success');
      } else {
        await patientsAPI.create(currentPatient as Omit<Patient, 'patient_id' | 'created_at'>);
        showToast('Patient créé avec succès', 'success');
      }
      setFormModalOpen(false);
      fetchPatients();
    } catch (err: any) {
      showToast(err.detail || 'Erreur lors de l\'enregistrement', 'error');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeletePatient = async () => {
    if (!currentPatient?.patient_id) return;
    setDeleteLoading(true);
    try {
      await patientsAPI.delete(currentPatient.patient_id);
      showToast('Patient supprimé avec succès', 'success');
      setDeleteModalOpen(false);
      fetchPatients();
    } catch (err: any) {
      showToast(err.detail || 'Erreur lors de la suppression', 'error');
    } finally {
      setDeleteLoading(false);
    }
  };

  const openForm = (patient?: Patient) => {
    setCurrentPatient(patient || { nom: '', prenoms: '', sexe: 'M', date_naissance: '', telephone: '', email: '', groupe_sanguin: '' });
    setFormModalOpen(true);
  };

  const openDelete = (patient: Patient) => {
    setCurrentPatient(patient);
    setDeleteModalOpen(true);
  };

  const calculateAge = (birthDate: string) => {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
    return age;
  };

  const getInitials = (nom: string, prenoms: string) =>
    `${prenoms.charAt(0)}${nom.charAt(0)}`.toUpperCase();

  const bloodGroupColor = (bg?: string) => {
    if (!bg) return { bg: '#F3F4F6', text: '#6B7280' };
    if (bg.includes('AB')) return { bg: '#EDE9FE', text: '#7C3AED' };
    if (bg.includes('A')) return { bg: '#FEE2E2', text: '#DC2626' };
    if (bg.includes('B')) return { bg: '#DBEAFE', text: '#2563EB' };
    return { bg: '#D1FAE5', text: '#065F46' };
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', flexDirection: 'column', gap: '16px' }}>
        <Activity size={48} style={{ animation: 'spin 1s linear infinite', color: '#4F46E5' }} />
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
        <p style={{ color: '#6B7280' }}>Chargement des patients...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <AlertCircle size={48} style={{ color: '#EF4444', margin: '0 auto 16px' }} />
        <h3 style={{ color: '#1F2937', marginBottom: '8px' }}>Erreur de chargement</h3>
        <p style={{ color: '#6B7280', marginBottom: '16px' }}>{error}</p>
        <button onClick={fetchPatients} className="sp-btn sp-btn-primary">Réessayer</button>
      </div>
    );
  }

  const filterOptions = [
    { key: 'all' as const, label: 'Tous', count: patients.length },
    { key: 'M' as const, label: 'Hommes', count: patients.filter(p => p.sexe === 'M').length },
    { key: 'F' as const, label: 'Femmes', count: patients.filter(p => p.sexe === 'F').length },
  ];

  return (
    <>
      {/* Page Header */}
      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Mes Patients</h1>
          <p className="sp-page-subtitle">{patients.length} patient{patients.length > 1 ? 's' : ''} enregistré{patients.length > 1 ? 's' : ''}</p>
        </div>
        {isAdmin && (
          <button className="sp-btn sp-btn-primary" onClick={() => openForm()}>
            <PlusCircle size={18} />
            <span>Nouveau patient</span>
          </button>
        )}
      </div>

      {/* Main Panel */}
      <div className="sp-card sp-fade-in" style={{ padding: 0, overflow: 'hidden' }}>

        {/* Toolbar */}
        <div style={{
          padding: '14px 20px',
          borderBottom: '1px solid #F3F4F6',
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          flexWrap: 'wrap',
        }}>
          <span style={{ fontSize: '15px', fontWeight: 700, color: '#1F2937', whiteSpace: 'nowrap', flexShrink: 0 }}>
            Liste des patients
          </span>

          {/* Filter pills */}
          <div style={{ display: 'flex', gap: '6px', flex: 1, flexWrap: 'wrap' }}>
            {filterOptions.map(({ key, label, count }) => {
              const isActive = sexFilter === key;
              return (
                <button
                  key={key}
                  onClick={() => setSexFilter(key)}
                  style={{
                    padding: '4px 14px',
                    borderRadius: '20px',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '13px',
                    fontWeight: 600,
                    background: isActive ? '#0B2545' : 'transparent',
                    color: isActive ? '#fff' : '#6B7280',
                    transition: 'all 0.2s',
                  }}
                >
                  {label} ({count})
                </button>
              );
            })}
          </div>

          {/* Search + View toggle */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ position: 'relative' }}>
              <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
              <input
                type="text"
                placeholder="Rechercher patient, motif..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="sp-input"
                style={{ paddingLeft: '32px', height: '36px', width: '220px', fontSize: '13px' }}
              />
            </div>
            <div className="sp-view-toggle">
              <button className={`sp-view-btn ${view === 'grid' ? 'active' : ''}`} onClick={() => handleViewChange('grid')} title="Vue cartes">
                <Grid size={16} />
              </button>
              <button className={`sp-view-btn ${view === 'table' ? 'active' : ''}`} onClick={() => handleViewChange('table')} title="Vue tableau">
                <List size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        {filtered.length === 0 ? (
          <div style={{ padding: '60px', textAlign: 'center' }}>
            <User size={48} style={{ color: '#D1D5DB', margin: '0 auto 16px' }} />
            <h3 style={{ color: '#1F2937', marginBottom: '8px' }}>Aucun patient trouvé</h3>
            <p style={{ color: '#6B7280' }}>
              {search ? `Aucun résultat pour "${search}"` : 'Aucun patient enregistré dans le système.'}
            </p>
          </div>
        ) : view === 'grid' ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px', padding: '20px', background: '#EEF2F7' }}>
            {filtered.map(patient => (
              <div
                key={patient.patient_id}
                className="sp-item-card mp-patient-card"
                style={{ padding: '20px', display: 'flex', flexDirection: 'column', minHeight: '260px' }}
              >
                {/* Admin actions */}
                {isAdmin && (
                  <div className="mp-actions-overlay" style={{
                    position: 'absolute', top: '12px', right: '12px',
                    display: 'flex', gap: '6px',
                    opacity: 0, transform: 'translateY(-6px)', transition: 'all 0.2s ease',
                  }}>
                    <button onClick={() => openForm(patient)} className="sp-btn sp-btn-ghost sp-btn-sm" style={{ background: '#fff', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', padding: '6px' }} title="Modifier">
                      <Edit2 size={14} style={{ color: '#4F46E5' }} />
                    </button>
                    <button onClick={() => openDelete(patient)} className="sp-btn sp-btn-ghost sp-btn-sm" style={{ background: '#fff', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', padding: '6px' }} title="Supprimer">
                      <Trash2 size={14} style={{ color: '#EF4444' }} />
                    </button>
                  </div>
                )}

                {/* Avatar + Name + Badges */}
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', marginBottom: '14px' }}>
                  <div
                    className="sp-item-avatar"
                    style={{ width: '46px', height: '46px', fontSize: '16px', borderRadius: '10px', flexShrink: 0 }}
                  >
                    {getInitials(patient.nom, patient.prenoms)}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <Link
                      to={`/dossier-patient/${patient.patient_id}`}
                      style={{
                        fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '15px',
                        color: 'var(--sp-primary)', textDecoration: 'none', display: 'block',
                        marginBottom: '5px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                      }}
                    >
                      {patient.prenoms} {patient.nom}
                    </Link>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <span style={{
                        padding: '2px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 600,
                        background: patient.sexe === 'M' ? '#DBEAFE' : '#FCE7F3',
                        color: patient.sexe === 'M' ? '#1D4ED8' : '#BE185D',
                      }}>
                        {patient.sexe === 'M' ? '♂ Masculin' : '♀ Féminin'}
                      </span>
                      {patient.groupe_sanguin && (
                        <span style={{
                          padding: '2px 8px', borderRadius: '20px', fontSize: '11px', fontWeight: 700,
                          background: bloodGroupColor(patient.groupe_sanguin).bg,
                          color: bloodGroupColor(patient.groupe_sanguin).text,
                        }}>
                          {patient.groupe_sanguin}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Info label */}
                <div style={{ fontSize: '12.5px', color: 'var(--sp-gray-500)', marginBottom: '10px' }}>
                  Informations patient :
                </div>

                {/* Info rows — flex:1 pour pousser les boutons en bas */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px' }}>
                    <Calendar size={14} style={{ color: 'var(--sp-gray-400)', flexShrink: 0 }} />
                    <span style={{ color: 'var(--sp-gray-700)' }}>{new Date(patient.date_naissance).toLocaleDateString('fr-FR')} · {calculateAge(patient.date_naissance)} ans</span>
                  </div>
                  {patient.telephone && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px' }}>
                      <Phone size={14} style={{ color: 'var(--sp-gray-400)', flexShrink: 0 }} />
                      <span style={{ color: 'var(--sp-gray-700)' }}>{patient.telephone}</span>
                    </div>
                  )}
                  {patient.email && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px' }}>
                      <Mail size={14} style={{ color: 'var(--sp-gray-400)', flexShrink: 0 }} />
                      <span style={{ color: 'var(--sp-gray-700)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{patient.email}</span>
                    </div>
                  )}
                </div>

                {/* Actions — toujours en bas grâce à flex:1 sur la section infos */}
                <div style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  paddingTop: '14px', marginTop: '14px', borderTop: '1px solid var(--sp-gray-100)',
                }}>
                  <Link
                    to={`/consultation/nouvelle?patientId=${patient.patient_id}`}
                    className="sp-btn sp-btn-outline"
                    style={{ padding: '6px 14px', fontSize: '12px', height: '34px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '6px', textDecoration: 'none' }}
                  >
                    <Calendar size={14} /> Consulter
                  </Link>
                  <Link
                    to={`/dossier-patient/${patient.patient_id}`}
                    className="sp-btn sp-btn-primary"
                    style={{ padding: '6px 16px', fontSize: '12px', height: '34px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '6px', textDecoration: 'none' }}
                  >
                    <Clipboard size={14} /> Dossier
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Table View */
          <div style={{ overflowX: 'auto' }}>
            <table className="sp-table" style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th>Patient</th>
                  <th>Sexe</th>
                  <th>Âge</th>
                  <th>Téléphone</th>
                  <th>Groupe</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(patient => (
                  <tr key={patient.patient_id} className="sp-table-row-hover">
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Link
                          to={`/dossier-patient/${patient.patient_id}`}
                          style={{
                            width: '32px', height: '32px', borderRadius: '8px', fontSize: '12px', fontWeight: 700, color: '#fff',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            background: patient.sexe === 'M' ? '#1a6b8a' : '#b83280',
                            textDecoration: 'none', flexShrink: 0,
                          }}
                        >
                          {getInitials(patient.nom, patient.prenoms)}
                        </Link>
                        <div>
                          <Link
                            to={`/dossier-patient/${patient.patient_id}`}
                            style={{ fontWeight: 600, color: '#1F2937', textDecoration: 'none', display: 'block' }}
                            onMouseEnter={e => { e.currentTarget.style.color = '#4F46E5'; }}
                            onMouseLeave={e => { e.currentTarget.style.color = '#1F2937'; }}
                          >
                            {patient.prenoms} {patient.nom}
                          </Link>
                          <div style={{ fontSize: '11px', color: '#9CA3AF' }}>#{patient.patient_id.toString().padStart(4, '0')}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span style={{
                        padding: '2px 8px', borderRadius: '20px', fontSize: '11px', fontWeight: 600,
                        background: patient.sexe === 'M' ? '#DBEAFE' : '#FCE7F3',
                        color: patient.sexe === 'M' ? '#1D4ED8' : '#BE185D',
                      }}>
                        {patient.sexe === 'M' ? '♂ Masc.' : '♀ Fém.'}
                      </span>
                    </td>
                    <td style={{ fontSize: '13px', color: '#374151' }}>{calculateAge(patient.date_naissance)} ans</td>
                    <td style={{ fontSize: '13px', color: '#374151' }}>{patient.telephone || '—'}</td>
                    <td>
                      {patient.groupe_sanguin ? (
                        <span style={{
                          padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700,
                          background: bloodGroupColor(patient.groupe_sanguin).bg,
                          color: bloodGroupColor(patient.groupe_sanguin).text,
                        }}>
                          {patient.groupe_sanguin}
                        </span>
                      ) : '—'}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '4px', justifyContent: 'flex-end' }}>
                        <Link to={`/dossier-patient/${patient.patient_id}`} className="sp-btn sp-btn-ghost sp-btn-sm" title="Voir dossier">
                          <Clipboard size={14} />
                        </Link>
                        {isAdmin && (
                          <>
                            <button onClick={() => openForm(patient)} className="sp-btn sp-btn-ghost sp-btn-sm" title="Modifier">
                              <Edit2 size={14} style={{ color: '#4F46E5' }} />
                            </button>
                            <button onClick={() => openDelete(patient)} className="sp-btn sp-btn-ghost sp-btn-sm" title="Supprimer">
                              <Trash2 size={14} style={{ color: '#EF4444' }} />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <style>{`
        .mp-patient-card:hover .mp-actions-overlay {
          opacity: 1 !important;
          transform: translateY(0) !important;
        }
        .sp-table-row-hover:hover {
          background-color: #F9FAFB;
        }
      `}</style>

      {/* Modal Formulaire */}
      {formModalOpen && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ maxWidth: '600px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937' }}>
                {currentPatient?.patient_id ? 'Modifier le patient' : 'Nouveau patient'}
              </h2>
              <button onClick={() => setFormModalOpen(false)} className="sp-btn sp-btn-ghost" style={{ padding: '4px' }}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleSavePatient}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div className="sp-form-group">
                  <label className="sp-form-label">Nom <span style={{ color: '#EF4444' }}>*</span></label>
                  <input type="text" className="sp-form-input" required value={currentPatient?.nom || ''} onChange={e => setCurrentPatient({ ...currentPatient, nom: e.target.value })} />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">Prénoms <span style={{ color: '#EF4444' }}>*</span></label>
                  <input type="text" className="sp-form-input" required value={currentPatient?.prenoms || ''} onChange={e => setCurrentPatient({ ...currentPatient, prenoms: e.target.value })} />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">Sexe <span style={{ color: '#EF4444' }}>*</span></label>
                  <select className="sp-form-select" required value={currentPatient?.sexe || 'M'} onChange={e => setCurrentPatient({ ...currentPatient, sexe: e.target.value as 'M' | 'F' })}>
                    <option value="M">♂ Masculin</option>
                    <option value="F">♀ Féminin</option>
                  </select>
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">Date de naissance <span style={{ color: '#EF4444' }}>*</span></label>
                  <input type="date" className="sp-form-input" required value={currentPatient?.date_naissance || ''} onChange={e => setCurrentPatient({ ...currentPatient, date_naissance: e.target.value })} />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">Téléphone</label>
                  <input type="text" className="sp-form-input" value={currentPatient?.telephone || ''} onChange={e => setCurrentPatient({ ...currentPatient, telephone: e.target.value })} />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">Groupe Sanguin</label>
                  <select className="sp-form-select" value={currentPatient?.groupe_sanguin || ''} onChange={e => setCurrentPatient({ ...currentPatient, groupe_sanguin: e.target.value })}>
                    <option value="">Sélectionner...</option>
                    <option value="A+">A+</option><option value="A-">A-</option>
                    <option value="B+">B+</option><option value="B-">B-</option>
                    <option value="AB+">AB+</option><option value="AB-">AB-</option>
                    <option value="O+">O+</option><option value="O-">O-</option>
                  </select>
                </div>
              </div>
              <div className="sp-form-group" style={{ marginTop: '16px' }}>
                <label className="sp-form-label">Email</label>
                <input type="email" className="sp-form-input" value={currentPatient?.email || ''} onChange={e => setCurrentPatient({ ...currentPatient, email: e.target.value })} />
              </div>
              <div style={{ display: 'flex', gap: '12px', marginTop: '24px', justifyContent: 'flex-end' }}>
                <button type="button" onClick={() => setFormModalOpen(false)} className="sp-btn sp-btn-ghost">Annuler</button>
                <button type="submit" className="sp-btn sp-btn-primary" disabled={formLoading}>
                  {formLoading ? 'Enregistrement...' : <><Save size={18} /> Enregistrer</>}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Suppression */}
      {deleteModalOpen && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ maxWidth: '400px', textAlign: 'center' }}>
            <div style={{ width: '60px', height: '60px', borderRadius: '50%', background: '#FEE2E2', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
              <Trash2 size={30} style={{ color: '#EF4444' }} />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#1F2937', marginBottom: '8px' }}>Supprimer le patient ?</h3>
            <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '24px' }}>
              Êtes-vous sûr de vouloir supprimer <strong>{currentPatient?.prenoms} {currentPatient?.nom}</strong> ? Cette action est irréversible.
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button onClick={() => setDeleteModalOpen(false)} className="sp-btn sp-btn-ghost">Annuler</button>
              <button onClick={handleDeletePatient} className="sp-btn sp-btn-danger" disabled={deleteLoading}>
                {deleteLoading ? 'Suppression...' : 'Supprimer définitivement'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default MesPatients;
