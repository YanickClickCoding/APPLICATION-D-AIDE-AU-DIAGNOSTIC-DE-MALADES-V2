# GASA SAD — Système d'Aide au Diagnostic

Application web médicale complète d'aide au diagnostic assisté par intelligence artificielle, destinée aux professionnels de santé.

## Description

**GASA SAD** (GASA Système d'Aide au Diagnostic) permet aux médecins et au personnel médical de :

- Gérer les patients et leurs dossiers médicaux
- Conduire des consultations structurées avec saisie des signes vitaux, symptômes et examens
- Obtenir un diagnostic assisté par IA parmi **121 maladies** identifiables
- Générer des ordonnances et assurer le suivi des patients
- Administrer le système et consulter les analytics

---

## Technologies

### Backend
| Technologie | Version | Usage |
|---|---|---|
| **FastAPI** | 0.115.0 | Framework API REST |
| **Uvicorn** | 0.32.0 | Serveur ASGI |
| **SQLAlchemy** | 2.0.36 | ORM |
| **MySQL** | 8.0+ | Base de données (`sante_plus_ia`) |
| **Alembic** | 1.14.0 | Migrations base de données |
| **scikit-learn** | 1.5.2 | Modèle ML (Random Forest) |
| **pandas / numpy** | 2.2.3 / 2.1.3 | Traitement des données |
| **joblib** | 1.4.2 | Sérialisation des modèles |
| **python-jose** | 3.3.0 | Authentification JWT |
| **passlib[bcrypt]** | 1.7.4 | Hachage des mots de passe |
| **ReportLab** | 4.0.9 | Génération de rapports PDF |
| **Celery + Redis** | 5.3.4 / 5.0.1 | Tâches asynchrones |
| **Pydantic** | 2.10.2 | Validation des données |

### Frontend
| Technologie | Version | Usage |
|---|---|---|
| **React** | 19.2.5 | Framework UI |
| **TypeScript** | 6.0.2 | Typage statique |
| **Vite** | 8.0.10 | Build tool & dev server |
| **React Router** | 7.14.2 | Navigation SPA |
| **Chart.js** | 4.5.1 | Visualisations et graphiques |
| **react-chartjs-2** | 5.3.1 | Intégration Chart.js/React |
| **Lucide React** | 1.14.0 | Bibliothèque d'icônes |

---

## Architecture

```
APPLICATION-D-AIDE-AU-DIAGNOSTIC-V2/
├── backend/                        # API FastAPI + services ML
│   ├── app/
│   │   ├── main.py                 # Point d'entrée
│   │   ├── config.py               # Configuration
│   │   ├── models/                 # 17 modèles SQLAlchemy
│   │   ├── routers/                # 6 routers API
│   │   ├── schemas/                # Schémas Pydantic
│   │   ├── services/               # Services métier
│   │   ├── ml/                     # 13 modules Machine Learning
│   │   └── utils/                  # Utilitaires
│   ├── ml_models/                  # Modèles entraînés (.pkl)
│   ├── datasets/                   # Données d'entraînement
│   └── requirements.txt
├── frontend/                       # Application React
│   └── src/
│       ├── pages/                  # 17 pages React
│       ├── components/             # Composants réutilisables
│       ├── context/                # AuthContext
│       ├── services/               # Client API (api.ts)
│       └── utils/
├── analyse_ml/                     # Analyse et génération du modèle
│   ├── analyse_complete.py         # Script d'analyse principal
│   ├── figures/                    # 12 graphiques de résultats
│   └── model/                      # Artefacts ML exportés
└── [fichiers SQL, diagrammes UML]
```

---

## Modèle Machine Learning

Le modèle de diagnostic repose sur un **Random Forest** entraîné sur des données synthétiques calibrées à partir de plusieurs datasets médicaux publics (Kaggle/UCI) :

- Heart Disease Dataset (UCI) — 303 observations
- Cardiovascular Disease Dataset — 70 000 observations
- Diabetes Dataset (Pima Indians) — 768 observations
- Chronic Kidney Disease Dataset — 400 observations
- Liver Disease Patient Dataset — 30 000 observations

**Caractéristiques du modèle :**
- **121 maladies** identifiables
- **70 features** : signes vitaux, NFS, bilan métabolique, rénal, hépatique, cardiaque, coagulation, symptômes
- Seuil de confiance minimum : 60 %
- Explainabilité des prédictions via `explainability.py`
- Réentraînement automatique géré par `retraining_manager.py`

> Les fichiers `.pkl` du modèle ne sont pas versionnés (taille > 100 MB). Ils doivent être générés localement via `analyse_ml/analyse_complete.py` puis copiés dans `backend/ml_models/`.

---

## Fonctionnalités principales

### Rôles utilisateurs
- **Médecin** : consultations, diagnostics IA, ordonnances, suivi patients
- **Infirmier** : saisie des signes vitaux et examens
- **Administrateur** : gestion des utilisateurs, analytics système

### Modules
- Authentification JWT avec gestion des rôles
- Gestion des patients avec détection des homonymes
- Workflow de consultation : signes vitaux → symptômes → examens → diagnostic IA → ordonnance
- Historique des prédictions IA avec scoring de confiance
- Catalogue médicaments et génération d'ordonnances
- Génération de rapports PDF
- Tableau de bord analytique avec visualisations Chart.js
- Administration système : logs, réentraînement, performance IA

---

## Installation

### Prérequis
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis (pour les tâches Celery)

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

Configurer les variables d'environnement :

```bash
cp .env.example .env
# Modifier .env selon votre environnement
```

Importer la base de données et lancer les migrations :

```bash
mysql -u root -p < gasa_sad_ia_v2.sql
alembic upgrade head
```

Démarrer le serveur :

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

L'application est accessible sur `http://localhost:5173`.

---

## Variables d'environnement

Créer un fichier `.env` dans `backend/` à partir de `.env.example` :

```env
APP_NAME=Medical Diagnostic AI System
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

DATABASE_URL=mysql+pymysql://root:@localhost:3306/sante_plus_ia

SECRET_KEY=votre_cle_secrete_en_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=180

MODEL_PATH=./ml_models/
DATASET_PATH=./datasets/
MIN_CONFIDENCE_THRESHOLD=0.6

CORS_ORIGINS=http://localhost:5173,http://localhost:3000
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

---

## API — Endpoints principaux

| Router | Préfixe | Description |
|---|---|---|
| `auth.py` | `/auth` | Connexion, tokens JWT |
| `patients.py` | `/patients` | CRUD patients |
| `consultations.py` | `/consultations` | Gestion des consultations |
| `ml_prediction.py` | `/predict` | Diagnostic IA |
| `analytics.py` | `/analytics` | Statistiques et performances |
| `admin.py` | `/admin` | Administration système |

Documentation Swagger interactive : `http://localhost:8000/docs`

---

## Pages Frontend

| Page | Description |
|---|---|
| `Login` | Authentification |
| `DashboardNew` | Tableau de bord principal |
| `MesPatients` | Liste des patients du médecin |
| `DossierPatient` | Dossier complet d'un patient |
| `Consultations` | Liste des consultations |
| `ConsultationWorkflow` | Flux de consultation avec diagnostic IA |
| `DiagnosticsIA` | Interface dédiée aux diagnostics IA |
| `AdminSystem` | Administration et monitoring |
| `PersonnelMedical` | Gestion du personnel médical |
| `Utilisateurs` | Gestion des comptes utilisateurs |

---

## Diagrammes UML

Les diagrammes de conception sont disponibles dans le dossier racine :
- Diagramme de cas d'utilisation complet
- Diagramme de séquence — Diagnostic IA
- Diagramme de séquence — Authentification
- Diagramme de classes
