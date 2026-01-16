from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MetricCreate(BaseModel):
    sensor_id: int = Field(..., gt=0, description="Positive integer sensor ID")
    metric_type: str = Field(..., description="e.g., temperature, humidity, wind_speed")
    value: float
    timestamp: Optional[datetime] = None

    @field_validator("metric_type")
    @classmethod
    def validate_metric_type(cls, v: str) -> str:
        allowed = {"temperature", "humidity", "wind_speed"}
        if v not in allowed:
            raise ValueError(f"Invalid metric_type. Allowed values: {', '.join(sorted(allowed))}")
        return v

    @field_validator("timestamp", mode="before")
    @classmethod
    def default_timestamp(cls, v):
        return v or datetime.now()


class QueryParams(BaseModel):
    sensors: str = Field("all", description="'all' or comma-separated IDs like '1,2,3'")
    metrics: str = Field(..., description="Comma-separated metrics like 'temperature,humidity'")
    statistic: str = Field(..., pattern="^(min|max|sum|avg)$", description="Aggregation type")
    start_date: Optional[str] = Field(None, description="YYYY-MM-DD (optional)")
    end_date: Optional[str] = Field(None, description="YYYY-MM-DD (optional)")
