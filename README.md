# Glossarion2

A lightweight, self-hosted translation system with lexical enhancement for better translations of ambiguous or compound terms.

## Features

- **Translation Pipeline**: Normalize -> Lexical Lookup -> Hint Injection -> LibreTranslate -> PostProcess
- **StarDict Dictionary Support**: Load FreeDict and Wiktionary-derived dictionaries
- **Glossary Overrides**: Custom term translations that override MT output
- **Term Protection**: Protect product names, URLs, emails, code identifiers from translation
- **Quality Heuristics**: Detect suspicious translations (empty, identical to source, repetition)
- **Feature Flags**: Optional online providers (disabled by default)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/univie-henrikjurek/Glossarion2.git
cd Glossarion2

# Copy environment file
cp .env.example .env

# Build and start
docker compose up --build

# Test the API
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "source_lang": "en", "target_lang": "de"}'
```

## API Endpoints

### Translate Text

```bash
POST /translate
{
  "text": "The honeybadger is known for its bravery",
  "source_lang": "en",
  "target_lang": "de",
  "glossary": {
    "honeybadger": {"de": "Honigdachs"}
  }
}
```

### Response

```json
{
  "translation": "Der Honigdachs ist für seine Tapferkeit bekannt",
  "original": "The honeybadger is known for its bravery",
  "source_lang": "en",
  "target_lang": "de",
  "hints_applied": ["honeybadger=Honigdachs"],
  "protected_terms": ["honeybadger"],
  "quality_issues": [],
  "provider": "libretranslate"
}
```

### Batch Translate

```bash
POST /batch-translate
{
  "texts": ["Hello", "Goodbye"],
  "source_lang": "en",
  "target_lang": "de"
}
```

### Dictionary Lookup

```bash
GET /lookup?text=honeybadger&source=en&target=de
```

## Supported Languages

- English (en)
- German (de)
- French (fr)
- Italian (it)
- Polish (pl)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    API Service (:8000)                    │
│  Normalizer → LexicalResolver → HintInjector → Translate  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│               Dictionary Service (:8001)              │
│  StarDict Loader + Glossary Index                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│            LibreTranslate (:5000)                     │
│  Self-hosted machine translation                     │
└─────────────────────────────────────────────────────────┘
```

## Configuration

See `.env.example` for all configuration options:

| Variable | Default | Description |
|----------|---------|-------------|
| `LIBRETRANSLATE_URL` | http://libretranslate:5000 | LibreTranslate endpoint |
| `DICTIONARY_SERVICE_URL` | http://dictionary:8001 | Dictionary service URL |
| `SOURCE_LANGUAGE` | en | Default source language |
| `TARGET_LANGUAGES` | de,fr,it,pl | Default target languages |
| `LOG_LEVEL` | INFO | Logging level |

## Custom Glossary

Create a glossary file at `./data/glossary.json`:

```json
{
  "honeybadger": {
    "de": "Honigdachs",
    "fr": "ratel"
  },
  "Dachs": {
    "en": "badger",
    "fr": "blaireau"
  }
}
```

Mount it in `docker-compose.yml`:

```yaml
api:
  volumes:
    - ./data/glossary.json:/app/data/glossary.json
```

## Testing

```bash
# Run tests
docker compose exec api pytest

# Run specific test
docker compose exec api pytest tests/test_normalizer.py
```

## Feature Flags

These features are disabled by default:

- `FEATURE_ONLINE_LOOKUP`: Web terminology API lookup
- `FEATURE_GOOGLE_FALLBACK`: Google Translate fallback
- `FEATURE_WEB_SEARCH`: Web search enrichment

## Project Structure

```
services/
├── api/                    # Translation API service
│   ├── src/
│   │   ├── normalization/  # Text normalization
│   │   ├── lexicon/        # Lexical layer
│   │   ├── providers/      # Translation providers
│   │   ├── pipeline/       # Translation pipeline
│   │   └── main.py         # FastAPI app
│   └── tests/              # Unit tests
├── dictionary/             # Dictionary service
│   └── src/               # StarDict loader
└── libretranslate/        # LibreTranslate config
data/                      # Dictionary data (mounted)
scripts/                   # Ingestion scripts
```

## License

MIT