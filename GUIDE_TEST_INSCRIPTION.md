# Guide de Test - Inscription avec Activation

## Prérequis

1. Backend démarré sur http://localhost:8000
2. Frontend démarré sur http://localhost:5173
3. Base de données MySQL configurée

## Étape 1 : Tester l'Inscription

### Via l'Interface Web

1. Ouvrir http://localhost:5173/register
2. Remplir le formulaire :
   - **Nom** : KOUASSI
   - **Prénom(s)** : Aya
   - **Email** : aya.kouassi@gasasad.com
   - **Rôle** : Médecin
   - **Mot de passe** : medecin2026
   - **Confirmation** : medecin2026
3. Cliquer sur "Créer mon compte"
4. Vérifier le message de succès et la redirection vers /login

### Via cURL (API directe)

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

**Réponse attendue** :
```json
{
  "utilisateur_id": 5,
  "nom": "KOUASSI",
  "prenoms": "Aya",
  "email": "aya.kouassi@gasasad.com",
  "role": "medecin",
  "actif": false,
  "created_at": "2026-05-09T..."
}
```

## Étape 2 : Vérifier que le Compte est Inactif

### Tentative de Connexion

1. Aller sur http://localhost:5173/login
2. Entrer :
   - **Email** : aya.kouassi@gasasad.com
   - **Mot de passe** : medecin2026
3. Cliquer sur "Se connecter"
4. **Résultat attendu** : Message d'erreur "Email ou mot de passe incorrect"

### Via cURL

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "aya.kouassi@gasasad.com",
    "password": "medecin2026"
  }'
```

**Réponse attendue** : Erreur 401

## Étape 3 : Se Connecter en tant qu'Admin

1. Aller sur http://localhost:5173/login
2. Entrer les identifiants admin :
   - **Email** : admin@gasasad.com
   - **Mot de passe** : admin123
3. Cliquer sur "Se connecter"
4. Vérifier la connexion réussie

## Étape 4 : Activer le Compte

### Via l'Interface Web

1. Dans le menu, cliquer sur "Utilisateurs"
2. Chercher "Aya KOUASSI" dans la liste
3. Observer :
   - Badge "Inactif" en rouge
   - Opacité réduite de la carte
   - Icône toggle à gauche (ToggleLeft)
4. Cliquer sur le bouton toggle
5. Vérifier que :
   - Le badge passe à "Actif" en vert
   - L'opacité revient à normale
   - L'icône toggle passe à droite (ToggleRight)

### Via cURL (API directe)

```bash
# D'abord, obtenir le token admin
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gasasad.com","password":"admin123"}' \
  | jq -r '.access_token')

# Ensuite, activer le compte (remplacer 5 par l'ID réel)
curl -X PUT http://localhost:8000/api/admin/users/5 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"actif": true}'
```

## Étape 5 : Vérifier la Connexion Après Activation

1. Se déconnecter (si connecté en tant qu'admin)
2. Aller sur http://localhost:5173/login
3. Entrer :
   - **Email** : aya.kouassi@gasasad.com
   - **Mot de passe** : medecin2026
4. Cliquer sur "Se connecter"
5. **Résultat attendu** : Connexion réussie, redirection vers le dashboard

## Étape 6 : Tester la Modification du Rôle

### Via l'Interface Web

1. Se connecter en tant qu'admin
2. Aller sur "Utilisateurs"
3. Trouver "Aya KOUASSI"
4. Cliquer sur le bouton "Rôle"
5. Dans la modale, sélectionner "Infirmier"
6. Cliquer sur "Enregistrer"
7. Vérifier que le badge change de "Médecin" à "Infirmier"

### Via cURL

```bash
curl -X PUT http://localhost:8000/api/admin/users/5 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"role": "infirmier"}'
```

## Étape 7 : Tester la Désactivation

1. Dans "Utilisateurs", trouver "Aya KOUASSI"
2. Cliquer sur le bouton toggle (à droite)
3. Vérifier que le compte passe à "Inactif"
4. Se déconnecter
5. Essayer de se connecter avec aya.kouassi@gasasad.com
6. **Résultat attendu** : Erreur de connexion

## Cas de Test Supplémentaires

### Test 1 : Email Déjà Utilisé

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "AUTRE",
    "prenoms": "Personne",
    "email": "aya.kouassi@gasasad.com",
    "mot_de_passe": "password123",
    "role": "infirmier"
  }'
```

