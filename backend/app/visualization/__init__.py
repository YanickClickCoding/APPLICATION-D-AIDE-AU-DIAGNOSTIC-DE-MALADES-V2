"""
Visualization Module
Configuration et utilitaires pour Matplotlib et Seaborn
"""
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour serveur
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

# Configuration du style Seaborn
sns.set_theme(style="whitegrid")
sns.set_palette("husl")

# Configuration Matplotlib
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10

# Répertoire pour sauvegarder les graphiques
CHARTS_DIR = Path("./charts")
CHARTS_DIR.mkdir(exist_ok=True)


def save_figure(fig, filename: str, dpi: int = 100) -> str:
    """
    Sauvegarde une figure Matplotlib
    
    Args:
        fig: Figure Matplotlib
        filename: Nom du fichier (sans extension)
        dpi: Résolution
        
    Returns:
        Chemin du fichier sauvegardé
    """
    filepath = CHARTS_DIR / f"{filename}.png"
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    return str(filepath)


def clear_old_charts(max_age_hours: int = 24):
    """
    Supprime les graphiques anciens
    
    Args:
        max_age_hours: Age maximum en heures
    """
    import time
    current_time = time.time()
    
    for filepath in CHARTS_DIR.glob("*.png"):
        file_age = current_time - filepath.stat().st_mtime
        if file_age > max_age_hours * 3600:
            filepath.unlink()


__all__ = ['plt', 'sns', 'save_figure', 'clear_old_charts', 'CHARTS_DIR']
