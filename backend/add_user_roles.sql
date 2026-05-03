-- ============================================================================
-- Script SQL : Ajout des rôles médecin et infirmier
-- Date : 3 mai 2026
-- Description : Modification de la table utilisateurs pour ajouter les rôles
--               médecin et infirmier, puis création des comptes utilisateurs
-- ============================================================================

USE sante_plus_ia;

-- ============================================================================
-- ÉTAPE 1 : Modifier la table utilisateurs pour ajouter les nouveaux rôles
-- ============================================================================

ALTER TABLE `utilisateurs` 
MODIFY COLUMN `role` ENUM('admin', 'medecin', 'infirmier') 
COLLATE utf8mb4_unicode_ci DEFAULT 'medecin';

-- ============================================================================
-- ÉTAPE 2 : Supprimer les opérateurs existants
-- ============================================================================

DELETE FROM `utilisateurs` WHERE `role` = 'operateur';

-- ============================================================================
-- ÉTAPE 3 : Créer des comptes utilisateurs pour les médecins existants
-- ============================================================================

-- Mot de passe par défaut : admin123
-- Hash bcrypt : $2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS

-- Médecin 1 : Dr. AHOUANSOU Gérard Koffi (Médecine Générale)
INSERT INTO `utilisateurs` (`nom`, `prenoms`, `email`, `mot_de_passe`, `role`, `created_at`)
SELECT 'AHOUANSOU', 'Gérard Koffi', 'gerard.ahouansou@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'medecin', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `utilisateurs` WHERE `email` = 'gerard.ahouansou@sante.com');

-- Médecin 2 : Dr. DOSSOU Marie-Claire Afi (Pédiatrie)
INSERT INTO `utilisateurs` (`nom`, `prenoms`, `email`, `mot_de_passe`, `role`, `created_at`)
SELECT 'DOSSOU', 'Marie-Claire Afi', 'marie.dossou@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'medecin', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `utilisateurs` WHERE `email` = 'marie.dossou@sante.com');

-- Médecin 3 : Dr. LEFEBVRE Jean-Baptiste (Cardiologie)
INSERT INTO `utilisateurs` (`nom`, `prenoms`, `email`, `mot_de_passe`, `role`, `created_at`)
SELECT 'LEFEBVRE', 'Jean-Baptiste', 'jean.lefebvre@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'medecin', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `utilisateurs` WHERE `email` = 'jean.lefebvre@sante.com');

-- Médecin 4 : Dr. BERNARD Sophie Marie (Pédiatrie)
INSERT INTO `utilisateurs` (`nom`, `prenoms`, `email`, `mot_de_passe`, `role`, `created_at`)
SELECT 'BERNARD', 'Sophie Marie', 'sophie.bernard@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'medecin', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `utilisateurs` WHERE `email` = 'sophie.bernard@sante.com');

-- Médecin 5 : Dr. PETIT Thomas André (Dermatologie)
INSERT INTO `utilisateurs` (`nom`, `prenoms`, `email`, `mot_de_passe`, `role`, `created_at`)
SELECT 'PETIT', 'Thomas André', 'thomas.petit@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'medecin', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `utilisateurs` WHERE `email` = 'thomas.petit@sante.com');

-- ============================================================================
-- ÉTAPE 4 : Créer des comptes utilisateurs pour les infirmiers
-- ============================================================================

-- Infirmier 1 : KOUASSI Aya
INSERT INTO `utilisateurs` (`nom`, `prenoms`, `email`, `mot_de_passe`, `role`, `created_at`)
SELECT 'KOUASSI', 'Aya', 'aya.kouassi@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'infirmier', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `utilisateurs` WHERE `email` = 'aya.kouassi@sante.com');

-- Infirmier 2 : MENSAH Kofi
INSERT INTO `utilisateurs` (`nom`, `prenoms`, `email`, `mot_de_passe`, `role`, `created_at`)
SELECT 'MENSAH', 'Kofi', 'kofi.mensah@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'infirmier', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `utilisateurs` WHERE `email` = 'kofi.mensah@sante.com');

-- Infirmier 3 : DIALLO Fatoumata
INSERT INTO `utilisateurs` (`nom`, `prenoms`, `email`, `mot_de_passe`, `role`, `created_at`)
SELECT 'DIALLO', 'Fatoumata', 'fatoumata.diallo@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'infirmier', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `utilisateurs` WHERE `email` = 'fatoumata.diallo@sante.com');

-- Infirmier 4 : TRAORE Moussa
INSERT INTO `utilisateurs` (`nom`, `prenoms`, `email`, `mot_de_passe`, `role`, `created_at`)
SELECT 'TRAORE', 'Moussa', 'moussa.traore@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'infirmier', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `utilisateurs` WHERE `email` = 'moussa.traore@sante.com');

-- ============================================================================
-- ÉTAPE 5 : Vérification des données insérées
-- ============================================================================

-- Afficher tous les utilisateurs par rôle
SELECT 
    utilisateur_id,
    nom,
    prenoms,
    email,
    role,
    created_at
FROM utilisateurs
ORDER BY 
    FIELD(role, 'admin', 'medecin', 'infirmier'),
    nom;

-- Statistiques par rôle
SELECT 
    role,
    COUNT(*) as nombre
FROM utilisateurs
GROUP BY role
ORDER BY FIELD(role, 'admin', 'medecin', 'infirmier');

-- ============================================================================
-- NOTES IMPORTANTES
-- ============================================================================

-- 1. Tous les comptes utilisent le mot de passe : admin123
-- 2. Le hash bcrypt est : $2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS
-- 3. En production, changez TOUS les mots de passe !
-- 4. Les médecins et infirmiers peuvent maintenant se connecter au système
-- 5. Permissions à implémenter dans le backend selon le rôle
-- 6. Les opérateurs ont été supprimés du système

-- ============================================================================
-- RÉSUMÉ DES COMPTES CRÉÉS
-- ============================================================================

-- ADMIN (1) :
--   - admin@santeplus.bj (mot de passe: admin123)

-- MÉDECINS (5) :
--   - gerard.ahouansou@sante.com (mot de passe: admin123)
--   - marie.dossou@sante.com (mot de passe: admin123)
--   - jean.lefebvre@sante.com (mot de passe: admin123)
--   - sophie.bernard@sante.com (mot de passe: admin123)
--   - thomas.petit@sante.com (mot de passe: admin123)

-- INFIRMIERS (4) :
--   - aya.kouassi@sante.com (mot de passe: admin123)
--   - kofi.mensah@sante.com (mot de passe: admin123)
--   - fatoumata.diallo@sante.com (mot de passe: admin123)
--   - moussa.traore@sante.com (mot de passe: admin123)

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================
