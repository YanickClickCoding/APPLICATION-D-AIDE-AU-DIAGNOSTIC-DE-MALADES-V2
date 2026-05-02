import type { Utilisateur, Medecin, Consultation } from './types';

const defaultUtilisateurs: Utilisateur[] = [
  {
    utilisateur_id: 1,
    nom: 'ADMIN',
    prenoms: 'Super',
    email: 'admin@santeplus.bj',
    mot_de_passe: 'Admin123', // Storing in plain text for this mock since there's no real backend
    role: 'admin',
    created_at: new Date().toISOString()
  }
];

const defaultMedecins: Medecin[] = [
  {
    medecin_id: 1,
    nom: 'AHOUANSOU',
    prenoms: 'Gérard Koffi',
    specialite: 'Médecine Générale',
    telephone: '+229 97 00 11 22',
    disponible: true,
    created_at: new Date().toISOString()
  },
  {
    medecin_id: 2,
    nom: 'DOSSOU',
    prenoms: 'Marie-Claire Afi',
    specialite: 'Pédiatrie',
    telephone: '+229 96 33 44 55',
    disponible: true,
    created_at: new Date().toISOString()
  }
];

const defaultConsultations: Consultation[] = [];

// Initialize LocalStorage if empty
export const initDB = () => {
  if (!localStorage.getItem('sp_utilisateurs')) {
    localStorage.setItem('sp_utilisateurs', JSON.stringify(defaultUtilisateurs));
  }
  if (!localStorage.getItem('sp_medecins')) {
    localStorage.setItem('sp_medecins', JSON.stringify(defaultMedecins));
  }
  if (!localStorage.getItem('sp_consultations')) {
    localStorage.setItem('sp_consultations', JSON.stringify(defaultConsultations));
  }
};

export const getUtilisateurs = (): Utilisateur[] => {
  try {
    return JSON.parse(localStorage.getItem('sp_utilisateurs') || '[]') || [];
  } catch { return []; }
};
export const getMedecins = (): Medecin[] => {
  try {
    return JSON.parse(localStorage.getItem('sp_medecins') || '[]') || [];
  } catch { return []; }
};
export const getConsultations = (): Consultation[] => {
  try {
    return JSON.parse(localStorage.getItem('sp_consultations') || '[]') || [];
  } catch { return []; }
};

export const saveUtilisateurs = (data: Utilisateur[]) => localStorage.setItem('sp_utilisateurs', JSON.stringify(data || []));
export const saveMedecins = (data: Medecin[]) => localStorage.setItem('sp_medecins', JSON.stringify(data || []));
export const saveConsultations = (data: Consultation[]) => localStorage.setItem('sp_consultations', JSON.stringify(data || []));
