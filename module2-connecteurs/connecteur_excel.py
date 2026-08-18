"""Connecteur Excel/CSV - Module 2 (Smart Mairie)Lit un fichier source (.xlsx OU .csv) déposé par un agent de la mairie
(ex: tableau de suivi des subventions associations tenu à la main), et écrit un CSV standardisé dans module2-connecteurs/data/staging/, 
prêt à être déclaré comme nouvelle entrée dans le CONFIGS de module1-nettoyage/classement.py.
But : éliminer la ressaisie manuelle de ce fichier vers d'autres outils."""

import os
import pandas as pd

# Dossier où l'agent dépose le fichier source (Excel ou CSV)
DOSSIER_SOURCE = os.path.join("module2-connecteurs", "data", "sources")
NOM_FICHIER_SOURCE = "subventions_associations"

DOSSIER_STAGING = os.path.join("module2-connecteurs", "data", "staging")
DELIMITER = ";"


def trouver_fichier_source() -> str:
    chemin_xlsx = os.path.join(DOSSIER_SOURCE, f"{NOM_FICHIER_SOURCE}.xlsx")
    chemin_csv = os.path.join(DOSSIER_SOURCE, f"{NOM_FICHIER_SOURCE}.csv")

    if os.path.exists(chemin_xlsx):
        return chemin_xlsx
    if os.path.exists(chemin_csv):
        return chemin_csv

    raise FileNotFoundError(
        f"Aucun fichier trouvé : ni {chemin_xlsx} ni {chemin_csv}. "
        "Dépose le fichier de l'agent dans ce dossier avant de relancer le connecteur."
    )


def lire_fichier(chemin: str) -> pd.DataFrame:
    if chemin.endswith(".xlsx"):
        return pd.read_excel(chemin)
    return pd.read_csv(chemin, sep=DELIMITER, encoding="utf-8-sig")


def exporter_csv(df: pd.DataFrame) -> str:
    os.makedirs(DOSSIER_STAGING, exist_ok=True)
    chemin = os.path.join(DOSSIER_STAGING, "subventions_associations.csv")
    df.to_csv(chemin, index=False, sep=DELIMITER, encoding="utf-8-sig")
    print(f"[OK] Export écrit : {chemin} ({len(df)} lignes)")
    return chemin


def run():
    chemin_source = trouver_fichier_source()
    print(f"[INFO] Fichier source détecté : {chemin_source}")
    df = lire_fichier(chemin_source)
    exporter_csv(df)


if __name__ == "__main__":
    run()
