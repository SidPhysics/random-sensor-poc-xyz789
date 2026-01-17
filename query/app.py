import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from shared.database import get_db
from shared.models import Metric
from shared.schemas import QueryParams

from shared.database import Base, engine

# Create tables (checkfirst=True prevents error if table exists)
Base.metadata.create_all(bind=engine, checkfirst=True)


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
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
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

    # Parse sensors
    sensor_filter = parse_sensors(params.sensors)

    # Parse metrics
    metric_types = [m.strip() for m in params.metrics.split(",") if m.strip()]

    if not metric_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one metric must be specified",
        )

    # Check if querying latest data (no date range specified)
    is_latest_query = not (params.start_date and params.end_date)
    
    if is_latest_query:
        # Get latest record for each sensor/metric combination
        results = []
        for sensor_id in ([int(s.strip()) for s in params.sensors.split(",")] if params.sensors != "all" else 
                         [r[0] for r in db.query(Metric.sensor_id).distinct().all()]):
            for metric_type in metric_types:
                latest_record = (
                    db.query(Metric)
                    .filter(
                        Metric.sensor_id == sensor_id,
                        Metric.metric_type == metric_type
                    )
                    .order_by(desc(Metric.timestamp))
                    .first()
                )
                if latest_record:
                    results.append((latest_record.sensor_id, latest_record.metric_type, 
                                  latest_record.value, latest_record.timestamp))
    else:
        # Aggregated query for date range
        if not params.statistic:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="statistic is required for date range queries",
            )
            
        agg_func = STAT_FUNC_MAP[params.statistic]
        start_dt, end_dt = parse_date_range(params.start_date, params.end_date)
        
        query = (
            db.query(
                Metric.sensor_id,
                Metric.metric_type,
                agg_func(Metric.value).label("value"),  # type: ignore[operator]
            )
            .filter(Metric.metric_type.in_(metric_types))
            .filter(
                Metric.timestamp >= start_dt,
                Metric.timestamp < end_dt,
            )
            .group_by(Metric.sensor_id, Metric.metric_type)
        )
        
        if sensor_filter is not None:
            query = query.filter(sensor_filter)

    try:
        if is_latest_query:
            # Results already collected in the if block above
            pass
        else:
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
    response: Dict[str, Dict[str, Any]] = {}
    
    if is_latest_query:
        # Group by sensor for response, but handle timestamps per metric
        sensor_timestamps = {}
        for sensor_id, metric_type, value, timestamp in results:
            sensor_key = str(sensor_id)
            if sensor_key not in response:
                response[sensor_key] = {}
                sensor_timestamps[sensor_key] = timestamp
            response[sensor_key][metric_type] = value
            # Use the latest timestamp across all metrics for this sensor
            if timestamp > sensor_timestamps[sensor_key]:
                sensor_timestamps[sensor_key] = timestamp
        
        # Add timestamps to response
        for sensor_key in response:
            response[sensor_key]["ingested_at"] = sensor_timestamps[sensor_key].isoformat()
    else:
        for sensor_id, metric_type, value in results:
            response.setdefault(str(sensor_id), {})[metric_type] = value

    return {
        "statistic": params.statistic if not is_latest_query else "latest",
        "results": response,
    }
