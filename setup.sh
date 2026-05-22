#!/usr/bin/env bash
# =============================================================================
#  GASA SAD - Script d'installation automatique (Linux / macOS)
#  Usage : bash setup.sh
#  Prerequis : Python 3.9+, Node.js 18+, MySQL 8.0+ en cours d'execution
# =============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOLD='\033[1m'; CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; RESET='\033[0m'

header()  { echo -e "\n${CYAN}${BOLD}$(printf '=%.0s' {1..70})${RESET}\n${CYAN}${BOLD}  $1${RESET}\n${CYAN}${BOLD}$(printf '=%.0s' {1..70})${RESET}"; }
step()    { echo -e "${YELLOW}[*] $1${RESET}"; }
ok()      { echo -e "${GREEN}[OK] $1${RESET}"; }
fail()    { echo -e "${RED}[ERREUR] $1${RESET}"; exit 1; }

# ---------------------------------------------------------------------------
header "GASA SAD - Installation de l'application medicale IA"

# ---------------------------------------------------------------------------
header "1. Verification des prerequis"

command -v python3 >/dev/null 2>&1 || fail "Python 3 introuvable. Installez Python 3.9+ via votre gestionnaire de paquets."
ok "Python installe : $(python3 --version)"

command -v node >/dev/null 2>&1 || fail "Node.js introuvable. Installez Node.js 18+ depuis https://nodejs.org"
ok "Node.js installe : $(node --version)"

command -v mysql >/dev/null 2>&1 || fail "MySQL CLI introuvable. Installez MySQL 8.0+ et assurez-vous qu'il est dans le PATH."
ok "MySQL installe : $(mysql --version)"

# ---------------------------------------------------------------------------
header "2. Configuration de la base de donnees MySQL"

DB_NAME="sante_plus_ia"
read -rp "Nom d'utilisateur MySQL [root]: " DB_USER
DB_USER="${DB_USER:-root}"
read -rsp "Mot de passe MySQL (laisser vide si aucun): " DB_PASS
echo ""

MYSQL_CMD="mysql -u $DB_USER"
[ -n "$DB_PASS" ] && MYSQL_CMD="mysql -u $DB_USER -p$DB_PASS"

step "Creation de la base de donnees '$DB_NAME'..."
$MYSQL_CMD -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" \
    || fail "Impossible de creer la base. Verifiez vos identifiants MySQL."
ok "Base de donnees '$DB_NAME' creee ou deja existante."

SQL_MAIN="$PROJECT_ROOT/gasa_sad_ia _v2.sql"
if [ -f "$SQL_MAIN" ]; then
    step "Import du schema principal..."
    $MYSQL_CMD "$DB_NAME" < "$SQL_MAIN"
    ok "Schema principal importe."
else
    echo -e "${YELLOW}  [ATTENTION] 'gasa_sad_ia _v2.sql' introuvable.${RESET}"
fi

for f in "catalogue_medicaments.sql" "medicaments.sql"; do
    fpath="$PROJECT_ROOT/$f"
    [ -f "$fpath" ] && { step "Import $f..."; $MYSQL_CMD "$DB_NAME" < "$fpath"; ok "$f importe."; }
done

# ---------------------------------------------------------------------------
header "3. Configuration du backend (FastAPI)"

BACKEND="$PROJECT_ROOT/backend"
cd "$BACKEND"

if [ ! -f ".env" ]; then
    cp .env.example .env
    ok ".env cree depuis .env.example"
else
    ok ".env existe deja."
fi

if [ -n "$DB_PASS" ]; then
    DB_URL="mysql+pymysql://${DB_USER}:${DB_PASS}@localhost:3306/$DB_NAME"
else
    DB_URL="mysql+pymysql://${DB_USER}:@localhost:3306/$DB_NAME"
fi
sed -i.bak "s|DATABASE_URL=.*|DATABASE_URL=$DB_URL|" .env && rm -f .env.bak
ok "DATABASE_URL mis a jour dans .env"

step "Creation de l'environnement virtuel Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    ok "Environnement virtuel cree dans backend/venv"
else
    ok "Environnement virtuel deja present."
fi

step "Installation des dependances Python..."
./venv/bin/pip install -r requirements.txt -q
ok "Dependances Python installees."

# ---------------------------------------------------------------------------
header "4. Entrainement du modele ML"

MODEL_DIR="$BACKEND/ml_models"
HAS_MODEL=false
[ -d "$MODEL_DIR" ] && [ "$(find "$MODEL_DIR" -name '*.joblib' 2>/dev/null | wc -l)" -gt 0 ] && HAS_MODEL=true

if $HAS_MODEL; then
    ok "Modele ML deja present dans backend/ml_models/"
else
    read -rp "Aucun modele ML detecte. Lancer l'entrainement maintenant ? (o/n, ~2-5 min) " TRAIN_CHOICE
    if [ "$TRAIN_CHOICE" = "o" ]; then
        step "Entrainement en cours..."
        ./venv/bin/python train_initial_model.py
        ok "Modele ML entraine."
    else
        echo -e "${YELLOW}  [ATTENTION] Sans modele ML, les predictions IA ne seront pas disponibles.${RESET}"
    fi
fi

# ---------------------------------------------------------------------------
header "5. Ajout des utilisateurs de demonstration"

read -rp "Ajouter les comptes de demonstration (admin, medecin, infirmier) ? (o/n) " SEED_CHOICE
[ "$SEED_CHOICE" = "o" ] && { ./venv/bin/python seed_users.py; ok "Utilisateurs de demonstration ajoutes."; }

# ---------------------------------------------------------------------------
header "6. Configuration du frontend (React + Vite)"

FRONTEND="$PROJECT_ROOT/frontend"
cd "$FRONTEND"

[ ! -f ".env" ] && cp .env.example .env && ok ".env frontend cree."

step "Installation des dependances npm..."
npm install --silent
ok "Dependances npm installees."

# ---------------------------------------------------------------------------
header "Installation terminee !"
cd "$PROJECT_ROOT"

echo ""
echo -e "${BOLD}Pour demarrer l'application :${RESET}"
echo ""
echo -e "${CYAN}  Backend  (terminal 1) :${RESET}"
echo -e "    cd backend"
echo -e "    source venv/bin/activate"
echo -e "    uvicorn app.main:app --reload --port 8000"
echo ""
echo -e "${CYAN}  Frontend (terminal 2) :${RESET}"
echo -e "    cd frontend"
echo -e "    npm run dev"
echo ""
echo -e "${CYAN}  Acces :${RESET}"
echo -e "${GREEN}    Application : http://localhost:5173${RESET}"
echo -e "${GREEN}    API Swagger : http://localhost:8000/docs${RESET}"
echo ""
