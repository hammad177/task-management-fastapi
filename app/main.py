from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import DBBase, engine
from app.common import settings, ApiResponseBuilder, register_exception_handlers
from app.routes import task_router, user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup/shutdown events"""
    async with engine.begin() as conn:
        await conn.run_sync(DBBase.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers with the FastAPI app
register_exception_handlers(app)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint with unified response"""
    return ApiResponseBuilder.success(
        message="Server is running",
        data={"status": "healthy"}
    )


# Include app routers
app.include_router(task_router)
app.include_router(user_router)