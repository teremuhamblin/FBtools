# Automatisation

## Cron

```cron
# Export des commentaires chaque lundi à 8 h
0 8 * * 1  FBTOOLS_ACCESS_TOKEN=... /home/me/.local/bin/fbtools comments export 123_456 -o /data/commentaires.csv
```

Voir [`examples/export-hebdo.sh`](https://github.com/teremuhamblin/FBtools/blob/main/examples/export-hebdo.sh).

## GitHub Actions

Un workflow d'exemple publie un message stocké dans le dépôt, avec le jeton dans les *secrets* chiffrés : [`examples/github-actions-publication.yml`](https://github.com/teremuhamblin/FBtools/blob/main/examples/github-actions-publication.yml).

```yaml
- run: pip install git+https://github.com/teremuhamblin/FBtools.git
- run: fbtools posts publish --page "$PAGE_ID" --message-file annonce.txt -y
  env:
    FBTOOLS_ACCESS_TOKEN: ${{ secrets.FBTOOLS_ACCESS_TOKEN }}
    PAGE_ID: ${{ vars.FB_PAGE_ID }}
```

## Docker

```bash
docker run --rm -e FBTOOLS_ACCESS_TOKEN -v "$PWD:/work" \
  ghcr.io/teremuhamblin/fbtools:latest comments export 123_456 -o /work/c.csv
```

## Programmation en lot (API Python)

[`examples/programmer_depuis_csv.py`](https://github.com/teremuhamblin/FBtools/blob/main/examples/programmer_depuis_csv.py) programme une série de publications à partir d'un CSV en utilisant directement `GraphClient`.
