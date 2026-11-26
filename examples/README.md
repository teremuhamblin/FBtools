# Exemples

| Fichier | Description |
| --- | --- |
| [`export-hebdo.sh`](export-hebdo.sh) | Export des commentaires et des Insights, à lancer via cron |
| [`github-actions-publication.yml`](github-actions-publication.yml) | Workflow GitHub Actions de publication avec secrets chiffrés |
| [`programmer_depuis_csv.py`](programmer_depuis_csv.py) | Programmation en lot depuis un CSV via l'API Python |
| [`publications.csv`](publications.csv) | Exemple de calendrier éditorial |

Tous les exemples lisent le jeton depuis `FBTOOLS_ACCESS_TOKEN` ou la configuration locale. Le script Python fonctionne en **simulation** par défaut : ajoutez `--go` pour envoyer.
