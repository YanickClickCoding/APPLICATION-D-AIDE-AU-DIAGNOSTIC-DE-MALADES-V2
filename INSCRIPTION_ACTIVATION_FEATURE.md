# Fonctionnalité : Inscription avec Activation par l'Administrateur

## Description

Cette fonctionnalité permet aux médecins et infirmiers de créer leur propre compte via la page d'inscription publique. Les comptes créés sont **inactifs par défaut** et doivent être **activés par un administrateur** qui peut également **modifier le rôle** si nécessaire.

## Changements Implémentés

### 1. Frontend - Page d'Inscription (`frontend/src/pages/Register.tsx`)

#### Modifications :
- ✅ Ajout d'un champ de sélection de rôle (Médecin / Infirmier)
- ✅ Connexion à l'API backend au lieu du localStorage
- ✅ Message d'information indiquant que le compte sera activé par un administrateur
- ✅ Gestion des états de chargement et des erreurs
- ✅ Redirection vers la page de connexion avec message de succès

#### Nouveau Formulaire :
```
- Nom *
- Prénom(s) *
- Email *
- Rôle * (Médecin / Infirmier) ← NOUVEAU
- Mot de passe * (min 8 caractères)
- Confirmation *
```

### 2. Backend - Endpoint d'Inscription (`backend/app/routers/auth.py`)

#### Nouvel Endpoint :
```python
POST /api/auth/register
```

#### Fonctionnalités :
- ✅ Validation de l'email unique
- ✅ Validation du rôle (medecin ou infirmier uniquement)
- ✅ Validation du mot de passe (min 8 caractères)
- ✅ Hashage sécurisé du mot de passe avec bcrypt
- ✅ Création du compte avec `actif=False` par défaut
- ✅ Logging des inscriptions

#### Schéma de Requête :
```json
{
  "nom": "DUPONT",
  "prenoms": "Jean",
  "email": "jean.dupont@gasasad.com",
  "mot_de_passe": "motdepasse123",
  "role": "medecin"
}
```

#### Schéma de Réponse :
```json
{
  "utilisateur_id": 1,
  "nom": "DUPONT",
  "prenoms": "Jean",
  "email": "jean.dupont@gasasad.com",
  "role": "medecin",
  "actif": false,
  "created_at": "2026-05-09T10:30:00"
}
```

### 3. Configuration Frontend (`frontend/src/config.ts`)

#### Nouveau Fichier :
```typescript
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
export const APP_NAME = 'GASA SAD';
export const APP_DESCRIPTION = 'Système d\'Aide au Diagnostic';
```

### 4. Page de Gestion des Utilisateurs (Déjà Existante)

La page `frontend/src/pages/Utilisateurs.tsx` dispose déjà des fonctionnalités nécessaires :
- ✅ Bouton toggle pour activer/désactiver un compte
- ✅ Bouton pour modifier le rôle d'un utilisateur
- ✅ Indicateur visuel du statut (Actif / Inactif)
- ✅ Badge "En attente" pour les comptes inactifs

## Workflow Complet

### 1. Inscription d'un Nouveau Médecin/Infirmier

```
Utilisateur → Page d'inscription (/register)
  ↓
Remplit le formulaire (nom, prénom, email, rôle, mot de passe)
  ↓
Clique sur "Créer mon compte"
  ↓
Frontend → POST /api/auth/register
  ↓
Backend crée le compte avec actif=False
  ↓
Redirection vers /login avec message :
"Compte créé avec succès ! Votre compte est en attente d'activation par un administrateur."
```

### 2. Tentative de Connexion (Compte Inactif)

```
Utilisateur → Page de connexion (/login)
  ↓
Entre email + mot de passe
  ↓
Frontend → POST /api/auth/login
  ↓
Backend vérifie :
  - Email existe ? ✓
  - Mot de passe correct ? ✓
  - Compte actif ? ✗
  ↓
Erreur 401 : "Compte désactivé"
  ↓
Message d'erreur affiché à l'utilisateur
```

### 3. Activation par l'Administrateur

```
Admin → Page Utilisateurs (/utilisateurs)
  ↓
Voit la liste des comptes avec statut "Inactif"
  ↓
Clique sur le bouton toggle (ToggleLeft → ToggleRight)
  ↓
Frontend → PUT /api/admin/users/{id} avec { actif: true }
  ↓
Backend met à jour le compte
  ↓
Le compte devient actif
  ↓
L'utilisateur peut maintenant se connecter
```

### 4. Modification du Rôle (Optionnel)

```
Admin → Page Utilisateurs
  ↓
Clique sur "Rôle" pour un utilisateur
  ↓
Sélectionne le nouveau rôle (Admin / Médecin / Infirmier)
  ↓
Clique sur "Enregistrer"
  ↓
Frontend → PUT /api/admin/users/{id} avec { role: "nouveau_role" }
  ↓
Backend met à jour le rôle
```

## Sécurité

### Mesures Implémentées :
1. ✅ **Hashage des mots de passe** : Utilisation de bcrypt avec salt
2. ✅ **Validation des entrées** : Email, longueur du mot de passe, rôle autorisé
3. ✅ **Comptes inactifs par défaut** : Prévient l'accès non autorisé
4. ✅ **Vérification du statut actif** : À chaque connexion et requête authentifiée
5. ✅ **Rôles limités** : Seuls "medecin" et "infirmier" peuvent s'inscrire (pas "admin")
6. ✅ **Tokens JWT** : Authentification sécurisée après activation

