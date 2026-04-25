# Glossarion2 Architecture

## Overview

Glossarion2 is a lightweight translation system that enhances machine translation with lexical lookup and glossary overrides.

## Pipeline Flow

```
INPUT TEXT
    │
    ▼
┌─────────────────────┐
│ 1. Normalizer      │  Case normalization, spacing, token splitting
│                    │  URL/File path/Email/Code ID protection
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 2. LexicalResolver  │  Longest-match phrase lookup
│                    │  StarDict dictionary lookup
│                    │  Glossary override check
└─────────────────────┘
    │
    ▼
┌────────────���────────┐
│ 3. HintInjector    │  Apply translation hints to LibreTranslate
│                    │  Mark protected terms
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 4. Translation     │  LibreTranslate (default)
│ Provider           │  Future: Online providers
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 5. PostProcessor   │  Normalize output
│                    │  Restore protected terms
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 6. Quality Check   │  Heuristics validation
│                    │  Suspicious pattern detection
└─────────────────────┘
    │
    ▼
OUTPUT TEXT
```

## Service Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     Docker Network                               │
│                                                                │
│  ┌────────────┐    ┌────────────┐    ┌────────────────────┐  │
│  │  API       │───►│ Dictionary │    │  LibreTranslate    │  │
│  │ :8000      │◄───│  :8001     │    │  :5000             │  │
│  └────────────┘    └────────────┘    └────────────────────┘  │
│         │                                    ▲                │
│         └────────────────────────────────────┘                │
│                      (HTTP)                                  │
└───────────────────────────────────────────────────────���────────┘
```

### Services

| Service | Port | Image | RAM | Purpose |
|---------|------|-------|-----|---------|
| api | 8000 | custom | ~200MB | Translation pipeline orchestration |
| dictionary | 8001 | custom | ~300MB | Lexical lookup, StarDict loading |
| libretranslate | 5000 | libretranslate:latest | ~1GB | MT engine |
| redis | 6379 | redis:7-alpine | ~50MB | Cache (optional) |

## Module Design

### Normalizer

Handles text preprocessing:

- Case normalization (lowercase)
- CamelCase splitting: `camelCase` → `camel Case`
- snake_case splitting: `snake_case` → `snake case`
- Merged compound detection
- Protected token detection:
  - URLs: `https://example.com`
  - File paths: `/var/log/app.log`
  - Emails: `user@example.com`
  - Code IDs: `PRODUCT-XY-123`

### LexicalResolver

Performs dictionary lookups:

- Loads glossary from JSON/YAML
- Queries dictionary service
- Longest-match phrase priority
- Returns:
  - Translation candidates
  - Protected terms
  - Translation hints

### TranslationProvider Interface

Pluggable provider system:

```python
class TranslationProvider(ABC):
    @abstractmethod
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        hints: Optional[list[str]] = None
    ) -> TranslationResult:
        pass
```

Default implementation: `LibreTranslateProvider`

### HeuristicsChecker

Validates translation quality:

- Empty output detection
- Identical to source detection
- Excessive repetition detection
- Placeholder remaining detection
- Length ratio anomalies

## Data Flow Example

Input: `The honeybadger is brave`
Glossary: `honeybadger → Honigdachs`

```
1. Normalized: "the honeybadger is brave"
2. Lexicon lookup: "honeybadger" found → "Honigdachs"
3. Hint applied: honeybadger=Honigdachs
4. LibreTranslate: "Der Honigdachs ist mutig"
5. Restored: "Der Honigdachs ist mutig"
6. Quality check: OK
Output: "Der Honigdachs ist mutig"
```

## Extension Points

### New Translation Provider

```python
from providers import TranslationProvider, ProviderFactory

class GoogleTranslateProvider(TranslationProvider):
    async def translate(self, text, source_lang, target_lang, hints=None):
        # Implementation
        return TranslationResult(...)

# Register
ProviderFactory.register("google", GoogleTranslateProvider)
```

### New Dictionary Source

Implement a new loader in `services/dictionary/src/`:

```python
class WiktionaryLoader:
    def load(self, url: str) -> bool:
        # Load Wiktionary data
        pass
```

## Memory Considerations

- LibreTranslate: ~1GB ( heaviest service)
- Dictionary: Loads on-demand, ~300MB max
- API: ~200MB (stateless)
- Redis: ~50MB (optional)

Total stack: ~1.5GB RAM

For limited RAM (8GB laptop), this is acceptable alongside other services.