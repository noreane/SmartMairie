# Module 4 — OCR archives

## Objectif

Extraire automatiquement le texte de documents scannés reçus ou archivés par la mairie (courriers, formulaires papier) via OCR, pour les faire entrer dans le même pipeline de nettoyage/classement que les autres sources, plutôt qu'une ressaisie manuelle.

## Fonctionnement

- Moteur : Tesseract OCR, en français (`fra.traineddata` fourni localement au projet pour contourner les soucis de permissions Windows avec l'installation par défaut)
- Cas d'usage testé : extraction d'un formulaire CERFA 12156 (demande de subvention association) — détection des champs référence, date, objet, association, montant via des motifs de texte simples
- Un identifiant de secours (`OCR-AAAAMMJJ-NNN`) est généré si aucune référence n'est détectée dans le document, avec un numéro de séquence unique par fichier pour éviter les collisions entre plusieurs courriers traités le même jour
- Un document qui échoue à l'OCR est signalé et ignoré, sans interrompre le traitement des autres fichiers du lot

## Limite connue

Seules les images (`.png`, `.jpg`, `.jpeg`) sont traitées actuellement — pas encore les PDF, malgré le cas d'usage visé (courriers scannés en PDF). À faire évoluer si des PDF doivent être supportés.

## Sources et sorties

- Source : `data/sources/` (images déposées manuellement)
- Sortie : `module2-connecteurs/data/staging/courriers_ocr.csv`
- Script : `connecteur_ocr.py`

## Outils

- Python (`pytesseract`, `Pillow`, `pandas`, `re`)