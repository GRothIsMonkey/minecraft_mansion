#!/usr/bin/env bash
# Build the AshgroveManor plugin JAR (Bukkit/Spigot 1.8.8, Java 8 bytecode).
#
#   tools/build_plugin.sh [spigot-api-1.8.8-R0.1-SNAPSHOT-shaded.jar]
#
# 1. Regenerates the plugin data from the design (tools/plugin_export.py), which first proves
#    the command list equals the 34 shipped console files (FINAL_MANIFEST.json hashes).
# 2. Compiles plugin/src/main/java against the Spigot 1.8.8 API.
# 3. Writes AshgroveManor-<version>.jar in the repository root.
#
# The API jar comes from Spigot's BuildTools (--rev 1.8.8) or
# https://hub.spigotmc.org/nexus/content/repositories/snapshots/org/spigotmc/spigot-api/1.8.8-R0.1-SNAPSHOT/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API="${1:-$(ls ~/.m2/repository/org/spigotmc/spigot-api/1.8.8-R0.1-SNAPSHOT/spigot-api-1.8.8-R0.1-SNAPSHOT-shaded.jar 2>/dev/null || true)}"
[ -f "$API" ] || { echo "Spigot 1.8.8 API jar not found; pass its path as the first argument" >&2; exit 1; }
VERSION="$(sed -n "s/^version: '\(.*\)'/\1/p" "$ROOT/plugin/src/main/resources/plugin.yml")"

(cd "$ROOT/tools" && python3 plugin_export.py | grep -v 'light pass')

BUILD="$ROOT/plugin/build"
rm -rf "$BUILD" && mkdir -p "$BUILD/classes"
javac --release 8 -encoding UTF-8 -nowarn -Xlint:-deprecation -Xlint:-options -cp "$API" \
      -d "$BUILD/classes" $(find "$ROOT/plugin/src/main/java" -name '*.java')
cp -r "$ROOT/plugin/src/main/resources/." "$BUILD/classes/"
OUT="$ROOT/AshgroveManor-$VERSION.jar"
rm -f "$OUT"
(cd "$BUILD/classes" && jar --create --file "$OUT" --date=2026-01-01T00:00:00Z .)
echo "built $OUT ($(stat -c %s "$OUT") bytes)"
