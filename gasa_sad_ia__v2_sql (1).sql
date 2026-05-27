-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : mer. 27 mai 2026 à 00:54
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
-- Base de données : `gasa_sad_ia _v2.sql`
--

-- --------------------------------------------------------

--
-- Structure de la table `analyses_ia`
--

DROP TABLE IF EXISTS `analyses_ia`;
CREATE TABLE IF NOT EXISTS `analyses_ia` (
  `analyse_id` int NOT NULL AUTO_INCREMENT,
  `consultation_id` int NOT NULL,
  `modele_ia` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `probabilite` float DEFAULT NULL,
  `diagnostics_suggeres` json DEFAULT NULL,
  `scoring_confiance` float DEFAULT NULL,
  `donnees_entree` json DEFAULT NULL,
  `temps_traitement` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`analyse_id`),
  KEY `consultation_id` (`consultation_id`)
) ENGINE=MyISAM AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `analyses_ia`
--

INSERT INTO `analyses_ia` (`analyse_id`, `consultation_id`, `modele_ia`, `probabilite`, `diagnostics_suggeres`, `scoring_confiance`, `donnees_entree`, `temps_traitement`, `created_at`) VALUES
(18, 75, 'RandomForest_v1.0_Finale', 0.0442395, '[{\"maladie\": \"Hyperthyroïdie\", \"probabilite\": 0.04423953701565932}, {\"maladie\": \"Hypothyroïdie\", \"probabilite\": 0.044099927982952994}, {\"maladie\": \"Épilepsie\", \"probabilite\": 0.04197689413533518}]', 0.0442395, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-15\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-15\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"\", \"type\": \"BIOLOGIE\", \"resultats\": \"\"}]}', NULL, '2026-05-15 14:18:15'),
(19, 79, 'RandomForest_v1.0_Preliminaire', 0.109104, '[{\"maladie\": \"Sclérose latérale amyotrophique\", \"probabilite\": 0.10910425802499316}, {\"maladie\": \"Parkinson\", \"probabilite\": 0.05569880998096486}, {\"maladie\": \"Alzheimer\", \"probabilite\": 0.04307117650564814}]', 0.109104, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Faiblesse musculaire\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Paralysie\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Spasticité\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Perte de réflexes\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Trouble de l\'équilibre\", \"severite\": \"Sévère\", \"duree_jours\": 1}, {\"nom\": \"Chute\", \"severite\": \"Sévère\", \"duree_jours\": 2}], \"signes_vitaux\": {\"temperature\": 37, \"saturation_o2\": 98, \"tension_systolique\": 120, \"frequence_cardiaque\": 70, \"tension_diastolique\": 80, \"frequence_respiratoire\": 16}}', NULL, '2026-05-15 14:45:17'),
(17, 72, 'RandomForest_v1.0_Finale', 0.070752, '[{\"maladie\": \"Grippe\", \"probabilite\": 0.07075197607099976}, {\"maladie\": \"Rougeole\", \"probabilite\": 0.06304704057659145}, {\"maladie\": \"Hypertrophie bénigne de prostate\", \"probabilite\": 0.03357082543962091}]', 0.070752, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-15\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-15\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}]}', NULL, '2026-05-15 12:20:24'),
(20, 79, 'RandomForest_v1.0_Finale', 0.108591, '[{\"maladie\": \"Sclérose latérale amyotrophique\", \"probabilite\": 0.10859107315681132}, {\"maladie\": \"Parkinson\", \"probabilite\": 0.05571669613522403}, {\"maladie\": \"Alzheimer\", \"probabilite\": 0.043260117397853994}]', 0.108591, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-15\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-15\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}], \"symptomes\": [{\"nom\": \"Faiblesse musculaire\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Paralysie\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Spasticité\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Perte de réflexes\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Trouble de l\'équilibre\", \"severite\": \"Sévère\", \"duree_jours\": 1}, {\"nom\": \"Chute\", \"severite\": \"Sévère\", \"duree_jours\": 2}], \"signes_vitaux\": {\"temperature\": 37, \"saturation_o2\": 98, \"tension_systolique\": 120, \"frequence_cardiaque\": 70, \"tension_diastolique\": 80, \"frequence_respiratoire\": 16}}', NULL, '2026-05-15 14:45:17'),
(21, 101, 'RandomForest_v1.0_Finale', 0.0997547, '[{\"maladie\": \"Sclérose latérale amyotrophique\", \"probabilite\": 0.0997546536349264}, {\"maladie\": \"Acné\", \"probabilite\": 0.08566358297385125}, {\"maladie\": \"Acromégalie\", \"probabilite\": 0.0700287227315784}]', 0.0997547, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-17\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-17\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}]}', NULL, '2026-05-17 14:27:23'),
(22, 104, 'RandomForest_v1.0_Finale', 0.0545706, '[{\"maladie\": \"Hypertrophie bénigne de prostate\", \"probabilite\": 0.054570612425529984}, {\"maladie\": \"Alzheimer\", \"probabilite\": 0.048387003877235824}, {\"maladie\": \"Acromégalie\", \"probabilite\": 0.032309505173669824}]', 0.0545706, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-17\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-17\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}]}', NULL, '2026-05-17 16:53:05'),
(23, 103, 'RandomForest_v1.0_Finale', 0.256061, '[{\"maladie\": \"Influenza A/B\", \"probabilite\": 0.25606060606060604}, {\"maladie\": \"Grippe\", \"probabilite\": 0.085}, {\"maladie\": \"Pneumonie\", \"probabilite\": 0.06613095238095239}]', 0.256061, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-17\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-17\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"Globules Blancs\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-17\", \"description\": \"Infection\", \"isSuggested\": true, \"unite_mesure\": \"K/µL\", \"valeur_numerique\": 7}, {\"nom\": \"Neutrophiles\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-17\", \"description\": \"Infection bactérienne\", \"isSuggested\": true, \"unite_mesure\": \"%\", \"valeur_numerique\": 60}]}', NULL, '2026-05-17 18:24:06'),
(24, 111, 'RandomForest_v1.0_Preliminaire', 0.0314286, '[{\"maladie\": \"Gonorrhée\", \"probabilite\": 0.03142857142857143}, {\"maladie\": \"Dégénérescence maculaire\", \"probabilite\": 0.02571428571428571}, {\"maladie\": \"Sclérose latérale amyotrophique\", \"probabilite\": 0.022857142857142857}]', 0.0314286, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Convulsions\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Vision jaunâtre\", \"severite\": \"Modérée\", \"duree_jours\": 1}], \"signes_vitaux\": {\"poids\": 70, \"taille\": 178, \"temperature\": 37, \"saturation_o2\": 98, \"tension_systolique\": 120, \"frequence_cardiaque\": 70, \"tension_diastolique\": 80, \"frequence_respiratoire\": 16}}', NULL, '2026-05-22 12:16:28'),
(25, 111, 'RandomForest_v1.0_Finale', 0.0314286, '[{\"maladie\": \"Gonorrhée\", \"probabilite\": 0.03142857142857143}, {\"maladie\": \"Sclérose latérale amyotrophique\", \"probabilite\": 0.02571428571428571}, {\"maladie\": \"Molluscum contagiosum\", \"probabilite\": 0.02571428571428571}]', 0.0314286, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-22\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-22\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"Eosinophiles\", \"type\": \"IMAGERIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-22\", \"unite_mesure\": \"K/µL\", \"valeur_numerique\": 12.5}], \"symptomes\": [{\"nom\": \"Convulsions\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Vision jaunâtre\", \"severite\": \"Modérée\", \"duree_jours\": 1}], \"signes_vitaux\": {\"poids\": 70, \"taille\": 178, \"temperature\": 37, \"saturation_o2\": 98, \"tension_systolique\": 120, \"frequence_cardiaque\": 70, \"tension_diastolique\": 80, \"frequence_respiratoire\": 16}}', NULL, '2026-05-22 12:16:28'),
(26, 110, 'RandomForest_v1.0_Preliminaire', 0.0806913, '[{\"maladie\": \"Constipation chronique\", \"probabilite\": 0.08069134328041581}, {\"maladie\": \"Stéatose hépatique\", \"probabilite\": 0.05628041094836493}, {\"maladie\": \"Cholangite\", \"probabilite\": 0.05000109422758148}]', 0.0806913, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Douleurs musculaires\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Douleur abdominale\", \"severite\": \"Modérée\", \"duree_jours\": 1}], \"signes_vitaux\": {\"temperature\": 37, \"saturation_o2\": 98, \"tension_systolique\": 120, \"frequence_cardiaque\": 70, \"tension_diastolique\": 80, \"frequence_respiratoire\": 16}}', NULL, '2026-05-24 17:08:55'),
(27, 110, 'RandomForest_v1.0_Finale', 0.0713933, '[{\"maladie\": \"Constipation chronique\", \"probabilite\": 0.07139331372376556}, {\"maladie\": \"Stéatose hépatique\", \"probabilite\": 0.06128041094836493}, {\"maladie\": \"Cholangite\", \"probabilite\": 0.05000109422758147}]', 0.0713933, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-24\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-24\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}], \"symptomes\": [{\"nom\": \"Douleurs musculaires\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Douleur abdominale\", \"severite\": \"Modérée\", \"duree_jours\": 1}], \"signes_vitaux\": {\"temperature\": 37, \"saturation_o2\": 98, \"tension_systolique\": 120, \"frequence_cardiaque\": 70, \"tension_diastolique\": 80, \"frequence_respiratoire\": 16}}', NULL, '2026-05-24 17:08:55'),
(28, 120, 'RandomForest_v1.0_Preliminaire', 0.035987, '[{\"maladie\": \"Vitiligo\", \"probabilite\": 0.035987020583895336}, {\"maladie\": \"Verrue\", \"probabilite\": 0.028351131870411245}, {\"maladie\": \"Acné\", \"probabilite\": 0.028208234135649005}]', 0.035987, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Albuminémie basse\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Anémie\", \"severite\": \"Modérée\", \"duree_jours\": 1}], \"signes_vitaux\": {\"temperature\": 37, \"saturation_o2\": 98, \"tension_systolique\": 120, \"frequence_cardiaque\": 70, \"tension_diastolique\": 80, \"frequence_respiratoire\": 16}}', NULL, '2026-05-25 23:57:35'),
(29, 120, 'RandomForest_v1.0_Finale', 0.0312289, '[{\"maladie\": \"Polyglobulie\", \"probabilite\": 0.031228855309197823}, {\"maladie\": \"Verrue\", \"probabilite\": 0.02809486034343077}, {\"maladie\": \"Acné\", \"probabilite\": 0.02753902202364849}]', 0.0312289, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-25\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-25\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}], \"symptomes\": [{\"nom\": \"Albuminémie basse\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Anémie\", \"severite\": \"Modérée\", \"duree_jours\": 1}], \"signes_vitaux\": {\"temperature\": 37, \"saturation_o2\": 98, \"tension_systolique\": 120, \"frequence_cardiaque\": 70, \"tension_diastolique\": 80, \"frequence_respiratoire\": 16}}', NULL, '2026-05-25 23:57:36'),
(30, 122, 'RandomForest_v1.0_Finale', 0.0312289, '[{\"maladie\": \"Polyglobulie\", \"probabilite\": 0.031228855309197823}, {\"maladie\": \"Verrue\", \"probabilite\": 0.02809486034343076}, {\"maladie\": \"Acné\", \"probabilite\": 0.02753902202364849}]', 0.0312289, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-26\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-26\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}]}', NULL, '2026-05-26 00:50:05'),
(31, 123, 'RandomForest_v1.0_Finale', 0.0405852, '[{\"maladie\": \"Sclérose latérale amyotrophique\", \"probabilite\": 0.040585240033154425}, {\"maladie\": \"Verrue\", \"probabilite\": 0.032468983970916854}, {\"maladie\": \"Acné\", \"probabilite\": 0.0302629346501863}]', 0.0405852, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-26\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-26\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}]}', NULL, '2026-05-26 01:01:13');

