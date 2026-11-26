# API Python

FBtools s'utilise aussi comme bibliothèque. Le paquet est typé (`py.typed`).

```python
from fbtools.client import GraphAPIError, GraphClient
from fbtools.config import Config

cfg = Config.load()  # fichier + variables d'environnement
client = GraphClient(cfg.access_token or "", cfg.api_version, cfg.app_secret)

for page in client.pages():
    print(page["id"], page["name"])

try:
    res = client.publish("1234567890", message="Bonjour", scheduled_unix=1_900_000_000)
    print(res["id"])
except GraphAPIError as exc:
    print(exc.code, exc.fbtrace_id)
```

## `GraphClient`

| Méthode | Description |
| --- | --- |
| `me()` | Identité du jeton |
| `permissions()` | Permissions accordées / refusées |
| `pages()` | Pages administrées (met en cache leurs jetons) |
| `page_token(page_id)` | Jeton de Page (récupéré puis mis en cache) |
| `posts(page_id, limit=25)` | Dernières publications |
| `publish(page_id, message, link, scheduled_unix)` | Publie ou programme |
| `delete_post(post_id)` | Supprime une publication |
| `comments(object_id, limit=None)` | Tous les commentaires |
| `insights(page_id, metrics, period, since, until)` | Statistiques |
| `paginate(path, limit=None, **params)` | Itérateur générique suivant `paging.next` |
| `request(method, path, params, data, token)` | Appel bas niveau avec retries |

Paramètres du constructeur : `access_token`, `api_version="v27.0"`, `app_secret=None`, `timeout=30.0`, `max_retries=3`, `session=None` (injectez une session pour les tests).
