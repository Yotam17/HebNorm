#!/usr/bin/env bash
set -euo pipefail

REQ_FILE=${1:-requirements.models.txt}
WHEEL_DIR=${2:-wheels}

mkdir -p "$WHEEL_DIR"

echo "🔍 Checking for wheels in $WHEEL_DIR ..."
while IFS= read -r line; do
  # מדלגים על שורות ריקות, הערות או options (מתחילים ב־--)
  [[ -z "$line" || "$line" == \#* || "$line" == --* ]] && continue

  pkg=$(echo "$line" | tr -d '[:space:]')
  pkg_file=$(echo "$pkg" | sed 's/==/-/')

  if ls "$WHEEL_DIR"/${pkg_file}-*.whl > /dev/null 2>&1; then
    echo "✅ Found cached wheel for $pkg"
  else
    echo "⬇️  Downloading $pkg ..."
    pip download "$pkg" -d "$WHEEL_DIR"
  fi
done < "$REQ_FILE"

echo "🎉 Done! Wheels are ready in $WHEEL_DIR/"
