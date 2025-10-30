"""
Script to run the FastAPI application.
"""
import uvicorn
from chatty.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "chatty.main:socketio_app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers if not settings.debug else 1,
        log_level=settings.log_level.lower(),
    )

