import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../components/Toast';
import { 
  User, Activity, Stethoscope, Brain, CheckCircle, 
  ArrowRight, ArrowLeft, X, AlertCircle, Thermometer,
  Heart, Wind, Droplet, Weight, Ruler, FileText, FlaskConical
} from 'lucide-react';

// Types
interface PatientData {
  nom: string;
  prenoms: string;
  date_naissance: string;
  sexe: 'M' | 'F';
  telephone?: string;
  email?: string;
}

interface Symptome {
  nom: string;
  severite: 'Légère' | 'Modérée' | 'Sévère';
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
  type: 'CLINIQUE' | 'IMAGERIE' | 'BIOLOGIE' | 'ELECTROCARDIOGRAMME';
  nom: string;
  description?: string;
  resultats?: string;
  valeur_numerique?: number;
  unite_mesure?: string;
  date_examen?: string;
}

interface PredictionIA {
  maladie_predite: string;
  confiance: number;
  top_3_predictions: Array<{ maladie: string; probabilite: number }>;
}

const ConsultationWorkflow = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [currentStep, setCurrentStep] = useState(1);
  const [patientData, setPatientData] = useState<PatientData>({
    nom: '',
    prenoms: '',
    date_naissance: '',
    sexe: 'M'
  });

  const [symptomes, setSymptomes] = useState<Symptome[]>([]);
  const [signesVitaux, setSignesVitaux] = useState<SignesVitaux>({
    tension_systolique: 120,
    tension_diastolique: 80,
    frequence_cardiaque: 70,
    frequence_respiratoire: 16,
    temperature: 37.0,
    saturation_o2: 98
  });
  const [examens, setExamens] = useState<Examen[]>([]);
  const [motifConsultation, setMotifConsultation] = useState('');
  const [predictionIA, setPredictionIA] = useState<PredictionIA | null>(null);
  const [diagnosticFinal, setDiagnosticFinal] = useState('');
  const [loading, setLoading] = useState(false);

  const steps = [
    { num: 1, title: 'Patient', icon: User },
    { num: 2, title: 'Symptômes', icon: Activity },
    { num: 3, title: 'Signes Vitaux', icon: Stethoscope },
    { num: 4, title: 'Examens', icon: FlaskConical },
    { num: 5, title: 'Consultation', icon: FileText },
    { num: 6, title: 'Diagnostic IA', icon: Brain },
    { num: 7, title: 'Validation', icon: CheckCircle }
  ];

  const handleNext = () => {
    if (currentStep < 7) setCurrentStep(currentStep + 1);
  };

  const handlePrevious = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const handleAddSymptome = () => {
    setSymptomes([...symptomes, { nom: '', severite: 'Modérée', duree_jours: 1 }]);
  };

  const handleRemoveSymptome = (index: number) => {
    setSymptomes(symptomes.filter((_, i) => i !== index));
  };

  const handleSymptomeChange = (index: number, field: keyof Symptome, value: any) => {
    const updated = [...symptomes];
    updated[index] = { ...updated[index], [field]: value };
    setSymptomes(updated);
  };

  const handleAddExamen = () => {
    setExamens([...examens, { type: 'BIOLOGIE', nom: '', description: '', resultats: '' }]);
  };

  const handleRemoveExamen = (index: number) => {
    setExamens(examens.filter((_, i) => i !== index));
  };

  const handleExamenChange = (index: number, field: keyof Examen, value: any) => {
    const updated = [...examens];
    updated[index] = { ...updated[index], [field]: value };
    setExamens(updated);
  };

  const handlePredictionIA = async () => {
    setLoading(true);
    try {
      // TODO: Appeler l'API backend réelle
      // const response = await fetch('http://localhost:8000/ml/predict', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({
      //     patient_data: {
      //       symptomes,
      //       signes_vitaux: signesVitaux
      //     }
      //   })
      // });
      // const data = await response.json();
      
      // Simuler un appel API pour l'instant
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setPredictionIA({
        maladie_predite: 'Grippe saisonnière',
        confiance: 0.87,
        top_3_predictions: [
          { maladie: 'Grippe saisonnière', probabilite: 0.87 },
          { maladie: 'Infection respiratoire', probabilite: 0.09 },
          { maladie: 'Bronchite aiguë', probabilite: 0.04 }
        ]
      });
      
      showToast('Diagnostic IA généré avec succès', 'success');
      handleNext();
    } catch (error) {
      console.error('Erreur lors de la prédiction IA:', error);
      showToast('Erreur lors de la génération du diagnostic IA', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      const consultationData = {
        patient: patientData,
        symptomes,
        signes_vitaux: signesVitaux,
        examens,
        motif: motifConsultation,
        prediction_ia: predictionIA,
        diagnostic_final: diagnosticFinal
      };
      
      // Appeler l'API backend
      const response = await fetch('http://localhost:8000/consultations/workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(consultationData)
      });
      
      if (!response.ok) {
        throw new Error('Erreur lors de l\'enregistrement');
      }
      
      const result = await response.json();
      console.log('Consultation enregistrée:', result);
      
      showToast('Consultation enregistrée avec succès !', 'success');
      
      // Rediriger vers la page des consultations après 1.5 secondes
      setTimeout(() => {
        navigate('/consultations');
      }, 1500);
      
    } catch (error) {
      console.error('Erreur lors de l\'enregistrement:', error);
      showToast('Erreur lors de l\'enregistrement de la consultation', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Nouvelle Consultation</h1>
          <p className="sp-page-subtitle">Workflow complet jusqu'au diagnostic IA</p>
        </div>
      </div>

      {/* Stepper */}
      <div className="sp-card sp-fade-in" style={{ marginBottom: '20px' }}>
        <div style={{ padding: '30px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'relative' }}>
            {/* Progress Line */}
            <div style={{
              position: 'absolute',
              top: '20px',
              left: '40px',
              right: '40px',
              height: '3px',
              background: '#E5E7EB',
              zIndex: 0
            }}>
              <div style={{
                height: '100%',
                background: 'linear-gradient(90deg, #4F46E5, #7C3AED)',
                width: `${((currentStep - 1) / 6) * 100}%`,
                transition: 'width 0.3s ease'
              }}></div>
            </div>

            {steps.map((step) => {
              const Icon = step.icon;
              const isActive = currentStep === step.num;
              const isCompleted = currentStep > step.num;

              return (
                <div key={step.num} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', zIndex: 1, flex: 1 }}>
                  <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: isCompleted ? 'linear-gradient(135deg, #4F46E5, #7C3AED)' : isActive ? '#4F46E5' : '#E5E7EB',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '8px',
                    transition: 'all 0.3s ease',
                    border: isActive ? '3px solid #EEF2FF' : 'none'
                  }}>
                    <Icon size={20} style={{ color: isCompleted || isActive ? 'white' : '#9CA3AF' }} />
                  </div>
                  <div style={{
                    fontSize: '12px',
                    fontWeight: isActive ? 700 : 600,
                    color: isActive ? '#4F46E5' : isCompleted ? '#6B7280' : '#9CA3AF',
                    textAlign: 'center'
                  }}>
                    {step.title}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="sp-card sp-fade-in">
        <div style={{ padding: '30px' }}>
          
          {/* Étape 1: Patient */}
          {currentStep === 1 && (
            <div>
              <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '20px', color: '#1F2937' }}>
                Informations du Patient
              </h2>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div className="sp-form-group">
                  <label className="sp-form-label">Nom <span style={{ color: '#EF4444' }}>*</span></label>
                  <input
                    type="text"
                    className="sp-form-input"
                    required
                    value={patientData.nom}
                    onChange={(e) => setPatientData({ ...patientData, nom: e.target.value })}
                  />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">Prénoms <span style={{ color: '#EF4444' }}>*</span></label>
                  <input
                    type="text"
                    className="sp-form-input"
                    required
                    value={patientData.prenoms}
                    onChange={(e) => setPatientData({ ...patientData, prenoms: e.target.value })}
                  />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">Date de naissance <span style={{ color: '#EF4444' }}>*</span></label>
                  <input
                    type="date"
                    className="sp-form-input"
                    required
                    value={patientData.date_naissance}
                    onChange={(e) => setPatientData({ ...patientData, date_naissance: e.target.value })}
                  />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">Sexe <span style={{ color: '#EF4444' }}>*</span></label>
                  <select
                    className="sp-form-select"
                    value={patientData.sexe}
                    onChange={(e) => setPatientData({ ...patientData, sexe: e.target.value as 'M' | 'F' })}
                  >
                    <option value="M">Masculin</option>
                    <option value="F">Féminin</option>
                  </select>
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">Téléphone</label>
                  <input
                    type="tel"
                    className="sp-form-input"
                    value={patientData.telephone || ''}
                    onChange={(e) => setPatientData({ ...patientData, telephone: e.target.value })}
                  />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">Email</label>
                  <input
                    type="email"
                    className="sp-form-input"
                    value={patientData.email || ''}
                    onChange={(e) => setPatientData({ ...patientData, email: e.target.value })}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Étape 2: Symptômes */}
          {currentStep === 2 && (
            <div>
              <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '20px', color: '#1F2937' }}>
                Saisie des Symptômes
              </h2>
              <p style={{ color: '#6B7280', marginBottom: '20px', fontSize: '14px' }}>
                Rôle: Infirmier - Enregistrez les symptômes rapportés par le patient
              </p>
              
              {symptomes.map((symptome, index) => (
                <div key={index} style={{ 
                  padding: '20px', 
                  background: '#F9FAFB', 
                  borderRadius: '12px', 
                  marginBottom: '16px',
                  border: '1px solid #E5E7EB'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#374151' }}>Symptôme {index + 1}</h3>
                    <button
                      type="button"
                      onClick={() => handleRemoveSymptome(index)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#EF4444',
                        cursor: 'pointer',
                        padding: '4px'
                      }}
                    >
                      <X size={20} />
                    </button>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '16px' }}>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Nom du symptôme</label>
                      <input
                        type="text"
                        className="sp-form-input"
                        value={symptome.nom}
                        onChange={(e) => handleSymptomeChange(index, 'nom', e.target.value)}
                        placeholder="Ex: Fièvre, Toux, Maux de tête..."
                      />
                    </div>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Sévérité</label>
                      <select
                        className="sp-form-select"
                        value={symptome.severite}
                        onChange={(e) => handleSymptomeChange(index, 'severite', e.target.value)}
                      >
                        <option value="Légère">Légère</option>
                        <option value="Modérée">Modérée</option>
                        <option value="Sévère">Sévère</option>
                      </select>
                    </div>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Durée (jours)</label>
                      <input
                        type="number"
                        className="sp-form-input"
                        min="1"
                        value={symptome.duree_jours}
                        onChange={(e) => handleSymptomeChange(index, 'duree_jours', parseInt(e.target.value))}
                      />
                    </div>
                  </div>
                  <div className="sp-form-group" style={{ marginTop: '12px' }}>
                    <label className="sp-form-label">Description</label>
                    <textarea
                      className="sp-form-textarea"
                      rows={2}
                      value={symptome.description || ''}
                      onChange={(e) => handleSymptomeChange(index, 'description', e.target.value)}
                      placeholder="Détails supplémentaires..."
                    />
                  </div>
                </div>
              ))}

              <button
                type="button"
                onClick={handleAddSymptome}
                className="sp-btn sp-btn-outline"
                style={{ width: '100%' }}
              >
                <Activity size={18} />
                Ajouter un symptôme
              </button>
            </div>
          )}

          {/* Étape 3: Signes Vitaux */}
          {currentStep === 3 && (
            <div>
              <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '20px', color: '#1F2937' }}>
                Mesure des Signes Vitaux
              </h2>
              <p style={{ color: '#6B7280', marginBottom: '20px', fontSize: '14px' }}>
                Rôle: Infirmier - Prenez les mesures des signes vitaux du patient
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div className="sp-form-group">
                  <label className="sp-form-label">
                    <Heart size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                    Tension Systolique (mmHg)
                  </label>
                  <input
                    type="number"
                    className="sp-form-input"
                    value={signesVitaux.tension_systolique}
                    onChange={(e) => setSignesVitaux({ ...signesVitaux, tension_systolique: parseInt(e.target.value) })}
                  />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">
                    <Heart size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                    Tension Diastolique (mmHg)
                  </label>
                  <input
                    type="number"
                    className="sp-form-input"
                    value={signesVitaux.tension_diastolique}
                    onChange={(e) => setSignesVitaux({ ...signesVitaux, tension_diastolique: parseInt(e.target.value) })}
                  />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">
                    <Activity size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                    Fréquence Cardiaque (bpm)
                  </label>
                  <input
                    type="number"
                    className="sp-form-input"
                    value={signesVitaux.frequence_cardiaque}
                    onChange={(e) => setSignesVitaux({ ...signesVitaux, frequence_cardiaque: parseInt(e.target.value) })}
                  />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">
                    <Wind size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                    Fréquence Respiratoire (rpm)
                  </label>
                  <input
                    type="number"
                    className="sp-form-input"
                    value={signesVitaux.frequence_respiratoire}
                    onChange={(e) => setSignesVitaux({ ...signesVitaux, frequence_respiratoire: parseInt(e.target.value) })}
                  />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">
                    <Thermometer size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                    Température (°C)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    className="sp-form-input"
                    value={signesVitaux.temperature}
                    onChange={(e) => setSignesVitaux({ ...signesVitaux, temperature: parseFloat(e.target.value) })}
                  />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">
                    <Droplet size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                    Saturation O2 (%)
                  </label>
                  <input
                    type="number"
                    className="sp-form-input"
                    value={signesVitaux.saturation_o2}
                    onChange={(e) => setSignesVitaux({ ...signesVitaux, saturation_o2: parseInt(e.target.value) })}
                  />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">
                    <Weight size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                    Poids (kg) - Optionnel
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    className="sp-form-input"
                    value={signesVitaux.poids || ''}
                    onChange={(e) => setSignesVitaux({ ...signesVitaux, poids: e.target.value ? parseFloat(e.target.value) : undefined })}
                  />
                </div>
                <div className="sp-form-group">
                  <label className="sp-form-label">
                    <Ruler size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                    Taille (cm) - Optionnel
                  </label>
                  <input
                    type="number"
                    className="sp-form-input"
                    value={signesVitaux.taille || ''}
                    onChange={(e) => setSignesVitaux({ ...signesVitaux, taille: e.target.value ? parseInt(e.target.value) : undefined })}
                  />
                </div>
              </div>

              {signesVitaux.poids && signesVitaux.taille && (
                <div style={{ 
                  marginTop: '20px', 
                  padding: '16px', 
                  background: '#EEF2FF', 
                  borderRadius: '8px',
                  border: '1px solid #C7D2FE'
                }}>
                  <strong style={{ color: '#4F46E5' }}>IMC calculé:</strong>{' '}
                  <span style={{ fontSize: '18px', fontWeight: 700, color: '#1F2937' }}>
                    {(signesVitaux.poids / Math.pow(signesVitaux.taille / 100, 2)).toFixed(1)} kg/m²
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Étape 4: Examens Médicaux */}
          {currentStep === 4 && (
            <div>
              <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '20px', color: '#1F2937' }}>
                Examens et Résultats d'Analyses
              </h2>
              <p style={{ color: '#6B7280', marginBottom: '20px', fontSize: '14px' }}>
                Rôle: Médecin/Infirmier - Enregistrez les résultats des examens complémentaires
              </p>

              {examens.map((examen, index) => (
                <div key={index} style={{ 
                  padding: '20px', 
                  background: '#F9FAFB', 
                  borderRadius: '12px', 
                  marginBottom: '16px',
                  border: '1px solid #E5E7EB'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#374151' }}>Examen {index + 1}</h3>
                    <button
                      type="button"
                      onClick={() => handleRemoveExamen(index)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#EF4444',
                        cursor: 'pointer',
                        padding: '4px'
                      }}
                    >
                      <X size={20} />
                    </button>
                  </div>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '16px', marginBottom: '16px' }}>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Type d'examen</label>
                      <select
                        className="sp-form-select"
                        value={examen.type}
                        onChange={(e) => handleExamenChange(index, 'type', e.target.value)}
                      >
                        <option value="BIOLOGIE">Biologie (Analyses de sang, urine...)</option>
                        <option value="IMAGERIE">Imagerie (Radio, Echo, Scanner...)</option>
                        <option value="ELECTROCARDIOGRAMME">Électrocardiogramme (ECG)</option>
                        <option value="CLINIQUE">Examen clinique</option>
                      </select>
                    </div>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Nom de l'examen</label>
                      <input
                        type="text"
                        className="sp-form-input"
                        value={examen.nom}
                        onChange={(e) => handleExamenChange(index, 'nom', e.target.value)}
                        placeholder="Ex: NFS, CRP, Radiographie thorax..."
                      />
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Valeur numérique</label>
                      <input
                        type="number"
                        step="0.01"
                        className="sp-form-input"
                        value={examen.valeur_numerique || ''}
                        onChange={(e) => handleExamenChange(index, 'valeur_numerique', e.target.value ? parseFloat(e.target.value) : undefined)}
                        placeholder="Ex: 12.5"
                      />
                    </div>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Unité de mesure</label>
                      <input
                        type="text"
                        className="sp-form-input"
                        value={examen.unite_mesure || ''}
                        onChange={(e) => handleExamenChange(index, 'unite_mesure', e.target.value)}
                        placeholder="Ex: g/L, mg/dL, mmol/L..."
                      />
                    </div>
                    <div className="sp-form-group">
                      <label className="sp-form-label">Date de l'examen</label>
                      <input
                        type="date"
                        className="sp-form-input"
                        value={examen.date_examen || ''}
                        onChange={(e) => handleExamenChange(index, 'date_examen', e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="sp-form-group">
                    <label className="sp-form-label">Résultats / Interprétation</label>
                    <textarea
                      className="sp-form-textarea"
                      rows={3}
                      value={examen.resultats || ''}
                      onChange={(e) => handleExamenChange(index, 'resultats', e.target.value)}
                      placeholder="Décrivez les résultats de l'examen et leur interprétation..."
                    />
                  </div>

                  <div className="sp-form-group">
                    <label className="sp-form-label">Description / Notes</label>
                    <textarea
                      className="sp-form-textarea"
                      rows={2}
                      value={examen.description || ''}
                      onChange={(e) => handleExamenChange(index, 'description', e.target.value)}
                      placeholder="Notes supplémentaires..."
                    />
                  </div>
                </div>
              ))}

              <button
                type="button"
                onClick={handleAddExamen}
                className="sp-btn sp-btn-outline"
                style={{ width: '100%' }}
              >
                <FlaskConical size={18} />
                Ajouter un examen
              </button>

              <div style={{
                marginTop: '20px',
                padding: '16px',
                background: '#EFF6FF',
                borderRadius: '8px',
                border: '1px solid #BFDBFE',
                display: 'flex',
                gap: '12px'
              }}>
                <AlertCircle size={20} style={{ color: '#3B82F6', flexShrink: 0, marginTop: '2px' }} />
                <div style={{ fontSize: '13px', color: '#1E40AF' }}>
                  <strong>Astuce:</strong> Les résultats d'examens complémentaires amélioreront la précision du diagnostic IA. 
                  Vous pouvez passer cette étape si aucun examen n'a été réalisé.
                </div>
              </div>
            </div>
          )}

          {/* Étape 5: Consultation Médecin */}
          {currentStep === 5 && (
            <div>
              <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '20px', color: '#1F2937' }}>
                Consultation Médicale
              </h2>
              <p style={{ color: '#6B7280', marginBottom: '20px', fontSize: '14px' }}>
                Rôle: Médecin - Examinez le patient et notez vos observations
              </p>

              <div className="sp-form-group">
                <label className="sp-form-label">Motif de consultation</label>
                <textarea
                  className="sp-form-textarea"
                  rows={4}
                  value={motifConsultation}
                  onChange={(e) => setMotifConsultation(e.target.value)}
                  placeholder="Décrivez le motif de la consultation et vos observations..."
                />
              </div>

              {/* Résumé des données collectées */}
              <div style={{ marginTop: '30px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px', color: '#374151' }}>
                  Résumé des données collectées
                </h3>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div style={{ padding: '16px', background: '#F9FAFB', borderRadius: '8px' }}>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>Patient</div>
                    <div style={{ fontWeight: 600 }}>{patientData.prenoms} {patientData.nom}</div>
                  </div>
                  <div style={{ padding: '16px', background: '#F9FAFB', borderRadius: '8px' }}>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>Symptômes</div>
                    <div style={{ fontWeight: 600 }}>{symptomes.length} symptôme(s)</div>
                  </div>
                  <div style={{ padding: '16px', background: '#F9FAFB', borderRadius: '8px' }}>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>Température</div>
                    <div style={{ fontWeight: 600 }}>{signesVitaux.temperature}°C</div>
                  </div>
                  <div style={{ padding: '16px', background: '#F9FAFB', borderRadius: '8px' }}>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>Tension</div>
                    <div style={{ fontWeight: 600 }}>{signesVitaux.tension_systolique}/{signesVitaux.tension_diastolique} mmHg</div>
                  </div>
                  <div style={{ padding: '16px', background: '#F9FAFB', borderRadius: '8px' }}>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>Examens</div>
                    <div style={{ fontWeight: 600 }}>{examens.length} examen(s)</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Étape 6: Prédiction IA */}
          {currentStep === 6 && (
            <div>
              <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '20px', color: '#1F2937' }}>
                Diagnostic par Intelligence Artificielle
              </h2>
              
              {!predictionIA ? (
                <div style={{ textAlign: 'center', padding: '40px' }}>
                  <div style={{
                    width: '80px',
                    height: '80px',
                    margin: '0 auto 20px',
                    background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <Brain size={40} style={{ color: 'white' }} />
                  </div>
                  <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '12px' }}>
                    Prêt pour l'analyse IA
                  </h3>
                  <p style={{ color: '#6B7280', marginBottom: '24px' }}>
                    Le système va analyser les symptômes, signes vitaux et résultats d'examens pour suggérer un diagnostic
                  </p>
                  <button
                    onClick={handlePredictionIA}
                    disabled={loading}
                    className="sp-btn sp-btn-primary"
                    style={{ minWidth: '200px' }}
                  >
                    {loading ? (
                      <>
                        <Activity size={18} style={{ animation: 'spin 1s linear infinite' }} />
                        Analyse en cours...
                      </>
                    ) : (
                      <>
                        <Brain size={18} />
                        Lancer le diagnostic IA
                      </>
                    )}
                  </button>
                </div>
              ) : (
                <div>
                  <div style={{
                    padding: '24px',
                    background: 'linear-gradient(135deg, #EEF2FF, #E0E7FF)',
                    borderRadius: '12px',
                    marginBottom: '24px',
                    border: '2px solid #C7D2FE'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <Brain size={24} style={{ color: 'white' }} />
                      </div>
                      <div>
                        <div style={{ fontSize: '14px', color: '#6B7280', marginBottom: '4px' }}>
                          Diagnostic suggéré par l'IA
                        </div>
                        <div style={{ fontSize: '24px', fontWeight: 700, color: '#1F2937' }}>
                          {predictionIA.maladie_predite}
                        </div>
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ fontSize: '14px', color: '#6B7280' }}>Niveau de confiance:</div>
                      <div style={{ flex: 1, height: '8px', background: '#E5E7EB', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{
                          height: '100%',
                          width: `${predictionIA.confiance * 100}%`,
                          background: predictionIA.confiance > 0.7 ? 'linear-gradient(90deg, #10B981, #059669)' : 
                                     predictionIA.confiance > 0.5 ? 'linear-gradient(90deg, #F59E0B, #D97706)' :
                                     'linear-gradient(90deg, #EF4444, #DC2626)',
                          transition: 'width 0.5s ease'
                        }}></div>
                      </div>
                      <div style={{ fontSize: '18px', fontWeight: 700, color: '#1F2937' }}>
                        {(predictionIA.confiance * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>

                  <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px', color: '#374151' }}>
                    Top 3 des diagnostics possibles
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {predictionIA.top_3_predictions.map((pred, index) => (
                      <div key={index} style={{
                        padding: '16px',
                        background: '#F9FAFB',
                        borderRadius: '8px',
                        border: '1px solid #E5E7EB',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <div style={{
                            width: '32px',
                            height: '32px',
                            borderRadius: '50%',
                            background: index === 0 ? '#4F46E5' : '#E5E7EB',
                            color: index === 0 ? 'white' : '#6B7280',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontWeight: 700,
                            fontSize: '14px'
                          }}>
                            {index + 1}
                          </div>
                          <div style={{ fontWeight: 600, color: '#1F2937' }}>{pred.maladie}</div>
                        </div>
                        <div style={{ fontWeight: 700, color: '#4F46E5' }}>
                          {(pred.probabilite * 100).toFixed(1)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Étape 7: Validation Médicale */}
          {currentStep === 7 && (
            <div>
              <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '20px', color: '#1F2937' }}>
                Validation Médicale
              </h2>
              <p style={{ color: '#6B7280', marginBottom: '20px', fontSize: '14px' }}>
                Rôle: Médecin - Validez ou modifiez le diagnostic suggéré par l'IA
              </p>

              {predictionIA && (
                <div style={{
                  padding: '20px',
                  background: '#F9FAFB',
                  borderRadius: '12px',
                  marginBottom: '24px',
                  border: '1px solid #E5E7EB'
                }}>
                  <div style={{ fontSize: '14px', color: '#6B7280', marginBottom: '8px' }}>
                    Diagnostic suggéré par l'IA
                  </div>
                  <div style={{ fontSize: '20px', fontWeight: 700, color: '#4F46E5', marginBottom: '8px' }}>
                    {predictionIA.maladie_predite}
                  </div>
                  <div style={{ fontSize: '14px', color: '#6B7280' }}>
                    Confiance: {(predictionIA.confiance * 100).toFixed(1)}%
                  </div>
                </div>
              )}

              <div className="sp-form-group">
                <label className="sp-form-label">
                  Diagnostic final <span style={{ color: '#EF4444' }}>*</span>
                </label>
                <textarea
                  className="sp-form-textarea"
                  rows={4}
                  required
                  value={diagnosticFinal}
                  onChange={(e) => setDiagnosticFinal(e.target.value)}
                  placeholder="Confirmez le diagnostic IA ou saisissez votre propre diagnostic..."
                />
              </div>

              <div style={{
                padding: '16px',
                background: '#FEF3C7',
                borderRadius: '8px',
                border: '1px solid #FCD34D',
                display: 'flex',
                gap: '12px',
                marginTop: '20px'
              }}>
                <AlertCircle size={20} style={{ color: '#D97706', flexShrink: 0, marginTop: '2px' }} />
                <div style={{ fontSize: '13px', color: '#92400E' }}>
                  <strong>Note importante:</strong> Le diagnostic final est sous votre responsabilité médicale. 
                  L'IA est un outil d'aide à la décision, pas un remplacement du jugement médical.
                </div>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: '40px',
            paddingTop: '24px',
            borderTop: '1px solid #E5E7EB'
          }}>
            <button
              onClick={handlePrevious}
              disabled={currentStep === 1}
              className="sp-btn sp-btn-outline"
              style={{ opacity: currentStep === 1 ? 0.5 : 1 }}
            >
              <ArrowLeft size={18} />
              Précédent
            </button>

            {currentStep < 6 && (
              <button onClick={handleNext} className="sp-btn sp-btn-primary">
                Suivant
                <ArrowRight size={18} />
              </button>
            )}

            {currentStep === 6 && predictionIA && (
              <button onClick={handleNext} className="sp-btn sp-btn-primary">
                Valider le diagnostic
                <ArrowRight size={18} />
              </button>
            )}

            {currentStep === 7 && (
              <button 
                onClick={handleSubmit} 
                className="sp-btn sp-btn-success"
                disabled={loading || !diagnosticFinal}
              >
                {loading ? (
                  <>
                    <Activity size={18} style={{ animation: 'spin 1s linear infinite' }} />
                    Enregistrement...
                  </>
                ) : (
                  <>
                    <CheckCircle size={18} />
                    Enregistrer la consultation
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConsultationWorkflow;
