-- ============================================================================
-- Script d'insertion de données de test
-- Base de données: sante_plus_ia
-- ============================================================================

USE sante_plus_ia;

-- Désactiver les vérifications de clés étrangères temporairement
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- 1. UTILISATEURS (Admin, Opérateurs)
-- ============================================================================

INSERT INTO utilisateurs (nom, prenoms, email, mot_de_passe, role, created_at)
VALUES 
('ADMIN', 'Système', 'admin@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'admin', NOW()),
('DUBOIS', 'Marie Claire', 'marie.dubois@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'operateur', NOW()),
('MARTIN', 'Pierre Jean', 'pierre.martin@sante.com', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'operateur', NOW());

-- ============================================================================
-- 2. MÉDECINS
-- ============================================================================

INSERT INTO medecins (nom, prenoms, specialite, telephone, disponible, created_at)
VALUES 
('LEFEBVRE', 'Jean-Baptiste', 'Cardiologie', '+229 97 11 22 33', 1, NOW()),
('BERNARD', 'Sophie Marie', 'Pédiatrie', '+229 96 44 55 66', 1, NOW()),
('PETIT', 'Thomas André', 'Dermatologie', '+229 95 77 88 99', 1, NOW()),
('ROBERT', 'Claire Isabelle', 'Pneumologie', '+229 94 00 11 22', 1, NOW()),
('MOREAU', 'Luc François', 'Neurologie', '+229 93 33 44 55', 1, NOW());

-- ============================================================================
-- 3. PATIENTS
-- ============================================================================

INSERT INTO patients (id, nom, prenoms, date_naissance, sexe, adresse, telephone, email, groupe_sanguin, created_at)
VALUES 
(UUID(), 'Dupont', 'Jean', '1980-05-15', 'M', '12 Rue de la Paix, 75001 Paris', '0601020304', 'jean.dupont@email.com', 'O+', NOW()),
(UUID(), 'Martin', 'Sophie', '1992-08-22', 'F', '45 Avenue des Champs, 69001 Lyon', '0602030405', 'sophie.martin@email.com', 'A+', NOW()),
(UUID(), 'Bernard', 'Luc', '1975-12-10', 'M', '8 Boulevard Victor Hugo, 31000 Toulouse', '0603040506', 'luc.bernard@email.com', 'B+', NOW()),
(UUID(), 'Petit', 'Marie', '1988-03-18', 'F', '23 Rue du Commerce, 13001 Marseille', '0604050607', 'marie.petit@email.com', 'AB+', NOW()),
(UUID(), 'Durand', 'Pierre', '1965-07-25', 'M', '67 Rue de la République, 33000 Bordeaux', '0605060708', 'pierre.durand@email.com', 'O-', NOW()),
(UUID(), 'Moreau', 'Claire', '1995-11-30', 'F', '34 Avenue Jean Jaurès, 59000 Lille', '0606070809', 'claire.moreau@email.com', 'A-', NOW()),
(UUID(), 'Simon', 'Marc', '1970-09-05', 'M', '56 Rue Nationale, 44000 Nantes', '0607080910', 'marc.simon@email.com', 'B-', NOW()),
(UUID(), 'Laurent', 'Julie', '1985-04-12', 'F', '89 Boulevard Gambetta, 67000 Strasbourg', '0608091011', 'julie.laurent@email.com', 'O+', NOW()),
(UUID(), 'Leroy', 'Antoine', '1978-06-20', 'M', '12 Place de la Comédie, 34000 Montpellier', '0609101112', 'antoine.leroy@email.com', 'A+', NOW()),
(UUID(), 'Roux', 'Isabelle', '1990-02-14', 'F', '45 Rue de la Liberté, 35000 Rennes', '0610111213', 'isabelle.roux@email.com', 'AB-', NOW());

-- ============================================================================
-- 4. CONSULTATIONS avec SYMPTÔMES et SIGNES VITAUX
-- ============================================================================

-- Récupérer les IDs des médecins pour les consultations
SET @medecin1 = (SELECT medecin_id FROM medecins WHERE nom = 'LEFEBVRE' LIMIT 1);
SET @medecin2 = (SELECT medecin_id FROM medecins WHERE nom = 'BERNARD' LIMIT 1);
SET @medecin3 = (SELECT medecin_id FROM medecins WHERE nom = 'PETIT' LIMIT 1);

-- Consultation 1: Grippe
INSERT INTO consultations (nom_patient, date_heure, motif, medecin_id, statut, created_at)
VALUES ('Jean Dupont', NOW() - INTERVAL 2 DAY, 'Fièvre et toux depuis 3 jours', @medecin1, 'terminée', NOW() - INTERVAL 2 DAY);

SET @consult1 = LAST_INSERT_ID();

INSERT INTO symptomes (id, consultation_id, nom, severite, duree_jours, description)
VALUES 
(UUID(), CAST(@consult1 AS CHAR(36)), 'Fièvre', 'MODERE', 3, 'Température élevée'),
(UUID(), CAST(@consult1 AS CHAR(36)), 'Toux', 'MODERE', 3, 'Toux sèche persistante'),
(UUID(), CAST(@consult1 AS CHAR(36)), 'Fatigue', 'SEVERE', 3, 'Fatigue intense'),
(UUID(), CAST(@consult1 AS CHAR(36)), 'Mal de tête', 'LEGER', 2, 'Céphalées');

INSERT INTO signes_vitaux (id, consultation_id, tension_systolique, tension_diastolique, frequence_cardiaque, temperature, frequence_respiratoire, saturation_oxygene, poids, taille, imc)
VALUES (UUID(), CAST(@consult1 AS CHAR(36)), 125, 80, 88, 38.5, 18, 97, 75, 175, 24.5);

-- Consultation 2: Hypertension
INSERT INTO consultations (nom_patient, date_heure, motif, medecin_id, statut, created_at)
VALUES ('Sophie Martin', NOW() - INTERVAL 5 DAY, 'Contrôle tension artérielle', @medecin2, 'terminée', NOW() - INTERVAL 5 DAY);

SET @consult2 = LAST_INSERT_ID();

INSERT INTO symptomes (id, consultation_id, nom, severite, duree_jours, description)
VALUES 
(UUID(), CAST(@consult2 AS CHAR(36)), 'Maux de tête', 'MODERE', 7, 'Céphalées matinales'),
(UUID(), CAST(@consult2 AS CHAR(36)), 'Vertiges', 'LEGER', 5, 'Sensation de vertige');

INSERT INTO signes_vitaux (id, consultation_id, tension_systolique, tension_diastolique, frequence_cardiaque, temperature, frequence_respiratoire, saturation_oxygene, poids, taille, imc)
VALUES (UUID(), CAST(@consult2 AS CHAR(36)), 155, 95, 75, 36.8, 16, 98, 68, 165, 25.0);

-- Consultation 3: Diabète Type 2
INSERT INTO consultations (nom_patient, date_heure, motif, medecin_id, statut, created_at)
VALUES ('Luc Bernard', NOW() - INTERVAL 10 DAY, 'Fatigue et soif excessive', @medecin1, 'terminée', NOW() - INTERVAL 10 DAY);

SET @consult3 = LAST_INSERT_ID();

INSERT INTO symptomes (id, consultation_id, nom, severite, duree_jours, description)
VALUES 
(UUID(), CAST(@consult3 AS CHAR(36)), 'Fatigue', 'SEVERE', 30, 'Fatigue chronique'),
(UUID(), CAST(@consult3 AS CHAR(36)), 'Soif excessive', 'MODERE', 20, 'Polydipsie'),
(UUID(), CAST(@consult3 AS CHAR(36)), 'Urination fréquente', 'MODERE', 20, 'Polyurie'),
(UUID(), CAST(@consult3 AS CHAR(36)), 'Vision floue', 'LEGER', 15, 'Troubles visuels');

INSERT INTO signes_vitaux (id, consultation_id, tension_systolique, tension_diastolique, frequence_cardiaque, temperature, frequence_respiratoire, saturation_oxygene, poids, taille, imc)
VALUES (UUID(), CAST(@consult3 AS CHAR(36)), 140, 88, 72, 36.6, 15, 98, 95, 178, 30.0);

-- Consultation 4: Asthme
INSERT INTO consultations (nom_patient, date_heure, motif, medecin_id, statut, created_at)
VALUES ('Marie Petit', NOW() - INTERVAL 1 DAY, 'Difficulté respiratoire', @medecin3, 'en cours', NOW() - INTERVAL 1 DAY);

SET @consult4 = LAST_INSERT_ID();

INSERT INTO symptomes (id, consultation_id, nom, severite, duree_jours, description)
VALUES 
(UUID(), CAST(@consult4 AS CHAR(36)), 'Essoufflement', 'SEVERE', 2, 'Dyspnée'),
(UUID(), CAST(@consult4 AS CHAR(36)), 'Sifflement respiratoire', 'MODERE', 2, 'Wheezing'),
(UUID(), CAST(@consult4 AS CHAR(36)), 'Toux', 'MODERE', 3, 'Toux sèche nocturne');

INSERT INTO signes_vitaux (id, consultation_id, tension_systolique, tension_diastolique, frequence_cardiaque, temperature, frequence_respiratoire, saturation_oxygene, poids, taille, imc)
VALUES (UUID(), CAST(@consult4 AS CHAR(36)), 118, 75, 95, 36.9, 24, 93, 62, 168, 22.0);

-- Consultation 5: Migraine
INSERT INTO consultations (nom_patient, date_heure, motif, medecin_id, statut, created_at)
VALUES ('Pierre Durand', NOW(), 'Maux de tête intenses', @medecin1, 'en cours', NOW());

SET @consult5 = LAST_INSERT_ID();

INSERT INTO symptomes (id, consultation_id, nom, severite, duree_jours, description)
VALUES 
(UUID(), CAST(@consult5 AS CHAR(36)), 'Céphalée', 'SEVERE', 1, 'Douleur pulsatile unilatérale'),
(UUID(), CAST(@consult5 AS CHAR(36)), 'Nausées', 'MODERE', 1, 'Sensation nauséeuse'),
(UUID(), CAST(@consult5 AS CHAR(36)), 'Photophobie', 'MODERE', 1, 'Sensibilité à la lumière'),
(UUID(), CAST(@consult5 AS CHAR(36)), 'Phonophobie', 'LEGER', 1, 'Sensibilité au bruit');

INSERT INTO signes_vitaux (id, consultation_id, tension_systolique, tension_diastolique, frequence_cardiaque, temperature, frequence_respiratoire, saturation_oxygene, poids, taille, imc)
VALUES (UUID(), CAST(@consult5 AS CHAR(36)), 130, 82, 78, 36.7, 16, 98, 70, 172, 23.7);

-- ============================================================================
-- 5. ANALYSES IA (Diagnostics générés par l'IA)
-- ============================================================================

INSERT INTO analyses_ia (id, consultation_id, modele_ia, probabilite, diagnostics_suggeres, scoring_confiance, created_at)
VALUES 
(UUID(), CAST(@consult1 AS CHAR(36)), 'RandomForest_v1.0', 0.92, JSON_ARRAY(JSON_OBJECT('maladie', 'Grippe', 'confiance', 0.92)), 0.92, NOW() - INTERVAL 2 DAY),
(UUID(), CAST(@consult2 AS CHAR(36)), 'RandomForest_v1.0', 0.88, JSON_ARRAY(JSON_OBJECT('maladie', 'Hypertension artérielle', 'confiance', 0.88)), 0.88, NOW() - INTERVAL 5 DAY),
(UUID(), CAST(@consult3 AS CHAR(36)), 'RandomForest_v1.0', 0.85, JSON_ARRAY(JSON_OBJECT('maladie', 'Diabète Type 2', 'confiance', 0.85)), 0.85, NOW() - INTERVAL 10 DAY),
(UUID(), CAST(@consult4 AS CHAR(36)), 'RandomForest_v1.0', 0.90, JSON_ARRAY(JSON_OBJECT('maladie', 'Asthme', 'confiance', 0.90)), 0.90, NOW() - INTERVAL 1 DAY),
(UUID(), CAST(@consult5 AS CHAR(36)), 'RandomForest_v1.0', 0.87, JSON_ARRAY(JSON_OBJECT('maladie', 'Migraine', 'confiance', 0.87)), 0.87, NOW());

-- Réactiver les vérifications de clés étrangères
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- RÉSUMÉ DES DONNÉES INSÉRÉES
-- ============================================================================

SELECT 'Données insérées avec succès!' AS Message;

SELECT 
    (SELECT COUNT(*) FROM utilisateurs) AS Utilisateurs,
    (SELECT COUNT(*) FROM medecins) AS Medecins,
    (SELECT COUNT(*) FROM patients) AS Patients,
    (SELECT COUNT(*) FROM consultations) AS Consultations,
    (SELECT COUNT(*) FROM symptomes) AS Symptomes,
    (SELECT COUNT(*) FROM signes_vitaux) AS SignesVitaux,
    (SELECT COUNT(*) FROM analyses_ia) AS AnalysesIA;

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================
