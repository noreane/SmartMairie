import csv
import os
import re
import logging
from datetime import datetime

import ftfy
from slugify import slugify


# Module 1 — Nettoyage des données & GED
#
# Volet 1 (GED) : CONFIGS ci-dessous déclare, pour chaque source, où trouver
# le fichier brut et quelles colonnes utiliser pour construire l'arborescence
# type-document/année/service et le nom de fichier standardisé.
#
# Volet 2 (nettoyage) : nettoyer_texte(), ligne_valide() et la détection de
# doublons dans classer_fichiers() traitent la qualité du contenu.


CONFIGS = {
    "deliberations": {
        "fichier": "module1-nettoyage/data/brut/deliberations-villerennes-2021.csv",
        "delimiter": ";",
        "colonne_date": "DELIB_DATE",
        "colonne_matiere": "DELIB_MATIERE_NOM",
        "colonne_id": "DELIB_ID",
        "type_document": "deliberations"
    },
    "deports_instances_municipales": {
        "fichier": "module1-nettoyage/data/brut/deports_instances_municipales.csv",
        "delimiter": ";",
        "colonne_date": "Date",
        "colonne_matiere": "Titre délib",
        "colonne_id": "ID élu",
        "type_document": "deports_instances_municipales"
    },
    "demandes_urbanisme": {
        "fichier": "module2-connecteurs/data/staging/mysql_demandes_urbanisme.csv",
        "delimiter": ";",
        "colonne_date": "date_depot",
        "colonne_matiere": "type_demande",
        "colonne_id": "id_projet",
        "type_document": "demandes_urbanisme"
    },
    "etat_civil": {
        "fichier": "module2-connecteurs/data/staging/mysql_etat_civil.csv",
        "delimiter": ";",
        "colonne_date": "date_evenement",
        "colonne_matiere": "type_acte",
        "colonne_id": "id_projet",
        "type_document": "etat_civil"
    },
    "subventions_associations": {
        "fichier": "module2-connecteurs/data/staging/subventions_associations.csv",
        "delimiter": ";",
        "colonne_date": "date_demande",
        "colonne_matiere": "objet_demande",
        "colonne_id": "id_projet",
        "type_document": "subventions_associations"
    },
    "ecoles_rennes": {
        "fichier": "module2-connecteurs/data/staging/ecoles_rennes.csv",
        "delimiter": ";",
        "colonne_date": "date_recuperation",
        "colonne_matiere": "secteur",
        "colonne_id": "id_projet",
        "type_document": "ecoles_rennes"
    },
    "courriers_ocr": {
        "fichier": "module2-connecteurs/data/staging/courriers_ocr.csv",
        "delimiter": ";",
        "colonne_date": "date_courrier",
        "colonne_matiere": "objet",
        "colonne_id": "id_projet",
        "type_document": "courriers_ocr"
    },
    "transcriptions": {
        "fichier": "module2-connecteurs/data/staging/transcriptions.csv",
        "delimiter": ";",
        "colonne_date": "date_transcription",
        "colonne_matiere": "objet",
        "colonne_id": "id_projet",
        "type_document": "transcriptions"
    },
}

# Sorties du Volet 1 (GED): Aborescence type-document/année/service et nom de fichier standardisé
DOSSIER_CLASSE = "module1-nettoyage/data/classe"      
FICHIER_METADONNEES = "module1-nettoyage/data/metadonnees.csv"  
FICHIER_REJETS = "module1-nettoyage/data/lignes_rejetees.csv"
FICHIER_LOG = "module1-nettoyage/data/run.log"



FORMATS_DATE = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y")

logger = logging.getLogger("classement")


def configurer_logging():
   # Log à la fois dans la console et dans un fichier run.log persistant
    logger.setLevel(logging.INFO)
    formatteur = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    if not os.path.exists(os.path.dirname(FICHIER_LOG)):
        os.makedirs(os.path.dirname(FICHIER_LOG))

    handler_fichier = logging.FileHandler(FICHIER_LOG, mode="w", encoding="utf-8")
    handler_fichier.setFormatter(formatteur)

    handler_console = logging.StreamHandler()
    handler_console.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(handler_fichier)
    logger.addHandler(handler_console)


def extraire_annee(date_brute):
    # Extrait l'année d'une date, quel que soit le format d'origine (YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY). Retourne None si le format est inconnu
    for fmt in FORMATS_DATE:
        try:
            return str(datetime.strptime(date_brute, fmt).year)
        except ValueError:
            continue
    return None


def nettoyer_texte(texte):
    # Volet 2 — nettoyage textuel appliqué à chaque valeur de chaque ligne
    if not texte:
        return texte
    texte = ftfy.fix_text(texte)          # corrige les problèmes d'encodage
    texte = re.sub(r'\s+', ' ', texte)     # réduit les espaces multiples
    texte = texte.strip()                  # supprime les espaces en début/fin
    return texte


def ligne_valide(ligne, config):
    # Volet 2 — détecte les lignes incomplètes (champs essentiels manquants)
    champs_essentiels = [config["colonne_date"], config["colonne_matiere"], config["colonne_id"]]
    return all(ligne.get(champ) for champ in champs_essentiels)

