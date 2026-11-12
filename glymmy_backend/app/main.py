"""Glymmy FastAPI application — mounts all feature routers."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.adapters.cgm import get_cgm_adapter
from app.adapters.labs import get_labs_adapter
from app.adapters.llm import get_llm_adapter
from app.adapters.storage import get_storage_adapter
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.graphql import schema as graphql_schema
from app.modules.chat import router as chat_router
from app.modules.food import router as food_router
from app.modules.glucose import router as glucose_router
from app.modules.inventory import router as inventory_router
from app.modules.labs import router as labs_router
from app.modules.notifications import router as notifications_router
from app.modules.profile import router as profile_router
from app.modules.reminders import router as reminders_router
from app.modules.scan import router as scan_router
from app.modules.scan.router import lab_router
from app.modules.share import router as share_router
from app.modules.tasks import router as tasks_router
from app.modules.users import me_router as me_router
from app.modules.users import router as users_router
from app.modules.wearables import router as wearables_router
from strawberry.fastapi import GraphQLRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings = get_settings()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Demo mode: {settings.DEMO_MODE} | Auto-seed: {settings.AUTO_SEED}")
    # Resolve adapters early so misconfigurations fail fast
    try:
        get_llm_adapter()
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"LLM adapter unavailable at startup: {exc}")
    try:
        get_cgm_adapter()
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"CGM adapter unavailable: {exc}")
    try:
        get_labs_adapter()
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Labs adapter unavailable: {exc}")
    storage = get_storage_adapter()

    # Auto-seed synthetic data on startup (demo mode)
    if settings.AUTO_SEED and not storage.list_users():
        from app.modules.users.synthetic import seed_synthetic_data

        logger.info("Auto-seeding synthetic wearable data (7 days)...")
        stats = seed_synthetic_data(storage, days=7)
        logger.info(f"Auto-seed complete: {stats}")

    yield
    logger.info("Shutting down Glymmy API")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Glymmy — your glycemic companion. Unified AI health platform.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "demo_mode": settings.DEMO_MODE,
            "providers": {
                "llm": settings.LLM_PROVIDER,
                "cgm": settings.CGM_PROVIDER,
                "labs": settings.LABS_PROVIDER,
                "storage": settings.STORAGE_PROVIDER,
                "chroma": settings.CHROMA_MODE,
            },
        }

    @app.get("/api/v1/info")
    def info() -> dict:
        stats: dict = {}
        try:
            cgm = get_cgm_adapter()
            stats["cgm_patients"] = len(cgm.list_patients())
        except Exception:  # noqa: BLE001
            stats["cgm_patients"] = None
        try:
            labs = get_labs_adapter()
            stats["lab_patients"] = len(labs.list_patients())
        except Exception:  # noqa: BLE001
            stats["lab_patients"] = None
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "llm": settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama_gemma" else settings.ANTHROPIC_MODEL,
            "dataset_stats": stats,
        }

    # Mount all REST feature routers
    app.include_router(profile_router)
    app.include_router(glucose_router)
    app.include_router(food_router)
    app.include_router(labs_router)
    app.include_router(scan_router)
    app.include_router(lab_router)
    app.include_router(wearables_router)
    app.include_router(inventory_router)
    app.include_router(notifications_router)
    app.include_router(reminders_router)
    app.include_router(tasks_router)
    app.include_router(share_router)
    app.include_router(me_router)      # /users/me/* must come before /users/{id}
    app.include_router(users_router)
    app.include_router(chat_router)

    # Mount GraphQL — same business logic, alternative protocol
    graphql_app: GraphQLRouter = GraphQLRouter(graphql_schema)
    app.include_router(graphql_app, prefix="/graphql", tags=["graphql"])

    return app


app = create_app()
