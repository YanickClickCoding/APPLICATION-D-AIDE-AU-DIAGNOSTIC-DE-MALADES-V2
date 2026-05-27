import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Calendar, Activity, FileText, Pill, AlertCircle, User, Phone, Mail, MapPin, Cake, Edit, Brain, CheckCircle, XCircle, Droplet, Printer, Download, Clipboard, Eye, ClipboardCheck, Save, Plus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import { patientsAPI, consultationsAPI } from '../services/api';
import { MedicalDisclaimerBanner } from '../components/MedicalDisclaimerBanner';

interface DossierMedicalInfo {
  dossier_id: number;
  numero_dossier: string;
  antecedents_familiaux?: string;
  antecedents_personnels?: string;
  allergies?: string;
}

interface Patient {
  patient_id: number;  // INT AUTO_INCREMENT
  nom: string;
  prenoms: string;
  date_naissance: string;
  sexe: string;
  telephone: string;
  email?: string;
  adresse?: string;
  groupe_sanguin?: string;
  dossier_medical?: DossierMedicalInfo;
}

interface DiagnosticInfo {
  nom_maladie: string;
  certitude: number;
  statut: string;
  description?: string;
  date_validation?: string;
}

interface Consultation {
  consultation_id: number;
  date_heure: string;
  motif: string;
  statut: string;
  medecin_id?: number | null;
  medecin_nom?: string;
  diagnostic?: DiagnosticInfo | null;
}

