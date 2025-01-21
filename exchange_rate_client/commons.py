from typing import Optional, Mapping, Any, Dict

from pydantic import BaseModel


class ExchangeRates(BaseModel):
    base_code: str
    conversion_rates: Dict[str, float]


class PairConversion(BaseModel):
    time_last_update_unix: Optional[int] = None
    time_last_update_utc: Optional[str] = None
    time_next_update_unix: Optional[int] = None
    time_next_update_utc: Optional[str] = None
    base_code: str
    target_code: str
    conversion_rate: float
    conversion_result: Optional[float] = None


class APIQuotaStatus(BaseModel):
    plan_quota: int
    requests_remaining: int
    refresh_day_of_month: int
