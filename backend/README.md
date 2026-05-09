# Backend - GASA SAD

Système d'Aide au Diagnostic assisté par IA utilisant FastAPI et Random Forest.

## 🏗️ Architecture

```
backend/
├── app/
│   ├── ml/                    # Modules ML (preprocessing, training, prediction)
│   ├── models/                # SQLAlchemy models (14 tables)
│   ├── schemas/               # Pydantic schemas (validation)
│   ├── routers/               # FastAPI routers (endpoints)
│   ├── utils/                 # Utilitaires (logger)
│   ├── config.py              # Configuration
│   ├── database.py            # Database connection
│   └── main.py                # FastAPI application
├── ml_models/                 # Modèles entraînés (créé automatiquement)
├── logs/                      # Logs (créé automatiquement)
├── requirements.txt           # Dépendances Python
├── .env.example               # Variables d'environnement
└── train_initial_model.py     # Script d'entraînement initial
```

## 📋 Prérequis

- Python 3.9+
- MySQL 8.0+
- Base de données `sante_plus_ia` créée (voir `../sante_plus_ia.sql`)

## 🚀 Installation

### 1. Créer un environnement virtuel

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configuration

Copier `.env.example` vers `.env` et configurer:

```bash
copy .env.example .env
```

Éditer `.env`:

```env
# Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/sante_plus_ia

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# ML
MODEL_PATH=./ml_models/
DATASET_PATH=../les ressources dataset/
MIN_CONFIDENCE_THRESHOLD=0.6

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### 4. Créer la base de données

```bash
# Se connecter à MySQL
mysql -u root -p

# Créer la base de données
CREATE DATABASE sante_plus_ia CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Importer le schéma
USE sante_plus_ia;
SOURCE ../sante_plus_ia.sql;
```

## 🤖 Entraînement du modèle initial

Avant de démarrer l'API, entraîner le modèle ML:

```bash
python train_initial_model.py
```

Cela va:
1. Charger le dataset (10,000 cas, 121 maladies)
2. Nettoyer et préparer les données
3. Entraîner un Random Forest (100 arbres, entropie)
4. Évaluer la performance
5. Sauvegarder le modèle dans `ml_models/`

**Résultats attendus:**
- Précision: >85%
- Durée: ~30-60 secondes
- Modèle sauvegardé: `ml_models/random_forest_v1.0_YYYYMMDD_HHMMSS.joblib`

## 🏃 Démarrer l'API

```bash
# Mode développement (avec auto-reload)
python -m app.main

# Ou avec uvicorn directement
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera disponible sur: http://localhost:8000

## 📚 Documentation API

Une fois l'API démarrée, accéder à:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Endpoints principaux

### Patients (US-001, US-004)

```
POST   /patients              # Créer un patient
GET    /patients              # Liste des patients
GET    /patients/{id}         # Détails d'un patient
PUT    /patients/{id}         # Mettre à jour
DELETE /patients/{id}         # Supprimer
```

### Consultations (US-002, US-003, US-005)

```
POST   /consultations                    # Créer une consultation
GET    /consultations                    # Liste des consultations
GET    /consultations/{id}               # Détails
GET    /consultations/patient/{id}       # Historique patient
```

### ML Prediction (US-014, US-015, US-016, US-020, US-021)

```
POST   /ml/predict                       # Prédire un diagnostic
POST   /ml/explain                       # Expliquer la prédiction
POST   /ml/diagnostics                   # Créer un diagnostic
POST   /ml/diagnostics/{id}/approve      # Approuver
POST   /ml/diagnostics/{id}/reject       # Rejeter
GET    /ml/model/info                    # Info sur le modèle
```

### Analytics (US-034, US-036, US-044)

```
GET    /analytics/dashboard              # Dashboard KPIs
GET    /analytics/diagnostics/distribution  # Distribution
GET    /analytics/performance/model      # Performance modèle
GET    /analytics/consultations/recent   # Consultations récentes
```

