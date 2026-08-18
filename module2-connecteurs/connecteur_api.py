"""Connecteur API - écoles de Rennes (Module 2).
Récupère les données via l'API Rennes Métropole, puis écrit un CSV standardisé dans module2-connecteurs/data/staging/, prêt à être déclaré comme nouvelle entrée dans le CONFIGS de module1-nettoyage/classement.py.
But : éliminer la ressaisie manuelle de ce fichier vers d'autres outils."""

import os
import logging
from datetime import date

import requests
import pandas as pd

API_URL = "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/ecoles-rennes/records"

DOSSIER_STAGING = os.path.join("module2-connecteurs", "data", "staging")
DELIMITER = ";"
PREFIXE_ID = "ECOLE"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("connecteur_api")

"""Récupère les enregistrements (pagination simple)."""
def recuperer_donnees(limite: int = 100) -> list[dict]:
    tous_les_resultats = []
    offset = 0

    while True:
        reponse = requests.get(
            API_URL,
            params={"limit": limite, "offset": offset},
            timeout=10,
        )
        reponse.raise_for_status()
        resultats = reponse.json().get("results", [])

        if not resultats:
            break

        tous_les_resultats.extend(resultats)
        offset += limite

        if len(resultats) < limite:
            break
    return tous_les_resultats


def construire_id_stable(ligne: dict, index: int, prefixe: str) -> str:
    id_source = ligne.get("recordid") or ligne.get("id")
    if id_source:
        return f"{prefixe}-{id_source}"
    return f"{prefixe}-{str(index + 1).zfill(4)}"


def run():
    try:
        resultats = recuperer_donnees()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur API Rennes : {e}")
        return

    logger.info(f"{len(resultats)} enregistrement(s) récupéré(s)")

    if not resultats:
        logger.warning("Aucun enregistrement reçu")
        return

    df = pd.DataFrame(resultats)
    logger.info(f"Colonnes : {list(df.columns)}")

    if "recordid" not in df.columns and "id" not in df.columns:
        logger.warning("Pas d'ID stable trouvé, fallback sur la position")

    df["date_recuperation"] = date.today().isoformat()
    df["id_projet"] = [construire_id_stable(ligne, i, PREFIXE_ID) for i, ligne in enumerate(resultats)]

    os.makedirs(DOSSIER_STAGING, exist_ok=True)
    chemin = os.path.join(DOSSIER_STAGING, "ecoles_rennes.csv")
    df.to_csv(chemin, index=False, sep=DELIMITER, encoding="utf-8-sig")
    logger.info(f"Export écrit : {chemin} ({len(df)} lignes)")


if __name__ == "__main__":
    run()