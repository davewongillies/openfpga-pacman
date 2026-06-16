#!/usr/bin/env bash
# Package the staged dist/ SD layout into a release zip named <Author>.<Shortname>_<Version>.zip.
# Run build.sh first to stage dist/. Produces release/<name>.zip ready to attach to a GitHub release.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"

read -r AUTHOR SHORT VER < <(python3 - "$ROOT/core.json" <<'PY'
import json,sys
m=json.load(open(sys.argv[1]))["core"]["metadata"]
print(m["author"], m["shortname"], m["version"])
PY
)

CORE="$AUTHOR.$SHORT"
NAME="${CORE}_${VER}.zip"
OUT="$ROOT/release/$NAME"

# Sanity: dist must be staged and version-consistent.
[ -f "$DIST/Cores/$CORE/bitstream.rbf_r" ] || { echo "!!! $DIST/Cores/$CORE/bitstream.rbf_r missing — run build.sh first." >&2; exit 1; }
DIST_VER=$(python3 -c "import json;print(json.load(open('$DIST/Cores/$CORE/core.json'))['core']['metadata']['version'])")
[ "$DIST_VER" = "$VER" ] || { echo "!!! dist core.json is $DIST_VER but repo is $VER — re-stage (build.sh)." >&2; exit 1; }

mkdir -p "$ROOT/release"
rm -f "$OUT"
# Zip the three SD trees; drop the .gitkeep placeholders (empty dirs are still preserved).
( cd "$DIST" && zip -r -X -q "$OUT" Assets Cores Platforms -x '*.gitkeep' )

echo "wrote $OUT"
unzip -l "$OUT"
