# Dépannage

Commencez toujours par :

```bash
fbtools --version
fbtools config show
fbtools whoami
```

## Erreurs fréquentes de l'API Graph

| Code | Signification | Que faire |
| --- | --- | --- |
| `190` | Jeton invalide ou expiré | Régénérez un jeton, idéalement longue durée |
| `10`, `200` | Permission manquante | Vérifiez avec `fbtools whoami` et ajoutez la permission |
| `100` | Paramètre invalide | Vérifiez l'ID, la métrique ou le format de date |
| `4`, `17`, `32`, `613` | Limite de débit | FBtools réessaie automatiquement ; espacez vos appels |
| `341` | Limite d'application atteinte | Patientez avant de relancer |
| `368` | Action bloquée par Meta | Consultez la qualité de la Page dans Meta Business Suite |

Gardez le `fbtrace_id` affiché : c'est l'identifiant à transmettre au support Meta.

## Problèmes locaux

??? question "« Aucun jeton configuré »"
    Lancez `fbtools config set-token` ou définissez `FBTOOLS_ACCESS_TOKEN`.

??? question "« Fichier de configuration illisible »"
    Le fichier JSON est corrompu. Corrigez-le ou supprimez `~/.config/fbtools/config.json` puis reconfigurez.

??? question "« La publication programmée doit être au moins 10 min dans le futur »"
    Meta impose un délai minimal pour la programmation. Précisez aussi le fuseau : `2026-12-01T09:00+01:00`.

??? question "« Impossible d'obtenir le jeton de la Page »"
    Vérifiez que vous administrez la Page et que `pages_show_list` et `pages_manage_posts` sont accordées.

??? question "Une métrique Insights renvoie une erreur"
    Elle a peut-être été retirée par Meta. Choisissez une autre métrique avec `--metric`.
