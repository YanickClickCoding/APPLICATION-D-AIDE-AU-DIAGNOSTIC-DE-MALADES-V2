"""
Synchronisation des données géographiques de maladies depuis l'OMS (GHO API).

Objectif : remplacer, pour les maladies réellement couvertes par l'OMS, les
valeurs statiques de la carte du monde par des données d'actualité issues du
Global Health Observatory (https://www.who.int/data/gho/info/gho-odata-api).

Fonctionnement :
- Le script interroge l'API GHO pour quelques maladies à compte de cas absolu
  par pays (paludisme, tuberculose, VIH). L'API fournit déjà le continent
  (`ParentLocation`), qu'on agrège pour obtenir une répartition en % par
  continent — la VRAIE charge mondiale, par source OMS.
- Le résultat est écrit dans un cache JSON (`who_geo_cache.json`) lu par
  l'endpoint analytics. Les maladies NON couvertes par l'OMS gardent leur
  estimation statique (inchangées).

Robustesse (lancé en tâche de fond au démarrage, ne doit jamais casser) :
- timeout court par requête ;
- si l'API est lente/indisponible, on conserve le cache existant ;
- aucune exception ne remonte : tout échec est journalisé, pas propagé.

Important / honnêteté : seules les maladies listées dans WHO_INDICATORS sont
réellement mises à jour depuis l'OMS. L'OMS ne publie pas de répartition par
continent pour les 122 maladies — les autres restent estimées.
"""
from __future__ import annotations

import json
import logging
import os
import tempfile
import time
from datetime import datetime, timezone
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)

# Base de l'API OData GHO de l'OMS.
GHO_BASE = "https://ghoapi.azureedge.net/api"

# Maladies couvertes → indicateur GHO (compte de cas ABSOLU par pays, agrégeable).
# Clé = nom de maladie tel qu'affiché dans l'application (cf. DISEASE_DISPLAY_NAMES).
WHO_INDICATORS: Dict[str, str] = {
    "Paludisme":   "MALARIA_EST_CASES",              # Estimated number of malaria cases
    "Tuberculose": "TB_e_inc_num",                   # Number of incident tuberculosis cases
    "VIH/SIDA":    "HIV_0000000001",                 # People (all ages) living with HIV
    "Hépatite B":  "HEPATITIS_HBV_LIVINGWITH_NUM",   # People living with chronic hepatitis B
    "Hépatite C":  "HEPATITIS_HCV_LIVINGWITH_CRD_NUM",  # People living with chronic hepatitis C
    "Rougeole":    "WHS3_62",                        # Measles - number of reported cases
    # NB : "Choléra" existe à l'OMS (CHOLERA_0000000001) mais PAS dans notre
    # dataset/modèle — inutile de l'ajouter ici.
}

# Continents tels qu'affichés dans l'app, et correspondance depuis les libellés
# `ParentLocation` renvoyés par l'OMS (régions OMS / continents).
CONTINENTS = ["Afrique", "Europe", "Amérique", "Asie", "Océanie"]
# Note : les 6 régions OMS ne coïncident pas avec les continents. « Western
# Pacific » est dominée par la Chine/Asie de l'Est (et non l'Océanie), on la
# rattache donc à l'Asie pour éviter de gonfler l'Océanie. L'Océanie réelle
# (Pacifique insulaire) y est noyée — limite assumée de la granularité OMS.
_OMS_REGION_TO_CONTINENT = {
    "africa": "Afrique",
    "americas": "Amérique",
    "europe": "Europe",
    "eastern mediterranean": "Asie",   # Moyen-Orient + Afrique du Nord
    "south-east asia": "Asie",
    "western pacific": "Asie",         # dominée par la Chine/Asie de l'Est
}

# Override par pays (code ISO3), prioritaire sur la région OMS. Sert pour les
# pays transcontinentaux dont le rattachement OMS diffère de la carte.
_PAYS_OVERRIDE = {
    "RUS": "Asie",   # Russie : OMS la classe en Europe, mais carte = Asie (Sibérie)
}

# Emplacement du cache (à côté du package app).
_CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "who_geo_cache.json")

# Délai mini entre deux synchronisations effectives (évite de spammer l'API si
# le backend redémarre souvent). 12h.
_MIN_REFRESH_SECONDS = 12 * 3600


def _continent_from_oms(parent_location: Optional[str]) -> Optional[str]:
    if not parent_location:
        return None
    return _OMS_REGION_TO_CONTINENT.get(parent_location.strip().lower())


