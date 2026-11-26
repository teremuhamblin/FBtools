<a id="top"></a>

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="FBtools v1.0 — Vos Pages Facebook, pilotées depuis le terminal" src="assets/banner-light.svg" width="100%">
</picture>

<br>

![Version](https://img.shields.io/badge/version-1.0-1877F2?style=for-the-badge&logo=semver&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B)
![Graph API](https://img.shields.io/badge/Graph%20API-v27.0-0866FF?style=for-the-badge&logo=meta&logoColor=white)
![Licence](https://img.shields.io/badge/licence-MIT-42B72A?style=for-the-badge)

![CLI](https://img.shields.io/badge/CLI-Click-4B4B4B?style=flat-square&logo=gnubash&logoColor=white)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![Lint](https://img.shields.io/badge/lint-ruff-D7FF64?style=flat-square&logo=ruff&logoColor=black)
![Formats](https://img.shields.io/badge/sortie-table%20%7C%20json%20%7C%20csv-F7B928?style=flat-square)
![Sécurité](https://img.shields.io/badge/config-chmod%20600-E41E3F?style=flat-square&logo=letsencrypt&logoColor=white)

### $\color{#1877F2}{\textsf{CLI Python pour gérer vos Pages Facebook via l'API Graph de Meta}}$

<sub><samp>publier · programmer · supprimer · exporter · mesurer — sans quitter le terminal</samp></sub>

[**Installation**](#installation) &nbsp;•&nbsp; [**Démarrage rapide**](#démarrage-rapide) &nbsp;•&nbsp; [**Commandes**](#référence-des-commandes) &nbsp;•&nbsp; [**Architecture**](#architecture) &nbsp;•&nbsp; [**Développement**](#développement)

</div>

---

## Sommaire

<details open>
<summary><b>Afficher / masquer le sommaire</b></summary>

1. [Aperçu](#aperçu)
2. [Fonctionnalités](#fonctionnalités)
3. [Installation](#installation)
4. [Prérequis Meta](#prérequis-meta)
5. [Démarrage rapide](#démarrage-rapide)
6. [Référence des commandes](#référence-des-commandes)
   - [Configuration](#configuration)
   - [Pages et identité](#pages-et-identité)
   - [Publications](#publications)
   - [Commentaires](#commentaires)
   - [Insights](#insights)
7. [Formats de sortie](#formats-de-sortie)
8. [Variables d'environnement](#variables-denvironnement)
9. [Architecture](#architecture)
   - [Vue d'ensemble](#vue-densemble)
   - [Cycle d'une publication](#cycle-dune-publication)
   - [Pagination automatique](#pagination-automatique)
   - [Limites de débit et backoff](#limites-de-débit-et-backoff)
10. [Structure du projet](#structure-du-projet)
11. [Développement](#développement)
12. [Notes et bonnes pratiques](#notes-et-bonnes-pratiques)
13. [Licence](#licence)

</details>

---

## Aperçu

> [!TIP]
> **FBtools** remplace les allers-retours dans l'interface Meta Business Suite par des commandes courtes, scriptables et versionnables. Idéal pour l'automatisation (cron, CI) et l'export de données.

<table>
<tr>
<td width="33%" valign="top">

#### $\color{#1877F2}{\textsf{Publier}}$
Publication immédiate ou **programmée** (`--at`), avec `--dry-run` et confirmation interactive.

</td>
<td width="33%" valign="top">

#### $\color{#42B72A}{\textsf{Exporter}}$
Tous les commentaires d'une publication en **CSV / JSON**, pagination gérée automatiquement.

</td>
<td width="33%" valign="top">

#### $\color{#F7B928}{\textsf{Mesurer}}$
Statistiques de Page avec **métriques configurables**, périodes et plages de dates.

</td>
</tr>
</table>

<p align="right"><a href="#top">↑ Retour en haut</a></p>

---

## Fonctionnalités

| Commande | Rôle | Type |
| :--- | :--- | :---: |
| `fbtools config set-token / set-page / set-version / show` | Configuration locale (fichier `chmod 600`) | ![config](https://img.shields.io/badge/config-6E7681?style=flat-square) |
| `fbtools whoami` | Identité du jeton et permissions accordées | ![lecture](https://img.shields.io/badge/lecture-1877F2?style=flat-square) |
| `fbtools pages list` | Pages administrées | ![lecture](https://img.shields.io/badge/lecture-1877F2?style=flat-square) |
| `fbtools posts list` | Dernières publications d'une Page | ![lecture](https://img.shields.io/badge/lecture-1877F2?style=flat-square) |
| `fbtools posts publish` | Publier ou **programmer** (`--at`), avec `--dry-run` et confirmation | ![écriture](https://img.shields.io/badge/écriture-E41E3F?style=flat-square) |
| `fbtools posts delete` | Supprimer une publication | ![écriture](https://img.shields.io/badge/écriture-E41E3F?style=flat-square) |
| `fbtools comments export` | Export CSV/JSON de tous les commentaires (pagination automatique) | ![lecture](https://img.shields.io/badge/lecture-1877F2?style=flat-square) |
| `fbtools insights` | Statistiques de Page (métriques configurables) | ![lecture](https://img.shields.io/badge/lecture-1877F2?style=flat-square) |

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'pie1':'#1877F2','pie2':'#6E7681','pie3':'#E41E3F','pieTitleTextSize':'18px','pieSectionTextColor':'#FFFFFF','pieStrokeColor':'#FFFFFF','pieOuterStrokeWidth':'0px'}}}%%
pie showData
    title Répartition des 11 commandes de FBtools v1.0
    "Lecture" : 5
    "Configuration" : 4
    "Écriture" : 2
```

**Points techniques**

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#1877F2','primaryTextColor':'#FFFFFF','lineColor':'#42B72A','fontFamily':'Segoe UI, Helvetica, Arial, sans-serif'}}}%%
mindmap
  root((FBtools))
    Jetons
      Récupération auto du jeton de Page
      appsecret_proof optionnel
      Config chmod 600
    Fiabilité
      Retries avec backoff
      Codes 4, 17, 32, 613…
      Erreurs lisibles + fbtrace_id
    Données
      Pagination paging.next
      Sortie table / json / csv
    Sécurité d'usage
      --dry-run
      Confirmation interactive
      Saisie masquée du jeton
```

<p align="right"><a href="#top">↑ Retour en haut</a></p>

---

## Installation

```bash
cd fbtools
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
fbtools --help
```

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
cd fbtools
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
fbtools --help
```

</details>

<p align="right"><a href="#top">↑ Retour en haut</a></p>

---

## Prérequis Meta

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'fontFamily':'Segoe UI, Helvetica, Arial, sans-serif'}}}%%
flowchart LR
    A["1 · Créer une app<br/>Meta for Developers"]:::meta --> B["2 · Graph API Explorer<br/>jeton utilisateur"]:::meta
    B --> C["3 · Échange contre<br/>jeton longue durée"]:::meta
    C --> D["fbtools config set-token"]:::cli
    D --> E(["Prêt"]):::ok
    classDef meta fill:#1877F2,stroke:#0B5FCC,color:#FFFFFF
    classDef cli fill:#242526,stroke:#42B72A,color:#42B72A,font-family:monospace
    classDef ok fill:#42B72A,stroke:#2E8B1E,color:#FFFFFF
```

1. Créez une app sur [Meta for Developers](https://developers.facebook.com/apps/).
2. Générez un jeton utilisateur (Graph API Explorer) avec les permissions ci-dessous.
3. Pour un usage durable, échangez-le contre un **jeton longue durée**.

| Permission | Nécessaire pour |
| :--- | :--- |
| ![](https://img.shields.io/badge/pages__show__list-1877F2?style=flat-square) | `pages list`, récupération du jeton de Page |
| ![](https://img.shields.io/badge/pages__read__engagement-1877F2?style=flat-square) | `posts list`, lecture des Pages |
| ![](https://img.shields.io/badge/pages__manage__posts-E41E3F?style=flat-square) | `posts publish`, `posts delete` |
| ![](https://img.shields.io/badge/read__insights-F7B928?style=flat-square) | `insights` |
| ![](https://img.shields.io/badge/pages__read__user__content-42B72A?style=flat-square) | `comments export` |

> [!IMPORTANT]
> Ne commitez jamais votre jeton. Utilisez `fbtools config set-token` (saisie masquée, fichier `chmod 600`) ou la variable `FBTOOLS_ACCESS_TOKEN`.

<p align="right"><a href="#top">↑ Retour en haut</a></p>

---

## Démarrage rapide

```bash
fbtools config set-token                  # saisie masquée
fbtools whoami                            # vérifie identité et permissions
fbtools pages list                        # liste vos Pages
fbtools config set-page 1234567890        # définit la Page par défaut
```

$\color{#42B72A}{\texttt{✔ Configuration terminée — vous pouvez publier.}}$

<p align="right"><a href="#top">↑ Retour en haut</a></p>

---

## Référence des commandes

### Configuration

```bash
fbtools config set-token          # enregistre le jeton (saisie masquée)
fbtools config set-page <PAGE_ID> # Page par défaut
fbtools config set-version v27.0  # version de l'API Graph
fbtools config show               # affiche la configuration courante
```

### Pages et identité

```bash
fbtools whoami
fbtools pages list -f json
```

### Publications

```bash
# Lister
fbtools posts list -n 10 -f csv > posts.csv

# Publier immédiatement
fbtools posts publish -m "Bonjour à tous" --link https://exemple.fr

# Programmer depuis un fichier, sans confirmation
fbtools posts publish --message-file annonce.txt --at 2026-12-01T09:00+01:00 -y

# Supprimer
fbtools posts delete <POST_ID>
```

> [!NOTE]
> `--dry-run` affiche la requête qui serait envoyée sans rien publier. Sans `-y`, une confirmation est demandée avant toute écriture.

### Commentaires

```bash
fbtools comments export 1234567890_987654321 -o commentaires.csv
```

### Insights

```bash
fbtools insights --period day --since 2026-11-01 --until 2026-11-25
fbtools insights --metric <METRIQUE> -f json
```

<p align="right"><a href="#top">↑ Retour en haut</a></p>

---

## Formats de sortie

Toutes les commandes de lecture acceptent `-f table|json|csv`.

| Option | Rendu | Usage conseillé |
| :---: | :--- | :--- |
| <kbd>-f table</kbd> | Tableau lisible | Consultation dans le terminal |
| <kbd>-f json</kbd> | JSON structuré | Scripts, `jq`, intégrations |
| <kbd>-f csv</kbd> | CSV | Tableurs, analyses de données |

<p align="right"><a href="#top">↑ Retour en haut</a></p>

---

## Variables d'environnement

Les variables d'environnement sont **prioritaires** sur le fichier de configuration.

| Variable | Rôle |
| :--- | :--- |
| `FBTOOLS_ACCESS_TOKEN` | Jeton d'accès |
| `FBTOOLS_APP_SECRET` | Secret d'app (active `appsecret_proof`) |
| `FBTOOLS_API_VERSION` | Version de l'API Graph |
| `FBTOOLS_CONFIG_DIR` | Répertoire du fichier de configuration |

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'fontFamily':'Segoe UI, Helvetica, Arial, sans-serif'}}}%%
flowchart LR
    ENV["Variables FBTOOLS_*"]:::hi -->|priorité 1| R{{"Valeur retenue"}}:::res
    CFG["Fichier de config<br/>(chmod 600)"]:::mid -->|priorité 2| R
    DEF["Valeurs par défaut<br/>(API v27.0)"]:::lo -->|priorité 3| R
    classDef hi fill:#1877F2,stroke:#0B5FCC,color:#FFFFFF
    classDef mid fill:#F7B928,stroke:#C99316,color:#1C1E21
    classDef lo fill:#E4E6EB,stroke:#BCC0C4,color:#1C1E21
    classDef res fill:#42B72A,stroke:#2E8B1E,color:#FFFFFF
```

<p align="right"><a href="#top">↑ Retour en haut</a></p>

---

## Architecture

### Vue d'ensemble

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'fontFamily':'Segoe UI, Helvetica, Arial, sans-serif','clusterBkg':'#F0F2F5','clusterBorder':'#1877F2'}}}%%
flowchart TB
    U(["Utilisateur / script"]):::user --> CLI
    subgraph PKG["src/fbtools"]
        CLI["cli.py<br/>commandes Click"]:::mod
        CONF["config.py<br/>config + env"]:::mod
        CLIENT["client.py<br/>pagination · retries · jetons de Page"]:::core
        OUT["output.py<br/>table / JSON / CSV"]:::mod
        CLI --> CONF
        CLI --> CLIENT
        CLI --> OUT
    end
    CONF -.-> FILE[("Fichier config<br/>chmod 600")]:::store
    CLIENT <-->|HTTPS| API["API Graph Meta<br/>v27.0"]:::meta
    classDef user fill:#42B72A,stroke:#2E8B1E,color:#FFFFFF
    classDef mod fill:#FFFFFF,stroke:#1877F2,color:#1C1E21
    classDef core fill:#1877F2,stroke:#0B5FCC,color:#FFFFFF
    classDef store fill:#F7B928,stroke:#C99316,color:#1C1E21
    classDef meta fill:#0866FF,stroke:#0548B8,color:#FFFFFF
```

### Cycle d'une publication

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'actorBkg':'#1877F2','actorTextColor':'#FFFFFF','actorBorder':'#0B5FCC','signalColor':'#1C1E21','noteBkgColor':'#FFF4D6','noteBorderColor':'#F7B928','fontFamily':'Segoe UI, Helvetica, Arial, sans-serif'}}}%%
sequenceDiagram
    autonumber
    actor U as Utilisateur
    participant C as fbtools CLI
    participant G as API Graph
    U->>C: posts publish -m "…" [--at] [--dry-run]
    C->>C: Lecture config + variables d'env
    C->>G: GET /me/accounts (jeton utilisateur)
    G-->>C: Jeton de Page
    alt --dry-run
        C-->>U: Affiche la requête, rien n'est envoyé
    else publication réelle
        C->>U: Confirmation ? (sauf -y)
        U-->>C: Oui
        C->>G: POST /{page-id}/feed (+ scheduled_publish_time si --at)
        G-->>C: id de la publication
        C-->>U: Publication créée / programmée
    end
    Note over C,G: En cas d'erreur : message lisible + fbtrace_id
```

### Pagination automatique

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'fontFamily':'Segoe UI, Helvetica, Arial, sans-serif'}}}%%
flowchart LR
    S(["Requête initiale"]):::a --> P["Page de résultats"]:::b
    P --> Q{"paging.next ?"}:::c
    Q -->|oui| N["Requête URL suivante"]:::a --> P
    Q -->|non| F(["Résultat complet<br/>→ table / JSON / CSV"]):::d
    classDef a fill:#1877F2,stroke:#0B5FCC,color:#FFFFFF
    classDef b fill:#FFFFFF,stroke:#1877F2,color:#1C1E21
    classDef c fill:#F7B928,stroke:#C99316,color:#1C1E21
    classDef d fill:#42B72A,stroke:#2E8B1E,color:#FFFFFF
```

### Limites de débit et backoff

Lorsque l'API renvoie un code de limitation (**4, 17, 32, 613…**), FBtools réessaie automatiquement avec un délai croissant.

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'fontFamily':'Segoe UI, Helvetica, Arial, sans-serif'}}}%%
stateDiagram-v2
    direction LR
    [*] --> Requete
    Requete --> Succes: 2xx
    Requete --> Attente: code 4 / 17 / 32 / 613
    Attente --> Requete: backoff puis nouvel essai
    Attente --> Erreur: tentatives épuisées
    Requete --> Erreur: autre erreur
    Succes --> [*]
    Erreur --> [*]: message + fbtrace_id
    classDef ok fill:#42B72A,color:#FFFFFF,stroke:#2E8B1E
    classDef ko fill:#E41E3F,color:#FFFFFF,stroke:#B0142F
    classDef wait fill:#F7B928,color:#1C1E21,stroke:#C99316
    class Succes ok
    class Erreur ko
    class Attente wait
```

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'xyChart': {'plotColorPalette':'#1877F2, #42B72A'}}}}%%
xychart-beta
    title "Backoff exponentiel — profil illustratif"
    x-axis "Tentative" [1, 2, 3, 4, 5]
    y-axis "Délai avant nouvel essai (s)" 0 --> 18
    bar [1, 2, 4, 8, 16]
    line [1, 2, 4, 8, 16]
```

<sub>Graphique illustratif du principe ; les délais et le nombre de tentatives réels sont définis dans <code>client.py</code>.</sub>

<p align="right"><a href="#top">↑ Retour en haut</a></p>

---

## Structure du projet

```text
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

<p align="right"><a href="#top">↑ Retour en haut</a></p>

---

## Développement

```bash
pytest              # tests sans réseau (session HTTP simulée)
ruff check src tests
```

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'git0':'#1877F2','git1':'#42B72A','git2':'#F7B928','gitBranchLabel0':'#FFFFFF','gitBranchLabel1':'#FFFFFF','fontFamily':'Segoe UI, Helvetica, Arial, sans-serif'}}}%%
gitGraph
    commit id: "main"
    branch feature
    checkout feature
    commit id: "code"
    commit id: "pytest ✔"
    commit id: "ruff ✔"
    checkout main
    merge feature id: "merge"
```

<p align="right"><a href="#top">↑ Retour en haut</a></p>

---

## Notes et bonnes pratiques

> [!WARNING]
> Certaines métriques Insights ont été retirées par Meta (ex. `page_impressions_unique`) ; utilisez `--metric` pour choisir les vôtres.

> [!CAUTION]
> Respectez les [Conditions de la plateforme Meta](https://developers.facebook.com/terms/) : FBtools n'utilise que l'API officielle.

---

## Licence

<div align="center">

Distribué sous licence **MIT**.

$\color{#1877F2}{\textsf{FB}}\color{#42B72A}{\textsf{tools}}$ &nbsp;<samp>v1.0</samp>

<a href="#top">↑ Retour en haut</a>

</div>
