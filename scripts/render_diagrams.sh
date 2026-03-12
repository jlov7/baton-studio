#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIAGRAM_DIR="$ROOT_DIR/assets/diagrams"

for src in "$DIAGRAM_DIR"/*.mmd; do
  out="${src%.mmd}.svg"
  npx -y @mermaid-js/mermaid-cli -i "$src" -o "$out"
done