### Restrictions :
- ❌ Les utilisateurs ne peuvent **pas** créer de compte administrateur
- ❌ Les comptes inactifs ne peuvent **pas** se connecter
- ❌ Les comptes inactifs ne peuvent **pas** accéder aux endpoints protégés
- ✅ Seuls les administrateurs peuvent activer/désactiver des comptes
- ✅ Seuls les administrateurs peuvent modifier les rôles

## Tests à Effectuer

### Test 1 : Inscription d'un Médecin
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "KOUASSI",
    "prenoms": "Aya",
    "email": "aya.kouassi@gasasad.com",
    "mot_de_passe": "medecin2026",
    "role": "medecin"
  }'
```

**Résultat attendu** : Compte créé avec `actif: false`

### Test 2 : Tentative de Connexion (Compte Inactif)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "aya.kouassi@gasasad.com",
    "password": "medecin2026"
  }'
```

**Résultat attendu** : Erreur 401 avec message "Email ou mot de passe incorrect"

### Test 3 : Activation par Admin
```bash
# D'abord, se connecter en tant qu'admin pour obtenir le token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@gasasad.com",
    "password": "admin123"
  }'

# Ensuite, activer le compte
curl -X PUT http://localhost:8000/api/admin/users/5 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "actif": true
  }'
```

**Résultat attendu** : Compte activé avec `actif: true`

### Test 4 : Connexion Après Activation
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "aya.kouassi@gasasad.com",
    "password": "medecin2026"
  }'
```

**Résultat attendu** : Token JWT retourné avec succès

## Interface Utilisateur

### Page d'Inscription
- Formulaire moderne avec validation en temps réel
- Champ de sélection de rôle avec icône
- Message informatif : "Votre compte sera activé par un administrateur"
- Indicateur de chargement pendant la création
- Gestion des erreurs (email déjà utilisé, mot de passe trop court, etc.)

### Page de Gestion des Utilisateurs (Admin)
- Badge "Inactif" en rouge pour les comptes en attente
- Bouton toggle pour activer/désactiver rapidement
- Bouton "Rôle" pour modifier le rôle
- Opacité réduite pour les comptes inactifs
- Filtrage et recherche des utilisateurs

## Cas d'Utilisation Mis à Jour

### Nouveaux Cas d'Utilisation :

**UC-61 : S'inscrire en tant que médecin/infirmier**
- **Acteur** : Médecin, Infirmier (non authentifié)
- **Description** : Créer un compte en fournissant nom, prénom, email, rôle et mot de passe
- **Résultat** : Compte créé avec statut inactif, en attente d'activation par un administrateur

**UC-62 : Activer un compte utilisateur**
- **Acteur** : Administrateur
- **Description** : Activer un compte en attente pour permettre à l'utilisateur de se connecter
- **Résultat** : Le compte passe de inactif à actif, l'utilisateur peut se connecter

**UC-63 : Modifier le rôle d'un utilisateur**
- **Acteur** : Administrateur
- **Description** : Changer le rôle d'un utilisateur (médecin ↔ infirmier ↔ admin)
- **Résultat** : Le rôle est mis à jour, les permissions changent en conséquence

## Prochaines Améliorations Possibles

1. **Notifications Email** :
   - Envoyer un email à l'utilisateur quand son compte est activé
   - Envoyer un email aux admins quand un nouveau compte est créé

2. **Dashboard Admin** :
   - Compteur de comptes en attente d'activation
   - Notification visuelle pour les nouveaux comptes

3. **Historique** :
   - Logger les activations/désactivations de comptes
   - Tracer qui a activé quel compte et quand

4. **Validation Avancée** :
   - Vérification de l'email (lien de confirmation)
   - Captcha pour prévenir les inscriptions automatisées

5. **Gestion des Demandes** :
   - Système de demande avec justification
   - Workflow d'approbation avec commentaires

## Fichiers Modifiés

```
frontend/
├── src/
│   ├── pages/
│   │   └── Register.tsx          ← MODIFIÉ
│   └── config.ts                  ← NOUVEAU
backend/
└── app/
    └── routers/
        └── auth.py                ← MODIFIÉ
```

## Commandes pour Tester

### Démarrer le Backend
```bash
cd backend
python -m app.main
```

### Démarrer le Frontend
```bash
cd frontend
npm run dev
```

### Accéder à l'Application
- Frontend : http://localhost:5173
- Backend API : http://localhost:8000
- Documentation API : http://localhost:8000/docs

## Conclusion

Cette fonctionnalité améliore la sécurité et le contrôle d'accès de l'application GASA SAD en permettant :
- ✅ L'auto-inscription des professionnels de santé
- ✅ La validation des comptes par les administrateurs
- ✅ La gestion flexible des rôles
- ✅ La prévention des accès non autorisés

Tous les comptes créés via l'inscription publique sont inactifs par défaut et nécessitent une activation manuelle par un administrateur, garantissant ainsi que seuls les utilisateurs légitimes peuvent accéder au système.
