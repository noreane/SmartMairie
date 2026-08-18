# Module 2 — Connecteurs automatisés

## Objectif

Automatiser la récupération de données municipales depuis différentes sources (base interne, fichiers déposés par un agent, open data externe) plutôt que de dépendre d'exports ou de ressaisies manuelles, et produire pour chacune un CSV standardisé écrit dans `data/staging/`, directement exploitable par le Module 1 (nettoyage/GED) via son `CONFIGS`.

## Connecteur MySQL

Se connecte à une base MySQL interne (mock d'un système de gestion municipal) pour en extraire les demandes d'urbanisme et l'état civil.

- Script : `connecteur_mysql.py`
- Sortie : `data/staging/mysql_demandes_urbanisme.csv`, `data/staging/mysql_etat_civil.csv`

## Connecteur Excel/CSV — subventions associations

Lit un fichier (`.xlsx` ou `.csv`) déposé par un agent de la mairie — typiquement un tableau de suivi tenu à la main — pour éliminer la ressaisie manuelle vers d'autres outils.

- Source : `data/sources/subventions_associations.xlsx` (ou `.csv`)
- Sortie : `data/staging/subventions_associations.csv`
- Script : `connecteur_excel.py`

## Connecteur API — écoles de Rennes

Interroge l'API Open Data de Rennes Métropole (Opendatasoft, gratuite, sans clé) pour récupérer automatiquement le jeu de données des écoles maternelles et primaires de Rennes.

- Source : `data.rennesmetropole.fr` (API Explore v2.1, dataset `ecoles-rennes`)
- Sortie : `data/staging/ecoles_rennes.csv`
- Script : `connecteur_api.py`

## Outils

- Python (`requests`, `pandas`, connecteur MySQL)

## Note

Les connecteurs OCR (Module 4) et Transcription (Module 5) écrivent également dans `module2-connecteurs/data/staging/` pour rejoindre le même pipeline, mais vivent dans leurs propres dossiers de module — voir `module4-ocr/README.md` et `module5-transcription/README.md`.