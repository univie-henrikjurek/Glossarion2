# Glossarion2 Deployment Guide

## Prerequisites

- Docker & Docker Compose
- 8GB+ RAM recommended
- Ports 8000, 8001, 5000, 6379 available

## Quick Deployment

```bash
# 1. Clone repository
git clone https://github.com/univie-henrikjurek/Glossarion2.git
cd Glossarion2

# 2. Configure environment
cp .env.example .env
# Edit .env as needed

# 3. Build and start
docker compose up --build -d

# 4. Check status
docker compose ps

# 5. Test
curl http://localhost:8000/health
```

## Service URLs

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Dictionary | http://localhost:8001 |
| LibreTranslate | http://localhost:5000 |
| Redis | localhost:6379 |

## Health Checks

```bash
# API health
curl http://localhost:8000/health

# Dictionary health
curl http://localhost:8001/health

# LibreTranslate health
curl http://localhost:5000

# All services
docker compose ps
```

## Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api

# Last 100 lines
docker compose logs --tail=100 api
```

## Stopping

```bash
docker compose down

# With volumes
docker compose down -v
```

## Restarting

```bash
docker compose restart

# Single service
docker compose restart api
```

## Updating

```bash
# Pull new images
git pull

# Rebuild
docker compose build

# Restart
docker compose up -d
```

## Dictionary Data

### Mount Custom Glossary

```yaml
# docker-compose.yml
api:
  volumes:
    - ./data/glossary.json:/app/data/glossary.json
```

### Add StarDict Dictionaries

Place in `./services/dictionary/data/`:

```
data/
├── fd-deu-eng/
│   ├── fd-deu-eng.ifo
│   ├── fd-deu-eng.idx
│   └── fd-deu-eng.dict.dz
└── fd-eng-deu/
    ├── fd-eng-deu.ifo
    ├── fd-eng-deu.idx
    └── fd-eng-deu.dict.dz
```

Mount in `docker-compose.yml`:

```yaml
dictionary:
  volumes:
    - ./services/dictionary/data:/data
```

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LIBRETRANSLATE_URL` | http://libretranslate:5000 | LibreTranslate endpoint |
| `DICTIONARY_SERVICE_URL` | http://dictionary:8001 | Dictionary service |
| `LOG_LEVEL` | INFO | DEBUG, INFO, WARNING, ERROR |
| `SOURCE_LANGUAGE` | en | Default source |
| `TARGET_LANGUAGES` | de,fr,it,pl | Default targets |
| `FEATURE_ONLINE_LOOKUP` | false | Enable online lookup |
| `FEATURE_GOOGLE_FALLBACK` | false | Google fallback |
| `FEATURE_WEB_SEARCH` | false | Web search |

### Feature Flags

All feature flags are **disabled by default**. Enable only for development:

```bash
FEATURE_ONLINE_LOOKUP=true
FEATURE_GOOGLE_FALLBACK=true
FEATURE_WEB_SEARCH=true
```

## Testing

```bash
# Run all tests
docker compose exec api pytest

# Run specific test file
docker compose exec api pytest tests/test_normalizer.py

# Run with verbose output
docker compose exec api pytest -v
```

## Troubleshooting

### LibreTranslate Won't Start

```bash
# Check logs
docker compose logs libretranslate

# Increase memory
# Edit docker-compose.yml
libretranslate:
  mem_limit: 2g
```

### API Returns 500

```bash
# Check API logs
docker compose logs api

# Check LibreTranslate is running
docker compose ps

# Test LibreTranslate directly
curl http://localhost:5000/translate -d "q=test&source=en&target=de"
```

### Dictionary Not Loading

```bash
# Check dictionary logs
docker compose logs dictionary

# Verify data path
docker compose exec dictionary ls -la /data
```

## Production Considerations

1. **CORS**: Set specific origins in `.env`:
   ```
   CORS_ORIGINS=https://your-domain.com
   ```

2. **Authentication**: Add API key validation to `/translate` endpoint

3. **Resource Limits**: Add to `docker-compose.yml`:
   ```yaml
   api:
     deploy:
       resources:
         limits:
           memory: 512M
   ```

4. **Monitoring**: Add health check endpoints for monitoring tools

5. **Backup**: Regular backup of `./data/` volume

## Raspberry Pi / ARM Deployment

LibreTranslate supports ARM64:

```yaml
libretranslate:
  platform: linux/arm64
  image: libretranslate/libretranslate:latest
```