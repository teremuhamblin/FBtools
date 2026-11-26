# FBtools v1.0

CLI Python pour gérer vos **Pages Facebook** depuis le terminal via l'**API Graph de Meta** (v27.0 par défaut).

## Fonctionnalités v1.0

| Commande | Rôle |
| --- | --- |
| `fbtools config set-token / set-page / set-version / show` | Configuration locale (fichier `chmod 600`) |
| `fbtools whoami` | Identité du jeton et permissions accordées |
| `fbtools pages list` | Pages administrées |
| `fbtools posts list` | Dernières publications d'une Page |
| `fbtools posts publish` | Publier ou **programmer** (`--at`), avec `--dry-run` et confirmation |
| `fbtools posts delete` | Supprimer une publication |
| `fbtools comments export` | Export CSV/JSON de tous les commentaires (pagination automatique) |
| `fbtools insights` | Statistiques de Page (métriques configurables) |

Toutes les commandes de lecture acceptent `-f table|json|csv`.

Points techniques : récupération automatique du jeton de Page, pagination `paging.next`, nouvelles tentatives avec backoff sur les limites de débit (codes 4, 17, 32, 613…), `appsecret_proof` optionnel, erreurs lisibles avec `fbtrace_id`.

## Installation

```bash
cd fbtools
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
fbtools --help
```

## Prérequis Meta

1. Créez une app sur [Meta for Developers](https://developers.facebook.com/apps/).
2. Générez un jeton utilisateur (Graph API Explorer) avec les permissions :
   `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `read_insights`
   (et `pages_read_user_content` pour les commentaires).
3. Pour un usage durable, échangez-le contre un jeton longue durée.

## Exemples

```bash
fbtools config set-token                  # saisie masquée
fbtools whoami
fbtools pages list
fbtools config set-page 1234567890

fbtools posts list -n 10 -f csv > posts.csv
fbtools posts publish -m "Bonjour à tous" --link https://exemple.fr
fbtools posts publish --message-file annonce.txt --at 2026-12-01T09:00+01:00 -y
fbtools comments export 1234567890_987654321 -o commentaires.csv
fbtools insights --period day --since 2026-11-01 --until 2026-11-25
```

Variables d'environnement (prioritaires) : `FBTOOLS_ACCESS_TOKEN`, `FBTOOLS_APP_SECRET`, `FBTOOLS_API_VERSION`, `FBTOOLS_CONFIG_DIR`.

## Développement

```bash
pytest          # tests sans réseau (session HTTP simulée)
ruff check src tests
```

## Structure

```
fbtools/
├── pyproject.toml
├── src/fbtools/
│   ├── __init__.py   # version, version d'API par défaut
│   ├── cli.py        # commandes Click
│   ├── client.py     # client API Graph (pagination, retries, jetons de Page)
│   ├── config.py     # configuration locale + variables d'environnement
│   └── output.py     # rendu table / JSON / CSV
└── tests/
```

## Notes

- Certaines métriques Insights ont été retirées par Meta (ex. `page_impressions_unique`) ; utilisez `--metric` pour choisir les vôtres.
- Respectez les [Conditions de la plateforme Meta](https://developers.facebook.com/terms/) : FBtools n'utilise que l'API officielle.

Licence MIT.
