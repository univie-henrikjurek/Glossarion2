#!/bin/bash
set -e

DATA_DIR="${DATA_DIR:-./data}"
mkdir -p "$DATA_DIR"

echo "Glossarion2 Dictionary Ingestion Script"
echo "==================================="
echo ""
echo "Data directory: $DATA_DIR"
echo ""

download_freedict() {
    local pair=$1
    local url=$2
    local name=$3

    local dir="$DATA_DIR/$name"
    mkdir -p "$dir"

    echo "Downloading $name..."
    local zipfile="/tmp/${name}.zip"

    if curl -L -o "$zipfile" "$url" 2>/dev/null; then
        echo "Extracting..."
        unzip -o "$zipfile" -d "$dir" 2>/dev/null || true

        for file in "$dir"/*; do
            if [[ -f "$file" && ! "$file" =~ \.(ifo|idx|dict) ]]; then
                ext="${file##*.}"
                if [[ -f "${file%.$ext}.ifo" ]]; then
                    mv "$file" "${file%.$ext}.ifo" 2>/dev/null || true
                fi
            fi
        done

        if ls "$dir"/*.ifo 1> /dev/null 2>&1; then
            local ifo_file=$(ls "$dir"/*.ifo | head -1)
            local base_name=$(basename "$ifo_file" .ifo)
            if [[ "$base_name" != "$name" ]]; then
                for ext in ifo idx dict.dz; do
                    if [[ -f "$dir/$base_name.$ext" ]]; then
                        mv "$dir/$base_name.$ext" "$dir/$name.$ext"
                    fi
                done
            fi
            echo "✓ $name installed"
        else
            echo "✗ $name failed to install"
            rm -rf "$dir"
        fi

        rm -f "$zipfile"
    else
        echo "✗ Failed to download $name"
        rm -rf "$dir"
    fi
}

download_freedict \
    "deu-eng" \
    "https://downloads.freedict.org/freedict-1b.deu-eng.zip" \
    "fd-deu-eng"

download_freedict \
    "eng-deu" \
    "https://downloads.freedict.org/freedict-1b.eng-deu.zip" \
    "fd-eng-deu"

download_freedict \
    "deu-fra" \
    "https://downloads.freedict.org/freedict-1b.deu-fra.zip" \
    "fd-deu-fra"

download_freedict \
    "fra-deu" \
    "https://downloads.freedict.org/freedict-1b.fra-deu.zip" \
    "fd-fra-deu"

download_freedict \
    "eng-fra" \
    "https://downloads.freedict.org/freedict-1b.eng-fra.zip" \
    "fd-eng-fra"

download_freedict \
    "fra-eng" \
    "https://downloads.freedict.org/freedict-1b.fra-eng.zip" \
    "fd-fra-eng"

echo ""
echo "Ingestion complete!"
echo ""

echo "Installed dictionaries:"
for dir in "$DATA_DIR"/*/; do
    if [[ -d "$dir" ]]; then
        name=$(basename "$dir")
        echo "  - $name"
    fi
done

echo ""
echo "To use these dictionaries, restart the dictionary service:"
echo "  docker compose restart dictionary"