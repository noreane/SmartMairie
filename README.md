# SmartMairie
Projet assistant data/IA pour une collectivité : nettoyage de données, dashboard Power BI, OCR, transcription, RAG.

Assistant data/IA pour une collectivité territoriale, construit autour de 6 modules couvrant l'ensemble des principales étapes d'une mission de transformation numérique en mairie : nettoyage de données, connecteurs automatisés, dashboard de pilotage, OCR d'archives, transcription de réunions, et base de connaissances interrogeable.

## Objectif

Plutôt que de traiter un seul cas d'usage en profondeur, ce projet couvre l'ensemble des missions type d'un poste data en collectivité, pour démontrer une compréhension concrète des contraintes de chaque chantier, même à petite échelle.

## Les 6 modules

| # | Module | Description |
|---|--------|--------------|
| 1 | Nettoyage / GED | Extraction et nettoyage de documents municipaux (délibérations, comptes-rendus) |
| 2 | Connecteurs automatisés | Automatisation de la récupération de données depuis différentes sources (MySQL, Excel, API open data) |
| 3 | Dashboard Power BI | Tableau de bord de pilotage à partir des données nettoyées |
| 4 | OCR archives | Numérisation et extraction de texte depuis des documents scannés |
| 5 | Transcription / synthèse | Transcription et résumé automatique de réunions |
| 6 | RAG + interface | Base de connaissances interrogeable en langage naturel, avec une interface Streamlit |

## Stack technique

- **Langage** : Python
- **Traitement de données** : Pandas
- **Nettoyage de texte** : ftfy, python-slugify
- **Base interne** : MySQL
- **Visualisation** : Power BI
- **OCR** : Tesseract (pytesseract)
- **Transcription** : Whisper
- **RAG** : ChromaDB (base vectorielle), Ollama (embeddings + LLM local)
- **Génération PDF** : reportlab
- **Interface** : Streamlit

## Statut

Les 6 modules sont fonctionnels.