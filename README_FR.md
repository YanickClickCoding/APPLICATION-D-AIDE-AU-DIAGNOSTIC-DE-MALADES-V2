# 🏥 Système de Diagnostic Médical Assisté par IA

## 📋 Description

Application web complète de gestion de consultations médicales avec assistance au diagnostic par Intelligence Artificielle utilisant Random Forest.

### Caractéristiques Principales

- 🤖 **IA de Diagnostic** : Modèle Random Forest avec 94.6% de précision
- 🏥 **Gestion Complète** : Patients, consultations, diagnostics
- 📊 **Analytics** : Tableaux de bord et statistiques en temps réel
- 🔐 **Sécurisé** : Authentification et gestion des rôles
- 💊 **121 Maladies** : Détection de 121 pathologies différentes

## 🛠️ Technologies Utilisées

### Backend
- **FastAPI** - Framework web Python moderne
- **SQLAlchemy** - ORM pour MySQL
- **Scikit-learn** - Machine Learning (Random Forest)
- **Pandas & NumPy** - Traitement des données
- **Pydantic** - Validation des données

### Frontend
- **React** + **TypeScript** - Interface utilisateur
- **Vite** - Build tool
- **React Router** - Navigation
- **Chart.js** - Graphiques
- **Lucide React** - Icônes

### Base de Données
- **MySQL** - Base de données relationnelle

## 📦 Installation

### Prérequis

- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- npm ou yarn

### 1. Cloner le Projet

```bash
git clone <url-du-repo>
cd APPLICATION-D-AIDE-AU-DIAGNOSTIC-DE-MALAGES
```

### 2. Configuration de la Base de Données

```bash
# Se connecter à MySQL
mysql -u root -p

# Créer la base de données
CREATE DATABASE gasa_sad;

# Importer le schéma
source gasa_sad.sql

# Insérer les données de test
source backend/seed_data.sql
```

### 3. Installation du Backend

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate

# Activer l'environnement (Linux/Mac)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
# Copier .env.example vers .env et ajuster si nécessaire
copy .env.example .env
```

### 4. Entraîner le Modèle IA

```bash
# Depuis le dossier backend
python train_initial_model.py
```

**Résultat attendu :**
- Précision : ~94.6%
- Durée : ~60 secondes
- Modèle sauvegardé dans `ml_models/`

### 5. Installation du Frontend

```bash
# Aller dans le dossier frontend
cd frontend

# Installer les dépendances
npm install
```

## 🚀 Démarrage

### Démarrer le Backend

```bash
cd backend
python -m app.main
```

Le backend sera accessible sur **http://localhost:8000**

- Documentation API : http://localhost:8000/docs
- Health Check : http://localhost:8000/health

### Démarrer le Frontend

```bash
# Dans un nouveau terminal, aller dans le dossier frontend
cd frontend

# Démarrer le serveur de développement
npm run dev
```

Le frontend sera accessible sur **http://localhost:5173**

## 👤 Comptes de Test

### Admin
- **Email** : `admin@gasasad.com`
- **Mot de passe** : `admin123`
- **Accès** : Toutes les fonctionnalités

### Médecin
- **Email** : `marie.dubois@gasasad.com`
- **Mot de passe** : `medecin123`
- **Accès** : Consultations, diagnostics

### Infirmier
- **Email** : `pierre.martin@gasasad.com`
- **Mot de passe** : `infirmier123`
- **Accès** : Consultations

## 📊 Fonctionnalités

### Dashboard
- Statistiques en temps réel
- Consultations du jour
- Performance du modèle IA
- Graphiques interactifs

### Gestion des Patients
- Enregistrement des patients
- Dossiers médicaux
- Historique des consultations
- Antécédents médicaux

### Consultations
- Création de consultations
- Saisie des symptômes
- Mesure des signes vitaux
- Prédiction IA automatique

### Diagnostics IA
- Prédiction automatique
- Score de confiance
- Top 3 des diagnostics probables
- Explainabilité (features importantes)
- Approbation/Rejet par le médecin

### Analytics
- Distribution des diagnostics
- Performance du modèle
- Taux d'approbation
- Statistiques mensuelles

## 🤖 Modèle IA

### Caractéristiques

- **Algorithme** : Random Forest
- **Précision** : 94.6%
- **Maladies** : 121 pathologies
- **Features** : 400 caractéristiques
  - 332 symptômes binaires
  - 60 mesures vitales/laboratoire
  - 8 features dérivées

### Entraînement

```bash
cd backend
python train_initial_model.py
```

### Réentraînement

```python
from app.ml.model_manager import model_manager

