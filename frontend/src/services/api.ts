/**
 * Service API pour communiquer avec le backend FastAPI
 * Base URL: http://localhost:8000
 */

const API_BASE_URL = 'http://localhost:8000';

// Types pour les réponses API
export interface Patient {
  id: string;
  nom: string;
  prenom: string;
  date_naissance: string;
  sexe: 'M' | 'F';
  adresse?: string;
  telephone?: string;
  email?: string;
  groupe_sanguin?: string;
  date_creation: string;
}

export interface Consultation {
  id: number;
  nom_patient: string;
  date: string;
  motif: string;
  statut: 'en attente' | 'en cours' | 'terminée';
}

export interface Symptome {
  nom: string;
  severite: 'Légère' | 'Modérée' | 'Sévère';
  duree_jours: number;
  description?: string;
}

export interface SignesVitaux {
  tension_systolique: number;
  tension_diastolique: number;
  frequence_cardiaque: number;
  frequence_respiratoire: number;
  temperature: number;
  saturation_o2: number;
  poids?: number;
  taille?: number;
  imc?: number;
}

export interface PredictionIA {
  predicted_disease: string;
  confidence: number;
  confidence_level: 'LOW' | 'MEDIUM' | 'HIGH';
  top_3_predictions: Array<{
    disease: string;
    probability: number;
  }>;
  timestamp: string;
}

export interface Diagnostic {
  id: string;
  consultation_id: number;
  analyse_ia_id?: string;
  diagnostic_final: string;
  code_cim10?: string;
  notes_medecin?: string;
  statut: 'en_attente' | 'confirme' | 'rejete';
  date_diagnostic: string;
}

export interface DashboardStats {
  kpis: {
    total_patients: number;
    patients_ce_mois: number;
    total_consultations: number;
    total_diagnostics: number;
    taux_approbation: number;
    confiance_moyenne: number;
  };
  tendance_patients: Array<{
    date: string;
    count: number;
  }>;
  top_diagnostics: Array<{
    diagnostic: string;
    count: number;
  }>;
}

// Gestion des erreurs
class APIError extends Error {
  status: number;
  
  constructor(status: number, message: string) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

// Helper pour les requêtes
async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erreur inconnue' }));
      throw new APIError(response.status, error.detail || `Erreur ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) throw error;
    throw new Error(`Erreur de connexion au serveur: ${error}`);
  }
}

// ============================================================================
// PATIENTS
// ============================================================================

export const patientsAPI = {
  // Créer un patient
  create: (data: Omit<Patient, 'id' | 'date_creation'>) =>
    fetchAPI<Patient>('/patients', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Liste des patients
  list: (skip = 0, limit = 100) =>
    fetchAPI<Patient[]>(`/patients?skip=${skip}&limit=${limit}`),

  // Détails d'un patient
  get: (id: string) =>
    fetchAPI<Patient>(`/patients/${id}`),

  // Mettre à jour un patient
  update: (id: string, data: Partial<Patient>) =>
    fetchAPI<Patient>(`/patients/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // Supprimer un patient
  delete: (id: string) =>
    fetchAPI<{ message: string }>(`/patients/${id}`, {
      method: 'DELETE',
    }),
};

// ============================================================================
// CONSULTATIONS
// ============================================================================

export const consultationsAPI = {
  // Créer une consultation
  create: (data: {
    patient_id: string;
    medecin_id: number;
    motif: string;
    symptomes?: Symptome[];
    signes_vitaux?: SignesVitaux;
  }) =>
    fetchAPI<Consultation>('/consultations', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Liste des consultations
  list: (skip = 0, limit = 100) =>
    fetchAPI<Consultation[]>(`/consultations?skip=${skip}&limit=${limit}`),

  // Détails d'une consultation
  get: (id: number) =>
    fetchAPI<Consultation>(`/consultations/${id}`),

  // Historique d'un patient
  getByPatient: (patientId: string) =>
    fetchAPI<Consultation[]>(`/consultations/patient/${patientId}`),
};

// ============================================================================
// ML / IA
// ============================================================================

export const mlAPI = {
  // Prédiction de diagnostic
  predict: (patientData: Record<string, any>) =>
    fetchAPI<PredictionIA>('/ml/predict', {
      method: 'POST',
      body: JSON.stringify({ patient_data: patientData }),
    }),

  // Explication de la prédiction
  explain: (patientData: Record<string, any>) =>
    fetchAPI<{
      predicted_disease: string;
      confidence: number;
      feature_importance: Array<{ feature: string; importance: number }>;
      explanation: string;
    }>('/ml/explain', {
      method: 'POST',
      body: JSON.stringify({ patient_data: patientData }),
    }),

  // Créer un diagnostic IA
  createDiagnostic: (data: {
    consultation_id: number;
    diagnostic_suggere: string;
    confiance: number;
    explications?: string;
  }) =>
    fetchAPI<Diagnostic>('/ml/diagnostics', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Approuver un diagnostic IA
  approveDiagnostic: (id: string, data: {
    diagnostic_final: string;
    code_cim10?: string;
    notes_medecin?: string;
  }) =>
    fetchAPI<Diagnostic>(`/ml/diagnostics/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Rejeter un diagnostic IA
  rejectDiagnostic: (id: string, data: {
    raison: string;
    notes_medecin?: string;
  }) =>
    fetchAPI<Diagnostic>(`/ml/diagnostics/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Informations sur le modèle
  getModelInfo: () =>
    fetchAPI<{
      loaded: boolean;
      version: string;
      metadata: Record<string, any>;
      n_features: number;
      n_classes: number;
      classes: string[];
    }>('/ml/model/info'),
};

// ============================================================================
// ANALYTICS
// ============================================================================

export const analyticsAPI = {
  // Dashboard KPIs
  getDashboard: () =>
    fetchAPI<DashboardStats>('/analytics/dashboard'),

  // Distribution des diagnostics
  getDiagnosticsDistribution: (limit = 10) =>
    fetchAPI<Array<{ diagnostic: string; count: number; percentage: number }>>(
      `/analytics/diagnostics/distribution?limit=${limit}`
    ),

  // Performance du modèle
  getModelPerformance: () =>
    fetchAPI<{
      total_predictions: number;
      approved: number;
      rejected: number;
      pending: number;
      approval_rate: number;
      avg_confidence: number;
      confidence_distribution: Record<string, number>;
    }>('/analytics/performance/model'),

  // Consultations récentes
  getRecentConsultations: (limit = 10) =>
    fetchAPI<Consultation[]>(`/analytics/consultations/recent?limit=${limit}`),
  
  // Personnel disponible
  getPersonnelDisponible: () =>
    fetchAPI<{
      medecins: {
        disponibles: number;
        total: number;
        liste: Array<{
          id: number;
          nom: string;
          prenoms: string;
          specialite: string;
          telephone: string;
        }>;
      };
      infirmiers: {
        disponibles: number;
        total: number;
        liste: Array<{
          id: number;
          nom: string;
          prenoms: string;
          telephone: string;
          email?: string;
        }>;
      };
    }>('/analytics/personnel/disponible'),
};

// ============================================================================
// HEALTH CHECK
// ============================================================================

export const healthAPI = {
  check: () =>
    fetchAPI<{
      status: string;
      model_loaded: boolean;
      database: string;
    }>('/health'),

  root: () =>
    fetchAPI<{
      app: string;
      version: string;
      status: string;
      environment: string;
      model_loaded: boolean;
    }>('/'),
};

// Export par défaut
export default {
  patients: patientsAPI,
  consultations: consultationsAPI,
  ml: mlAPI,
  analytics: analyticsAPI,
  health: healthAPI,
};
