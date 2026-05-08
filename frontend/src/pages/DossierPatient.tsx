import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Calendar, Activity, FileText, Pill, AlertCircle, User, Phone, Mail, MapPin, Cake, Edit, Brain, CheckCircle, XCircle, Droplet } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { patientsAPI, consultationsAPI } from '../services/api';

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
  allergies?: string;
  antecedents_medicaux?: string;
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
  medecin_nom?: string;
  diagnostic?: DiagnosticInfo | null;
}

const DossierPatient = () => {
  const { patientId } = useParams<{ patientId: string }>();
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Vérifier les permissions : seulement admin et médecin
  useEffect(() => {
    if (user?.role === 'infirmier') {
      navigate('/consultations', { replace: true });
    }
  }, [user, navigate]);

  useEffect(() => {
    const fetchData = async () => {
      if (!token || !patientId) return;
      
      try {
        setLoading(true);
        // Récupérer les données du patient (patientId est un INT)
        const patientData = await patientsAPI.get(parseInt(patientId), token);
        setPatient(patientData);

        // Récupérer l'historique des consultations
        const consultationsData = await consultationsAPI.getByPatient(parseInt(patientId), token);
        setConsultations(consultationsData);
        
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

  const calculateAge = (birthDate: string) => {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const getInitials = (nom: string, prenoms: string) => {
    return `${prenoms.charAt(0)}${nom.charAt(0)}`.toUpperCase();
  };

  return (
    <>
      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Dossier Patient</h1>
          <p className="sp-page-subtitle">{consultations.length} visite(s)</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Link to="/consultations" className="sp-btn sp-btn-outline">
            <ArrowLeft size={18} /> Retour aux consultations
          </Link>
          {user?.role === 'admin' && (
            <button className="sp-btn sp-btn-primary">
              <Edit size={18} /> Modifier le dossier
            </button>
          )}
        </div>
      </div>

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

            {/* Détails */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#6B7280', fontSize: '12px', marginBottom: '4px' }}>
                  <Cake size={14} />
                  <span>Date de naissance</span>
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#1F2937' }}>
                  {new Date(patient.date_naissance).toLocaleDateString('fr-FR')} ({calculateAge(patient.date_naissance)} ans)
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#6B7280', fontSize: '12px', marginBottom: '4px' }}>
                  <User size={14} />
                  <span>Sexe</span>
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#1F2937' }}>
                  {patient.sexe === 'M' ? 'Masculin' : 'Féminin'}
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
            {patient.allergies && (
              <div style={{ marginTop: '24px', padding: '12px', background: '#FEF3C7', borderRadius: '8px', border: '1px solid #FCD34D' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#92400E', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>
                  <AlertCircle size={14} />
                  <span>ALLERGIES</span>
                </div>
                <div style={{ fontSize: '13px', color: '#78350F' }}>
                  {patient.allergies}
                </div>
              </div>
            )}

            {/* Antécédents */}
            {patient.antecedents_medicaux && (
              <div style={{ marginTop: '16px', padding: '12px', background: '#DBEAFE', borderRadius: '8px', border: '1px solid #93C5FD' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#1E40AF', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>
                  <FileText size={14} />
                  <span>ANTÉCÉDENTS MÉDICAUX</span>
                </div>
                <div style={{ fontSize: '13px', color: '#1E3A8A' }}>
                  {patient.antecedents_medicaux}
                </div>
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
                      style={{
                        padding: '20px',
                        borderBottom: index < consultations.length - 1 ? '1px solid #E5E7EB' : 'none',
                        borderLeft: `4px solid ${colors.border}`,
                        background: index % 2 === 0 ? '#FAFAFA' : '#fff'
                      }}
                    >
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
                        </div>
                      ) : (
                        <div style={{ marginTop: '10px', padding: '10px 14px', background: '#F9FAFB', borderRadius: '8px', border: '1px dashed #D1D5DB' }}>
                          <span style={{ fontSize: '12px', color: '#9CA3AF', fontStyle: 'italic' }}>Aucun diagnostic enregistré pour cette consultation</span>
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
    </>
  );
};

export default DossierPatient;
