# Politique de sécurité

## Versions prises en charge

| Version | Correctifs de sécurité |
| --- | --- |
| 1.0.x | Oui |
| < 1.0 | Non |

## Signaler une vulnérabilité

**N'ouvrez pas d'issue publique.** Utilisez le [signalement privé de vulnérabilité GitHub](https://github.com/teremuhamblin/FBtools/security/advisories/new).

Indiquez :

- la version de FBtools et de Python ;
- la description du problème et son impact ;
- les étapes de reproduction (sans jeton réel) ;
- une proposition de correctif si possible.

Délais visés : accusé de réception sous 72 h, évaluation sous 7 jours, correctif selon la gravité.

## Bonnes pratiques pour les utilisateurs

- **Jetons** : stockez-les avec `fbtools config set-token` (fichier en `chmod 600`) ou dans `FBTOOLS_ACCESS_TOKEN`. Ne les committez jamais.
- **`appsecret_proof`** : définissez `FBTOOLS_APP_SECRET` et activez « Require App Secret » dans les réglages de votre app Meta.
- **Moindre privilège** : n'accordez que les permissions nécessaires à vos commandes.
- **Révocation** : en cas de fuite, révoquez le jeton immédiatement depuis les [paramètres de votre app Meta](https://developers.facebook.com/apps/).
- **CI** : utilisez les *secrets* chiffrés de GitHub Actions, jamais de jetons en clair dans les workflows.

## Périmètre

FBtools n'utilise que l'API Graph officielle de Meta. Les vulnérabilités de la plateforme Meta elle-même relèvent du [programme Meta Bug Bounty](https://www.facebook.com/whitehat).
