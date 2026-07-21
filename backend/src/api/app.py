from fastapi import FastAPI

from backend.src.api.routes_events import router as events_router
from backend.src.api.routes_metrics import router as metrics_router
from backend.src.api.routes_systems import router as systems_router
from backend.src.domain.metrics import MetricDefinition
from backend.src.infra.config import get_settings
from backend.src.infra.db_models import get_store


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    app.include_router(systems_router, prefix=settings.api_prefix)
    app.include_router(events_router, prefix=settings.api_prefix)
    app.include_router(metrics_router, prefix=settings.api_prefix)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": "1.0.0"}

    store = get_store()
    if not store.metrics:
        for name in settings.default_metric_names:
            metric = MetricDefinition(name=name, description=f"Auto-seeded metric for {name}")
            store.metrics[metric.id] = metric

    return app


app = create_app()
