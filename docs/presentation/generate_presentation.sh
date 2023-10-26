#!/bin/bash

set -euo pipefail

echo "generate diagrams"
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
DIAGRAMS_FOLDER="$SCRIPT_DIR/diagrams"

for file in "$DIAGRAMS_FOLDER"/*.py; do
  if [ -f "$file" ]; then
    python "$file"
  fi
done

echo "generate qrcode"
python "$SCRIPT_DIR/static/qrcode_gen.py"

echo "generate presentation"
marp PRESENTATION.md
