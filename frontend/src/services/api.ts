/**
 * Service API pour communiquer avec le backend FastAPI
 * Base URL: http://localhost:8000
 */

const API_BASE_URL = 'http://localhost:8000';

// Types pour les réponses API
export interface Patient {
  patient_id: number;  // INT AUTO_INCREMENT
  nom: string;
  prenoms: string;  // Pluriel comme dans la DB
  date_naissance: string;
  sexe: 'M' | 'F';
  adresse?: string;
  telephone?: string;
  email?: string;
  groupe_sanguin?: string;
  created_at: string;
}

export interface Consultation {
  id: number;
  patient_id?: number;
  nom_patient: string;
  // champs utilisés dans le formulaire rapide (create mode)
  nom?: string;
  prenoms?: string;
  sexe?: 'M' | 'F';
  date_naissance?: string;
  date: string;
  date_heure?: string;
  motif: string;
  medecin_id?: number | null;
  statut: 'en attente' | 'en cours' | 'terminée' | 'en_attente_medecin';
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
    consultations_en_attente?: number; // Ajout
    consultations_en_cours?: number; // Ajout
    consultations_terminees?: number; // Ajout
    total_diagnostics: number;
    taux_approbation: number;
    confiance_moyenne: number;
  };
  model_accuracy?: number; // Ajout
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
export class APIError extends Error {
  status: number;
  detail: string;
  
  constructor(status: number, message: string) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.detail = message;
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

    // Lire le contenu de la réponse
    const contentType = response.headers.get('content-type');
    let data;
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      data = { detail: text || 'Erreur inconnue' };
    }

    if (!response.ok) {
      const errorMessage = data.detail || data.message || `Erreur ${response.status}`;
      // Token invalide/expiré → purger la session et rediriger vers login
      if (response.status === 401) {
        localStorage.removeItem('sp_token');
        localStorage.removeItem('sp_user');
        window.location.href = '/login';
      }
      throw new APIError(response.status, errorMessage);
    }

    return data as T;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    
    // Erreur réseau ou autre
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new APIError(0, 'Impossible de se connecter au serveur. Vérifiez que le backend est démarré sur http://localhost:8000');
    }
    
    throw new APIError(500, `Erreur: ${error}`);
  }
}

// ============================================================================
// PATIENTS
// ============================================================================

