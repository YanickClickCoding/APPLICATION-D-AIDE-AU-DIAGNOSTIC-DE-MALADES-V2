# Relations de la table `catalogue_medicaments`

> **Base de données :** `gasa_sad_ia _v2.sql`  
> **Type de table :** Table de référence (données maîtres) — aucune clé étrangère formelle

---

## Principe général

La table `catalogue_medicaments` est un **dictionnaire médical de référence** : elle recense les médicaments standards associés à chaque maladie connue du système (121 maladies, 425 médicaments).

Elle **n'est jamais modifiée** au cours d'une consultation. Son rôle est uniquement d'être **consultée** pour proposer des suggestions au médecin. Lorsqu'un médecin sélectionne un médicament depuis ce catalogue, l'application **crée une copie** de cette ligne dans la table `medicaments` (prescription réelle), liée à l'ordonnance du patient. Cette prescription intègre ensuite le dossier médical du patient.

---

## Schéma des relations (logique applicative)

```
                    ┌──────────────────────────────────┐
                    │       catalogue_medicaments       │
                    │  ─────────────────────────────── │
                    │  PK  id                          │
                    │      maladie          (index)    │
                    │      nom_commercial              │
                    │      denomination_commune        │
                    │      dosage_standard             │
                    │      forme                       │
                    │      voie_administration         │
                    │      frequence_habituelle        │
                    │      duree_standard_jours        │
                    │      categorie                   │
                    │      notes                       │
                    └──────────────┬───────────────────┘
                                   │
              lookup sur maladie   │   copie snapshot (prescription)
                ┌──────────────────┴───────────────────┐
                │                                      │
                ▼  N:1 (N médicaments )                 ▼  1 → 0..N
   ┌────────────────────────┐             ┌────────────────────────┐
   │       diagnostics      │             │      medicaments       │
   │  ──────────────────── │             │  ──────────────────── │
   │  PK  diagnostic_id     │             │  PK  medicament_id     │
   │  FK  consultation_id   │             │  FK  ordonnance_id  ───┐│
   │  FK  analyse_ia_id     │             │      nom_commercial    ││
   │  FK  medecin_id        │             │      denomination_comm ││
   │  FK  dossier_id     ───┐│            │      dosage            ││
   │      nom_maladie   ════╪╗            │      forme             ││
   │      statut            ││            │      quantite          ││
   └────────────────────────┘│            │      frequence         ││
                             ││            │      voie_admin        ││
                             ││            │      duree_jours       ││
                             ││            └────────────────────────┘│
                             ││                                      │
                             ││            ┌────────────────────────┐│
                             ││            │       ordonnances      ││
                             ││            │  ──────────────────── ││
                             ││            │  PK  ordonnance_id    ◄┘│
                             ││            │  FK  traitement_id ───┐ │
                             ││            │  FK  medecin_id       │ │
                             ││            │  FK  patient_id    ───┤ │
                             ││            │  FK  dossier_id    ───┼─┤
                             ││            └────────────────────────┘ │
                             ││                         │             │
                             ││          FK dossier_id  │             │
                             ││                         ▼             │
                             ││            ┌────────────────────────┐ │
                             ╚╪════════════▶   dossiers_medicaux   ◄──┘
                              │            │  ──────────────────── │
                              │            │  PK  dossier_id       │
                              │            │  FK  patient_id    ───┐│
                              │            │      numero_dossier   ││
                              │            │      antecedents...   ││
                              │            └────────────────────────┘│
                              │                         │             │
                              │          FK patient_id  │             │
                              │                         ▼             │
                              │            ┌────────────────────────┐ │
                              │            │        patients        │◄─┘
                              │            │  ──────────────────── │
                              └────────────│  PK  patient_id       │
                (dossier_id                │      nom, prenoms      │
               dans diagnostics)          │      date_naissance    │
                                          └────────────────────────┘
```

---

## Relations détaillées

### Relation 1 — `catalogue_medicaments` → `medicaments`

| Propriété | Valeur |
|---|---|
| **Type** | Logique applicative (pas de FK SQL) |
| **Direction** | `catalogue_medicaments` → `medicaments` |
| **Cardinalité** | **1 → 0..N** |
| **Nature du lien** | Copie snapshot au moment de la prescription |

**Justification de la cardinalité :**

