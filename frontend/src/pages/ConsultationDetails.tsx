import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft, Activity, Stethoscope, Brain, FlaskConical, CheckCircle,
  XCircle, Pill, Calendar, User, Thermometer, Heart, Wind, Droplet,
  Weight, Ruler, FileText, AlertCircle, ClipboardList, Printer
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { MedicalDisclaimerBanner } from '../components/MedicalDisclaimerBanner';

interface Symptome {
  nom: string;
  severite: string;
  duree_jours: number;
  description?: string;
}

interface SignesVitaux {
  tension_systolique: number;
  tension_diastolique: number;
  frequence_cardiaque: number;
  frequence_respiratoire: number;
  temperature: number;
  saturation_o2: number;
  poids?: number;
  taille?: number;
}

interface Examen {
  type: string;
  nom: string;
  description?: string;
  resultats?: string;
  valeur_numerique?: number;
  unite_mesure?: string;
  date_examen?: string;
  is_suggested?: boolean;  // Indique si l'examen a été suggéré par l'IA
}

interface Prediction {
  maladie: string;
  probabilite: number;
}

interface AnalyseIA {
  maladie_predite: string;
  confiance: number;
  top_predictions: Prediction[];
}

interface Medicament {
  nom: string;
  dosage: string;
  frequence: string;
  duree_jours: number;
  instructions?: string;
}

interface ConsultationData {
  consultation_id: number;
  date_heure: string;
  motif: string;
  statut: string;
  patient: {
    nom: string;
    prenoms: string;
    date_naissance: string;
    sexe: string;
  };
  medecin_nom?: string;
  symptomes: Symptome[];
  signes_vitaux?: SignesVitaux;
  analyse_preliminaire?: AnalyseIA;
  examens: Examen[];
  analyse_finale?: AnalyseIA;
  diagnostic_final?: string;
  validation_type?: string;
  notes_validation?: string;
  ordonnance: Medicament[];
  suivi?: {
    date_prochain_rdv?: string;
    instructions_patient?: string;
    notes_medecin?: string;
  };
}

