#!/usr/bin/env bash
# Export hebdomadaire des commentaires et des statistiques d'une Page.
# Usage : FBTOOLS_ACCESS_TOKEN=... ./export-hebdo.sh <PAGE_ID> <POST_ID> [dossier]
set -euo pipefail

PAGE_ID="${1:?ID de Page requis}"
POST_ID="${2:?ID de publication requis}"
OUT="${3:-./exports}"
DATE="$(date +%Y-%m-%d)"
SINCE="$(date -d '7 days ago' +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d)"

mkdir -p "$OUT"
fbtools comments export "$POST_ID" -o "$OUT/commentaires-$DATE.csv"
fbtools insights --page "$PAGE_ID" --since "$SINCE" --until "$DATE" -f csv > "$OUT/insights-$DATE.csv"
echo "Exports écrits dans $OUT"
