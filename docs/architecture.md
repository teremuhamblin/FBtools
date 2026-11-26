# Architecture

## Modules

```mermaid
flowchart TB
    U([Utilisateur / script]) --> CLI
    subgraph PKG[src/fbtools]
        CLI[cli.py — commandes Click] --> CONF[config.py — fichier + env]
        CLI --> CLIENT[client.py — pagination, retries, jetons de Page]
        CLI --> OUT[output.py — table / JSON / CSV]
    end
    CONF -.-> FILE[(config.json chmod 600)]
    CLIENT <-->|HTTPS| API[API Graph Meta]
```

| Module | Responsabilité |
| --- | --- |
| `__init__.py` | Version du paquet, version d'API par défaut |
| `cli.py` | Commandes Click, validation des entrées, codes de sortie |
| `client.py` | `GraphClient` : authentification, `appsecret_proof`, pagination, retries, cache des jetons de Page |
| `config.py` | Chargement/sauvegarde de la configuration, priorité des variables d'environnement |
| `output.py` | Aplatissement des objets imbriqués et rendu table / JSON / CSV |

## Cycle d'une publication

```mermaid
sequenceDiagram
    autonumber
    actor U as Utilisateur
    participant C as fbtools
    participant G as API Graph
    U->>C: posts publish -m "…" [--at]
    C->>G: GET /{page-id}?fields=access_token
    G-->>C: Jeton de Page (mis en cache)
    C->>U: Confirmation (sauf -y)
    C->>G: POST /{page-id}/feed
    G-->>C: id de la publication
    C-->>U: Publiée / Programmée
```

## Fiabilité

- **Nouvelles tentatives** sur les codes temporaires ou de limitation `1, 2, 4, 17, 32, 341, 613`, sur les erreurs HTTP 5xx et sur les coupures réseau.
- **Backoff exponentiel** : 1 s, 2 s, 4 s… plafonné à 30 s (`max_retries=3` par défaut).
- **Erreurs lisibles** : message, code, sous-code et `fbtrace_id` pour le support Meta.

```mermaid
stateDiagram-v2
    direction LR
    [*] --> Requête
    Requête --> Succès: 2xx
    Requête --> Attente: code temporaire / 5xx / réseau
    Attente --> Requête: backoff
    Attente --> Erreur: tentatives épuisées
    Requête --> Erreur: autre erreur
    Succès --> [*]
    Erreur --> [*]
```