def _fetch_indicator(code: str, timeout: float = 15.0) -> Optional[Dict[str, float]]:
    """
    Récupère un indicateur GHO et agrège la valeur la plus récente par continent.
    Retourne {continent: somme_valeurs} ou None en cas d'échec.
    """
    url = f"{GHO_BASE}/{code}?$filter=SpatialDimType eq 'COUNTRY'"
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        rows = resp.json().get("value", [])
    except Exception as e:
        logger.warning(f"[WHO sync] Échec récupération {code} : {e}")
        return None

    # Pour chaque pays, ne garder que l'année la plus récente disponible.
    dernier_par_pays: Dict[str, dict] = {}
    for r in rows:
        pays = r.get("SpatialDim")
        annee = r.get("TimeDim") or 0
        val = r.get("NumericValue")
        if pays is None or val is None:
            continue
        if pays not in dernier_par_pays or annee > dernier_par_pays[pays]["annee"]:
            dernier_par_pays[pays] = {"annee": annee, "val": float(val), "parent": r.get("ParentLocation")}

    agg = {c: 0.0 for c in CONTINENTS}
    for pays, info in dernier_par_pays.items():
        # Override par pays (prioritaire) puis région OMS. Aligne l'agrégation
        # sur la coloration de la carte (ex. Russie rattachée à l'Asie).
        cont = _PAYS_OVERRIDE.get(pays) or _continent_from_oms(info["parent"])
        if cont:
            agg[cont] += info["val"]

    if sum(agg.values()) <= 0:
        return None
    return agg


# Plancher minimal (en %) attribué à un continent que l'OMS compte à 0. Les
# données OMS ne recensent que les cas autochtones ; un continent à 0 « réel »
# reçoit néanmoins des cas importés (voyageurs). On évite donc le 0 % strict,
# trompeur, par un petit plancher réaliste, puis on renormalise.
_PLANCHER_PCT = 0.1


def _to_percentages(agg: Dict[str, float]) -> Dict[str, float]:
    total = sum(agg.values()) or 1.0
    pct = {c: agg[c] / total * 100 for c in CONTINENTS}
    # Relever les 0 stricts au plancher (cas importés/résiduels non comptés par l'OMS).
    for c in CONTINENTS:
        if pct[c] <= 0:
            pct[c] = _PLANCHER_PCT
    # Renormaliser pour que la somme reste 100 %.
    s = sum(pct.values()) or 1.0
    return {c: round(pct[c] / s * 100, 1) for c in CONTINENTS}


def _read_cache() -> Optional[dict]:
    try:
        with open(_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_cache(data: dict) -> None:
    """Écriture atomique du cache (évite un fichier corrompu si interruption)."""
    try:
        d = os.path.dirname(_CACHE_PATH)
        fd, tmp = tempfile.mkstemp(prefix="who_geo_", suffix=".tmp", dir=d)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, _CACHE_PATH)
    except Exception as e:
        logger.warning(f"[WHO sync] Écriture cache impossible : {e}")


def get_cached_who_data() -> Dict[str, Dict[str, float]]:
    """
    Renvoie les répartitions OMS en cache : {maladie: {continent: %}}.
    Utilisé par l'endpoint analytics. Vide si pas de cache.
    """
    cache = _read_cache()
    if not cache:
        return {}
    return cache.get("maladies", {})


def sync_who_data(force: bool = False) -> bool:
    """
    Met à jour le cache depuis l'OMS. Ne lève jamais d'exception.
    Retourne True si le cache a été mis à jour, False sinon.
    """
    cache = _read_cache()
    # Respecter le délai mini de rafraîchissement, sauf si forcé.
    if not force and cache:
        last = cache.get("updated_at_epoch", 0)
        if time.time() - last < _MIN_REFRESH_SECONDS:
            logger.info("[WHO sync] Cache OMS récent, pas de rafraîchissement.")
            return False

    resultats: Dict[str, Dict[str, float]] = {}
    for maladie, code in WHO_INDICATORS.items():
        agg = _fetch_indicator(code)
        if agg:
            resultats[maladie] = _to_percentages(agg)
            logger.info(f"[WHO sync] {maladie} ✔ ({code})")
        else:
            logger.warning(f"[WHO sync] {maladie} ✘ — donnée OMS indisponible, valeur conservée")

    if not resultats:
        # Aucun indicateur récupéré : on garde le cache existant tel quel.
        logger.warning("[WHO sync] Aucune donnée OMS récupérée — cache inchangé.")
        return False

    # Fusionner avec l'ancien cache (ne pas perdre les maladies déjà obtenues
    # si une seule requête échoue cette fois-ci).
    ancien = (cache or {}).get("maladies", {})
    ancien.update(resultats)

    _write_cache({
        "source": "OMS — Global Health Observatory (GHO OData API)",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_at_epoch": time.time(),
        "indicateurs": WHO_INDICATORS,
        "maladies": ancien,
    })
    logger.info(f"[WHO sync] Cache OMS mis à jour ({len(resultats)} maladie(s)).")
    return True


def start_background_sync() -> None:
    """
    Lance la synchronisation en tâche de fond (thread daemon). Non bloquant :
    le backend démarre immédiatement, la MAJ se fait en arrière-plan.
    """
    import threading

    def _run():
        try:
            sync_who_data(force=False)
        except Exception as e:  # filet de sécurité ultime
            logger.warning(f"[WHO sync] Erreur inattendue (ignorée) : {e}")

    threading.Thread(target=_run, name="who-data-sync", daemon=True).start()
    logger.info("[WHO sync] Synchronisation OMS lancée en arrière-plan.")