## 🧪 Tester l'API

### Exemple: Créer un patient

```bash
curl -X POST "http://localhost:8000/patients" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Dupont",
    "prenom": "Jean",
    "date_naissance": "1980-05-15",
    "sexe": "M",
    "numero_securite_sociale": "180051234567890",
    "telephone": "0612345678",
    "email": "jean.dupont@email.com"
  }'
```

### Exemple: Prédire un diagnostic

```bash
curl -X POST "http://localhost:8000/ml/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "consultation_id": 1
  }'
```

## 📊 User Stories implémentées

### ✅ Priorité 1 (Critiques)
- **US-001**: Enregistrement patient
- **US-002**: Saisie symptômes
- **US-003**: Saisie analyses
- **US-005**: Validation données
- **US-006**: Nettoyage données
- **US-007**: Normalisation
- **US-012**: Entraînement modèle
- **US-013**: Évaluation modèle
- **US-014**: Prédiction
- **US-015**: Score de confiance
- **US-016**: Explainabilité
- **US-020**: Approbation diagnostic
- **US-021**: Rejet diagnostic

### ✅ Priorité 2 (Importants)
- **US-004**: Historique patient
- **US-034**: Rapport mensuel
- **US-036**: Distribution diagnostics
- **US-044**: Dashboard statistiques

## 🔄 Réentraînement du modèle

Pour réentraîner avec de nouvelles données:

```python
from app.ml.model_manager import model_manager

# Réentraîner
results = model_manager.retrain_with_new_data(
    new_data_path="path/to/new_data.csv"
)

# Le nouveau modèle sera automatiquement chargé si meilleur
```

## 🐛 Debugging

### Logs

Les logs sont dans `logs/app.log` et aussi affichés dans la console.

### Vérifier le modèle

```bash
curl http://localhost:8000/ml/model/info
```

### Health check

```bash
curl http://localhost:8000/health
```

## 📦 Structure des données

### Patient
```json
{
  "nom": "string",
  "prenom": "string",
  "date_naissance": "YYYY-MM-DD",
  "sexe": "M|F",
  "numero_securite_sociale": "string",
  "telephone": "string",
  "email": "email@example.com"
}
```

### Consultation avec symptômes
```json
{
  "patient_id": "uuid",
  "medecin_id": 1,
  "motif": "string",
  "symptomes": [
    {
      "nom": "fievre",
      "present": true,
      "severite": "modere",
      "duree_jours": 3
    }
  ],
  "signes_vitaux": {
    "saturation_o2": 98.0,
    "frequence_cardiaque": 75,
    "temperature": 38.5,
    "tension_arterielle_systolique": 120,
    "tension_arterielle_diastolique": 80
  }
}
```

### Prédiction
```json
{
  "diagnostic_propose": "Grippe",
  "confiance": 0.92,
  "niveau_confiance": "high",
  "couleur_confiance": "green",
  "diagnostics_alternatifs": [
    {"diagnostic": "Rhume", "confiance": 0.05},
    {"diagnostic": "Bronchite", "confiance": 0.03}
  ],
  "temps_prediction_secondes": 0.045
}
```

## 🚧 Prochaines étapes

1. ✅ Backend API complet
2. ⏳ Intégration avec frontend React
3. ⏳ Authentification JWT
4. ⏳ Visualisations (Matplotlib/Seaborn)
5. ⏳ Tests unitaires
6. ⏳ Déploiement

## 📝 Notes

- Le modèle utilise **Random Forest avec entropie** comme spécifié
- Toutes les prédictions sont enregistrées pour traçabilité
- Les diagnostics rejetés sont utilisés pour améliorer le modèle
- Seuil de confiance minimum: 60% (configurable)

## 🤝 Support

Pour toute question, consulter:
- Documentation API: http://localhost:8000/docs
- User stories: `../informations.md`
- Dataset doc: `../les ressources dataset/DOCUMENTATION_DATASET.md`
