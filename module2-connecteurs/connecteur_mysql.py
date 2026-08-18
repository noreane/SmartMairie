""" Connecteur MySQL - Module 2 (Smart Mairie)
Extrait les tables de mairie_db et écrit un CSV brut par table dans module2-connecteurs/data/staging/, prêt à être déclaré comme nouvelle 
entrée dans le dict CONFIGS de module1-nettoyage/classement.py (pas de renommage de colonnes : classement.py s'adapte via colonne_date /
colonne_matiere / colonne_id / delimiter déclarés dans CONFIGS) """

import os
import pandas as pd
from sqlalchemy import create_engine

# Configuration de connexion
DB_USER = "root"
DB_PASSWORD = ""          
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "mairie_db"

DOSSIER_STAGING = os.path.join("module2-connecteurs", "data", "staging")
DELIMITER = ";" 


def get_engine():
    url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


def extraire_table(nom_table: str) -> pd.DataFrame:
    """Extrait une table MySQL, sous forme de DataFrame."""
    engine = get_engine()
    return pd.read_sql_table(nom_table, engine)


def exporter_csv(df: pd.DataFrame, nom_source: str) -> str:
    os.makedirs(DOSSIER_STAGING, exist_ok=True)
    chemin = os.path.join(DOSSIER_STAGING, f"mysql_{nom_source}.csv")
    df.to_csv(chemin, index=False, sep=DELIMITER, encoding="utf-8-sig")
    print(f"[OK] Export écrit : {chemin} ({len(df)} lignes)")
    return chemin


def run():
    tables = ["demandes_urbanisme", "etat_civil"]
    chemins = {}
    for nom_table in tables:
        df = extraire_table(nom_table)
        chemins[nom_table] = exporter_csv(df, nom_table)
    return chemins


if __name__ == "__main__":
    run()
