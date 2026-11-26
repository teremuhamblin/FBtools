---
hide:
  - navigation
---

# FBtools

**CLI Python pour gérer vos Pages Facebook depuis le terminal via l'API Graph de Meta** (v27.0 par défaut).

<div class="grid cards" markdown>

-   :material-send-clock:{ .lg } **Publier et programmer**

    ---

    Publication immédiate ou programmée (`--at`), avec `--dry-run` et confirmation.

    [:octicons-arrow-right-24: Commandes](commandes.md#publications)

-   :material-file-export:{ .lg } **Exporter**

    ---

    Tous les commentaires d'une publication en CSV ou JSON, pagination automatique.

    [:octicons-arrow-right-24: Export](commandes.md#commentaires)

-   :material-chart-line:{ .lg } **Mesurer**

    ---

    Statistiques de Page avec métriques, périodes et plages de dates configurables.

    [:octicons-arrow-right-24: Insights](commandes.md#insights)

-   :material-robot:{ .lg } **Automatiser**

    ---

    Cron, GitHub Actions, Docker : FBtools est conçu pour les scripts.

    [:octicons-arrow-right-24: Automatisation](automatisation.md)

</div>

## En 30 secondes

```bash
pip install git+https://github.com/teremuhamblin/FBtools.git
fbtools config set-token          # saisie masquée
fbtools pages list
fbtools config set-page 1234567890
fbtools posts publish -m "Bonjour à tous" --dry-run
```

!!! tip "Première fois ?"
    Suivez le guide [Installation](installation.md) puis [Configuration](configuration.md) pour obtenir un jeton Meta avec les bonnes permissions.
