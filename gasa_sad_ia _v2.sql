-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : mer. 13 mai 2026 à 15:34
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
  `analyse_id` int NOT NULL AUTO_INCREMENT,
  `consultation_id` int NOT NULL,
  `modele_ia` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `probabilite` float DEFAULT NULL,
  `diagnostics_suggeres` json DEFAULT NULL,
  `scoring_confiance` float DEFAULT NULL,
  `donnees_entree` json DEFAULT NULL,
  `temps_traitement` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`analyse_id`),
  KEY `consultation_id` (`consultation_id`)
) ENGINE=MyISAM AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `analyses_ia`
--

INSERT INTO `analyses_ia` (`analyse_id`, `consultation_id`, `modele_ia`, `probabilite`, `diagnostics_suggeres`, `scoring_confiance`, `donnees_entree`, `temps_traitement`, `created_at`) VALUES
(2, 33, 'RandomForest_v1.0_Finale', 0.87, '[{\"maladie\": \"Fievre typhoide\", \"probabilite\": 0.87}, {\"maladie\": \"Paludisme\", \"probabilite\": 0.08}, {\"maladie\": \"Hepatite virale\", \"probabilite\": 0.05}]', 0.87, '{\"phase\": \"finale\", \"symptomes\": [\"Fievre\", \"Douleurs abdominales\", \"Cephalees\"]}', NULL, '2026-05-06 17:40:43'),
(3, 34, 'RandomForest_v1.0_Preliminaire', 0.0433978, '[{\"maladie\": \"Acné\", \"probabilite\": 0.043397799219553584}, {\"maladie\": \"Hypertrophie bénigne de prostate\", \"probabilite\": 0.04176953553106988}, {\"maladie\": \"Alzheimer\", \"probabilite\": 0.040975232199333946}]', 0.0433978, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Maux de tête forts, fatigue chronique, perte de mobilités, vision floue\", \"severite\": \"Sévère\", \"duree_jours\": 14}], \"signes_vitaux\": {\"poids\": 70, \"taille\": 175, \"temperature\": 37, \"saturation_o2\": 98, \"tension_systolique\": 120, \"frequence_cardiaque\": 70, \"tension_diastolique\": 80, \"frequence_respiratoire\": 16}}', NULL, '2026-05-06 21:49:27'),
(4, 38, 'RandomForest_v1.0_Finale', 0.05, '[{\"maladie\": \"Alzheimer\", \"probabilite\": 0.05}, {\"maladie\": \"Scléroderomie\", \"probabilite\": 0.03}, {\"maladie\": \"Vitiligo\", \"probabilite\": 0.03}]', 0.05, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"NFS (Numération Formule Sanguine)\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-07\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP (Protéine C-réactive)\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-07\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}]}', NULL, '2026-05-07 12:17:55'),
(5, 39, 'RandomForest_v1.0_Finale', 0.0366302, '[{\"maladie\": \"Alzheimer\", \"probabilite\": 0.036630188945440505}, {\"maladie\": \"Acné\", \"probabilite\": 0.03166905847018778}, {\"maladie\": \"Dégénérescence maculaire\", \"probabilite\": 0.03048886113143642}]', 0.0366302, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"OIIII\", \"type\": \"IMAGERIE\", \"resultats\": \"\"}]}', NULL, '2026-05-07 17:13:58'),
(6, 41, 'RandomForest_v1.0_Preliminaire', 0.124142, '[{\"maladie\": \"Malaria\", \"probabilite\": 0.12414203264151664}, {\"maladie\": \"Pyélonéphrite\", \"probabilite\": 0.060333333333333336}, {\"maladie\": \"Hépatite A\", \"probabilite\": 0.058888763679162605}]', 0.124142, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Fièvre \", \"severite\": \"Sévère\", \"duree_jours\": 3}, {\"nom\": \"Frissons \", \"severite\": \"Sévère\", \"duree_jours\": 3}, {\"nom\": \"Céphalées \", \"severite\": \"Sévère\", \"duree_jours\": 3}, {\"nom\": \" Douleurs musculaires\", \"severite\": \"Modérée\", \"duree_jours\": 3}, {\"nom\": \"Nausées \", \"severite\": \"Modérée\", \"duree_jours\": 2}, {\"nom\": \"Fatigue \", \"severite\": \"Sévère\", \"duree_jours\": 3}], \"signes_vitaux\": {\"poids\": 72, \"taille\": 175, \"temperature\": 39.8, \"saturation_o2\": 98, \"tension_systolique\": 110, \"frequence_cardiaque\": 105, \"tension_diastolique\": 70, \"frequence_respiratoire\": 96}}', NULL, '2026-05-08 02:18:22'),
(7, 41, 'RandomForest_v1.0_Finale', 0.124142, '[{\"maladie\": \"Malaria\", \"probabilite\": 0.12414203264151664}, {\"maladie\": \"Pyélonéphrite\", \"probabilite\": 0.060333333333333336}, {\"maladie\": \"Hépatite A\", \"probabilite\": 0.058888763679162605}]', 0.124142, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"NFS (Numération Formule Sanguine)\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-08\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP (Protéine C-réactive)\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-08\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"Frottis sanguin + GE\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-08\", \"description\": \"Recherche Plasmodium\", \"isSuggested\": true, \"unite_mesure\": \"résultat\"}, {\"nom\": \"TDR Paludisme\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-08\", \"description\": \"Test rapide antigènes Plasmodium\", \"isSuggested\": true, \"unite_mesure\": \"résultat\"}], \"symptomes\": [{\"nom\": \"Fièvre \", \"severite\": \"Sévère\", \"duree_jours\": 3}, {\"nom\": \"Frissons \", \"severite\": \"Sévère\", \"duree_jours\": 3}, {\"nom\": \"Céphalées \", \"severite\": \"Sévère\", \"duree_jours\": 3}, {\"nom\": \" Douleurs musculaires\", \"severite\": \"Modérée\", \"duree_jours\": 3}, {\"nom\": \"Nausées \", \"severite\": \"Modérée\", \"duree_jours\": 2}, {\"nom\": \"Fatigue \", \"severite\": \"Sévère\", \"duree_jours\": 3}], \"signes_vitaux\": {\"poids\": 72, \"taille\": 175, \"temperature\": 39.8, \"saturation_o2\": 98, \"tension_systolique\": 110, \"frequence_cardiaque\": 105, \"tension_diastolique\": 70, \"frequence_respiratoire\": 96}}', NULL, '2026-05-08 02:18:22'),
(8, 42, 'RandomForest_v1.0_Preliminaire', 0.112631, '[{\"maladie\": \"Varicelle\", \"probabilite\": 0.11263065646306895}, {\"maladie\": \"Syphilis\", \"probabilite\": 0.07463287097699225}, {\"maladie\": \"Laryngite\", \"probabilite\": 0.0412489751477621}]', 0.112631, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Fièvre\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Yeux de couleur jaune\", \"severite\": \"Modérée\", \"duree_jours\": 5}, {\"nom\": \"fatigue chronique\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"des courbatures \", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Perte d\'appétit\", \"severite\": \"Modérée\", \"duree_jours\": 1}], \"signes_vitaux\": {\"poids\": 60, \"taille\": 180, \"temperature\": 39.9, \"saturation_o2\": 98, \"tension_systolique\": 120, \"frequence_cardiaque\": 70, \"tension_diastolique\": 80, \"frequence_respiratoire\": 16}}', NULL, '2026-05-08 16:37:50'),
(9, 42, 'RandomForest_v1.0_Finale', 0.112631, '[{\"maladie\": \"Varicelle\", \"probabilite\": 0.11263065646306894}, {\"maladie\": \"Syphilis\", \"probabilite\": 0.07463287097699225}, {\"maladie\": \"Laryngite\", \"probabilite\": 0.0412489751477621}]', 0.112631, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"NFS (Numération Formule Sanguine)\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-08\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP (Protéine C-réactive)\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-08\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}], \"symptomes\": [{\"nom\": \"Fièvre\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Yeux de couleur jaune\", \"severite\": \"Modérée\", \"duree_jours\": 5}, {\"nom\": \"fatigue chronique\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"des courbatures \", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Perte d\'appétit\", \"severite\": \"Modérée\", \"duree_jours\": 1}], \"signes_vitaux\": {\"poids\": 60, \"taille\": 180, \"temperature\": 39.9, \"saturation_o2\": 98, \"tension_systolique\": 120, \"frequence_cardiaque\": 70, \"tension_diastolique\": 80, \"frequence_respiratoire\": 16}}', NULL, '2026-05-08 16:37:50'),
(10, 53, 'RandomForest_v1.0_Preliminaire', 0.128571, '[{\"maladie\": \"Lymphome\", \"probabilite\": 0.12857142857142856}, {\"maladie\": \"Syphilis\", \"probabilite\": 0.07142857142857142}, {\"maladie\": \"VIH/SIDA\", \"probabilite\": 0.05142857142857143}]', 0.128571, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Adénopathie\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Sueurs nocturnes\", \"severite\": \"Modérée\", \"duree_jours\": 4}, {\"nom\": \"Fièvre\", \"severite\": \"Modérée\", \"duree_jours\": 3}], \"signes_vitaux\": {\"poids\": 60, \"taille\": 180, \"temperature\": 36.66, \"saturation_o2\": 98, \"tension_systolique\": 108, \"frequence_cardiaque\": 90, \"tension_diastolique\": 88, \"frequence_respiratoire\": 17}}', NULL, '2026-05-09 15:32:44'),
(11, 53, 'RandomForest_v1.0_Finale', 0.128571, '[{\"maladie\": \"Lymphome\", \"probabilite\": 0.12857142857142856}, {\"maladie\": \"Syphilis\", \"probabilite\": 0.07142857142857142}, {\"maladie\": \"VIH/SIDA\", \"probabilite\": 0.05142857142857143}]', 0.128571, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"NFS (Numération Formule Sanguine)\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-09\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP (Protéine C-réactive)\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-09\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}], \"symptomes\": [{\"nom\": \"Adénopathie\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Sueurs nocturnes\", \"severite\": \"Modérée\", \"duree_jours\": 4}, {\"nom\": \"Fièvre\", \"severite\": \"Modérée\", \"duree_jours\": 3}], \"signes_vitaux\": {\"poids\": 60, \"taille\": 180, \"temperature\": 36.66, \"saturation_o2\": 98, \"tension_systolique\": 108, \"frequence_cardiaque\": 90, \"tension_diastolique\": 88, \"frequence_respiratoire\": 17}}', NULL, '2026-05-09 15:32:44'),
(12, 55, 'RandomForest_v1.0_Preliminaire', 0.134286, '[{\"maladie\": \"Hyperthyroïdie\", \"probabilite\": 0.13428571428571429}, {\"maladie\": \"Diabète Type 1\", \"probabilite\": 0.10857142857142855}, {\"maladie\": \"Lymphome\", \"probabilite\": 0.08285714285714285}]', 0.134286, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Perte de poids\", \"severite\": \"Modérée\", \"duree_jours\": 60}, {\"nom\": \"Hémoptysie\", \"severite\": \"Légère\", \"duree_jours\": 59}, {\"nom\": \"Toux persistante\", \"severite\": \"Légère\", \"duree_jours\": 58}, {\"nom\": \"Fatigue\", \"severite\": \"Légère\", \"duree_jours\": 60}], \"signes_vitaux\": {\"poids\": 60, \"taille\": 155.7, \"temperature\": 37.4, \"saturation_o2\": 96.9, \"tension_systolique\": 109.41, \"frequence_cardiaque\": 51.33, \"tension_diastolique\": 97.72, \"frequence_respiratoire\": 10.55}}', NULL, '2026-05-09 18:05:37'),
(13, 55, 'RandomForest_v1.0_Finale', 0.142857, '[{\"maladie\": \"Hyperthyroïdie\", \"probabilite\": 0.14285714285714285}, {\"maladie\": \"Diabète Type 1\", \"probabilite\": 0.10285714285714286}, {\"maladie\": \"Insuffisance rénale chronique\", \"probabilite\": 0.08571428571428572}]', 0.142857, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-09\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-09\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}], \"symptomes\": [{\"nom\": \"Perte de poids\", \"severite\": \"Modérée\", \"duree_jours\": 60}, {\"nom\": \"Hémoptysie\", \"severite\": \"Légère\", \"duree_jours\": 59}, {\"nom\": \"Toux persistante\", \"severite\": \"Légère\", \"duree_jours\": 58}, {\"nom\": \"Fatigue\", \"severite\": \"Légère\", \"duree_jours\": 60}], \"signes_vitaux\": {\"poids\": 60, \"taille\": 155.7, \"temperature\": 37.4, \"saturation_o2\": 96.9, \"tension_systolique\": 109.41, \"frequence_cardiaque\": 51.33, \"tension_diastolique\": 97.72, \"frequence_respiratoire\": 10.55}}', NULL, '2026-05-09 18:05:37'),
(14, 57, 'RandomForest_v1.0_Preliminaire', 0.106, '[{\"maladie\": \"Athérosclérose\", \"probabilite\": 0.106}, {\"maladie\": \"Angine de poitrine\", \"probabilite\": 0.09}, {\"maladie\": \"Asthme\", \"probabilite\": 0.036}]', 0.106, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Douleur thoracique\", \"severite\": \"Modérée\", \"duree_jours\": 74}, {\"nom\": \"Fatigue\", \"severite\": \"Légère\", \"duree_jours\": 73}, {\"nom\": \"Anxiété\", \"severite\": \"Légère\", \"duree_jours\": 72}], \"signes_vitaux\": {\"poids\": 60, \"taille\": 158.6, \"temperature\": 36.73, \"saturation_o2\": 97.14, \"tension_systolique\": 130.37, \"frequence_cardiaque\": 72.72, \"tension_diastolique\": 86.88, \"frequence_respiratoire\": 9.15}}', NULL, '2026-05-11 14:48:42'),
(15, 57, 'RandomForest_v1.0_Finale', 0.106, '[{\"maladie\": \"Athérosclérose\", \"probabilite\": 0.106}, {\"maladie\": \"Angine de poitrine\", \"probabilite\": 0.08}, {\"maladie\": \"Asthme\", \"probabilite\": 0.036}]', 0.106, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-11\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-11\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}], \"symptomes\": [{\"nom\": \"Douleur thoracique\", \"severite\": \"Modérée\", \"duree_jours\": 74}, {\"nom\": \"Fatigue\", \"severite\": \"Légère\", \"duree_jours\": 73}, {\"nom\": \"Anxiété\", \"severite\": \"Légère\", \"duree_jours\": 72}], \"signes_vitaux\": {\"poids\": 60, \"taille\": 158.6, \"temperature\": 36.73, \"saturation_o2\": 97.14, \"tension_systolique\": 130.37, \"frequence_cardiaque\": 72.72, \"tension_diastolique\": 86.88, \"frequence_respiratoire\": 9.15}}', NULL, '2026-05-11 14:48:42');

-- --------------------------------------------------------

--
-- Structure de la table `consultations`
--

DROP TABLE IF EXISTS `consultations`;
CREATE TABLE IF NOT EXISTS `consultations` (
  `consultation_id` int NOT NULL AUTO_INCREMENT,
  `nom_patient` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `patient_id` int DEFAULT NULL,
  `date_heure` datetime NOT NULL,
  `motif` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `medecin_id` int DEFAULT NULL,
  `statut` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'en attente',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`consultation_id`),
  KEY `medecin_id` (`medecin_id`),
  KEY `idx_patient_id` (`patient_id`)
) ENGINE=MyISAM AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `consultations`
--

INSERT INTO `consultations` (`consultation_id`, `nom_patient`, `patient_id`, `date_heure`, `motif`, `medecin_id`, `statut`, `created_at`) VALUES
(57, 'Angine Patients', 35, '2026-05-11 15:44:10', 'Angine de poitrine', 15, 'terminée', '2026-05-11 14:44:09'),
(53, 'Test Pateint', 32, '2026-05-09 15:48:57', 'Ne se sent pas bien', 15, 'terminée', '2026-05-09 14:48:56'),
(65, 'ioooooo ffttfttt', 40, '2026-05-12 15:32:12', 'xwe', 17, 'en attente', '2026-05-12 14:32:12'),
(64, 'uiiioi hvygt uh__', 39, '2026-05-11 17:59:16', 'fr', 14, 'en cours', '2026-05-11 16:59:15'),
(63, 'uiiioi hvygt uh__', 39, '2026-05-11 17:58:44', 'fr', 1, 'en attente', '2026-05-11 16:58:43');

-- --------------------------------------------------------

--
-- Structure de la table `consultation_infirmiers`
--

DROP TABLE IF EXISTS `consultation_infirmiers`;
CREATE TABLE IF NOT EXISTS `consultation_infirmiers` (
  `consultation_id` int NOT NULL,
  `infirmier_id` int NOT NULL,
  PRIMARY KEY (`consultation_id`,`infirmier_id`),
  KEY `infirmier_id` (`infirmier_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `diagnostics`
--

DROP TABLE IF EXISTS `diagnostics`;
CREATE TABLE IF NOT EXISTS `diagnostics` (
  `diagnostic_id` int NOT NULL AUTO_INCREMENT,
  `consultation_id` int NOT NULL,
  `analyse_ia_id` int DEFAULT NULL,
  `medecin_id` int DEFAULT NULL,
  `dossier_id` int NOT NULL,
  `code_icd10` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nom_maladie` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `certitude` float DEFAULT NULL,
  `statut` enum('PROVISOIRE','CONFIRMÉ','REJETÉ','ARCHIVÉ') COLLATE utf8mb4_unicode_ci DEFAULT 'PROVISOIRE',
  `severite` enum('LEGER','MODERE','GRAVE','CRITIQUE') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `justification` text COLLATE utf8mb4_unicode_ci,
  `date_validation` date DEFAULT NULL,
  PRIMARY KEY (`diagnostic_id`),
  KEY `consultation_id` (`consultation_id`),
  KEY `analyse_ia_id` (`analyse_ia_id`),
  KEY `medecin_id` (`medecin_id`),
  KEY `dossier_id` (`dossier_id`)
) ENGINE=MyISAM AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `diagnostics`
--

INSERT INTO `diagnostics` (`diagnostic_id`, `consultation_id`, `analyse_ia_id`, `medecin_id`, `dossier_id`, `code_icd10`, `nom_maladie`, `description`, `certitude`, `statut`, `severite`, `justification`, `date_validation`) VALUES
(14, 53, 11, NULL, 16, NULL, 'Lymphome', 'Validation : CONFIRMÉ. Suggestion IA : Lymphome (12.9%). Notes : ', 0.128571, 'CONFIRMÉ', NULL, NULL, '2026-05-09'),
(15, 55, 13, NULL, 16, NULL, 'Tuberculose ', 'Validation : REJETÉ. Suggestion IA : Hyperthyroïdie (14.3%). Notes : ', 0.142857, 'REJETÉ', NULL, NULL, '2026-05-09'),
(16, 57, 15, NULL, 17, NULL, 'Angine de poitrine', 'Validation : REJETÉ. Suggestion IA : Athérosclérose (10.6%). Notes : ', 0.106, 'REJETÉ', NULL, NULL, '2026-05-11');

-- --------------------------------------------------------

--
-- Structure de la table `doctor_feedback`
--

DROP TABLE IF EXISTS `doctor_feedback`;
CREATE TABLE IF NOT EXISTS `doctor_feedback` (
  `id` int NOT NULL AUTO_INCREMENT,
  `consultation_id` int NOT NULL,
  `medecin_id` int NOT NULL,
  `prediction_id` int DEFAULT NULL,
  `quality_rating` int NOT NULL,
  `accuracy_rating` int DEFAULT NULL,
  `explainability_rating` int DEFAULT NULL,
  `usefulness_rating` int DEFAULT NULL,
  `comments` text COLLATE utf8mb4_unicode_ci,
  `suggestions` text COLLATE utf8mb4_unicode_ci,
  `suggested_diagnosis` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `feedback_category` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_doctor_feedback_id` (`id`),
  KEY `ix_doctor_feedback_created_at` (`created_at`),
  KEY `ix_doctor_feedback_consultation_id` (`consultation_id`),
  KEY `ix_doctor_feedback_medecin_id` (`medecin_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `dossiers_medicaux`
--

DROP TABLE IF EXISTS `dossiers_medicaux`;
CREATE TABLE IF NOT EXISTS `dossiers_medicaux` (
  `dossier_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `numero_dossier` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `antecedents_familiaux` text COLLATE utf8mb4_unicode_ci,
  `antecedents_personnels` text COLLATE utf8mb4_unicode_ci,
  `allergies` text COLLATE utf8mb4_unicode_ci,
  `date_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`dossier_id`),
  UNIQUE KEY `patient_id` (`patient_id`),
  UNIQUE KEY `numero_dossier` (`numero_dossier`),
  KEY `idx_patient` (`patient_id`)
) ENGINE=MyISAM AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `dossiers_medicaux`
--

INSERT INTO `dossiers_medicaux` (`dossier_id`, `patient_id`, `numero_dossier`, `antecedents_familiaux`, `antecedents_personnels`, `allergies`, `date_creation`) VALUES
(1, 1, 'DM-2026-001', 'Père: Hypertension, Mère: Diabète type 2', 'Appendicectomie en 2010', 'Pénicilline', '2026-05-06 06:10:04'),
(2, 2, 'DM-2026-002', 'Mère: Asthme', 'Aucun', 'Aucune allergie connue', '2026-05-06 06:10:04'),
(3, 3, 'DM-2026-003', 'Père: AVC à 65 ans', 'Hypertension diagnostiquée en 2020', 'Aspirine', '2026-05-06 06:10:04'),
(4, 5, 'DM-2026-005', 'Aucun antécédent notable', 'Fracture du bras gauche en 2015', 'Aucune allergie connue', '2026-05-06 06:10:04'),
(5, 7, 'DM-2026-007', 'Père: Cancer du côlon', 'Ulcère gastrique traité en 2018', 'Iode', '2026-05-06 06:10:04'),
(6, 10, 'DM-2026-010', 'Mère: Polyarthrite rhumatoïde', 'Aucun', 'Aucune allergie connue', '2026-05-06 06:10:04'),
(7, 15, 'DM-2026-015', 'Père et Mère: Diabète type 2', 'Diabète type 2 diagnostiqué en 2022', 'Aucune allergie connue', '2026-05-06 06:10:04'),
(8, 19, 'DM-2026-019', 'Père: Hypertension, Frère: Infarctus à 45 ans', 'Hypertension depuis 2019', 'Sulfamides', '2026-05-06 06:10:04'),
(9, 21, 'DM-20260506155658-21', NULL, NULL, NULL, '2026-05-06 14:56:58'),
(11, 26, 'DM-20260507131755-26', NULL, NULL, NULL, '2026-05-07 12:17:55'),
(12, 27, 'DM-20260507181358-27', NULL, NULL, NULL, '2026-05-07 17:13:58'),
(13, 28, 'DM-20260508031822-28', NULL, NULL, NULL, '2026-05-08 02:18:22'),
(14, 29, 'DM-20260508173750-29', NULL, NULL, NULL, '2026-05-08 16:37:50'),
(15, 30, 'DOS-30-AUTO', NULL, 'Aucun', NULL, '2026-05-09 01:35:10'),
(16, 32, 'DM-20260509163244-32', NULL, NULL, NULL, '2026-05-09 15:32:44'),
(17, 35, 'DM-20260511154842-35', NULL, NULL, NULL, '2026-05-11 14:48:42');

-- --------------------------------------------------------

--
-- Structure de la table `examens`
--

DROP TABLE IF EXISTS `examens`;
CREATE TABLE IF NOT EXISTS `examens` (
  `examen_id` int NOT NULL AUTO_INCREMENT,
  `consultation_id` int NOT NULL,
  `type` enum('CLINIQUE','IMAGERIE','BIOLOGIE','ELECTROCARDIOGRAMME') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nom` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `resultats` text COLLATE utf8mb4_unicode_ci,
  `valeur_numerique` float DEFAULT NULL,
  `unite_mesure` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `statut` enum('DEMANDE','EN_COURS','REALISE','ANALYSE') COLLATE utf8mb4_unicode_ci DEFAULT 'DEMANDE',
  `date_examen` date DEFAULT NULL,
  `is_suggested` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`examen_id`),
  KEY `consultation_id` (`consultation_id`)
) ENGINE=MyISAM AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `examens`
--

INSERT INTO `examens` (`examen_id`, `consultation_id`, `type`, `nom`, `description`, `resultats`, `valeur_numerique`, `unite_mesure`, `statut`, `date_examen`, `is_suggested`) VALUES
(1, 31, 'BIOLOGIE', 'NFS (Numération Formule Sanguine)', 'Bilan sanguin de base', NULL, NULL, NULL, 'REALISE', NULL, 0),
(2, 31, 'BIOLOGIE', 'CRP (Protéine C-réactive)', 'Marqueur inflammatoire', NULL, NULL, NULL, 'REALISE', NULL, 0),
(3, 31, 'BIOLOGIE', 'Frottis sanguin + GE', 'Recherche Plasmodium', NULL, NULL, NULL, 'REALISE', NULL, 0),
(4, 31, 'BIOLOGIE', 'TDR Paludisme', 'Test rapide antigènes Plasmodium', NULL, NULL, NULL, 'REALISE', NULL, 0),
(5, 31, 'BIOLOGIE', 'Hémoculture', 'Culture bactérienne du sang', NULL, NULL, NULL, 'REALISE', NULL, 0),
(6, 31, 'BIOLOGIE', 'Widal', 'Sérologie anti-Salmonella', NULL, NULL, NULL, 'REALISE', NULL, 0),
(7, 33, 'BIOLOGIE', 'NFS (Numeration Formule Sanguine)', NULL, 'Leucocytose moderee - 11000/mm3', 11, 'g/dL', 'REALISE', '2026-05-05', 0),
(8, 33, 'BIOLOGIE', 'Widal', NULL, 'Positif au 1/160 - Salmonella typhi confirmee', 160, 'titre', 'REALISE', '2026-05-05', 0),
(9, 33, 'BIOLOGIE', 'Hemoculture', NULL, 'Salmonella typhi isolee - sensible ampicilline', NULL, 'resultat', 'REALISE', '2026-05-05', 0),
(10, 33, 'BIOLOGIE', 'CRP (Proteine C-reactive)', NULL, 'Eleve - syndrome inflammatoire', 48, 'mg/L', 'REALISE', '2026-05-05', 0),
(11, 38, 'BIOLOGIE', 'NFS (Numération Formule Sanguine)', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-07', 0),
(12, 38, 'BIOLOGIE', 'CRP (Protéine C-réactive)', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-07', 0),
(13, 39, 'IMAGERIE', 'OIIII', NULL, NULL, NULL, NULL, 'REALISE', NULL, 0),
(14, 41, 'BIOLOGIE', 'NFS (Numération Formule Sanguine)', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-08', 0),
(15, 41, 'BIOLOGIE', 'CRP (Protéine C-réactive)', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-08', 0),
(16, 41, 'BIOLOGIE', 'Frottis sanguin + GE', 'Recherche Plasmodium', NULL, NULL, 'résultat', 'REALISE', '2026-05-08', 0),
(17, 41, 'BIOLOGIE', 'TDR Paludisme', 'Test rapide antigènes Plasmodium', NULL, NULL, 'résultat', 'REALISE', '2026-05-08', 0),
(18, 42, 'BIOLOGIE', 'NFS (Numération Formule Sanguine)', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-08', 0),
(19, 42, 'BIOLOGIE', 'CRP (Protéine C-réactive)', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-08', 0),
(20, 53, 'BIOLOGIE', 'NFS (Numération Formule Sanguine)', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-09', 0),
(21, 53, 'BIOLOGIE', 'CRP (Protéine C-réactive)', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-09', 0),
(22, 55, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-09', 0),
(23, 55, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-09', 0),
(24, 57, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-11', 1),
(25, 57, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-11', 1);

-- --------------------------------------------------------

--
-- Structure de la table `infirmiers`
--

DROP TABLE IF EXISTS `infirmiers`;
CREATE TABLE IF NOT EXISTS `infirmiers` (
  `infirmier_id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenoms` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `telephone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `disponible` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`infirmier_id`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `infirmiers`
--

INSERT INTO `infirmiers` (`infirmier_id`, `nom`, `prenoms`, `telephone`, `email`, `disponible`, `created_at`) VALUES
(1, 'AGOSSOU', 'Martine', '+229 97 11 22 33', 'martine.agossou@santeplus.bj', 1, '2026-05-06 06:10:04'),
(2, 'DOSSOU', 'Léon', '+229 96 22 33 44', 'leon.dossou@santeplus.bj', 1, '2026-05-06 06:10:04'),
(3, 'KPOHINTO', 'Sylviane', '+229 95 33 44 55', 'sylviane.kpohinto@santeplus.bj', 1, '2026-05-06 06:10:04'),
(4, 'HOUNGBEDJI', 'Arnaud', '+229 94 44 55 66', 'arnaud.houngbedji@santeplus.bj', 1, '2026-05-06 06:10:04'),
(5, 'ZANNOU', 'Odette', '+229 97 55 66 77', 'odette.zannou@santeplus.bj', 1, '2026-05-06 06:10:04'),
(6, 'AKPLOGAN', 'Didier', '+229 96 66 77 88', 'didier.akplogan@santeplus.bj', 1, '2026-05-06 06:10:04'),
(7, 'TOSSOU', 'Bernadette', '+229 95 77 88 99', 'bernadette.tossou@santeplus.bj', 1, '2026-05-06 06:10:04'),
(8, 'GBAGUIDI', 'Norbert', '+229 94 88 99 00', 'norbert.gbaguidi@santeplus.bj', 1, '2026-05-06 06:10:04'),
(9, 'HOUNKANRIN', 'Pauline', '+229 97 99 00 11', 'pauline.hounkanrin@santeplus.bj', 1, '2026-05-06 06:10:04'),
(10, 'ASSOGBA', 'Clément', '+229 96 00 11 22', 'clement.assogba@santeplus.bj', 1, '2026-05-06 06:10:04');

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
  `role` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`medecin_id`)
) ENGINE=MyISAM AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `medecins`
--

INSERT INTO `medecins` (`medecin_id`, `nom`, `prenoms`, `specialite`, `telephone`, `disponible`, `created_at`, `role`) VALUES
(1, 'KOUDJO', 'Alain', 'Cardiologie', '+229 97 10 20 30', 1, '2026-05-06 06:10:04', NULL),
(2, 'SOGLO', 'Brigitte', 'Gynécologie', '+229 96 20 30 40', 1, '2026-05-06 06:10:04', NULL),
(3, 'ADJOVI', 'Charles', 'Chirurgie Générale', '+229 95 30 40 50', 1, '2026-05-06 06:10:04', NULL),
(4, 'DANSOU', 'Diane', 'Dermatologie', '+229 94 40 50 60', 1, '2026-05-06 06:10:04', NULL),
(5, 'HOUENOU', 'Émile', 'Ophtalmologie', '+229 97 50 60 70', 1, '2026-05-06 06:10:04', NULL),
(6, 'AZONHIHO', 'Françoise', 'ORL', '+229 96 60 70 80', 1, '2026-05-06 06:10:04', NULL),
(7, 'DEGUENON', 'Georges', 'Neurologie', '+229 95 70 80 90', 1, '2026-05-06 06:10:04', NULL),
(8, 'KPADE', 'Hélène', 'Rhumatologie', '+229 94 80 90 00', 1, '2026-05-06 06:10:04', NULL),
(9, 'SOSSOU', 'Ignace', 'Pneumologie', '+229 97 90 00 10', 1, '2026-05-06 06:10:04', NULL),
(10, 'AGBODJAN', 'Juliette', 'Endocrinologie', '+229 96 00 10 20', 1, '2026-05-06 06:10:04', NULL),
(16, 'LEFEBVRE', 'Jean-Baptiste', 'Médecin Général', '00000000', 1, '2026-05-09 14:07:51', NULL),
(15, 'DOSSOU', 'Marie-Claire Afi', 'Médecin Général', '00000000', 1, '2026-05-09 14:07:51', NULL),
(14, 'PETIT', 'Thomas André', 'Medecin General', '+229 96 00 10 99', 1, '2026-05-07 06:36:27', NULL),
(17, 'BERNARD', 'Sophie Marie', 'Médecin Général', '00000000', 1, '2026-05-09 14:07:51', NULL);

-- --------------------------------------------------------

--
-- Structure de la table `medicaments`
--

DROP TABLE IF EXISTS `medicaments`;
CREATE TABLE IF NOT EXISTS `medicaments` (
  `medicament_id` int NOT NULL AUTO_INCREMENT,
  `ordonnance_id` int NOT NULL,
  `nom_commercial` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `denomination_commune` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dosage` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `forme` enum('COMPRIME','INJECTION','SIROP','CREME') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `quantite` int DEFAULT NULL,
  `frequence` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `voie_administration` enum('ORALE','INTRAVEINEUSE','CUTANEE','INTRAMUSCULAIRE') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `duree_jours` int DEFAULT NULL,
  PRIMARY KEY (`medicament_id`),
  KEY `ordonnance_id` (`ordonnance_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `model_training_logs`
--

DROP TABLE IF EXISTS `model_training_logs`;
CREATE TABLE IF NOT EXISTS `model_training_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `version` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `accuracy` float NOT NULL,
  `precision` float DEFAULT NULL,
  `recall` float DEFAULT NULL,
  `f1_score` float DEFAULT NULL,
  `confusion_matrix` json DEFAULT NULL,
  `training_samples` int DEFAULT NULL,
  `test_samples` int DEFAULT NULL,
  `n_features` int DEFAULT NULL,
  `n_classes` int DEFAULT NULL,
  `hyperparameters` json DEFAULT NULL,
  `feature_importance` json DEFAULT NULL,
  `training_duration_seconds` float DEFAULT NULL,
  `is_deployed` int DEFAULT NULL,
  `deployed_at` datetime DEFAULT NULL,
  `model_filepath` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_model_training_logs_id` (`id`),
  KEY `ix_model_training_logs_created_at` (`created_at`),
  KEY `ix_model_training_logs_version` (`version`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `ordonnances`
--

DROP TABLE IF EXISTS `ordonnances`;
CREATE TABLE IF NOT EXISTS `ordonnances` (
  `ordonnance_id` int NOT NULL AUTO_INCREMENT,
  `traitement_id` int NOT NULL,
  `medecin_id` int NOT NULL,
  `patient_id` int NOT NULL,
  `dossier_id` int NOT NULL,
  `posologie_generale` text COLLATE utf8mb4_unicode_ci,
  `date_emission` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `renouvelable` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`ordonnance_id`),
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
  `patient_id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenoms` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_naissance` date NOT NULL,
  `sexe` enum('M','F') COLLATE utf8mb4_unicode_ci NOT NULL,
  `groupe_sanguin` enum('A+','A-','B+','B-','AB+','AB-','O+','O-') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telephone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `adresse` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`patient_id`)
) ENGINE=MyISAM AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `patients`
--

INSERT INTO `patients` (`patient_id`, `nom`, `prenoms`, `date_naissance`, `sexe`, `groupe_sanguin`, `telephone`, `email`, `adresse`, `created_at`) VALUES
(1, 'AHOUANSOU', 'Jean-Baptiste', '1985-03-15', 'M', 'O+', '+229 97 12 34 56', 'jb.ahouansou@gmail.com', 'Cotonou, Quartier Akpakpa', '2026-05-06 06:10:04'),
(2, 'DOSSOU', 'Marie-Claire', '1990-07-22', 'F', 'A+', '+229 96 23 45 67', 'mc.dossou@yahoo.fr', 'Porto-Novo, Quartier Ouando', '2026-05-06 06:10:04'),
(3, 'KPOSSOU', 'Rodrigue', '1978-11-08', 'M', 'B+', '+229 95 34 56 78', NULL, 'Parakou, Centre-ville', '2026-05-06 06:10:04'),
(4, 'AGBODJAN', 'Sylvie', '1995-02-14', 'F', 'AB+', '+229 94 45 67 89', 'sylvie.agbodjan@hotmail.com', 'Abomey-Calavi, Godomey', '2026-05-06 06:10:04'),
(5, 'HOUNGBO', 'Mathieu', '1982-09-30', 'M', 'O-', '+229 97 56 78 90', 'mathieu.h@gmail.com', 'Cotonou, Quartier Cadjèhoun', '2026-05-06 06:10:04'),
(6, 'ZANNOU', 'Françoise', '1988-05-18', 'F', 'A-', '+229 96 67 89 01', NULL, 'Ouidah, Quartier Zoungbodji', '2026-05-06 06:10:04'),
(7, 'AKPLOGAN', 'Serge', '1975-12-25', 'M', 'B-', '+229 95 78 90 12', 'serge.akplogan@yahoo.fr', 'Bohicon, Quartier Gare', '2026-05-06 06:10:04'),
(8, 'TOSSOU', 'Angélique', '1992-08-07', 'F', 'O+', '+229 94 89 01 23', 'angelique.tossou@gmail.com', 'Cotonou, Quartier Fidjrossè', '2026-05-06 06:10:04'),
(9, 'GBAGUIDI', 'Pascal', '1980-04-12', 'M', 'A+', '+229 97 90 12 34', NULL, 'Lokossa, Centre-ville', '2026-05-06 06:10:04'),
(10, 'HOUNKANRIN', 'Nadège', '1993-10-28', 'F', 'AB-', '+229 96 01 23 45', 'nadege.h@hotmail.com', 'Cotonou, Quartier Vêdoko', '2026-05-06 06:10:04'),
(11, 'ASSOGBA', 'Désiré', '1987-06-19', 'M', 'O+', '+229 95 12 34 56', 'desire.assogba@gmail.com', 'Parakou, Quartier Banikanni', '2026-05-06 06:10:04'),
(12, 'KOUDJO', 'Estelle', '1991-01-03', 'F', 'B+', '+229 94 23 45 67', NULL, 'Abomey, Quartier Houndjro', '2026-05-06 06:10:04'),
(13, 'SOGLO', 'Armand', '1979-09-16', 'M', 'A-', '+229 97 34 56 78', 'armand.soglo@yahoo.fr', 'Cotonou, Quartier Zogbo', '2026-05-06 06:10:04'),
(14, 'ADJOVI', 'Rachelle', '1994-03-21', 'F', 'O-', '+229 96 45 67 89', 'rachelle.adjovi@gmail.com', 'Porto-Novo, Quartier Djegan', '2026-05-06 06:10:04'),
(15, 'DANSOU', 'Gérard', '1983-11-11', 'M', 'AB+', '+229 95 56 67 90', NULL, 'Natitingou, Centre-ville', '2026-05-06 06:10:04'),
(16, 'HOUENOU', 'Clarisse', '1989-07-05', 'F', 'O+', '+229 94 67 78 01', 'clarisse.houenou@hotmail.com', 'Cotonou, Quartier Gbégamey', '2026-05-06 06:10:04'),
(17, 'AZONHIHO', 'Fabrice', '1986-02-28', 'M', 'A+', '+229 97 78 89 12', 'fabrice.azonhiho@gmail.com', 'Savalou, Quartier Agbokpa', '2026-05-06 06:10:04'),
(18, 'DEGUENON', 'Joséphine', '1996-12-09', 'F', 'B-', '+229 96 89 90 23', 'josephine@gmail.com', 'Cotonou, Quartier Akpakpa', '2026-05-06 06:10:04'),
(19, 'KPADE', 'Honoré', '1981-05-14', 'M', 'O+', '+229 95 90 01 34', 'honore.kpade@yahoo.fr', 'Djougou, Centre-ville', '2026-05-06 06:10:04'),
(20, 'SOSSOU', 'Véronique', '1990-08-26', 'F', 'A+', '+229 94 01 12 45', 'veronique.sossou@gmail.com', 'Cotonou, Quartier Cocotomey', '2026-05-06 06:10:04'),
(21, 'AGOSSOU', 'Koffi Mensah ', '1996-03-15', 'M', NULL, '97 00 11 22', 'agossou@gmail.com', NULL, '2026-05-06 14:56:58'),
(23, 'Test', 'Users', '2026-05-06', 'M', 'AB+', '0112121212', 'testuser@gmail.com', NULL, '2026-05-06 21:49:27'),
(24, 'UserTes', 'UTest', '2026-05-07', 'F', 'O+', '0122443322', 'Utest@gmail.com', NULL, '2026-05-07 06:44:55'),
(25, 'enregistrer', 'Enrg', '2026-04-27', 'M', NULL, NULL, NULL, NULL, '2026-05-07 07:16:30'),
(26, 'vfrr', 'rrfr', '2026-05-31', 'M', 'AB-', '0122334455', 'efefefe@gmail.com', NULL, '2026-05-07 12:11:27'),
(27, 'ETERER', 'TETETE', '2026-05-08', 'M', 'AB-', '4242424235', 'zrererer@gmail.com', NULL, '2026-05-07 17:08:48'),
(28, 'AGOSSOU ', 'Koffi', '1990-03-15', 'M', 'O+', ' 97 12 34 56', 'koffi@gmail.com', NULL, '2026-05-08 02:08:59'),
(29, 'DDRR', 'GGGG', '2026-05-08', 'M', 'AB+', '018879973', NULL, NULL, '2026-05-08 16:28:22'),
(30, 'TEST_IA', 'Robot', '1990-01-01', 'M', 'O+', NULL, NULL, NULL, '2026-05-09 01:33:09'),
(31, 'HOUNSOU ', 'Armelle Bénédicte', '1985-07-20', 'F', 'O-', '0196 44 55 66', 'armelle@gmail.com', NULL, '2026-05-09 02:03:42'),
(32, 'TEST', 'Test', '2026-05-15', 'M', 'AB+', '22334455', 'test@gmail.com', NULL, '2026-05-09 02:41:53'),
(33, 'DEGLA', 'Lhys', '2022-02-10', 'F', 'O+', '0196746919', 'lhys@gmail.com', NULL, '2026-05-09 15:59:05'),
(34, 'dede', 'ddddddddd', '2008-01-23', 'M', 'AB-', '11223344', 'edededde@gmail.com', NULL, '2026-05-10 22:21:38'),
(35, 'Patient', 'Angine', '2007-02-11', 'M', 'B+', '1299887733', 'angine@gamail.com', NULL, '2026-05-11 14:44:09'),
(39, 'hvygt uh__', 'uiiioi', '2026-04-29', 'M', 'B-', '11Z2222323232323', 'lllll@gmail.com', NULL, '2026-05-11 16:58:43'),
(40, 'ffttfttt', 'ioooooo', '2026-05-02', 'M', 'AB+', '44667', NULL, NULL, '2026-05-12 14:32:12');

-- --------------------------------------------------------

--
-- Structure de la table `prediction_history`
--

DROP TABLE IF EXISTS `prediction_history`;
CREATE TABLE IF NOT EXISTS `prediction_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `consultation_id` int DEFAULT NULL,
  `predicted_disease` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `confidence` float NOT NULL,
  `confidence_level` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `prediction_probabilities` json DEFAULT NULL,
  `feature_values` json DEFAULT NULL,
  `top_features` json DEFAULT NULL,
  `model_version` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `model_accuracy` float DEFAULT NULL,
  `is_validated` int DEFAULT NULL,
  `validated_by` int DEFAULT NULL,
  `validated_at` datetime DEFAULT NULL,
  `validation_notes` text COLLATE utf8mb4_unicode_ci,
  `actual_disease` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `validated_by` (`validated_by`),
  KEY `ix_prediction_history_created_at` (`created_at`),
  KEY `ix_prediction_history_consultation_id` (`consultation_id`),
  KEY `ix_prediction_history_patient_id` (`patient_id`),
  KEY `ix_prediction_history_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `prescriptions`
--

DROP TABLE IF EXISTS `prescriptions`;
CREATE TABLE IF NOT EXISTS `prescriptions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `consultation_id` int DEFAULT NULL,
  `medecin_id` int NOT NULL,
  `diagnostic` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `medications` json NOT NULL,
  `contraindications` json DEFAULT NULL,
  `patient_allergies` json DEFAULT NULL,
  `drug_interactions` json DEFAULT NULL,
  `warnings` json DEFAULT NULL,
  `has_critical_warning` tinyint(1) DEFAULT NULL,
  `special_instructions` text COLLATE utf8mb4_unicode_ci,
  `is_signed` tinyint(1) DEFAULT NULL,
  `signed_by` int DEFAULT NULL,
  `signed_at` datetime DEFAULT NULL,
  `signature_hash` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `medical_notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  `delivered_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `signed_by` (`signed_by`),
  KEY `ix_prescriptions_id` (`id`),
  KEY `ix_prescriptions_medecin_id` (`medecin_id`),
  KEY `ix_prescriptions_consultation_id` (`consultation_id`),
  KEY `ix_prescriptions_created_at` (`created_at`),
  KEY `ix_prescriptions_patient_id` (`patient_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `signes_vitaux`
--

DROP TABLE IF EXISTS `signes_vitaux`;
CREATE TABLE IF NOT EXISTS `signes_vitaux` (
  `signes_vitaux_id` int NOT NULL AUTO_INCREMENT,
  `consultation_id` int NOT NULL,
  `infirmier_id` int DEFAULT NULL,
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
  PRIMARY KEY (`signes_vitaux_id`),
  KEY `consultation_id` (`consultation_id`),
  KEY `infirmier_id` (`infirmier_id`)
) ENGINE=MyISAM AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `signes_vitaux`
--

INSERT INTO `signes_vitaux` (`signes_vitaux_id`, `consultation_id`, `infirmier_id`, `date_enregistrement`, `tension_systolique`, `tension_diastolique`, `frequence_cardiaque`, `temperature`, `frequence_respiratoire`, `saturation_oxygene`, `poids`, `taille`, `imc`, `glycemie`) VALUES
(38, 53, NULL, '2026-05-09 15:32:44', 108, 88, 90, 36.66, 17, 98, 60, 180, 18.5, NULL),
(39, 54, NULL, '2026-05-09 16:12:46', 109, 98, 51, 37.44, 11, 96.93, 70, 168, 24.8, NULL),
(40, 55, NULL, '2026-05-09 18:05:37', 109, 98, 51, 37.4, 11, 96.9, 60, 155.7, 24.7, NULL),
(41, 57, NULL, '2026-05-11 14:48:42', 130, 87, 73, 36.73, 9, 97.14, 60, 158.6, 23.9, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `suivis`
--

DROP TABLE IF EXISTS `suivis`;
CREATE TABLE IF NOT EXISTS `suivis` (
  `suivi_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `medecin_id` int NOT NULL,
  `consultation_id` int DEFAULT NULL,
  `diagnostic_id` int DEFAULT NULL,
  `traitement_id` int DEFAULT NULL,
  `dossier_id` int NOT NULL,
  `numero_suivi` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_suivi` date NOT NULL,
  `etat_general` enum('EXCELLENT','BON','STABLE','DECLINE','CRITIQUE') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `amelioration` enum('EXCELLENTE','BON','MOYEN','MAUVAIS','DECLINE') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pourcentage_amelioration` float DEFAULT NULL,
  `adherence_traitement` float DEFAULT NULL,
  `statut` enum('EN_COURS','TERMINE_SUCCES','TERMINE_ECHEC','A_REPRENDRE') COLLATE utf8mb4_unicode_ci DEFAULT 'EN_COURS',
  `prochaine_consultation` date DEFAULT NULL,
  PRIMARY KEY (`suivi_id`),
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
  `symptome_id` int NOT NULL AUTO_INCREMENT,
  `consultation_id` int NOT NULL,
  `nom` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `severite` enum('LEGER','MODERE','SEVERE') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_apparition` date DEFAULT NULL,
  `duree_jours` int DEFAULT NULL,
  `zone_atteinte` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `frequence` enum('CONSTANT','INTERMITTENT','PROGRESSIF') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`symptome_id`),
  KEY `consultation_id` (`consultation_id`)
) ENGINE=MyISAM AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `symptomes`
--

INSERT INTO `symptomes` (`symptome_id`, `consultation_id`, `nom`, `description`, `severite`, `date_apparition`, `duree_jours`, `zone_atteinte`, `frequence`) VALUES
(77, 53, 'Adénopathie', NULL, 'SEVERE', NULL, 5, NULL, NULL),
(78, 53, 'Sueurs nocturnes', NULL, 'MODERE', NULL, 4, NULL, NULL),
(79, 53, 'Fièvre', NULL, 'MODERE', NULL, 3, NULL, NULL),
(80, 54, 'Perte de poids', '\n', 'MODERE', NULL, 60, NULL, NULL),
(81, 54, 'Hémoptysie', NULL, 'LEGER', NULL, 59, NULL, NULL),
(82, 54, 'Toux persistante', NULL, 'LEGER', NULL, 58, NULL, NULL),
(83, 54, 'Fatigue', NULL, 'LEGER', NULL, 60, NULL, NULL),
(84, 55, 'Perte de poids', NULL, 'MODERE', NULL, 60, NULL, NULL),
(85, 55, 'Hémoptysie', NULL, 'LEGER', NULL, 59, NULL, NULL),
(86, 55, 'Toux persistante', NULL, 'LEGER', NULL, 58, NULL, NULL),
(87, 55, 'Fatigue', NULL, 'LEGER', NULL, 60, NULL, NULL),
(88, 57, 'Douleur thoracique', NULL, 'MODERE', NULL, 74, NULL, NULL),
(89, 57, 'Fatigue', NULL, 'LEGER', NULL, 73, NULL, NULL),
(90, 57, 'Anxiété', NULL, 'LEGER', NULL, 72, NULL, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `traitements`
--

DROP TABLE IF EXISTS `traitements`;
CREATE TABLE IF NOT EXISTS `traitements` (
  `traitement_id` int NOT NULL AUTO_INCREMENT,
  `diagnostic_id` int NOT NULL,
  `nom_traitement` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `type` enum('MEDICAMENTEUX','CHIRURGICAL','PHYSIQUE','PSYCHOLOGIQUE') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `duree_jours` int DEFAULT NULL,
  `date_debut` date DEFAULT NULL,
  `date_fin` date DEFAULT NULL,
  `statut` enum('PRESCRIT','EN_COURS','TERMINE','ABANDONNE','ECHEC') COLLATE utf8mb4_unicode_ci DEFAULT 'PRESCRIT',
  `objective_therapeutique` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`traitement_id`),
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
  `role` enum('admin','medecin','infirmier') COLLATE utf8mb4_unicode_ci DEFAULT 'medecin',
  `actif` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login` datetime DEFAULT NULL,
  PRIMARY KEY (`utilisateur_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `utilisateurs`
--

INSERT INTO `utilisateurs` (`utilisateur_id`, `nom`, `prenoms`, `email`, `mot_de_passe`, `role`, `actif`, `created_at`, `last_login`) VALUES
(1, 'ADMIN', 'Super', 'admin@santeplus.bj', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'admin', 1, '2026-05-02 20:29:04', '2026-05-13 14:43:55'),
(7, 'AGBODJAN', 'Edem Patricia', 'edem.agbodjan@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:12:16', '2026-05-12 12:25:10'),
(6, 'MENSAH', 'Kokou David', 'kokou.mensah@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:12:16', NULL),
(5, 'KOFFI', 'Awa Sylvie', 'awa.koffi@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:12:16', NULL),
(8, 'TOSSOU', 'Yao Emmanuel', 'yao.tossou@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:12:16', NULL),
(9, 'AHOUANSOU', 'Gérard Koffi', 'gerard.ahouansou@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', '2026-05-09 16:52:22'),
(10, 'DOSSOU', 'Marie-Claire Afi', 'marie.dossou@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'medecin', 1, '2026-05-02 23:33:49', '2026-05-11 13:48:38'),
(11, 'LEFEBVRE', 'Jean-Baptiste', 'jean.lefebvre@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'medecin', 1, '2026-05-02 23:33:49', '2026-05-09 03:49:56'),
(12, 'BERNARD', 'Sophie Marie', 'sophie.bernard@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'medecin', 1, '2026-05-02 23:33:49', NULL),
(13, 'PETIT', 'Thomas André', 'thomas.petit@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'medecin', 1, '2026-05-02 23:33:49', NULL),
(14, 'KOUASSI', 'Aya', 'aya.kouassi@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', '2026-05-07 18:07:01'),
(15, 'MENSAH', 'Kofi', 'kofi.mensah@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', NULL),
(16, 'DIALLO', 'Fatoumata', 'fatoumata.diallo@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', NULL),
(17, 'TRAORE', 'Moussa', 'moussa.traore@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', NULL),
(18, 'M\'POLO', 'Yanick', 'yanickmpolo@gasasad.bj', '$2b$12$pEC30rX9D4QRXY9mkH6iTudj6HOqA6PHs0e9HJwC6PZSlJtMTX6O6', 'medecin', 1, '2026-05-09 19:21:06', '2026-05-12 16:17:49');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
