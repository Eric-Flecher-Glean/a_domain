"""FastAPI application for DataOps Registry."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import datasets_router, templates_router, health_router
from .middleware import add_error_handlers


# Create FastAPI app
app = FastAPI(
    title="DataOps Lifecycle API",
    description="REST API for dataset discovery, registry, and lifecycle management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handlers
add_error_handlers(app)

# Include routers
app.include_router(health_router)
app.include_router(datasets_router)
app.include_router(templates_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "DataOps Lifecycle API",
        "version": "1.0.0",
        "description": "REST API for dataset discovery, registry, and lifecycle management",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
