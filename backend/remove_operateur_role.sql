-- ============================================================================
-- Script SQL : Suppression du rôle opérateur
-- Date : 3 mai 2026
-- Description : Supprime le rôle opérateur de la table utilisateurs
-- ============================================================================

USE sante_plus_ia;

-- ============================================================================
-- ÉTAPE 1 : Supprimer tous les utilisateurs avec le rôle opérateur
-- ============================================================================

DELETE FROM `utilisateurs` WHERE `role` = 'operateur';

-- ============================================================================
-- ÉTAPE 2 : Modifier la table pour supprimer le rôle opérateur de l'ENUM
-- ============================================================================

ALTER TABLE `utilisateurs` 
MODIFY COLUMN `role` ENUM('admin', 'medecin', 'infirmier') 
COLLATE utf8mb4_unicode_ci DEFAULT 'medecin';

-- ============================================================================
-- ÉTAPE 3 : Vérification
-- ============================================================================

-- Afficher tous les utilisateurs restants
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
-- FIN DU SCRIPT
-- ============================================================================
