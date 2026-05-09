# Frontend - GASA SAD

Application React + TypeScript pour le système d'aide au diagnostic médical.

## 🚀 Démarrage Rapide

```bash
# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev

# Compiler pour la production
npm run build
```

## 📁 Structure du Projet

```
frontend/
├── src/
│   ├── components/     # Composants réutilisables
│   ├── pages/          # Pages de l'application
│   ├── App.tsx         # Composant principal
│   └── main.tsx        # Point d'entrée
├── public/             # Fichiers statiques
├── index.html          # Template HTML
├── package.json        # Dépendances npm
├── vite.config.ts      # Configuration Vite
└── tsconfig.json       # Configuration TypeScript
```

## 🎯 Fonctionnalités Principales

### 1. Dashboard
- Vue d'ensemble des statistiques
- Graphiques interactifs
- Indicateurs clés de performance

### 2. Gestion des Patients
- Liste des patients
- Ajout/modification de patients
- Historique médical

### 3. Workflow de Consultation (7 étapes)
1. **Patient** - Informations personnelles
2. **Symptômes** - Saisie des symptômes cliniques
3. **Signes Vitaux** - Mesure des constantes
4. **Examens** - Résultats d'analyses (Biologie, Imagerie, ECG, Clinique)
5. **Consultation** - Observations médicales
6. **Diagnostic IA** - Prédiction automatique
7. **Validation** - Diagnostic final du médecin

### 4. Gestion des Consultations
- Liste des consultations
- Détails complets
- Historique par patient

### 5. Système de Notifications
- Toast notifications
- Messages de succès/erreur
- Feedback utilisateur en temps réel

## 🛠️ Technologies Utilisées

- **React 19** - Framework UI
- **TypeScript** - Typage statique
- **Vite** - Build tool ultra-rapide
- **React Router** - Navigation
- **Lucide React** - Icônes
- **Chart.js** - Graphiques
- **CSS Modules** - Styles

## 🔗 API Backend

L'application communique avec le backend FastAPI sur `http://localhost:8000`

### Endpoints principaux :
- `POST /consultations/workflow` - Créer une consultation complète
- `GET /consultations` - Liste des consultations
- `GET /patients` - Liste des patients
- `POST /ml/predict` - Prédiction IA

## 🎨 Design System

### Couleurs
- **Primary** : `#4F46E5` (Indigo)
- **Secondary** : `#7C3AED` (Purple)
- **Success** : `#10B981` (Green)
- **Error** : `#EF4444` (Red)
- **Warning** : `#F59E0B` (Amber)

### Typographie
- **Font** : Syne (Google Fonts)
- **Tailles** : 12px - 32px

## 📱 Responsive Design

L'application est entièrement responsive et fonctionne sur :
- 💻 Desktop (1920px+)
- 💻 Laptop (1366px+)
- 📱 Tablet (768px+)
- 📱 Mobile (375px+)

## 🧪 Tests

```bash
# Lancer les tests (à venir)
npm run test

# Linter
npm run lint
```

## 📦 Build Production

```bash
# Compiler pour la production
npm run build

# Prévisualiser le build
npm run preview
```

Les fichiers compilés seront dans le dossier `dist/`.

## 🔧 Configuration

### Variables d'environnement

Créer un fichier `.env` à la racine du dossier frontend :

```env
VITE_API_URL=http://localhost:8000
```

### Vite Config

Le fichier `vite.config.ts` contient la configuration du build :
- Plugin React avec Fast Refresh
- Optimisation des dépendances
- Configuration du serveur de dev

## 📚 Documentation Complète

Voir les fichiers de documentation à la racine du projet :
- `WORKFLOW_COMPLET_AVEC_EXAMENS.md` - Workflow de consultation
- `GUIDE_DEMARRAGE_RAPIDE.md` - Guide de démarrage
- `INTEGRATION_FRONTEND_BACKEND.md` - Intégration API

## 🤝 Contribution

1. Créer une branche : `git checkout -b feature/ma-fonctionnalite`
2. Commiter les changements : `git commit -m "Ajout de ma fonctionnalité"`
3. Pousser la branche : `git push origin feature/ma-fonctionnalite`
4. Créer une Pull Request

## 📄 Licence

Propriétaire - Tous droits réservés

---

**Version** : 2.0  
**Dernière mise à jour** : 3 mai 2026
