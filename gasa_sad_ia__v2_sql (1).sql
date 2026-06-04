-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : mer. 03 juin 2026 à 16:39
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
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `analyses_ia`
--

INSERT INTO `analyses_ia` (`analyse_id`, `consultation_id`, `modele_ia`, `probabilite`, `diagnostics_suggeres`, `scoring_confiance`, `donnees_entree`, `temps_traitement`, `created_at`) VALUES
(17, 72, 'RandomForest_v1.0_Finale', 0.070752, '[{\"maladie\": \"Grippe\", \"probabilite\": 0.07075197607099976}, {\"maladie\": \"Rougeole\", \"probabilite\": 0.06304704057659145}, {\"maladie\": \"Hypertrophie bénigne de prostate\", \"probabilite\": 0.03357082543962091}]', 0.070752, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-15\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-15\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}]}', NULL, '2026-05-15 12:20:24'),
(18, 75, 'RandomForest_v1.0_Finale', 0.0442395, '[{\"maladie\": \"Hyperthyroïdie\", \"probabilite\": 0.04423953701565932}, {\"maladie\": \"Hypothyroïdie\", \"probabilite\": 0.044099927982952994}, {\"maladie\": \"Épilepsie\", \"probabilite\": 0.04197689413533518}]', 0.0442395, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-15\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-15\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"\", \"type\": \"BIOLOGIE\", \"resultats\": \"\"}]}', NULL, '2026-05-15 14:18:15'),
(19, 79, 'RandomForest_v1.0_Preliminaire', 0.109104, '[{\"maladie\": \"Sclérose latérale amyotrophique\", \"probabilite\": 0.10910425802499316}, {\"maladie\": \"Parkinson\", \"probabilite\": 0.05569880998096486}, {\"maladie\": \"Alzheimer\", \"probabilite\": 0.04307117650564814}]', 0.109104, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Faiblesse musculaire\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Paralysie\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Spasticité\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Perte de réflexes\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Trouble de l\'équilibre\", \"severite\": \"Sévère\", \"duree_jours\": 1}, {\"nom\": \"Chute\", \"severite\": \"Sévère\", \"duree_jours\": 2}], \"signes_vitaux\": {\"temperature\": 37, \"saturation_o2\": 98, \"tension_systolique\": 120, \"frequence_cardiaque\": 70, \"tension_diastolique\": 80, \"frequence_respiratoire\": 16}}', NULL, '2026-05-15 14:45:17'),
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
(31, 123, 'RandomForest_v1.0_Finale', 0.0405852, '[{\"maladie\": \"Sclérose latérale amyotrophique\", \"probabilite\": 0.040585240033154425}, {\"maladie\": \"Verrue\", \"probabilite\": 0.032468983970916854}, {\"maladie\": \"Acné\", \"probabilite\": 0.0302629346501863}]', 0.0405852, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-26\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-26\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}]}', NULL, '2026-05-26 01:01:13'),
(32, 121, 'RandomForest_v1.0_Finale', 0.064085, '[{\"maladie\": \"Acromégalie\", \"probabilite\": 0.06408499208396393}, {\"maladie\": \"Polyglobulie\", \"probabilite\": 0.02858320601591161}, {\"maladie\": \"Vitiligo\", \"probabilite\": 0.025205953856608385}]', 0.064085, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}], \"symptomes\": [], \"signes_vitaux\": {\"temperature\": 37, \"saturation_o2\": 98, \"tension_systolique\": 120, \"frequence_cardiaque\": 70, \"tension_diastolique\": 80, \"frequence_respiratoire\": 16}}', NULL, '2026-05-27 01:10:26'),
(33, 125, 'RandomForest_v1.0_Finale', 0.064085, '[{\"maladie\": \"Acromégalie\", \"probabilite\": 0.06408499208396394}, {\"maladie\": \"Polyglobulie\", \"probabilite\": 0.028583206015911612}, {\"maladie\": \"Vitiligo\", \"probabilite\": 0.025205953856608378}]', 0.064085, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}]}', NULL, '2026-05-27 01:23:10'),
(34, 128, 'RandomForest_v1.0_Preliminaire', 0.187663, '[{\"maladie\": \"Glomérulonéphrite\", \"probabilite\": 0.18766347334063968}, {\"maladie\": \"Apnée du sommeil\", \"probabilite\": 0.0918429731211223}, {\"maladie\": \"Acromégalie\", \"probabilite\": 0.06511735809144768}]', 0.187663, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Maux de tête\", \"severite\": \"Modérée\", \"duree_jours\": 87}, {\"nom\": \"Maux de tête matinaux\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Hypertension\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Vertiges\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Palpitations\", \"severite\": \"Modérée\", \"duree_jours\": 90}], \"signes_vitaux\": {\"poids\": 92, \"taille\": 174.7, \"temperature\": 37, \"saturation_o2\": 97, \"tension_systolique\": 165, \"frequence_cardiaque\": 82, \"tension_diastolique\": 100, \"frequence_respiratoire\": 16}}', NULL, '2026-05-27 17:03:45'),
(35, 128, 'RandomForest_v1.0_Finale', 0.149111, '[{\"maladie\": \"Glomérulonéphrite\", \"probabilite\": 0.14911090083457887}, {\"maladie\": \"Apnée du sommeil\", \"probabilite\": 0.1018429731211223}, {\"maladie\": \"Acromégalie\", \"probabilite\": 0.07500107902168024}]', 0.149111, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"Créatinine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 1.2}, {\"nom\": \"Potassium\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mEq/L\", \"valeur_numerique\": 4.2}, {\"nom\": \"Glucose à jeun\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 105}, {\"nom\": \"Cholestérol total\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 220}], \"symptomes\": [{\"nom\": \"Maux de tête\", \"severite\": \"Modérée\", \"duree_jours\": 87}, {\"nom\": \"Maux de tête matinaux\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Hypertension\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Vertiges\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Palpitations\", \"severite\": \"Modérée\", \"duree_jours\": 90}], \"signes_vitaux\": {\"poids\": 92, \"taille\": 174.7, \"temperature\": 37, \"saturation_o2\": 97, \"tension_systolique\": 165, \"frequence_cardiaque\": 82, \"tension_diastolique\": 100, \"frequence_respiratoire\": 16}}', NULL, '2026-05-27 17:03:45'),
(36, 128, 'RandomForest_v1.0_Finale', 0.149111, '[{\"maladie\": \"Glomérulonéphrite\", \"probabilite\": 0.14911090083457887}, {\"maladie\": \"Apnée du sommeil\", \"probabilite\": 0.1018429731211223}, {\"maladie\": \"Acromégalie\", \"probabilite\": 0.07500107902168024}]', 0.149111, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"Créatinine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 1.2}, {\"nom\": \"Potassium\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mEq/L\", \"valeur_numerique\": 4.2}, {\"nom\": \"Glucose à jeun\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 105}, {\"nom\": \"Cholestérol total\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 220}]}', NULL, '2026-05-27 17:46:39'),
(37, 128, 'RandomForest_v1.0_Finale', 0.149111, '[{\"maladie\": \"Glomérulonéphrite\", \"probabilite\": 0.14911090083457887}, {\"maladie\": \"Apnée du sommeil\", \"probabilite\": 0.1018429731211223}, {\"maladie\": \"Acromégalie\", \"probabilite\": 0.07500107902168024}]', 0.149111, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"Créatinine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 1.2}, {\"nom\": \"Potassium\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mEq/L\", \"valeur_numerique\": 4.2}, {\"nom\": \"Glucose à jeun\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 105}, {\"nom\": \"Cholestérol total\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 220}]}', NULL, '2026-05-27 17:46:40'),
(38, 130, 'RandomForest_v1.0_Preliminaire', 0.133734, '[{\"maladie\": \"Syndrome de Cushing\", \"probabilite\": 0.13373358683538514}, {\"maladie\": \"Diabète Type 1\", \"probabilite\": 0.11284051828240198}, {\"maladie\": \"Insuffisance rénale chronique\", \"probabilite\": 0.0699509712566334}]', 0.133734, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Perte de poids\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Grossissement du visage\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Hypertension\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Vergetures\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Fatigue\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Infections fréquentes\", \"severite\": \"Modérée\", \"duree_jours\": 180}], \"signes_vitaux\": {\"poids\": 90, \"taille\": 162, \"temperature\": 37, \"saturation_o2\": 97, \"tension_systolique\": 155, \"frequence_cardiaque\": 88, \"tension_diastolique\": 95, \"frequence_respiratoire\": 15.9}}', NULL, '2026-05-27 22:15:17'),
(39, 130, 'RandomForest_v1.0_Finale', 0.109624, '[{\"maladie\": \"Syndrome de Cushing\", \"probabilite\": 0.10962362643990496}, {\"maladie\": \"Diabète Type 1\", \"probabilite\": 0.09634804413703796}, {\"maladie\": \"Insuffisance rénale chronique\", \"probabilite\": 0.08062081006288765}]', 0.109624, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"Glucose à jeun\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 145}, {\"nom\": \"Potassium\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mEq/L\", \"valeur_numerique\": 4}, {\"nom\": \"Sodium\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-27\", \"unite_mesure\": \"mEq/L\", \"valeur_numerique\": 140}], \"symptomes\": [{\"nom\": \"Perte de poids\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Grossissement du visage\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Hypertension\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Vergetures\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Fatigue\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Infections fréquentes\", \"severite\": \"Modérée\", \"duree_jours\": 180}], \"signes_vitaux\": {\"poids\": 90, \"taille\": 162, \"temperature\": 37, \"saturation_o2\": 97, \"tension_systolique\": 155, \"frequence_cardiaque\": 88, \"tension_diastolique\": 95, \"frequence_respiratoire\": 15.9}}', NULL, '2026-05-27 22:15:17'),
(40, 132, 'RandomForest_v1.0_Preliminaire', 0.411631, '[{\"maladie\": \"Paludisme\", \"probabilite\": 0.4116312456864214}, {\"maladie\": \"Migraine\", \"probabilite\": 0.09692220911109352}, {\"maladie\": \"Salmonellose\", \"probabilite\": 0.0565513916998189}]', 0.411631, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Fièvre intermittente\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Frissons\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Sueurs\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Maux de tête sévère\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Douleurs musculaires\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Nausées\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Vomissements\", \"severite\": \"Sévère\", \"duree_jours\": 5}], \"signes_vitaux\": {\"poids\": 65, \"taille\": 170, \"temperature\": 40.5, \"saturation_o2\": 94, \"tension_systolique\": 100, \"frequence_cardiaque\": 115, \"tension_diastolique\": 62, \"frequence_respiratoire\": 22}}', NULL, '2026-05-28 01:20:39'),
(41, 132, 'RandomForest_v1.0_Finale', 0.392634, '[{\"maladie\": \"Paludisme\", \"probabilite\": 0.39263430406279337}, {\"maladie\": \"Migraine\", \"probabilite\": 0.10197306079599404}, {\"maladie\": \"Salmonellose\", \"probabilite\": 0.06038013176992073}]', 0.392634, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"Globules Rouges\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Anémie hémolytique\", \"isSuggested\": true, \"unite_mesure\": \"M/µL\", \"valeur_numerique\": 4.5}, {\"nom\": \"Plaquettes\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Thrombocytopénie\", \"isSuggested\": true, \"unite_mesure\": \"K/µL\", \"valeur_numerique\": 250}, {\"nom\": \"Bilirubine totale\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Hémolyse\", \"isSuggested\": true, \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 10}, {\"nom\": \"ALT/SGPT\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Atteinte hépatique\", \"isSuggested\": true, \"unite_mesure\": \"U/L\", \"valeur_numerique\": 35}], \"symptomes\": [{\"nom\": \"Fièvre intermittente\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Frissons\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Sueurs\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Maux de tête sévère\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Douleurs musculaires\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Nausées\", \"severite\": \"Sévère\", \"duree_jours\": 5}, {\"nom\": \"Vomissements\", \"severite\": \"Sévère\", \"duree_jours\": 5}], \"signes_vitaux\": {\"poids\": 65, \"taille\": 170, \"temperature\": 40.5, \"saturation_o2\": 94, \"tension_systolique\": 100, \"frequence_cardiaque\": 115, \"tension_diastolique\": 62, \"frequence_respiratoire\": 22}}', NULL, '2026-05-28 01:20:39'),
(42, 129, 'RandomForest_v1.0_Preliminaire', 0.381703, '[{\"maladie\": \"Insuffisance rénale chronique\", \"probabilite\": 0.381702514389579}, {\"maladie\": \"Insuffisance rénale aiguë\", \"probabilite\": 0.3534282540644249}, {\"maladie\": \"Hépatite B\", \"probabilite\": 0.02888641835372491}]', 0.381703, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Fatigue\", \"severite\": \"Sévère\", \"duree_jours\": 180}, {\"nom\": \"Nausées\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Perte d\'appétit\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Gonflement des pieds\", \"severite\": \"Modérée\", \"duree_jours\": 120}, {\"nom\": \"Oligurie ou polyurie\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Prurit\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Démangeaisons\", \"severite\": \"Modérée\", \"duree_jours\": 90}], \"signes_vitaux\": {\"poids\": 80, \"taille\": 170, \"temperature\": 36.8, \"saturation_o2\": 96, \"tension_systolique\": 158, \"frequence_cardiaque\": 80, \"tension_diastolique\": 96, \"frequence_respiratoire\": 18}}', NULL, '2026-05-28 18:38:49'),
(43, 129, 'RandomForest_v1.0_Finale', 0.372395, '[{\"maladie\": \"Insuffisance rénale chronique\", \"probabilite\": 0.37239544850007394}, {\"maladie\": \"Insuffisance rénale aiguë\", \"probabilite\": 0.3706713954977588}, {\"maladie\": \"Hépatite B\", \"probabilite\": 0.023748800645971905}]', 0.372395, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"\", \"type\": \"BIOLOGIE\", \"resultats\": \"\"}], \"symptomes\": [{\"nom\": \"Fatigue\", \"severite\": \"Sévère\", \"duree_jours\": 180}, {\"nom\": \"Nausées\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Perte d\'appétit\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Gonflement des pieds\", \"severite\": \"Modérée\", \"duree_jours\": 120}, {\"nom\": \"Oligurie ou polyurie\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Prurit\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Démangeaisons\", \"severite\": \"Modérée\", \"duree_jours\": 90}], \"signes_vitaux\": {\"poids\": 80, \"taille\": 170, \"temperature\": 36.8, \"saturation_o2\": 96, \"tension_systolique\": 158, \"frequence_cardiaque\": 80, \"tension_diastolique\": 96, \"frequence_respiratoire\": 18}}', NULL, '2026-05-28 18:38:49'),
(44, 131, 'RandomForest_v1.0_Finale', 0.757081, '[{\"maladie\": \"Syndrome de Cushing\", \"probabilite\": 0.7570805610071193}, {\"maladie\": \"Acromégalie\", \"probabilite\": 0.09596878097632636}, {\"maladie\": \"Glomérulonéphrite\", \"probabilite\": 0.021151266282605424}]', 0.757081, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}]}', NULL, '2026-05-29 03:00:14'),
(45, 134, 'RandomForest_v1.0_Finale', 0.741167, '[{\"maladie\": \"Syndrome de Cushing\", \"probabilite\": 0.7411671283007506}, {\"maladie\": \"Acromégalie\", \"probabilite\": 0.0970216606798666}, {\"maladie\": \"Glomérulonéphrite\", \"probabilite\": 0.021553645640243677}]', 0.741167, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}]}', NULL, '2026-05-29 03:04:52'),
(46, 132, 'RandomForest_v1.0_Finale', 0.392634, '[{\"maladie\": \"Paludisme\", \"probabilite\": 0.39263430406279337}, {\"maladie\": \"Migraine\", \"probabilite\": 0.10197306079599404}, {\"maladie\": \"Salmonellose\", \"probabilite\": 0.06038013176992073}]', 0.392634, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"Globules Rouges\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Anémie hémolytique\", \"isSuggested\": true, \"unite_mesure\": \"M/µL\", \"valeur_numerique\": 4.5}, {\"nom\": \"Plaquettes\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Thrombocytopénie\", \"isSuggested\": true, \"unite_mesure\": \"K/µL\", \"valeur_numerique\": 250}, {\"nom\": \"Bilirubine totale\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Hémolyse\", \"isSuggested\": true, \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 10}, {\"nom\": \"ALT/SGPT\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-28\", \"description\": \"Atteinte hépatique\", \"isSuggested\": true, \"unite_mesure\": \"U/L\", \"valeur_numerique\": 35}]}', NULL, '2026-05-29 03:14:55'),
(47, 135, 'RandomForest_v1.0_Finale', 0.501712, '[{\"maladie\": \"Insuffisance rénale chronique\", \"probabilite\": 0.501712388103611}, {\"maladie\": \"Insuffisance rénale aiguë\", \"probabilite\": 0.4813041101577114}, {\"maladie\": \"Hépatite B\", \"probabilite\": 0.0016734366512378795}]', 0.501712, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"Créatinine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"unite_mesure\": \"µmol/L\", \"valeur_numerique\": 4.8}, {\"nom\": \"Urée\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 85}, {\"nom\": \"TFG\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"unite_mesure\": \"mL/min/1.73m²\", \"valeur_numerique\": 14}, {\"nom\": \"Potassium\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"unite_mesure\": \"mEq/L\", \"valeur_numerique\": 5.8}]}', NULL, '2026-05-29 08:59:39'),
(48, 136, 'RandomForest_v1.0_Preliminaire', 0.472788, '[{\"maladie\": \"Lithiase rénale\", \"probabilite\": 0.4727876577270203}, {\"maladie\": \"Migraine\", \"probabilite\": 0.0512429134179113}, {\"maladie\": \"Ulcère gastro-duodénal\", \"probabilite\": 0.04408469904941813}]', 0.472788, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Douleur lombaire\", \"severite\": \"Sévère\", \"duree_jours\": 2}, {\"nom\": \"Douleur colique intense\", \"severite\": \"Sévère\", \"duree_jours\": 2}, {\"nom\": \"Hématurie\", \"severite\": \"Modérée\", \"duree_jours\": 2}, {\"nom\": \"Nausées\", \"severite\": \"Modérée\", \"duree_jours\": 2}, {\"nom\": \"Vomissements\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Urination fréquente\", \"severite\": \"Légère\", \"duree_jours\": 2}], \"signes_vitaux\": {\"poids\": 80, \"taille\": 175, \"temperature\": 37.8, \"saturation_o2\": 98, \"tension_systolique\": 108, \"frequence_cardiaque\": 70, \"tension_diastolique\": 82, \"frequence_respiratoire\": 20}}', NULL, '2026-05-29 09:19:07'),
(49, 136, 'RandomForest_v1.0_Finale', 0.471104, '[{\"maladie\": \"Lithiase rénale\", \"probabilite\": 0.4711043571812232}, {\"maladie\": \"Migraine\", \"probabilite\": 0.047737380012017286}, {\"maladie\": \"Salmonellose\", \"probabilite\": 0.03902082042771041}]', 0.471104, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}, {\"nom\": \"Sodium\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Déshydratation\", \"isSuggested\": true, \"unite_mesure\": \"mEq/L\", \"valeur_numerique\": 140}, {\"nom\": \"Potassium\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Hypokaliémie\", \"isSuggested\": true, \"unite_mesure\": \"mEq/L\", \"valeur_numerique\": 4}, {\"nom\": \"Créatinine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Insuffisance rénale aiguë\", \"isSuggested\": true, \"unite_mesure\": \"µmol/L\", \"valeur_numerique\": 80}, {\"nom\": \"Urée\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Déshydratation\", \"isSuggested\": true, \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 30}, {\"nom\": \"Acide urique\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 9.2}, {\"nom\": \"Calcium\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"unite_mesure\": \"mg/dL\", \"valeur_numerique\": 11.2}, {\"nom\": \"Créatinine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"unite_mesure\": \"µmol/L\", \"valeur_numerique\": 1.3}], \"symptomes\": [{\"nom\": \"Douleur lombaire\", \"severite\": \"Sévère\", \"duree_jours\": 2}, {\"nom\": \"Douleur colique intense\", \"severite\": \"Sévère\", \"duree_jours\": 2}, {\"nom\": \"Hématurie\", \"severite\": \"Modérée\", \"duree_jours\": 2}, {\"nom\": \"Nausées\", \"severite\": \"Modérée\", \"duree_jours\": 2}, {\"nom\": \"Vomissements\", \"severite\": \"Modérée\", \"duree_jours\": 1}, {\"nom\": \"Urination fréquente\", \"severite\": \"Légère\", \"duree_jours\": 2}], \"signes_vitaux\": {\"poids\": 80, \"taille\": 175, \"temperature\": 37.8, \"saturation_o2\": 98, \"tension_systolique\": 108, \"frequence_cardiaque\": 70, \"tension_diastolique\": 82, \"frequence_respiratoire\": 20}}', NULL, '2026-05-29 09:19:07'),
(50, 133, 'RandomForest_v1.0_Finale', 0.627434, '[{\"maladie\": \"Épilepsie\", \"probabilite\": 0.627434094740523}, {\"maladie\": \"Alzheimer\", \"probabilite\": 0.04338343374649372}, {\"maladie\": \"Acné\", \"probabilite\": 0.014343481639457494}]', 0.627434, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-05-29\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}]}', NULL, '2026-05-29 16:28:46'),
(61, 146, 'RandomForest_v1.0_Preliminaire', 0.786109, '[{\"maladie\": \"Syndrome de Cushing\", \"probabilite\": 0.7861088745901751}, {\"maladie\": \"Acromégalie\", \"probabilite\": 0.05520976845452484}, {\"maladie\": \"Diabète Type 2\", \"probabilite\": 0.01148136344081303}]', 0.786109, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Prise de poids rapide\", \"severite\": \"Sévère\", \"duree_jours\": 180}, {\"nom\": \"Grossissement du visage\", \"severite\": \"Modérée\", \"duree_jours\": 120}, {\"nom\": \"Hypertension\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Vergetures\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Fatigue\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Infections fréquentes\", \"severite\": \"Légère\", \"duree_jours\": 90}], \"signes_vitaux\": {\"poids\": 90, \"taille\": 162, \"temperature\": 37, \"saturation_o2\": 97, \"tension_systolique\": 155, \"frequence_cardiaque\": 88, \"tension_diastolique\": 95, \"frequence_respiratoire\": 16}}', NULL, '2026-06-02 16:13:19'),
(62, 146, 'RandomForest_v1.0_Finale', 0.789934, '[{\"maladie\": \"Syndrome de Cushing\", \"probabilite\": 0.7899337799750235}, {\"maladie\": \"Acromégalie\", \"probabilite\": 0.05257138606127155}, {\"maladie\": \"Diabète Type 2\", \"probabilite\": 0.009952522468256586}]', 0.789934, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-06-02\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-06-02\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}], \"symptomes\": [{\"nom\": \"Prise de poids rapide\", \"severite\": \"Sévère\", \"duree_jours\": 180}, {\"nom\": \"Grossissement du visage\", \"severite\": \"Modérée\", \"duree_jours\": 120}, {\"nom\": \"Hypertension\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Vergetures\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Fatigue\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Infections fréquentes\", \"severite\": \"Légère\", \"duree_jours\": 90}], \"signes_vitaux\": {\"poids\": 90, \"taille\": 162, \"temperature\": 37, \"saturation_o2\": 97, \"tension_systolique\": 155, \"frequence_cardiaque\": 88, \"tension_diastolique\": 95, \"frequence_respiratoire\": 16}}', NULL, '2026-06-02 16:13:19'),
(63, 147, 'RandomForest_v1.0_Preliminaire', 0.786109, '[{\"maladie\": \"Syndrome de Cushing\", \"probabilite\": 0.7861088745901751}, {\"maladie\": \"Acromégalie\", \"probabilite\": 0.05520976845452484}, {\"maladie\": \"Diabète Type 2\", \"probabilite\": 0.01148136344081303}]', 0.786109, '{\"phase\": \"preliminaire\", \"symptomes\": [{\"nom\": \"Prise de poids rapide\", \"severite\": \"Sévère\", \"duree_jours\": 180}, {\"nom\": \"Grossissement du visage\", \"severite\": \"Modérée\", \"duree_jours\": 120}, {\"nom\": \"Hypertension\", \"severite\": \"Modérée\", \"duree_jours\": 120}, {\"nom\": \"Vergetures\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Fatigue\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Infections fréquentes\", \"severite\": \"Modérée\", \"duree_jours\": 90}], \"signes_vitaux\": {\"poids\": 90, \"taille\": 162, \"temperature\": 37, \"saturation_o2\": 97, \"tension_systolique\": 155, \"frequence_cardiaque\": 88, \"tension_diastolique\": 95, \"frequence_respiratoire\": 16}}', NULL, '2026-06-02 17:53:26'),
(64, 147, 'RandomForest_v1.0_Finale', 0.789934, '[{\"maladie\": \"Syndrome de Cushing\", \"probabilite\": 0.7899337799750235}, {\"maladie\": \"Acromégalie\", \"probabilite\": 0.052571386061271555}, {\"maladie\": \"Diabète Type 2\", \"probabilite\": 0.009952522468256588}]', 0.789934, '{\"phase\": \"finale\", \"examens\": [{\"nom\": \"Hémoglobine\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-06-02\", \"description\": \"Bilan sanguin de base\", \"isSuggested\": true, \"unite_mesure\": \"g/dL\", \"valeur_numerique\": 13}, {\"nom\": \"CRP\", \"type\": \"BIOLOGIE\", \"resultats\": \"\", \"date_examen\": \"2026-06-02\", \"description\": \"Marqueur inflammatoire\", \"isSuggested\": true, \"unite_mesure\": \"mg/L\", \"valeur_numerique\": 5}], \"symptomes\": [{\"nom\": \"Prise de poids rapide\", \"severite\": \"Sévère\", \"duree_jours\": 180}, {\"nom\": \"Grossissement du visage\", \"severite\": \"Modérée\", \"duree_jours\": 120}, {\"nom\": \"Hypertension\", \"severite\": \"Modérée\", \"duree_jours\": 120}, {\"nom\": \"Vergetures\", \"severite\": \"Modérée\", \"duree_jours\": 90}, {\"nom\": \"Fatigue\", \"severite\": \"Modérée\", \"duree_jours\": 180}, {\"nom\": \"Infections fréquentes\", \"severite\": \"Modérée\", \"duree_jours\": 90}], \"signes_vitaux\": {\"poids\": 90, \"taille\": 162, \"temperature\": 37, \"saturation_o2\": 97, \"tension_systolique\": 155, \"frequence_cardiaque\": 88, \"tension_diastolique\": 95, \"frequence_respiratoire\": 16}}', NULL, '2026-06-02 17:53:26');

-- --------------------------------------------------------

--
-- Structure de la table `catalogue_medicaments`
--

DROP TABLE IF EXISTS `catalogue_medicaments`;
CREATE TABLE IF NOT EXISTS `catalogue_medicaments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `maladie` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `nom_commercial` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `denomination_commune` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `dosage_standard` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `forme` enum('COMPRIME','INJECTION','SIROP','CREME','COLLYRE','POUDRE','PATCH','SPRAY','CAPSULE','SOLUTION') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'COMPRIME',
  `voie_administration` enum('ORALE','INTRAVEINEUSE','CUTANEE','INTRAMUSCULAIRE','OPHTALMIQUE','NASALE','INHALATION','SOUS-CUTANEE','RECTALE') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'ORALE',
  `frequence_habituelle` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `duree_standard_jours` int DEFAULT NULL,
  `categorie` enum('PREMIERE_INTENTION','DEUXIEME_INTENTION','ADJUVANT','SYMPTOMATIQUE') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'PREMIERE_INTENTION',
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `idx_maladie` (`maladie`)
) ENGINE=InnoDB AUTO_INCREMENT=426 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `catalogue_medicaments`
--

INSERT INTO `catalogue_medicaments` (`id`, `maladie`, `nom_commercial`, `denomination_commune`, `dosage_standard`, `forme`, `voie_administration`, `frequence_habituelle`, `duree_standard_jours`, `categorie`, `notes`) VALUES
(1, 'Accident vasculaire cérébral', 'Aspirine UPSA', 'Acide acétylsalicylique', '100 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Antiplaquettaire long terme'),
(2, 'Accident vasculaire cérébral', 'Actolyse', 'Alteplase (rtPA)', '0.9 mg/kg IV', 'INJECTION', 'INTRAVEINEUSE', 'En une seule prise', 1, 'PREMIERE_INTENTION', 'Thrombolyse — dans les 4h30 post-AVC ischémique'),
(3, 'Accident vasculaire cérébral', 'Plavix', 'Clopidogrel', '75 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'Association avec aspirine si nécessaire'),
(4, 'Accident vasculaire cérébral', 'Tahor', 'Atorvastatine', '40-80 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Réduction du risque de récidive'),
(5, 'Accident vasculaire cérébral', 'Lisinopril Mylan', 'Lisinopril', '5-10 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Contrôle tensionnel post-AVC'),
(6, 'Acné', 'Cutacnyl', 'Peroxyde de benzoyle', '5%', 'CREME', 'CUTANEE', '1×/jour', 90, 'PREMIERE_INTENTION', 'Appliquer sur peau propre le soir'),
(7, 'Acné', 'Vibramycine', 'Doxycycline', '100 mg', 'COMPRIME', 'ORALE', '1×/jour', 84, 'PREMIERE_INTENTION', 'Acné inflammatoire modérée à sévère'),
(8, 'Acné', 'Dalacin T', 'Clindamycine phosphate', '1%', 'SOLUTION', 'CUTANEE', '2×/jour', 90, 'ADJUVANT', 'Application locale, éviter les muqueuses'),
(9, 'Acné', 'Roaccutane', 'Isotrétinoïne', '0.5-1 mg/kg/j', 'CAPSULE', 'ORALE', '2×/jour', 180, 'DEUXIEME_INTENTION', 'Réservée aux formes sévères — surveillance hépatique'),
(10, 'Acné', 'Effederm', 'Trétinoïne', '0.025%', 'CREME', 'CUTANEE', '1×/soir', 90, 'ADJUVANT', 'Éviter le soleil — photosensibilisant'),
(11, 'Acromégalie', 'Sandostatine LAR', 'Octréotide LP', '20-30 mg IM/mois', 'INJECTION', 'INTRAMUSCULAIRE', '1×/mois', 365, 'PREMIERE_INTENTION', 'Analogue de la somatostatine'),
(12, 'Acromégalie', 'Somatuline Autogel', 'Lanréotide', '90-120 mg SC/4 sem', 'INJECTION', 'SOUS-CUTANEE', '1×/4 semaines', 365, 'PREMIERE_INTENTION', 'Alternative à l\'octréotide'),
(13, 'Acromégalie', 'Dostinex', 'Cabergoline', '0.5-3.5 mg/sem', 'COMPRIME', 'ORALE', '2×/semaine', 365, 'DEUXIEME_INTENTION', 'Agoniste dopaminergique'),
(14, 'Acromégalie', 'Somavert', 'Pégvisomant', '10-30 mg/j SC', 'INJECTION', 'SOUS-CUTANEE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'Antagoniste du récepteur GH — si autres traitements insuffisants'),
(15, 'Alzheimer', 'Aricept', 'Donépézil', '5-10 mg', 'COMPRIME', 'ORALE', '1×/soir', 365, 'PREMIERE_INTENTION', 'Inhibiteur de cholinestérase'),
(16, 'Alzheimer', 'Exelon', 'Rivastigmine', '4.6-9.5 mg/24h', 'PATCH', 'CUTANEE', '1 patch/jour', 365, 'PREMIERE_INTENTION', 'Patch transcutané ou capsule orale'),
(17, 'Alzheimer', 'Reminyl', 'Galantamine', '8-24 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', 'Inhibiteur de cholinestérase'),
(18, 'Alzheimer', 'Ebixa', 'Mémantine', '5-20 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'Antagoniste NMDA — stades modérés à sévères'),
(19, 'Angine de poitrine', 'Nitroquick', 'Nitroglycérine sublinguale', '0.4 mg', 'COMPRIME', 'ORALE', 'Au besoin', NULL, 'PREMIERE_INTENTION', 'Crise angineuse aiguë — max 3 prises / 15 min'),
(20, 'Angine de poitrine', 'Lopressor', 'Métoprolol', '25-100 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', 'Bêtabloquant anti-angineux'),
(21, 'Angine de poitrine', 'Aspirine UPSA', 'Acide acétylsalicylique', '75-100 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Antiplaquettaire de fond'),
(22, 'Angine de poitrine', 'Tahor', 'Atorvastatine', '40 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Réduction du LDL'),
(23, 'Angine de poitrine', 'Adalate LP', 'Nifédipine LP', '30-60 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'Inhibiteur calcique si bêtabloquant contre-indiqué'),
(24, 'Angine streptococcique', 'Clamoxyl', 'Amoxicilline', '500 mg', 'COMPRIME', 'ORALE', '3×/jour', 6, 'PREMIERE_INTENTION', 'Traitement de référence des angines streptococciques'),
(25, 'Angine streptococcique', 'Pénicilline V', 'Phénoxyméthylpénicilline', '1 M UI', 'COMPRIME', 'ORALE', '3×/jour', 10, 'PREMIERE_INTENTION', 'Alternative à l\'amoxicilline'),
(26, 'Angine streptococcique', 'Zithromax', 'Azithromycine', '500 mg J1 puis 250 mg', 'COMPRIME', 'ORALE', '1×/jour', 5, 'DEUXIEME_INTENTION', 'Si allergie à la pénicilline'),
(27, 'Angine streptococcique', 'Paracétamol EG', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '3×/jour', 6, 'SYMPTOMATIQUE', 'Antalgique et antipyrétique'),
(28, 'Anémie aplasique', 'Néoral', 'Ciclosporine', '3-6 mg/kg/j', 'CAPSULE', 'ORALE', '2×/jour', 180, 'PREMIERE_INTENTION', 'Immunosuppresseur — surveillance rénale'),
(29, 'Anémie aplasique', 'Thymoglobuline', 'Globuline antithymocyte', '2.5-3.75 mg/kg/j', 'INJECTION', 'INTRAVEINEUSE', '1×/jour', 5, 'PREMIERE_INTENTION', 'Immunosuppression intensive'),
(30, 'Anémie aplasique', 'Revolade', 'Eltrombopag', '50-150 mg', 'COMPRIME', 'ORALE', '1×/jour', 180, 'ADJUVANT', 'Stimulant de la thrombopoïèse'),
(31, 'Anémie aplasique', 'Neorecormon', 'Érythropoïétine (EPO)', '2000-4000 UI', 'INJECTION', 'SOUS-CUTANEE', '3×/semaine', 90, 'ADJUVANT', 'Stimulation érythropoïèse'),
(32, 'Anémie ferriprive', 'Ferrograd', 'Sulfate ferreux', '325 mg', 'COMPRIME', 'ORALE', '1×/jour', 90, 'PREMIERE_INTENTION', 'Prendre à jeun ou avec jus d\'orange'),
(33, 'Anémie ferriprive', 'Tardyferon', 'Sulfate ferreux LP', '80 mg (élément Fe)', 'COMPRIME', 'ORALE', '1-2×/jour', 90, 'PREMIERE_INTENTION', 'Libération prolongée — meilleure tolérance digestive'),
(34, 'Anémie ferriprive', 'Venofer', 'Fer saccharose IV', '200 mg', 'INJECTION', 'INTRAVEINEUSE', '1×/semaine', 4, 'DEUXIEME_INTENTION', 'Si intolérance orale ou malabsorption'),
(35, 'Anémie ferriprive', 'Acide folique Mylan', 'Acide folique', '5 mg', 'COMPRIME', 'ORALE', '1×/jour', 90, 'ADJUVANT', 'Supplément en acide folique'),
(36, 'Anémie hemolytique', 'Solupred', 'Prednisolone', '1 mg/kg/j', 'COMPRIME', 'ORALE', '1×/matin', 30, 'PREMIERE_INTENTION', 'Anémie hémolytique auto-immune'),
(37, 'Anémie hemolytique', 'Acide folique Mylan', 'Acide folique', '5 mg', 'COMPRIME', 'ORALE', '1×/jour', 90, 'ADJUVANT', 'Prévention de la carence en folates'),
(38, 'Anémie hemolytique', 'Mabthera', 'Rituximab', '375 mg/m²', 'INJECTION', 'INTRAVEINEUSE', '1×/semaine', 28, 'DEUXIEME_INTENTION', 'Formes réfractaires aux corticoïdes'),
(39, 'Apnée du sommeil', 'Modiodal', 'Modafinil', '100-200 mg', 'COMPRIME', 'ORALE', '1×/matin', 365, 'SYMPTOMATIQUE', 'Somnolence diurne résiduelle — pas un traitement curatif'),
(40, 'Apnée du sommeil', 'Fluticasone Mylan', 'Fluticasone nasale', '50 µg/pulv.', 'SPRAY', 'NASALE', '2×/jour', 30, 'ADJUVANT', 'Si rhinite associée aggravant l\'apnée'),
(41, 'Arthrite rhumatoïde', 'Novatrex', 'Méthotrexate', '7.5-25 mg/sem', 'COMPRIME', 'ORALE', '1×/semaine', 365, 'PREMIERE_INTENTION', 'DMARDs de référence — supplémentation folates nécessaire'),
(42, 'Arthrite rhumatoïde', 'Plaquenil', 'Hydroxychloroquine', '200-400 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Surveillance ophtalmologique annuelle'),
(43, 'Arthrite rhumatoïde', 'Solupred', 'Prednisolone', '5-10 mg', 'COMPRIME', 'ORALE', '1×/matin', 30, 'ADJUVANT', 'Traitement de courte durée en poussée'),
(44, 'Arthrite rhumatoïde', 'Remicade', 'Infliximab', '3-5 mg/kg', 'INJECTION', 'INTRAVEINEUSE', 'S0, S2, S6 puis /8 sem', 365, 'DEUXIEME_INTENTION', 'Anti-TNFα — bilan pré-thérapeutique requis'),
(45, 'Arthrite rhumatoïde', 'Arava', 'Léflunomide', '20 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'Alternative au méthotrexate'),
(46, 'Arythmie cardiaque', 'Cordarone', 'Amiodarone', '200 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Surveillance thyroïdienne et pulmonaire'),
(47, 'Arythmie cardiaque', 'Digoxine Nativelle', 'Digoxine', '0.125-0.25 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Contrôle de la fréquence en FA'),
(48, 'Arythmie cardiaque', 'Lopressor', 'Métoprolol', '25-100 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'ADJUVANT', 'Ralentisseur de fréquence'),
(49, 'Arythmie cardiaque', 'Xarelto', 'Rivaroxaban', '20 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Anticoagulation en cas de FA'),
(50, 'Asthme', 'Ventoline', 'Salbutamol', '100 µg/bouffée', 'SPRAY', 'INHALATION', 'Au besoin (max 6×/j)', NULL, 'PREMIERE_INTENTION', 'Bronchodilatateur d\'action rapide — crise aiguë'),
(51, 'Asthme', 'Flixotide', 'Fluticasone', '125-250 µg', 'SPRAY', 'INHALATION', '2×/jour', 365, 'PREMIERE_INTENTION', 'Corticoïde inhalé de fond'),
(52, 'Asthme', 'Atrovent', 'Ipratropium', '20 µg/bouffée', 'SPRAY', 'INHALATION', '3-4×/jour', 14, 'ADJUVANT', 'Anticholinergique — exacerbations sévères'),
(53, 'Asthme', 'Singulair', 'Montélukast', '10 mg', 'COMPRIME', 'ORALE', '1×/soir', 365, 'DEUXIEME_INTENTION', 'Antagoniste des leucotriènes'),
(54, 'Asthme', 'Solupred', 'Prednisolone', '40-60 mg', 'COMPRIME', 'ORALE', '1×/matin', 5, 'SYMPTOMATIQUE', 'Exacerbation aiguë sévère'),
(55, 'Astigmatisme', 'Artane', 'Larmes artificielles', '1 goutte', 'COLLYRE', 'OPHTALMIQUE', '3-4×/jour', 30, 'SYMPTOMATIQUE', 'Soulagement de la sécheresse oculaire associée'),
(56, 'Athérosclérose', 'Tahor', 'Atorvastatine', '40-80 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Réduction LDL < 0.7 g/L'),
(57, 'Athérosclérose', 'Aspirine UPSA', 'Acide acétylsalicylique', '75-100 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Antiplaquettaire de prévention secondaire'),
(58, 'Athérosclérose', 'Amlor', 'Amlodipine', '5-10 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Inhibiteur calcique antihypertenseur'),
(59, 'Athérosclérose', 'Triatec', 'Ramipril', '5-10 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'IEC cardioprotecteur'),
(60, 'BPCO', 'Spiriva', 'Tiotropium', '18 µg', 'CAPSULE', 'INHALATION', '1×/jour', 365, 'PREMIERE_INTENTION', 'Bronchodilatateur anticholinergique de longue durée'),
(61, 'BPCO', 'Ventoline', 'Salbutamol', '100 µg/bouffée', 'SPRAY', 'INHALATION', 'Au besoin', NULL, 'PREMIERE_INTENTION', 'Bronchodilatateur de secours'),
(62, 'BPCO', 'Seretide', 'Fluticasone/Salmétérol', '500/50 µg', 'SPRAY', 'INHALATION', '2×/jour', 365, 'DEUXIEME_INTENTION', 'Corticoïde + LABA en cas d\'exacerbations fréquentes'),
(63, 'BPCO', 'Solupred', 'Prednisolone', '40 mg', 'COMPRIME', 'ORALE', '1×/matin', 5, 'SYMPTOMATIQUE', 'Exacerbation aiguë'),
(64, 'BPCO', 'Augmentin', 'Amoxicilline-clavulanate', '1 g', 'COMPRIME', 'ORALE', '3×/jour', 7, 'ADJUVANT', 'Exacerbation infectieuse'),
(65, 'Bronchite', 'Clamoxyl', 'Amoxicilline', '500 mg', 'COMPRIME', 'ORALE', '3×/jour', 7, 'PREMIERE_INTENTION', 'Bronchite bactérienne — souvent virale donc antibiothérapie prudente'),
(66, 'Bronchite', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '3×/jour', 7, 'SYMPTOMATIQUE', 'Fièvre et douleurs'),
(67, 'Bronchite', 'Bisolvon', 'Bromhexine', '8 mg', 'COMPRIME', 'ORALE', '3×/jour', 7, 'SYMPTOMATIQUE', 'Mucolytique — fluidifie les sécrétions'),
(68, 'Bronchite', 'Drill', 'Dextrométhorphane', '15 mg', 'SIROP', 'ORALE', '3×/jour', 5, 'SYMPTOMATIQUE', 'Antitussif — bronchite sèche seulement'),
(69, 'COVID-19', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '3×/jour', 10, 'PREMIERE_INTENTION', 'Fièvre et douleurs — éviter AINS'),
(70, 'COVID-19', 'Decadron', 'Dexaméthasone', '6 mg', 'COMPRIME', 'ORALE', '1×/jour', 10, 'PREMIERE_INTENTION', 'Formes sévères nécessitant O2 — réduction mortalité'),
(71, 'COVID-19', 'Veklury', 'Remdesivir', '200 mg J1 puis 100 mg', 'INJECTION', 'INTRAVEINEUSE', '1×/jour', 5, 'DEUXIEME_INTENTION', 'Formes hospitalisées avec O2'),
(72, 'COVID-19', 'Xarelto', 'Rivaroxaban', '10 mg', 'COMPRIME', 'ORALE', '1×/jour', 30, 'ADJUVANT', 'Anticoagulation préventive — risque thrombotique élevé'),
(73, 'COVID-19', 'Kaletra', 'Lopinavir/Ritonavir', '400/100 mg', 'COMPRIME', 'ORALE', '2×/jour', 14, 'DEUXIEME_INTENTION', 'Cas sévères selon protocole'),
(74, 'Cataracte', 'Indocollyre', 'Indométacine collyre', '0.1%', 'COLLYRE', 'OPHTALMIQUE', '3×/jour', 14, 'SYMPTOMATIQUE', 'Anti-inflammatoire post-opératoire'),
(75, 'Cataracte', 'Tobradex', 'Tobramycine + Dexaméthasone', '1 goutte', 'COLLYRE', 'OPHTALMIQUE', '4×/jour', 14, 'ADJUVANT', 'Prévention infection + inflammation post-op'),
(76, 'Chlamydia', 'Zithromax', 'Azithromycine', '1 g', 'COMPRIME', 'ORALE', 'En une seule prise', 1, 'PREMIERE_INTENTION', 'Dose unique — traiter le partenaire'),
(77, 'Chlamydia', 'Vibramycine', 'Doxycycline', '100 mg', 'COMPRIME', 'ORALE', '2×/jour', 7, 'PREMIERE_INTENTION', 'Alternative à l\'azithromycine'),
(78, 'Chlamydia', 'Erythrocine', 'Érythromycine', '500 mg', 'COMPRIME', 'ORALE', '4×/jour', 7, 'DEUXIEME_INTENTION', 'Si grossesse — éviter doxycycline'),
(79, 'Cholangite', 'Augmentin', 'Amoxicilline-clavulanate', '1 g', 'COMPRIME', 'ORALE', '3×/jour', 7, 'PREMIERE_INTENTION', 'Cholangite légère à modérée'),
(80, 'Cholangite', 'Ciflox', 'Ciprofloxacine', '400 mg IV', 'INJECTION', 'INTRAVEINEUSE', '2×/jour', 7, 'PREMIERE_INTENTION', 'Formes sévères — IV d\'abord'),
(81, 'Cholangite', 'Flagyl', 'Métronidazole', '500 mg', 'COMPRIME', 'ORALE', '3×/jour', 7, 'ADJUVANT', 'Couverture anaérobies'),
(82, 'Cholangite', 'Ursofalk', 'Acide ursodéoxycholique', '13-15 mg/kg/j', 'COMPRIME', 'ORALE', '2×/jour', 365, 'ADJUVANT', 'Lithiase biliaire associée'),
(83, 'Cholécystite', 'Augmentin', 'Amoxicilline-clavulanate', '1 g', 'COMPRIME', 'ORALE', '3×/jour', 7, 'PREMIERE_INTENTION', 'Couverture bactérienne large'),
(84, 'Cholécystite', 'Kétodolac', 'Kétorolac', '30 mg IV', 'INJECTION', 'INTRAVEINEUSE', '4×/jour', 2, 'SYMPTOMATIQUE', 'Antalgique AINS en crise aiguë'),
(85, 'Cholécystite', 'Flagyl', 'Métronidazole', '500 mg', 'INJECTION', 'INTRAVEINEUSE', '3×/jour', 5, 'ADJUVANT', 'Couverture anaérobies'),
(86, 'Cholécystite', 'Spasfon', 'Phloroglucinol', '80 mg', 'COMPRIME', 'ORALE', '3×/jour', 5, 'SYMPTOMATIQUE', 'Antispasmodique — colique biliaire'),
(87, 'Cirrhose', 'Aldactone', 'Spironolactone', '100-400 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Diurétique antialdostérone — ascite'),
(88, 'Cirrhose', 'Lasilix', 'Furosémide', '40-80 mg', 'COMPRIME', 'ORALE', '1×/matin', 365, 'PREMIERE_INTENTION', 'Diurétique de l\'anse — ascite'),
(89, 'Cirrhose', 'Duphalac', 'Lactulose', '15-30 mL', 'SIROP', 'ORALE', '3×/jour', 365, 'PREMIERE_INTENTION', 'Prévention encéphalopathie hépatique'),
(90, 'Cirrhose', 'Avlocardyl', 'Propranolol', '20-40 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'ADJUVANT', 'Prévention rupture de varices œsophagiennes'),
(91, 'Cirrhose', 'Vitamine K1', 'Phytoménadione', '10 mg', 'COMPRIME', 'ORALE', '1×/jour', 30, 'ADJUVANT', 'Troubles de coagulation hépatiques'),
(92, 'Colite ulcéreuse', 'Pentasa', 'Mésalazine', '2-4 g', 'COMPRIME', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', '5-ASA — entretien et poussée légère'),
(93, 'Colite ulcéreuse', 'Solupred', 'Prednisolone', '40-60 mg', 'COMPRIME', 'ORALE', '1×/matin', 30, 'PREMIERE_INTENTION', 'Poussée modérée à sévère'),
(94, 'Colite ulcéreuse', 'Imurel', 'Azathioprine', '2-2.5 mg/kg/j', 'COMPRIME', 'ORALE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'Maintien de rémission — délai 3 mois'),
(95, 'Colite ulcéreuse', 'Remicade', 'Infliximab', '5 mg/kg', 'INJECTION', 'INTRAVEINEUSE', 'S0, S2, S6 puis /8 sem', 365, 'DEUXIEME_INTENTION', 'Formes sévères corticorésistantes'),
(96, 'Condylomes', 'Aldara', 'Imiquimod', '5%', 'CREME', 'CUTANEE', '3×/semaine', 84, 'PREMIERE_INTENTION', 'Appliquer la nuit — rincer après 6-10 h'),
(97, 'Condylomes', 'Wartec', 'Podophyllotoxine', '0.5%', 'SOLUTION', 'CUTANEE', '2×/jour', 3, 'PREMIERE_INTENTION', '3 jours puis 4 jours de repos — max 4 cycles'),
(98, 'Condylomes', 'Interféron alpha', 'Interféron alpha-2b', '1 M UI', 'INJECTION', 'INTRAMUSCULAIRE', '3×/semaine', 28, 'DEUXIEME_INTENTION', 'Formes récidivantes'),
(99, 'Conjonctivite', 'Tobrex', 'Tobramycine', '0.3%', 'COLLYRE', 'OPHTALMIQUE', '4×/jour', 7, 'PREMIERE_INTENTION', 'Conjonctivite bactérienne'),
(100, 'Conjonctivite', 'Zovirax', 'Aciclovir gel ophtalmique', '3%', 'COLLYRE', 'OPHTALMIQUE', '5×/jour', 14, 'PREMIERE_INTENTION', 'Conjonctivite herpétique'),
(101, 'Conjonctivite', 'Zaditen', 'Kétotifène', '0.025%', 'COLLYRE', 'OPHTALMIQUE', '2×/jour', 14, 'SYMPTOMATIQUE', 'Conjonctivite allergique'),
(102, 'Conjonctivite', 'Naphazoline', 'Naphazoline + phéniramine', '1 goutte', 'COLLYRE', 'OPHTALMIQUE', '3×/jour', 5, 'SYMPTOMATIQUE', 'Rougeur et démangeaisons'),
(103, 'Constipation chronique', 'Duphalac', 'Lactulose', '15 mL', 'SIROP', 'ORALE', '2×/jour', 30, 'PREMIERE_INTENTION', 'Laxatif osmotique — selles molles'),
(104, 'Constipation chronique', 'Psyllium Blond', 'Psyllium', '5 g', 'POUDRE', 'ORALE', '2×/jour', 30, 'PREMIERE_INTENTION', 'Fibres solubles — boire beaucoup d\'eau'),
(105, 'Constipation chronique', 'Forlax', 'Macrogol (PEG) 4000', '10 g', 'POUDRE', 'ORALE', '2×/jour', 30, 'PREMIERE_INTENTION', 'Osmotique — bon profil de tolérance'),
(106, 'Constipation chronique', 'Dulcolax', 'Bisacodyl', '5-10 mg', 'COMPRIME', 'ORALE', '1×/soir', 5, 'DEUXIEME_INTENTION', 'Stimulant — usage ponctuel uniquement'),
(107, 'Crohn', 'Pentasa', 'Mésalazine', '3-4 g', 'COMPRIME', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', 'Formes légères à modérées'),
(108, 'Crohn', 'Flagyl', 'Métronidazole', '500 mg', 'COMPRIME', 'ORALE', '3×/jour', 14, 'PREMIERE_INTENTION', 'Complications septiques ou fistulisantes'),
(109, 'Crohn', 'Imurel', 'Azathioprine', '2-2.5 mg/kg/j', 'COMPRIME', 'ORALE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'Entretien de rémission'),
(110, 'Crohn', 'Humira', 'Adalimumab', '160 mg J1, 80 mg J15, puis 40 mg/2 sem', 'INJECTION', 'SOUS-CUTANEE', '1×/2 semaines', 365, 'DEUXIEME_INTENTION', 'Formes modérées à sévères — anti-TNFα'),
(111, 'Cystite', 'Furadantine', 'Nitrofurantoïne', '100 mg LP', 'CAPSULE', 'ORALE', '2×/jour', 5, 'PREMIERE_INTENTION', 'Cystite non compliquée de la femme'),
(112, 'Cystite', 'Monoflocet', 'Fosfomycine trométamol', '3 g', 'POUDRE', 'ORALE', 'Dose unique', 1, 'PREMIERE_INTENTION', 'Traitement minute — excellente observance'),
(113, 'Cystite', 'Triméthoprime', 'Triméthoprime', '200 mg', 'COMPRIME', 'ORALE', '2×/jour', 7, 'DEUXIEME_INTENTION', 'Selon antibiogramme'),
(114, 'Cystite', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '3×/jour', 3, 'SYMPTOMATIQUE', 'Antalgique — brûlures mictionnelles'),
(115, 'Céphalée de tension', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '3×/jour', 3, 'PREMIERE_INTENTION', 'Traitement de la crise'),
(116, 'Céphalée de tension', 'Ibuprofène EG', 'Ibuprofène', '400 mg', 'COMPRIME', 'ORALE', '3×/jour', 3, 'PREMIERE_INTENTION', 'AINS — si paracétamol insuffisant'),
(117, 'Céphalée de tension', 'Laroxyl', 'Amitriptyline', '10-75 mg', 'COMPRIME', 'ORALE', '1×/soir', 90, 'DEUXIEME_INTENTION', 'Prévention formes chroniques'),
(118, 'Dengue', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '4×/jour', 7, 'PREMIERE_INTENTION', 'Seul antalgique autorisé — AINS contre-indiqués'),
(119, 'Dengue', 'SRO OMS', 'Sels de réhydratation orale', '1 sachet/L d\'eau', 'POUDRE', 'ORALE', 'Selon besoin', 7, 'ADJUVANT', 'Maintien de l\'hydratation'),
(120, 'Dermatite atopique', 'Hydrocortisone Bailleul', 'Hydrocortisone 1%', 'Fine couche', 'CREME', 'CUTANEE', '2×/jour', 14, 'PREMIERE_INTENTION', 'Corticoïde faible pour le visage et plis'),
(121, 'Dermatite atopique', 'Protopic', 'Tacrolimus 0.1%', 'Fine couche', 'CREME', 'CUTANEE', '2×/jour', 30, 'DEUXIEME_INTENTION', 'Zones sensibles — visage et cou'),
(122, 'Dermatite atopique', 'Zyrtec', 'Cétirizine', '10 mg', 'COMPRIME', 'ORALE', '1×/soir', 30, 'SYMPTOMATIQUE', 'Antihistaminique — prurit'),
(123, 'Dermatite atopique', 'Dupixent', 'Dupilumab', '300 mg', 'INJECTION', 'SOUS-CUTANEE', '1×/2 semaines', 365, 'DEUXIEME_INTENTION', 'Formes modérées à sévères réfractaires'),
(124, 'Diabète Type 1', 'Novorapid', 'Insuline asparte (rapide)', 'Selon glycémie', 'INJECTION', 'SOUS-CUTANEE', '3×/jour (avant repas)', 365, 'PREMIERE_INTENTION', 'Insuline rapide — adapter selon glycémie'),
(125, 'Diabète Type 1', 'Lantus', 'Insuline glargine (lente)', 'Selon besoins', 'INJECTION', 'SOUS-CUTANEE', '1×/soir', 365, 'PREMIERE_INTENTION', 'Insuline basale — injection au coucher'),
(126, 'Diabète Type 1', 'Glucagon GlucaGen', 'Glucagon', '1 mg', 'INJECTION', 'SOUS-CUTANEE', '1 injection si hypoglycémie sévère', NULL, 'ADJUVANT', 'Traitement de l\'hypoglycémie sévère'),
(127, 'Diabète Type 2', 'Glucophage', 'Metformine', '500-1000 mg', 'COMPRIME', 'ORALE', '2-3×/jour', 365, 'PREMIERE_INTENTION', 'Première intention — si tolérance digestive bonne'),
(128, 'Diabète Type 2', 'Daonil', 'Glibenclamide', '2.5-5 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'Sulfamide hypoglycémiant'),
(129, 'Diabète Type 2', 'Januvia', 'Sitagliptine', '100 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'Inhibiteur DPP-4'),
(130, 'Diabète Type 2', 'Jardiance', 'Empagliflozine', '10-25 mg', 'COMPRIME', 'ORALE', '1×/matin', 365, 'DEUXIEME_INTENTION', 'Inhibiteur SGLT2 — protection cardiovasculaire'),
(131, 'Diabète Type 2', 'Victoza', 'Liraglutide', '0.6-1.8 mg', 'INJECTION', 'SOUS-CUTANEE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'Agoniste GLP-1 — perte de poids'),
(132, 'Diabète gestationnel', 'Actrapid', 'Insuline humaine rapide', 'Selon glycémie', 'INJECTION', 'SOUS-CUTANEE', '3×/jour', 270, 'PREMIERE_INTENTION', 'Si régime insuffisant — surveillance glycémique rapprochée'),
(133, 'Diabète gestationnel', 'Glucophage', 'Metformine', '500 mg', 'COMPRIME', 'ORALE', '2×/jour', 180, 'DEUXIEME_INTENTION', 'Selon avis obstétrical — non recommandé systématiquement'),
(134, 'Dégénérescence maculaire', 'Lucentis', 'Ranibizumab', '0.5 mg', 'INJECTION', 'OPHTALMIQUE', '1×/mois (3 mois puis PRN)', 365, 'PREMIERE_INTENTION', 'DMLA néovasculaire — injection intravitréenne'),
(135, 'Dégénérescence maculaire', 'Avastin', 'Bévacizumab', '1.25 mg', 'INJECTION', 'OPHTALMIQUE', '1×/mois', 365, 'DEUXIEME_INTENTION', 'Anti-VEGF — usage hors AMM mais efficace'),
(136, 'Dégénérescence maculaire', 'AREDS2 Vitamine', 'Zinc + Vitamine C/E', '1 comprimé', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Formes intermédiaires — ralentissement progression'),
(137, 'Eczéma', 'Dermoval', 'Clobétasol propionate 0.05%', 'Fine couche', 'CREME', 'CUTANEE', '1×/jour', 14, 'PREMIERE_INTENTION', 'Corticoïde fort — usage court'),
(138, 'Eczéma', 'Hydracort', 'Hydrocortisone 1%', 'Fine couche', 'CREME', 'CUTANEE', '2×/jour', 14, 'PREMIERE_INTENTION', 'Corticoïde faible pour visage'),
(139, 'Eczéma', 'Topicrem', 'Émollient dermatologique', 'Généreusement', 'CREME', 'CUTANEE', '2×/jour', 365, 'ADJUVANT', 'Hydratation quotidienne — prévention rechutes'),
(140, 'Eczéma', 'Zyrtec', 'Cétirizine', '10 mg', 'COMPRIME', 'ORALE', '1×/soir', 30, 'SYMPTOMATIQUE', 'Prurit — antihistaminique'),
(141, 'Embolie pulmonaire', 'Xarelto', 'Rivaroxaban', '15 mg (21 j) puis 20 mg', 'COMPRIME', 'ORALE', '2×/jour puis 1×/jour', 90, 'PREMIERE_INTENTION', 'Anticoagulant oral direct — Embolie pulmonaire'),
(142, 'Embolie pulmonaire', 'Eliquis', 'Apixaban', '10 mg (7 j) puis 5 mg', 'COMPRIME', 'ORALE', '2×/jour', 90, 'PREMIERE_INTENTION', 'Anticoagulant oral direct — alternative'),
(143, 'Embolie pulmonaire', 'Fragmine', 'Daltéparine', '200 UI/kg/j', 'INJECTION', 'SOUS-CUTANEE', '1×/jour', 10, 'PREMIERE_INTENTION', 'Héparinothérapie initiale'),
(144, 'Embolie pulmonaire', 'Actolyse', 'Alteplase', '100 mg IV', 'INJECTION', 'INTRAVEINEUSE', 'En 2 heures', 1, 'DEUXIEME_INTENTION', 'Thrombolyse systémique — EP massive'),
(145, 'Emphysème', 'Spiriva', 'Tiotropium', '18 µg', 'CAPSULE', 'INHALATION', '1×/jour', 365, 'PREMIERE_INTENTION', 'Bronchodilatateur anticholinergique'),
(146, 'Emphysème', 'Ventoline', 'Salbutamol', '100 µg', 'SPRAY', 'INHALATION', 'Au besoin', NULL, 'PREMIERE_INTENTION', 'Bronchodilatateur de secours'),
(147, 'Emphysème', 'Théophylline LP', 'Théophylline', '200-400 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'DEUXIEME_INTENTION', 'Bronchodilatateur oral — taux sérique à surveiller'),
(148, 'Fibromyalgie', 'Cymbalta', 'Duloxétine', '30-60 mg', 'CAPSULE', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Antidépresseur IRSN — douleurs neuropathiques'),
(149, 'Fibromyalgie', 'Lyrica', 'Prégabaline', '75-300 mg', 'CAPSULE', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', 'Douleurs neuropathiques — fibromyalgie'),
(150, 'Fibromyalgie', 'Laroxyl', 'Amitriptyline', '10-50 mg', 'COMPRIME', 'ORALE', '1×/soir', 365, 'ADJUVANT', 'Troubles du sommeil et douleurs'),
(151, 'Fibromyalgie', 'Tramadol EG', 'Tramadol', '50-100 mg', 'COMPRIME', 'ORALE', '3×/jour', 30, 'SYMPTOMATIQUE', 'Antalgique palier 2 — usage limité'),
(152, 'Gastrite', 'Mopral', 'Oméprazole', '20-40 mg', 'CAPSULE', 'ORALE', '1×/jour', 28, 'PREMIERE_INTENTION', 'IPP — à jeun le matin'),
(153, 'Gastrite', 'Clamoxyl', 'Amoxicilline', '1 g', 'COMPRIME', 'ORALE', '2×/jour', 14, 'ADJUVANT', 'Éradication H. pylori — triple thérapie'),
(154, 'Gastrite', 'Zéclar', 'Clarithromycine', '500 mg', 'COMPRIME', 'ORALE', '2×/jour', 14, 'ADJUVANT', 'Éradication H. pylori — triple thérapie'),
(155, 'Gastrite', 'Ulcar', 'Sucralfate', '1 g', 'COMPRIME', 'ORALE', '4×/jour', 28, 'ADJUVANT', 'Gastroprotection — prendre à jeun'),
(156, 'Gastroentérite', 'SRO OMS', 'Sels de réhydratation orale', '1 sachet/250 mL', 'POUDRE', 'ORALE', 'Selon soif', 5, 'PREMIERE_INTENTION', 'Réhydratation — priorité absolue'),
(157, 'Gastroentérite', 'Imodium', 'Lopéramide', '2 mg', 'COMPRIME', 'ORALE', 'Après chaque selle liquide (max 8/j)', 3, 'SYMPTOMATIQUE', 'Antidiarrhéique — CI si fièvre élevée ou sang dans selles'),
(158, 'Gastroentérite', 'Smecta', 'Diosmectite', '3 g', 'POUDRE', 'ORALE', '3×/jour', 5, 'ADJUVANT', 'Pansement intestinal — selles et nausées'),
(159, 'Gastroentérite', 'Primpéran', 'Métoclopramide', '10 mg', 'COMPRIME', 'ORALE', '3×/jour', 3, 'SYMPTOMATIQUE', 'Antiémétique'),
(160, 'Glaucome', 'Timoptol', 'Timolol 0.5%', '1 goutte', 'COLLYRE', 'OPHTALMIQUE', '2×/jour', 365, 'PREMIERE_INTENTION', 'Bêtabloquant collyre — baisse de la PIO'),
(161, 'Glaucome', 'Xalatan', 'Latanoprost 0.005%', '1 goutte', 'COLLYRE', 'OPHTALMIQUE', '1×/soir', 365, 'PREMIERE_INTENTION', 'Analogue des prostaglandines — très efficace'),
(162, 'Glaucome', 'Alphagan', 'Brimonidine 0.2%', '1 goutte', 'COLLYRE', 'OPHTALMIQUE', '2×/jour', 365, 'DEUXIEME_INTENTION', 'Agoniste alpha-2 — si bêtabloquant CI'),
(163, 'Glaucome', 'Diamox', 'Acétazolamide', '250 mg', 'COMPRIME', 'ORALE', '4×/jour', 7, 'ADJUVANT', 'Crise aiguë de glaucome — urgence'),
(164, 'Glomérulonéphrite', 'Solupred', 'Prednisolone', '1 mg/kg/j', 'COMPRIME', 'ORALE', '1×/matin', 60, 'PREMIERE_INTENTION', 'Immunosuppression initiale'),
(165, 'Glomérulonéphrite', 'Cyclophosphamide Endoxan', 'Cyclophosphamide', '2 mg/kg/j', 'COMPRIME', 'ORALE', '1×/jour', 90, 'DEUXIEME_INTENTION', 'Formes prolifératives sévères'),
(166, 'Glomérulonéphrite', 'Cobalt Inhibace', 'Cilazapril', '2.5-5 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'IEC — protéinurie et HTA'),
(167, 'Gonorrhée', 'Rocéphine', 'Ceftriaxone', '500 mg IM', 'INJECTION', 'INTRAMUSCULAIRE', 'Dose unique', 1, 'PREMIERE_INTENTION', 'Traitement de référence — dose unique'),
(168, 'Gonorrhée', 'Zithromax', 'Azithromycine', '1 g', 'COMPRIME', 'ORALE', 'Dose unique', 1, 'ADJUVANT', 'Associé à la ceftriaxone si chlamydia non exclu'),
(169, 'Gonorrhée', 'Vibramycine', 'Doxycycline', '100 mg', 'COMPRIME', 'ORALE', '2×/jour', 7, 'DEUXIEME_INTENTION', 'Alternative si ceftriaxone indisponible'),
(170, 'Goutte', 'Colchicine Pierre Fabre', 'Colchicine', '1 mg puis 0.5 mg', 'COMPRIME', 'ORALE', '1 h après puis 12 h après', 3, 'PREMIERE_INTENTION', 'Crise aiguë de goutte — en première intention'),
(171, 'Goutte', 'Zyloric', 'Allopurinol', '100-300 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Réduction uricémie — traitement de fond'),
(172, 'Goutte', 'Ibuprofène EG', 'Ibuprofène', '400-600 mg', 'COMPRIME', 'ORALE', '3×/jour', 5, 'SYMPTOMATIQUE', 'Crise aiguë si colchicine CI'),
(173, 'Goutte', 'Solupred', 'Prednisolone', '30 mg', 'COMPRIME', 'ORALE', '1×/jour', 5, 'DEUXIEME_INTENTION', 'Crise réfractaire ou AINS CI'),
(174, 'Grippe', 'Tamiflu', 'Oseltamivir', '75 mg', 'CAPSULE', 'ORALE', '2×/jour', 5, 'PREMIERE_INTENTION', 'Dans les 48 h après début des symptômes'),
(175, 'Grippe', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '4×/jour', 7, 'PREMIERE_INTENTION', 'Fièvre et myalgies — antipyrétique de choix'),
(176, 'Grippe', 'Relenza', 'Zanamivir', '10 mg (2 inhal.)', 'SPRAY', 'INHALATION', '2×/jour', 5, 'DEUXIEME_INTENTION', 'Grippe saisonnière — formes légères'),
(177, 'Hernie hiatale', 'Mopral', 'Oméprazole', '20 mg', 'CAPSULE', 'ORALE', '1×/matin', 28, 'PREMIERE_INTENTION', 'IPP — traitement de référence du RGO'),
(178, 'Hernie hiatale', 'Primpéran', 'Métoclopramide', '10 mg', 'COMPRIME', 'ORALE', '3×/jour', 14, 'ADJUVANT', 'Prokinétique — améliore la vidange gastrique'),
(179, 'Hernie hiatale', 'Phosphalugel', 'Phosphate d\'aluminium', '1 sachet', 'SOLUTION', 'ORALE', '3×/jour', 30, 'SYMPTOMATIQUE', 'Antiacide — soulagement immédiat'),
(180, 'Herpès génital', 'Zovirax', 'Aciclovir', '400 mg', 'COMPRIME', 'ORALE', '3×/jour', 7, 'PREMIERE_INTENTION', 'Primo-infection herpétique'),
(181, 'Herpès génital', 'Zelitrex', 'Valaciclovir', '500 mg', 'COMPRIME', 'ORALE', '2×/jour', 10, 'PREMIERE_INTENTION', 'Traitement curatif ou suppressif long terme'),
(182, 'Herpès génital', 'Famvir', 'Famciclovir', '250 mg', 'COMPRIME', 'ORALE', '3×/jour', 5, 'DEUXIEME_INTENTION', 'Alternative au valaciclovir'),
(183, 'Hypercholestérolémie', 'Tahor', 'Atorvastatine', '10-80 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Statine — réduction LDL-cholestérol'),
(184, 'Hypercholestérolémie', 'Crestor', 'Rosuvastatine', '5-40 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Statine haute intensité'),
(185, 'Hypercholestérolémie', 'Ezetrol', 'Ézétimibe', '10 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'En association ou si statine CI'),
(186, 'Hypercholestérolémie', 'Lipanthyl', 'Fénofibrate', '145 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Hypertriglycéridémie associée'),
(187, 'Hypermétropie', 'Larmes artificielles', 'Hypromellose', '1 goutte', 'COLLYRE', 'OPHTALMIQUE', '3×/jour', 30, 'SYMPTOMATIQUE', 'Sécheresse oculaire liée à l\'effort visuel'),
(188, 'Hypertension', 'Amlor', 'Amlodipine', '5-10 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Inhibiteur calcique — toléré en monothérapie'),
(189, 'Hypertension', 'Triatec', 'Ramipril', '2.5-10 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'IEC — néphroprotecteur'),
(190, 'Hypertension', 'Cozaar', 'Losartan', '25-100 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'ARA II — si toux sous IEC'),
(191, 'Hypertension', 'Esidrex', 'Hydrochlorothiazide', '12.5-25 mg', 'COMPRIME', 'ORALE', '1×/matin', 365, 'ADJUVANT', 'Diurétique thiazidique — en association'),
(192, 'Hypertension', 'Lopressor', 'Métoprolol', '25-100 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'ADJUVANT', 'Bêtabloquant — si comorbidité cardio'),
(193, 'Hyperthyroïdie', 'Néomercazole', 'Carbimazole', '5-60 mg', 'COMPRIME', 'ORALE', '3×/jour', 365, 'PREMIERE_INTENTION', 'Antithyroïdien de synthèse'),
(194, 'Hyperthyroïdie', 'Avlocardyl', 'Propranolol', '40-80 mg', 'COMPRIME', 'ORALE', '2-3×/jour', 30, 'ADJUVANT', 'Contrôle symptômes — tachycardie et tremblement'),
(195, 'Hyperthyroïdie', 'Méthimazole', 'Méthimazole', '5-30 mg', 'COMPRIME', 'ORALE', '1-3×/jour', 365, 'PREMIERE_INTENTION', 'Alternative au carbimazole'),
(196, 'Hypertrophie bénigne de prostate', 'Josir', 'Tamsulosine', '0.4 mg', 'CAPSULE', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Alpha-bloquant — amélioration rapide des symptômes'),
(197, 'Hypertrophie bénigne de prostate', 'Chibro-Proscar', 'Finastéride', '5 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Inhibiteur 5-alpha-réductase — réduction volume prostate'),
(198, 'Hypertrophie bénigne de prostate', 'Avodart', 'Dutastéride', '0.5 mg', 'CAPSULE', 'ORALE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'Alternative au finastéride'),
(199, 'Hypotension', 'Gutron', 'Midodrine', '2.5-10 mg', 'COMPRIME', 'ORALE', '3×/jour', 30, 'PREMIERE_INTENTION', 'Vasoconstricteur — hypotension orthostatique'),
(200, 'Hypotension', 'Fludrocortisone Aspen', 'Fludrocortisone', '0.1-0.3 mg', 'COMPRIME', 'ORALE', '1×/jour', 30, 'DEUXIEME_INTENTION', 'Minéralocorticoïde — hypotension neurogène'),
(201, 'Hypothyroïdie', 'Lévothyrox', 'Lévothyroxine (T4)', '25-200 µg', 'COMPRIME', 'ORALE', '1×/matin à jeun', 365, 'PREMIERE_INTENTION', 'Hormonothérapie substitutive — ajuster selon TSH'),
(202, 'Hypothyroïdie', 'Cytomel', 'Liothyronine (T3)', '5-25 µg', 'COMPRIME', 'ORALE', '2-3×/jour', 365, 'DEUXIEME_INTENTION', 'Formes réfractaires ou symptômes persistants'),
(203, 'Hépatite A', 'Doliprane', 'Paracétamol', '500-1000 mg', 'COMPRIME', 'ORALE', '3×/jour', 14, 'SYMPTOMATIQUE', 'Fièvre et douleurs — éviter doses élevées'),
(204, 'Hépatite A', 'Vitamine B complexe', 'Vitamines B1/B6/B12', '1 ampoule buvable', 'SOLUTION', 'ORALE', '1×/jour', 30, 'ADJUVANT', 'Support nutritionnel'),
(205, 'Hépatite B', 'Viread', 'Ténofovir disoproxil', '300 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Antivirale — hépatite B chronique'),
(206, 'Hépatite B', 'Baraclude', 'Entécavir', '0.5-1 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Alternative au ténofovir'),
(207, 'Hépatite B', 'Pegasys', 'Peg-interféron alpha-2a', '180 µg', 'INJECTION', 'SOUS-CUTANEE', '1×/semaine', 48, 'DEUXIEME_INTENTION', 'Hépatite B chronique — durée limitée'),
(208, 'Hépatite C', 'Sovaldi', 'Sofosbuvir', '400 mg', 'COMPRIME', 'ORALE', '1×/jour', 84, 'PREMIERE_INTENTION', 'Pangenotypique — association obligatoire'),
(209, 'Hépatite C', 'Daklinza', 'Daclatasvir', '60 mg', 'COMPRIME', 'ORALE', '1×/jour', 84, 'PREMIERE_INTENTION', 'Association avec sofosbuvir'),
(210, 'Hépatite C', 'Harvoni', 'Ledipasvir/Sofosbuvir', '90/400 mg', 'COMPRIME', 'ORALE', '1×/jour', 84, 'PREMIERE_INTENTION', 'Génotype 1 — taux de guérison > 95%'),
(211, 'Infarctus du myocarde', 'Aspirine UPSA', 'Acide acétylsalicylique', '250-500 mg IV puis 75 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Antiplaquettaire — dès suspicion IDM'),
(212, 'Infarctus du myocarde', 'Plavix', 'Clopidogrel', '300-600 mg de charge puis 75 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Double antiplaquettaire — 12 mois après stent'),
(213, 'Infarctus du myocarde', 'Morphine', 'Chlorhydrate de morphine', '2-4 mg IV', 'INJECTION', 'INTRAVEINEUSE', 'Si douleur persiste toutes 5 min', NULL, 'SYMPTOMATIQUE', 'Antalgie — IDM aigu'),
(214, 'Infarctus du myocarde', 'Lénitral', 'Trinitrine', '0.4 mg sublingual', 'SPRAY', 'ORALE', '1-2 bouffées sublinguales', NULL, 'PREMIERE_INTENTION', 'Vasodilatateur — crise angineuse / IDM'),
(215, 'Infarctus du myocarde', 'Tahor', 'Atorvastatine', '40-80 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Réduction LDL post-IDM — commencer en urgence'),
(216, 'Influenza A/B', 'Tamiflu', 'Oseltamivir', '75 mg', 'CAPSULE', 'ORALE', '2×/jour', 5, 'PREMIERE_INTENTION', 'Grippe A ou B — dans les 48 h'),
(217, 'Influenza A/B', 'Relenza', 'Zanamivir', '10 mg (2 inhal.)', 'SPRAY', 'INHALATION', '2×/jour', 5, 'DEUXIEME_INTENTION', 'Alternative à l\'oseltamivir'),
(218, 'Influenza A/B', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '4×/jour', 5, 'SYMPTOMATIQUE', 'Fièvre et douleurs'),
(219, 'Insuffisance cardiaque', 'Lasilix', 'Furosémide', '20-80 mg', 'COMPRIME', 'ORALE', '1-2×/jour', 365, 'PREMIERE_INTENTION', 'Diurétique de l\'anse — décongestion'),
(220, 'Insuffisance cardiaque', 'Aldactone', 'Spironolactone', '25-50 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Diurétique épargnant potassium — réduction mortalité'),
(221, 'Insuffisance cardiaque', 'Rénitec', 'Énalapril', '2.5-20 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', 'IEC — réduction mortalité'),
(222, 'Insuffisance cardiaque', 'Kredex', 'Carvédilol', '3.125-25 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', 'Bêtabloquant — débuter à faible dose'),
(223, 'Insuffisance cardiaque', 'Digoxine Nativelle', 'Digoxine', '0.125-0.25 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Contrôle FC en FA associée'),
(224, 'Insuffisance rénale aiguë', 'Lasilix', 'Furosémide', '40-200 mg IV', 'INJECTION', 'INTRAVEINEUSE', '2×/jour', 7, 'PREMIERE_INTENTION', 'Relance diurèse si anurie fonctionnelle'),
(225, 'Insuffisance rénale aiguë', 'Bicarbonate de Na', 'Bicarbonate de sodium', '1.4% IV', 'INJECTION', 'INTRAVEINEUSE', 'En continu', NULL, 'ADJUVANT', 'Correction acidose métabolique'),
(226, 'Insuffisance rénale aiguë', 'Kayexalate', 'Résine échangeuse d\'ions (polystyrène)', '15 g', 'POUDRE', 'ORALE', '3×/jour', 5, 'SYMPTOMATIQUE', 'Hyperkaliémie — à surveiller'),
(227, 'Insuffisance rénale chronique', 'Amlor', 'Amlodipine', '5-10 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Contrôle tensionnel — protection rénale'),
(228, 'Insuffisance rénale chronique', 'Triatec', 'Ramipril', '2.5-5 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'IEC — réduction protéinurie'),
(229, 'Insuffisance rénale chronique', 'NeoRecormon', 'Érythropoïétine bêta', '2000-10000 UI', 'INJECTION', 'SOUS-CUTANEE', '2-3×/semaine', 365, 'ADJUVANT', 'Anémie de l\'IRC'),
(230, 'Insuffisance rénale chronique', 'Renvela', 'Sévélamer', '800 mg', 'COMPRIME', 'ORALE', '3×/jour', 365, 'ADJUVANT', 'Chélateur du phosphore'),
(231, 'Kératite', 'Tobradex', 'Tobramycine 0.3%', '1 goutte', 'COLLYRE', 'OPHTALMIQUE', '4×/jour', 7, 'PREMIERE_INTENTION', 'Kératite bactérienne'),
(232, 'Kératite', 'Zovirax opht.', 'Aciclovir gel ophtalmique 3%', '1 bande de 10 mm', 'COLLYRE', 'OPHTALMIQUE', '5×/jour', 14, 'PREMIERE_INTENTION', 'Kératite herpétique'),
(233, 'Kératite', 'Voltarène', 'Diclofénac ophtalmique 0.1%', '1 goutte', 'COLLYRE', 'OPHTALMIQUE', '3×/jour', 7, 'SYMPTOMATIQUE', 'Anti-inflammatoire oculaire'),
(234, 'Laryngite', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '3×/jour', 5, 'PREMIERE_INTENTION', 'Antalgique et antipyrétique'),
(235, 'Laryngite', 'Ibuprofène EG', 'Ibuprofène', '400 mg', 'COMPRIME', 'ORALE', '3×/jour', 5, '', 'Anti-inflammatoire — douleur laryngée'),
(236, 'Laryngite', 'Solupred', 'Prednisolone', '1 mg/kg chez l\'enfant', 'COMPRIME', 'ORALE', 'Dose unique', 1, 'ADJUVANT', 'Laryngite striduleuse sévère'),
(237, 'Leucémie', 'Glivec', 'Imatinib', '400-600 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'LMC — inhibiteur de tyrosine kinase'),
(238, 'Leucémie', 'Novatrex', 'Méthotrexate', 'Variable selon protocole', 'INJECTION', 'INTRAVEINEUSE', 'Selon protocole', NULL, 'PREMIERE_INTENTION', 'LAL — selon schéma de chimiothérapie'),
(239, 'Leucémie', 'Adriamycine', 'Doxorubicine', 'Variable selon protocole', 'INJECTION', 'INTRAVEINEUSE', 'Selon protocole', NULL, 'PREMIERE_INTENTION', 'Chimiothérapie — protocoles LAL/LAM'),
(240, 'Leucémie', 'Cytarabine Pfizer', 'Cytarabine', '100-200 mg/m²/j', 'INJECTION', 'INTRAVEINEUSE', 'Selon protocole', NULL, 'PREMIERE_INTENTION', 'LAM — traitement d\'induction'),
(241, 'Lithiase rénale', 'Kétodolac', 'Kétorolac', '30 mg IM', 'INJECTION', 'INTRAMUSCULAIRE', 'Au besoin (max 4×/j)', 3, 'PREMIERE_INTENTION', 'Antalgie en crise colique — AINS efficace'),
(242, 'Lithiase rénale', 'Josir', 'Tamsulosine', '0.4 mg', 'CAPSULE', 'ORALE', '1×/jour', 28, 'PREMIERE_INTENTION', 'Facilite l\'expulsion du calcul distal'),
(243, 'Lithiase rénale', 'Zyloric', 'Allopurinol', '300 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Prévention lithiase urique'),
(244, 'Lithiase rénale', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '4×/jour', 3, 'SYMPTOMATIQUE', 'Antalgique complémentaire'),
(245, 'Lupus érythémateux systémique', 'Plaquenil', 'Hydroxychloroquine', '200-400 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Traitement de fond — tous les lupus'),
(246, 'Lupus érythémateux systémique', 'Solupred', 'Prednisolone', '0.5-1 mg/kg/j', 'COMPRIME', 'ORALE', '1×/matin', 60, 'PREMIERE_INTENTION', 'Poussée lupique — dégression progressive'),
(247, 'Lupus érythémateux systémique', 'Imurel', 'Azathioprine', '2-3 mg/kg/j', 'COMPRIME', 'ORALE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'Épargne cortisonique'),
(248, 'Lupus érythémateux systémique', 'Benlysta', 'Belimumab', '10 mg/kg IV', 'INJECTION', 'INTRAVEINEUSE', 'S0, S2, S4 puis /4 sem', 365, 'DEUXIEME_INTENTION', 'Anti-BLyS — formes réfractaires'),
(249, 'Lymphome', 'Mabthera', 'Rituximab', '375 mg/m²', 'INJECTION', 'INTRAVEINEUSE', 'J1 de chaque cycle', 182, 'PREMIERE_INTENTION', 'Lymphome B — anti-CD20'),
(250, 'Lymphome', 'Endoxan', 'Cyclophosphamide', '750 mg/m²', 'INJECTION', 'INTRAVEINEUSE', 'J1 de chaque cycle', 182, 'PREMIERE_INTENTION', 'Protocole R-CHOP — lymphome agressif'),
(251, 'Lymphome', 'Solupred', 'Prednisolone', '100 mg/j', 'COMPRIME', 'ORALE', 'J1-J5 de chaque cycle', 182, 'ADJUVANT', 'Protocole CHOP'),
(252, 'Lymphome', 'Oncovin', 'Vincristine', '1.4 mg/m²', 'INJECTION', 'INTRAVEINEUSE', 'J1 de chaque cycle', 182, 'PREMIERE_INTENTION', 'Protocole CHOP'),
(253, 'Maladie d\'Addison', 'Hydrocortisone ROUSSEL', 'Hydrocortisone', '15-25 mg/j', 'COMPRIME', 'ORALE', '2-3×/jour', 365, 'PREMIERE_INTENTION', 'Substitution glucocorticoïde — indispensable'),
(254, 'Maladie d\'Addison', 'Fludrocortisone BESINS', 'Fludrocortisone', '0.05-0.2 mg', 'COMPRIME', 'ORALE', '1×/matin', 365, 'PREMIERE_INTENTION', 'Substitution minéralocorticoïde'),
(255, 'Malaria', 'Coartem', 'Artéméther + Luméfantrine', '4 cp par prise', 'COMPRIME', 'ORALE', '2×/jour', 3, 'PREMIERE_INTENTION', 'Paludisme simple non compliqué — première intention'),
(256, 'Malaria', 'Quinimax', 'Quinine', '8 mg/kg toutes 8 h IV', 'INJECTION', 'INTRAVEINEUSE', '3×/jour', 7, 'PREMIERE_INTENTION', 'Paludisme grave — perfusion lente'),
(257, 'Malaria', 'Artésunate IV', 'Artésunate', '2.4 mg/kg IV', 'INJECTION', 'INTRAVEINEUSE', 'H0, H12, H24 puis 1×/jour', 7, 'PREMIERE_INTENTION', 'Paludisme grave — préféré à la quinine IV'),
(258, 'Malaria', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '4×/jour', 5, 'SYMPTOMATIQUE', 'Fièvre et céphalées'),
(259, 'Migraine', 'Imigrane', 'Sumatriptan', '50-100 mg', 'COMPRIME', 'ORALE', 'À la crise', NULL, 'PREMIERE_INTENTION', 'Triptan — traitement de la crise migraineuse'),
(260, 'Migraine', 'Ibuprofène EG', 'Ibuprofène', '400-600 mg', 'COMPRIME', 'ORALE', 'À la crise (max 3/sem)', NULL, 'PREMIERE_INTENTION', 'AINS — crises légères à modérées'),
(261, 'Migraine', 'Propranolol', 'Propranolol', '40-80 mg', 'COMPRIME', 'ORALE', '2×/jour', 180, 'DEUXIEME_INTENTION', 'Prévention migraine fréquente'),
(262, 'Migraine', 'Epitomax', 'Topiramate', '25-100 mg', 'COMPRIME', 'ORALE', '1×/soir', 180, 'DEUXIEME_INTENTION', 'Prévention — formes fréquentes'),
(263, 'Molluscum contagiosum', 'Aldara', 'Imiquimod 5%', 'Fine couche', 'CREME', 'CUTANEE', '3×/semaine (soir)', 60, 'PREMIERE_INTENTION', 'Immunomodulateur local'),
(264, 'Molluscum contagiosum', 'Wartec', 'Podophyllotoxine 0.5%', 'Locale', 'SOLUTION', 'CUTANEE', '2×/jour 3 j/sem', 28, 'DEUXIEME_INTENTION', 'Traitement local des lésions'),
(265, 'Mononucléose', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '3×/jour', 14, 'PREMIERE_INTENTION', 'Fièvre et douleurs — ne pas donner Aspirine'),
(266, 'Mononucléose', 'Ibuprofène EG', 'Ibuprofène', '400 mg', 'COMPRIME', 'ORALE', '3×/jour', 7, 'ADJUVANT', 'Angine — soulagement de la douleur'),
(267, 'Myocardite', 'Ibuprofène EG', 'Ibuprofène', '400 mg', 'COMPRIME', 'ORALE', '3×/jour', 14, 'PREMIERE_INTENTION', 'Myocardite légère — AINS'),
(268, 'Myocardite', 'Colchicine Pierre Fabre', 'Colchicine', '0.5 mg', 'COMPRIME', 'ORALE', '2×/jour', 90, 'ADJUVANT', 'Réduction récidive péricardite/myocardite'),
(269, 'Myocardite', 'Lasilix', 'Furosémide', '40 mg', 'COMPRIME', 'ORALE', '1×/jour', 30, 'ADJUVANT', 'Insuffisance cardiaque associée'),
(270, 'Myocardite', 'Solupred', 'Prednisolone', '1 mg/kg', 'COMPRIME', 'ORALE', '1×/matin', 30, 'DEUXIEME_INTENTION', 'Myocardite auto-immune sévère'),
(271, 'Myopie', 'Larmes artificielles', 'Hypromellose', '1 goutte', 'COLLYRE', 'OPHTALMIQUE', '3-4×/jour', 30, 'SYMPTOMATIQUE', 'Sécheresse oculaire liée au port de lentilles'),
(272, 'Neuropathie diabétique', 'Lyrica', 'Prégabaline', '75-300 mg', 'CAPSULE', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', 'Douleurs neuropathiques'),
(273, 'Neuropathie diabétique', 'Cymbalta', 'Duloxétine', '30-60 mg', 'CAPSULE', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Douleurs neuropathiques diabétiques'),
(274, 'Neuropathie diabétique', 'Neurontin', 'Gabapentine', '300-1200 mg', 'CAPSULE', 'ORALE', '3×/jour', 365, 'ADJUVANT', 'Alternative à la prégabaline'),
(275, 'Neuropathie diabétique', 'Laroxyl', 'Amitriptyline', '25-75 mg', 'COMPRIME', 'ORALE', '1×/soir', 365, 'DEUXIEME_INTENTION', 'Douleurs neuropathiques chroniques'),
(276, 'Néphrotique', 'Solupred', 'Prednisolone', '1 mg/kg/j', 'COMPRIME', 'ORALE', '1×/matin', 60, 'PREMIERE_INTENTION', 'Syndrome néphrotique idiopathique'),
(277, 'Néphrotique', 'Lasilix', 'Furosémide', '40-80 mg', 'COMPRIME', 'ORALE', '2×/jour', 30, 'ADJUVANT', 'Œdèmes importants'),
(278, 'Néphrotique', 'Tahor', 'Atorvastatine', '20-40 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Hypercholestérolémie associée'),
(279, 'Néphrotique', 'Triatec', 'Ramipril', '2.5-5 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Réduction protéinurie'),
(280, 'Otite', 'Clamoxyl', 'Amoxicilline', '500 mg', 'COMPRIME', 'ORALE', '3×/jour', 7, 'PREMIERE_INTENTION', 'Otite moyenne aiguë bactérienne'),
(281, 'Otite', 'Ibuprofène EG', 'Ibuprofène', '400 mg', 'COMPRIME', 'ORALE', '3×/jour', 5, 'SYMPTOMATIQUE', 'Antalgique et anti-inflammatoire'),
(282, 'Otite', 'Ciprodex', 'Ciprofloxacine + Dexaméthasone', '3 gouttes', 'COLLYRE', 'OPHTALMIQUE', '2×/jour', 7, 'PREMIERE_INTENTION', 'Otite externe bactérienne'),
(283, 'Otite', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '4×/jour', 5, 'SYMPTOMATIQUE', 'Douleur otalgique'),
(284, 'Pancréatite', 'Morphine', 'Chlorhydrate de morphine', '0.1 mg/kg IV/SC', 'INJECTION', 'SOUS-CUTANEE', 'Toutes les 4 h si douleur', NULL, 'PREMIERE_INTENTION', 'Antalgie — pancréatite aiguë sévère'),
(285, 'Pancréatite', 'Tramadol EG', 'Tramadol', '100 mg LP', 'COMPRIME', 'ORALE', '2×/jour', 7, 'PREMIERE_INTENTION', 'Antalgie palier 2 — formes légères'),
(286, 'Pancréatite', 'Ondansétron', 'Ondansétron', '8 mg', 'COMPRIME', 'ORALE', '3×/jour', 5, 'SYMPTOMATIQUE', 'Antiémétique — nausées et vomissements'),
(287, 'Parkinson', 'Sinemet', 'Lévodopa + Carbidopa', '25/100 mg', 'COMPRIME', 'ORALE', '3×/jour', 365, 'PREMIERE_INTENTION', 'Traitement de référence de la maladie de Parkinson'),
(288, 'Parkinson', 'Mirapexin', 'Pramipexole', '0.088-3.3 mg', 'COMPRIME', 'ORALE', '3×/jour', 365, 'PREMIERE_INTENTION', 'Agoniste dopaminergique — en monothérapie ou association'),
(289, 'Parkinson', 'Jumexal', 'Sélégiline', '5 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'ADJUVANT', 'IMAO-B — neuroprotection et symptômes légers'),
(290, 'Parkinson', 'Mantadix', 'Amantadine', '100 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'ADJUVANT', 'Dyskinésies induites par lévodopa'),
(291, 'Pemphigus', 'Solupred', 'Prednisolone', '1-2 mg/kg/j', 'COMPRIME', 'ORALE', '1×/matin', 90, 'PREMIERE_INTENTION', 'Corticothérapie systémique haute dose'),
(292, 'Pemphigus', 'Mabthera', 'Rituximab', '1000 mg', 'INJECTION', 'INTRAVEINEUSE', 'J1 et J15', 28, 'PREMIERE_INTENTION', 'Formes sévères — réduction récidives'),
(293, 'Pemphigus', 'Imurel', 'Azathioprine', '2-3 mg/kg/j', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Épargne cortisonique'),
(294, 'Pemphigus', 'Disulone', 'Dapsone', '50-100 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Pemphigus foliacé léger'),
(295, 'Pneumonie', 'Augmentin', 'Amoxicilline-clavulanate', '1 g', 'COMPRIME', 'ORALE', '3×/jour', 7, 'PREMIERE_INTENTION', 'Pneumonie communautaire sans comorbidité'),
(296, 'Pneumonie', 'Zithromax', 'Azithromycine', '500 mg', 'COMPRIME', 'ORALE', '1×/jour', 5, 'DEUXIEME_INTENTION', 'Pneumonie atypique ou allergie péni'),
(297, 'Pneumonie', 'Rocéphine', 'Ceftriaxone', '1-2 g IV', 'INJECTION', 'INTRAVEINEUSE', '1×/jour', 7, 'PREMIERE_INTENTION', 'Formes sévères hospitalisées'),
(298, 'Pneumonie', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '4×/jour', 7, 'SYMPTOMATIQUE', 'Fièvre et douleurs thoraciques'),
(299, 'Polyglobulie', 'Aspirine UPSA', 'Acide acétylsalicylique', '100 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Prévention thrombotique'),
(300, 'Polyglobulie', 'Hydréa', 'Hydroxyurée', '500-2000 mg', 'CAPSULE', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Réduction polyglobulie — haut risque thrombotique'),
(301, 'Polyglobulie', 'Jakavi', 'Ruxolitinib', '10-25 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'DEUXIEME_INTENTION', 'Résistance ou intolérance à l\'hydroxyurée'),
(302, 'Polymyosite/Dermatomyosite', 'Solupred', 'Prednisolone', '1-1.5 mg/kg/j', 'COMPRIME', 'ORALE', '1×/matin', 60, 'PREMIERE_INTENTION', 'Traitement de première ligne'),
(303, 'Polymyosite/Dermatomyosite', 'Novatrex', 'Méthotrexate', '15-25 mg/sem', 'COMPRIME', 'ORALE', '1×/semaine', 365, 'DEUXIEME_INTENTION', 'Épargne cortisonique'),
(304, 'Polymyosite/Dermatomyosite', 'Imurel', 'Azathioprine', '2 mg/kg/j', 'COMPRIME', 'ORALE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'Alternative au méthotrexate'),
(305, 'Presbytie', 'Larmes artificielles', 'Hypromellose', '1 goutte', 'COLLYRE', 'OPHTALMIQUE', '3×/jour', 30, 'SYMPTOMATIQUE', 'Sécheresse oculaire fréquente chez les presbytes'),
(306, 'Prostatite', 'Ciflox', 'Ciprofloxacine', '500 mg', 'COMPRIME', 'ORALE', '2×/jour', 28, 'PREMIERE_INTENTION', 'Fluoroquinolone — prostatite bactérienne aiguë'),
(307, 'Prostatite', 'Vibramycine', 'Doxycycline', '100 mg', 'COMPRIME', 'ORALE', '2×/jour', 28, 'DEUXIEME_INTENTION', 'Prostatite chronique — si fluoroquinolone CI');
INSERT INTO `catalogue_medicaments` (`id`, `maladie`, `nom_commercial`, `denomination_commune`, `dosage_standard`, `forme`, `voie_administration`, `frequence_habituelle`, `duree_standard_jours`, `categorie`, `notes`) VALUES
(308, 'Prostatite', 'Josir', 'Tamsulosine', '0.4 mg', 'CAPSULE', 'ORALE', '1×/jour', 30, 'ADJUVANT', 'Symptômes obstructifs associés'),
(309, 'Prostatite', 'Ibuprofène EG', 'Ibuprofène', '400 mg', 'COMPRIME', 'ORALE', '3×/jour', 7, 'SYMPTOMATIQUE', 'Douleurs pelviennes'),
(310, 'Psoriasis', 'Dermovate', 'Clobétasol 0.05%', 'Fine couche', 'CREME', 'CUTANEE', '1×/jour', 28, 'PREMIERE_INTENTION', 'Corticoïde local puissant — poussée'),
(311, 'Psoriasis', 'Daivonex', 'Calcipotriol', '50 µg/g', 'CREME', 'CUTANEE', '2×/jour', 56, 'PREMIERE_INTENTION', 'Analogue vitamine D3 — plaques chroniques'),
(312, 'Psoriasis', 'Novatrex', 'Méthotrexate', '7.5-25 mg', 'COMPRIME', 'ORALE', '1×/semaine', 365, 'DEUXIEME_INTENTION', 'Psoriasis modéré à sévère — bilan pré-thérapeutique'),
(313, 'Psoriasis', 'Humira', 'Adalimumab', '80 mg J1, 40 mg J15, puis 40 mg/2 sem', 'INJECTION', 'SOUS-CUTANEE', '1×/2 semaines', 365, 'DEUXIEME_INTENTION', 'Biothérapie anti-TNFα'),
(314, 'Psoriasis', 'Daivobet', 'Bétaméthasone + Calcipotriol', 'Locale', 'CREME', 'CUTANEE', '1×/jour', 28, 'PREMIERE_INTENTION', 'Association corticoïde + vit D3'),
(315, 'Pyélonéphrite', 'Rocéphine', 'Ceftriaxone', '1-2 g IV', 'INJECTION', 'INTRAVEINEUSE', '1×/jour', 14, 'PREMIERE_INTENTION', 'Pyélonéphrite aiguë hospitalisée'),
(316, 'Pyélonéphrite', 'Ciflox', 'Ciprofloxacine', '500 mg', 'COMPRIME', 'ORALE', '2×/jour', 14, 'PREMIERE_INTENTION', 'Pyélonéphrite simple — ambulatoire'),
(317, 'Pyélonéphrite', 'Augmentin', 'Amoxicilline-clavulanate', '1 g', 'COMPRIME', 'ORALE', '3×/jour', 14, 'DEUXIEME_INTENTION', 'Selon antibiogramme'),
(318, 'Pyélonéphrite', 'Gentalline', 'Gentamicine', '3-5 mg/kg/j IV', 'INJECTION', 'INTRAVEINEUSE', '1×/jour', 5, 'ADJUVANT', 'Association initiale — formes sévères'),
(319, 'Péricardite', 'Ibuprofène EG', 'Ibuprofène', '600 mg', 'COMPRIME', 'ORALE', '3×/jour', 14, 'PREMIERE_INTENTION', 'AINS de choix en péricardite'),
(320, 'Péricardite', 'Colchicine Pierre Fabre', 'Colchicine', '0.5 mg', 'COMPRIME', 'ORALE', '2×/jour', 90, 'PREMIERE_INTENTION', 'Réduction récidive — associer aux AINS'),
(321, 'Péricardite', 'Solupred', 'Prednisolone', '0.2-0.5 mg/kg/j', 'COMPRIME', 'ORALE', '1×/matin', 28, 'DEUXIEME_INTENTION', 'Péricardite réfractaire — risque de rechute'),
(322, 'Rhinite allergique', 'Zyrtec', 'Cétirizine', '10 mg', 'COMPRIME', 'ORALE', '1×/soir', 30, 'PREMIERE_INTENTION', 'Antihistaminique H1 non sédatif'),
(323, 'Rhinite allergique', 'Clarityne', 'Loratadine', '10 mg', 'COMPRIME', 'ORALE', '1×/jour', 30, 'PREMIERE_INTENTION', 'Antihistaminique H1 — non sédatif'),
(324, 'Rhinite allergique', 'Rhinocort', 'Budésonide nasal', '64 µg/nasal', 'SPRAY', 'NASALE', '2×/jour', 30, 'PREMIERE_INTENTION', 'Corticoïde nasal — symptômes nasaux'),
(325, 'Rhinite allergique', 'Rhinadvil', 'Ibuprofène + Pseudoéphédrine', 'Selon posologie', 'COMPRIME', 'ORALE', '3×/jour', 5, 'SYMPTOMATIQUE', 'Congestion nasale — usage court'),
(326, 'Rougeole', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '4×/jour', 7, 'PREMIERE_INTENTION', 'Fièvre — traitement symptomatique'),
(327, 'Rougeole', 'Vitamine A', 'Rétinol (vitamine A)', '200 000 UI 2 doses', 'COMPRIME', 'ORALE', 'J1 et J2', 2, 'ADJUVANT', 'OMS — réduit complications chez l\'enfant'),
(328, 'Rétinopathie diabétique', 'Lucentis', 'Ranibizumab', '0.5 mg', 'INJECTION', 'OPHTALMIQUE', '1×/mois', 365, 'PREMIERE_INTENTION', 'DMAO proliférante — injection intravitréenne'),
(329, 'Rétinopathie diabétique', 'Glucophage', 'Metformine', '500-1000 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'ADJUVANT', 'Contrôle glycémique — prévention progression'),
(330, 'Rétinopathie diabétique', 'Triatec', 'Ramipril', '5-10 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Contrôle tensionnel — protection rétinienne'),
(331, 'Salmonellose', 'Ciflox', 'Ciprofloxacine', '500 mg', 'COMPRIME', 'ORALE', '2×/jour', 5, 'PREMIERE_INTENTION', 'Formes sévères ou immunodéprimés'),
(332, 'Salmonellose', 'Rocéphine', 'Ceftriaxone', '1-2 g IV', 'INJECTION', 'INTRAVEINEUSE', '1×/jour', 5, 'PREMIERE_INTENTION', 'Bactériémie — formes graves'),
(333, 'Salmonellose', 'Zithromax', 'Azithromycine', '500 mg', 'COMPRIME', 'ORALE', '1×/jour', 3, 'DEUXIEME_INTENTION', 'Alternative selon antibiogramme'),
(334, 'Salmonellose', 'SRO OMS', 'Sels de réhydratation orale', '1 sachet/L', 'POUDRE', 'ORALE', 'Selon soif', 5, 'ADJUVANT', 'Réhydratation — priorité'),
(335, 'Scléroderomie', 'Novatrex', 'Méthotrexate', '15-25 mg/sem', 'COMPRIME', 'ORALE', '1×/semaine', 365, 'PREMIERE_INTENTION', 'Atteinte cutanée précoce'),
(336, 'Scléroderomie', 'Cellcept', 'Mycophénolate mofétil', '1-3 g/j', 'COMPRIME', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', 'Atteinte pulmonaire interstitielle'),
(337, 'Scléroderomie', 'Adalate', 'Nifédipine', '10-30 mg', 'COMPRIME', 'ORALE', '3×/jour', 365, 'ADJUVANT', 'Phénomène de Raynaud'),
(338, 'Scléroderomie', 'Tracleer', 'Bosentan', '125 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'ADJUVANT', 'Hypertension artérielle pulmonaire'),
(339, 'Sclérose en plaques', 'Avonex', 'Interféron bêta-1a', '30 µg IM', 'INJECTION', 'INTRAMUSCULAIRE', '1×/semaine', 365, 'PREMIERE_INTENTION', 'Formes rémittentes — réduction poussées'),
(340, 'Sclérose en plaques', 'Tysabri', 'Natalizumab', '300 mg IV', 'INJECTION', 'INTRAVEINEUSE', '1×/4 semaines', 365, 'DEUXIEME_INTENTION', 'Formes très actives — risque LEMP'),
(341, 'Sclérose en plaques', 'Gilenya', 'Fingolimod', '0.5 mg', 'CAPSULE', 'ORALE', '1×/jour', 365, 'DEUXIEME_INTENTION', 'SEP-R active — immunomodulateur oral'),
(342, 'Sclérose en plaques', 'Solumedrol', 'Méthylprednisolone IV', '1 g', 'INJECTION', 'INTRAVEINEUSE', '1×/jour (5 jours)', 5, 'PREMIERE_INTENTION', 'Poussée aiguë'),
(343, 'Sclérose latérale amyotrophique', 'Rilutek', 'Riluzole', '50 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', 'Seul traitement modifiant la maladie — ralentit progression'),
(344, 'Sclérose latérale amyotrophique', 'Radicava', 'Édaravone', '60 mg IV', 'INJECTION', 'INTRAVEINEUSE', 'Cycles de 14 j/28 j', 365, 'DEUXIEME_INTENTION', 'Réducteur du stress oxydatif'),
(345, 'Sclérose latérale amyotrophique', 'Liorésal', 'Baclofène', '5-80 mg', 'COMPRIME', 'ORALE', '3×/jour', 365, 'SYMPTOMATIQUE', 'Spasticité'),
(346, 'Sinusite', 'Clamoxyl', 'Amoxicilline', '500 mg', 'COMPRIME', 'ORALE', '3×/jour', 7, 'PREMIERE_INTENTION', 'Sinusite bactérienne confirmée'),
(347, 'Sinusite', 'Augmentin', 'Amoxicilline-clavulanate', '1 g', 'COMPRIME', 'ORALE', '3×/jour', 7, 'DEUXIEME_INTENTION', 'Sinusite frontale ou pansinusite'),
(348, 'Sinusite', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '4×/jour', 7, 'SYMPTOMATIQUE', 'Douleurs faciales et céphalées'),
(349, 'Sinusite', 'Rhinofluimucil', 'Acétylcystéine nasale', '2 pulv.', 'SPRAY', 'NASALE', '3×/jour', 10, 'ADJUVANT', 'Fluidifiant des sécrétions sinusiennes'),
(350, 'Spondylarthrite ankylosante', 'Naproxène', 'Naproxène', '500 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', 'AINS — traitement symptomatique de fond'),
(351, 'Spondylarthrite ankylosante', 'Salazopyrine', 'Sulfasalazine', '500-3000 mg', 'COMPRIME', 'ORALE', '3×/jour', 365, 'DEUXIEME_INTENTION', 'Atteinte périphérique prédominante'),
(352, 'Spondylarthrite ankylosante', 'Humira', 'Adalimumab', '40 mg', 'INJECTION', 'SOUS-CUTANEE', '1×/2 semaines', 365, 'DEUXIEME_INTENTION', 'Anti-TNFα — formes axiales actives'),
(353, 'Spondylarthrite ankylosante', 'Enbrel', 'Étanercept', '50 mg', 'INJECTION', 'SOUS-CUTANEE', '1×/semaine', 365, 'DEUXIEME_INTENTION', 'Anti-TNFα — alternative à l\'adalimumab'),
(354, 'Stéatose hépatique', 'Glucophage', 'Metformine', '500-1000 mg', 'COMPRIME', 'ORALE', '2×/jour', 180, 'ADJUVANT', 'Résistance à l\'insuline associée au diabète'),
(355, 'Stéatose hépatique', 'Vitamine E', 'Alpha-tocophérol', '800 UI', 'CAPSULE', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'NASH non diabétique — effet antioxydant'),
(356, 'Syndrome de Cushing', 'Métopirone', 'Métyrapone', '250-4000 mg/j', 'CAPSULE', 'ORALE', '4×/jour', 30, 'PREMIERE_INTENTION', 'Inhibiteur de synthèse du cortisol'),
(357, 'Syndrome de Cushing', 'Nizoral', 'Kétoconazole', '200-1200 mg', 'COMPRIME', 'ORALE', '2-3×/jour', 30, 'DEUXIEME_INTENTION', 'Inhibiteur stéroïdogénèse — surveillance hépatique'),
(358, 'Syndrome de Cushing', 'Korlym', 'Mifépristone', '300-1200 mg', 'COMPRIME', 'ORALE', '1×/jour', 30, 'DEUXIEME_INTENTION', 'Cushing non chirurgical — antagoniste du récepteur glucocorticoïde'),
(359, 'Syndrome de Guillain-Barré', 'Immunoglobulines polyvalentes', 'IgIV humaines', '0.4 g/kg/j', 'INJECTION', 'INTRAVEINEUSE', '1×/jour (5 jours)', 5, 'PREMIERE_INTENTION', 'Traitement immunomodulateur de référence'),
(360, 'Syndrome de Guillain-Barré', 'Gabapentine EG', 'Gabapentine', '300-600 mg', 'CAPSULE', 'ORALE', '3×/jour', 30, 'SYMPTOMATIQUE', 'Douleurs neuropathiques'),
(361, 'Syndrome de Guillain-Barré', 'Morphine', 'Chlorhydrate de morphine', '2-4 mg SC', 'INJECTION', 'SOUS-CUTANEE', 'Toutes les 4 h si douleur', NULL, 'SYMPTOMATIQUE', 'Antalgie forte — formes douloureuses'),
(362, 'Syndrome de Sjögren', 'Plaquenil', 'Hydroxychloroquine', '200-400 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Atteinte systémique légère'),
(363, 'Syndrome de Sjögren', 'Ciclosporine A', 'Ciclosporine A 0.05%', '1 goutte', 'COLLYRE', 'OPHTALMIQUE', '2×/jour', 365, 'PREMIERE_INTENTION', 'Sécheresse oculaire sévère'),
(364, 'Syndrome de Sjögren', 'Salagen', 'Pilocarpine', '5 mg', 'COMPRIME', 'ORALE', '3×/jour', 90, 'ADJUVANT', 'Stimulation des glandes salivaires et lacrymales'),
(365, 'Syndrome du côlon irritable', 'Spasfon', 'Phloroglucinol', '80 mg', 'COMPRIME', 'ORALE', '3×/jour', 30, 'PREMIERE_INTENTION', 'Antispasmodique — douleurs abdominales'),
(366, 'Syndrome du côlon irritable', 'Imodium', 'Lopéramide', '2 mg', 'COMPRIME', 'ORALE', 'Après chaque selle liquide', 30, 'PREMIERE_INTENTION', 'Forme diarrhéique prédominante'),
(367, 'Syndrome du côlon irritable', 'Forlax', 'Macrogol 4000', '10 g', 'POUDRE', 'ORALE', '2×/jour', 30, 'ADJUVANT', 'Forme constipée prédominante'),
(368, 'Syndrome du côlon irritable', 'Laroxyl', 'Amitriptyline', '10-25 mg', 'COMPRIME', 'ORALE', '1×/soir', 90, 'DEUXIEME_INTENTION', 'Douleurs et troubles du sommeil associés'),
(369, 'Syphilis', 'Extencilline', 'Benzathine pénicilline G', '2.4 M UI IM', 'INJECTION', 'INTRAMUSCULAIRE', 'Dose unique (ou 3 si tardive)', NULL, 'PREMIERE_INTENTION', 'Traitement de référence toute syphilis'),
(370, 'Syphilis', 'Vibramycine', 'Doxycycline', '100 mg', 'COMPRIME', 'ORALE', '2×/jour', 14, 'DEUXIEME_INTENTION', 'Si allergie pénicilline — syphilis primaire/secondaire'),
(371, 'Syphilis', 'Zithromax', 'Azithromycine', '2 g', 'COMPRIME', 'ORALE', 'Dose unique', 1, 'DEUXIEME_INTENTION', 'Alternative — résistances émergentes à surveiller'),
(372, 'Thrombocytémie', 'Hydréa', 'Hydroxyurée', '500-2000 mg', 'CAPSULE', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Haut risque thrombotique — cytoreduction'),
(373, 'Thrombocytémie', 'Aspirine UPSA', 'Acide acétylsalicylique', '100 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'ADJUVANT', 'Prévention thrombose'),
(374, 'Thrombocytémie', 'Agrylin', 'Anagrélide', '0.5-2.5 mg', 'CAPSULE', 'ORALE', '2×/jour', 365, 'DEUXIEME_INTENTION', 'Si intolérance ou résistance à l\'hydroxyurée'),
(375, 'Thrombose veineuse', 'Eliquis', 'Apixaban', '10 mg (7 j) puis 5 mg', 'COMPRIME', 'ORALE', '2×/jour', 90, 'PREMIERE_INTENTION', 'TVP — anticoagulant oral direct'),
(376, 'Thrombose veineuse', 'Xarelto', 'Rivaroxaban', '15 mg (21 j) puis 20 mg', 'COMPRIME', 'ORALE', '2×/jour puis 1×/jour', 90, 'PREMIERE_INTENTION', 'TVP — anticoagulant oral direct'),
(377, 'Thrombose veineuse', 'Lovenox', 'Enoxaparine', '1 mg/kg', 'INJECTION', 'SOUS-CUTANEE', '2×/jour', 10, 'PREMIERE_INTENTION', 'Héparinothérapie initiale'),
(378, 'Thrombose veineuse', 'Coumadine', 'Warfarine', '2-10 mg (selon INR)', 'COMPRIME', 'ORALE', '1×/soir', 180, 'DEUXIEME_INTENTION', 'Anticoagulation long terme — INR cible 2-3'),
(379, 'Thyroïdite', 'Ibuprofène EG', 'Ibuprofène', '400-600 mg', 'COMPRIME', 'ORALE', '3×/jour', 14, 'PREMIERE_INTENTION', 'Thyroïdite subaiguë de De Quervain — douleur'),
(380, 'Thyroïdite', 'Solupred', 'Prednisolone', '30-40 mg', 'COMPRIME', 'ORALE', '1×/matin', 30, 'DEUXIEME_INTENTION', 'Thyroïdite sévère réfractaire aux AINS'),
(381, 'Thyroïdite', 'Lévothyrox', 'Lévothyroxine', '25-100 µg', 'COMPRIME', 'ORALE', '1×/matin', 365, 'ADJUVANT', 'Si hypothyroïdie séquellaire'),
(382, 'Trachéite', 'Clamoxyl', 'Amoxicilline', '500 mg', 'COMPRIME', 'ORALE', '3×/jour', 7, 'PREMIERE_INTENTION', 'Trachéite bactérienne confirmée'),
(383, 'Trachéite', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '4×/jour', 5, 'SYMPTOMATIQUE', 'Douleur trachéale et fièvre'),
(384, 'Trachéite', 'Bisolvon', 'Bromhexine', '8 mg', 'COMPRIME', 'ORALE', '3×/jour', 7, 'SYMPTOMATIQUE', 'Mucolytique — sécrétions trachéales'),
(385, 'Trouble de coagulation', 'Exacyl', 'Acide tranexamique', '500-1000 mg', 'COMPRIME', 'ORALE', '3×/jour', 7, 'PREMIERE_INTENTION', 'Antifibrinolytique — saignement actif'),
(386, 'Trouble de coagulation', 'Facteur VIII', 'Facteur VIII de coagulation', 'Variable selon poids et sévérité', 'INJECTION', 'INTRAVEINEUSE', 'Selon schéma', NULL, 'PREMIERE_INTENTION', 'Hémophilie A — substitution'),
(387, 'Trouble de coagulation', 'Vitamine K1', 'Phytoménadione', '10 mg', 'COMPRIME', 'ORALE', '1×/jour', 5, 'ADJUVANT', 'Surdosage AVK ou carence en vit K'),
(388, 'Trouble de coagulation', 'PFC', 'Plasma frais congelé', 'Variable mL/kg', 'INJECTION', 'INTRAVEINEUSE', 'Selon bilan', NULL, 'ADJUVANT', 'Coagulopathie sévère — urgence'),
(389, 'Tuberculose', 'Rifampicine', 'Rifampicine', '600 mg', 'COMPRIME', 'ORALE', '1×/jour à jeun', 180, 'PREMIERE_INTENTION', 'Protocole HRZE — 2 premiers mois'),
(390, 'Tuberculose', 'Isoniazide', 'Isoniazide', '300 mg', 'COMPRIME', 'ORALE', '1×/jour', 180, 'PREMIERE_INTENTION', 'Protocole HRZE — toute la durée'),
(391, 'Tuberculose', 'Pyrazinamide', 'Pyrazinamide', '1500-2000 mg', 'COMPRIME', 'ORALE', '1×/jour', 60, 'PREMIERE_INTENTION', 'Protocole HRZE — 2 premiers mois uniquement'),
(392, 'Tuberculose', 'Myambutol', 'Éthambutol', '1200-1600 mg', 'COMPRIME', 'ORALE', '1×/jour', 60, 'PREMIERE_INTENTION', 'Protocole HRZE — 2 premiers mois'),
(393, 'Tuberculose', 'Vitamine B6', 'Pyridoxine', '25-50 mg', 'COMPRIME', 'ORALE', '1×/jour', 180, 'ADJUVANT', 'Prévention neuropathie à l\'isoniazide'),
(394, 'Typhoïde', 'Zithromax', 'Azithromycine', '500 mg', 'COMPRIME', 'ORALE', '1×/jour', 7, 'PREMIERE_INTENTION', 'Fièvre typhoïde non compliquée — résistances faibles'),
(395, 'Typhoïde', 'Ciflox', 'Ciprofloxacine', '500 mg', 'COMPRIME', 'ORALE', '2×/jour', 7, 'PREMIERE_INTENTION', 'Typhoïde sensible aux fluoroquinolones'),
(396, 'Typhoïde', 'Rocéphine', 'Ceftriaxone', '2 g IV', 'INJECTION', 'INTRAVEINEUSE', '1×/jour', 14, 'DEUXIEME_INTENTION', 'Formes compliquées ou résistantes'),
(397, 'Typhoïde', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '4×/jour', 7, 'SYMPTOMATIQUE', 'Fièvre typhoïde — antipyrétique'),
(398, 'Ulcère gastro-duodénal', 'Mopral', 'Oméprazole', '20-40 mg', 'CAPSULE', 'ORALE', '1×/jour à jeun', 28, 'PREMIERE_INTENTION', 'IPP — cicatrisation de l\'ulcère'),
(399, 'Ulcère gastro-duodénal', 'Clamoxyl', 'Amoxicilline', '1 g', 'COMPRIME', 'ORALE', '2×/jour', 14, 'ADJUVANT', 'Éradication H. pylori — triple thérapie'),
(400, 'Ulcère gastro-duodénal', 'Zéclar', 'Clarithromycine', '500 mg', 'COMPRIME', 'ORALE', '2×/jour', 14, 'ADJUVANT', 'Éradication H. pylori — triple thérapie'),
(401, 'Ulcère gastro-duodénal', 'Pepto-Bismol', 'Bismuth sous-salicylate', '525 mg', 'COMPRIME', 'ORALE', '4×/jour', 14, 'ADJUVANT', 'Quadrithérapie bismuthée — résistances'),
(402, 'Urticaire', 'Zyrtec', 'Cétirizine', '10 mg', 'COMPRIME', 'ORALE', '1×/jour', 30, 'PREMIERE_INTENTION', 'Antihistaminique H1 — urticaire aiguë ou chronique'),
(403, 'Urticaire', 'Clarityne', 'Loratadine', '10 mg', 'COMPRIME', 'ORALE', '1×/jour', 30, 'PREMIERE_INTENTION', 'Alternative non sédative'),
(404, 'Urticaire', 'Solupred', 'Prednisolone', '30-40 mg', 'COMPRIME', 'ORALE', '1×/matin', 5, 'DEUXIEME_INTENTION', 'Poussée sévère — traitement court'),
(405, 'Urticaire', 'Adrénaline Mylan', 'Adrénaline', '0.3-0.5 mg IM', 'INJECTION', 'INTRAMUSCULAIRE', 'En urgence', NULL, 'ADJUVANT', 'Urticaire géante + anaphylaxie'),
(406, 'Urétrite', 'Zithromax', 'Azithromycine', '1 g', 'COMPRIME', 'ORALE', 'Dose unique', 1, 'PREMIERE_INTENTION', 'Urétrite à Chlamydia — dose unique'),
(407, 'Urétrite', 'Vibramycine', 'Doxycycline', '100 mg', 'COMPRIME', 'ORALE', '2×/jour', 7, 'PREMIERE_INTENTION', 'Alternative à l\'azithromycine'),
(408, 'Urétrite', 'Rocéphine', 'Ceftriaxone', '500 mg IM', 'INJECTION', 'INTRAMUSCULAIRE', 'Dose unique', 1, 'PREMIERE_INTENTION', 'Urétrite gonococcique — associer à azithromycine'),
(409, 'VIH/SIDA', 'Truvada', 'Ténofovir + Emtricitabine', '200/245 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'Backbone du traitement antirétroviral'),
(410, 'VIH/SIDA', 'Sustiva', 'Éfavirenz', '600 mg', 'COMPRIME', 'ORALE', '1×/soir', 365, 'PREMIERE_INTENTION', 'INNTI — 3e agent du traitement ARV'),
(411, 'VIH/SIDA', 'Biktarvy', 'Bictégravir/TAF/FTC', '50/25/200 mg', 'COMPRIME', 'ORALE', '1×/jour', 365, 'PREMIERE_INTENTION', 'STR — traitement naïf de référence'),
(412, 'VIH/SIDA', 'Kaletra', 'Lopinavir/Ritonavir', '200/50 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'DEUXIEME_INTENTION', 'Protocole 2e ligne — ressources limitées'),
(413, 'Varicelle', 'Zovirax', 'Aciclovir', '800 mg', 'COMPRIME', 'ORALE', '5×/jour', 7, 'PREMIERE_INTENTION', 'Adulte ou immunodéprimé — commencer dans les 24 h'),
(414, 'Varicelle', 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 'ORALE', '4×/jour', 7, 'PREMIERE_INTENTION', 'Fièvre — ne pas donner aspirine (risque Reye)'),
(415, 'Varicelle', 'Atarax', 'Hydroxyzine', '25 mg', 'COMPRIME', 'ORALE', '3×/jour', 7, 'SYMPTOMATIQUE', 'Prurit — antihistaminique sédatif'),
(416, 'Verrue', 'Koloderm', 'Acide salicylique 16%', 'Application locale', 'SOLUTION', 'CUTANEE', '1×/jour', 56, 'PREMIERE_INTENTION', 'Traitement local — limer la verrue avant application'),
(417, 'Verrue', 'Aldara', 'Imiquimod 5%', 'Fine couche', 'CREME', 'CUTANEE', '3×/semaine (soir)', 84, 'DEUXIEME_INTENTION', 'Verrue plane ou génitale'),
(418, 'Vitiligo', 'Protopic', 'Tacrolimus 0.1%', 'Fine couche', 'CREME', 'CUTANEE', '2×/jour', 90, 'PREMIERE_INTENTION', 'Zones sensibles — visage et plis'),
(419, 'Vitiligo', 'Dermoval', 'Clobétasol 0.05%', 'Fine couche', 'CREME', 'CUTANEE', '1×/jour', 28, 'PREMIERE_INTENTION', 'Lésions récentes et limitées'),
(420, 'Vitiligo', 'Méladinine', 'Méthoxsalène (8-MOP)', '10-20 mg', 'COMPRIME', 'ORALE', '2 h avant UV', NULL, 'DEUXIEME_INTENTION', 'PUVA thérapie — suivi dermatologique requis'),
(421, 'Épilepsie', 'Dépakine', 'Valproate de sodium', '500-1500 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', 'Large spectre — épilepsie généralisée'),
(422, 'Épilepsie', 'Tegretol', 'Carbamazépine', '200-800 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', 'Crises partielles et généralisées'),
(423, 'Épilepsie', 'Keppra', 'Lévétiracétam', '250-1500 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'PREMIERE_INTENTION', 'Très bonne tolérance — epilepsies variées'),
(424, 'Épilepsie', 'Dilantin', 'Phénytoïne', '100-300 mg', 'COMPRIME', 'ORALE', '1-3×/jour', 365, 'DEUXIEME_INTENTION', 'Crises partielles — fenêtre thérapeutique étroite'),
(425, 'Épilepsie', 'Lamictal', 'Lamotrigine', '25-400 mg', 'COMPRIME', 'ORALE', '2×/jour', 365, 'DEUXIEME_INTENTION', 'Epilepsies partielles et généralisées — titration lente');

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
) ENGINE=InnoDB AUTO_INCREMENT=148 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `consultations`
--

INSERT INTO `consultations` (`consultation_id`, `nom_patient`, `patient_id`, `date_heure`, `motif`, `medecin_id`, `statut`, `created_at`) VALUES
(70, 'Lola LULU', 45, '2026-05-15 12:06:21', 'Consultation médicale', 15, 'en attente', '2026-05-15 11:06:21'),
(72, 'patient MOI', 47, '2026-05-15 12:55:25', 'écoulement nasal', 15, 'terminée', '2026-05-15 11:55:25'),
(74, 'KOLO YANICK', 49, '2026-05-15 13:34:05', 'Consultation médicale', NULL, 'en attente', '2026-05-15 12:34:05'),
(75, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:00:51', 'Malaises ', 15, 'terminée', '2026-05-15 14:00:50'),
(76, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:39:21', 'Consultation médicale', 15, 'en attente', '2026-05-15 14:39:20'),
(77, 'Mathieux  AHOUANNOU', 50, '2026-05-15 15:39:49', 'Consultation médicale', 15, 'en attente', '2026-05-15 14:39:49'),
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
(90, 'KOLO YANICK', 49, '2026-05-15 16:59:05', 'Consultation médicale', 15, 'en attente', '2026-05-15 15:59:04'),
(91, 'KOLO YANICK', 49, '2026-05-16 17:45:03', 'Consultation médicale', 15, 'en attente', '2026-05-16 16:45:03'),
(92, 'Jen-Luc MELENCHON', 64, '2026-05-16 18:31:28', 'Consultation médicale', 15, 'en attente', '2026-05-16 17:31:27'),
(93, 'Patien TEST', 65, '2026-05-17 01:36:55', 'Consultation médicale', 15, 'en attente', '2026-05-17 00:36:55'),
(94, 'Patien TEST', 65, '2026-05-17 02:04:17', 'Consultation médicale', 15, 'en attente', '2026-05-17 01:04:16'),
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
(114, 'Yanick M\'POLO', 67, '2026-05-25 20:24:27', 'Consultation médicale', NULL, 'en attente', '2026-05-25 19:24:26'),
(115, 'Yanick M\'POLO', 67, '2026-05-25 20:25:44', 'Consultation médicale', NULL, 'en attente', '2026-05-25 19:25:44'),
(116, 'Yanick M\'POLO', 67, '2026-05-25 20:33:51', 'Consultation médicale', 15, 'en attente', '2026-05-25 19:33:51'),
(117, 'Yanick M\'POLO', 67, '2026-05-25 21:43:29', 'Consultation médicale', 15, 'en attente', '2026-05-25 20:43:29'),
(118, 'Yanick M\'POLO', 67, '2026-05-25 22:00:59', 'Consultation médicale', 15, 'en attente', '2026-05-25 21:00:58'),
(119, 'liee au sexe CONSULT', 69, '2026-05-25 23:57:51', 'Consultation médicale', 15, 'en attente', '2026-05-25 22:57:50'),
(120, 'Jaan MARKOV', 70, '2026-05-25 23:58:13', 'Consultation médicale', 15, 'terminée', '2026-05-25 22:58:12'),
(121, 'Yanick M\'POLO', 67, '2026-05-26 00:16:46', 'Consultation médicale', 15, 'terminée', '2026-05-25 23:16:45'),
(122, 'Jean-luc MARTISE', 72, '2026-05-26 01:34:21', 'malaises ', 15, 'terminée', '2026-05-26 00:34:21'),
(123, 'Yanick M\'POLO', 67, '2026-05-26 01:52:23', 'Malisse importante', 15, 'terminée', '2026-05-26 00:52:22'),
(124, 'Yanick M\'POLO', 67, '2026-05-27 01:25:05', 'Consultation médicale', 15, 'en attente', '2026-05-27 00:25:05'),
(125, 'Yanick M\'POLO', 67, '2026-05-27 02:21:56', 'Consultation médicale', 15, 'terminée', '2026-05-27 01:21:56'),
(126, 'test TESTE', 73, '2026-05-27 16:24:01', 'Consultation médicale', 15, 'en attente', '2026-05-27 15:24:00'),
(127, 'test TESTE', 74, '2026-05-27 16:24:47', 'Consultation médicale', 15, 'en attente', '2026-05-27 15:24:46'),
(128, 'Patien TEST', 65, '2026-05-27 17:20:32', 'Consultation médicale', 15, 'terminée', '2026-05-27 16:20:31'),
(129, 'KOLO YANICK', 49, '2026-05-27 18:46:50', 'Consultation médicale', 15, 'terminée', '2026-05-27 17:46:50'),
(130, 'Cushing1 PATIENT', 75, '2026-05-27 22:35:48', 'Prise de poids', 15, 'terminée', '2026-05-27 21:35:47'),
(131, 'Cushing1 PATIENT', 75, '2026-05-27 23:05:30', 'Consultation médicale', 15, 'terminée', '2026-05-27 22:05:29'),
(132, 'Teste PALUDIME1', 76, '2026-05-28 02:13:52', 'palu', 15, 'terminée', '2026-05-28 01:13:51'),
(133, 'liee au sexe CONSULT', 69, '2026-05-28 19:43:06', 'Consultation médicale', 15, 'terminée', '2026-05-28 18:43:06'),
(134, 'Patient CUSHING2', 77, '2026-05-29 03:33:19', 'teste de cushing', 15, 'terminée', '2026-05-29 02:33:18'),
(135, 'Rénale INSUFFS', 78, '2026-05-29 09:52:15', 'Teste pour l\'insuffisance rénale', 15, 'terminée', '2026-05-29 08:52:15'),
(136, 'Rénale LITHIASE', 79, '2026-05-29 10:13:33', 'Teste lithiase renal', 15, 'terminée', '2026-05-29 09:13:33'),
(137, 'test GRIPPE2', 80, '2026-06-01 15:28:10', 'deuxième test pour la grippe', 15, 'en attente', '2026-06-01 14:28:10'),
(138, 'Test MÉNINGITE1', 81, '2026-06-01 17:10:16', 'Premier test pour la Méningite', 15, 'en attente', '2026-06-01 16:10:15'),
(139, 'Richelle AMAHAYA', 68, '2026-06-02 14:19:33', 'Consultation médicale', 15, 'en attente', '2026-06-02 13:19:33'),
(140, 'Patient CUSHING2', 77, '2026-06-02 16:45:12', 'Consultation médicale', 15, 'en attente', '2026-06-02 15:45:12'),
(146, 'Patient CUSHING2', 87, '2026-06-02 17:13:19', '', NULL, 'terminée', '2026-06-02 16:13:19'),
(147, 'Patient CUSHING2', 87, '2026-06-02 17:21:39', 'Consultation médicale', 15, 'terminée', '2026-06-02 16:21:38');

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
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `diagnostics`
--

INSERT INTO `diagnostics` (`diagnostic_id`, `consultation_id`, `analyse_ia_id`, `medecin_id`, `dossier_id`, `code_icd10`, `nom_maladie`, `description`, `certitude`, `statut`, `severite`, `justification`, `date_validation`) VALUES
(18, 72, 17, NULL, 19, NULL, 'Grippe', 'Validation : CONFIRMÉ. Suggestion IA : Grippe (7.1%). Notes : ', 0.070752, 'CONFIRMÉ', NULL, NULL, '2026-05-15'),
(19, 75, 18, NULL, 20, NULL, 'Hyperthyroïdie', 'Validation : CONFIRMÉ. Suggestion IA : Hyperthyroïdie (4.4%). Notes : ', 0.0442395, 'CONFIRMÉ', NULL, NULL, '2026-05-15'),
(20, 79, 20, NULL, 20, NULL, 'Sclérose latérale amyotrophique', 'Validation : CONFIRMÉ. Suggestion IA : Sclérose latérale amyotrophique (10.9%). Notes : ', 0.108591, 'CONFIRMÉ', NULL, NULL, '2026-05-15'),
(21, 101, 21, NULL, 21, NULL, 'Sclérose latérale amyotrophique', 'Validation : CONFIRMÉ. Suggestion IA : Sclérose latérale amyotrophique (10.0%). Notes : ', 0.0997547, 'CONFIRMÉ', NULL, NULL, '2026-05-17'),
(22, 104, 22, NULL, 22, NULL, 'Hypertrophie bénigne de prostate', 'Validation : CONFIRMÉ. Suggestion IA : Hypertrophie bénigne de prostate (5.5%). Notes : ', 0.0545706, 'CONFIRMÉ', NULL, NULL, '2026-05-17'),
(23, 103, 23, NULL, 19, NULL, 'Influenza A/B', 'Validation : CONFIRMÉ. Suggestion IA : Influenza A/B (25.6%). Notes : ', 0.256061, 'CONFIRMÉ', NULL, NULL, '2026-05-17'),
(24, 111, 25, NULL, 23, NULL, 'Paludisme grave (Neuropaludisme)', 'Validation : REJETÉ. Suggestion IA : Gonorrhée (3.1%). Notes : ', 0.0314286, 'REJETÉ', NULL, NULL, '2026-05-22'),
(25, 110, 27, NULL, 24, NULL, 'Constipation chronique', 'Validation : CONFIRMÉ. Suggestion IA : Constipation chronique (7.1%). Notes : ', 0.0713933, 'CONFIRMÉ', NULL, NULL, '2026-05-24'),
(26, 120, 29, NULL, 25, NULL, 'Polyglobulie', 'Validation : CONFIRMÉ. Suggestion IA : Polyglobulie (3.1%). Notes : ', 0.0312289, 'CONFIRMÉ', NULL, NULL, '2026-05-26'),
(27, 122, 30, NULL, 26, NULL, 'Polyglobulie', 'Validation : CONFIRMÉ. Suggestion IA : Polyglobulie (3.1%). Notes : ', 0.0312289, 'CONFIRMÉ', NULL, NULL, '2026-05-26'),
(28, 123, 31, NULL, 27, NULL, 'Sclérose latérale amyotrophique', 'Validation : CONFIRMÉ. Suggestion IA : Sclérose latérale amyotrophique (4.1%). Notes : ', 0.0405852, 'CONFIRMÉ', NULL, NULL, '2026-05-26'),
(29, 121, 32, NULL, 27, NULL, 'Acromégalie', 'Validation : CONFIRMÉ. Suggestion IA : Acromégalie (6.4%). Notes : ', 0.064085, 'CONFIRMÉ', NULL, NULL, '2026-05-27'),
(30, 125, 33, NULL, 27, NULL, 'Acromégalie', 'Validation : CONFIRMÉ. Suggestion IA : Acromégalie (6.4%). Notes : ', 0.064085, 'CONFIRMÉ', NULL, NULL, '2026-05-27'),
(31, 128, 35, NULL, 28, NULL, 'Hypertension', 'Validation : REJETÉ. Suggestion IA : Glomérulonéphrite (14.9%). Notes : ', 0.149111, 'REJETÉ', NULL, NULL, '2026-05-27'),
(32, 128, 36, NULL, 28, NULL, 'Hypertension', 'Validation : REJETÉ. Suggestion IA : Glomérulonéphrite (14.9%). Notes : ', 0.149111, 'REJETÉ', NULL, NULL, '2026-05-27'),
(33, 128, 37, NULL, 28, NULL, 'Hypertension', 'Validation : REJETÉ. Suggestion IA : Glomérulonéphrite (14.9%). Notes : ', 0.149111, 'REJETÉ', NULL, NULL, '2026-05-27'),
(34, 130, 39, NULL, 29, NULL, 'Syndrome de Cushing', 'Validation : CONFIRMÉ. Suggestion IA : Syndrome de Cushing (11.0%). Notes : ', 0.109624, 'CONFIRMÉ', NULL, NULL, '2026-05-27'),
(35, 132, 41, NULL, 30, NULL, 'Paludisme', 'Validation : CONFIRMÉ. Suggestion IA : Paludisme (39.3%). Notes : ', 0.392634, 'CONFIRMÉ', NULL, NULL, '2026-05-28'),
(36, 129, 43, NULL, 22, NULL, 'Insuffisance rénale chronique', 'Validation : CONFIRMÉ. Suggestion IA : Insuffisance rénale chronique (37.2%). Notes : ', 0.372395, 'CONFIRMÉ', NULL, NULL, '2026-05-28'),
(37, 131, 44, NULL, 29, NULL, 'Syndrome de Cushing', 'Validation : CONFIRMÉ. Suggestion IA : Syndrome de Cushing (75.7%). Notes : ', 0.757081, 'CONFIRMÉ', NULL, NULL, '2026-05-29'),
(38, 134, 45, NULL, 32, NULL, 'Syndrome de Cushing', 'Validation : CONFIRMÉ. Suggestion IA : Syndrome de Cushing (74.1%). Notes : ', 0.741167, 'CONFIRMÉ', NULL, NULL, '2026-05-29'),
(39, 132, 46, NULL, 30, NULL, 'Paludisme', 'Validation : CONFIRMÉ. Suggestion IA : Paludisme (39.3%). Notes : ', 0.392634, 'CONFIRMÉ', NULL, NULL, '2026-05-29'),
(40, 135, 47, NULL, 33, NULL, 'Insuffisance rénale chronique', 'Validation : CONFIRMÉ. Suggestion IA : Insuffisance rénale chronique (50.2%). Notes : ', 0.501712, 'CONFIRMÉ', NULL, NULL, '2026-05-29'),
(41, 136, 49, NULL, 34, NULL, 'Lithiase rénale', 'Validation : CONFIRMÉ. Suggestion IA : Lithiase rénale (47.1%). Notes : ', 0.471104, 'CONFIRMÉ', NULL, NULL, '2026-05-29'),
(42, 133, 50, NULL, 23, NULL, 'Épilepsie', 'Validation : CONFIRMÉ. Suggestion IA : Épilepsie (62.7%). Notes : ', 0.627434, 'CONFIRMÉ', 'GRAVE', NULL, '2026-05-29'),
(48, 146, 62, NULL, 43, NULL, 'Syndrome de Cushing', 'Validation : CONFIRMÉ. Suggestion IA : Syndrome de Cushing (79.0%). Notes : ', 0.789934, 'CONFIRMÉ', 'CRITIQUE', NULL, '2026-06-02'),
(49, 147, 64, NULL, 43, NULL, 'Syndrome de Cushing', 'Validation : CONFIRMÉ. Suggestion IA : Syndrome de Cushing (79.0%). Notes : ', 0.789934, 'CONFIRMÉ', 'CRITIQUE', NULL, '2026-06-02');

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
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `dossiers_medicaux`
--

INSERT INTO `dossiers_medicaux` (`dossier_id`, `patient_id`, `numero_dossier`, `antecedents_familiaux`, `antecedents_personnels`, `allergies`, `date_creation`) VALUES
(19, 47, 'DM-20260515132024-47', NULL, NULL, NULL, '2026-05-15 12:20:24'),
(20, 50, 'DM-20260515151815-50', NULL, NULL, NULL, '2026-05-15 14:18:15'),
(21, 66, 'DM-20260517152723-66', NULL, NULL, NULL, '2026-05-17 14:27:23'),
(22, 49, 'DM-20260517175305-49', NULL, NULL, NULL, '2026-05-17 16:53:05'),
(23, 69, 'DM-20260522131628-69', NULL, NULL, NULL, '2026-05-22 12:16:28'),
(24, 68, 'DM-20260524180855-68', NULL, NULL, NULL, '2026-05-24 17:08:55'),
(25, 70, 'DM-20260526005735-70', NULL, NULL, NULL, '2026-05-25 23:57:35'),
(26, 72, 'DM-20260526015005-72', NULL, NULL, NULL, '2026-05-26 00:50:05'),
(27, 67, 'DM-20260526020113-67', NULL, NULL, NULL, '2026-05-26 01:01:13'),
(28, 65, 'DM-20260527180345-65', NULL, NULL, NULL, '2026-05-27 17:03:45'),
(29, 75, 'DM-20260527231517-75', NULL, NULL, NULL, '2026-05-27 22:15:17'),
(30, 76, 'DM-20260528022039-76', NULL, NULL, NULL, '2026-05-28 01:20:39'),
(31, 45, 'DM-20260528131706-45', NULL, NULL, NULL, '2026-05-28 12:17:06'),
(32, 77, 'DM-20260529033318-77', NULL, NULL, NULL, '2026-05-29 02:33:18'),
(33, 78, 'DM-20260529095215-78', NULL, NULL, NULL, '2026-05-29 08:52:15'),
(34, 79, 'DM-20260529101333-79', NULL, NULL, NULL, '2026-05-29 09:13:33'),
(35, 74, 'DM-20260529173609-74', NULL, NULL, NULL, '2026-05-29 16:36:09'),
(36, 80, 'DM-20260601152810-80', NULL, NULL, NULL, '2026-06-01 14:28:10'),
(37, 81, 'DM-20260601171015-81', NULL, NULL, NULL, '2026-06-01 16:10:15'),
(43, 87, 'DM-20260602171319-87', NULL, NULL, NULL, '2026-06-02 16:13:19');

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
) ENGINE=InnoDB AUTO_INCREMENT=132 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `examens`
--

INSERT INTO `examens` (`examen_id`, `consultation_id`, `type`, `nom`, `description`, `resultats`, `valeur_numerique`, `unite_mesure`, `statut`, `date_examen`, `is_suggested`) VALUES
(31, 72, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-15', 1),
(32, 72, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-15', 1),
(33, 75, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-15', 1),
(34, 75, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-15', 1),
(35, 79, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-15', 1),
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
(55, 123, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-26', 1),
(56, 121, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-27', 1),
(57, 121, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-27', 1),
(58, 125, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-27', 1),
(59, 125, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-27', 1),
(60, 128, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-27', 1),
(61, 128, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-27', 1),
(62, 128, 'BIOLOGIE', 'Créatinine', NULL, NULL, 1.2, 'mg/dL', 'REALISE', '2026-05-27', 0),
(63, 128, 'BIOLOGIE', 'Potassium', NULL, NULL, 4.2, 'mEq/L', 'REALISE', '2026-05-27', 0),
(64, 128, 'BIOLOGIE', 'Glucose à jeun', NULL, NULL, 105, 'mg/dL', 'REALISE', '2026-05-27', 0),
(65, 128, 'BIOLOGIE', 'Cholestérol total', NULL, NULL, 220, 'mg/dL', 'REALISE', '2026-05-27', 0),
(66, 128, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-27', 1),
(67, 128, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-27', 1),
(68, 128, 'BIOLOGIE', 'Créatinine', NULL, NULL, 1.2, 'mg/dL', 'REALISE', '2026-05-27', 0),
(69, 128, 'BIOLOGIE', 'Potassium', NULL, NULL, 4.2, 'mEq/L', 'REALISE', '2026-05-27', 0),
(70, 128, 'BIOLOGIE', 'Glucose à jeun', NULL, NULL, 105, 'mg/dL', 'REALISE', '2026-05-27', 0),
(71, 128, 'BIOLOGIE', 'Cholestérol total', NULL, NULL, 220, 'mg/dL', 'REALISE', '2026-05-27', 0),
(72, 128, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-27', 1),
(73, 128, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-27', 1),
(74, 128, 'BIOLOGIE', 'Créatinine', NULL, NULL, 1.2, 'mg/dL', 'REALISE', '2026-05-27', 0),
(75, 128, 'BIOLOGIE', 'Potassium', NULL, NULL, 4.2, 'mEq/L', 'REALISE', '2026-05-27', 0),
(76, 128, 'BIOLOGIE', 'Glucose à jeun', NULL, NULL, 105, 'mg/dL', 'REALISE', '2026-05-27', 0),
(77, 128, 'BIOLOGIE', 'Cholestérol total', NULL, NULL, 220, 'mg/dL', 'REALISE', '2026-05-27', 0),
(78, 130, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-27', 1),
(79, 130, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-27', 1),
(80, 130, 'BIOLOGIE', 'Glucose à jeun', NULL, NULL, 145, 'mg/dL', 'REALISE', '2026-05-27', 0),
(81, 130, 'BIOLOGIE', 'Potassium', NULL, NULL, 4, 'mEq/L', 'REALISE', '2026-05-27', 0),
(82, 130, 'BIOLOGIE', 'Sodium', NULL, NULL, 140, 'mEq/L', 'REALISE', '2026-05-27', 0),
(83, 132, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-28', 1),
(84, 132, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-28', 1),
(85, 132, 'BIOLOGIE', 'Globules Rouges', 'Anémie hémolytique', NULL, 4.5, 'M/µL', 'REALISE', '2026-05-28', 1),
(86, 132, 'BIOLOGIE', 'Plaquettes', 'Thrombocytopénie', NULL, 250, 'K/µL', 'REALISE', '2026-05-28', 1),
(87, 132, 'BIOLOGIE', 'Bilirubine totale', 'Hémolyse', NULL, 10, 'mg/dL', 'REALISE', '2026-05-28', 1),
(88, 132, 'BIOLOGIE', 'ALT/SGPT', 'Atteinte hépatique', NULL, 35, 'U/L', 'REALISE', '2026-05-28', 1),
(89, 129, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-28', 1),
(90, 129, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-28', 1),
(91, 131, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-29', 1),
(92, 131, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-29', 1),
(93, 134, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-29', 1),
(94, 134, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-29', 1),
(95, 132, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-28', 1),
(96, 132, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-28', 1),
(97, 132, 'BIOLOGIE', 'Globules Rouges', 'Anémie hémolytique', NULL, 4.5, 'M/µL', 'REALISE', '2026-05-28', 1),
(98, 132, 'BIOLOGIE', 'Plaquettes', 'Thrombocytopénie', NULL, 250, 'K/µL', 'REALISE', '2026-05-28', 1),
(99, 132, 'BIOLOGIE', 'Bilirubine totale', 'Hémolyse', NULL, 10, 'mg/dL', 'REALISE', '2026-05-28', 1),
(100, 132, 'BIOLOGIE', 'ALT/SGPT', 'Atteinte hépatique', NULL, 35, 'U/L', 'REALISE', '2026-05-28', 1),
(101, 135, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-29', 1),
(102, 135, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-29', 1),
(103, 135, 'BIOLOGIE', 'Créatinine', NULL, NULL, 4.8, 'µmol/L', 'REALISE', '2026-05-29', 0),
(104, 135, 'BIOLOGIE', 'Urée', NULL, NULL, 85, 'mg/dL', 'REALISE', '2026-05-29', 0),
(105, 135, 'BIOLOGIE', 'TFG', NULL, NULL, 14, 'mL/min/1.73m²', 'REALISE', '2026-05-29', 0),
(106, 135, 'BIOLOGIE', 'Potassium', NULL, NULL, 5.8, 'mEq/L', 'REALISE', '2026-05-29', 0),
(107, 136, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-29', 1),
(108, 136, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-29', 1),
(109, 136, 'BIOLOGIE', 'Sodium', 'Déshydratation', NULL, 140, 'mEq/L', 'REALISE', '2026-05-29', 1),
(110, 136, 'BIOLOGIE', 'Potassium', 'Hypokaliémie', NULL, 4, 'mEq/L', 'REALISE', '2026-05-29', 1),
(111, 136, 'BIOLOGIE', 'Créatinine', 'Insuffisance rénale aiguë', NULL, 80, 'µmol/L', 'REALISE', '2026-05-29', 1),
(112, 136, 'BIOLOGIE', 'Urée', 'Déshydratation', NULL, 30, 'mg/dL', 'REALISE', '2026-05-29', 1),
(113, 136, 'BIOLOGIE', 'Acide urique', NULL, NULL, 9.2, 'mg/dL', 'REALISE', '2026-05-29', 0),
(114, 136, 'BIOLOGIE', 'Calcium', NULL, NULL, 11.2, 'mg/dL', 'REALISE', '2026-05-29', 0),
(115, 136, 'BIOLOGIE', 'Créatinine', NULL, NULL, 1.3, 'µmol/L', 'REALISE', '2026-05-29', 0),
(116, 133, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-05-29', 1),
(117, 133, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-05-29', 1),
(128, 146, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-06-02', 1),
(129, 146, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-06-02', 1),
(130, 147, 'BIOLOGIE', 'Hémoglobine', 'Bilan sanguin de base', NULL, 13, 'g/dL', 'REALISE', '2026-06-02', 1),
(131, 147, 'BIOLOGIE', 'CRP', 'Marqueur inflammatoire', NULL, 5, 'mg/L', 'REALISE', '2026-06-02', 1);

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
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `historique_prediction`
--

INSERT INTO `historique_prediction` (`id`, `patient_id`, `consultation_id`, `predicted_disease`, `confidence`, `confidence_level`, `prediction_probabilities`, `feature_values`, `top_features`, `model_version`, `model_accuracy`, `is_validated`, `validated_by`, `validated_at`, `validation_notes`, `actual_disease`, `created_at`, `updated_at`) VALUES
(1, 47, 103, 'Influenza A/B', 0.256061, 'LOW', '{\"Grippe\": 0.085, \"Pneumonie\": 0.06613095238095239, \"Influenza A/B\": 0.25606060606060604}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Influenza A/B', '2026-05-17 18:24:06', '2026-05-17 18:24:06'),
(2, 69, 111, 'Gonorrhée', 0.0314286, 'LOW', '{\"Gonorrhée\": 0.03142857142857143, \"Molluscum contagiosum\": 0.02571428571428571, \"Sclérose latérale amyotrophique\": 0.02571428571428571}', NULL, NULL, 'RandomForest_v1.0', NULL, -1, NULL, NULL, NULL, 'Paludisme grave (Neuropaludisme)', '2026-05-22 12:16:29', '2026-05-22 12:16:29'),
(3, 68, 110, 'Constipation chronique', 0.0713933, 'LOW', '{\"Cholangite\": 0.05000109422758147, \"Stéatose hépatique\": 0.06128041094836493, \"Constipation chronique\": 0.07139331372376556}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Constipation chronique', '2026-05-24 17:08:55', '2026-05-24 17:08:55'),
(4, 70, 120, 'Polyglobulie', 0.0312289, 'LOW', '{\"Acné\": 0.02753902202364849, \"Verrue\": 0.02809486034343077, \"Polyglobulie\": 0.031228855309197823}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Polyglobulie', '2026-05-25 23:57:36', '2026-05-25 23:57:36'),
(5, 72, 122, 'Polyglobulie', 0.0312289, 'LOW', '{\"Acné\": 0.02753902202364849, \"Verrue\": 0.02809486034343076, \"Polyglobulie\": 0.031228855309197823}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Polyglobulie', '2026-05-26 00:50:05', '2026-05-26 00:50:05'),
(6, 67, 123, 'Sclérose latérale amyotrophique', 0.0405852, 'LOW', '{\"Acné\": 0.0302629346501863, \"Verrue\": 0.032468983970916854, \"Sclérose latérale amyotrophique\": 0.040585240033154425}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Sclérose latérale amyotrophique', '2026-05-26 01:01:13', '2026-05-26 01:01:13'),
(7, 67, 121, 'Acromégalie', 0.064085, 'LOW', '{\"Vitiligo\": 0.025205953856608385, \"Acromégalie\": 0.06408499208396393, \"Polyglobulie\": 0.02858320601591161}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Acromégalie', '2026-05-27 01:10:27', '2026-05-27 01:10:27'),
(8, 67, 125, 'Acromégalie', 0.064085, 'LOW', '{\"Vitiligo\": 0.025205953856608378, \"Acromégalie\": 0.06408499208396394, \"Polyglobulie\": 0.028583206015911612}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Acromégalie', '2026-05-27 01:23:10', '2026-05-27 01:23:10'),
(9, 65, 128, 'Glomérulonéphrite', 0.149111, 'LOW', '{\"Acromégalie\": 0.07500107902168024, \"Apnée du sommeil\": 0.1018429731211223, \"Glomérulonéphrite\": 0.14911090083457887}', NULL, NULL, 'RandomForest_v1.0', NULL, -1, NULL, NULL, NULL, 'Hypertension', '2026-05-27 17:03:45', '2026-05-27 17:03:45'),
(10, 65, 128, 'Glomérulonéphrite', 0.149111, 'LOW', '{\"Acromégalie\": 0.07500107902168024, \"Apnée du sommeil\": 0.1018429731211223, \"Glomérulonéphrite\": 0.14911090083457887}', NULL, NULL, 'RandomForest_v1.0', NULL, -1, NULL, NULL, NULL, 'Hypertension', '2026-05-27 17:46:40', '2026-05-27 17:46:40'),
(11, 65, 128, 'Glomérulonéphrite', 0.149111, 'LOW', '{\"Acromégalie\": 0.07500107902168024, \"Apnée du sommeil\": 0.1018429731211223, \"Glomérulonéphrite\": 0.14911090083457887}', NULL, NULL, 'RandomForest_v1.0', NULL, -1, NULL, NULL, NULL, 'Hypertension', '2026-05-27 17:46:41', '2026-05-27 17:46:41'),
(12, 75, 130, 'Syndrome de Cushing', 0.109624, 'LOW', '{\"Diabète Type 1\": 0.09634804413703796, \"Syndrome de Cushing\": 0.10962362643990496, \"Insuffisance rénale chronique\": 0.08062081006288765}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Syndrome de Cushing', '2026-05-27 22:15:18', '2026-05-27 22:15:18'),
(13, 76, 132, 'Paludisme', 0.392634, 'LOW', '{\"Migraine\": 0.10197306079599404, \"Paludisme\": 0.39263430406279337, \"Salmonellose\": 0.06038013176992073}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Paludisme', '2026-05-28 01:20:40', '2026-05-28 01:20:40'),
(14, 49, 129, 'Insuffisance rénale chronique', 0.372395, 'LOW', '{\"Hépatite B\": 0.023748800645971905, \"Insuffisance rénale aiguë\": 0.3706713954977588, \"Insuffisance rénale chronique\": 0.37239544850007394}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Insuffisance rénale chronique', '2026-05-28 18:38:49', '2026-05-28 18:38:49'),
(15, 75, 131, 'Syndrome de Cushing', 0.757081, 'HIGH', '{\"Acromégalie\": 0.09596878097632636, \"Glomérulonéphrite\": 0.021151266282605424, \"Syndrome de Cushing\": 0.7570805610071193}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Syndrome de Cushing', '2026-05-29 03:00:15', '2026-05-29 03:00:15'),
(16, 77, 134, 'Syndrome de Cushing', 0.741167, 'MEDIUM', '{\"Acromégalie\": 0.0970216606798666, \"Glomérulonéphrite\": 0.021553645640243677, \"Syndrome de Cushing\": 0.7411671283007506}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Syndrome de Cushing', '2026-05-29 03:04:52', '2026-05-29 03:04:52'),
(17, 76, 132, 'Paludisme', 0.392634, 'LOW', '{\"Migraine\": 0.10197306079599404, \"Paludisme\": 0.39263430406279337, \"Salmonellose\": 0.06038013176992073}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Paludisme', '2026-05-29 03:14:56', '2026-05-29 03:14:56'),
(18, 78, 135, 'Insuffisance rénale chronique', 0.501712, 'MEDIUM', '{\"Hépatite B\": 0.0016734366512378795, \"Insuffisance rénale aiguë\": 0.4813041101577114, \"Insuffisance rénale chronique\": 0.501712388103611}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Insuffisance rénale chronique', '2026-05-29 08:59:40', '2026-05-29 08:59:40'),
(19, 79, 136, 'Lithiase rénale', 0.471104, 'LOW', '{\"Migraine\": 0.047737380012017286, \"Salmonellose\": 0.03902082042771041, \"Lithiase rénale\": 0.4711043571812232}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Lithiase rénale', '2026-05-29 09:19:08', '2026-05-29 09:19:08'),
(20, 69, 133, 'Épilepsie', 0.627434, 'MEDIUM', '{\"Acné\": 0.014343481639457494, \"Alzheimer\": 0.04338343374649372, \"Épilepsie\": 0.627434094740523}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Épilepsie', '2026-05-29 16:28:46', '2026-05-29 16:28:46'),
(26, 87, 146, 'Syndrome de Cushing', 0.789934, 'HIGH', '{\"Acromégalie\": 0.05257138606127155, \"Diabète Type 2\": 0.009952522468256586, \"Syndrome de Cushing\": 0.7899337799750235}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Syndrome de Cushing', '2026-06-02 16:13:19', '2026-06-02 16:13:19'),
(27, 87, 147, 'Syndrome de Cushing', 0.789934, 'HIGH', '{\"Acromégalie\": 0.052571386061271555, \"Diabète Type 2\": 0.009952522468256588, \"Syndrome de Cushing\": 0.7899337799750235}', NULL, NULL, 'RandomForest_v1.0', NULL, 1, NULL, NULL, NULL, 'Syndrome de Cushing', '2026-06-02 17:53:26', '2026-06-02 17:53:26');

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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
(14, 'PETIT', 'Thomas André', 'Medecin General', '+229 96 00 10 99', 1, '2026-05-07 06:36:27', NULL),
(15, 'DOSSOU', 'Marie-Claire Afi', 'Médecin Général', '00000000', 1, '2026-05-09 14:07:51', NULL),
(16, 'LEFEBVRE', 'Jean-Baptiste', 'Médecin Général', '00000000', 1, '2026-05-09 14:07:51', NULL),
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
  `forme` enum('COMPRIME','INJECTION','SIROP','CREME','COLLYRE','POUDRE','PATCH','SPRAY','CAPSULE','SOLUTION') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'COMPRIME',
  `quantite` int DEFAULT NULL,
  `frequence` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `voie_administration` enum('ORALE','INTRAVEINEUSE','CUTANEE','INTRAMUSCULAIRE','OPHTALMIQUE','NASALE','INHALATION','SOUS-CUTANEE','RECTALE') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'ORALE',
  `duree_jours` int DEFAULT NULL,
  PRIMARY KEY (`medicament_id`),
  KEY `ordonnance_id` (`ordonnance_id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `medicaments`
--

INSERT INTO `medicaments` (`medicament_id`, `ordonnance_id`, `nom_commercial`, `denomination_commune`, `dosage`, `forme`, `quantite`, `frequence`, `voie_administration`, `duree_jours`) VALUES
(1, 1, 'Sandostatine LAR', 'Octréotide LP', '20-30 mg IM/mois', 'INJECTION', 1, '1×/mois', 'INTRAMUSCULAIRE', 365),
(2, 1, 'Dostinex', 'Cabergoline', '0.5-3.5 mg/sem', 'COMPRIME', 1, '2×/semaine', 'ORALE', 365),
(3, 1, 'Somavert', 'Pégvisomant', '10-30 mg/j SC', 'INJECTION', 1, '1×/jour', 'SOUS-CUTANEE', 365),
(4, 1, 'Somatuline Autogel', 'Lanréotide', '90-120 mg SC/4 sem', 'INJECTION', 1, '1×/4 semaines', 'SOUS-CUTANEE', 365),
(5, 2, 'Amlor', 'Amlodipine', '5-10 mg', 'COMPRIME', 1, '1×/jour', 'ORALE', 365),
(6, 2, 'Cozaar', 'Losartan', '25-100 mg', 'COMPRIME', 1, '1×/jour', 'ORALE', 365),
(7, 2, 'Triatec', 'Ramipril', '2.5-10 mg', 'COMPRIME', 1, '1×/jour', 'ORALE', 365),
(8, 3, 'Amlor', 'Amlodipine', '5-10 mg', 'COMPRIME', 1, '1×/jour', 'ORALE', 365),
(9, 3, 'Cozaar', 'Losartan', '25-100 mg', 'COMPRIME', 1, '1×/jour', 'ORALE', 365),
(10, 3, 'Triatec', 'Ramipril', '2.5-10 mg', 'COMPRIME', 1, '1×/jour', 'ORALE', 365),
(11, 4, 'Métopirone', 'Métyrapone', '250-4000 mg/j', 'CAPSULE', 1, '4×/jour', 'ORALE', 30),
(12, 4, 'Korlym', 'Mifépristone', '300-1200 mg', 'COMPRIME', 1, '1×/jour', 'ORALE', 30),
(13, 4, 'Nizoral', 'Kétoconazole', '200-1200 mg', 'COMPRIME', 1, '2-3×/jour', 'ORALE', 30),
(14, 5, 'Métopirone', 'Métyrapone', '250-4000 mg/j', 'CAPSULE', 1, '4×/jour', 'ORALE', 30),
(15, 5, 'Korlym', 'Mifépristone', '300-1200 mg', 'COMPRIME', 1, '1×/jour', 'ORALE', 30),
(16, 5, 'Nizoral', 'Kétoconazole', '200-1200 mg', 'COMPRIME', 1, '2-3×/jour', 'ORALE', 30),
(17, 6, 'Artésunate IV', 'Artésunate', '2.4 mg/kg IV', 'INJECTION', 1, 'H0, H12, H24 puis 1×/jour', 'INTRAVEINEUSE', 7),
(18, 6, 'Coartem', 'Artéméther + Luméfantrine', '4 cp par prise', 'COMPRIME', 1, '2×/jour', 'ORALE', 3),
(19, 6, 'Quinimax', 'Quinine', '8 mg/kg toutes 8 h IV', 'INJECTION', 1, '3×/jour', 'INTRAVEINEUSE', 7),
(20, 6, 'Doliprane', 'Paracétamol', '1000 mg', 'COMPRIME', 1, '4×/jour', 'ORALE', 5),
(21, 7, 'Amlor', 'Amlodipine', '5-10 mg', 'COMPRIME', 1, '1×/jour', 'ORALE', 365),
(22, 7, 'Triatec', 'Ramipril', '2.5-5 mg', 'COMPRIME', 1, '1×/jour', 'ORALE', 365),
(23, 7, 'NeoRecormon', 'Érythropoïétine bêta', '2000-10000 UI', 'INJECTION', 1, '2-3×/semaine', 'SOUS-CUTANEE', 365),
(24, 7, 'Renvela', 'Sévélamer', '800 mg', 'COMPRIME', 1, '3×/jour', 'ORALE', 365),
(25, 8, 'Dépakine', 'Valproate de sodium', '500-1500 mg', 'COMPRIME', 1, '2×/jour', 'ORALE', 365),
(26, 8, 'Keppra', 'Lévétiracétam', '250-1500 mg', 'COMPRIME', 1, '2×/jour', 'ORALE', 365),
(27, 8, 'Tegretol', 'Carbamazépine', '200-800 mg', 'COMPRIME', 1, '2×/jour', 'ORALE', 365),
(28, 8, 'Lamictal', 'Lamotrigine', '25-400 mg', 'COMPRIME', 1, '2×/jour', 'ORALE', 365),
(29, 8, 'Dilantin', 'Phénytoïne', '100-300 mg', 'COMPRIME', 1, '1-3×/jour', 'ORALE', 365);

-- --------------------------------------------------------

--
-- Structure de la table `ordonnances`
--

DROP TABLE IF EXISTS `ordonnances`;
CREATE TABLE IF NOT EXISTS `ordonnances` (
  `ordonnance_id` int NOT NULL AUTO_INCREMENT,
  `traitement_id` int NOT NULL,
  `medecin_id` int DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `ordonnances`
--

INSERT INTO `ordonnances` (`ordonnance_id`, `traitement_id`, `medecin_id`, `patient_id`, `dossier_id`, `posologie_generale`, `date_emission`, `renouvelable`) VALUES
(1, 1, 15, 67, 27, 'Voir médicaments prescrits', '2026-05-27 01:23:10', 0),
(2, 2, 15, 65, 28, 'Voir médicaments prescrits', '2026-05-27 17:46:39', 0),
(3, 3, 15, 65, 28, 'Voir médicaments prescrits', '2026-05-27 17:46:40', 0),
(4, 4, 15, 75, 29, 'Voir médicaments prescrits', '2026-05-29 03:00:14', 0),
(5, 5, 15, 77, 32, 'Voir médicaments prescrits', '2026-05-29 03:04:52', 0),
(6, 6, 15, 76, 30, 'Voir médicaments prescrits', '2026-05-29 03:14:55', 0),
(7, 7, 15, 78, 33, 'Voir médicaments prescrits', '2026-05-29 08:59:39', 0),
(8, 8, 15, 69, 23, 'Voir médicaments prescrits', '2026-05-29 16:28:46', 0);

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
) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `patients`
--

INSERT INTO `patients` (`patient_id`, `nom`, `prenoms`, `date_naissance`, `sexe`, `groupe_sanguin`, `telephone`, `email`, `adresse`, `created_at`) VALUES
(45, 'LULU', 'Lola', '2004-02-14', 'F', NULL, NULL, NULL, NULL, '2026-05-15 11:06:21'),
(47, 'MOI', 'patient', '1990-07-03', 'M', 'O-', '0155554444', NULL, NULL, '2026-05-15 11:55:25'),
(49, 'YANICK', 'KOLO', '1900-01-01', 'M', NULL, NULL, NULL, NULL, '2026-05-15 12:34:05'),
(50, 'AHOUANNOU', 'Mathieux ', '2010-01-15', 'M', 'AB+', NULL, 'matieux@gmail.com', NULL, '2026-05-15 14:00:50'),
(64, 'MELENCHON', 'Jen-Luc', '2018-06-17', 'M', 'A-', '2344567789', NULL, NULL, '2026-05-16 17:31:27'),
(65, 'TEST', 'Patien', '2010-01-01', 'F', NULL, NULL, NULL, NULL, '2026-05-17 00:36:55'),
(66, 'PATIENT', 'NouveauConsult', '1990-02-12', 'M', NULL, NULL, NULL, NULL, '2026-05-17 13:09:46'),
(67, 'M\'POLO', 'Yanick', '2001-01-01', 'M', NULL, NULL, NULL, NULL, '2026-05-19 12:13:16'),
(68, 'AMAHAYA', 'Richelle', '2005-01-01', 'F', NULL, NULL, NULL, NULL, '2026-05-19 16:10:04'),
(69, 'CONSULT', 'liee au sexe', '2001-01-01', 'F', NULL, NULL, NULL, NULL, '2026-05-22 10:50:45'),
(70, 'MARKOV', 'Jaan', '2004-01-01', 'M', NULL, NULL, NULL, NULL, '2026-05-23 21:16:21'),
(72, 'MARTISE', 'Jean-luc', '2009-03-26', 'M', 'B+', NULL, NULL, NULL, '2026-05-26 00:34:21'),
(73, 'TESTE', 'test', '1959-01-01', 'M', NULL, NULL, NULL, NULL, '2026-05-27 15:24:00'),
(74, 'TESTE', 'test', '2016-01-01', 'M', NULL, NULL, NULL, NULL, '2026-05-27 15:24:46'),
(75, 'PATIENT', 'Cushing1', '1988-01-01', 'F', NULL, NULL, NULL, NULL, '2026-05-27 21:35:47'),
(76, 'PALUDIME1', 'Teste', '1998-01-01', 'M', NULL, NULL, NULL, NULL, '2026-05-28 01:13:51'),
(77, 'CUSHING2', 'Patient', '2018-06-29', 'M', 'AB+', NULL, NULL, NULL, '2026-05-29 02:33:18'),
(78, 'INSUFFS', 'Rénale', '2022-02-28', 'M', 'B+', NULL, NULL, NULL, '2026-05-29 08:52:15'),
(79, 'LITHIASE', 'Rénale', '1988-01-01', 'M', NULL, NULL, NULL, NULL, '2026-05-29 09:13:33'),
(80, 'GRIPPE2', 'test', '2008-01-01', 'M', NULL, NULL, NULL, NULL, '2026-06-01 14:28:10'),
(81, 'MÉNINGITE1', 'Test', '1977-01-01', 'M', NULL, NULL, NULL, NULL, '2026-06-01 16:10:15'),
(87, 'CUSHING2', 'Patient', '2018-06-29', 'M', 'AB+', NULL, NULL, NULL, '2026-06-02 16:13:19');

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
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `signes_vitaux`
--

INSERT INTO `signes_vitaux` (`signes_vitaux_id`, `consultation_id`, `infirmier_id`, `date_enregistrement`, `tension_systolique`, `tension_diastolique`, `frequence_cardiaque`, `temperature`, `frequence_respiratoire`, `saturation_oxygene`, `poids`, `taille`, `imc`, `glycemie`) VALUES
(43, 72, NULL, '2026-05-15 11:58:49', 120, 80, 70, 38, 16, 98, 70, 170, 24.2, NULL),
(44, 75, NULL, '2026-05-15 14:03:29', 120, 80, 70, 37, 16, 98, 70, 170, 24.2, NULL),
(45, 79, NULL, '2026-05-15 14:45:17', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(46, 101, NULL, '2026-05-17 13:10:30', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(47, 103, NULL, '2026-05-17 16:44:04', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(48, 104, NULL, '2026-05-17 16:48:47', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(49, 111, NULL, '2026-05-22 12:16:28', 120, 80, 70, 37, 16, 98, 70, 178, 22.1, NULL),
(50, 110, NULL, '2026-05-24 17:08:55', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(51, 120, NULL, '2026-05-25 23:57:35', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(52, 122, NULL, '2026-05-26 00:35:23', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(53, 123, NULL, '2026-05-26 00:53:13', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(54, 121, NULL, '2026-05-27 01:10:26', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(55, 125, NULL, '2026-05-27 01:22:12', 120, 80, 70, 37, 16, 98, NULL, NULL, NULL, NULL),
(56, 128, NULL, '2026-05-27 17:03:45', 165, 100, 82, 37, 16, 97, 92, 174.7, 30.1, NULL),
(57, 130, NULL, '2026-05-27 22:15:17', 155, 95, 88, 37, 16, 97, 90, 162, 34.3, NULL),
(58, 132, NULL, '2026-05-28 01:20:39', 100, 62, 115, 40.5, 22, 94, 65, 170, 22.5, NULL),
(59, 129, NULL, '2026-05-28 18:38:49', 158, 96, 80, 36.8, 18, 96, 80, 170, 27.7, NULL),
(60, 131, NULL, '2026-05-29 01:52:21', 155, 95, 88, 37, 16, 97, 90, 162, 34.3, NULL),
(61, 134, NULL, '2026-05-29 02:51:05', 155, 95, 88, 37, 16, 97, 90, 162, 34.3, NULL),
(62, 135, NULL, '2026-05-29 08:56:08', 158, 96, 80, 36.8, 18, 96, 80, 169.9, 27.7, NULL),
(63, 136, NULL, '2026-05-29 09:19:07', 108, 82, 70, 37.8, 20, 98, 80, 175, 26.1, NULL),
(64, 133, NULL, '2026-05-29 16:27:29', 122, 75, 88, 37, 16, 97, 68, 172, 23, NULL),
(70, 146, NULL, '2026-06-02 16:13:19', 155, 95, 88, 37, 16, 97, 90, 162, 34.3, NULL),
(71, 147, NULL, '2026-06-02 17:53:26', 155, 95, 88, 37, 16, 97, 90, 162, 34.3, NULL);

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
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `suivis`
--

INSERT INTO `suivis` (`suivi_id`, `patient_id`, `medecin_id`, `consultation_id`, `diagnostic_id`, `traitement_id`, `dossier_id`, `numero_suivi`, `date_suivi`, `etat_general`, `amelioration`, `pourcentage_amelioration`, `adherence_traitement`, `statut`, `prochaine_consultation`) VALUES
(1, 47, 15, 103, 23, NULL, 19, 'SV-20260517192406066-103', '2026-05-17', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(2, 69, 15, 111, NULL, NULL, 23, 'SV-20260522131628640-111', '2026-05-22', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(3, 68, 15, 110, NULL, NULL, 24, 'SV-20260524180855282-110', '2026-05-24', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(4, 70, 15, 120, NULL, NULL, 25, 'SV-20260526005736006-120', '2026-05-26', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(5, 72, 15, 122, 27, NULL, 26, 'SV-20260526015005448-122', '2026-05-26', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(6, 67, 15, 123, 28, NULL, 27, 'SV-20260526020113334-123', '2026-05-26', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(7, 67, 15, 121, NULL, NULL, 27, 'SV-20260527021026751-121', '2026-05-27', NULL, NULL, NULL, NULL, 'EN_COURS', '2026-05-30'),
(8, 67, 15, 125, 30, 1, 27, 'SV-20260527022310076-125', '2026-05-27', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(9, 65, 15, 128, NULL, NULL, 28, 'SV-20260527180345356-128', '2026-05-27', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(10, 65, 15, 128, 32, 2, 28, 'SV-20260527184639849-128', '2026-05-27', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(11, 65, 15, 128, 33, 3, 28, 'SV-20260527184640801-128', '2026-05-27', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(12, 75, 15, 130, NULL, NULL, 29, 'SV-20260527231517944-130', '2026-05-27', NULL, NULL, NULL, NULL, 'EN_COURS', '2026-05-30'),
(13, 76, 15, 132, NULL, NULL, 30, 'SV-20260528022039796-132', '2026-05-28', NULL, NULL, NULL, NULL, 'EN_COURS', '2026-05-31'),
(14, 49, 15, 129, NULL, NULL, 22, 'SV-20260528193849283-129', '2026-05-28', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(15, 75, 15, 131, 37, 4, 29, 'SV-20260529040014981-131', '2026-05-29', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(16, 77, 15, 134, 38, 5, 32, 'SV-20260529040452207-134', '2026-05-29', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(17, 76, 15, 132, 39, 6, 30, 'SV-20260529041455633-132', '2026-05-29', NULL, NULL, NULL, NULL, 'EN_COURS', '2026-05-31'),
(18, 78, 15, 135, 40, 7, 33, 'SV-20260529095939770-135', '2026-05-29', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(19, 79, 15, 136, NULL, NULL, 34, 'SV-20260529101907663-136', '2026-05-29', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(20, 69, 15, 133, 42, 8, 23, 'SV-20260529172846113-133', '2026-05-29', NULL, NULL, NULL, NULL, 'EN_COURS', NULL),
(21, 87, 15, 147, NULL, NULL, 43, 'SV-20260602185326312-147', '2026-06-02', NULL, NULL, NULL, NULL, 'EN_COURS', NULL);

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
) ENGINE=InnoDB AUTO_INCREMENT=232 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `symptomes`
--

INSERT INTO `symptomes` (`symptome_id`, `consultation_id`, `nom`, `description`, `severite`, `date_apparition`, `duree_jours`, `zone_atteinte`, `frequence`) VALUES
(93, 72, 'Congestion nasale', NULL, 'SEVERE', NULL, 1, NULL, NULL),
(94, 72, 'Écoulement nasal', NULL, 'MODERE', NULL, 1, NULL, NULL),
(95, 72, 'Douleurs musculaires', NULL, 'MODERE', NULL, 1, NULL, NULL),
(96, 75, 'Fatigue', NULL, 'SEVERE', NULL, 4, NULL, NULL),
(97, 75, 'Insomnie', NULL, 'LEGER', NULL, 3, NULL, NULL),
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
(132, 123, 'Atrophie musculaire', NULL, 'MODERE', NULL, 1, NULL, NULL),
(133, 125, 'Adénopathie', NULL, 'MODERE', NULL, 1, NULL, NULL),
(134, 125, 'Agrandissement des mains pieds', NULL, 'MODERE', NULL, 1, NULL, NULL),
(135, 128, 'Maux de tête', NULL, 'MODERE', NULL, 87, NULL, NULL),
(136, 128, 'Maux de tête matinaux', NULL, 'MODERE', NULL, 90, NULL, NULL),
(137, 128, 'Hypertension', NULL, 'MODERE', NULL, 90, NULL, NULL),
(138, 128, 'Vertiges', NULL, 'MODERE', NULL, 90, NULL, NULL),
(139, 128, 'Palpitations', NULL, 'MODERE', NULL, 90, NULL, NULL),
(140, 130, 'Perte de poids', NULL, 'MODERE', NULL, 180, NULL, NULL),
(141, 130, 'Grossissement du visage', NULL, 'MODERE', NULL, 180, NULL, NULL),
(142, 130, 'Hypertension', NULL, 'MODERE', NULL, 180, NULL, NULL),
(143, 130, 'Vergetures', NULL, 'MODERE', NULL, 180, NULL, NULL),
(144, 130, 'Fatigue', NULL, 'MODERE', NULL, 180, NULL, NULL),
(145, 130, 'Infections fréquentes', NULL, 'MODERE', NULL, 180, NULL, NULL),
(146, 132, 'Fièvre intermittente', NULL, 'SEVERE', NULL, 5, NULL, NULL),
(147, 132, 'Frissons', NULL, 'SEVERE', NULL, 5, NULL, NULL),
(148, 132, 'Sueurs', NULL, 'SEVERE', NULL, 5, NULL, NULL),
(149, 132, 'Maux de tête sévère', NULL, 'SEVERE', NULL, 5, NULL, NULL),
(150, 132, 'Douleurs musculaires', NULL, 'SEVERE', NULL, 5, NULL, NULL),
(151, 132, 'Nausées', NULL, 'SEVERE', NULL, 5, NULL, NULL),
(152, 132, 'Vomissements', NULL, 'SEVERE', NULL, 5, NULL, NULL),
(153, 129, 'Fatigue', NULL, 'SEVERE', NULL, 180, NULL, NULL),
(154, 129, 'Nausées', NULL, 'MODERE', NULL, 90, NULL, NULL),
(155, 129, 'Perte d\'appétit', NULL, 'MODERE', NULL, 90, NULL, NULL),
(156, 129, 'Gonflement des pieds', NULL, 'MODERE', NULL, 120, NULL, NULL),
(157, 129, 'Oligurie ou polyurie', NULL, 'MODERE', NULL, 180, NULL, NULL),
(158, 129, 'Prurit', NULL, 'MODERE', NULL, 1, NULL, NULL),
(159, 129, 'Démangeaisons', NULL, 'MODERE', NULL, 90, NULL, NULL),
(160, 131, 'Prise de poids rapide', NULL, 'SEVERE', NULL, 180, NULL, NULL),
(161, 131, 'Grossissement du visage', NULL, 'MODERE', NULL, 120, NULL, NULL),
(162, 131, 'Hypertension', NULL, 'MODERE', NULL, 180, NULL, NULL),
(163, 131, 'Vergetures', NULL, 'MODERE', NULL, 90, NULL, NULL),
(164, 131, 'Fatigue', NULL, 'MODERE', NULL, 180, NULL, NULL),
(165, 131, 'Infections fréquentes', NULL, 'MODERE', NULL, 1, NULL, NULL),
(166, 134, 'Prise de poids rapide', NULL, 'SEVERE', NULL, 180, NULL, NULL),
(167, 134, 'Grossissement du visage', NULL, 'MODERE', NULL, 120, NULL, NULL),
(168, 134, 'Hypertension', NULL, 'MODERE', NULL, 180, NULL, NULL),
(169, 134, 'Vergetures', NULL, 'MODERE', NULL, 90, NULL, NULL),
(170, 134, 'Fatigue', NULL, 'MODERE', NULL, 180, NULL, NULL),
(171, 134, 'Infections fréquentes', NULL, 'LEGER', NULL, 90, NULL, NULL),
(172, 135, 'Fatigue', NULL, 'SEVERE', NULL, 180, NULL, NULL),
(173, 135, 'Nausées', NULL, 'MODERE', NULL, 90, NULL, NULL),
(174, 135, 'Perte d\'appétit', NULL, 'MODERE', NULL, 90, NULL, NULL),
(175, 135, 'Gonflement des chevilles', NULL, 'MODERE', NULL, 120, NULL, NULL),
(176, 135, 'Gonflement des pieds', NULL, 'MODERE', NULL, 120, NULL, NULL),
(177, 135, 'Oligurie ou polyurie', NULL, 'MODERE', NULL, 180, NULL, NULL),
(178, 135, 'Démangeaisons', NULL, 'MODERE', NULL, 90, NULL, NULL),
(179, 136, 'Douleur lombaire', NULL, 'SEVERE', NULL, 2, NULL, NULL),
(180, 136, 'Douleur colique intense', NULL, 'SEVERE', NULL, 2, NULL, NULL),
(181, 136, 'Hématurie', NULL, 'MODERE', NULL, 2, NULL, NULL),
(182, 136, 'Nausées', NULL, 'MODERE', NULL, 2, NULL, NULL),
(183, 136, 'Vomissements', NULL, 'MODERE', NULL, 1, NULL, NULL),
(184, 136, 'Urination fréquente', NULL, 'LEGER', NULL, 2, NULL, NULL),
(185, 133, 'Convulsions', NULL, 'SEVERE', NULL, 7, NULL, NULL),
(186, 133, 'Perte de conscience', NULL, 'SEVERE', NULL, 2, NULL, NULL),
(187, 133, 'Fatigue post-critique', NULL, 'MODERE', NULL, 7, NULL, NULL),
(188, 133, 'Confusion', NULL, 'MODERE', NULL, 2, NULL, NULL),
(189, 133, 'Troubles cognitifs', NULL, 'LEGER', NULL, 7, NULL, NULL),
(220, 146, 'Prise de poids rapide', NULL, 'SEVERE', NULL, 180, NULL, NULL),
(221, 146, 'Grossissement du visage', NULL, 'MODERE', NULL, 120, NULL, NULL),
(222, 146, 'Hypertension', NULL, 'MODERE', NULL, 180, NULL, NULL),
(223, 146, 'Vergetures', NULL, 'MODERE', NULL, 90, NULL, NULL),
(224, 146, 'Fatigue', NULL, 'MODERE', NULL, 180, NULL, NULL),
(225, 146, 'Infections fréquentes', NULL, 'LEGER', NULL, 90, NULL, NULL),
(226, 147, 'Prise de poids rapide', NULL, 'SEVERE', NULL, 180, NULL, NULL),
(227, 147, 'Grossissement du visage', NULL, 'MODERE', NULL, 120, NULL, NULL),
(228, 147, 'Hypertension', NULL, 'MODERE', NULL, 120, NULL, NULL),
(229, 147, 'Vergetures', NULL, 'MODERE', NULL, 90, NULL, NULL),
(230, 147, 'Fatigue', NULL, 'MODERE', NULL, 180, NULL, NULL),
(231, 147, 'Infections fréquentes', NULL, 'MODERE', NULL, 90, NULL, NULL);

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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `traitements`
--

INSERT INTO `traitements` (`traitement_id`, `diagnostic_id`, `nom_traitement`, `description`, `type`, `duree_jours`, `date_debut`, `date_fin`, `statut`, `objective_therapeutique`) VALUES
(1, 30, 'Traitement — Acromégalie', NULL, 'MEDICAMENTEUX', NULL, '2026-05-27', NULL, 'PRESCRIT', NULL),
(2, 32, 'Traitement — Hypertension', NULL, 'MEDICAMENTEUX', NULL, '2026-05-27', NULL, 'PRESCRIT', NULL),
(3, 33, 'Traitement — Hypertension', NULL, 'MEDICAMENTEUX', NULL, '2026-05-27', NULL, 'PRESCRIT', NULL),
(4, 37, 'Traitement — Syndrome de Cushing', NULL, 'MEDICAMENTEUX', NULL, '2026-05-29', NULL, 'PRESCRIT', NULL),
(5, 38, 'Traitement — Syndrome de Cushing', NULL, 'MEDICAMENTEUX', NULL, '2026-05-29', NULL, 'PRESCRIT', NULL),
(6, 39, 'Traitement — Paludisme', NULL, 'MEDICAMENTEUX', NULL, '2026-05-29', NULL, 'PRESCRIT', NULL),
(7, 40, 'Traitement — Insuffisance rénale chronique', NULL, 'MEDICAMENTEUX', NULL, '2026-05-29', NULL, 'PRESCRIT', NULL),
(8, 42, 'Traitement — Épilepsie', NULL, 'MEDICAMENTEUX', NULL, '2026-05-29', NULL, 'PRESCRIT', NULL);

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
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `utilisateurs`
--

INSERT INTO `utilisateurs` (`utilisateur_id`, `nom`, `prenoms`, `email`, `mot_de_passe`, `role`, `actif`, `created_at`, `last_login`) VALUES
(1, 'ADMIN', 'Super', 'admin@santeplus.bj', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'admin', 1, '2026-05-02 20:29:04', '2026-06-02 16:19:33'),
(5, 'KOFFI', 'Awa Sylvie', 'awa.koffi@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:12:16', NULL),
(6, 'MENSAH', 'Kokou David', 'kokou.mensah@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:12:16', NULL),
(7, 'AGBODJAN', 'Edem Patricia', 'edem.agbodjan@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:12:16', '2026-05-15 14:06:46'),
(8, 'TOSSOU', 'Yao Emmanuel', 'yao.tossou@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:12:16', NULL),
(9, 'AHOUANSOU', 'Gérard Koffi', 'gerard.ahouansou@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', '2026-05-09 16:52:22'),
(10, 'DOSSOU', 'Marie-Claire Afi', 'marie.dossou@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'medecin', 1, '2026-05-02 23:33:49', '2026-06-03 14:17:56'),
(11, 'LEFEBVRE', 'Jean-Baptiste', 'jean.lefebvre@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'medecin', 1, '2026-05-02 23:33:49', '2026-05-17 23:34:39'),
(12, 'BERNARD', 'Sophie Marie', 'sophie.bernard@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'medecin', 1, '2026-05-02 23:33:49', NULL),
(13, 'PETIT', 'Thomas André', 'thomas.petit@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'medecin', 1, '2026-05-02 23:33:49', NULL),
(14, 'KOUASSI', 'Aya', 'aya.kouassi@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', '2026-05-29 17:22:51'),
(15, 'MENSAH', 'Kofi', 'kofi.mensah@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', NULL),
(16, 'DIALLO', 'Fatoumata', 'fatoumata.diallo@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', NULL),
(17, 'TRAORE', 'Moussa', 'moussa.traore@sante.com', '$2b$12$vj9R8ecGO9H6EpUK7GRgcO8EOljZpRPxQNyqBx3nPvJT.et70nwSW', 'infirmier', 1, '2026-05-02 23:33:49', NULL),
(18, 'M\'POLO', 'Yanick', 'yanickmpolo@gasasad.bj', '$2b$12$pEC30rX9D4QRXY9mkH6iTudj6HOqA6PHs0e9HJwC6PZSlJtMTX6O6', 'medecin', 1, '2026-05-09 19:21:06', '2026-05-17 17:50:20'),
(19, 'AMAHAYA', 'Richelle', 'richelleamahaya@gmail.com', '$2b$12$J8KypAInV/RzkIgevQxm.umXRXEc41m5t3OIbHIK8fM9LWfyYiZtO', 'medecin', 1, '2026-05-19 16:37:29', '2026-05-26 16:46:20');

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `analyses_ia`
--
ALTER TABLE `analyses_ia`
  ADD CONSTRAINT `fk_anal_cons` FOREIGN KEY (`consultation_id`) REFERENCES `consultations` (`consultation_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `consultations`
--
ALTER TABLE `consultations`
  ADD CONSTRAINT `fk_cons_medecin` FOREIGN KEY (`medecin_id`) REFERENCES `medecins` (`medecin_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_cons_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Contraintes pour la table `diagnostics`
--
ALTER TABLE `diagnostics`
  ADD CONSTRAINT `fk_diag_analyse` FOREIGN KEY (`analyse_ia_id`) REFERENCES `analyses_ia` (`analyse_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_diag_cons` FOREIGN KEY (`consultation_id`) REFERENCES `consultations` (`consultation_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_diag_dossier` FOREIGN KEY (`dossier_id`) REFERENCES `dossiers_medicaux` (`dossier_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_diag_medecin` FOREIGN KEY (`medecin_id`) REFERENCES `medecins` (`medecin_id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Contraintes pour la table `dossiers_medicaux`
--
ALTER TABLE `dossiers_medicaux`
  ADD CONSTRAINT `fk_doss_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `examens`
--
ALTER TABLE `examens`
  ADD CONSTRAINT `fk_exam_cons` FOREIGN KEY (`consultation_id`) REFERENCES `consultations` (`consultation_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `historique_prediction`
--
ALTER TABLE `historique_prediction`
  ADD CONSTRAINT `fk_hist_cons` FOREIGN KEY (`consultation_id`) REFERENCES `consultations` (`consultation_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_hist_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `medicaments`
--
ALTER TABLE `medicaments`
  ADD CONSTRAINT `fk_med_ord` FOREIGN KEY (`ordonnance_id`) REFERENCES `ordonnances` (`ordonnance_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `ordonnances`
--
ALTER TABLE `ordonnances`
  ADD CONSTRAINT `fk_ord_dossier` FOREIGN KEY (`dossier_id`) REFERENCES `dossiers_medicaux` (`dossier_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_ord_medecin` FOREIGN KEY (`medecin_id`) REFERENCES `medecins` (`medecin_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_ord_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_ord_trait` FOREIGN KEY (`traitement_id`) REFERENCES `traitements` (`traitement_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `signes_vitaux`
--
ALTER TABLE `signes_vitaux`
  ADD CONSTRAINT `fk_sv_cons` FOREIGN KEY (`consultation_id`) REFERENCES `consultations` (`consultation_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `suivis`
--
ALTER TABLE `suivis`
  ADD CONSTRAINT `fk_suiv_cons` FOREIGN KEY (`consultation_id`) REFERENCES `consultations` (`consultation_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_suiv_diag` FOREIGN KEY (`diagnostic_id`) REFERENCES `diagnostics` (`diagnostic_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_suiv_dossier` FOREIGN KEY (`dossier_id`) REFERENCES `dossiers_medicaux` (`dossier_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_suiv_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_suiv_trait` FOREIGN KEY (`traitement_id`) REFERENCES `traitements` (`traitement_id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Contraintes pour la table `symptomes`
--
ALTER TABLE `symptomes`
  ADD CONSTRAINT `fk_symp_cons` FOREIGN KEY (`consultation_id`) REFERENCES `consultations` (`consultation_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `traitements`
--
ALTER TABLE `traitements`
  ADD CONSTRAINT `fk_trait_diag` FOREIGN KEY (`diagnostic_id`) REFERENCES `diagnostics` (`diagnostic_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
