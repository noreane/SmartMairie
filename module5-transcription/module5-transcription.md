# Module 5 — Transcription / synthèse

## Objectif

Transcrire automatiquement des enregistrements audio municipaux (interventions en conseil municipal, messages vocaux citoyens) en texte exploitable, avec une synthèse automatique des points clés, pour éviter une retranscription manuelle.

## Fonctionnement

- Transcription : Whisper (modèle `base`, un compromis vitesse/précision adapté à une démo en local sans GPU)
- Synthèse automatique : un LLM local via Ollama (`llama3.2:3B`, déjà utilisé au Module 6) résume chaque transcription en 3 à 5 phrases factuelles
- Deux sorties par fichier audio traité :
  1. Une entrée dans le CSV standardisé, qui alimente le pipeline automatisé du Module 1
  2. Un PDF lisible (transcription complète + synthèse), généré en parallèle pour archive/consultation humaine — ce PDF ne rentre pas dans le pipeline Module 1
- Un fichier audio qui échoue à la transcription est signalé et ignoré, sans interrompre le traitement des autres fichiers du lot
- Le cas d'usage réel testé : un discours audio libre de droits (René Viviani, 1917, domaine public)

## Sources et sorties

- Source : `data/sources/` (fichiers `.wav`, `.mp3`, `.m4a`)
- Sortie pipeline : `module2-connecteurs/data/staging/transcriptions.csv`
- Sortie archive : `data/pdf/` (un PDF par fichier audio)
- Script : `connecteur_transcription.py`

## Outils

- Python (`whisper`, `ollama`, `reportlab`, `pandas`)