results = model_manager.retrain_with_new_data('path/to/new/data.csv')
```

## 📁 Structure du Projet

```
.
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── ml/                # Modules ML
│   │   ├── models/            # Modèles SQLAlchemy
│   │   ├── routers/           # Endpoints API
│   │   ├── schemas/           # Schémas Pydantic
│   │   └── main.py            # Application principale
│   ├── ml_models/             # Modèles entraînés
│   ├── train_initial_model.py # Script d'entraînement
│   └── seed_data.sql          # Données de test
│
├── frontend/                  # Frontend React + TypeScript
│   ├── src/
│   │   ├── pages/             # Pages de l'application
│   │   ├── components/        # Composants réutilisables
│   │   └── App.tsx            # Composant principal
│   ├── public/                # Fichiers statiques
│   ├── package.json           # Dépendances npm
│   └── vite.config.ts         # Configuration Vite
│
├── les ressources dataset/    # Dataset médical
│   └── dataset_medical_robust_10000_cas.csv
│
└── gasa_sad.sql         # Schéma de la base de données
```

## 🔧 Configuration

### Backend (.env)

```env
# Application
APP_NAME="Medical Diagnostic AI System"
APP_VERSION="1.0.0"
DEBUG=True
ENVIRONMENT=development

# Database
DATABASE_URL=mysql+pymysql://root:@localhost:3306/gasa_sad

# ML Models
MODEL_PATH=./ml_models/
MIN_CONFIDENCE_THRESHOLD=0.6

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### Frontend (.env)

Créer un fichier `.env` dans le dossier `frontend/` :

```env
VITE_API_URL=http://localhost:8000
```

## 📡 API Endpoints

### Patients
- `POST /patients` - Créer un patient
- `GET /patients` - Liste des patients
- `GET /patients/{id}` - Détails
- `PUT /patients/{id}` - Mettre à jour
- `DELETE /patients/{id}` - Supprimer

### Consultations
- `POST /consultations` - Créer une consultation
- `GET /consultations` - Liste
- `GET /consultations/{id}` - Détails
- `GET /consultations/patient/{id}` - Historique patient

### ML/IA
- `POST /ml/predict` - Prédiction de diagnostic
- `POST /ml/explain` - Explication
- `POST /ml/diagnostics` - Créer un diagnostic
- `POST /ml/diagnostics/{id}/approve` - Approuver
- `POST /ml/diagnostics/{id}/reject` - Rejeter
- `GET /ml/model/info` - Info modèle

### Analytics
- `GET /analytics/dashboard` - KPIs
- `GET /analytics/diagnostics/distribution` - Distribution
- `GET /analytics/performance/model` - Performance
- `GET /analytics/consultations/recent` - Récentes

## 🧪 Tests

### Tester l'API

```bash
cd backend
python test_api.py
```

### Tester une Prédiction

```python
import requests

response = requests.post('http://localhost:8000/ml/predict', json={
    'patient_data': {
        'symptom_Fièvre': 1,
        'symptom_Toux': 1,
        'Vital_Température (°C)': 38.5,
        'Age': 35
    }
})

print(response.json())
```

## 📈 Performance du Modèle

### Métriques

- **Accuracy** : 94.60%
- **Precision** : 94.86%
- **Recall** : 94.60%
- **F1-Score** : 94.44%

### Temps de Réponse

- Prédiction : < 100ms
- Explication : < 200ms
- Entraînement : ~60 secondes

## 🐛 Dépannage

### Le backend ne démarre pas

```bash
# Vérifier que MySQL est démarré
mysql -u root -p

# Vérifier les dépendances
pip install -r requirements.txt

# Vérifier les logs
cat backend/logs/app.log
```

### Le modèle n'est pas chargé

```bash
# Entraîner le modèle
cd backend
python train_initial_model.py

# Vérifier que le fichier existe
ls ml_models/
```

### Erreur de connexion frontend-backend

1. Vérifier que le backend tourne sur http://localhost:8000
2. Vérifier la configuration CORS dans `.env`
3. Vérifier `API_BASE_URL` dans `src/services/api.ts`

## 📝 Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [Implementation Status](backend/IMPLEMENTATION_STATUS.md)
- [ML Model Training](ML_MODEL_TRAINING_SUCCESS.md)
- [Workflow Complet avec Examens](WORKFLOW_COMPLET_AVEC_EXAMENS.md)
- [Frontend-Backend Integration](INTEGRATION_FRONTEND_BACKEND.md)
- [User Stories](informations.md)

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

## 👥 Auteurs

- **Équipe de Développement** - Système de Diagnostic Médical IA

## 🙏 Remerciements

- Dataset médical avec 10,000 cas et 121 maladies
- Scikit-learn pour le framework ML
- FastAPI pour le backend moderne
- React pour l'interface utilisateur

---

**🏥 Medical Diagnostic AI System - v1.0.0**

*Développé avec ❤️ pour améliorer les diagnostics médicaux*
