-- ============================================================================
-- Script pour ajouter la table infirmiers et les données
-- Base de données: sante_plus_ia
-- ============================================================================

USE sante_plus_ia;

-- ============================================================================
-- 1. CRÉER LA TABLE INFIRMIERS
-- ============================================================================

DROP TABLE IF EXISTS `infirmiers`;
CREATE TABLE IF NOT EXISTS `infirmiers` (
  `infirmier_id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenoms` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telephone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `disponible` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`infirmier_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 2. INSÉRER LES INFIRMIERS
-- ============================================================================

INSERT INTO infirmiers (nom, prenoms, telephone, email, disponible, created_at)
VALUES 
('KOFFI', 'Awa Sylvie', '+229 97 22 33 44', 'awa.koffi@sante.com', 1, NOW()),
('MENSAH', 'Kokou David', '+229 96 55 66 77', 'kokou.mensah@sante.com', 1, NOW()),
('AGBODJAN', 'Edem Patricia', '+229 95 88 99 00', 'edem.agbodjan@sante.com', 1, NOW()),
('TOSSOU', 'Yao Emmanuel', '+229 94 11 22 33', 'yao.tossou@sante.com', 1, NOW());

-- ============================================================================
-- 3. AJOUTER LES INFIRMIERS DANS LA TABLE UTILISATEURS
-- ============================================================================

INSERT INTO utilisateurs (nom, prenoms, email, mot_de_passe, role, created_at)
VALUES 
('KOFFI', 'Awa Sylvie', 'awa.koffi@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'operateur', NOW()),
('MENSAH', 'Kokou David', 'kokou.mensah@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'operateur', NOW()),
('AGBODJAN', 'Edem Patricia', 'edem.agbodjan@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'operateur', NOW()),
('TOSSOU', 'Yao Emmanuel', 'yao.tossou@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'operateur', NOW());

-- ============================================================================
-- VÉRIFICATION
-- ============================================================================

SELECT 'Infirmiers ajoutés avec succès!' AS Message;

SELECT 
    (SELECT COUNT(*) FROM infirmiers) AS Infirmiers,
    (SELECT COUNT(*) FROM utilisateurs WHERE role = 'operateur') AS Operateurs_Total;

SELECT * FROM infirmiers;

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================
