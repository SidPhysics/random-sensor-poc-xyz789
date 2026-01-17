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
    statistic: Optional[str] = Field(None, pattern="^(min|max|sum|avg)$", description="Aggregation type (required for date range queries)")
    start_date: Optional[str] = Field(None, description="YYYY-MM-DD (optional)")
    end_date: Optional[str] = Field(None, description="YYYY-MM-DD (optional)")
    
    @field_validator("statistic")
    @classmethod
    def validate_statistic_for_date_range(cls, v, info):
        # Get other field values from validation context
        start_date = info.data.get('start_date')
        end_date = info.data.get('end_date')
        
        # If date range is provided, statistic is required
        if (start_date or end_date) and not v:
            raise ValueError("statistic is required when start_date or end_date is provided")
            
        return v
