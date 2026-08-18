# Module 6 — RAG + interface

## Objectif

Rendre l'ensemble des données classées par le Module 1 (toutes sources confondues : délibérations, subventions, écoles, courriers OCR, transcriptions...) interrogeable en langage naturel, plutôt que de devoir chercher manuellement dans les fichiers classés.

## Fonctionnement

- Indexation : chaque document classé est découpé en morceaux (chunks de ~1000 caractères avec chevauchement, pour ne pas couper une information pertinente à la frontière de deux morceaux), puis converti en embedding via Ollama (`nomic-embed-text`) et stocké dans une base vectorielle locale ChromaDB
- L'indexation repart de zéro à chaque exécution pour éviter les doublons dans la base
- Un chunk qui échoue à l'embedding est signalé et ignoré, sans interrompre l'indexation des autres documents
- Interrogation : une interface Streamlit permet de poser une question en langage naturel ; la question est comparée aux embeddings stockés pour retrouver les passages les plus pertinents, à partir desquels un LLM local (Ollama) formule une réponse en citant ses sources

## Sources et sorties

- Source : `module1-nettoyage/data/classe/` (tous les documents classés, toutes sources)
- Base vectorielle : `chroma_db/`
- Scripts : `indexer_rag.py` (indexation), `interroger_rag.py` (recherche/réponse en ligne de commande), `interface_rag.py` (interface Streamlit)

## Outils

- Python (`ollama`, `chromadb`, `streamlit`)



## Lancement

python -m streamlit run module6-rag/interface_rag.py