**Résultat attendu** : Erreur 400 "Cette adresse email est déjà utilisée"

### Test 2 : Mot de Passe Trop Court

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "TEST",
    "prenoms": "User",
    "email": "test@gasasad.com",
    "mot_de_passe": "123",
    "role": "medecin"
  }'
```

**Résultat attendu** : Erreur 400 "Le mot de passe doit faire au moins 8 caractères"

### Test 3 : Rôle Invalide

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "HACKER",
    "prenoms": "Evil",
    "email": "hacker@gasasad.com",
    "mot_de_passe": "password123",
    "role": "admin"
  }'
```

**Résultat attendu** : Erreur 400 "Le rôle doit être 'medecin' ou 'infirmier'"

## Vérification dans la Base de Données

```sql
-- Voir tous les utilisateurs
SELECT utilisateur_id, nom, prenoms, email, role, actif, created_at 
FROM utilisateurs 
ORDER BY created_at DESC;

-- Voir uniquement les comptes inactifs
SELECT utilisateur_id, nom, prenoms, email, role, created_at 
FROM utilisateurs 
WHERE actif = FALSE;

-- Activer manuellement un compte (si besoin)
UPDATE utilisateurs 
SET actif = TRUE 
WHERE email = 'aya.kouassi@gasasad.com';
```

## Checklist de Validation

- [ ] L'inscription crée un compte avec actif=False
- [ ] Le mot de passe est hashé avec bcrypt
- [ ] Les comptes inactifs ne peuvent pas se connecter
- [ ] L'admin peut voir les comptes inactifs dans la liste
- [ ] L'admin peut activer un compte via le toggle
- [ ] L'admin peut modifier le rôle d'un utilisateur
- [ ] L'admin peut désactiver un compte
- [ ] Les comptes activés peuvent se connecter normalement
- [ ] Les erreurs sont gérées correctement (email dupliqué, mot de passe court, etc.)
- [ ] Les messages de succès/erreur sont affichés à l'utilisateur

## Logs à Surveiller

### Backend (console)
```
🔐 Tentative de connexion: aya.kouassi@gasasad.com
⚠️ Tentative de connexion avec compte inactif: aya.kouassi@gasasad.com
✅ Inscription réussie: aya.kouassi@gasasad.com (medecin) - En attente d'activation
✅ Authentification réussie: aya.kouassi@gasasad.com (medecin)
```

### Frontend (console navigateur)
```
🌐 API: Envoi requête login à /api/auth/login
❌ Erreur de connexion: Email ou mot de passe incorrect
✅ Connexion réussie, redirection...
```

## Dépannage

### Problème : "Cannot find module '../config'"
**Solution** : Vérifier que le fichier `frontend/src/config.ts` existe

### Problème : "Impossible de se connecter au serveur"
**Solution** : Vérifier que le backend est démarré sur http://localhost:8000

### Problème : "Email ou mot de passe incorrect" (compte actif)
**Solution** : Vérifier dans la base de données que actif=TRUE

### Problème : Le toggle ne fonctionne pas
**Solution** : Vérifier que vous êtes connecté en tant qu'admin et que le token est valide

## Conclusion

Si tous les tests passent, la fonctionnalité d'inscription avec activation est opérationnelle ! 🎉

Les utilisateurs peuvent maintenant :
- ✅ S'inscrire eux-mêmes
- ✅ Attendre l'activation par un admin
- ✅ Se connecter une fois activés

Les administrateurs peuvent :
- ✅ Voir les comptes en attente
- ✅ Activer/désactiver des comptes
- ✅ Modifier les rôles
- ✅ Gérer tous les utilisateurs