const ConsultationDetails = () => {
  const { consultationId } = useParams<{ consultationId: string }>();
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [consultation, setConsultation] = useState<ConsultationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchConsultationDetails = async () => {
      if (!token || !consultationId) return;

      try {
        setLoading(true);
        const response = await fetch(`http://localhost:8000/api/consultations/${consultationId}/details-complets`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Impossible de charger les détails de la consultation');
        }

        const data = await response.json();
        setConsultation(data);
        setError(null);
      } catch (err: any) {
        console.error('Erreur chargement consultation:', err);
        setError(err.message || 'Erreur lors du chargement');
      } finally {
        setLoading(false);
      }
    };

    fetchConsultationDetails();
  }, [consultationId, token]);

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', flexDirection: 'column', gap: '16px' }}>
        <Activity size={48} style={{ animation: 'spin 1s linear infinite', color: '#4F46E5' }} />
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
        <p style={{ color: '#6B7280' }}>Chargement des détails...</p>
      </div>
    );
  }

  if (error || !consultation) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <AlertCircle size={48} style={{ color: '#EF4444', margin: '0 auto 16px' }} />
        <h3 style={{ color: '#1F2937', marginBottom: '8px' }}>Erreur de chargement</h3>
        <p style={{ color: '#6B7280', marginBottom: '16px' }}>{error || 'Consultation non trouvée'}</p>
        <button onClick={() => navigate(-1)} className="sp-btn sp-btn-primary">
          <ArrowLeft size={18} /> Retour
        </button>
      </div>
    );
  }

  const severityColors: Record<string, { bg: string; text: string }> = {
    'Légère': { bg: '#D1FAE5', text: '#065F46' },
    'Modérée': { bg: '#FEF3C7', text: '#92400E' },
    'Sévère': { bg: '#FEE2E2', text: '#991B1B' }
  };

  return (
    <>
      <div className="sp-page-header sp-fade-in no-print">
        <div>
          <h1 className="sp-page-title">Détails de la Consultation</h1>
          <p className="sp-page-subtitle">
            #{consultation.consultation_id.toString().padStart(4, '0')} — {consultation.patient.prenoms} {consultation.patient.nom}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={() => navigate(-1)} className="sp-btn sp-btn-outline">
            <ArrowLeft size={18} /> Retour
          </button>
          <button onClick={handlePrint} className="sp-btn sp-btn-outline">
            <Printer size={18} /> Imprimer
          </button>
        </div>
      </div>

      <MedicalDisclaimerBanner />

      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }} className="sp-fade-in">
        {/* En-tête consultation */}
        <div className="sp-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '16px' }}>
            <div>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937', marginBottom: '8px' }}>
                {consultation.motif}
              </h2>
              <div style={{ display: 'flex', gap: '16px', fontSize: '14px', color: '#6B7280' }}>
                <div>
                  <Calendar size={14} style={{ display: 'inline', marginRight: '4px' }} />
                  {new Date(consultation.date_heure).toLocaleDateString('fr-FR', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
                {consultation.medecin_nom && (
                  <div>
                    <User size={14} style={{ display: 'inline', marginRight: '4px' }} />
                    Dr. {consultation.medecin_nom}
                  </div>
                )}
              </div>
            </div>
            <span style={{
              padding: '6px 16px',
              background: consultation.statut === 'terminée' ? '#D1FAE5' : '#DBEAFE',
              color: consultation.statut === 'terminée' ? '#065F46' : '#1E40AF',
              borderRadius: '12px',
              fontSize: '12px',
              fontWeight: 600,
              textTransform: 'uppercase'
            }}>
              {consultation.statut}
            </span>
          </div>
        </div>

        {/* Symptômes */}
        {consultation.symptomes && consultation.symptomes.length > 0 && (
          <div className="sp-card">
            <div className="sp-card-header">
              <div className="sp-card-title">
                <Activity size={20} />
                Symptômes
              </div>
            </div>
            <div style={{ padding: '20px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '12px' }}>
                {consultation.symptomes.map((symptome, index) => {
                  const colors = severityColors[symptome.severite] || severityColors['Modérée'];
                  return (
                    <div key={index} style={{
                      padding: '14px',
                      background: '#F9FAFB',
                      borderRadius: '10px',
                      border: '1px solid #E5E7EB'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                        <div style={{ fontWeight: 600, color: '#1F2937', fontSize: '14px' }}>
                          {symptome.nom}
                        </div>
                        <span style={{
                          padding: '2px 8px',
                          background: colors.bg,
                          color: colors.text,
                          borderRadius: '6px',
                          fontSize: '11px',
                          fontWeight: 600
                        }}>
                          {symptome.severite}
                        </span>
                      </div>
                      <div style={{ fontSize: '12px', color: '#6B7280' }}>
                        Durée: {symptome.duree_jours} jour{symptome.duree_jours > 1 ? 's' : ''}
                      </div>
                      {symptome.description && (
                        <div style={{ fontSize: '12px', color: '#4B5563', marginTop: '6px', fontStyle: 'italic' }}>
                          {symptome.description}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Signes Vitaux */}
        {consultation.signes_vitaux && (
          <div className="sp-card">
            <div className="sp-card-header">
              <div className="sp-card-title">
                <Stethoscope size={20} />
                Signes Vitaux
              </div>
            </div>
            <div style={{ padding: '20px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
                <VitalCard
                  icon={Heart}
                  label="Tension Artérielle"
                  value={`${consultation.signes_vitaux.tension_systolique}/${consultation.signes_vitaux.tension_diastolique}`}
                  unit="mmHg"
                />
                <VitalCard
                  icon={Activity}
                  label="Fréquence Cardiaque"
                  value={consultation.signes_vitaux.frequence_cardiaque}
                  unit="bpm"
                />
                <VitalCard
                  icon={Wind}
                  label="Fréquence Respiratoire"
                  value={consultation.signes_vitaux.frequence_respiratoire}
                  unit="/min"
                />
                <VitalCard
                  icon={Thermometer}
                  label="Température"
                  value={consultation.signes_vitaux.temperature}
                  unit="°C"
                />
                <VitalCard
                  icon={Droplet}
                  label="Saturation O₂"
                  value={consultation.signes_vitaux.saturation_o2}
                  unit="%"
                />
                {consultation.signes_vitaux.poids && (
                  <VitalCard
                    icon={Weight}
                    label="Poids"
                    value={consultation.signes_vitaux.poids}
                    unit="kg"
                  />
                )}
                {consultation.signes_vitaux.taille && (
                  <VitalCard
                    icon={Ruler}
                    label="Taille"
                    value={consultation.signes_vitaux.taille}
                    unit="cm"
                  />
                )}
              </div>
            </div>
          </div>
        )}

        {/* Analyse Préliminaire IA */}
        {consultation.analyse_preliminaire && (
          <div className="sp-card">
            <div className="sp-card-header">
              <div className="sp-card-title">
                <Brain size={20} />
                Analyse Préliminaire IA
              </div>
            </div>
            <div style={{ padding: '20px' }}>
              <AnalyseIACard analyse={consultation.analyse_preliminaire} />
            </div>
          </div>
        )}

        {/* Examens */}
        {consultation.examens && consultation.examens.length > 0 && (
          <div className="sp-card">
            <div className="sp-card-header">
              <div className="sp-card-title">
                <FlaskConical size={20} />
                Examens Complémentaires
              </div>
            </div>
            <div style={{ padding: '20px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {consultation.examens.map((examen, index) => (
                  <div key={index} style={{
                    padding: '16px',
                    background: '#F9FAFB',
                    borderRadius: '10px',
                    border: '1px solid #E5E7EB'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', flexWrap: 'wrap' }}>
                          <span style={{ fontWeight: 600, color: '#1F2937', fontSize: '15px' }}>
                            {examen.nom}
                          </span>
                          {examen.is_suggested && (
                            <span style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px',
                              padding: '2px 8px',
                              background: 'linear-gradient(135deg, #10B981, #059669)',
                              color: '#fff',
                              borderRadius: '6px',
                              fontSize: '10px',
                              fontWeight: 700,
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }}>
                              <Brain size={10} />
                              Suggestion IA
                            </span>
                          )}
                          {!examen.is_suggested && examen.description && (
                            <span style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px',
                              padding: '2px 8px',
                              background: '#6366F1',
                              color: '#fff',
                              borderRadius: '6px',
                              fontSize: '10px',
                              fontWeight: 700,
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }}>
                              <User size={10} />
                              Médecin
                            </span>
                          )}
                        </div>
                        <span style={{
                          padding: '2px 8px',
                          background: '#DBEAFE',
                          color: '#1E40AF',
                          borderRadius: '6px',
                          fontSize: '11px',
                          fontWeight: 600
                        }}>
                          {examen.type}
                        </span>
                      </div>
                      {examen.valeur_numerique != null && (
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '18px', fontWeight: 700, color: '#4F46E5' }}>
                            {examen.valeur_numerique}
                          </div>
                          <div style={{ fontSize: '11px', color: '#6B7280' }}>
                            {examen.unite_mesure}
                          </div>
                        </div>
                      )}
                    </div>
                    {examen.description && (
                      <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '6px' }}>
                        {examen.description}
                      </div>
                    )}
                    {examen.resultats && (
                      <div style={{ fontSize: '13px', color: '#374151', marginTop: '8px', padding: '8px', background: '#fff', borderRadius: '6px' }}>
                        <strong>Résultats:</strong> {examen.resultats}
                      </div>
                    )}
                    {examen.date_examen && (
                      <div style={{ fontSize: '11px', color: '#9CA3AF', marginTop: '6px' }}>
                        <Calendar size={10} style={{ display: 'inline', marginRight: '4px' }} />
                        {new Date(examen.date_examen).toLocaleDateString('fr-FR')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Analyse Finale IA */}
        {consultation.analyse_finale && (
          <div className="sp-card">
            <div className="sp-card-header">
              <div className="sp-card-title">
                <Brain size={20} />
                Diagnostic IA Final
              </div>
            </div>
            <div style={{ padding: '20px' }}>
              <AnalyseIACard analyse={consultation.analyse_finale} />
            </div>
          </div>
        )}

        {/* Validation Médicale */}
        {consultation.diagnostic_final && (
          <div className="sp-card">
            <div className="sp-card-header">
              <div className="sp-card-title">
                {consultation.validation_type === 'confirme' ? <CheckCircle size={20} /> : <XCircle size={20} />}
                Validation Médicale
              </div>
            </div>
            <div style={{ padding: '20px' }}>
              <div style={{
                padding: '16px',
                background: consultation.validation_type === 'confirme' ? '#D1FAE5' : '#FEE2E2',
                borderRadius: '10px',
                border: `2px solid ${consultation.validation_type === 'confirme' ? '#6EE7B7' : '#FCA5A5'}`,
                marginBottom: '16px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  {consultation.validation_type === 'confirme' ? (
                    <CheckCircle size={20} style={{ color: '#065F46' }} />
                  ) : (
                    <XCircle size={20} style={{ color: '#991B1B' }} />
                  )}
                  <span style={{
                    fontSize: '12px',
                    fontWeight: 700,
                    color: consultation.validation_type === 'confirme' ? '#065F46' : '#991B1B',
                    textTransform: 'uppercase'
                  }}>
                    {consultation.validation_type === 'confirme' ? 'Diagnostic Confirmé' : 'Diagnostic Rejeté'}
                  </span>
                </div>
                <div style={{
                  fontSize: '18px',
                  fontWeight: 700,
                  color: consultation.validation_type === 'confirme' ? '#065F46' : '#991B1B'
                }}>
                  {consultation.diagnostic_final}
                </div>
              </div>
              {consultation.notes_validation && (
                <div style={{ padding: '14px', background: '#F9FAFB', borderRadius: '8px', border: '1px solid #E5E7EB' }}>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: '#6B7280', marginBottom: '6px' }}>
                    Notes du médecin:
                  </div>
                  <div style={{ fontSize: '14px', color: '#374151', lineHeight: 1.6 }}>
                    {consultation.notes_validation}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Ordonnance */}
        {consultation.ordonnance && consultation.ordonnance.length > 0 && (
          <div className="sp-card">
            <div className="sp-card-header">
              <div className="sp-card-title">
                <Pill size={20} />
                Ordonnance
              </div>
            </div>
            <div style={{ padding: '20px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {consultation.ordonnance.map((medicament, index) => (
                  <div key={index} style={{
                    padding: '16px',
                    background: '#F0FDF4',
                    borderRadius: '10px',
                    border: '1px solid #86EFAC'
                  }}>
                    <div style={{ fontWeight: 700, color: '#1F2937', fontSize: '16px', marginBottom: '8px' }}>
                      {medicament.nom}
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))', gap: '12px', marginBottom: '8px' }}>
                      <div>
                        <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '2px' }}>Dosage</div>
                        <div style={{ fontSize: '13px', fontWeight: 600, color: '#374151' }}>{medicament.dosage}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '2px' }}>Fréquence</div>
                        <div style={{ fontSize: '13px', fontWeight: 600, color: '#374151' }}>{medicament.frequence}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '2px' }}>Durée</div>
                        <div style={{ fontSize: '13px', fontWeight: 600, color: '#374151' }}>
                          {medicament.duree_jours} jour{medicament.duree_jours > 1 ? 's' : ''}
                        </div>
                      </div>
                    </div>
                    {medicament.instructions && (
                      <div style={{ fontSize: '12px', color: '#065F46', fontStyle: 'italic', marginTop: '6px' }}>
                        {medicament.instructions}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Suivi */}
        {consultation.suivi && (
          <div className="sp-card">
            <div className="sp-card-header">
              <div className="sp-card-title">
                <ClipboardList size={20} />
                Suivi
              </div>
            </div>
            <div style={{ padding: '20px' }}>
              {consultation.suivi.date_prochain_rdv && (
                <div style={{ marginBottom: '16px' }}>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: '#6B7280', marginBottom: '6px' }}>
                    Prochain rendez-vous:
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 700, color: '#4F46E5' }}>
                    <Calendar size={16} style={{ display: 'inline', marginRight: '6px' }} />
                    {new Date(consultation.suivi.date_prochain_rdv).toLocaleDateString('fr-FR', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </div>
                </div>
              )}
              {consultation.suivi.instructions_patient && (
                <div style={{ marginBottom: '16px', padding: '14px', background: '#EEF2FF', borderRadius: '8px', border: '1px solid #C7D2FE' }}>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: '#4338CA', marginBottom: '6px' }}>
                    Instructions pour le patient:
                  </div>
                  <div style={{ fontSize: '14px', color: '#3730A3', lineHeight: 1.6 }}>
                    {consultation.suivi.instructions_patient}
                  </div>
                </div>
              )}
              {consultation.suivi.notes_medecin && (
                <div style={{ padding: '14px', background: '#F9FAFB', borderRadius: '8px', border: '1px solid #E5E7EB' }}>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: '#6B7280', marginBottom: '6px' }}>
                    Notes du médecin:
                  </div>
                  <div style={{ fontSize: '14px', color: '#374151', lineHeight: 1.6 }}>
                    {consultation.suivi.notes_medecin}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style>{`
        @media print {
          .no-print {
            display: none !important;
          }
          .sp-card {
            page-break-inside: avoid;
            margin-bottom: 20px;
          }
        }
      `}</style>
    </>
  );
};

// Composants auxiliaires
const VitalCard = ({ icon: Icon, label, value, unit }: any) => (
  <div style={{
    padding: '14px',
    background: '#F9FAFB',
    borderRadius: '10px',
    border: '1px solid #E5E7EB'
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: '#6B7280', marginBottom: '6px' }}>
      <Icon size={12} />
      {label}
    </div>
    <div style={{ fontWeight: 700, fontSize: '18px', color: '#1F2937' }}>
      {value} <span style={{ fontSize: '12px', fontWeight: 400, color: '#9CA3AF' }}>{unit}</span>
    </div>
  </div>
);

const AnalyseIACard = ({ analyse }: { analyse: AnalyseIA }) => {
  const toPercent = (v: number) => (v <= 1 ? v * 100 : v);
  const confiance = toPercent(analyse.confiance);
  const isHigh   = confiance >= 70;
  const isMedium = confiance >= 50 && confiance < 70;

  const badge = isHigh
    ? { label: 'Diagnostic fiable', bg: '#D1FAE5', color: '#065F46' }
    : isMedium
    ? { label: 'À vérifier cliniquement', bg: '#FEF3C7', color: '#92400E' }
    : { label: 'Suggestion exploratoire', bg: '#FEE2E2', color: '#991B1B' };

  return (
    <div style={{ marginBottom: '4px' }}>
      <div style={{
        padding: '20px',
        background: 'linear-gradient(135deg, #EEF2FF, #F5F3FF)',
        borderRadius: '12px',
        border: '2px solid #C7D2FE',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#4F46E5', textTransform: 'uppercase', marginBottom: '8px' }}>
              🤖 Diagnostic Principal IA
            </div>
            <div style={{ fontSize: '22px', fontWeight: 800, color: '#3730A3' }}>
              {analyse.maladie_predite}
            </div>
          </div>
          <span style={{
            padding: '4px 12px',
            borderRadius: '20px',
            fontSize: '11px',
            fontWeight: 700,
            background: badge.bg,
            color: badge.color,
            whiteSpace: 'nowrap',
          }}>
            {badge.label}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <span style={{ fontSize: '12px', color: '#6B7280' }}>Confiance :</span>
          <div style={{ flex: 1, height: '8px', background: '#E5E7EB', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{
              height: '100%',
              width: `${confiance}%`,
              background: isHigh
                ? 'linear-gradient(90deg, #10B981, #059669)'
                : isMedium
                ? 'linear-gradient(90deg, #F59E0B, #D97706)'
                : 'linear-gradient(90deg, #EF4444, #DC2626)',
              borderRadius: '4px',
              transition: 'width 0.6s ease',
            }} />
          </div>
          <strong style={{ fontSize: '16px', color: isHigh ? '#059669' : isMedium ? '#D97706' : '#DC2626' }}>
            {confiance.toFixed(1)}%
          </strong>
        </div>

        {analyse.top_predictions && analyse.top_predictions.length > 1 && (
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase', marginBottom: '10px' }}>
              Diagnostics Alternatifs
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {analyse.top_predictions.slice(1, 4).map((pred, index) => {
                const prob = toPercent(pred.probabilite);
                return (
                  <div key={index} style={{
                    padding: '10px 12px',
                    background: 'rgba(255, 255, 255, 0.7)',
                    borderRadius: '8px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}>
                    <span style={{ fontSize: '13px', color: '#374151', fontWeight: 500 }}>{pred.maladie}</span>
                    <span style={{ fontSize: '13px', fontWeight: 700, color: '#6B7280' }}>{prob.toFixed(1)}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

    </div>
  );
};

export default ConsultationDetails;
