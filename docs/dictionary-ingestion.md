# Dictionary Ingestion Guide

## Overview

Glossarion2 supports StarDict-compatible dictionaries for lexical lookup.

## Dictionary Sources

### FreeDict

FreeDict provides open-source dictionaries in StarDict format:

- https://freedict.org/downloads/
- https://freedict.org/support/dictionaries/

Available language pairs:
- DE ↔ EN
- DE ↔ FR
- EN ↔ FR
- And many more...

### Wiktionary

Wiktionary-derived dictionaries available from:

- https://www.wiktionary.org/
- https://github.com/tatuylonen/wiktextract

## StarDict Format

StarDict consists of three files:

| File | Purpose |
|------|---------|
| `.ifo` | Header/metadata |
| `.idx` | Word index |
| `.dict.dz` | Compressed dictionary data |

## Manual Ingestion

### 1. Download FreeDict

```bash
mkdir -p data/fd-deu-eng
cd data/fd-deu-eng

# Download English-German dictionary
wget https://downloads.freedict.org/freedict-1b.deu-eng.zip
unzip freedict-1b.deu-eng.zip
mv *.ifo fd-deu-eng.ifo
mv *.idx fd-deu-eng.idx
mv *.dict.dz fd-deu-eng.dict.dz
```

### 2. Verify Installation

```bash
# Check files exist
ls -la data/fd-deu-eng/

# Restart dictionary service
docker compose restart dictionary

# Check logs
docker compose logs dictionary
```

### 3. Test Lookup

```bash
curl "http://localhost:8001/lookup?text=Hund&source=de&target=en"
```

## Ingestion Script

Run the provided script:

```bash
# Download and ingest FreeDict dictionaries
./scripts/ingest_freedict.sh
```

## Custom Glossary

Create a JSON glossary:

```json
{
  "honeybadger": {
    "de": "Honigdachs",
    "fr": "ratel"
  },
  "Dachs": {
    "en": "badger",
    "fr": "blaireau"
  },
  "technical_term": {
    "de": "Fachbegriff"
  }
}
```

Mount in `docker-compose.yml`:

```yaml
api:
  volumes:
    - ./data/glossary.json:/app/data/glossary.json
```

## Dictionary Format Converter

Convert other formats to JSON glossary:

### CSV to JSON

```python
import csv
import json

glossary = {}
with open('terms.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        term = row['term']
        glossary[term] = {
            'en': row['en'],
            'de': row['de'],
            'fr': row['fr']
        }

with open('glossary.json', 'w') as f:
    json.dump(glossary, f, indent=2, ensure_ascii=False)
```

### TSV to JSON

```python
import csv
import json

glossary = {}
with open('terms.tsv', 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        term = row['term']
        glossary[term] = {
            lang: row[lang]
            for lang in ['en', 'de', 'fr', 'it', 'pl']
            if lang in row
        }

with open('glossary.json', 'w') as f:
    json.dump(glossary, f, indent=2, ensure_ascii=False)
```

## Data Directory Structure

```
data/
├── glossary.json              # Custom glossary (gitignore)
├── fd-deu-eng/              # FreeDict German-English
│   ├── fd-deu-eng.ifo
│   ├── fd-deu-eng.idx
│   └── fd-deu-eng.dict.dz
├── fd-eng-deu/              # FreeDict English-German
└── fd-fre-eng/             # FreeDict French-English
```

## Performance Notes

- StarDict index loaded in memory (~100-300MB per dictionary)
- Only active dictionaries are loaded
- Use JSON glossary for small term sets (< 1000 terms)
- Use StarDict for large dictionaries

## Troubleshooting

### Dictionary Not Found

```bash
# Check directory structure
docker compose exec dictionary ls -la /data

# Verify .ifo file
docker compose exec dictionary cat /data/fd-deu-eng/fd-deu-eng.ifo | head
```

### Index Not Loading

```bash
# Check file permissions
docker compose exec dictionary ls -la /data/*/

# Rebuild dictionary service
docker compose build dictionary
docker compose up -d dictionary
```