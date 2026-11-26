# Commandes

Toutes les commandes de lecture acceptent `-f table|json|csv`. Utilisez `--help` sur n'importe quelle commande pour le détail des options.

## Identité et Pages

```bash
fbtools whoami                 # utilisateur + permissions accordées
fbtools pages list -f json     # Pages administrées (jetons jamais affichés)
```

## Publications

```bash
fbtools posts list -n 10 -f csv > posts.csv
fbtools posts publish -m "Bonjour à tous" --link https://exemple.fr
fbtools posts publish --message-file annonce.txt --at 2026-12-01T09:00+01:00 -y
fbtools posts publish -m "Test" --dry-run
fbtools posts delete 1234567890_987654321
```

| Option | Effet |
| --- | --- |
| `--page ID` | Page cible (sinon Page par défaut) |
| `-m`, `--message` | Texte |
| `--message-file` | Lit le texte depuis un fichier |
| `--link` | Lien à partager |
| `--at` | Programme la publication (ISO 8601, au moins 10 min dans le futur) |
| `--dry-run` | Affiche la requête sans rien envoyer |
| `-y`, `--yes` | Pas de confirmation |

## Commentaires

```bash
fbtools comments export 1234567890_987654321                    # CSV sur stdout
fbtools comments export 1234567890_987654321 -o commentaires.json
fbtools comments export 1234567890_987654321 -n 500 -o top500.csv
```

## Insights

```bash
fbtools insights --period day --since 2026-11-01 --until 2026-11-25
fbtools insights --metric page_follows,page_post_engagements -f csv
```

!!! note
    Meta retire régulièrement des métriques (ex. `page_impressions_unique`). Utilisez `--metric` pour choisir les vôtres.

## Codes de sortie

| Code | Signification |
| --- | --- |
| `0` | Succès |
| `1` | Erreur locale (configuration, valeur invalide) ou annulation |
| `2` | Erreur d'usage (option manquante) ou erreur de l'API Graph |