export const patientsAPI = {
  // Créer un patient
  create: (data: Omit<Patient, 'patient_id' | 'created_at'>) =>
    fetchAPI<Patient>('/api/patients', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Liste des patients
  list: (skip = 0, limit = 100) =>
    fetchAPI<Patient[]>(`/api/patients?skip=${skip}&limit=${limit}`),

  // Détails d'un patient par ID (INT)
  get: (id: number, token?: string) =>
    fetchAPI<Patient>(`/api/patients/${id}`, {
      headers: token ? {
        'Authorization': `Bearer ${token}`,
      } : {},
    }),

  // Mettre à jour un patient
  update: (id: number, data: Partial<Patient>) =>
    fetchAPI<Patient>(`/api/patients/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // Supprimer un patient
  delete: (id: number) =>
    fetchAPI<{ message: string }>(`/api/patients/${id}`, {
      method: 'DELETE',
    }),
};

// ============================================================================
// CONSULTATIONS
// ============================================================================

export const consultationsAPI = {
  // Créer une consultation complète
  create: (data: {
    patient_id: string;
    medecin_id: number;
    motif: string;
    symptomes?: Symptome[];
    signes_vitaux?: SignesVitaux;
  }) =>
    fetchAPI<Consultation>('/api/consultations', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Initialise patient + consultation draft dès l'étape 1
  init: (data: { patient: object; motif: string; medecin_id?: number | null }) =>
    fetchAPI<{ success: boolean; consultation_id: number; patient_id: number }>('/api/consultations/init', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Consultation rapide avec création du patient (nom, prenoms, sexe requis)
  createRapide: (data: { nom?: string; prenoms?: string; sexe?: string; date_naissance?: string; nom_patient?: string; motif: string; date_heure: string; medecin_id?: number | null }) =>
    fetchAPI<{ success: boolean; consultation_id: number; patient_id: number | null }>('/api/consultations/rapide', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Liste des consultations
  list: (skip = 0, limit = 100) =>
    fetchAPI<Consultation[]>(`/api/consultations?skip=${skip}&limit=${limit}`),

  // Détails d'une consultation
  get: (id: number) =>
    fetchAPI<Consultation>(`/api/consultations/${id}`),

  // Historique d'un patient par ID (INT)
  getByPatient: (patientId: number, token?: string) =>
    fetchAPI<Consultation[]>(`/api/consultations/patient/${patientId}`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    }),

  // Affecter un médecin
  affecter: (id: number, medecinId: number) =>
    fetchAPI<{ success: boolean }>(`/api/consultations/${id}/affecter-medecin`, {
      method: 'PUT',
      body: JSON.stringify({ medecin_id: medecinId }),
    }),

  // Changer le statut
  updateStatut: (id: number, statut: string) =>
    fetchAPI<{ success: boolean }>(`/api/consultations/${id}/statut`, {
      method: 'PATCH',
      body: JSON.stringify({ statut }),
    }),

  // Mise à jour générale
  update: (id: number, data: { nom_patient?: string; motif?: string; date_heure?: string; medecin_id?: number | null; statut?: string }) =>
    fetchAPI<{ success: boolean }>(`/api/consultations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // Supprimer
  delete: (id: number) =>
    fetchAPI<{ success: boolean }>(`/api/consultations/${id}`, {
      method: 'DELETE',
    }),
};

// ============================================================================
// ML / IA
// ============================================================================

export const mlAPI = {
  // Prédiction de diagnostic
  predict: (patientData: Record<string, any>) =>
    fetchAPI<PredictionIA>('/api/ml/predict', {
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
    }>('/api/ml/explain', {
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
    fetchAPI<Diagnostic>('/api/ml/diagnostics', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Approuver un diagnostic IA
  approveDiagnostic: (id: string, data: {
    diagnostic_final: string;
    code_cim10?: string;
    notes_medecin?: string;
  }) =>
    fetchAPI<Diagnostic>(`/api/ml/diagnostics/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Rejeter un diagnostic IA
  rejectDiagnostic: (id: string, data: {
    raison: string;
    notes_medecin?: string;
  }) =>
    fetchAPI<Diagnostic>(`/api/ml/diagnostics/${id}/reject`, {
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
    }>('/api/ml/model/info'),
};

// ============================================================================
// ANALYTICS
// ============================================================================

export const analyticsAPI = {
  // Dashboard KPIs
  getDashboard: () =>
    fetchAPI<DashboardStats>('/api/analytics/dashboard'),

  // Distribution des diagnostics
  getDiagnosticsDistribution: (limit = 10) =>
    fetchAPI<Array<{ diagnostic: string; count: number; percentage: number }>>(
      `/api/analytics/diagnostics/distribution?limit=${limit}`
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
    }>('/api/analytics/performance/model'),

  // Consultations récentes
  getRecentConsultations: (limit = 10) =>
    fetchAPI<Consultation[]>(`/api/analytics/consultations/recent?limit=${limit}`),
  
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
    }>('/api/analytics/personnel/disponible'),
};

// ============================================================================
// AUTHENTICATION
// ============================================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    utilisateur_id: number;
    nom: string;
    prenoms: string;
    email: string;
    role: string;
    actif: boolean;
  };
}

export interface UserInfo {
  utilisateur_id: number;
  nom: string;
  prenoms: string;
  email: string;
  role: string;
  actif: boolean;
  created_at: string;
  last_login?: string;
}

export const authAPI = {
  // Connexion
  login: (credentials: LoginRequest) => {
    console.log('🌐 API: Envoi requête login à /api/auth/login');
    return fetchAPI<LoginResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  // Récupérer les infos de l'utilisateur connecté
  getMe: (token: string) =>
    fetchAPI<UserInfo>('/api/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }),

  // Déconnexion
  logout: (token: string) =>
    fetchAPI<{ message: string }>('/api/auth/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }),

  // Rafraîchir le token
  refresh: (token: string) =>
    fetchAPI<LoginResponse>('/api/auth/refresh', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }),
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

// ============================================================================
// ADMIN TYPES - Définis AVANT adminAPI
// ============================================================================

export interface AdminUser {
  utilisateur_id: number;
  nom: string;
  prenoms: string;
  email: string;
  role: 'admin' | 'medecin' | 'infirmier';
  actif: boolean;
  created_at: string;
  last_login?: string | null;
}

export interface AdminUserCreate {
  nom: string;
  prenoms: string;
  email: string;
  password: string;
  role: 'admin' | 'medecin' | 'infirmier';
}

export interface AdminUserUpdate {
  nom?: string;
  prenoms?: string;
  email?: string;
  role?: 'admin' | 'medecin' | 'infirmier';
  actif?: boolean;
  password?: string;
}

export interface AdminMedecin {
  medecin_id: number;
  nom: string;
  prenoms: string;
  specialite: string;
  telephone: string;
  disponible: boolean;
  created_at?: string;
}

export interface AdminMedecinCreate {
  nom: string;
  prenoms: string;
  specialite: string;
  telephone: string;
  disponible?: boolean;
}

export interface AdminInfirmier {
  infirmier_id: number;
  nom: string;
  prenoms: string;
  telephone: string;
  email?: string | null;
  disponible: boolean;
  created_at?: string;
}

export interface AdminInfirmierCreate {
  nom: string;
  prenoms: string;
  telephone: string;
  email?: string;
  disponible?: boolean;
}

export interface IAConfig {
  seuil_confiance_min: number;
  seuil_alerte_bas: number;
  n_estimators: number;
  max_depth: number;
}

// ============================================================================
// ADMIN — helper token-aware + CRUD complet
// ============================================================================

async function fetchAPIAuth<T>(token: string, endpoint: string, options: RequestInit = {}): Promise<T> {
  return fetchAPI<T>(endpoint, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });
}

export const adminAPI = {
  // Statut & logs système
  getStatus: (token: string) =>
    fetchAPIAuth<any>(token, '/api/admin/status'),
  getLogs: (token: string, lines = 200) =>
    fetchAPIAuth<{ lines: string[]; total: number; exists: boolean }>(token, `/api/admin/logs?lines=${lines}`),
  startTraining: (token: string, nEstimators = 200, maxDepth = 30) =>
    fetchAPIAuth<{ message: string; status: string }>(
      token, `/api/admin/train?n_estimators=${nEstimators}&max_depth=${maxDepth}`, { method: 'POST' }
    ),
  getTrainingStatus: (token: string) =>
    fetchAPIAuth<any>(token, '/api/admin/train/status'),
  cleanupModels: (token: string) =>
    fetchAPIAuth<{ removed: string[]; count: number; message: string }>(
      token, '/api/admin/cleanup/models', { method: 'POST' }
    ),
  cleanupLogs: (token: string) =>
    fetchAPIAuth<{ message: string; done: boolean }>(
      token, '/api/admin/cleanup/logs', { method: 'POST' }
    ),

  // CRUD Utilisateurs
  getUsers: (token: string) =>
    fetchAPIAuth<AdminUser[]>(token, '/api/admin/users'),
  createUser: (token: string, data: AdminUserCreate) =>
    fetchAPIAuth<AdminUser>(token, '/api/admin/users', { method: 'POST', body: JSON.stringify(data) }),
  updateUser: (token: string, id: number, data: AdminUserUpdate) =>
    fetchAPIAuth<AdminUser>(token, `/api/admin/users/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteUser: (token: string, id: number) =>
    fetchAPIAuth<{ message: string }>(token, `/api/admin/users/${id}`, { method: 'DELETE' }),

  // CRUD Médecins
  getMedecins: (token: string) =>
    fetchAPIAuth<AdminMedecin[]>(token, '/api/admin/personnel/medecins'),
  createMedecin: (token: string, data: AdminMedecinCreate) =>
    fetchAPIAuth<AdminMedecin>(token, '/api/admin/personnel/medecins', { method: 'POST', body: JSON.stringify(data) }),
  updateMedecin: (token: string, id: number, data: Partial<AdminMedecinCreate & { disponible: boolean }>) =>
    fetchAPIAuth<AdminMedecin>(token, `/api/admin/personnel/medecins/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteMedecin: (token: string, id: number) =>
    fetchAPIAuth<{ message: string }>(token, `/api/admin/personnel/medecins/${id}`, { method: 'DELETE' }),

  // CRUD Infirmiers
  getInfirmiers: (token: string) =>
    fetchAPIAuth<AdminInfirmier[]>(token, '/api/admin/personnel/infirmiers'),
  createInfirmier: (token: string, data: AdminInfirmierCreate) =>
    fetchAPIAuth<AdminInfirmier>(token, '/api/admin/personnel/infirmiers', { method: 'POST', body: JSON.stringify(data) }),
  updateInfirmier: (token: string, id: number, data: Partial<AdminInfirmierCreate & { disponible: boolean }>) =>
    fetchAPIAuth<AdminInfirmier>(token, `/api/admin/personnel/infirmiers/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteInfirmier: (token: string, id: number) =>
    fetchAPIAuth<{ message: string }>(token, `/api/admin/personnel/infirmiers/${id}`, { method: 'DELETE' }),

  // Config IA
  getIAConfig: (token: string) =>
    fetchAPIAuth<IAConfig>(token, '/api/admin/config/ia'),
  updateIAConfig: (token: string, data: Partial<IAConfig>) =>
    fetchAPIAuth<IAConfig>(token, '/api/admin/config/ia', { method: 'PUT', body: JSON.stringify(data) }),
};

// Export par défaut
export default {
  auth: authAPI,
  patients: patientsAPI,
  consultations: consultationsAPI,
  ml: mlAPI,
  analytics: analyticsAPI,
  health: healthAPI,
  admin: adminAPI,
};
