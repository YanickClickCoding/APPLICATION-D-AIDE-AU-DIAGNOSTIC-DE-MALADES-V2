export type Role = 'admin' | 'medecin' | 'infirmier';
export type StatutConsultation = 'en attente' | 'en cours' | 'terminée';

export interface Utilisateur {
  utilisateur_id: number;
  nom: string;
  prenoms: string;
  email: string;
  mot_de_passe: string;
  role: Role;
  created_at: string;
}

export interface Medecin {
  medecin_id: number;
  nom: string;
  prenoms: string;
  specialite: string;
  telephone: string;
  disponible: boolean;
  created_at: string;
}

export interface Consultation {
  consultation_id: number;
  nom_patient: string;
  date_heure: string;
  motif: string;
  medecin_id: number | null;
  statut: StatutConsultation;
  created_at: string;
}
