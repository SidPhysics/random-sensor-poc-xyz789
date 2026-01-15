import logging

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from shared.database import get_db, Base, engine
from shared.models import Metric
from shared.schemas import MetricCreate

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Weather Sensor Metrics Ingest API",
    version="1.0.0",
)

# Create tables
Base.metadata.create_all(bind=engine)


@app.post("/metrics", status_code=status.HTTP_201_CREATED)
def ingest_metric(
    metric: MetricCreate,
    db: Session = Depends(get_db),
) -> dict:
    """
    Ingest a new sensor metric.
    """
    try:
        db_metric = Metric(
            sensor_id=metric.sensor_id,
            metric_type=metric.metric_type,
            value=metric.value,
            timestamp=metric.timestamp,
        )

        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)

        return {
            "message": "Metric ingested successfully",
            "id": db_metric.id,
        }

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error: {e.orig}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate or invalid data",
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest metric",
        )
