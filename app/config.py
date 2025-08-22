from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    nikud_model: str = "dicta-il/dictabert-large-char-menaked"
    hf_home: str = "/app/.cache"  # Hugging Face cache directory
    transformers_cache: str = "/app/.cache"  # Transformers cache directory
    pythonpath: str = "/app"  # Python path for imports
    log_level: str = "INFO"  # Logging level
    model_cache_dir: str = "/app/.cache"  # Model cache directory
    dev_mode: bool = True  # Development mode flag
    max_workers: int = 1  # Maximum number of workers
    timeout: int = 30  # Request timeout in seconds
    cors_origins: str = "*"  # CORS allowed origins
    debug: bool = True  # Debug mode flag
    environment: str = "development"  # Environment name
    version: str = "0.1.0"  # Application version
    api_prefix: str = "/api/v1"  # API version prefix
    model_device: str = "auto"  # Model device (auto/cpu/cuda)
    model_trust_remote_code: bool = True  # Trust remote code for model loading
    model_cache_size: int = 1024  # Model cache size in MB
    model_download_timeout: int = 300  # Model download timeout in seconds
    spellchecker_max_edit_distance: int = 2
    spellchecker_prefix_length: int = 7
    spellchecker_corpus_dir: str = "app/data/spellcheck_corpus"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()
