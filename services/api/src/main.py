from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
from .config import settings
from .pipeline import TranslationPipeline, PipelineConfig, TranslateRequest, TranslateResponse
from .utils import logger


app = FastAPI(title="Glossarion2 Translation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranslateRequestModel(BaseModel):
    text: str
    source_lang: Optional[str] = None
    target_lang: str = "de"
    glossary: Optional[Dict[str, Dict[str, str]]] = None


class BatchTranslateRequest(BaseModel):
    texts: List[str]
    source_lang: Optional[str] = None
    target_lang: str = "de"
    glossary: Optional[Dict[str, Dict[str, str]]] = None


class LookupRequest(BaseModel):
    text: str
    source_lang: str = "en"
    target_lang: str = "de"


pipeline = TranslationPipeline(
    PipelineConfig(
        libretranslate_url=settings.libretranslate_url,
        dictionary_url=settings.dictionary_service_url,
        glossary_path=settings.glossary_path,
        default_source_lang=settings.source_language,
        default_target_lang="de"
    )
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "glossarion2-api",
        "version": "1.0.0"
    }


@app.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequestModel):
    try:
        source_lang = request.source_lang or settings.source_language
        
        pipeline_request = TranslateRequest(
            text=request.text,
            source_lang=source_lang,
            target_lang=request.target_lang,
            glossary=request.glossary
        )
        
        result = await pipeline.translate(pipeline_request)
        
        return TranslateResponse(
            translation=result.translation,
            original=result.original,
            source_lang=result.source_lang,
            target_lang=result.target_lang,
            hints_applied=result.hints_applied,
            protected_terms=result.protected_terms,
            quality_issues=result.quality_issues,
            provider=result.provider
        )
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch-translate")
async def batch_translate(request: BatchTranslateRequest):
    results = []
    source_lang = request.source_lang or settings.source_language
    
    for text in request.texts:
        try:
            pipeline_request = TranslateRequest(
                text=text,
                source_lang=source_lang,
                target_lang=request.target_lang,
                glossary=request.glossary
            )
            result = await pipeline.translate(pipeline_request)
            results.append(result.translation)
        except Exception as e:
            logger.error(f"Batch translation error for '{text}': {e}")
            results.append("")
    
    return {"translations": results}


@app.get("/lookup")
async def lookup(text: str, source: str = "en", target: str = "de"):
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.dictionary_service_url}/lookup",
                params={"text": text, "source": source, "target": target}
            )
            if response.status_code == 200:
                return response.json()
            return {"matches": []}
    except Exception as e:
        logger.error(f"Lookup error: {e}")
        return {"matches": []}


@app.get("/languages")
async def get_languages():
    return {
        "source": settings.source_language,
        "targets": settings.target_language_list
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)