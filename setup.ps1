# =============================================================================
#  GASA SAD - Script d'installation automatique (Windows PowerShell)
#  Usage : .\setup.ps1
#  Prerequis : Python 3.9+, Node.js 18+, MySQL 8.0+ en cours d'execution
# =============================================================================

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

function Write-Header($title) {
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host "  $title" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
}

function Write-Step($msg)  { Write-Host "[*] $msg" -ForegroundColor Yellow }
function Write-OK($msg)    { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Fail($msg)  { Write-Host "[ERREUR] $msg" -ForegroundColor Red }

# ---------------------------------------------------------------------------
Write-Header "GASA SAD - Installation de l'application medicale IA"

# ---------------------------------------------------------------------------
Write-Header "1. Verification des prerequis"

# Python
try {
    $pyVersion = python --version 2>&1
    Write-OK "Python installe : $pyVersion"
} catch {
    Write-Fail "Python introuvable. Installez Python 3.9+ depuis https://python.org"
    exit 1
}

# Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-OK "Node.js installe : $nodeVersion"
} catch {
    Write-Fail "Node.js introuvable. Installez Node.js 18+ depuis https://nodejs.org"
    exit 1
}

# MySQL
try {
    $mysqlVersion = mysql --version 2>&1
    Write-OK "MySQL installe : $mysqlVersion"
} catch {
    Write-Fail "mysql CLI introuvable. Assurez-vous que MySQL 8.0+ est installe et dans le PATH."
    Write-Host "  Telechargez MySQL : https://dev.mysql.com/downloads/mysql/" -ForegroundColor Gray
    exit 1
}

# ---------------------------------------------------------------------------
Write-Header "2. Configuration de la base de donnees MySQL"

$DB_NAME = "sante_plus_ia"
$DB_USER = Read-Host "Nom d'utilisateur MySQL (defaut: root)"
if (-not $DB_USER) { $DB_USER = "root" }

$DB_PASS_SEC = Read-Host "Mot de passe MySQL (laisser vide si aucun)" -AsSecureString
$DB_PASS = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($DB_PASS_SEC)
)

$mysqlAuth = if ($DB_PASS) { "-u $DB_USER -p$DB_PASS" } else { "-u $DB_USER" }

Write-Step "Creation de la base de donnees '$DB_NAME'..."
try {
    $createDB = "CREATE DATABASE IF NOT EXISTS ``$DB_NAME`` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    Invoke-Expression "mysql $mysqlAuth -e `"$createDB`"" 2>&1 | Out-Null
    Write-OK "Base de donnees '$DB_NAME' creee ou deja existante."
} catch {
    Write-Fail "Impossible de creer la base de donnees. Verifiez vos identifiants MySQL."
    exit 1
}

Write-Step "Import du schema principal..."
$sqlFile = Join-Path $ProjectRoot "gasa_sad_ia _v2.sql"
if (Test-Path $sqlFile) {
    Invoke-Expression "mysql $mysqlAuth $DB_NAME < `"$sqlFile`"" 2>&1 | Out-Null
    Write-OK "Schema principal importe."
} else {
    Write-Host "  [ATTENTION] Fichier 'gasa_sad_ia _v2.sql' introuvable a la racine." -ForegroundColor Yellow
}

Write-Step "Import du catalogue des medicaments..."
$catFile = Join-Path $ProjectRoot "catalogue_medicaments.sql"
if (Test-Path $catFile) {
    Invoke-Expression "mysql $mysqlAuth $DB_NAME < `"$catFile`"" 2>&1 | Out-Null
    Write-OK "Catalogue medicaments importe."
}

