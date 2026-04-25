from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    libretranslate_url: str = "http://libretranslate:5000"
    dictionary_service_url: str = "http://dictionary:8001"
    log_level: str = "INFO"
    source_language: str = "en"
    target_languages: str = "de,fr,it,pl"
    glossary_path: str = "/app/data/glossary.json"
    cors_origins: str = "*"
    
    feature_online_lookup: bool = False
    feature_google_fallback: bool = False
    feature_web_search: bool = False

    @property
    def target_language_list(self) -> List[str]:
        return [lang.strip() for lang in self.target_languages.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()