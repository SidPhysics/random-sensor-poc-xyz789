# shared/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from .database import Base
from datetime import datetime, timezone


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, index=True, nullable=False)
    metric_type = Column(String(50), index=True, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), index=True)