def classer_fichiers(config, ecrivain_meta, ecrivain_rejets):
    # Lit une source CSV, nettoie chaque ligne (Volet 2), puis la range dans l'arborescence GED avec un nom standardisé (Volet 1)
    if not os.path.exists(DOSSIER_CLASSE):
        os.makedirs(DOSSIER_CLASSE)

    noms_deja_utilises = set()   # évite d'écraser un fichier si deux lignes donnent le même nom
    contenus_deja_vus = set()    # sert à la détection de doublons de contenu (Volet 2)
    compteur_doublons = 0
    compteur_rejets = 0
    compteur_classes = 0

    with open(config["fichier"], mode='r', encoding='utf-8-sig') as fichier_csv:
        lecteur_csv = csv.DictReader(fichier_csv, delimiter=config["delimiter"])

        for ligne in lecteur_csv:
            # Volet 2 : nettoyage textuel de toutes les colonnes avant tout traitement
            ligne = {cle: nettoyer_texte(valeur) for cle, valeur in ligne.items()}

            # Vérification des valeurs manquantes
            if not ligne_valide(ligne, config):
                ecrivain_rejets.writerow({
                    "type_document": config["type_document"],
                    "raison": "champ essentiel manquant",
                    "contenu": str(ligne)
                })
                compteur_rejets += 1
                continue

            date_brute = ligne[config["colonne_date"]]
            annee = extraire_annee(date_brute)
            if annee is None:
                ecrivain_rejets.writerow({
                    "type_document": config["type_document"],
                    "raison": f"format de date non reconnu : '{date_brute}'",
                    "contenu": str(ligne)
                })
                compteur_rejets += 1
                continue

            # Détection de doublon de contenu
            signature = tuple(ligne.values())
            if signature in contenus_deja_vus:
                compteur_doublons += 1
                continue
            contenus_deja_vus.add(signature)

            # Volet 1 (GED) : construction de l'arborescence type-document/année/service 
            matiere_brute = ligne[config["colonne_matiere"]]
            matiere = slugify(matiere_brute)[:50]  # tronqué pour éviter les limites de longueur de chemin Windows
            type_doc = config["type_document"]

            identifiant = slugify(ligne[config["colonne_id"]])

            dossier_cible = os.path.join(DOSSIER_CLASSE, type_doc, annee, matiere)
            if not os.path.exists(dossier_cible):
                os.makedirs(dossier_cible)

            # Nommage standardisé : AAAA-MM-JJ_type-document_service_id.csv
            nom_fichier = f"{date_brute}_{type_doc}_{matiere}_{identifiant}.csv"
            if nom_fichier in noms_deja_utilises:
                compteur = 2
                while f"{date_brute}_{type_doc}_{matiere}_{identifiant}_{compteur}.csv" in noms_deja_utilises:
                    compteur += 1
                nom_fichier = f"{date_brute}_{type_doc}_{matiere}_{identifiant}_{compteur}.csv"
            noms_deja_utilises.add(nom_fichier)

            chemin_fichier = os.path.join(dossier_cible, nom_fichier)

            # Un fichier CSV par document classé (une seule ligne de données)
            with open(chemin_fichier, mode='w', encoding='utf-8-sig', newline='') as fichier_sortie:
                ecrivain_csv = csv.DictWriter(fichier_sortie, fieldnames=lecteur_csv.fieldnames)
                ecrivain_csv.writeheader()
                ecrivain_csv.writerow(ligne)

            # Entrée correspondante dans le fichier de métadonnées centralisé
            ecrivain_meta.writerow({
                "date": date_brute,
                "service": matiere_brute,
                "type_document": type_doc,
                "chemin_fichier": chemin_fichier
            })
            compteur_classes += 1

    logger.info(
        f"{config['type_document']} : {compteur_classes} classé(s), "
        f"{compteur_doublons} doublon(s) ignoré(s), {compteur_rejets} ligne(s) rejetée(s)"
    )


def main():
    configurer_logging()

    with open(FICHIER_METADONNEES, mode='w', encoding='utf-8-sig', newline='') as fichier_meta, \
         open(FICHIER_REJETS, mode='w', encoding='utf-8-sig', newline='') as fichier_rejets:

        champs_meta = ["date", "service", "type_document", "chemin_fichier"]
        ecrivain_meta = csv.DictWriter(fichier_meta, fieldnames=champs_meta)
        ecrivain_meta.writeheader()

        champs_rejets = ["type_document", "raison", "contenu"]
        ecrivain_rejets = csv.DictWriter(fichier_rejets, fieldnames=champs_rejets)
        ecrivain_rejets.writeheader()

        for nom_config, config in CONFIGS.items():
            try:
                classer_fichiers(config, ecrivain_meta, ecrivain_rejets)
            except FileNotFoundError:
                logger.error(f"{nom_config} : fichier source introuvable ({config['fichier']}) — source ignorée")
            except Exception as e:
                logger.error(f"{nom_config} : erreur inattendue ({e}) — source ignorée")

    logger.info(f"Fichier de métadonnées généré : {FICHIER_METADONNEES}")
    logger.info(f"Fichier des lignes rejetées généré : {FICHIER_REJETS}")
    logger.info(f"Log complet du run : {FICHIER_LOG}")


if __name__ == "__main__":
    main()