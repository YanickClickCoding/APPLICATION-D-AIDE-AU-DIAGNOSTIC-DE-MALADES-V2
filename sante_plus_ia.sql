-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : sam. 02 mai 2026 à 21:48
-- Version du serveur : 8.0.31
-- Version de PHP : 8.0.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `sante_plus_ia`
--

-- --------------------------------------------------------

--
-- Structure de la table `analyses_ia`
--

DROP TABLE IF EXISTS `analyses_ia`;
CREATE TABLE IF NOT EXISTS `analyses_ia` (
  `id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `consultation_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `modele_ia` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `probabilite` float DEFAULT NULL,
  `diagnostics_suggeres` json DEFAULT NULL,
  `scoring_confiance` float DEFAULT NULL,
  `donnees_entree` json DEFAULT NULL,
  `temps_traitement` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `consultation_id` (`consultation_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `consultations`
--

DROP TABLE IF EXISTS `consultations`;
CREATE TABLE IF NOT EXISTS `consultations` (
  `consultation_id` int NOT NULL AUTO_INCREMENT,
  `nom_patient` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_heure` datetime NOT NULL,
  `motif` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `medecin_id` int DEFAULT NULL,
  `statut` enum('en attente','en cours','terminée') COLLATE utf8mb4_unicode_ci DEFAULT 'en attente',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`consultation_id`),
  KEY `medecin_id` (`medecin_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `consultations`
--

INSERT INTO `consultations` (`consultation_id`, `nom_patient`, `date_heure`, `motif`, `medecin_id`, `statut`, `created_at`) VALUES
(1, 'Jojo', '2026-05-02 20:30:30', 'maux de tête', NULL, 'en attente', '2026-05-02 20:30:48');

-- --------------------------------------------------------

--
-- Structure de la table `consultation_infirmiers`
--

DROP TABLE IF EXISTS `consultation_infirmiers`;
CREATE TABLE IF NOT EXISTS `consultation_infirmiers` (
  `consultation_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `infirmier_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`consultation_id`,`infirmier_id`),
  KEY `infirmier_id` (`infirmier_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `diagnostics`
--

DROP TABLE IF EXISTS `diagnostics`;
CREATE TABLE IF NOT EXISTS `diagnostics` (
  `id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `consultation_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `analyse_ia_id` char(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `medecin_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dossier_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code_icd10` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nom_maladie` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `certitude` float DEFAULT NULL,
  `statut` enum('PROVISOIRE','CONFIRMÉ','REJETÉ','ARCHIVÉ') COLLATE utf8mb4_unicode_ci DEFAULT 'PROVISOIRE',
  `severite` enum('LEGER','MODERE','GRAVE','CRITIQUE') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `justification` text COLLATE utf8mb4_unicode_ci,
  `date_validation` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `consultation_id` (`consultation_id`),
  KEY `analyse_ia_id` (`analyse_ia_id`),
  KEY `medecin_id` (`medecin_id`),
  KEY `dossier_id` (`dossier_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `dossiers_medicaux`
--

DROP TABLE IF EXISTS `dossiers_medicaux`;
CREATE TABLE IF NOT EXISTS `dossiers_medicaux` (
  `id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `patient_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `numero_dossier` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `antecedents_familiaux` text COLLATE utf8mb4_unicode_ci,
  `antecedents_personnels` text COLLATE utf8mb4_unicode_ci,
  `allergies` text COLLATE utf8mb4_unicode_ci,
  `date_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `patient_id` (`patient_id`),
  UNIQUE KEY `numero_dossier` (`numero_dossier`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `examens`
--

DROP TABLE IF EXISTS `examens`;
CREATE TABLE IF NOT EXISTS `examens` (
  `id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `consultation_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` enum('CLINIQUE','IMAGERIE','BIOLOGIE','ELECTROCARDIOGRAMME') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nom` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `resultats` text COLLATE utf8mb4_unicode_ci,
  `valeur_numerique` float DEFAULT NULL,
  `unite_mesure` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `statut` enum('DEMANDE','EN_COURS','REALISE','ANALYSE') COLLATE utf8mb4_unicode_ci DEFAULT 'DEMANDE',
  `date_examen` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `consultation_id` (`consultation_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `medecins`
--

DROP TABLE IF EXISTS `medecins`;
CREATE TABLE IF NOT EXISTS `medecins` (
  `medecin_id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenoms` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `specialite` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telephone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `disponible` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`medecin_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `medecins`
--

INSERT INTO `medecins` (`medecin_id`, `nom`, `prenoms`, `specialite`, `telephone`, `disponible`, `created_at`) VALUES
(1, 'AHOUANSOU', 'Gérard Koffi', 'Médecine Générale', '+229 97 00 11 22', 1, '2026-05-02 20:29:04'),
(2, 'DOSSOU', 'Marie-Claire Afi', 'Pédiatrie', '+229 96 33 44 55', 1, '2026-05-02 20:29:04'),
(3, 'AHOUANSOU', 'Gérard Koffi', 'Médecine Générale', '+229 97 00 11 22', 1, '2026-05-02 20:29:44'),
(4, 'DOSSOU', 'Marie-Claire Afi', 'Pédiatrie', '+229 96 33 44 55', 1, '2026-05-02 20:29:44');

-- --------------------------------------------------------

--
-- Structure de la table `medicaments`
--

DROP TABLE IF EXISTS `medicaments`;
CREATE TABLE IF NOT EXISTS `medicaments` (
  `id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ordonnance_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nom_commercial` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `denomination_commune` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dosage` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `forme` enum('COMPRIME','INJECTION','SIROP','CREME') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `quantite` int DEFAULT NULL,
  `frequence` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `voie_administration` enum('ORALE','INTRAVEINEUSE','CUTANEE','INTRAMUSCULAIRE') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `duree_jours` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ordonnance_id` (`ordonnance_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `ordonnances`
--

DROP TABLE IF EXISTS `ordonnances`;
CREATE TABLE IF NOT EXISTS `ordonnances` (
  `id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `traitement_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `medecin_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `patient_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dossier_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `posologie_generale` text COLLATE utf8mb4_unicode_ci,
  `date_emission` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `renouvelable` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `traitement_id` (`traitement_id`),
  KEY `medecin_id` (`medecin_id`),
  KEY `patient_id` (`patient_id`),
  KEY `dossier_id` (`dossier_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `patients`
--

DROP TABLE IF EXISTS `patients`;
CREATE TABLE IF NOT EXISTS `patients` (
  `id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenoms` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_naissance` date NOT NULL,
  `sexe` enum('M','F') COLLATE utf8mb4_unicode_ci NOT NULL,
  `groupe_sanguin` enum('A+','A-','B+','B-','AB+','AB-','O+','O-') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telephone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `adresse` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `signes_vitaux`
--

DROP TABLE IF EXISTS `signes_vitaux`;
CREATE TABLE IF NOT EXISTS `signes_vitaux` (
  `id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `consultation_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `infirmier_id` char(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_enregistrement` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `tension_systolique` int DEFAULT NULL,
  `tension_diastolique` int DEFAULT NULL,
  `frequence_cardiaque` int DEFAULT NULL,
  `temperature` float DEFAULT NULL,
  `frequence_respiratoire` int DEFAULT NULL,
  `saturation_oxygene` float DEFAULT NULL,
  `poids` float DEFAULT NULL,
  `taille` float DEFAULT NULL,
  `imc` float DEFAULT NULL,
  `glycemie` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `consultation_id` (`consultation_id`),
  KEY `infirmier_id` (`infirmier_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `suivis`
--

DROP TABLE IF EXISTS `suivis`;
CREATE TABLE IF NOT EXISTS `suivis` (
  `id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `patient_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `medecin_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `consultation_id` char(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `diagnostic_id` char(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `traitement_id` char(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dossier_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `numero_suivi` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_suivi` date NOT NULL,
  `etat_general` enum('EXCELLENT','BON','STABLE','DECLINE','CRITIQUE') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `amelioration` enum('EXCELLENTE','BON','MOYEN','MAUVAIS','DECLINE') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pourcentage_amelioration` float DEFAULT NULL,
  `adherence_traitement` float DEFAULT NULL,
  `statut` enum('EN_COURS','TERMINE_SUCCES','TERMINE_ECHEC','A_REPRENDRE') COLLATE utf8mb4_unicode_ci DEFAULT 'EN_COURS',
  `prochaine_consultation` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_suivi` (`numero_suivi`),
  KEY `patient_id` (`patient_id`),
  KEY `medecin_id` (`medecin_id`),
  KEY `consultation_id` (`consultation_id`),
  KEY `diagnostic_id` (`diagnostic_id`),
  KEY `traitement_id` (`traitement_id`),
  KEY `dossier_id` (`dossier_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `symptomes`
--

DROP TABLE IF EXISTS `symptomes`;
CREATE TABLE IF NOT EXISTS `symptomes` (
  `id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `consultation_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nom` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `severite` enum('LEGER','MODERE','SEVERE') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_apparition` date DEFAULT NULL,
  `duree_jours` int DEFAULT NULL,
  `zone_atteinte` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `frequence` enum('CONSTANT','INTERMITTENT','PROGRESSIF') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `consultation_id` (`consultation_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `traitements`
--

DROP TABLE IF EXISTS `traitements`;
CREATE TABLE IF NOT EXISTS `traitements` (
  `id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `diagnostic_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nom_traitement` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `type` enum('MEDICAMENTEUX','CHIRURGICAL','PHYSIQUE','PSYCHOLOGIQUE') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `duree_jours` int DEFAULT NULL,
  `date_debut` date DEFAULT NULL,
  `date_fin` date DEFAULT NULL,
  `statut` enum('PRESCRIT','EN_COURS','TERMINE','ABANDONNE','ECHEC') COLLATE utf8mb4_unicode_ci DEFAULT 'PRESCRIT',
  `objective_therapeutique` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `diagnostic_id` (`diagnostic_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `utilisateurs`
--

DROP TABLE IF EXISTS `utilisateurs`;
CREATE TABLE IF NOT EXISTS `utilisateurs` (
  `utilisateur_id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenoms` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mot_de_passe` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('admin','operateur') COLLATE utf8mb4_unicode_ci DEFAULT 'operateur',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`utilisateur_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `utilisateurs`
--

INSERT INTO `utilisateurs` (`utilisateur_id`, `nom`, `prenoms`, `email`, `mot_de_passe`, `role`, `created_at`) VALUES
(1, 'ADMIN', 'Super', 'admin@santeplus.bj', '$2y$10$PPd/pZSW9uZbvWVwWNqMlOAzB41iUDU1RFZHQYizShHuv4aZpRdSS', 'admin', '2026-05-02 20:29:04');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
