from functools import lru_cache

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "misalignment-platform"
    api_prefix: str = "/api"
    require_auth: bool = False
    default_metric_names: list[str] = Field(
        default_factory=lambda: ["risk_score", "compliance_score", "violation_rate"]
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