$medFile = Join-Path $ProjectRoot "medicaments.sql"
if (Test-Path $medFile) {
    Invoke-Expression "mysql $mysqlAuth $DB_NAME < `"$medFile`"" 2>&1 | Out-Null
    Write-OK "Donnees medicaments importees."
}

# ---------------------------------------------------------------------------
Write-Header "3. Configuration du backend (FastAPI)"

$backendDir = Join-Path $ProjectRoot "backend"
Set-Location $backendDir

# Copier .env
$envFile    = Join-Path $backendDir ".env"
$envExample = Join-Path $backendDir ".env.example"
if (-not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
    Write-OK ".env cree depuis .env.example"
} else {
    Write-OK ".env existe deja, aucune modification."
}

# Mettre a jour DATABASE_URL dans .env
$dbUrl = if ($DB_PASS) {
    "mysql+pymysql://${DB_USER}:${DB_PASS}@localhost:3306/$DB_NAME"
} else {
    "mysql+pymysql://${DB_USER}:@localhost:3306/$DB_NAME"
}
(Get-Content $envFile) -replace "DATABASE_URL=.*", "DATABASE_URL=$dbUrl" | Set-Content $envFile
Write-OK "DATABASE_URL mis a jour dans .env"

# Environnement virtuel Python
Write-Step "Creation de l'environnement virtuel Python..."
if (-not (Test-Path (Join-Path $backendDir "venv"))) {
    python -m venv venv
    Write-OK "Environnement virtuel cree dans backend/venv"
} else {
    Write-OK "Environnement virtuel deja present."
}

Write-Step "Installation des dependances Python..."
& "$backendDir\venv\Scripts\pip.exe" install -r requirements.txt --quiet
Write-OK "Dependances Python installees."

# ---------------------------------------------------------------------------
Write-Header "4. Entrainement du modele ML"

$modelDir = Join-Path $backendDir "ml_models"
$hasModel  = (Test-Path $modelDir) -and ((Get-ChildItem $modelDir -Filter "*.joblib" -ErrorAction SilentlyContinue).Count -gt 0)

if ($hasModel) {
    Write-OK "Modele ML deja present dans backend/ml_models/"
} else {
    $trainChoice = Read-Host "Aucun modele ML detecte. Lancer l'entrainement maintenant ? (o/n, ~2-5 min)"
    if ($trainChoice -eq "o") {
        Write-Step "Entrainement en cours..."
        & "$backendDir\venv\Scripts\python.exe" train_initial_model.py
        Write-OK "Modele ML entraine."
    } else {
        Write-Host "  [ATTENTION] Sans modele ML, les predictions IA ne seront pas disponibles." -ForegroundColor Yellow
    }
}

# ---------------------------------------------------------------------------
Write-Header "5. Ajout des utilisateurs de demonstration"

$seedChoice = Read-Host "Ajouter les comptes de demonstration (admin, medecin, infirmier) ? (o/n)"
if ($seedChoice -eq "o") {
    & "$backendDir\venv\Scripts\python.exe" seed_users.py
    Write-OK "Utilisateurs de demonstration ajoutes."
}

# ---------------------------------------------------------------------------
Write-Header "6. Configuration du frontend (React + Vite)"

$frontendDir = Join-Path $ProjectRoot "frontend"
Set-Location $frontendDir

$frontEnv    = Join-Path $frontendDir ".env"
$frontExample = Join-Path $frontendDir ".env.example"
if (-not (Test-Path $frontEnv)) {
    Copy-Item $frontExample $frontEnv
    Write-OK ".env frontend cree."
}

Write-Step "Installation des dependances npm..."
npm install --silent
Write-OK "Dependances npm installees."

# ---------------------------------------------------------------------------
Write-Header "Installation terminee !"

Set-Location $ProjectRoot

Write-Host ""
Write-Host "Pour demarrer l'application :" -ForegroundColor White
Write-Host ""
Write-Host "  Backend  (terminal 1) :" -ForegroundColor Cyan
Write-Host "    cd backend" -ForegroundColor Gray
Write-Host "    .\venv\Scripts\python.exe start_server.py" -ForegroundColor Gray
Write-Host "    -- ou directement --" -ForegroundColor Gray
Write-Host "    .\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "  Frontend (terminal 2) :" -ForegroundColor Cyan
Write-Host "    cd frontend" -ForegroundColor Gray
Write-Host "    npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "  Acces :" -ForegroundColor Cyan
Write-Host "    Application : http://localhost:5173" -ForegroundColor Green
Write-Host "    API Swagger : http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
