# Tests

Suite **100 % hors ligne** : aucun appel réseau n'est effectué.

| Fichier | Couverture |
| --- | --- |
| [`conftest.py`](conftest.py) | `FakeSession` / `FakeResponse` et isolation de la configuration (`tmp_path`) |
| [`test_client.py`](test_client.py) | Pagination, retries, erreurs réseau, `appsecret_proof`, jetons de Page |
| [`test_cli.py`](test_cli.py) | Version, configuration, `--dry-run`, validation des dates |
| [`test_cli_commands.py`](test_cli_commands.py) | Toutes les commandes avec un client simulé, codes de sortie |
| [`test_config.py`](test_config.py) | Priorité des variables, fichier corrompu, droits `600`, masquage |
| [`test_output.py`](test_output.py) | Aplatissement, table, CSV, JSON |

```bash
pytest                                   # rapide
pytest --cov --cov-report=term-missing   # avec couverture (seuil : 80 %)
```
