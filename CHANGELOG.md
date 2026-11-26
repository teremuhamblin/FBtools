# Journal des modifications

Toutes les évolutions notables sont consignées ici.
Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) · Versions : [SemVer](https://semver.org/lang/fr/).

## [Non publié]

### Ajouté
- Nouvelles tentatives automatiques sur les coupures réseau et les délais dépassés.
- Message clair lorsque le fichier de configuration est corrompu.
- Marqueur `py.typed` : le paquet est typé (PEP 561).
- CI GitHub Actions : lint, format, mypy strict, tests Linux / macOS / Windows × Python 3.10 à 3.14, build du paquet.
- Analyse CodeQL, revue des dépendances, Dependabot.
- Workflow de release : paquet, attestation de provenance, release GitHub, image Docker GHCR, PyPI optionnel.
- Documentation MkDocs Material publiée sur GitHub Pages.
- Dockerfile (utilisateur non root), Makefile, pre-commit (Ruff, gitleaks), EditorConfig.
- Fichiers communautaires : CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT, CITATION, modèles d'issues et de PR, CODEOWNERS.
- Exemples : cron, GitHub Actions, programmation en lot depuis un CSV.
- 40 nouveaux tests (52 au total), couverture ≈ 97 %.

### Modifié
- Code formaté avec Ruff, règles de lint étendues, typage strict complet.
- Le workflow Jekyll est remplacé par la documentation MkDocs.

## [1.0.0] — 2026-11-26

### Ajouté
- Première version : configuration, `whoami`, `pages list`, `posts list/publish/delete`,
  programmation de publications, `comments export`, `insights`.
- Client API Graph v27.0 avec pagination, retries et `appsecret_proof`.
- Sorties table / JSON / CSV, suite de tests hors ligne.

[Non publié]: https://github.com/teremuhamblin/FBtools/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/teremuhamblin/FBtools/releases/tag/v1.0.0