const DossierPatient = () => {
  const { patientId } = useParams<{ patientId: string }>();
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const { showToast } = useToast();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredConsultId, setHoveredConsultId] = useState<number | null>(null);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editData, setEditData] = useState({ date_naissance: '', sexe: 'M' as 'M' | 'F', telephone: '', groupe_sanguin: '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user?.role === 'infirmier') {
      showToast("Accès refusé. Les infirmiers ne peuvent pas consulter le dossier médical.", "error");
      navigate('/consultations');
      return;
    }

    const fetchData = async () => {
      if (!token || !patientId) return;
      
      try {
        setLoading(true);
        // Récupérer les données du patient (patientId est un INT)
        const patientData = await patientsAPI.get(parseInt(patientId), token);
        setPatient(patientData);

        // Récupérer l'historique des consultations
        const consultationsData = await consultationsAPI.getByPatient(parseInt(patientId), token);
        setConsultations([...consultationsData].sort((a, b) =>
          new Date(b.date_heure ?? '').getTime() - new Date(a.date_heure ?? '').getTime()
        ));
        
        setError(null);
      } catch (err: any) {
        console.error('Erreur chargement dossier patient:', err);
        setError('Impossible de charger le dossier patient');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [patientId, token]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <Activity size={48} style={{ animation: 'spin 1s linear infinite', color: '#4F46E5' }} />
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error || !patient) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <AlertCircle size={48} style={{ color: '#EF4444', margin: '0 auto' }} />
        <h3 style={{ marginTop: '16px', color: '#1F2937' }}>Erreur</h3>
        <p style={{ color: '#6B7280', marginTop: '8px' }}>{error || 'Patient non trouvé'}</p>
        <Link to="/consultations" className="sp-btn sp-btn-primary" style={{ marginTop: '16px', display: 'inline-flex' }}>
          <ArrowLeft size={18} /> Retour aux consultations
        </Link>
      </div>
    );
  }

  const isIncomplete = !patient.date_naissance || patient.date_naissance.startsWith('1900-01-01');

  const calculateAge = (birthDate: string) => {
    if (!birthDate || birthDate.startsWith('1900-01-01')) return null;
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const handleCompleteForm = async () => {
    if (!editData.date_naissance) return;
    setSaving(true);
    try {
      await patientsAPI.update(patient.patient_id, {
        date_naissance: editData.date_naissance as any,
        sexe: editData.sexe,
        telephone: editData.telephone || undefined,
        groupe_sanguin: editData.groupe_sanguin || undefined,
      });
      setPatient({
        ...patient,
        date_naissance: editData.date_naissance,
        sexe: editData.sexe,
        telephone: editData.telephone,
        groupe_sanguin: editData.groupe_sanguin,
      });
      setShowEditForm(false);
    } catch {
      // silently ignored — the user will see the form still open
    } finally {
      setSaving(false);
    }
  };

  const getInitials = (nom: string, prenoms: string) => {
    return `${prenoms.charAt(0)}${nom.charAt(0)}`.toUpperCase();
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExportCSV = () => {
    if (!patient) return;
    
    // Header
    let csv = "DOSSIER MÉDICAL\n";
    csv += `Patient:;${patient.prenoms} ${patient.nom}\n`;
    csv += `ID:;${patient.patient_id}\n`;
    csv += `Né(e) le:;${new Date(patient.date_naissance).toLocaleDateString('fr-FR')}\n`;
    csv += `Sexe:;${patient.sexe}\n`;
    csv += `Téléphone:;${patient.telephone}\n`;
    csv += `\nHISTORIQUE DES CONSULTATIONS\n`;
    csv += "ID;Date;Motif;Médecin;Diagnostic;Statut\n";
    
    consultations.forEach(c => {
      const diag = c.diagnostic ? c.diagnostic.nom_maladie : "N/A";
      csv += `${c.consultation_id};${new Date(c.date_heure).toLocaleDateString('fr-FR')};"${c.motif.replace(/"/g, '""')}";${c.medecin_nom || 'N/A'};${diag};${c.statut}\n`;
    });
    
    const blob = new Blob(["\ufeff" + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `Dossier_${patient.nom}_${patient.prenoms}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Dossier Patient</h1>
          <p className="sp-page-subtitle">{consultations.length} visite(s)</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Link to="/consultations" className="sp-btn sp-btn-outline no-print">
            <ArrowLeft size={18} /> Retour
          </Link>
          {(user?.role === 'admin' || user?.role === 'medecin' || user?.role === 'infirmier') && (
            <Link
              to={`/consultation/nouvelle?patientId=${patientId}`}
              className="sp-btn sp-btn-primary no-print"
            >
              <Plus size={18} /> Nouvelle consultation
            </Link>
          )}
          {(user?.role === 'admin' || user?.role === 'medecin') && (
            <>
              <button className="sp-btn sp-btn-outline no-print" onClick={handlePrint}>
                <Printer size={18} /> Imprimer
              </button>
              <button className="sp-btn sp-btn-outline no-print" onClick={handleExportCSV}>
                <Download size={18} /> Exporter CSV
              </button>
            </>
          )}
          {user?.role === 'admin' && (
            <button className="sp-btn sp-btn-primary no-print">
              <Edit size={18} /> Modifier
            </button>
          )}
        </div>
      </div>

      <MedicalDisclaimerBanner compact />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' }} className="sp-fade-in">
        {/* Informations du patient */}
        <div className="sp-card">
          <div className="sp-card-header">
            <div className="sp-card-title">
              <User size={20} />
              Informations Patient
            </div>
          </div>
          <div style={{ padding: '20px' }}>
            {/* Avatar et nom */}
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
              <div style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontSize: '32px',
                fontWeight: 700,
                margin: '0 auto 12px'
              }}>
                {getInitials(patient.nom, patient.prenoms)}
              </div>
              <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#1F2937', marginBottom: '4px' }}>
                {patient.prenoms} {patient.nom}
              </h2>
              <p style={{ color: '#6B7280', fontSize: '14px' }}>
                #{patient.patient_id.toString().padStart(4, '0')}
              </p>
            </div>

            {/* Bandeau dossier incomplet */}
            {isIncomplete && (
              <div style={{ marginBottom: '20px', padding: '12px 16px', background: '#FFF7ED', borderRadius: '10px', border: '1px solid #FED7AA' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                  <AlertCircle size={16} style={{ color: '#EA580C', flexShrink: 0 }} />
                  <span style={{ fontSize: '13px', fontWeight: 700, color: '#9A3412' }}>Dossier à compléter</span>
                </div>
                <p style={{ fontSize: '12px', color: '#C2410C', margin: '0 0 10px' }}>
                  Ce dossier a été créé en urgence par le médecin. Veuillez compléter les informations du patient.
                </p>
                {!showEditForm ? (
                  <button
                    onClick={() => { setEditData({ date_naissance: '', sexe: patient.sexe as 'M' | 'F', telephone: patient.telephone || '', groupe_sanguin: patient.groupe_sanguin || '' }); setShowEditForm(true); }}
                    className="sp-btn sp-btn-outline"
                    style={{ fontSize: '12px', padding: '6px 14px', color: '#EA580C', borderColor: '#EA580C' }}
                  >
                    <ClipboardCheck size={13} /> Compléter le dossier
                  </button>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      <div>
                        <label style={{ fontSize: '11px', fontWeight: 600, color: '#6B7280', display: 'block', marginBottom: '4px' }}>Date de naissance *</label>
                        <input type="date" className="sp-form-input" style={{ fontSize: '13px' }} max={new Date().toISOString().split('T')[0]} value={editData.date_naissance} onChange={e => setEditData({ ...editData, date_naissance: e.target.value })} />
                      </div>
                      <div>
                        <label style={{ fontSize: '11px', fontWeight: 600, color: '#6B7280', display: 'block', marginBottom: '4px' }}>Sexe *</label>
                        <select className="sp-form-select" style={{ fontSize: '13px' }} value={editData.sexe} onChange={e => setEditData({ ...editData, sexe: e.target.value as 'M' | 'F' })}>
                          <option value="M">♂ Masculin</option>
                          <option value="F">♀ Féminin</option>
                        </select>
                      </div>
                      <div>
                        <label style={{ fontSize: '11px', fontWeight: 600, color: '#6B7280', display: 'block', marginBottom: '4px' }}>Téléphone</label>
                        <input type="tel" className="sp-form-input" style={{ fontSize: '13px' }} value={editData.telephone} onChange={e => setEditData({ ...editData, telephone: e.target.value })} placeholder="Ex: +229 90000000" />
                      </div>
                      <div>
                        <label style={{ fontSize: '11px', fontWeight: 600, color: '#6B7280', display: 'block', marginBottom: '4px' }}>Groupe sanguin</label>
                        <select className="sp-form-select" style={{ fontSize: '13px' }} value={editData.groupe_sanguin} onChange={e => setEditData({ ...editData, groupe_sanguin: e.target.value })}>
                          <option value="">—</option>
                          {['A+','A-','B+','B-','AB+','AB-','O+','O-'].map(g => <option key={g} value={g}>{g}</option>)}
                        </select>
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button onClick={handleCompleteForm} disabled={saving || !editData.date_naissance} className="sp-btn sp-btn-primary" style={{ fontSize: '12px', padding: '6px 14px' }}>
                        {saving ? 'Enregistrement...' : <><Save size={13} /> Enregistrer</>}
                      </button>
                      <button onClick={() => setShowEditForm(false)} className="sp-btn sp-btn-outline" style={{ fontSize: '12px', padding: '6px 14px' }}>Annuler</button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Détails */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#6B7280', fontSize: '12px', marginBottom: '4px' }}>
                  <Cake size={14} />
                  <span>Date de naissance</span>
                </div>
                {isIncomplete ? (
                  <div style={{ fontSize: '13px', color: '#EA580C', fontStyle: 'italic' }}>Non renseignée</div>
                ) : (
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#1F2937' }}>
                    {new Date(patient.date_naissance).toLocaleDateString('fr-FR')} ({calculateAge(patient.date_naissance)} ans)
                  </div>
                )}
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#6B7280', fontSize: '12px', marginBottom: '4px' }}>
                  <User size={14} />
                  <span>Sexe</span>
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#1F2937' }}>
                  {patient.sexe === 'M' ? '♂ Masculin' : '♀ Féminin'}
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#6B7280', fontSize: '12px', marginBottom: '4px' }}>
                  <Phone size={14} />
                  <span>Téléphone</span>
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#1F2937' }}>
                  {patient.telephone}
                </div>
              </div>

              {patient.email && (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#6B7280', fontSize: '12px', marginBottom: '4px' }}>
                    <Mail size={14} />
                    <span>Email</span>
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#1F2937' }}>
                    {patient.email}
                  </div>
                </div>
              )}

              {patient.adresse && (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#6B7280', fontSize: '12px', marginBottom: '4px' }}>
                    <MapPin size={14} />
                    <span>Adresse</span>
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#1F2937' }}>
                    {patient.adresse}
                  </div>
                </div>
              )}

              {patient.groupe_sanguin && (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#6B7280', fontSize: '12px', marginBottom: '4px' }}>
                    <Activity size={14} />
                    <span>Groupe sanguin</span>
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#1F2937' }}>
                    {patient.groupe_sanguin}
                  </div>
                </div>
              )}
            </div>

            {/* Allergies */}
            {patient.dossier_medical?.allergies && (
              <div style={{ marginTop: '24px', padding: '12px', background: '#FEF3C7', borderRadius: '8px', border: '1px solid #FCD34D' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#92400E', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>
                  <AlertCircle size={14} />
                  <span>ALLERGIES</span>
                </div>
                <div style={{ fontSize: '13px', color: '#78350F' }}>
                  {patient.dossier_medical.allergies}
                </div>
              </div>
            )}

            {/* Antécédents */}
            {(patient.dossier_medical?.antecedents_personnels || patient.dossier_medical?.antecedents_familiaux) && (
              <div style={{ marginTop: '16px', padding: '12px', background: '#DBEAFE', borderRadius: '8px', border: '1px solid #93C5FD' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#1E40AF', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>
                  <FileText size={14} />
                  <span>ANTÉCÉDENTS MÉDICAUX</span>
                </div>
                {patient.dossier_medical?.antecedents_personnels && (
                  <div style={{ fontSize: '13px', color: '#1E3A8A', marginBottom: '4px' }}>
                    <strong>Personnels : </strong>{patient.dossier_medical.antecedents_personnels}
                  </div>
                )}
                {patient.dossier_medical?.antecedents_familiaux && (
                  <div style={{ fontSize: '13px', color: '#1E3A8A' }}>
                    <strong>Familiaux : </strong>{patient.dossier_medical.antecedents_familiaux}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Historique des consultations */}
        <div className="sp-card">
          <div className="sp-card-header">
            <div className="sp-card-title">
              <Calendar size={20} />
              Historique des visites
            </div>
          </div>
          <div style={{ padding: 0 }}>
            {consultations.length === 0 ? (
              <div style={{ padding: '40px', textAlign: 'center' }}>
                <Calendar size={48} style={{ color: '#D1D5DB', margin: '0 auto 16px' }} />
                <p style={{ color: '#9CA3AF' }}>Aucune consultation enregistrée</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                {consultations.map((consultation, index) => {
                  const statusColors: Record<string, { bg: string; text: string; border: string }> = {
                    'en attente': { bg: '#FEF3C7', text: '#92400E', border: '#FCD34D' },
                    'en cours': { bg: '#DBEAFE', text: '#1E40AF', border: '#93C5FD' },
                    'terminée': { bg: '#D1FAE5', text: '#065F46', border: '#6EE7B7' }
                  };
                  const colors = statusColors[consultation.statut] || statusColors['en attente'];

                  return (
                    <div
                      key={consultation.consultation_id}
                      onMouseEnter={() => setHoveredConsultId(consultation.consultation_id)}
                      onMouseLeave={() => setHoveredConsultId(null)}
                      style={{
                        position: 'relative',
                        padding: '20px',
                        borderBottom: index < consultations.length - 1 ? '1px solid #E5E7EB' : 'none',
                        borderLeft: `4px solid ${colors.border}`,
                        background: index % 2 === 0 ? '#FAFAFA' : '#fff',
                        transition: 'background 0.15s'
                      }}
                    >
                      {/* Badge "Dossier à compléter" au survol */}
                      {isIncomplete && hoveredConsultId === consultation.consultation_id && (
                        <div style={{
                          position: 'absolute', top: '10px', right: '110px',
                          display: 'flex', alignItems: 'center', gap: '5px',
                          padding: '4px 12px', borderRadius: '20px',
                          background: '#FFF7ED', border: '1px solid #FED7AA',
                          color: '#EA580C', fontSize: '11px', fontWeight: 700,
                          boxShadow: '0 2px 8px rgba(234,88,12,0.15)',
                          zIndex: 10, pointerEvents: 'none'
                        }}>
                          <AlertCircle size={11} /> Dossier à compléter
                        </div>
                      )}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                        <div>
                          <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>
                            <Calendar size={12} style={{ display: 'inline', marginRight: '4px' }} />
                            {new Date(consultation.date_heure).toLocaleDateString('fr-FR', { 
                              weekday: 'long', 
                              year: 'numeric', 
                              month: 'long', 
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </div>
                          <div style={{ fontSize: '16px', fontWeight: 600, color: '#1F2937' }}>
                            #{consultation.consultation_id.toString().padStart(4, '0')} — {consultation.motif}
                          </div>
                        </div>
                        <span style={{
                          padding: '4px 12px',
                          background: colors.bg,
                          color: colors.text,
                          borderRadius: '12px',
                          fontSize: '11px',
                          fontWeight: 600,
                          textTransform: 'uppercase',
                          border: `1px solid ${colors.border}`
                        }}>
                          {consultation.statut}
                        </span>
                      </div>

                      {consultation.medecin_nom && (
                        <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px' }}>
                          <User size={12} style={{ display: 'inline', marginRight: '4px' }} />
                          Dr. {consultation.medecin_nom}
                        </div>
                      )}

                      {consultation.diagnostic ? (
                        <div style={{ marginTop: '14px', padding: '14px 16px', background: 'linear-gradient(135deg, #EEF2FF, #F5F3FF)', borderRadius: '10px', border: '1px solid #C7D2FE' }}>
                          {/* Header diagnostic */}
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <Brain size={14} style={{ color: '#4F46E5' }} />
                              <span style={{ fontSize: '11px', fontWeight: 700, color: '#4F46E5', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                                Diagnostic IA
                              </span>
                            </div>
                            <span style={{
                              display: 'inline-flex', alignItems: 'center', gap: '4px',
                              padding: '2px 10px', borderRadius: '10px', fontSize: '11px', fontWeight: 700,
                              background: consultation.diagnostic.statut === 'CONFIRMÉ' ? '#D1FAE5' : consultation.diagnostic.statut === 'REJETÉ' ? '#FEE2E2' : '#FEF3C7',
                              color: consultation.diagnostic.statut === 'CONFIRMÉ' ? '#065F46' : consultation.diagnostic.statut === 'REJETÉ' ? '#991B1B' : '#92400E',
                            }}>
                              {consultation.diagnostic.statut === 'CONFIRMÉ'
                                ? <><CheckCircle size={11} /> Confirmé</>
                                : consultation.diagnostic.statut === 'REJETÉ'
                                ? <><XCircle size={11} /> Rejeté</>
                                : 'Provisoire'}
                            </span>
                          </div>

                          {/* Maladie + certitude */}
                          <div style={{ fontSize: '17px', fontWeight: 800, color: '#3730A3', marginBottom: '8px' }}>
                            {consultation.diagnostic.nom_maladie}
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                            <span style={{ fontSize: '12px', color: '#6B7280' }}>Certitude :</span>
                            <div style={{ flex: 1, height: '6px', background: '#E5E7EB', borderRadius: '3px', overflow: 'hidden' }}>
                              <div style={{
                                height: '100%',
                                width: `${consultation.diagnostic.certitude}%`,
                                background: consultation.diagnostic.certitude >= 70 ? 'linear-gradient(90deg,#10B981,#059669)' : consultation.diagnostic.certitude >= 50 ? 'linear-gradient(90deg,#F59E0B,#D97706)' : 'linear-gradient(90deg,#EF4444,#DC2626)',
                                borderRadius: '3px', transition: 'width 0.6s ease'
                              }} />
                            </div>
                            <strong style={{ fontSize: '13px', color: consultation.diagnostic.certitude >= 70 ? '#059669' : consultation.diagnostic.certitude >= 50 ? '#D97706' : '#DC2626' }}>
                              {consultation.diagnostic.certitude}%
                            </strong>
                          </div>

                          {/* Description */}
                          {consultation.diagnostic.description && (
                            <div style={{ fontSize: '12px', color: '#374151', lineHeight: 1.5, padding: '8px 10px', background: 'rgba(255,255,255,0.7)', borderRadius: '6px', marginBottom: '6px' }}>
                              {consultation.diagnostic.description}
                            </div>
                          )}

                          {/* Date validation */}
                          {consultation.diagnostic.date_validation && (
                            <div style={{ fontSize: '11px', color: '#6B7280', marginTop: '6px' }}>
                              <Calendar size={10} style={{ display: 'inline', marginRight: '4px' }} />
                              Validé le {new Date(consultation.diagnostic.date_validation).toLocaleDateString('fr-FR')}
                            </div>
                          )}

                          {/* Bouton Voir Détails */}
                          <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid rgba(199, 210, 254, 0.5)' }}>
                            <Link
                              to={`/consultation/${consultation.consultation_id}/details`}
                              className="sp-btn sp-btn-outline sp-btn-sm"
                              style={{ width: '100%', justifyContent: 'center', fontSize: '12px' }}
                            >
                              <Eye size={14} />
                              Voir tous les détails
                            </Link>
                          </div>
                        </div>
                      ) : (
                        <div style={{ marginTop: '10px', padding: '12px 14px', background: '#F9FAFB', borderRadius: '8px', border: '1px dashed #D1D5DB', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px' }}>
                          <span style={{ fontSize: '12px', color: '#9CA3AF', fontStyle: 'italic' }}>Aucun diagnostic enregistré pour cette consultation</span>
                          {(consultation.statut === 'en attente' || consultation.statut === 'en cours' || consultation.statut === 'en_attente_medecin') && (user?.role === 'medecin' || user?.role === 'admin') && (
                            consultation.medecin_id == null || consultation.medecin_id === user?.medecin_id || user?.role === 'admin' ? (
                              <button
                                onClick={() => navigate(`/consultation/nouvelle?reprendre=${consultation.consultation_id}`)}
                                className="sp-btn sp-btn-primary"
                                style={{ fontSize: '12px', padding: '6px 16px', whiteSpace: 'nowrap', flexShrink: 0 }}
                              >
                                <Brain size={13} /> Continuer le diagnostic
                              </button>
                            ) : (
                              <button
                                className="sp-btn sp-btn-outline"
                                style={{ fontSize: '12px', padding: '6px 16px', whiteSpace: 'nowrap', flexShrink: 0, opacity: 0.5, cursor: 'not-allowed' }}
                                onClick={() => showToast('Cette consultation est assignée à un autre médecin', 'error')}
                              >
                                <Brain size={13} /> Réservé
                              </button>
                            )
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
      {/* ── Section Impression (Cachée à l'écran) ──────────────────── */}
      <div className="print-only medical-folder" style={{ display: 'none' }}>
        <div style={{ textAlign: 'center', borderBottom: '2px solid #000', paddingBottom: '20px', marginBottom: '30px' }}>
          <h1 style={{ fontSize: '28px', textTransform: 'uppercase', marginBottom: '5px' }}>GASA SAD</h1>
          <p style={{ fontSize: '14px', margin: 0 }}>Système d'Aide au Diagnostic</p>
          <p style={{ fontSize: '12px', color: '#666' }}>Rapport généré le {new Date().toLocaleString('fr-FR')}</p>
        </div>

        <div style={{ marginBottom: '30px' }}>
          <h2 style={{ fontSize: '20px', borderBottom: '1px solid #ccc', paddingBottom: '5px', marginBottom: '15px' }}>IDENTITÉ DU PATIENT</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <tbody>
              <tr>
                <td style={{ width: '25%', padding: '8px 0', fontWeight: 'bold' }}>Nom Complet:</td>
                <td style={{ padding: '8px 0' }}>{patient.prenoms} {patient.nom}</td>
                <td style={{ width: '25%', padding: '8px 0', fontWeight: 'bold' }}>ID Patient:</td>
                <td style={{ padding: '8px 0' }}>#{patient.patient_id.toString().padStart(4, '0')}</td>
              </tr>
              <tr>
                <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Date de Naissance:</td>
                <td style={{ padding: '8px 0' }}>{new Date(patient.date_naissance).toLocaleDateString('fr-FR')} ({calculateAge(patient.date_naissance)} ans)</td>
                <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Sexe:</td>
                <td style={{ padding: '8px 0' }}>{patient.sexe === 'M' ? '♂ Masculin' : '♀ Féminin'}</td>
              </tr>
              <tr>
                <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Téléphone:</td>
                <td style={{ padding: '8px 0' }}>{patient.telephone}</td>
                <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Email:</td>
                <td style={{ padding: '8px 0' }}>{patient.email || 'N/A'}</td>
              </tr>
              <tr>
                <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Groupe Sanguin:</td>
                <td style={{ padding: '8px 0' }}>{patient.groupe_sanguin || 'Inconnu'}</td>
                <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Adresse:</td>
                <td style={{ padding: '8px 0' }}>{patient.adresse || 'N/A'}</td>
              </tr>
            </tbody>
          </table>
        </div>

        {(patient.dossier_medical?.allergies || patient.dossier_medical?.antecedents_personnels || patient.dossier_medical?.antecedents_familiaux) && (
          <div style={{ marginBottom: '30px' }}>
            <h2 style={{ fontSize: '20px', borderBottom: '1px solid #ccc', paddingBottom: '5px', marginBottom: '15px' }}>ALERTE ET ANTÉCÉDENTS</h2>
            {patient.dossier_medical?.allergies && (
              <div style={{ marginBottom: '10px' }}>
                <strong style={{ color: '#d32f2f' }}>ALLERGIES: </strong>
                <span>{patient.dossier_medical.allergies}</span>
              </div>
            )}
            {patient.dossier_medical?.antecedents_personnels && (
              <div style={{ marginBottom: '6px' }}>
                <strong>ANTÉCÉDENTS PERSONNELS: </strong>
                <span>{patient.dossier_medical.antecedents_personnels}</span>
              </div>
            )}
            {patient.dossier_medical?.antecedents_familiaux && (
              <div>
                <strong>ANTÉCÉDENTS FAMILIAUX: </strong>
                <span>{patient.dossier_medical.antecedents_familiaux}</span>
              </div>
            )}
          </div>
        )}

        <div>
          <h2 style={{ fontSize: '20px', borderBottom: '1px solid #ccc', paddingBottom: '5px', marginBottom: '15px' }}>HISTORIQUE MÉDICAL</h2>
          {consultations.length === 0 ? (
            <p>Aucun historique de consultation.</p>
          ) : (
            consultations.map((c) => (
              <div key={c.consultation_id} style={{ marginBottom: '25px', padding: '15px', border: '1px solid #eee', borderRadius: '5px', pageBreakInside: 'avoid' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px', borderBottom: '1px dashed #eee', paddingBottom: '5px' }}>
                  <span style={{ fontWeight: 'bold' }}>Consultation #{c.consultation_id.toString().padStart(4, '0')}</span>
                  <span>{new Date(c.date_heure).toLocaleString('fr-FR')}</span>
                </div>
                <div style={{ marginBottom: '8px' }}>
                  <strong>Motif: </strong> {c.motif}
                </div>
                {c.medecin_nom && (
                  <div style={{ marginBottom: '8px' }}>
                    <strong>Praticien: </strong> Dr. {c.medecin_nom}
                  </div>
                )}
                {c.diagnostic && (
                  <div style={{ marginTop: '10px', padding: '10px', background: '#f5f5f5', borderRadius: '4px' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>DIAGNOSTIC IA : {c.diagnostic.nom_maladie}</div>
                    <div style={{ fontSize: '12px' }}>
                      Confiance: {c.diagnostic.certitude}% | Statut: {c.diagnostic.statut}
                    </div>
                    {c.diagnostic.description && (
                      <div style={{ marginTop: '5px', fontStyle: 'italic', fontSize: '13px' }}>
                        {c.diagnostic.description}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        <div style={{ marginTop: '50px', textAlign: 'right' }}>
          <div style={{ display: 'inline-block', width: '200px', borderTop: '1px solid #000', paddingTop: '10px', textAlign: 'center' }}>
            Cachet et Signature
          </div>
        </div>
      </div>

      <style>{`
        @media print {
          body * {
            visibility: hidden;
          }
          .print-only, .print-only * {
            visibility: visible;
          }
          .print-only {
            display: block !important;
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
          }
          .no-print {
            display: none !important;
          }
          @page {
            margin: 2cm;
          }
        }
      `}</style>
    </>
  );
};

export default DossierPatient;
