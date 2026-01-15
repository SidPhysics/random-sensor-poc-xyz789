import logging
from typing import Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import func

from shared.database import get_db
from shared.models import Metric
from shared.schemas import QueryParams

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Weather Sensor Metrics Query API",
    version="1.0.0",
)


STAT_FUNC_MAP = {
    "min": func.min,
    "max": func.max,
    "sum": func.sum,
    "avg": func.avg,
}


def parse_sensors(sensors_param: str):
    """
    Convert sensor query parameter into SQLAlchemy filter.
    """
    if sensors_param == "all":
        return None

    try:
        sensor_ids = [int(s.strip()) for s in sensors_param.split(",")]
        return Metric.sensor_id.in_(sensor_ids)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sensor IDs format",
        )


def parse_date_range(start_date: str, end_date: str):
    """
    Parse date strings into datetime objects.
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD",
        )

    if start_dt > end_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date",
        )

    return start_dt, end_dt


@app.get("/query", status_code=status.HTTP_200_OK)
def query_metrics(
    params: QueryParams = Depends(),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Query aggregated sensor metrics.
    
    """

    # Statistic already validated by schema
    agg_func = STAT_FUNC_MAP[params.statistic]

    # Parse sensors
    sensor_filter = parse_sensors(params.sensors)

    # Parse metrics
    metric_types: List[str] = [m.strip() for m in params.metrics.split(",")]

    # Build base query
    query = (
        db.query(
            Metric.sensor_id,
            Metric.metric_type,
            agg_func(Metric.value).label("value"),
        )
        .filter(Metric.metric_type.in_(metric_types))
        .group_by(Metric.sensor_id, Metric.metric_type)
    )

    if sensor_filter is not None:
        query = query.filter(sensor_filter)

    if params.start_date and params.end_date:
        start_dt, end_dt = parse_date_range(
            params.start_date, params.end_date
        )
        query = query.filter(
            Metric.timestamp >= start_dt,
            Metric.timestamp <= end_dt,
        )

    try:
        results = query.all()
    except SQLAlchemyError as e:
        logger.error(
            f"Database error during query: {type(e).__name__}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query metrics",
        )

    # Format response
    response: Dict[str, Dict[str, float]] = {}
    for sensor_id, metric_type, value in results:
        response.setdefault(str(sensor_id), {})[metric_type] = value

    return {
        "statistic": params.statistic,
        "results": response,
    }
