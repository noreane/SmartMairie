# Module 3 — Dashboard Power BI

## Objectif

Donner une vue d'ensemble de pilotage à partir des données déjà nettoyées et classées par le Module 1, pour permettre à un agent ou un élu de suivre l'activité municipale sans avoir à consulter chaque source séparément.

## Dashboard



4 visuels connectés aux CSV classés du Module 1 :

- **KPI card** : nombre total de documents par type
- **Camembert** : répartition des documents par `type_document` (mesure DAX `COUNTROWS`)
- **Courbe temporelle** : évolution du volume de documents dans le temps
- **Carte géographique** : localisation des écoles de Rennes (latitude/longitude)

Un segment (slicer) par **service** permet de filtrer dynamiquement l'ensemble du dashboard d'un simple clic.

## Source de données

CSV classés par le Module 1 (`module1-nettoyage/data/classe/`) — connexion directe, sans passer par MySQL, le volume de données ne justifiant pas une comparaison multi-sources à cette échelle.

## Outils

- Power BI Desktop
- Power Query (nettoyage et typage des colonnes, notamment latitude/longitude)
- DAX (mesures)