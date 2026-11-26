# Paquet `fbtools`

| Module | Rôle |
| --- | --- |
| [`__init__.py`](__init__.py) | `__version__` et `DEFAULT_API_VERSION` |
| [`__main__.py`](__main__.py) | Permet `python -m fbtools` |
| [`cli.py`](cli.py) | Commandes Click et gestion des codes de sortie |
| [`client.py`](client.py) | `GraphClient` : authentification, `appsecret_proof`, pagination, retries, jetons de Page |
| [`config.py`](config.py) | Configuration locale (`chmod 600`) et variables d'environnement |
| [`output.py`](output.py) | Rendu table / JSON / CSV |
| `py.typed` | Marqueur PEP 561 : le paquet est typé |

Dépendances : `click` et `requests` uniquement. Voir [l'architecture](../../docs/architecture.md).