- **Du côté catalogue (1) :** Un médicament du catalogue (ex. *Sandostatine LAR* pour l'Acromégalie) peut n'avoir jamais été prescrit (`0`) ou avoir été prescrit à plusieurs patients (`N`).
- **Du côté medicaments (N) :** Chaque ligne dans `medicaments` correspond à **une prescription réelle** pour un patient donné, liée à une ordonnance précise.
- La relation est **1 vers 0..N** : un même médicament de référence génère autant de lignes `medicaments` qu'il y a de prescriptions.

**Pourquoi pas de FK ?**

La table `medicaments` stocke une **copie figée** des informations au moment de la prescription. Si le catalogue est mis à jour (ex. changement de dosage standard), les prescriptions historiques ne doivent pas être affectées. L'absence de FK garantit cette immutabilité.

**Flux applicatif :**
```
Médecin clique sur chip  →  addMedFromCatalogue()  →  INSERT INTO medicaments
(catalogue_medicaments)      (ConsultationWorkflow)     (lié à ordonnance_id)
```

---

### Relation 2 — `diagnostics.nom_maladie` ↔ `catalogue_medicaments.maladie`

| Propriété | Valeur |
|---|---|
| **Type** | Lookup sémantique par correspondance de chaîne |
| **Direction** | `diagnostics` → `catalogue_medicaments` |
| **Cardinalité** | **N → N** (via colonne string commune) |
| **Nature du lien** | Recherche textuelle avec alias et LIKE |

**Justification de la cardinalité :**

- **Du côté diagnostics (N) :** Plusieurs diagnostics différents peuvent avoir le même `nom_maladie` (ex. plusieurs patients diagnostiqués *Acromégalie*). Chacun interroge le catalogue pour la même maladie.
- **Du côté catalogue (N) :** Pour une maladie donnée, le catalogue contient plusieurs médicaments (ex. 4 pour *Acromégalie*) répartis en catégories.
- La cardinalité réelle est **N diagnostics → N médicaments catalogue** pour une même maladie.

**Mécanisme de correspondance (3 niveaux) :**
```
1. Exacte      : maladie == nom_maladie
2. Alias       : ex. "Paludisme" → "Malaria", "Acromégalie" → "Acromégalie"
3. LIKE partiel: LOWER(maladie) LIKE '%acrom%'
```

---

### Relation 3 — `analyses_ia` → `catalogue_medicaments`

| Propriété | Valeur |
|---|---|
| **Type** | Lookup indirect via JSON |
| **Direction** | `analyses_ia` → `catalogue_medicaments` |
| **Cardinalité** | **1 → 0..N** |
| **Nature du lien** | Extraction de `maladie_predite` depuis le champ JSON `diagnostics_suggeres` |

**Justification de la cardinalité :**

- Une analyse IA prédit une maladie stockée dans `diagnostics_suggeres` (JSON).
- Cette maladie prédite est extraite par l'application et utilisée pour interroger le catalogue.
- **1 analyse** → extraction de `maladie_predite` → **0..N médicaments** dans le catalogue.
- Pas de FK possible : la valeur vit dans un blob JSON non indexable.

---

## Chaîne complète : du catalogue au dossier médical

Voici le parcours complet depuis la suggestion d'un médicament jusqu'à son inscription dans le dossier du patient :

```
[1] catalogue_medicaments         (référentiel — lecture seule)
        │
        │  Le médecin sélectionne un médicament suggéré
        │  L'app copie les données dans la prescription
        ▼
[2] medicaments                   (prescription réelle)
        │  FK ordonnance_id
        ▼
[3] ordonnances                   (ordonnance émise pour la consultation)
        │  FK dossier_id
        ▼
[4] dossiers_medicaux             (dossier du patient)
        │  FK patient_id
        ▼
[5] patients                      (fiche du patient)
```

**Justification des cardinalités sur la chaîne :**

| Lien | Cardinalité | Justification |
|---|---|---|
| `medicaments` → `ordonnances` | **N → 1** | Une ordonnance peut contenir plusieurs médicaments ; chaque ligne `medicaments` appartient à une seule ordonnance |
| `ordonnances` → `dossiers_medicaux` | **N → 1** | Un dossier médical accumule toutes les ordonnances du patient au fil des consultations |
| `dossiers_medicaux` → `patients` | **1 → 1** | Chaque patient a exactement un dossier médical (`unique=True` sur `patient_id`) |

---

## Résumé des cardinalités

```
catalogue_medicaments
    │
    │ 1 ─────────────────────────────────────────── 0..N
    └──────────────────────────────→ medicaments
                                     (par prescription, par patient, par maladie)

diagnostics (nom_maladie)
    │
    │ N ─────────────────────────────────────────── N
    └──────────────────────────────→ catalogue_medicaments (maladie)
                                     (plusieurs diagnostics, plusieurs médicaments)

analyses_ia (diagnostics_suggeres JSON)
    │
    │ 1 ─────────────────────────────────────────── 0..N
    └──────────────────────────────→ catalogue_medicaments (maladie)
                                     (maladie prédite → médicaments suggérés)
```

---

## Pourquoi l'absence de FK sur `catalogue_medicaments` est un choix architectural justifié

| Contrainte | Sans FK (choix actuel) | Avec FK |
|---|---|---|
| Mise à jour du catalogue | Possible sans impact sur les prescriptions passées | Risque de cascade involontaire |
| Historique des prescriptions | Figé au moment de la prescription (correct) | Sensible aux changements du catalogue |
| Flexibilité des noms de maladie | Gérée par alias + LIKE (variations ML) | Nécessiterait une normalisation stricte |
| Performance | Index sur `maladie` (varchar) — suffisant | FK entière plus rapide mais moins flexible |
| Indépendance des données | Le catalogue peut évoluer librement | Couplage fort avec les tables transactionnelles |
