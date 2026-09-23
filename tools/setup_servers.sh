#!/usr/bin/env bash
# Download the official vanilla Minecraft 1.8.9 and 1.8.0 server jars for the real-server tests.
#
#   tools/setup_servers.sh [base-dir]        (default: ~/mcservers)
#
# Creates <base>/mc189/server.jar and <base>/mc180/server.jar (checksums verified).
# The tests create their own worlds and server.properties inside those folders and accept
# the Minecraft EULA there (eula=true), which is required to run a server.
set -euo pipefail
BASE="${1:-$HOME/mcservers}"

fetch() {  # dir url sha1
    mkdir -p "$BASE/$1"
    if [ -f "$BASE/$1/server.jar" ] && echo "$3  $BASE/$1/server.jar" | sha1sum -c --quiet 2>/dev/null; then
        echo "$1: already present"
        return
    fi
    curl -sSfL -o "$BASE/$1/server.jar" "$2"
    echo "$3  $BASE/$1/server.jar" | sha1sum -c --quiet
    echo "$1: downloaded to $BASE/$1/server.jar"
}

fetch mc189 https://launcher.mojang.com/v1/objects/b58b2ceb36e01bcd8dbf49c8fb66c55a9f0676cd/server.jar b58b2ceb36e01bcd8dbf49c8fb66c55a9f0676cd
fetch mc180 https://launcher.mojang.com/v1/objects/a028f00e678ee5c6aef0e29656dca091b5df11c7/server.jar a028f00e678ee5c6aef0e29656dca091b5df11c7
