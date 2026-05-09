-- Script pour créer la base de données GASA SAD
-- Exécuter ce script dans MySQL

-- Supprimer la base si elle existe déjà (optionnel)
-- DROP DATABASE IF EXISTS gasa_sad;

-- Créer la nouvelle base de données
CREATE DATABASE IF NOT EXISTS gasa_sad CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Utiliser la base de données
USE gasa_sad;

-- Message de confirmation
SELECT 'Base de données gasa_sad créée avec succès!' AS message;
