-- ============================================================
-- Catalogue de référence des médicaments par maladie (121 maladies)
-- Table : medicaments  (≠ catalogue_medicaments qui est réservé aux prescriptions)
-- À exécuter sur la base sante_plus_ia
-- ============================================================

CREATE TABLE IF NOT EXISTS `medicaments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `maladie` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nom_commercial` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `denomination_commune` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dosage_standard` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `forme` enum('COMPRIME','INJECTION','SIROP','CREME','COLLYRE','POUDRE','PATCH','SPRAY','CAPSULE','SOLUTION') COLLATE utf8mb4_unicode_ci DEFAULT 'COMPRIME',
  `voie_administration` enum('ORALE','INTRAVEINEUSE','CUTANEE','INTRAMUSCULAIRE','OPHTALMIQUE','NASALE','INHALATION','SOUS-CUTANEE','RECTALE') COLLATE utf8mb4_unicode_ci DEFAULT 'ORALE',
  `frequence_habituelle` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `duree_standard_jours` int DEFAULT NULL,
  `categorie` enum('PREMIERE_INTENTION','DEUXIEME_INTENTION','ADJUVANT','SYMPTOMATIQUE') COLLATE utf8mb4_unicode_ci DEFAULT 'PREMIERE_INTENTION',
  `notes` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `idx_maladie` (`maladie`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Vider la table avant ré-insertion pour éviter les doublons
TRUNCATE TABLE `medicaments`;

-- ============================================================
-- INSERT: 121 maladies — ~3 à 5 médicaments par maladie
-- ============================================================

INSERT INTO `medicaments`
  (`maladie`,`nom_commercial`,`denomination_commune`,`dosage_standard`,`forme`,`voie_administration`,`frequence_habituelle`,`duree_standard_jours`,`categorie`,`notes`)
VALUES

-- Accident vasculaire cérébral
('Accident vasculaire cérébral','Aspirine UPSA','Acide acétylsalicylique','100 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Antiplaquettaire long terme'),
('Accident vasculaire cérébral','Actolyse','Alteplase (rtPA)','0.9 mg/kg IV','INJECTION','INTRAVEINEUSE','En une seule prise','1','PREMIERE_INTENTION','Thrombolyse — dans les 4h30 post-AVC ischémique'),
('Accident vasculaire cérébral','Plavix','Clopidogrel','75 mg','COMPRIME','ORALE','1×/jour','365','DEUXIEME_INTENTION','Association avec aspirine si nécessaire'),
('Accident vasculaire cérébral','Tahor','Atorvastatine','40-80 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Réduction du risque de récidive'),
('Accident vasculaire cérébral','Lisinopril Mylan','Lisinopril','5-10 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Contrôle tensionnel post-AVC'),

-- Acné
('Acné','Cutacnyl','Peroxyde de benzoyle','5%','CREME','CUTANEE','1×/jour','90','PREMIERE_INTENTION','Appliquer sur peau propre le soir'),
('Acné','Vibramycine','Doxycycline','100 mg','COMPRIME','ORALE','1×/jour','84','PREMIERE_INTENTION','Acné inflammatoire modérée à sévère'),
('Acné','Dalacin T','Clindamycine phosphate','1%','SOLUTION','CUTANEE','2×/jour','90','ADJUVANT','Application locale, éviter les muqueuses'),
('Acné','Roaccutane','Isotrétinoïne','0.5-1 mg/kg/j','CAPSULE','ORALE','2×/jour','180','DEUXIEME_INTENTION','Réservée aux formes sévères — surveillance hépatique'),
('Acné','Effederm','Trétinoïne','0.025%','CREME','CUTANEE','1×/soir','90','ADJUVANT','Éviter le soleil — photosensibilisant'),

-- Acromégalie
('Acromégalie','Sandostatine LAR','Octréotide LP','20-30 mg IM/mois','INJECTION','INTRAMUSCULAIRE','1×/mois','365','PREMIERE_INTENTION','Analogue de la somatostatine'),
('Acromégalie','Somatuline Autogel','Lanréotide','90-120 mg SC/4 sem','INJECTION','SOUS-CUTANEE','1×/4 semaines','365','PREMIERE_INTENTION','Alternative à l''octréotide'),
('Acromégalie','Dostinex','Cabergoline','0.5-3.5 mg/sem','COMPRIME','ORALE','2×/semaine','365','DEUXIEME_INTENTION','Agoniste dopaminergique'),
('Acromégalie','Somavert','Pégvisomant','10-30 mg/j SC','INJECTION','SOUS-CUTANEE','1×/jour','365','DEUXIEME_INTENTION','Antagoniste du récepteur GH — si autres traitements insuffisants'),

-- Alzheimer
('Alzheimer','Aricept','Donépézil','5-10 mg','COMPRIME','ORALE','1×/soir','365','PREMIERE_INTENTION','Inhibiteur de cholinestérase'),
('Alzheimer','Exelon','Rivastigmine','4.6-9.5 mg/24h','PATCH','CUTANEE','1 patch/jour','365','PREMIERE_INTENTION','Patch transcutané ou capsule orale'),
('Alzheimer','Reminyl','Galantamine','8-24 mg','COMPRIME','ORALE','2×/jour','365','PREMIERE_INTENTION','Inhibiteur de cholinestérase'),
('Alzheimer','Ebixa','Mémantine','5-20 mg','COMPRIME','ORALE','1×/jour','365','DEUXIEME_INTENTION','Antagoniste NMDA — stades modérés à sévères'),

-- Angine de poitrine
('Angine de poitrine','Nitroquick','Nitroglycérine sublinguale','0.4 mg','COMPRIME','ORALE','Au besoin',NULL,'PREMIERE_INTENTION','Crise angineuse aiguë — max 3 prises / 15 min'),
('Angine de poitrine','Lopressor','Métoprolol','25-100 mg','COMPRIME','ORALE','2×/jour','365','PREMIERE_INTENTION','Bêtabloquant anti-angineux'),
('Angine de poitrine','Aspirine UPSA','Acide acétylsalicylique','75-100 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Antiplaquettaire de fond'),
('Angine de poitrine','Tahor','Atorvastatine','40 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Réduction du LDL'),
('Angine de poitrine','Adalate LP','Nifédipine LP','30-60 mg','COMPRIME','ORALE','1×/jour','365','DEUXIEME_INTENTION','Inhibiteur calcique si bêtabloquant contre-indiqué'),

-- Angine streptococcique
('Angine streptococcique','Clamoxyl','Amoxicilline','500 mg','COMPRIME','ORALE','3×/jour','6','PREMIERE_INTENTION','Traitement de référence des angines streptococciques'),
('Angine streptococcique','Pénicilline V','Phénoxyméthylpénicilline','1 M UI','COMPRIME','ORALE','3×/jour','10','PREMIERE_INTENTION','Alternative à l''amoxicilline'),
('Angine streptococcique','Zithromax','Azithromycine','500 mg J1 puis 250 mg','COMPRIME','ORALE','1×/jour','5','DEUXIEME_INTENTION','Si allergie à la pénicilline'),
('Angine streptococcique','Paracétamol EG','Paracétamol','1000 mg','COMPRIME','ORALE','3×/jour','6','SYMPTOMATIQUE','Antalgique et antipyrétique'),

-- Anémie aplasique
('Anémie aplasique','Néoral','Ciclosporine','3-6 mg/kg/j','CAPSULE','ORALE','2×/jour','180','PREMIERE_INTENTION','Immunosuppresseur — surveillance rénale'),
('Anémie aplasique','Thymoglobuline','Globuline antithymocyte','2.5-3.75 mg/kg/j','INJECTION','INTRAVEINEUSE','1×/jour','5','PREMIERE_INTENTION','Immunosuppression intensive'),
('Anémie aplasique','Revolade','Eltrombopag','50-150 mg','COMPRIME','ORALE','1×/jour','180','ADJUVANT','Stimulant de la thrombopoïèse'),
('Anémie aplasique','Neorecormon','Érythropoïétine (EPO)','2000-4000 UI','INJECTION','SOUS-CUTANEE','3×/semaine','90','ADJUVANT','Stimulation érythropoïèse'),

-- Anémie ferriprive
('Anémie ferriprive','Ferrograd','Sulfate ferreux','325 mg','COMPRIME','ORALE','1×/jour','90','PREMIERE_INTENTION','Prendre à jeun ou avec jus d''orange'),
('Anémie ferriprive','Tardyferon','Sulfate ferreux LP','80 mg (élément Fe)','COMPRIME','ORALE','1-2×/jour','90','PREMIERE_INTENTION','Libération prolongée — meilleure tolérance digestive'),
('Anémie ferriprive','Venofer','Fer saccharose IV','200 mg','INJECTION','INTRAVEINEUSE','1×/semaine','4','DEUXIEME_INTENTION','Si intolérance orale ou malabsorption'),
('Anémie ferriprive','Acide folique Mylan','Acide folique','5 mg','COMPRIME','ORALE','1×/jour','90','ADJUVANT','Supplément en acide folique'),

-- Anémie hémolytique
('Anémie hemolytique','Solupred','Prednisolone','1 mg/kg/j','COMPRIME','ORALE','1×/matin','30','PREMIERE_INTENTION','Anémie hémolytique auto-immune'),
('Anémie hemolytique','Acide folique Mylan','Acide folique','5 mg','COMPRIME','ORALE','1×/jour','90','ADJUVANT','Prévention de la carence en folates'),
('Anémie hemolytique','Mabthera','Rituximab','375 mg/m²','INJECTION','INTRAVEINEUSE','1×/semaine','28','DEUXIEME_INTENTION','Formes réfractaires aux corticoïdes'),

-- Apnée du sommeil
('Apnée du sommeil','Modiodal','Modafinil','100-200 mg','COMPRIME','ORALE','1×/matin','365','SYMPTOMATIQUE','Somnolence diurne résiduelle — pas un traitement curatif'),
('Apnée du sommeil','Fluticasone Mylan','Fluticasone nasale','50 µg/pulv.','SPRAY','NASALE','2×/jour','30','ADJUVANT','Si rhinite associée aggravant l''apnée'),

-- Arthrite rhumatoïde
('Arthrite rhumatoïde','Novatrex','Méthotrexate','7.5-25 mg/sem','COMPRIME','ORALE','1×/semaine','365','PREMIERE_INTENTION','DMARDs de référence — supplémentation folates nécessaire'),
('Arthrite rhumatoïde','Plaquenil','Hydroxychloroquine','200-400 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Surveillance ophtalmologique annuelle'),
('Arthrite rhumatoïde','Solupred','Prednisolone','5-10 mg','COMPRIME','ORALE','1×/matin','30','ADJUVANT','Traitement de courte durée en poussée'),
('Arthrite rhumatoïde','Remicade','Infliximab','3-5 mg/kg','INJECTION','INTRAVEINEUSE','S0, S2, S6 puis /8 sem','365','DEUXIEME_INTENTION','Anti-TNFα — bilan pré-thérapeutique requis'),
('Arthrite rhumatoïde','Arava','Léflunomide','20 mg','COMPRIME','ORALE','1×/jour','365','DEUXIEME_INTENTION','Alternative au méthotrexate'),

-- Arythmie cardiaque
('Arythmie cardiaque','Cordarone','Amiodarone','200 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Surveillance thyroïdienne et pulmonaire'),
('Arythmie cardiaque','Digoxine Nativelle','Digoxine','0.125-0.25 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Contrôle de la fréquence en FA'),
('Arythmie cardiaque','Lopressor','Métoprolol','25-100 mg','COMPRIME','ORALE','2×/jour','365','ADJUVANT','Ralentisseur de fréquence'),
('Arythmie cardiaque','Xarelto','Rivaroxaban','20 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Anticoagulation en cas de FA'),

-- Asthme
('Asthme','Ventoline','Salbutamol','100 µg/bouffée','SPRAY','INHALATION','Au besoin (max 6×/j)',NULL,'PREMIERE_INTENTION','Bronchodilatateur d''action rapide — crise aiguë'),
('Asthme','Flixotide','Fluticasone','125-250 µg','SPRAY','INHALATION','2×/jour','365','PREMIERE_INTENTION','Corticoïde inhalé de fond'),
('Asthme','Atrovent','Ipratropium','20 µg/bouffée','SPRAY','INHALATION','3-4×/jour','14','ADJUVANT','Anticholinergique — exacerbations sévères'),
('Asthme','Singulair','Montélukast','10 mg','COMPRIME','ORALE','1×/soir','365','DEUXIEME_INTENTION','Antagoniste des leucotriènes'),
('Asthme','Solupred','Prednisolone','40-60 mg','COMPRIME','ORALE','1×/matin','5','SYMPTOMATIQUE','Exacerbation aiguë sévère'),

-- Astigmatisme
('Astigmatisme','Artane','Larmes artificielles','1 goutte','COLLYRE','OPHTALMIQUE','3-4×/jour','30','SYMPTOMATIQUE','Soulagement de la sécheresse oculaire associée'),

-- Athérosclérose
('Athérosclérose','Tahor','Atorvastatine','40-80 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Réduction LDL < 0.7 g/L'),
('Athérosclérose','Aspirine UPSA','Acide acétylsalicylique','75-100 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Antiplaquettaire de prévention secondaire'),
('Athérosclérose','Amlor','Amlodipine','5-10 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Inhibiteur calcique antihypertenseur'),
('Athérosclérose','Triatec','Ramipril','5-10 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','IEC cardioprotecteur'),

-- BPCO
('BPCO','Spiriva','Tiotropium','18 µg','CAPSULE','INHALATION','1×/jour','365','PREMIERE_INTENTION','Bronchodilatateur anticholinergique de longue durée'),
('BPCO','Ventoline','Salbutamol','100 µg/bouffée','SPRAY','INHALATION','Au besoin',NULL,'PREMIERE_INTENTION','Bronchodilatateur de secours'),
('BPCO','Seretide','Fluticasone/Salmétérol','500/50 µg','SPRAY','INHALATION','2×/jour','365','DEUXIEME_INTENTION','Corticoïde + LABA en cas d''exacerbations fréquentes'),
('BPCO','Solupred','Prednisolone','40 mg','COMPRIME','ORALE','1×/matin','5','SYMPTOMATIQUE','Exacerbation aiguë'),
('BPCO','Augmentin','Amoxicilline-clavulanate','1 g','COMPRIME','ORALE','3×/jour','7','ADJUVANT','Exacerbation infectieuse'),

-- Bronchite
('Bronchite','Clamoxyl','Amoxicilline','500 mg','COMPRIME','ORALE','3×/jour','7','PREMIERE_INTENTION','Bronchite bactérienne — souvent virale donc antibiothérapie prudente'),
('Bronchite','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','3×/jour','7','SYMPTOMATIQUE','Fièvre et douleurs'),
('Bronchite','Bisolvon','Bromhexine','8 mg','COMPRIME','ORALE','3×/jour','7','SYMPTOMATIQUE','Mucolytique — fluidifie les sécrétions'),
('Bronchite','Drill','Dextrométhorphane','15 mg','SIROP','ORALE','3×/jour','5','SYMPTOMATIQUE','Antitussif — bronchite sèche seulement'),

-- COVID-19
('COVID-19','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','3×/jour','10','PREMIERE_INTENTION','Fièvre et douleurs — éviter AINS'),
('COVID-19','Decadron','Dexaméthasone','6 mg','COMPRIME','ORALE','1×/jour','10','PREMIERE_INTENTION','Formes sévères nécessitant O2 — réduction mortalité'),
('COVID-19','Veklury','Remdesivir','200 mg J1 puis 100 mg','INJECTION','INTRAVEINEUSE','1×/jour','5','DEUXIEME_INTENTION','Formes hospitalisées avec O2'),
('COVID-19','Xarelto','Rivaroxaban','10 mg','COMPRIME','ORALE','1×/jour','30','ADJUVANT','Anticoagulation préventive — risque thrombotique élevé'),
('COVID-19','Kaletra','Lopinavir/Ritonavir','400/100 mg','COMPRIME','ORALE','2×/jour','14','DEUXIEME_INTENTION','Cas sévères selon protocole'),

-- Cataracte
('Cataracte','Indocollyre','Indométacine collyre','0.1%','COLLYRE','OPHTALMIQUE','3×/jour','14','SYMPTOMATIQUE','Anti-inflammatoire post-opératoire'),
('Cataracte','Tobradex','Tobramycine + Dexaméthasone','1 goutte','COLLYRE','OPHTALMIQUE','4×/jour','14','ADJUVANT','Prévention infection + inflammation post-op'),

-- Chlamydia
('Chlamydia','Zithromax','Azithromycine','1 g','COMPRIME','ORALE','En une seule prise','1','PREMIERE_INTENTION','Dose unique — traiter le partenaire'),
('Chlamydia','Vibramycine','Doxycycline','100 mg','COMPRIME','ORALE','2×/jour','7','PREMIERE_INTENTION','Alternative à l''azithromycine'),
('Chlamydia','Erythrocine','Érythromycine','500 mg','COMPRIME','ORALE','4×/jour','7','DEUXIEME_INTENTION','Si grossesse — éviter doxycycline'),

-- Cholangite
('Cholangite','Augmentin','Amoxicilline-clavulanate','1 g','COMPRIME','ORALE','3×/jour','7','PREMIERE_INTENTION','Cholangite légère à modérée'),
('Cholangite','Ciflox','Ciprofloxacine','400 mg IV','INJECTION','INTRAVEINEUSE','2×/jour','7','PREMIERE_INTENTION','Formes sévères — IV d''abord'),
('Cholangite','Flagyl','Métronidazole','500 mg','COMPRIME','ORALE','3×/jour','7','ADJUVANT','Couverture anaérobies'),
('Cholangite','Ursofalk','Acide ursodéoxycholique','13-15 mg/kg/j','COMPRIME','ORALE','2×/jour','365','ADJUVANT','Lithiase biliaire associée'),

-- Cholécystite
('Cholécystite','Augmentin','Amoxicilline-clavulanate','1 g','COMPRIME','ORALE','3×/jour','7','PREMIERE_INTENTION','Couverture bactérienne large'),
('Cholécystite','Kétodolac','Kétorolac','30 mg IV','INJECTION','INTRAVEINEUSE','4×/jour','2','SYMPTOMATIQUE','Antalgique AINS en crise aiguë'),
('Cholécystite','Flagyl','Métronidazole','500 mg','INJECTION','INTRAVEINEUSE','3×/jour','5','ADJUVANT','Couverture anaérobies'),
('Cholécystite','Spasfon','Phloroglucinol','80 mg','COMPRIME','ORALE','3×/jour','5','SYMPTOMATIQUE','Antispasmodique — colique biliaire'),

-- Cirrhose
('Cirrhose','Aldactone','Spironolactone','100-400 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Diurétique antialdostérone — ascite'),
('Cirrhose','Lasilix','Furosémide','40-80 mg','COMPRIME','ORALE','1×/matin','365','PREMIERE_INTENTION','Diurétique de l''anse — ascite'),
('Cirrhose','Duphalac','Lactulose','15-30 mL','SIROP','ORALE','3×/jour','365','PREMIERE_INTENTION','Prévention encéphalopathie hépatique'),
('Cirrhose','Avlocardyl','Propranolol','20-40 mg','COMPRIME','ORALE','2×/jour','365','ADJUVANT','Prévention rupture de varices œsophagiennes'),
('Cirrhose','Vitamine K1','Phytoménadione','10 mg','COMPRIME','ORALE','1×/jour','30','ADJUVANT','Troubles de coagulation hépatiques'),

-- Colite ulcéreuse
('Colite ulcéreuse','Pentasa','Mésalazine','2-4 g','COMPRIME','ORALE','2×/jour','365','PREMIERE_INTENTION','5-ASA — entretien et poussée légère'),
('Colite ulcéreuse','Solupred','Prednisolone','40-60 mg','COMPRIME','ORALE','1×/matin','30','PREMIERE_INTENTION','Poussée modérée à sévère'),
('Colite ulcéreuse','Imurel','Azathioprine','2-2.5 mg/kg/j','COMPRIME','ORALE','1×/jour','365','DEUXIEME_INTENTION','Maintien de rémission — délai 3 mois'),
('Colite ulcéreuse','Remicade','Infliximab','5 mg/kg','INJECTION','INTRAVEINEUSE','S0, S2, S6 puis /8 sem','365','DEUXIEME_INTENTION','Formes sévères corticorésistantes'),

-- Condylomes
('Condylomes','Aldara','Imiquimod','5%','CREME','CUTANEE','3×/semaine','84','PREMIERE_INTENTION','Appliquer la nuit — rincer après 6-10 h'),
('Condylomes','Wartec','Podophyllotoxine','0.5%','SOLUTION','CUTANEE','2×/jour','3','PREMIERE_INTENTION','3 jours puis 4 jours de repos — max 4 cycles'),
('Condylomes','Interféron alpha','Interféron alpha-2b','1 M UI','INJECTION','INTRAMUSCULAIRE','3×/semaine','28','DEUXIEME_INTENTION','Formes récidivantes'),

-- Conjonctivite
('Conjonctivite','Tobrex','Tobramycine','0.3%','COLLYRE','OPHTALMIQUE','4×/jour','7','PREMIERE_INTENTION','Conjonctivite bactérienne'),
('Conjonctivite','Zovirax','Aciclovir gel ophtalmique','3%','COLLYRE','OPHTALMIQUE','5×/jour','14','PREMIERE_INTENTION','Conjonctivite herpétique'),
('Conjonctivite','Zaditen','Kétotifène','0.025%','COLLYRE','OPHTALMIQUE','2×/jour','14','SYMPTOMATIQUE','Conjonctivite allergique'),
('Conjonctivite','Naphazoline','Naphazoline + phéniramine','1 goutte','COLLYRE','OPHTALMIQUE','3×/jour','5','SYMPTOMATIQUE','Rougeur et démangeaisons'),

-- Constipation chronique
('Constipation chronique','Duphalac','Lactulose','15 mL','SIROP','ORALE','2×/jour','30','PREMIERE_INTENTION','Laxatif osmotique — selles molles'),
('Constipation chronique','Psyllium Blond','Psyllium','5 g','POUDRE','ORALE','2×/jour','30','PREMIERE_INTENTION','Fibres solubles — boire beaucoup d''eau'),
('Constipation chronique','Forlax','Macrogol (PEG) 4000','10 g','POUDRE','ORALE','2×/jour','30','PREMIERE_INTENTION','Osmotique — bon profil de tolérance'),
('Constipation chronique','Dulcolax','Bisacodyl','5-10 mg','COMPRIME','ORALE','1×/soir','5','DEUXIEME_INTENTION','Stimulant — usage ponctuel uniquement'),

-- Crohn
('Crohn','Pentasa','Mésalazine','3-4 g','COMPRIME','ORALE','2×/jour','365','PREMIERE_INTENTION','Formes légères à modérées'),
('Crohn','Flagyl','Métronidazole','500 mg','COMPRIME','ORALE','3×/jour','14','PREMIERE_INTENTION','Complications septiques ou fistulisantes'),
('Crohn','Imurel','Azathioprine','2-2.5 mg/kg/j','COMPRIME','ORALE','1×/jour','365','DEUXIEME_INTENTION','Entretien de rémission'),
('Crohn','Humira','Adalimumab','160 mg J1, 80 mg J15, puis 40 mg/2 sem','INJECTION','SOUS-CUTANEE','1×/2 semaines','365','DEUXIEME_INTENTION','Formes modérées à sévères — anti-TNFα'),

-- Cystite
('Cystite','Furadantine','Nitrofurantoïne','100 mg LP','CAPSULE','ORALE','2×/jour','5','PREMIERE_INTENTION','Cystite non compliquée de la femme'),
('Cystite','Monoflocet','Fosfomycine trométamol','3 g','POUDRE','ORALE','Dose unique','1','PREMIERE_INTENTION','Traitement minute — excellente observance'),
('Cystite','Triméthoprime','Triméthoprime','200 mg','COMPRIME','ORALE','2×/jour','7','DEUXIEME_INTENTION','Selon antibiogramme'),
('Cystite','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','3×/jour','3','SYMPTOMATIQUE','Antalgique — brûlures mictionnelles'),

-- Céphalée de tension
('Céphalée de tension','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','3×/jour','3','PREMIERE_INTENTION','Traitement de la crise'),
('Céphalée de tension','Ibuprofène EG','Ibuprofène','400 mg','COMPRIME','ORALE','3×/jour','3','PREMIERE_INTENTION','AINS — si paracétamol insuffisant'),
('Céphalée de tension','Laroxyl','Amitriptyline','10-75 mg','COMPRIME','ORALE','1×/soir','90','DEUXIEME_INTENTION','Prévention formes chroniques'),

-- Dengue
('Dengue','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','4×/jour','7','PREMIERE_INTENTION','Seul antalgique autorisé — AINS contre-indiqués'),
('Dengue','SRO OMS','Sels de réhydratation orale','1 sachet/L d''eau','POUDRE','ORALE','Selon besoin','7','ADJUVANT','Maintien de l''hydratation'),

-- Dermatite atopique
('Dermatite atopique','Hydrocortisone Bailleul','Hydrocortisone 1%','Fine couche','CREME','CUTANEE','2×/jour','14','PREMIERE_INTENTION','Corticoïde faible pour le visage et plis'),
('Dermatite atopique','Protopic','Tacrolimus 0.1%','Fine couche','CREME','CUTANEE','2×/jour','30','DEUXIEME_INTENTION','Zones sensibles — visage et cou'),
('Dermatite atopique','Zyrtec','Cétirizine','10 mg','COMPRIME','ORALE','1×/soir','30','SYMPTOMATIQUE','Antihistaminique — prurit'),
('Dermatite atopique','Dupixent','Dupilumab','300 mg','INJECTION','SOUS-CUTANEE','1×/2 semaines','365','DEUXIEME_INTENTION','Formes modérées à sévères réfractaires'),

-- Diabète Type 1
('Diabète Type 1','Novorapid','Insuline asparte (rapide)','Selon glycémie','INJECTION','SOUS-CUTANEE','3×/jour (avant repas)','365','PREMIERE_INTENTION','Insuline rapide — adapter selon glycémie'),
('Diabète Type 1','Lantus','Insuline glargine (lente)','Selon besoins','INJECTION','SOUS-CUTANEE','1×/soir','365','PREMIERE_INTENTION','Insuline basale — injection au coucher'),
('Diabète Type 1','Glucagon GlucaGen','Glucagon','1 mg','INJECTION','SOUS-CUTANEE','1 injection si hypoglycémie sévère',NULL,'ADJUVANT','Traitement de l''hypoglycémie sévère'),

-- Diabète Type 2
('Diabète Type 2','Glucophage','Metformine','500-1000 mg','COMPRIME','ORALE','2-3×/jour','365','PREMIERE_INTENTION','Première intention — si tolérance digestive bonne'),
('Diabète Type 2','Daonil','Glibenclamide','2.5-5 mg','COMPRIME','ORALE','1×/jour','365','DEUXIEME_INTENTION','Sulfamide hypoglycémiant'),
('Diabète Type 2','Januvia','Sitagliptine','100 mg','COMPRIME','ORALE','1×/jour','365','DEUXIEME_INTENTION','Inhibiteur DPP-4'),
('Diabète Type 2','Jardiance','Empagliflozine','10-25 mg','COMPRIME','ORALE','1×/matin','365','DEUXIEME_INTENTION','Inhibiteur SGLT2 — protection cardiovasculaire'),
('Diabète Type 2','Victoza','Liraglutide','0.6-1.8 mg','INJECTION','SOUS-CUTANEE','1×/jour','365','DEUXIEME_INTENTION','Agoniste GLP-1 — perte de poids'),

-- Diabète gestationnel
('Diabète gestationnel','Actrapid','Insuline humaine rapide','Selon glycémie','INJECTION','SOUS-CUTANEE','3×/jour','270','PREMIERE_INTENTION','Si régime insuffisant — surveillance glycémique rapprochée'),
('Diabète gestationnel','Glucophage','Metformine','500 mg','COMPRIME','ORALE','2×/jour','180','DEUXIEME_INTENTION','Selon avis obstétrical — non recommandé systématiquement'),

-- Dégénérescence maculaire
('Dégénérescence maculaire','Lucentis','Ranibizumab','0.5 mg','INJECTION','OPHTALMIQUE','1×/mois (3 mois puis PRN)','365','PREMIERE_INTENTION','DMLA néovasculaire — injection intravitréenne'),
('Dégénérescence maculaire','Avastin','Bévacizumab','1.25 mg','INJECTION','OPHTALMIQUE','1×/mois','365','DEUXIEME_INTENTION','Anti-VEGF — usage hors AMM mais efficace'),
('Dégénérescence maculaire','AREDS2 Vitamine','Zinc + Vitamine C/E','1 comprimé','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Formes intermédiaires — ralentissement progression'),

-- Eczéma
('Eczéma','Dermoval','Clobétasol propionate 0.05%','Fine couche','CREME','CUTANEE','1×/jour','14','PREMIERE_INTENTION','Corticoïde fort — usage court'),
('Eczéma','Hydracort','Hydrocortisone 1%','Fine couche','CREME','CUTANEE','2×/jour','14','PREMIERE_INTENTION','Corticoïde faible pour visage'),
('Eczéma','Topicrem','Émollient dermatologique','Généreusement','CREME','CUTANEE','2×/jour','365','ADJUVANT','Hydratation quotidienne — prévention rechutes'),
('Eczéma','Zyrtec','Cétirizine','10 mg','COMPRIME','ORALE','1×/soir','30','SYMPTOMATIQUE','Prurit — antihistaminique'),

-- Embolie pulmonaire
('Embolie pulmonaire','Xarelto','Rivaroxaban','15 mg (21 j) puis 20 mg','COMPRIME','ORALE','2×/jour puis 1×/jour','90','PREMIERE_INTENTION','Anticoagulant oral direct — Embolie pulmonaire'),
('Embolie pulmonaire','Eliquis','Apixaban','10 mg (7 j) puis 5 mg','COMPRIME','ORALE','2×/jour','90','PREMIERE_INTENTION','Anticoagulant oral direct — alternative'),
('Embolie pulmonaire','Fragmine','Daltéparine','200 UI/kg/j','INJECTION','SOUS-CUTANEE','1×/jour','10','PREMIERE_INTENTION','Héparinothérapie initiale'),
('Embolie pulmonaire','Actolyse','Alteplase','100 mg IV','INJECTION','INTRAVEINEUSE','En 2 heures','1','DEUXIEME_INTENTION','Thrombolyse systémique — EP massive'),

-- Emphysème
('Emphysème','Spiriva','Tiotropium','18 µg','CAPSULE','INHALATION','1×/jour','365','PREMIERE_INTENTION','Bronchodilatateur anticholinergique'),
('Emphysème','Ventoline','Salbutamol','100 µg','SPRAY','INHALATION','Au besoin',NULL,'PREMIERE_INTENTION','Bronchodilatateur de secours'),
('Emphysème','Théophylline LP','Théophylline','200-400 mg','COMPRIME','ORALE','2×/jour','365','DEUXIEME_INTENTION','Bronchodilatateur oral — taux sérique à surveiller'),

-- Fibromyalgie
('Fibromyalgie','Cymbalta','Duloxétine','30-60 mg','CAPSULE','ORALE','1×/jour','365','PREMIERE_INTENTION','Antidépresseur IRSN — douleurs neuropathiques'),
('Fibromyalgie','Lyrica','Prégabaline','75-300 mg','CAPSULE','ORALE','2×/jour','365','PREMIERE_INTENTION','Douleurs neuropathiques — fibromyalgie'),
('Fibromyalgie','Laroxyl','Amitriptyline','10-50 mg','COMPRIME','ORALE','1×/soir','365','ADJUVANT','Troubles du sommeil et douleurs'),
('Fibromyalgie','Tramadol EG','Tramadol','50-100 mg','COMPRIME','ORALE','3×/jour','30','SYMPTOMATIQUE','Antalgique palier 2 — usage limité'),

-- Gastrite
('Gastrite','Mopral','Oméprazole','20-40 mg','CAPSULE','ORALE','1×/jour','28','PREMIERE_INTENTION','IPP — à jeun le matin'),
('Gastrite','Clamoxyl','Amoxicilline','1 g','COMPRIME','ORALE','2×/jour','14','ADJUVANT','Éradication H. pylori — triple thérapie'),
('Gastrite','Zéclar','Clarithromycine','500 mg','COMPRIME','ORALE','2×/jour','14','ADJUVANT','Éradication H. pylori — triple thérapie'),
('Gastrite','Ulcar','Sucralfate','1 g','COMPRIME','ORALE','4×/jour','28','ADJUVANT','Gastroprotection — prendre à jeun'),

-- Gastroentérite
('Gastroentérite','SRO OMS','Sels de réhydratation orale','1 sachet/250 mL','POUDRE','ORALE','Selon soif','5','PREMIERE_INTENTION','Réhydratation — priorité absolue'),
('Gastroentérite','Imodium','Lopéramide','2 mg','COMPRIME','ORALE','Après chaque selle liquide (max 8/j)','3','SYMPTOMATIQUE','Antidiarrhéique — CI si fièvre élevée ou sang dans selles'),
('Gastroentérite','Smecta','Diosmectite','3 g','POUDRE','ORALE','3×/jour','5','ADJUVANT','Pansement intestinal — selles et nausées'),
('Gastroentérite','Primpéran','Métoclopramide','10 mg','COMPRIME','ORALE','3×/jour','3','SYMPTOMATIQUE','Antiémétique'),

-- Glaucome
('Glaucome','Timoptol','Timolol 0.5%','1 goutte','COLLYRE','OPHTALMIQUE','2×/jour','365','PREMIERE_INTENTION','Bêtabloquant collyre — baisse de la PIO'),
('Glaucome','Xalatan','Latanoprost 0.005%','1 goutte','COLLYRE','OPHTALMIQUE','1×/soir','365','PREMIERE_INTENTION','Analogue des prostaglandines — très efficace'),
('Glaucome','Alphagan','Brimonidine 0.2%','1 goutte','COLLYRE','OPHTALMIQUE','2×/jour','365','DEUXIEME_INTENTION','Agoniste alpha-2 — si bêtabloquant CI'),
('Glaucome','Diamox','Acétazolamide','250 mg','COMPRIME','ORALE','4×/jour','7','ADJUVANT','Crise aiguë de glaucome — urgence'),

-- Glomérulonéphrite
('Glomérulonéphrite','Solupred','Prednisolone','1 mg/kg/j','COMPRIME','ORALE','1×/matin','60','PREMIERE_INTENTION','Immunosuppression initiale'),
('Glomérulonéphrite','Cyclophosphamide Endoxan','Cyclophosphamide','2 mg/kg/j','COMPRIME','ORALE','1×/jour','90','DEUXIEME_INTENTION','Formes prolifératives sévères'),
('Glomérulonéphrite','Cobalt Inhibace','Cilazapril','2.5-5 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','IEC — protéinurie et HTA'),

-- Gonorrhée
('Gonorrhée','Rocéphine','Ceftriaxone','500 mg IM','INJECTION','INTRAMUSCULAIRE','Dose unique','1','PREMIERE_INTENTION','Traitement de référence — dose unique'),
('Gonorrhée','Zithromax','Azithromycine','1 g','COMPRIME','ORALE','Dose unique','1','ADJUVANT','Associé à la ceftriaxone si chlamydia non exclu'),
('Gonorrhée','Vibramycine','Doxycycline','100 mg','COMPRIME','ORALE','2×/jour','7','DEUXIEME_INTENTION','Alternative si ceftriaxone indisponible'),

-- Goutte
('Goutte','Colchicine Pierre Fabre','Colchicine','1 mg puis 0.5 mg','COMPRIME','ORALE','1 h après puis 12 h après','3','PREMIERE_INTENTION','Crise aiguë de goutte — en première intention'),
('Goutte','Zyloric','Allopurinol','100-300 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Réduction uricémie — traitement de fond'),
('Goutte','Ibuprofène EG','Ibuprofène','400-600 mg','COMPRIME','ORALE','3×/jour','5','SYMPTOMATIQUE','Crise aiguë si colchicine CI'),
('Goutte','Solupred','Prednisolone','30 mg','COMPRIME','ORALE','1×/jour','5','DEUXIEME_INTENTION','Crise réfractaire ou AINS CI'),

-- Grippe
('Grippe','Tamiflu','Oseltamivir','75 mg','CAPSULE','ORALE','2×/jour','5','PREMIERE_INTENTION','Dans les 48 h après début des symptômes'),
('Grippe','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','4×/jour','7','PREMIERE_INTENTION','Fièvre et myalgies — antipyrétique de choix'),
('Grippe','Relenza','Zanamivir','10 mg (2 inhal.)','SPRAY','INHALATION','2×/jour','5','DEUXIEME_INTENTION','Grippe saisonnière — formes légères'),

-- Hernie hiatale
('Hernie hiatale','Mopral','Oméprazole','20 mg','CAPSULE','ORALE','1×/matin','28','PREMIERE_INTENTION','IPP — traitement de référence du RGO'),
('Hernie hiatale','Primpéran','Métoclopramide','10 mg','COMPRIME','ORALE','3×/jour','14','ADJUVANT','Prokinétique — améliore la vidange gastrique'),
('Hernie hiatale','Phosphalugel','Phosphate d''aluminium','1 sachet','SOLUTION','ORALE','3×/jour','30','SYMPTOMATIQUE','Antiacide — soulagement immédiat'),

-- Herpès génital
('Herpès génital','Zovirax','Aciclovir','400 mg','COMPRIME','ORALE','3×/jour','7','PREMIERE_INTENTION','Primo-infection herpétique'),
('Herpès génital','Zelitrex','Valaciclovir','500 mg','COMPRIME','ORALE','2×/jour','10','PREMIERE_INTENTION','Traitement curatif ou suppressif long terme'),
('Herpès génital','Famvir','Famciclovir','250 mg','COMPRIME','ORALE','3×/jour','5','DEUXIEME_INTENTION','Alternative au valaciclovir'),

-- Hypercholestérolémie
('Hypercholestérolémie','Tahor','Atorvastatine','10-80 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Statine — réduction LDL-cholestérol'),
('Hypercholestérolémie','Crestor','Rosuvastatine','5-40 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Statine haute intensité'),
('Hypercholestérolémie','Ezetrol','Ézétimibe','10 mg','COMPRIME','ORALE','1×/jour','365','DEUXIEME_INTENTION','En association ou si statine CI'),
('Hypercholestérolémie','Lipanthyl','Fénofibrate','145 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Hypertriglycéridémie associée'),

-- Hypermétropie
('Hypermétropie','Larmes artificielles','Hypromellose','1 goutte','COLLYRE','OPHTALMIQUE','3×/jour','30','SYMPTOMATIQUE','Sécheresse oculaire liée à l''effort visuel'),

-- Hypertension
('Hypertension','Amlor','Amlodipine','5-10 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Inhibiteur calcique — toléré en monothérapie'),
('Hypertension','Triatec','Ramipril','2.5-10 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','IEC — néphroprotecteur'),
('Hypertension','Cozaar','Losartan','25-100 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','ARA II — si toux sous IEC'),
('Hypertension','Esidrex','Hydrochlorothiazide','12.5-25 mg','COMPRIME','ORALE','1×/matin','365','ADJUVANT','Diurétique thiazidique — en association'),
('Hypertension','Lopressor','Métoprolol','25-100 mg','COMPRIME','ORALE','2×/jour','365','ADJUVANT','Bêtabloquant — si comorbidité cardio'),

-- Hyperthyroïdie
('Hyperthyroïdie','Néomercazole','Carbimazole','5-60 mg','COMPRIME','ORALE','3×/jour','365','PREMIERE_INTENTION','Antithyroïdien de synthèse'),
('Hyperthyroïdie','Avlocardyl','Propranolol','40-80 mg','COMPRIME','ORALE','2-3×/jour','30','ADJUVANT','Contrôle symptômes — tachycardie et tremblement'),
('Hyperthyroïdie','Méthimazole','Méthimazole','5-30 mg','COMPRIME','ORALE','1-3×/jour','365','PREMIERE_INTENTION','Alternative au carbimazole'),

-- Hypertrophie bénigne de prostate
('Hypertrophie bénigne de prostate','Josir','Tamsulosine','0.4 mg','CAPSULE','ORALE','1×/jour','365','PREMIERE_INTENTION','Alpha-bloquant — amélioration rapide des symptômes'),
('Hypertrophie bénigne de prostate','Chibro-Proscar','Finastéride','5 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Inhibiteur 5-alpha-réductase — réduction volume prostate'),
('Hypertrophie bénigne de prostate','Avodart','Dutastéride','0.5 mg','CAPSULE','ORALE','1×/jour','365','DEUXIEME_INTENTION','Alternative au finastéride'),

-- Hypotension
('Hypotension','Gutron','Midodrine','2.5-10 mg','COMPRIME','ORALE','3×/jour','30','PREMIERE_INTENTION','Vasoconstricteur — hypotension orthostatique'),
('Hypotension','Fludrocortisone Aspen','Fludrocortisone','0.1-0.3 mg','COMPRIME','ORALE','1×/jour','30','DEUXIEME_INTENTION','Minéralocorticoïde — hypotension neurogène'),

-- Hypothyroïdie
('Hypothyroïdie','Lévothyrox','Lévothyroxine (T4)','25-200 µg','COMPRIME','ORALE','1×/matin à jeun','365','PREMIERE_INTENTION','Hormonothérapie substitutive — ajuster selon TSH'),
('Hypothyroïdie','Cytomel','Liothyronine (T3)','5-25 µg','COMPRIME','ORALE','2-3×/jour','365','DEUXIEME_INTENTION','Formes réfractaires ou symptômes persistants'),

-- Hépatite A
('Hépatite A','Doliprane','Paracétamol','500-1000 mg','COMPRIME','ORALE','3×/jour','14','SYMPTOMATIQUE','Fièvre et douleurs — éviter doses élevées'),
('Hépatite A','Vitamine B complexe','Vitamines B1/B6/B12','1 ampoule buvable','SOLUTION','ORALE','1×/jour','30','ADJUVANT','Support nutritionnel'),

-- Hépatite B
('Hépatite B','Viread','Ténofovir disoproxil','300 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Antivirale — hépatite B chronique'),
('Hépatite B','Baraclude','Entécavir','0.5-1 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Alternative au ténofovir'),
('Hépatite B','Pegasys','Peg-interféron alpha-2a','180 µg','INJECTION','SOUS-CUTANEE','1×/semaine','48','DEUXIEME_INTENTION','Hépatite B chronique — durée limitée'),

-- Hépatite C
('Hépatite C','Sovaldi','Sofosbuvir','400 mg','COMPRIME','ORALE','1×/jour','84','PREMIERE_INTENTION','Pangenotypique — association obligatoire'),
('Hépatite C','Daklinza','Daclatasvir','60 mg','COMPRIME','ORALE','1×/jour','84','PREMIERE_INTENTION','Association avec sofosbuvir'),
('Hépatite C','Harvoni','Ledipasvir/Sofosbuvir','90/400 mg','COMPRIME','ORALE','1×/jour','84','PREMIERE_INTENTION','Génotype 1 — taux de guérison > 95%'),

-- Infarctus du myocarde
('Infarctus du myocarde','Aspirine UPSA','Acide acétylsalicylique','250-500 mg IV puis 75 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Antiplaquettaire — dès suspicion IDM'),
('Infarctus du myocarde','Plavix','Clopidogrel','300-600 mg de charge puis 75 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Double antiplaquettaire — 12 mois après stent'),
('Infarctus du myocarde','Morphine','Chlorhydrate de morphine','2-4 mg IV','INJECTION','INTRAVEINEUSE','Si douleur persiste toutes 5 min',NULL,'SYMPTOMATIQUE','Antalgie — IDM aigu'),
('Infarctus du myocarde','Lénitral','Trinitrine','0.4 mg sublingual','SPRAY','ORALE','1-2 bouffées sublinguales',NULL,'PREMIERE_INTENTION','Vasodilatateur — crise angineuse / IDM'),
('Infarctus du myocarde','Tahor','Atorvastatine','40-80 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Réduction LDL post-IDM — commencer en urgence'),

-- Influenza A/B
('Influenza A/B','Tamiflu','Oseltamivir','75 mg','CAPSULE','ORALE','2×/jour','5','PREMIERE_INTENTION','Grippe A ou B — dans les 48 h'),
('Influenza A/B','Relenza','Zanamivir','10 mg (2 inhal.)','SPRAY','INHALATION','2×/jour','5','DEUXIEME_INTENTION','Alternative à l''oseltamivir'),
('Influenza A/B','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','4×/jour','5','SYMPTOMATIQUE','Fièvre et douleurs'),

-- Insuffisance cardiaque
('Insuffisance cardiaque','Lasilix','Furosémide','20-80 mg','COMPRIME','ORALE','1-2×/jour','365','PREMIERE_INTENTION','Diurétique de l''anse — décongestion'),
('Insuffisance cardiaque','Aldactone','Spironolactone','25-50 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Diurétique épargnant potassium — réduction mortalité'),
('Insuffisance cardiaque','Rénitec','Énalapril','2.5-20 mg','COMPRIME','ORALE','2×/jour','365','PREMIERE_INTENTION','IEC — réduction mortalité'),
('Insuffisance cardiaque','Kredex','Carvédilol','3.125-25 mg','COMPRIME','ORALE','2×/jour','365','PREMIERE_INTENTION','Bêtabloquant — débuter à faible dose'),
('Insuffisance cardiaque','Digoxine Nativelle','Digoxine','0.125-0.25 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Contrôle FC en FA associée'),

-- Insuffisance rénale aiguë
('Insuffisance rénale aiguë','Lasilix','Furosémide','40-200 mg IV','INJECTION','INTRAVEINEUSE','2×/jour','7','PREMIERE_INTENTION','Relance diurèse si anurie fonctionnelle'),
('Insuffisance rénale aiguë','Bicarbonate de Na','Bicarbonate de sodium','1.4% IV','INJECTION','INTRAVEINEUSE','En continu',NULL,'ADJUVANT','Correction acidose métabolique'),
('Insuffisance rénale aiguë','Kayexalate','Résine échangeuse d''ions (polystyrène)','15 g','POUDRE','ORALE','3×/jour','5','SYMPTOMATIQUE','Hyperkaliémie — à surveiller'),

-- Insuffisance rénale chronique
('Insuffisance rénale chronique','Amlor','Amlodipine','5-10 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Contrôle tensionnel — protection rénale'),
('Insuffisance rénale chronique','Triatec','Ramipril','2.5-5 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','IEC — réduction protéinurie'),
('Insuffisance rénale chronique','NeoRecormon','Érythropoïétine bêta','2000-10000 UI','INJECTION','SOUS-CUTANEE','2-3×/semaine','365','ADJUVANT','Anémie de l''IRC'),
('Insuffisance rénale chronique','Renvela','Sévélamer','800 mg','COMPRIME','ORALE','3×/jour','365','ADJUVANT','Chélateur du phosphore'),

-- Kératite
('Kératite','Tobradex','Tobramycine 0.3%','1 goutte','COLLYRE','OPHTALMIQUE','4×/jour','7','PREMIERE_INTENTION','Kératite bactérienne'),
('Kératite','Zovirax opht.','Aciclovir gel ophtalmique 3%','1 bande de 10 mm','COLLYRE','OPHTALMIQUE','5×/jour','14','PREMIERE_INTENTION','Kératite herpétique'),
('Kératite','Voltarène','Diclofénac ophtalmique 0.1%','1 goutte','COLLYRE','OPHTALMIQUE','3×/jour','7','SYMPTOMATIQUE','Anti-inflammatoire oculaire'),

-- Laryngite
('Laryngite','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','3×/jour','5','PREMIERE_INTENTION','Antalgique et antipyrétique'),
('Laryngite','Ibuprofène EG','Ibuprofène','400 mg','COMPRIME','ORALE','3×/jour','5','PREMIER_INTENTION','Anti-inflammatoire — douleur laryngée'),
('Laryngite','Solupred','Prednisolone','1 mg/kg chez l''enfant','COMPRIME','ORALE','Dose unique','1','ADJUVANT','Laryngite striduleuse sévère'),

-- Leucémie
('Leucémie','Glivec','Imatinib','400-600 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','LMC — inhibiteur de tyrosine kinase'),
('Leucémie','Novatrex','Méthotrexate','Variable selon protocole','INJECTION','INTRAVEINEUSE','Selon protocole',NULL,'PREMIERE_INTENTION','LAL — selon schéma de chimiothérapie'),
('Leucémie','Adriamycine','Doxorubicine','Variable selon protocole','INJECTION','INTRAVEINEUSE','Selon protocole',NULL,'PREMIERE_INTENTION','Chimiothérapie — protocoles LAL/LAM'),
('Leucémie','Cytarabine Pfizer','Cytarabine','100-200 mg/m²/j','INJECTION','INTRAVEINEUSE','Selon protocole',NULL,'PREMIERE_INTENTION','LAM — traitement d''induction'),

-- Lithiase rénale
('Lithiase rénale','Kétodolac','Kétorolac','30 mg IM','INJECTION','INTRAMUSCULAIRE','Au besoin (max 4×/j)','3','PREMIERE_INTENTION','Antalgie en crise colique — AINS efficace'),
('Lithiase rénale','Josir','Tamsulosine','0.4 mg','CAPSULE','ORALE','1×/jour','28','PREMIERE_INTENTION','Facilite l''expulsion du calcul distal'),
('Lithiase rénale','Zyloric','Allopurinol','300 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Prévention lithiase urique'),
('Lithiase rénale','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','4×/jour','3','SYMPTOMATIQUE','Antalgique complémentaire'),

-- Lupus érythémateux systémique
('Lupus érythémateux systémique','Plaquenil','Hydroxychloroquine','200-400 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Traitement de fond — tous les lupus'),
('Lupus érythémateux systémique','Solupred','Prednisolone','0.5-1 mg/kg/j','COMPRIME','ORALE','1×/matin','60','PREMIERE_INTENTION','Poussée lupique — dégression progressive'),
('Lupus érythémateux systémique','Imurel','Azathioprine','2-3 mg/kg/j','COMPRIME','ORALE','1×/jour','365','DEUXIEME_INTENTION','Épargne cortisonique'),
('Lupus érythémateux systémique','Benlysta','Belimumab','10 mg/kg IV','INJECTION','INTRAVEINEUSE','S0, S2, S4 puis /4 sem','365','DEUXIEME_INTENTION','Anti-BLyS — formes réfractaires'),

-- Lymphome
('Lymphome','Mabthera','Rituximab','375 mg/m²','INJECTION','INTRAVEINEUSE','J1 de chaque cycle','182','PREMIERE_INTENTION','Lymphome B — anti-CD20'),
('Lymphome','Endoxan','Cyclophosphamide','750 mg/m²','INJECTION','INTRAVEINEUSE','J1 de chaque cycle','182','PREMIERE_INTENTION','Protocole R-CHOP — lymphome agressif'),
('Lymphome','Solupred','Prednisolone','100 mg/j','COMPRIME','ORALE','J1-J5 de chaque cycle','182','ADJUVANT','Protocole CHOP'),
('Lymphome','Oncovin','Vincristine','1.4 mg/m²','INJECTION','INTRAVEINEUSE','J1 de chaque cycle','182','PREMIERE_INTENTION','Protocole CHOP'),

-- Maladie d''Addison
('Maladie d''Addison','Hydrocortisone ROUSSEL','Hydrocortisone','15-25 mg/j','COMPRIME','ORALE','2-3×/jour','365','PREMIERE_INTENTION','Substitution glucocorticoïde — indispensable'),
('Maladie d''Addison','Fludrocortisone BESINS','Fludrocortisone','0.05-0.2 mg','COMPRIME','ORALE','1×/matin','365','PREMIERE_INTENTION','Substitution minéralocorticoïde'),

-- Malaria
('Malaria','Coartem','Artéméther + Luméfantrine','4 cp par prise','COMPRIME','ORALE','2×/jour','3','PREMIERE_INTENTION','Paludisme simple non compliqué — première intention'),
('Malaria','Quinimax','Quinine','8 mg/kg toutes 8 h IV','INJECTION','INTRAVEINEUSE','3×/jour','7','PREMIERE_INTENTION','Paludisme grave — perfusion lente'),
('Malaria','Artésunate IV','Artésunate','2.4 mg/kg IV','INJECTION','INTRAVEINEUSE','H0, H12, H24 puis 1×/jour','7','PREMIERE_INTENTION','Paludisme grave — préféré à la quinine IV'),
('Malaria','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','4×/jour','5','SYMPTOMATIQUE','Fièvre et céphalées'),

-- Migraine
('Migraine','Imigrane','Sumatriptan','50-100 mg','COMPRIME','ORALE','À la crise',NULL,'PREMIERE_INTENTION','Triptan — traitement de la crise migraineuse'),
('Migraine','Ibuprofène EG','Ibuprofène','400-600 mg','COMPRIME','ORALE','À la crise (max 3/sem)',NULL,'PREMIERE_INTENTION','AINS — crises légères à modérées'),
('Migraine','Propranolol','Propranolol','40-80 mg','COMPRIME','ORALE','2×/jour','180','DEUXIEME_INTENTION','Prévention migraine fréquente'),
('Migraine','Epitomax','Topiramate','25-100 mg','COMPRIME','ORALE','1×/soir','180','DEUXIEME_INTENTION','Prévention — formes fréquentes'),

-- Molluscum contagiosum
('Molluscum contagiosum','Aldara','Imiquimod 5%','Fine couche','CREME','CUTANEE','3×/semaine (soir)','60','PREMIERE_INTENTION','Immunomodulateur local'),
('Molluscum contagiosum','Wartec','Podophyllotoxine 0.5%','Locale','SOLUTION','CUTANEE','2×/jour 3 j/sem','28','DEUXIEME_INTENTION','Traitement local des lésions'),

-- Mononucléose
('Mononucléose','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','3×/jour','14','PREMIERE_INTENTION','Fièvre et douleurs — ne pas donner Aspirine'),
('Mononucléose','Ibuprofène EG','Ibuprofène','400 mg','COMPRIME','ORALE','3×/jour','7','ADJUVANT','Angine — soulagement de la douleur'),

-- Myocardite
('Myocardite','Ibuprofène EG','Ibuprofène','400 mg','COMPRIME','ORALE','3×/jour','14','PREMIERE_INTENTION','Myocardite légère — AINS'),
('Myocardite','Colchicine Pierre Fabre','Colchicine','0.5 mg','COMPRIME','ORALE','2×/jour','90','ADJUVANT','Réduction récidive péricardite/myocardite'),
('Myocardite','Lasilix','Furosémide','40 mg','COMPRIME','ORALE','1×/jour','30','ADJUVANT','Insuffisance cardiaque associée'),
('Myocardite','Solupred','Prednisolone','1 mg/kg','COMPRIME','ORALE','1×/matin','30','DEUXIEME_INTENTION','Myocardite auto-immune sévère'),

-- Myopie
('Myopie','Larmes artificielles','Hypromellose','1 goutte','COLLYRE','OPHTALMIQUE','3-4×/jour','30','SYMPTOMATIQUE','Sécheresse oculaire liée au port de lentilles'),

-- Neuropathie diabétique
('Neuropathie diabétique','Lyrica','Prégabaline','75-300 mg','CAPSULE','ORALE','2×/jour','365','PREMIERE_INTENTION','Douleurs neuropathiques'),
('Neuropathie diabétique','Cymbalta','Duloxétine','30-60 mg','CAPSULE','ORALE','1×/jour','365','PREMIERE_INTENTION','Douleurs neuropathiques diabétiques'),
('Neuropathie diabétique','Neurontin','Gabapentine','300-1200 mg','CAPSULE','ORALE','3×/jour','365','ADJUVANT','Alternative à la prégabaline'),
('Neuropathie diabétique','Laroxyl','Amitriptyline','25-75 mg','COMPRIME','ORALE','1×/soir','365','DEUXIEME_INTENTION','Douleurs neuropathiques chroniques'),

-- Néphrotique
('Néphrotique','Solupred','Prednisolone','1 mg/kg/j','COMPRIME','ORALE','1×/matin','60','PREMIERE_INTENTION','Syndrome néphrotique idiopathique'),
('Néphrotique','Lasilix','Furosémide','40-80 mg','COMPRIME','ORALE','2×/jour','30','ADJUVANT','Œdèmes importants'),
('Néphrotique','Tahor','Atorvastatine','20-40 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Hypercholestérolémie associée'),
('Néphrotique','Triatec','Ramipril','2.5-5 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Réduction protéinurie'),

-- Otite
('Otite','Clamoxyl','Amoxicilline','500 mg','COMPRIME','ORALE','3×/jour','7','PREMIERE_INTENTION','Otite moyenne aiguë bactérienne'),
('Otite','Ibuprofène EG','Ibuprofène','400 mg','COMPRIME','ORALE','3×/jour','5','SYMPTOMATIQUE','Antalgique et anti-inflammatoire'),
('Otite','Ciprodex','Ciprofloxacine + Dexaméthasone','3 gouttes','COLLYRE','OPHTALMIQUE','2×/jour','7','PREMIERE_INTENTION','Otite externe bactérienne'),
('Otite','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','4×/jour','5','SYMPTOMATIQUE','Douleur otalgique'),

-- Pancréatite
('Pancréatite','Morphine','Chlorhydrate de morphine','0.1 mg/kg IV/SC','INJECTION','SOUS-CUTANEE','Toutes les 4 h si douleur',NULL,'PREMIERE_INTENTION','Antalgie — pancréatite aiguë sévère'),
('Pancréatite','Tramadol EG','Tramadol','100 mg LP','COMPRIME','ORALE','2×/jour','7','PREMIERE_INTENTION','Antalgie palier 2 — formes légères'),
('Pancréatite','Ondansétron','Ondansétron','8 mg','COMPRIME','ORALE','3×/jour','5','SYMPTOMATIQUE','Antiémétique — nausées et vomissements'),

-- Parkinson
('Parkinson','Sinemet','Lévodopa + Carbidopa','25/100 mg','COMPRIME','ORALE','3×/jour','365','PREMIERE_INTENTION','Traitement de référence de la maladie de Parkinson'),
('Parkinson','Mirapexin','Pramipexole','0.088-3.3 mg','COMPRIME','ORALE','3×/jour','365','PREMIERE_INTENTION','Agoniste dopaminergique — en monothérapie ou association'),
('Parkinson','Jumexal','Sélégiline','5 mg','COMPRIME','ORALE','2×/jour','365','ADJUVANT','IMAO-B — neuroprotection et symptômes légers'),
('Parkinson','Mantadix','Amantadine','100 mg','COMPRIME','ORALE','2×/jour','365','ADJUVANT','Dyskinésies induites par lévodopa'),

-- Pemphigus
('Pemphigus','Solupred','Prednisolone','1-2 mg/kg/j','COMPRIME','ORALE','1×/matin','90','PREMIERE_INTENTION','Corticothérapie systémique haute dose'),
('Pemphigus','Mabthera','Rituximab','1000 mg','INJECTION','INTRAVEINEUSE','J1 et J15','28','PREMIERE_INTENTION','Formes sévères — réduction récidives'),
('Pemphigus','Imurel','Azathioprine','2-3 mg/kg/j','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Épargne cortisonique'),
('Pemphigus','Disulone','Dapsone','50-100 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Pemphigus foliacé léger'),

-- Pneumonie
('Pneumonie','Augmentin','Amoxicilline-clavulanate','1 g','COMPRIME','ORALE','3×/jour','7','PREMIERE_INTENTION','Pneumonie communautaire sans comorbidité'),
('Pneumonie','Zithromax','Azithromycine','500 mg','COMPRIME','ORALE','1×/jour','5','DEUXIEME_INTENTION','Pneumonie atypique ou allergie péni'),
('Pneumonie','Rocéphine','Ceftriaxone','1-2 g IV','INJECTION','INTRAVEINEUSE','1×/jour','7','PREMIERE_INTENTION','Formes sévères hospitalisées'),
('Pneumonie','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','4×/jour','7','SYMPTOMATIQUE','Fièvre et douleurs thoraciques'),

-- Polyglobulie
('Polyglobulie','Aspirine UPSA','Acide acétylsalicylique','100 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Prévention thrombotique'),
('Polyglobulie','Hydréa','Hydroxyurée','500-2000 mg','CAPSULE','ORALE','1×/jour','365','PREMIERE_INTENTION','Réduction polyglobulie — haut risque thrombotique'),
('Polyglobulie','Jakavi','Ruxolitinib','10-25 mg','COMPRIME','ORALE','2×/jour','365','DEUXIEME_INTENTION','Résistance ou intolérance à l''hydroxyurée'),

-- Polymyosite/Dermatomyosite
('Polymyosite/Dermatomyosite','Solupred','Prednisolone','1-1.5 mg/kg/j','COMPRIME','ORALE','1×/matin','60','PREMIERE_INTENTION','Traitement de première ligne'),
('Polymyosite/Dermatomyosite','Novatrex','Méthotrexate','15-25 mg/sem','COMPRIME','ORALE','1×/semaine','365','DEUXIEME_INTENTION','Épargne cortisonique'),
('Polymyosite/Dermatomyosite','Imurel','Azathioprine','2 mg/kg/j','COMPRIME','ORALE','1×/jour','365','DEUXIEME_INTENTION','Alternative au méthotrexate'),

-- Presbytie
('Presbytie','Larmes artificielles','Hypromellose','1 goutte','COLLYRE','OPHTALMIQUE','3×/jour','30','SYMPTOMATIQUE','Sécheresse oculaire fréquente chez les presbytes'),

-- Prostatite
('Prostatite','Ciflox','Ciprofloxacine','500 mg','COMPRIME','ORALE','2×/jour','28','PREMIERE_INTENTION','Fluoroquinolone — prostatite bactérienne aiguë'),
('Prostatite','Vibramycine','Doxycycline','100 mg','COMPRIME','ORALE','2×/jour','28','DEUXIEME_INTENTION','Prostatite chronique — si fluoroquinolone CI'),
('Prostatite','Josir','Tamsulosine','0.4 mg','CAPSULE','ORALE','1×/jour','30','ADJUVANT','Symptômes obstructifs associés'),
('Prostatite','Ibuprofène EG','Ibuprofène','400 mg','COMPRIME','ORALE','3×/jour','7','SYMPTOMATIQUE','Douleurs pelviennes'),

-- Psoriasis
('Psoriasis','Dermovate','Clobétasol 0.05%','Fine couche','CREME','CUTANEE','1×/jour','28','PREMIERE_INTENTION','Corticoïde local puissant — poussée'),
('Psoriasis','Daivonex','Calcipotriol','50 µg/g','CREME','CUTANEE','2×/jour','56','PREMIERE_INTENTION','Analogue vitamine D3 — plaques chroniques'),
('Psoriasis','Novatrex','Méthotrexate','7.5-25 mg','COMPRIME','ORALE','1×/semaine','365','DEUXIEME_INTENTION','Psoriasis modéré à sévère — bilan pré-thérapeutique'),
('Psoriasis','Humira','Adalimumab','80 mg J1, 40 mg J15, puis 40 mg/2 sem','INJECTION','SOUS-CUTANEE','1×/2 semaines','365','DEUXIEME_INTENTION','Biothérapie anti-TNFα'),
('Psoriasis','Daivobet','Bétaméthasone + Calcipotriol','Locale','CREME','CUTANEE','1×/jour','28','PREMIERE_INTENTION','Association corticoïde + vit D3'),

-- Pyélonéphrite
('Pyélonéphrite','Rocéphine','Ceftriaxone','1-2 g IV','INJECTION','INTRAVEINEUSE','1×/jour','14','PREMIERE_INTENTION','Pyélonéphrite aiguë hospitalisée'),
('Pyélonéphrite','Ciflox','Ciprofloxacine','500 mg','COMPRIME','ORALE','2×/jour','14','PREMIERE_INTENTION','Pyélonéphrite simple — ambulatoire'),
('Pyélonéphrite','Augmentin','Amoxicilline-clavulanate','1 g','COMPRIME','ORALE','3×/jour','14','DEUXIEME_INTENTION','Selon antibiogramme'),
('Pyélonéphrite','Gentalline','Gentamicine','3-5 mg/kg/j IV','INJECTION','INTRAVEINEUSE','1×/jour','5','ADJUVANT','Association initiale — formes sévères'),

-- Péricardite
('Péricardite','Ibuprofène EG','Ibuprofène','600 mg','COMPRIME','ORALE','3×/jour','14','PREMIERE_INTENTION','AINS de choix en péricardite'),
('Péricardite','Colchicine Pierre Fabre','Colchicine','0.5 mg','COMPRIME','ORALE','2×/jour','90','PREMIERE_INTENTION','Réduction récidive — associer aux AINS'),
('Péricardite','Solupred','Prednisolone','0.2-0.5 mg/kg/j','COMPRIME','ORALE','1×/matin','28','DEUXIEME_INTENTION','Péricardite réfractaire — risque de rechute'),

-- Rhinite allergique
('Rhinite allergique','Zyrtec','Cétirizine','10 mg','COMPRIME','ORALE','1×/soir','30','PREMIERE_INTENTION','Antihistaminique H1 non sédatif'),
('Rhinite allergique','Clarityne','Loratadine','10 mg','COMPRIME','ORALE','1×/jour','30','PREMIERE_INTENTION','Antihistaminique H1 — non sédatif'),
('Rhinite allergique','Rhinocort','Budésonide nasal','64 µg/nasal','SPRAY','NASALE','2×/jour','30','PREMIERE_INTENTION','Corticoïde nasal — symptômes nasaux'),
('Rhinite allergique','Rhinadvil','Ibuprofène + Pseudoéphédrine','Selon posologie','COMPRIME','ORALE','3×/jour','5','SYMPTOMATIQUE','Congestion nasale — usage court'),

-- Rougeole
('Rougeole','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','4×/jour','7','PREMIERE_INTENTION','Fièvre — traitement symptomatique'),
('Rougeole','Vitamine A','Rétinol (vitamine A)','200 000 UI 2 doses','COMPRIME','ORALE','J1 et J2','2','ADJUVANT','OMS — réduit complications chez l''enfant'),

-- Rétinopathie diabétique
('Rétinopathie diabétique','Lucentis','Ranibizumab','0.5 mg','INJECTION','OPHTALMIQUE','1×/mois','365','PREMIERE_INTENTION','DMAO proliférante — injection intravitréenne'),
('Rétinopathie diabétique','Glucophage','Metformine','500-1000 mg','COMPRIME','ORALE','2×/jour','365','ADJUVANT','Contrôle glycémique — prévention progression'),
('Rétinopathie diabétique','Triatec','Ramipril','5-10 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Contrôle tensionnel — protection rétinienne'),

-- Salmonellose
('Salmonellose','Ciflox','Ciprofloxacine','500 mg','COMPRIME','ORALE','2×/jour','5','PREMIERE_INTENTION','Formes sévères ou immunodéprimés'),
('Salmonellose','Rocéphine','Ceftriaxone','1-2 g IV','INJECTION','INTRAVEINEUSE','1×/jour','5','PREMIERE_INTENTION','Bactériémie — formes graves'),
('Salmonellose','Zithromax','Azithromycine','500 mg','COMPRIME','ORALE','1×/jour','3','DEUXIEME_INTENTION','Alternative selon antibiogramme'),
('Salmonellose','SRO OMS','Sels de réhydratation orale','1 sachet/L','POUDRE','ORALE','Selon soif','5','ADJUVANT','Réhydratation — priorité'),

-- Scléroderomie
('Scléroderomie','Novatrex','Méthotrexate','15-25 mg/sem','COMPRIME','ORALE','1×/semaine','365','PREMIERE_INTENTION','Atteinte cutanée précoce'),
('Scléroderomie','Cellcept','Mycophénolate mofétil','1-3 g/j','COMPRIME','ORALE','2×/jour','365','PREMIERE_INTENTION','Atteinte pulmonaire interstitielle'),
('Scléroderomie','Adalate','Nifédipine','10-30 mg','COMPRIME','ORALE','3×/jour','365','ADJUVANT','Phénomène de Raynaud'),
('Scléroderomie','Tracleer','Bosentan','125 mg','COMPRIME','ORALE','2×/jour','365','ADJUVANT','Hypertension artérielle pulmonaire'),

-- Sclérose en plaques
('Sclérose en plaques','Avonex','Interféron bêta-1a','30 µg IM','INJECTION','INTRAMUSCULAIRE','1×/semaine','365','PREMIERE_INTENTION','Formes rémittentes — réduction poussées'),
('Sclérose en plaques','Tysabri','Natalizumab','300 mg IV','INJECTION','INTRAVEINEUSE','1×/4 semaines','365','DEUXIEME_INTENTION','Formes très actives — risque LEMP'),
('Sclérose en plaques','Gilenya','Fingolimod','0.5 mg','CAPSULE','ORALE','1×/jour','365','DEUXIEME_INTENTION','SEP-R active — immunomodulateur oral'),
('Sclérose en plaques','Solumedrol','Méthylprednisolone IV','1 g','INJECTION','INTRAVEINEUSE','1×/jour (5 jours)','5','PREMIERE_INTENTION','Poussée aiguë'),

-- Sclérose latérale amyotrophique
('Sclérose latérale amyotrophique','Rilutek','Riluzole','50 mg','COMPRIME','ORALE','2×/jour','365','PREMIERE_INTENTION','Seul traitement modifiant la maladie — ralentit progression'),
('Sclérose latérale amyotrophique','Radicava','Édaravone','60 mg IV','INJECTION','INTRAVEINEUSE','Cycles de 14 j/28 j','365','DEUXIEME_INTENTION','Réducteur du stress oxydatif'),
('Sclérose latérale amyotrophique','Liorésal','Baclofène','5-80 mg','COMPRIME','ORALE','3×/jour','365','SYMPTOMATIQUE','Spasticité'),

-- Sinusite
('Sinusite','Clamoxyl','Amoxicilline','500 mg','COMPRIME','ORALE','3×/jour','7','PREMIERE_INTENTION','Sinusite bactérienne confirmée'),
('Sinusite','Augmentin','Amoxicilline-clavulanate','1 g','COMPRIME','ORALE','3×/jour','7','DEUXIEME_INTENTION','Sinusite frontale ou pansinusite'),
('Sinusite','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','4×/jour','7','SYMPTOMATIQUE','Douleurs faciales et céphalées'),
('Sinusite','Rhinofluimucil','Acétylcystéine nasale','2 pulv.','SPRAY','NASALE','3×/jour','10','ADJUVANT','Fluidifiant des sécrétions sinusiennes'),

-- Spondylarthrite ankylosante
('Spondylarthrite ankylosante','Naproxène','Naproxène','500 mg','COMPRIME','ORALE','2×/jour','365','PREMIERE_INTENTION','AINS — traitement symptomatique de fond'),
('Spondylarthrite ankylosante','Salazopyrine','Sulfasalazine','500-3000 mg','COMPRIME','ORALE','3×/jour','365','DEUXIEME_INTENTION','Atteinte périphérique prédominante'),
('Spondylarthrite ankylosante','Humira','Adalimumab','40 mg','INJECTION','SOUS-CUTANEE','1×/2 semaines','365','DEUXIEME_INTENTION','Anti-TNFα — formes axiales actives'),
('Spondylarthrite ankylosante','Enbrel','Étanercept','50 mg','INJECTION','SOUS-CUTANEE','1×/semaine','365','DEUXIEME_INTENTION','Anti-TNFα — alternative à l''adalimumab'),

-- Stéatose hépatique
('Stéatose hépatique','Glucophage','Metformine','500-1000 mg','COMPRIME','ORALE','2×/jour','180','ADJUVANT','Résistance à l''insuline associée au diabète'),
('Stéatose hépatique','Vitamine E','Alpha-tocophérol','800 UI','CAPSULE','ORALE','1×/jour','365','ADJUVANT','NASH non diabétique — effet antioxydant'),

-- Syndrome de Cushing
('Syndrome de Cushing','Métopirone','Métyrapone','250-4000 mg/j','CAPSULE','ORALE','4×/jour','30','PREMIERE_INTENTION','Inhibiteur de synthèse du cortisol'),
('Syndrome de Cushing','Nizoral','Kétoconazole','200-1200 mg','COMPRIME','ORALE','2-3×/jour','30','DEUXIEME_INTENTION','Inhibiteur stéroïdogénèse — surveillance hépatique'),
('Syndrome de Cushing','Korlym','Mifépristone','300-1200 mg','COMPRIME','ORALE','1×/jour','30','DEUXIEME_INTENTION','Cushing non chirurgical — antagoniste du récepteur glucocorticoïde'),

-- Syndrome de Guillain-Barré
('Syndrome de Guillain-Barré','Immunoglobulines polyvalentes','IgIV humaines','0.4 g/kg/j','INJECTION','INTRAVEINEUSE','1×/jour (5 jours)','5','PREMIERE_INTENTION','Traitement immunomodulateur de référence'),
('Syndrome de Guillain-Barré','Gabapentine EG','Gabapentine','300-600 mg','CAPSULE','ORALE','3×/jour','30','SYMPTOMATIQUE','Douleurs neuropathiques'),
('Syndrome de Guillain-Barré','Morphine','Chlorhydrate de morphine','2-4 mg SC','INJECTION','SOUS-CUTANEE','Toutes les 4 h si douleur',NULL,'SYMPTOMATIQUE','Antalgie forte — formes douloureuses'),

-- Syndrome de Sjögren
('Syndrome de Sjögren','Plaquenil','Hydroxychloroquine','200-400 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Atteinte systémique légère'),
('Syndrome de Sjögren','Ciclosporine A','Ciclosporine A 0.05%','1 goutte','COLLYRE','OPHTALMIQUE','2×/jour','365','PREMIERE_INTENTION','Sécheresse oculaire sévère'),
('Syndrome de Sjögren','Salagen','Pilocarpine','5 mg','COMPRIME','ORALE','3×/jour','90','ADJUVANT','Stimulation des glandes salivaires et lacrymales'),

-- Syndrome du côlon irritable
('Syndrome du côlon irritable','Spasfon','Phloroglucinol','80 mg','COMPRIME','ORALE','3×/jour','30','PREMIERE_INTENTION','Antispasmodique — douleurs abdominales'),
('Syndrome du côlon irritable','Imodium','Lopéramide','2 mg','COMPRIME','ORALE','Après chaque selle liquide','30','PREMIERE_INTENTION','Forme diarrhéique prédominante'),
('Syndrome du côlon irritable','Forlax','Macrogol 4000','10 g','POUDRE','ORALE','2×/jour','30','ADJUVANT','Forme constipée prédominante'),
('Syndrome du côlon irritable','Laroxyl','Amitriptyline','10-25 mg','COMPRIME','ORALE','1×/soir','90','DEUXIEME_INTENTION','Douleurs et troubles du sommeil associés'),

-- Syphilis
('Syphilis','Extencilline','Benzathine pénicilline G','2.4 M UI IM','INJECTION','INTRAMUSCULAIRE','Dose unique (ou 3 si tardive)',NULL,'PREMIERE_INTENTION','Traitement de référence toute syphilis'),
('Syphilis','Vibramycine','Doxycycline','100 mg','COMPRIME','ORALE','2×/jour','14','DEUXIEME_INTENTION','Si allergie pénicilline — syphilis primaire/secondaire'),
('Syphilis','Zithromax','Azithromycine','2 g','COMPRIME','ORALE','Dose unique','1','DEUXIEME_INTENTION','Alternative — résistances émergentes à surveiller'),

-- Thrombocytémie
('Thrombocytémie','Hydréa','Hydroxyurée','500-2000 mg','CAPSULE','ORALE','1×/jour','365','PREMIERE_INTENTION','Haut risque thrombotique — cytoreduction'),
('Thrombocytémie','Aspirine UPSA','Acide acétylsalicylique','100 mg','COMPRIME','ORALE','1×/jour','365','ADJUVANT','Prévention thrombose'),
('Thrombocytémie','Agrylin','Anagrélide','0.5-2.5 mg','CAPSULE','ORALE','2×/jour','365','DEUXIEME_INTENTION','Si intolérance ou résistance à l''hydroxyurée'),

-- Thrombose veineuse
('Thrombose veineuse','Eliquis','Apixaban','10 mg (7 j) puis 5 mg','COMPRIME','ORALE','2×/jour','90','PREMIERE_INTENTION','TVP — anticoagulant oral direct'),
('Thrombose veineuse','Xarelto','Rivaroxaban','15 mg (21 j) puis 20 mg','COMPRIME','ORALE','2×/jour puis 1×/jour','90','PREMIERE_INTENTION','TVP — anticoagulant oral direct'),
('Thrombose veineuse','Lovenox','Enoxaparine','1 mg/kg','INJECTION','SOUS-CUTANEE','2×/jour','10','PREMIERE_INTENTION','Héparinothérapie initiale'),
('Thrombose veineuse','Coumadine','Warfarine','2-10 mg (selon INR)','COMPRIME','ORALE','1×/soir','180','DEUXIEME_INTENTION','Anticoagulation long terme — INR cible 2-3'),

-- Thyroïdite
('Thyroïdite','Ibuprofène EG','Ibuprofène','400-600 mg','COMPRIME','ORALE','3×/jour','14','PREMIERE_INTENTION','Thyroïdite subaiguë de De Quervain — douleur'),
('Thyroïdite','Solupred','Prednisolone','30-40 mg','COMPRIME','ORALE','1×/matin','30','DEUXIEME_INTENTION','Thyroïdite sévère réfractaire aux AINS'),
('Thyroïdite','Lévothyrox','Lévothyroxine','25-100 µg','COMPRIME','ORALE','1×/matin','365','ADJUVANT','Si hypothyroïdie séquellaire'),

-- Trachéite
('Trachéite','Clamoxyl','Amoxicilline','500 mg','COMPRIME','ORALE','3×/jour','7','PREMIERE_INTENTION','Trachéite bactérienne confirmée'),
('Trachéite','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','4×/jour','5','SYMPTOMATIQUE','Douleur trachéale et fièvre'),
('Trachéite','Bisolvon','Bromhexine','8 mg','COMPRIME','ORALE','3×/jour','7','SYMPTOMATIQUE','Mucolytique — sécrétions trachéales'),

-- Trouble de coagulation
('Trouble de coagulation','Exacyl','Acide tranexamique','500-1000 mg','COMPRIME','ORALE','3×/jour','7','PREMIERE_INTENTION','Antifibrinolytique — saignement actif'),
('Trouble de coagulation','Facteur VIII','Facteur VIII de coagulation','Variable selon poids et sévérité','INJECTION','INTRAVEINEUSE','Selon schéma',NULL,'PREMIERE_INTENTION','Hémophilie A — substitution'),
('Trouble de coagulation','Vitamine K1','Phytoménadione','10 mg','COMPRIME','ORALE','1×/jour','5','ADJUVANT','Surdosage AVK ou carence en vit K'),
('Trouble de coagulation','PFC','Plasma frais congelé','Variable mL/kg','INJECTION','INTRAVEINEUSE','Selon bilan',NULL,'ADJUVANT','Coagulopathie sévère — urgence'),

-- Tuberculose
('Tuberculose','Rifampicine','Rifampicine','600 mg','COMPRIME','ORALE','1×/jour à jeun','180','PREMIERE_INTENTION','Protocole HRZE — 2 premiers mois'),
('Tuberculose','Isoniazide','Isoniazide','300 mg','COMPRIME','ORALE','1×/jour','180','PREMIERE_INTENTION','Protocole HRZE — toute la durée'),
('Tuberculose','Pyrazinamide','Pyrazinamide','1500-2000 mg','COMPRIME','ORALE','1×/jour','60','PREMIERE_INTENTION','Protocole HRZE — 2 premiers mois uniquement'),
('Tuberculose','Myambutol','Éthambutol','1200-1600 mg','COMPRIME','ORALE','1×/jour','60','PREMIERE_INTENTION','Protocole HRZE — 2 premiers mois'),
('Tuberculose','Vitamine B6','Pyridoxine','25-50 mg','COMPRIME','ORALE','1×/jour','180','ADJUVANT','Prévention neuropathie à l''isoniazide'),

-- Typhoïde
('Typhoïde','Zithromax','Azithromycine','500 mg','COMPRIME','ORALE','1×/jour','7','PREMIERE_INTENTION','Fièvre typhoïde non compliquée — résistances faibles'),
('Typhoïde','Ciflox','Ciprofloxacine','500 mg','COMPRIME','ORALE','2×/jour','7','PREMIERE_INTENTION','Typhoïde sensible aux fluoroquinolones'),
('Typhoïde','Rocéphine','Ceftriaxone','2 g IV','INJECTION','INTRAVEINEUSE','1×/jour','14','DEUXIEME_INTENTION','Formes compliquées ou résistantes'),
('Typhoïde','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','4×/jour','7','SYMPTOMATIQUE','Fièvre typhoïde — antipyrétique'),

-- Ulcère gastro-duodénal
('Ulcère gastro-duodénal','Mopral','Oméprazole','20-40 mg','CAPSULE','ORALE','1×/jour à jeun','28','PREMIERE_INTENTION','IPP — cicatrisation de l''ulcère'),
('Ulcère gastro-duodénal','Clamoxyl','Amoxicilline','1 g','COMPRIME','ORALE','2×/jour','14','ADJUVANT','Éradication H. pylori — triple thérapie'),
('Ulcère gastro-duodénal','Zéclar','Clarithromycine','500 mg','COMPRIME','ORALE','2×/jour','14','ADJUVANT','Éradication H. pylori — triple thérapie'),
('Ulcère gastro-duodénal','Pepto-Bismol','Bismuth sous-salicylate','525 mg','COMPRIME','ORALE','4×/jour','14','ADJUVANT','Quadrithérapie bismuthée — résistances'),

-- Urticaire
('Urticaire','Zyrtec','Cétirizine','10 mg','COMPRIME','ORALE','1×/jour','30','PREMIERE_INTENTION','Antihistaminique H1 — urticaire aiguë ou chronique'),
('Urticaire','Clarityne','Loratadine','10 mg','COMPRIME','ORALE','1×/jour','30','PREMIERE_INTENTION','Alternative non sédative'),
('Urticaire','Solupred','Prednisolone','30-40 mg','COMPRIME','ORALE','1×/matin','5','DEUXIEME_INTENTION','Poussée sévère — traitement court'),
('Urticaire','Adrénaline Mylan','Adrénaline','0.3-0.5 mg IM','INJECTION','INTRAMUSCULAIRE','En urgence',NULL,'ADJUVANT','Urticaire géante + anaphylaxie'),

-- Urétrite
('Urétrite','Zithromax','Azithromycine','1 g','COMPRIME','ORALE','Dose unique','1','PREMIERE_INTENTION','Urétrite à Chlamydia — dose unique'),
('Urétrite','Vibramycine','Doxycycline','100 mg','COMPRIME','ORALE','2×/jour','7','PREMIERE_INTENTION','Alternative à l''azithromycine'),
('Urétrite','Rocéphine','Ceftriaxone','500 mg IM','INJECTION','INTRAMUSCULAIRE','Dose unique','1','PREMIERE_INTENTION','Urétrite gonococcique — associer à azithromycine'),

-- VIH/SIDA
('VIH/SIDA','Truvada','Ténofovir + Emtricitabine','200/245 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','Backbone du traitement antirétroviral'),
('VIH/SIDA','Sustiva','Éfavirenz','600 mg','COMPRIME','ORALE','1×/soir','365','PREMIERE_INTENTION','INNTI — 3e agent du traitement ARV'),
('VIH/SIDA','Biktarvy','Bictégravir/TAF/FTC','50/25/200 mg','COMPRIME','ORALE','1×/jour','365','PREMIERE_INTENTION','STR — traitement naïf de référence'),
('VIH/SIDA','Kaletra','Lopinavir/Ritonavir','200/50 mg','COMPRIME','ORALE','2×/jour','365','DEUXIEME_INTENTION','Protocole 2e ligne — ressources limitées'),

-- Varicelle
('Varicelle','Zovirax','Aciclovir','800 mg','COMPRIME','ORALE','5×/jour','7','PREMIERE_INTENTION','Adulte ou immunodéprimé — commencer dans les 24 h'),
('Varicelle','Doliprane','Paracétamol','1000 mg','COMPRIME','ORALE','4×/jour','7','PREMIERE_INTENTION','Fièvre — ne pas donner aspirine (risque Reye)'),
('Varicelle','Atarax','Hydroxyzine','25 mg','COMPRIME','ORALE','3×/jour','7','SYMPTOMATIQUE','Prurit — antihistaminique sédatif'),

-- Verrue
('Verrue','Koloderm','Acide salicylique 16%','Application locale','SOLUTION','CUTANEE','1×/jour','56','PREMIERE_INTENTION','Traitement local — limer la verrue avant application'),
('Verrue','Aldara','Imiquimod 5%','Fine couche','CREME','CUTANEE','3×/semaine (soir)','84','DEUXIEME_INTENTION','Verrue plane ou génitale'),

-- Vitiligo
('Vitiligo','Protopic','Tacrolimus 0.1%','Fine couche','CREME','CUTANEE','2×/jour','90','PREMIERE_INTENTION','Zones sensibles — visage et plis'),
('Vitiligo','Dermoval','Clobétasol 0.05%','Fine couche','CREME','CUTANEE','1×/jour','28','PREMIERE_INTENTION','Lésions récentes et limitées'),
('Vitiligo','Méladinine','Méthoxsalène (8-MOP)','10-20 mg','COMPRIME','ORALE','2 h avant UV',NULL,'DEUXIEME_INTENTION','PUVA thérapie — suivi dermatologique requis'),

-- Épilepsie
('Épilepsie','Dépakine','Valproate de sodium','500-1500 mg','COMPRIME','ORALE','2×/jour','365','PREMIERE_INTENTION','Large spectre — épilepsie généralisée'),
('Épilepsie','Tegretol','Carbamazépine','200-800 mg','COMPRIME','ORALE','2×/jour','365','PREMIERE_INTENTION','Crises partielles et généralisées'),
('Épilepsie','Keppra','Lévétiracétam','250-1500 mg','COMPRIME','ORALE','2×/jour','365','PREMIERE_INTENTION','Très bonne tolérance — epilepsies variées'),
('Épilepsie','Dilantin','Phénytoïne','100-300 mg','COMPRIME','ORALE','1-3×/jour','365','DEUXIEME_INTENTION','Crises partielles — fenêtre thérapeutique étroite'),
('Épilepsie','Lamictal','Lamotrigine','25-400 mg','COMPRIME','ORALE','2×/jour','365','DEUXIEME_INTENTION','Epilepsies partielles et généralisées — titration lente');
