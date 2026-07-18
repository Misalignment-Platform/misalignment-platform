"""
sentinel/sentinel.py
Service C — Continuum Sentinel (Timeline Integrity)
Batch worker. Runs every M minutes. Reads DriftMetrics,
computes continuity score, flags timeline breaks.
ATA-Cont_x3 supervised.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.config import config
from shared.db import init_db, AsyncSessionLocal, DriftMetricORM, ContinuityReportORM
from shared.schemas import DriftSeverity, AltitudeLevel
from ata.ata import boot, altitude_context
from ata.continuity import score_continuity, detect_timeline_breaks, recommended_actions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinel")

_ata_ctx: Dict[str, Any] = {}


def _severity_from_continuity(score: float) -> DriftSeverity:
    if score >= 0.85: return DriftSeverity.NOMINAL
    if score >= 0.7:  return DriftSeverity.LOW
    if score >= 0.5:  return DriftSeverity.MODERATE
    if score >= 0.3:  return DriftSeverity.HIGH
    return DriftSeverity.CRITICAL


async def run_cycle():
    window_start = datetime.utcnow() - timedelta(
        minutes=config.SENTINEL_INTERVAL_MINUTES * 6   # look back 6 cycles
    )
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(DriftMetricORM)
            .where(DriftMetricORM.window_end >= window_start)
            .order_by(DriftMetricORM.window_end.asc())
        )
        metrics = result.scalars().all()

        if not metrics:
            logger.info("Sentinel: no metrics in window. Skipping.")
            return

        metric_dicts = [
            {
                "metric_id":        m.metric_id,
                "continuity_score": m.continuity_score,
                "window_start":     m.window_start.isoformat(),
                "window_end":       m.window_end.isoformat(),
                "severity":         m.severity,
            }
            for m in metrics
        ]

        # Score
        continuity = score_continuity(
            drift_magnitudes  = [m.drift_magnitude  for m in metrics],
            drift_confidences = [m.drift_confidence for m in metrics],
            gap_penalties     = [m.drift_spread      for m in metrics],
        )

        # Detect breaks
        breaks = detect_timeline_breaks(
            metric_dicts, threshold=config.CONTINUITY_THRESHOLD
        )

        # Warnings
        warnings = []
        if continuity < config.CONTINUITY_THRESHOLD:
            warnings.append(
                f"Continuity score {continuity:.3f} is below threshold "
                f"{config.CONTINUITY_THRESHOLD}."
            )
        if breaks:
            warnings.append(f"{len(breaks)} timeline break(s) detected.")

        actions  = recommended_actions(breaks)
        severity = _severity_from_continuity(continuity)
        altitude = metrics[-1].altitude if metrics else "satellite"

        report = ContinuityReportORM(
            report_id           = str(uuid.uuid4()),
            evaluated_at        = datetime.utcnow(),
            continuity_score    = continuity,
            timeline_breaks     = breaks,
            warnings            = warnings,
            recommended_actions = actions,
            altitude            = altitude,
            severity            = severity.value,
            source_metric_ids   = [m.metric_id for m in metrics],
        )
        db.add(report)
        await db.commit()

        logger.info(
            "Sentinel: report %s | score=%.3f | breaks=%d | sev=%s",
            report.report_id, continuity, len(breaks), severity.value
        )


async def main():
    global _ata_ctx
    _ata_ctx = boot("sentinel")
    await init_db()
    interval = config.SENTINEL_INTERVAL_MINUTES * 60
    logger.info("Sentinel started. Interval: %ds", interval)
    while True:
        try:
            await run_cycle()
        except Exception as e:
            logger.error("Sentinel cycle error: %s", e)
        await asyncio.sleep(interval)


if __name__ == "__main__":
    asyncio.run(main())

