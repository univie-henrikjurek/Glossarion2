from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from .lookup import DictionaryIndex
from .stardict_loader import StarDictLoader
from .utils import logger


app = FastAPI(title="Glossarion2 Dictionary Service")

data_path = os.getenv("DICTIONARY_DATA_PATH", "/data")
dictionary = DictionaryIndex()
stardict = StarDictLoader(data_path)
stardict.load_all()

glossary_path = os.path.join(data_path, "glossary.json")
if os.path.exists(glossary_path):
    dictionary.load_glossary(glossary_path)
    logger.info("Loaded glossary")


class LookupRequest(BaseModel):
    text: str
    source: str = "en"
    target: str = "de"


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "glossarion2-dictionary",
        "entries_loaded": len(dictionary.entries)
    }


@app.get("/lookup")
async def lookup(text: str, source: str = "en", target: str = "de"):
    stardict_results = stardict.lookup(text)
    dict_results = dictionary.lookup(text, source, target)
    
    all_results = dict_results + stardict_results
    seen = set()
    unique_results = []
    for r in all_results:
        if r["term"] not in seen:
            unique_results.append(r)
            seen.add(r["term"])
        if len(unique_results) >= 20:
            break
    
    return {"matches": unique_results}


@app.post("/lookup")
async def lookup_post(request: LookupRequest):
    return await lookup(request.text, request.source, request.target)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)