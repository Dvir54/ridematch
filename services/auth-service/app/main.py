"""
Auth Service - FastAPI Application Entry Point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import engine, test_db_connection, test_redis_connection
from app.routers import auth_router, users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: test connections
    if test_db_connection():
        print("✓ Database connected")
    else:
        print("✗ Database connection failed")
    
    if test_redis_connection():
        print("✓ Redis connected")
    else:
        print("✗ Redis connection failed")
    
    yield
    
    # Shutdown: close connections
    engine.dispose()
    print("Database connections closed")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api/auth")
app.include_router(users_router, prefix="/api/users")


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return clean validation error messages."""
    errors = [
        {"field": ".".join(str(x) for x in err["loc"][1:]), "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": "Validation error", "errors": errors})


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors without exposing internals."""
    return JSONResponse(status_code=503, content={"detail": "Database error"})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions."""
    if settings.debug:
        return JSONResponse(status_code=500, content={"detail": str(exc)})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["Health"])
async def health_check():
    """Service health check with dependency status."""
    db_ok = test_db_connection()
    redis_ok = test_redis_connection()
    
    return {
        "status": "healthy" if (db_ok and redis_ok) else "degraded",
        "service": settings.app_name,
        "version": settings.app_version,
        "dependencies": {
            "database": "ok" if db_ok else "error",
            "redis": "ok" if redis_ok else "error",
        }
    }