-- --------------------------------------------------------

--
-- Structure de la table `consultations`
--

DROP TABLE IF EXISTS `consultations`;
CREATE TABLE IF NOT EXISTS `consultations` (
  `consultation_id` int NOT NULL AUTO_INCREMENT,
  `nom_patient` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `patient_id` int DEFAULT NULL,
  `date_heure` datetime NOT NULL,
  `motif` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `medecin_id` int DEFAULT NULL,
  `statut` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'en attente',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`consultation_id`),
  KEY `medecin_id` (`medecin_id`),
  KEY `idx_patient_id` (`patient_id`)
) ENGINE=MyISAM AUTO_INCREMENT=125 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `consultations`
--

INSERT INTO `consultations` (`consultation_id`, `nom_patient`, `patient_id`, `date_heure`, `motif`, `medecin_id`, `statut`, `created_at`) VALUES
(76, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:39:21', 'Consultation médicale', 15, 'en attente', '2026-05-15 14:39:20'),
(72, 'patient MOI', 47, '2026-05-15 12:55:25', 'écoulement nasal', 15, 'terminée', '2026-05-15 11:55:25'),
(77, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:39:49', 'Consultation médicale', 15, 'en attente', '2026-05-15 14:39:49'),
(70, 'Lola LULU', 45, '2026-05-15 12:06:21', 'Consultation médicale', 15, 'en attente', '2026-05-15 11:06:21'),
(75, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:00:51', 'Malaises ', 15, 'terminée', '2026-05-15 14:00:50'),
(74, 'KOLO YANICK', 49, '2026-05-15 13:34:05', 'Consultation médicale', NULL, 'en attente', '2026-05-15 12:34:05'),
(78, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:39:50', 'Consultation médicale', 15, 'en attente', '2026-05-15 14:39:49'),
(79, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:45:18', '', NULL, 'terminée', '2026-05-15 14:45:17'),
(80, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:45:48', 'Consultation médicale', 15, 'en attente', '2026-05-15 14:45:47'),
(81, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:45:48', 'Consultation médicale', 15, 'en attente', '2026-05-15 14:45:47'),
(82, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:45:56', 'Consultation médicale', 15, 'en attente', '2026-05-15 14:45:55'),
(83, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:45:56', 'Consultation médicale', 15, 'en attente', '2026-05-15 14:45:55'),
(84, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:46:05', 'Consultation médicale', 15, 'en attente', '2026-05-15 14:46:05'),
(85, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:46:05', 'Consultation médicale', 15, 'en attente', '2026-05-15 14:46:05'),
(86, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:55:18', 'Consultation médicale', 15, 'en attente', '2026-05-15 14:55:17'),
(87, 'Mathieux  AHOUANNOU', 50, '2026-05-15 16:08:49', 'Consultation médicale', 15, 'en attente', '2026-05-15 15:08:49'),
(88, 'Mathieux  AHOUANNOU', 50, '2026-05-15 16:27:28', 'Consultation médicale', 15, 'en attente', '2026-05-15 15:27:27'),
(89, 'fgreg MATHKK', 63, '2026-05-15 16:58:48', 'Consultation médicale', 15, 'en attente', '2026-05-15 15:58:47'),
(90, 'KOLO YANICK', 49, '2026-05-15 16:59:05', 'Consultation médicale', 15, 'en attente', '2026-05-15 15:59:04'),
(91, 'KOLO YANICK', 49, '2026-05-16 17:45:03', 'Consultation médicale', 15, 'en attente', '2026-05-16 16:45:03'),
(92, 'Jen-Luc MELENCHON', 64, '2026-05-16 18:31:28', 'Consultation médicale', 15, 'en attente', '2026-05-16 17:31:27'),
(93, 'Patien TEST', 65, '2026-05-17 01:36:55', 'Consultation médicale', 15, 'en attente', '2026-05-17 00:36:55'),
(94, 'Patien TEST', 65, '2026-05-17 02:04:17', 'Consultation médicale', 15, 'en attente', '2026-05-17 01:04:16'),
(95, 'fgreg MATHKK', 63, '2026-05-17 02:04:25', 'Consultation médicale', 15, 'en attente', '2026-05-17 01:04:24'),
(96, 'KOLO YANICK', 49, '2026-05-17 02:04:27', 'Consultation médicale', 15, 'en attente', '2026-05-17 01:04:27'),
(97, 'patient MOI', 47, '2026-05-17 02:04:34', 'Consultation médicale', 15, 'en attente', '2026-05-17 01:04:34'),
(98, 'KOLO YANICK', 49, '2026-05-17 03:18:22', 'Consultation médicale', 16, 'en attente', '2026-05-17 02:18:22'),
(99, 'KOLO YANICK', 49, '2026-05-17 03:18:30', 'Consultation médicale', 16, 'en attente', '2026-05-17 02:18:30'),
(100, 'KOLO YANICK', 49, '2026-05-17 03:18:45', 'Consultation médicale', 16, 'en attente', '2026-05-17 02:18:45'),
(101, 'NouveauConsult PATIENT', 66, '2026-05-17 14:09:47', 'Test de diagnostic', 15, 'terminée', '2026-05-17 13:09:46'),
(102, 'patient MOI', 47, '2026-05-17 17:33:41', 'Rhumatisme ', NULL, 'en attente', '2026-05-17 16:33:41'),
(103, 'patient MOI', 47, '2026-05-17 17:39:00', 'Rhumatisme', 15, 'terminée', '2026-05-17 16:39:00'),
(104, 'KOLO YANICK', 49, '2026-05-17 17:48:22', 'Mal de dos', 15, 'terminée', '2026-05-17 16:48:21'),
(105, 'KOLO YANICK', 49, '2026-05-17 17:52:27', 'Consultation médicale', 15, 'en attente', '2026-05-17 16:52:27'),
(106, 'Patien TEST', 65, '2026-05-17 19:08:34', 'Consultation médicale', 15, 'en attente', '2026-05-17 18:08:34'),
(107, 'Yanick M\'POLO', 67, '2026-05-19 13:13:16', 'Consultation médicale', 16, 'en attente', '2026-05-19 12:13:16'),
(108, 'Yanick M\'POLO', 67, '2026-05-19 13:13:51', 'Consultation médicale', 16, 'en attente', '2026-05-19 12:13:51'),
(109, 'Yanick M\'POLO', 67, '2026-05-19 16:16:08', 'v', NULL, 'en attente', '2026-05-19 15:16:08'),
(110, 'Richelle AMAHAYA', 68, '2026-05-19 17:10:05', 'Consultation médicale', 15, 'terminée', '2026-05-19 16:10:04'),
(111, 'liee au sexe CONSULT', 69, '2026-05-22 11:50:45', 'Consultation médicale', 15, 'terminée', '2026-05-22 10:50:45'),
(112, 'Jaan MARKOV', 70, '2026-05-23 22:16:22', 'Consultation médicale', 15, 'en attente', '2026-05-23 21:16:21'),
(113, 'Niall ABALO', 71, '2026-05-24 19:34:43', 'Consultation médicale', 15, 'en attente', '2026-05-24 18:34:42'),
(114, 'Yanick M\'POLO', 67, '2026-05-25 20:24:27', 'Consultation médicale', NULL, 'en attente', '2026-05-25 19:24:26'),
(115, 'Yanick M\'POLO', 67, '2026-05-25 20:25:44', 'Consultation médicale', NULL, 'en attente', '2026-05-25 19:25:44'),
(116, 'Yanick M\'POLO', 67, '2026-05-25 20:33:51', 'Consultation médicale', 15, 'en attente', '2026-05-25 19:33:51'),
(117, 'Yanick M\'POLO', 67, '2026-05-25 21:43:29', 'Consultation médicale', 15, 'en attente', '2026-05-25 20:43:29'),
(118, 'Yanick M\'POLO', 67, '2026-05-25 22:00:59', 'Consultation médicale', 15, 'en attente', '2026-05-25 21:00:58'),
(119, 'liee au sexe CONSULT', 69, '2026-05-25 23:57:51', 'Consultation médicale', 15, 'en attente', '2026-05-25 22:57:50'),
(120, 'Jaan MARKOV', 70, '2026-05-25 23:58:13', 'Consultation médicale', 15, 'terminée', '2026-05-25 22:58:12'),
(121, 'Yanick M\'POLO', 67, '2026-05-26 00:16:46', 'Consultation médicale', 15, 'en attente', '2026-05-25 23:16:45'),
(122, 'Jean-luc MARTISE', 72, '2026-05-26 01:34:21', 'malaises ', 15, 'terminée', '2026-05-26 00:34:21'),
(123, 'Yanick M\'POLO', 67, '2026-05-26 01:52:23', 'Malisse importante', 15, 'terminée', '2026-05-26 00:52:22'),
(124, 'Yanick M\'POLO', 67, '2026-05-27 01:25:05', 'Consultation médicale', 15, 'en attente', '2026-05-27 00:25:05');

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
  `code_icd10` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nom_maladie` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `certitude` float DEFAULT NULL,
  `statut` enum('PROVISOIRE','CONFIRMÉ','REJETÉ','ARCHIVÉ') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'PROVISOIRE',
  `severite` enum('LEGER','MODERE','GRAVE','CRITIQUE') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `justification` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `date_validation` date DEFAULT NULL,
  PRIMARY KEY (`diagnostic_id`),
  KEY `consultation_id` (`consultation_id`),
  KEY `analyse_ia_id` (`analyse_ia_id`),
  KEY `medecin_id` (`medecin_id`),
  KEY `dossier_id` (`dossier_id`)
) ENGINE=MyISAM AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `diagnostics`
--

INSERT INTO `diagnostics` (`diagnostic_id`, `consultation_id`, `analyse_ia_id`, `medecin_id`, `dossier_id`, `code_icd10`, `nom_maladie`, `description`, `certitude`, `statut`, `severite`, `justification`, `date_validation`) VALUES
(19, 75, 18, NULL, 20, NULL, 'Hyperthyroïdie', 'Validation : CONFIRMÉ. Suggestion IA : Hyperthyroïdie (4.4%). Notes : ', 0.0442395, 'CONFIRMÉ', NULL, NULL, '2026-05-15'),
(18, 72, 17, NULL, 19, NULL, 'Grippe', 'Validation : CONFIRMÉ. Suggestion IA : Grippe (7.1%). Notes : ', 0.070752, 'CONFIRMÉ', NULL, NULL, '2026-05-15'),
(20, 79, 20, NULL, 20, NULL, 'Sclérose latérale amyotrophique', 'Validation : CONFIRMÉ. Suggestion IA : Sclérose latérale amyotrophique (10.9%). Notes : ', 0.108591, 'CONFIRMÉ', NULL, NULL, '2026-05-15'),
(21, 101, 21, NULL, 21, NULL, 'Sclérose latérale amyotrophique', 'Validation : CONFIRMÉ. Suggestion IA : Sclérose latérale amyotrophique (10.0%). Notes : ', 0.0997547, 'CONFIRMÉ', NULL, NULL, '2026-05-17'),
(22, 104, 22, NULL, 22, NULL, 'Hypertrophie bénigne de prostate', 'Validation : CONFIRMÉ. Suggestion IA : Hypertrophie bénigne de prostate (5.5%). Notes : ', 0.0545706, 'CONFIRMÉ', NULL, NULL, '2026-05-17'),
(23, 103, 23, NULL, 19, NULL, 'Influenza A/B', 'Validation : CONFIRMÉ. Suggestion IA : Influenza A/B (25.6%). Notes : ', 0.256061, 'CONFIRMÉ', NULL, NULL, '2026-05-17'),
(24, 111, 25, NULL, 23, NULL, 'Paludisme grave (Neuropaludisme)', 'Validation : REJETÉ. Suggestion IA : Gonorrhée (3.1%). Notes : ', 0.0314286, 'REJETÉ', NULL, NULL, '2026-05-22'),
(25, 110, 27, NULL, 24, NULL, 'Constipation chronique', 'Validation : CONFIRMÉ. Suggestion IA : Constipation chronique (7.1%). Notes : ', 0.0713933, 'CONFIRMÉ', NULL, NULL, '2026-05-24'),
(26, 120, 29, NULL, 25, NULL, 'Polyglobulie', 'Validation : CONFIRMÉ. Suggestion IA : Polyglobulie (3.1%). Notes : ', 0.0312289, 'CONFIRMÉ', NULL, NULL, '2026-05-26'),
(27, 122, 30, NULL, 26, NULL, 'Polyglobulie', 'Validation : CONFIRMÉ. Suggestion IA : Polyglobulie (3.1%). Notes : ', 0.0312289, 'CONFIRMÉ', NULL, NULL, '2026-05-26'),
(28, 123, 31, NULL, 27, NULL, 'Sclérose latérale amyotrophique', 'Validation : CONFIRMÉ. Suggestion IA : Sclérose latérale amyotrophique (4.1%). Notes : ', 0.0405852, 'CONFIRMÉ', NULL, NULL, '2026-05-26');

-- --------------------------------------------------------

--
-- Structure de la table `dossiers_medicaux`
--

DROP TABLE IF EXISTS `dossiers_medicaux`;
CREATE TABLE IF NOT EXISTS `dossiers_medicaux` (
  `dossier_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `numero_dossier` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `antecedents_familiaux` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `antecedents_personnels` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `allergies` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `date_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`dossier_id`),
  UNIQUE KEY `patient_id` (`patient_id`),
  UNIQUE KEY `numero_dossier` (`numero_dossier`),
  KEY `idx_patient` (`patient_id`)
) ENGINE=MyISAM AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
(17, 35, 'DM-20260511154842-35', NULL, NULL, NULL, '2026-05-11 14:48:42'),
(20, 50, 'DM-20260515151815-50', NULL, NULL, NULL, '2026-05-15 14:18:15'),
(19, 47, 'DM-20260515132024-47', NULL, NULL, NULL, '2026-05-15 12:20:24'),
(21, 66, 'DM-20260517152723-66', NULL, NULL, NULL, '2026-05-17 14:27:23'),
(22, 49, 'DM-20260517175305-49', NULL, NULL, NULL, '2026-05-17 16:53:05'),
(23, 69, 'DM-20260522131628-69', NULL, NULL, NULL, '2026-05-22 12:16:28'),
(24, 68, 'DM-20260524180855-68', NULL, NULL, NULL, '2026-05-24 17:08:55'),
(25, 70, 'DM-20260526005735-70', NULL, NULL, NULL, '2026-05-25 23:57:35'),
(26, 72, 'DM-20260526015005-72', NULL, NULL, NULL, '2026-05-26 00:50:05'),
(27, 67, 'DM-20260526020113-67', NULL, NULL, NULL, '2026-05-26 01:01:13');

-- --------------------------------------------------------

--
-- Structure de la table `examens`
--

DROP TABLE IF EXISTS `examens`;
CREATE TABLE IF NOT EXISTS `examens` (
  `examen_id` int NOT NULL AUTO_INCREMENT,
  `consultation_id` int NOT NULL,
  `type` enum('CLINIQUE','IMAGERIE','BIOLOGIE','ELECTROCARDIOGRAMME') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nom` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `resultats` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `valeur_numerique` float DEFAULT NULL,
  `unite_mesure` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `statut` enum('DEMANDE','EN_COURS','REALISE','ANALYSE') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'DEMANDE',
  `date_examen` date DEFAULT NULL,
  `is_suggested` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`examen_id`),
  KEY `consultation_id` (`consultation_id`)
) ENGINE=MyISAM AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `examens`
--

INSERT INTO `examens` (`examen_id`, `consultation_id`, `type`, `nom`, `description`, `resultats`, `valeur_numerique`, `unite_mesure`, `statut`, `date_examen`, `is_suggested`) VALUES
(35, 79, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-15', 1),
(34, 75, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-15', 1),
(33, 75, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-15', 1),
(31, 72, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-15', 1),
(32, 72, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-15', 1),
(36, 79, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-15', 1),
(37, 101, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-17', 1),
(38, 101, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-17', 1),
(39, 104, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-17', 1),
(40, 104, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-17', 1),
(41, 103, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-17', 1),
(42, 103, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-17', 1),
(43, 103, 'BIOLOGIE', 'Globules Blancs', 'Infection', NULL, 7, 'K/µL', 'REALISE', '2026-05-17', 1),
(44, 103, 'BIOLOGIE', 'Neutrophiles', 'Infection bactérienne', NULL, 60, '%', 'REALISE', '2026-05-17', 1),
(45, 111, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-22', 1),
(46, 111, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-22', 1),
(47, 111, 'IMAGERIE', 'Eosinophiles', NULL, NULL, 12.5, 'K/µL', 'REALISE', '2026-05-22', 0),
(48, 110, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-24', 1),
(49, 110, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-24', 1),
(50, 120, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-25', 1),
(51, 120, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-25', 1),
(52, 122, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-26', 1),
(53, 122, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-26', 1),
(54, 123, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-26', 1),
(55, 123, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-26', 1);

-- --------------------------------------------------------

--
-- Structure de la table `historique_prediction`
--

DROP TABLE IF EXISTS `historique_prediction`;
CREATE TABLE IF NOT EXISTS `historique_prediction` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `consultation_id` int DEFAULT NULL,
  `predicted_disease` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `confidence` float NOT NULL,
  `confidence_level` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `prediction_probabilities` json DEFAULT NULL,
  `feature_values` json DEFAULT NULL,
  `top_features` json DEFAULT NULL,
  `model_version` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `model_accuracy` float DEFAULT NULL,
  `is_validated` int DEFAULT NULL,
  `validated_by` int DEFAULT NULL,
  `validated_at` datetime DEFAULT NULL,
  `validation_notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `actual_disease` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `validated_by` (`validated_by`),
  KEY `ix_prediction_history_created_at` (`created_at`),
  KEY `ix_prediction_history_consultation_id` (`consultation_id`),
  KEY `ix_prediction_history_patient_id` (`patient_id`),
  KEY `ix_prediction_history_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `historique_prediction`
--

INSERT INTO `historique_prediction` (`id`, `patient_id`, `consultation_id`, `predicted_disease`, `confidence`, `confidence_level`, `prediction_probabilities`, `feature_values`, `top_features`, `model_version`, `model_accuracy`, `is_validated`, `validated_by`, `validated_at`, `validation_notes`, `actual_disease`, `created_at`, `updated_at`) VALUES
(1, 47, 103, 'Influenza A/B', 0.256061, 'LOW', '{\"Grippe\": 0.085, \"Pneumonie\": 0.06613095238095239, \"Influenza A/B\": 0.25606060606060604}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Influenza A/B', '2026-05-17 18:24:06', '2026-05-17 18:24:06'),
(2, 69, 111, 'Gonorrhée', 0.0314286, 'LOW', '{\"Gonorrhée\": 0.03142857142857143, \"Molluscum contagiosum\": 0.02571428571428571, \"Sclérose latérale amyotrophique\": 0.02571428571428571}', NULL, NULL, 'RandomForest_v1.0', NULL, -1, NULL, NULL, NULL, 'Paludisme grave (Neuropaludisme)', '2026-05-22 12:16:29', '2026-05-22 12:16:29'),
(3, 68, 110, 'Constipation chronique', 0.0713933, 'LOW', '{\"Cholangite\": 0.05000109422758147, \"Stéatose hépatique\": 0.06128041094836493, \"Constipation chronique\": 0.07139331372376556}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Constipation chronique', '2026-05-24 17:08:55', '2026-05-24 17:08:55'),
(4, 70, 120, 'Polyglobulie', 0.0312289, 'LOW', '{\"Acné\": 0.02753902202364849, \"Verrue\": 0.02809486034343077, \"Polyglobulie\": 0.031228855309197823}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Polyglobulie', '2026-05-25 23:57:36', '2026-05-25 23:57:36'),
(5, 72, 122, 'Polyglobulie', 0.0312289, 'LOW', '{\"Acné\": 0.02753902202364849, \"Verrue\": 0.02809486034343076, \"Polyglobulie\": 0.031228855309197823}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Polyglobulie', '2026-05-26 00:50:05', '2026-05-26 00:50:05'),
(6, 67, 123, 'Sclérose latérale amyotrophique', 0.0405852, 'LOW', '{\"Acné\": 0.0302629346501863, \"Verrue\": 0.032468983970916854, \"Sclérose latérale amyotrophique\": 0.040585240033154425}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Sclérose latérale amyotrophique', '2026-05-26 01:01:13', '2026-05-26 01:01:13');

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
  `nom` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenoms` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `specialite` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `telephone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `disponible` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `role` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`medecin_id`)
) ENGINE=MyISAM AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
(17, 'BERNARD', 'Sophie Marie', 'Médecin Général', '00000000', 1, '2026-05-09 14:07:51', NULL),
(18, 'AMAHAYA', 'Richelle', 'Gynécologie-Obstétrique', 'N/A', 1, '2026-05-19 16:37:29', NULL);

-- --------------------------------------------------------

--
-- Structure de la table `medicaments`
--

DROP TABLE IF EXISTS `medicaments`;
CREATE TABLE IF NOT EXISTS `medicaments` (
  `medicament_id` int NOT NULL AUTO_INCREMENT,
  `ordonnance_id` int NOT NULL,
  `nom_commercial` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `denomination_commune` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dosage` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `forme` enum('COMPRIME','INJECTION','SIROP','CREME') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `quantite` int DEFAULT NULL,
  `frequence` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `voie_administration` enum('ORALE','INTRAVEINEUSE','CUTANEE','INTRAMUSCULAIRE') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `duree_jours` int DEFAULT NULL,
  PRIMARY KEY (`medicament_id`),
  KEY `ordonnance_id` (`ordonnance_id`)
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
  `posologie_generale` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
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
  `nom` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenoms` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_naissance` date NOT NULL,
  `sexe` enum('M','F') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `groupe_sanguin` enum('A+','A-','B+','B-','AB+','AB-','O+','O-') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telephone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `adresse` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`patient_id`)
) ENGINE=MyISAM AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `patients`
--

INSERT INTO `patients` (`patient_id`, `nom`, `prenoms`, `date_naissance`, `sexe`, `groupe_sanguin`, `telephone`, `email`, `adresse`, `created_at`) VALUES
(72, 'MARTISE', 'Jean-luc', '2009-03-26', 'M', 'B+', NULL, NULL, NULL, '2026-05-26 00:34:21'),
(70, 'MARKOV', 'Jaan', '2004-01-01', 'M', NULL, NULL, NULL, NULL, '2026-05-23 21:16:21'),
(69, 'CONSULT', 'liee au sexe', '2001-01-01', 'F', NULL, NULL, NULL, NULL, '2026-05-22 10:50:45'),
(67, 'M\'POLO', 'Yanick', '2001-01-01', 'M', NULL, NULL, NULL, NULL, '2026-05-19 12:13:16'),
(68, 'AMAHAYA', 'Richelle', '2005-01-01', 'F', NULL, NULL, NULL, NULL, '2026-05-19 16:10:04'),
(65, 'TEST', 'Patien', '2010-01-01', 'F', NULL, NULL, NULL, NULL, '2026-05-17 00:36:55'),
(66, 'PATIENT', 'NouveauConsult', '1990-02-12', 'M', NULL, NULL, NULL, NULL, '2026-05-17 13:09:46'),
(49, 'YANICK', 'KOLO', '1900-01-01', 'M', NULL, NULL, NULL, NULL, '2026-05-15 12:34:05'),
(47, 'MOI', 'patient', '1990-07-03', 'M', 'O-', '0155554444', NULL, NULL, '2026-05-15 11:55:25'),
(64, 'MELENCHON', 'Jen-Luc', '2018-06-17', 'M', 'A-', '2344567789', NULL, NULL, '2026-05-16 17:31:27'),
(45, 'LULU', 'Lola', '2004-02-14', 'F', NULL, NULL, NULL, NULL, '2026-05-15 11:06:21'),
(50, 'AHOUANNOU', 'Mathieux ', '2010-01-15', 'M', 'AB+', NULL, 'matieux@gmail.com', NULL, '2026-05-15 14:00:50');

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
) ENGINE=MyISAM AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `signes_vitaux`
--

INSERT INTO `signes_vitaux` (`signes_vitaux_id`, `consultation_id`, `infirmier_id`, `date_enregistrement`, `tension_systolique`, `tension_diastolique`, `frequence_cardiaque`, `temperature`, `frequence_respiratoire`, `saturation_oxygene`, `poids`, `taille`, `imc`, `glycemie`) VALUES
(44, 75, NULL, '2026-05-15 14:03:29', 120, 80, 70, 37, 16, 98, 70, 170, 24.2, NULL),
(43, 72, NULL, '2026-05-15 11:58:49', 120, 80, 70, 38, 16, 98, 70, 170, 24.2, NULL),
(45, 79, NULL, '2026-05-15 14:45:17', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(46, 101, NULL, '2026-05-17 13:10:30', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(47, 103, NULL, '2026-05-17 16:44:04', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(48, 104, NULL, '2026-05-17 16:48:47', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(49, 111, NULL, '2026-05-22 12:16:28', 120, 80, 70, 37, 16, 98, 70, 178, 22.1, NULL),
(50, 110, NULL, '2026-05-24 17:08:55', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(51, 120, NULL, '2026-05-25 23:57:35', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(52, 122, NULL, '2026-05-26 00:35:23', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(53, 123, NULL, '2026-05-26 00:53:13', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL);

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
  `numero_suivi` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_suivi` date NOT NULL,
  `etat_general` enum('EXCELLENT','BON','STABLE','DECLINE','CRITIQUE') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `amelioration` enum('EXCELLENTE','BON','MOYEN','MAUVAIS','DECLINE') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pourcentage_amelioration` float DEFAULT NULL,
  `adherence_traitement` float DEFAULT NULL,
  `statut` enum('EN_COURS','TERMINE_SUCCES','TERMINE_ECHEC','A_REPRENDRE') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'EN_COURS',
  `prochaine_consultation` date DEFAULT NULL,
  PRIMARY KEY (`suivi_id`),
  UNIQUE KEY `numero_suivi` (`numero_suivi`),
  KEY `patient_id` (`patient_id`),
  KEY `medecin_id` (`medecin_id`),
  KEY `consultation_id` (`consultation_id`),
  KEY `diagnostic_id` (`diagnostic_id`),
  KEY `traitement_id` (`traitement_id`),
  KEY `dossier_id` (`dossier_id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `suivis`
--

INSERT INTO `suivis` (`suivi_id`, `patient_id`, `medecin_id`, `consultation_id`, `diagnostic_id`, `traitement_id`, `dossier_id`, `numero_suivi`, `date_suivi`, `etat_general`, `amelioration`, `pourcentage_amelioration`, `adherence_traitement`, `statut`, `prochaine_consultation`) VALUES
(1, 47, 15, 103, 23, NULL, 19, 'SV-20260517192406066-103', '2026-05-17', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(2, 69, 15, 111, NULL, NULL, 23, 'SV-20260522131628640-111', '2026-05-22', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(3, 68, 15, 110, NULL, NULL, 24, 'SV-20260524180855282-110', '2026-05-24', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(4, 70, 15, 120, NULL, NULL, 25, 'SV-20260526005736006-120', '2026-05-26', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(5, 72, 15, 122, 27, NULL, 26, 'SV-20260526015005448-122', '2026-05-26', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(6, 67, 15, 123, 28, NULL, 27, 'SV-20260526020113334-123', '2026-05-26', NULL, NULL, NULL, NULL, 'EN_COURS', NULL);

-- --------------------------------------------------------

--
-- Structure de la table `symptomes`
--

DROP TABLE IF EXISTS `symptomes`;
CREATE TABLE IF NOT EXISTS `symptomes` (
  `symptome_id` int NOT NULL AUTO_INCREMENT,
  `consultation_id` int NOT NULL,
  `nom` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `severite` enum('LEGER','MODERE','SEVERE') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_apparition` date DEFAULT NULL,
  `duree_jours` int DEFAULT NULL,
  `zone_atteinte` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `frequence` enum('CONSTANT','INTERMITTENT','PROGRESSIF') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`symptome_id`),
  KEY `consultation_id` (`consultation_id`)
) ENGINE=MyISAM AUTO_INCREMENT=133 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `symptomes`
--

INSERT INTO `symptomes` (`symptome_id`, `consultation_id`, `nom`, `description`, `severite`, `date_apparition`, `duree_jours`, `zone_atteinte`, `frequence`) VALUES
(97, 75, 'Insomnie', NULL, 'LEGER', NULL, 3, NULL, NULL),
(96, 75, 'Fatigue', NULL, 'SEVERE', NULL, 4, NULL, NULL),
(93, 72, 'Congestion nasale', NULL, 'SEVERE', NULL, 1, NULL, NULL),
(94, 72, 'Écoulement nasal', NULL, 'MODERE', NULL, 1, NULL, NULL),
(95, 72, 'Douleurs musculaires', NULL, 'MODERE', NULL, 1, NULL, NULL),
(98, 75, 'Trouble du sommeil', NULL, 'MODERE', NULL, 2, NULL, NULL),
(99, 75, 'Trouble de l\'équilibre', NULL, 'MODERE', NULL, 1, NULL, NULL),
(100, 79, 'Faiblesse musculaire', NULL, 'MODERE', NULL, 1, NULL, NULL),
(101, 79, 'Paralysie', NULL, 'MODERE', NULL, 1, NULL, NULL),
(102, 79, 'Spasticité', NULL, 'MODERE', NULL, 1, NULL, NULL),
(103, 79, 'Perte de réflexes', NULL, 'MODERE', NULL, 1, NULL, NULL),
(104, 79, 'Trouble de l\'équilibre', NULL, 'SEVERE', NULL, 1, NULL, NULL),
(105, 79, 'Chute', NULL, 'SEVERE', NULL, 2, NULL, NULL),
(106, 101, 'Atrophie musculaire', NULL, 'MODERE', NULL, 1, NULL, NULL),
(107, 101, 'Apnée du sommeil', NULL, 'MODERE', NULL, 1, NULL, NULL),
(108, 101, 'Agrandissement des mains pieds', NULL, 'MODERE', NULL, 1, NULL, NULL),
(109, 101, 'Cheveux cassants', NULL, 'MODERE', NULL, 1, NULL, NULL),
(110, 101, 'Comédones', NULL, 'MODERE', NULL, 1, NULL, NULL),
(111, 101, 'Éternuements', NULL, 'MODERE', NULL, 1, NULL, NULL),
(112, 103, 'Maux de tête', NULL, 'SEVERE', NULL, 1, NULL, NULL),
(113, 103, 'Écoulement nasal', NULL, 'MODERE', NULL, 1, NULL, NULL),
(114, 103, 'Fatigue', NULL, 'MODERE', NULL, 1, NULL, NULL),
(115, 103, 'Toux', NULL, 'MODERE', NULL, 1, NULL, NULL),
(116, 103, 'Fièvre élevée', NULL, 'MODERE', NULL, 1, NULL, NULL),
(117, 103, 'Fatigue post-critique', NULL, 'MODERE', NULL, 1, NULL, NULL),
(118, 103, 'Fièvre', NULL, 'MODERE', NULL, 1, NULL, NULL),
(119, 103, 'Fièvre intermittente', NULL, 'MODERE', NULL, 1, NULL, NULL),
(120, 104, 'Besoin fréquent d\'uriner', NULL, 'MODERE', NULL, 1, NULL, NULL),
(121, 104, 'Besoin impérieux de déféquer', NULL, 'MODERE', NULL, 1, NULL, NULL),
(122, 111, 'Convulsions', NULL, 'SEVERE', NULL, 5, NULL, NULL),
(123, 111, 'Vision jaunâtre', NULL, 'MODERE', NULL, 1, NULL, NULL),
(124, 110, 'Douleurs musculaires', NULL, 'MODERE', NULL, 1, NULL, NULL),
(125, 110, 'Douleur abdominale', NULL, 'MODERE', NULL, 1, NULL, NULL),
(126, 120, 'Albuminémie basse', NULL, 'MODERE', NULL, 1, NULL, NULL),
(127, 120, 'Anémie', NULL, 'MODERE', NULL, 1, NULL, NULL),
(128, 122, 'Albuminémie basse', NULL, 'MODERE', NULL, 1, NULL, NULL),
(129, 122, 'Anémie', NULL, 'MODERE', NULL, 1, NULL, NULL),
(130, 123, 'Albuminémie basse', NULL, 'MODERE', NULL, 1, NULL, NULL),
(131, 123, 'Anémie', NULL, 'MODERE', NULL, 1, NULL, NULL),
(132, 123, 'Atrophie musculaire', NULL, 'MODERE', NULL, 1, NULL, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `traitements`
--

DROP TABLE IF EXISTS `traitements`;
CREATE TABLE IF NOT EXISTS `traitements` (
  `traitement_id` int NOT NULL AUTO_INCREMENT,
  `diagnostic_id` int NOT NULL,
  `nom_traitement` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `type` enum('MEDICAMENTEUX','CHIRURGICAL','PHYSIQUE','PSYCHOLOGIQUE') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `duree_jours` int DEFAULT NULL,
  `date_debut` date DEFAULT NULL,
  `date_fin` date DEFAULT NULL,
  `statut` enum('PRESCRIT','EN_COURS','TERMINE','ABANDONNE','ECHEC') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'PRESCRIT',
  `objective_therapeutique` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
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
  `nom` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenoms` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `mot_de_passe` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('admin','medecin','infirmier') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'medecin',
  `actif` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login` datetime DEFAULT NULL,
  PRIMARY KEY (`utilisateur_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `utilisateurs`
--

INSERT INTO `utilisateurs` (`utilisateur_id`, `nom`, `prenoms`, `email`, `mot_de_passe`, `role`, `actif`, `created_at`, `last_login`) VALUES
(1, 'ADMIN', 'Super', 'admin@santeplus.bj', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'admin', 1, '2026-05-02 20:29:04', '2026-05-24 19:32:13'),
(7, 'AGBODJAN', 'Edem Patricia', 'edem.agbodjan@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:12:16', '2026-05-15 14:06:46'),
(6, 'MENSAH', 'Kokou David', 'kokou.mensah@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:12:16', NULL),
(5, 'KOFFI', 'Awa Sylvie', 'awa.koffi@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:12:16', NULL),
(8, 'TOSSOU', 'Yao Emmanuel', 'yao.tossou@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:12:16', NULL),
(9, 'AHOUANSOU', 'Gérard Koffi', 'gerard.ahouansou@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', '2026-05-09 16:52:22'),
(10, 'DOSSOU', 'Marie-Claire Afi', 'marie.dossou@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'medecin', 1, '2026-05-02 23:33:49', '2026-05-27 01:52:47'),
(11, 'LEFEBVRE', 'Jean-Baptiste', 'jean.lefebvre@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'medecin', 1, '2026-05-02 23:33:49', '2026-05-17 23:34:39'),
(12, 'BERNARD', 'Sophie Marie', 'sophie.bernard@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'medecin', 1, '2026-05-02 23:33:49', NULL),
(13, 'PETIT', 'Thomas André', 'thomas.petit@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'medecin', 1, '2026-05-02 23:33:49', NULL),
(14, 'KOUASSI', 'Aya', 'aya.kouassi@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', '2026-05-27 00:00:44'),
(15, 'MENSAH', 'Kofi', 'kofi.mensah@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', NULL),
(16, 'DIALLO', 'Fatoumata', 'fatoumata.diallo@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', NULL),
(17, 'TRAORE', 'Moussa', 'moussa.traore@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', NULL),
(18, 'M\'POLO', 'Yanick', 'yanickmpolo@gasasad.bj', '$2b$12$pEC30rX9D4QRXY9mkH6iTudj6HOqA6PHs0e9HJwC6PZSlJtMTX6O6', 'medecin', 1, '2026-05-09 19:21:06', '2026-05-17 17:50:20'),
(19, 'AMAHAYA', 'Richelle', 'richelleamahaya@gmail.com', '$2b$12$J8KypAInV/RzkIgevQxm.umXRXEc41m5t3OIbHIK8fM9LWfyYiZtO', 'medecin', 1, '2026-05-19 16:37:29', '2026-05-26 16:46:20');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
