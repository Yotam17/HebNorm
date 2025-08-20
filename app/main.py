from fastapi import FastAPI
from app.routes import nikud, normalize, spellcheck
from app.config import settings
import platform
import psutil
import time

app = FastAPI(
    title="HEBNORM - Hebrew Text Normalizer",
    description="API for Hebrew text: nikud, normalization, spellcheck",
    version="0.1"
)

# API version prefix
API_V1_PREFIX = "/api/v1"

# Routers with version prefix
app.include_router(nikud.router, prefix=API_V1_PREFIX)
app.include_router(normalize.router, prefix=API_V1_PREFIX)
app.include_router(spellcheck.router, prefix=API_V1_PREFIX)

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "HEBNORM - Hebrew Text Normalizer",
        "version": "0.1",
        "description": "API for Hebrew text processing: nikud, normalization, spellcheck",
        "api_version": "v1",
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs",
            "api_v1": f"{API_V1_PREFIX}",
            "nikud": f"{API_V1_PREFIX}/add_nikud",
            "normalize": f"{API_V1_PREFIX}/normalize",
            "spellcheck": f"{API_V1_PREFIX}/spellcheck"
        }
    }

@app.get("/health")
def healthcheck():
    """Detailed health check endpoint"""
    try:
        # System information
        system_info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0]
        }
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_info = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "percent_used": memory.percent
        }
        
        # CPU info
        cpu_info = {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1)
        }
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "model": settings.nikud_model,
            "system": system_info,
            "memory": memory_info,
            "cpu": cpu_info
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }
