# Module 1 — Nettoyage des données & GED

## Objectif

Préparer les documents municipaux pour qu'ils soient exploitables, à la fois par un humain (classement) et par les modules suivants du projet (nettoyage du contenu).

## Volet 1 : GED (Gestion Électronique des Documents)

- Définir une arborescence de dossiers logique (par type-document/année/service)
- Établir une règle de nommage standardisée, ex. : `AAAA-MM-JJ_type-document_service_id.csv`
- Identifier les métadonnées à associer à chaque document (date, service émetteur, type de document)

## Volet 2 : Nettoyage des données

- Nettoyage textuel des champs (correction des problèmes d'encodage avec `ftfy`, normalisation des espaces)
- Détection et rejet des lignes incomplètes (champs essentiels manquants), tracées dans un fichier dédié (`lignes_rejetees.csv`)
- Détection et suppression des doublons de contenu (lignes strictement identiques)
- Structuration des données en sortie : un fichier CSV par document classé, plus un fichier de métadonnées centralisé (`metadonnees.csv`) consolidant toutes les sources dans un schéma commun

## Outils

- Python (`csv`, `os`, `re`, `logging`)
- `python-slugify` pour la normalisation des noms de dossiers/fichiers
- `ftfy` pour la correction des problèmes d'encodage

## Sources de données

Open data de la ville de Rennes (portail data.rennesmetropole.fr) : délibérations, déports des instances municipales.