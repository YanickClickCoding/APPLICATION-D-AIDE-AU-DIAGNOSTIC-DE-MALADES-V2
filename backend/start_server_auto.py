"""
Script de démarrage automatique du serveur FastAPI
Lance le serveur sans interaction utilisateur
"""

import uvicorn
import sys
import os

# Forcer UTF-8 pour la console Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 80)
    print("  MEDICAL DIAGNOSTIC AI SYSTEM - BACKEND")
    print("=" * 80)
    print()
    print("Demarrage du serveur FastAPI...")
    print("URL: http://localhost:8000")
    print("Documentation: http://localhost:8000/docs")
    print()
    print("Appuyez sur Ctrl+C pour arreter le serveur")
    print("=" * 80)
    print()

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
