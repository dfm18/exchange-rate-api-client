from typing import Optional, Dict

from pydantic import BaseModel, ConfigDict


class BaseResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class StandardResponse(BaseResponseModel):
    base_code: str
    conversion_rates: Dict[str, float]


class PairConversion(BaseResponseModel):
    time_last_update_unix: Optional[int] = None
    time_last_update_utc: Optional[str] = None
    time_next_update_unix: Optional[int] = None
    time_next_update_utc: Optional[str] = None
    base_code: str
    target_code: str
    conversion_rate: float
    conversion_result: Optional[float] = None


class TargetData(BaseResponseModel):
    locale: str
    two_letter_code: str
    currency_name: str
    currency_name_short: str
    display_symbol: str
    flag_url: str


class EnrichedData(BaseResponseModel):
    time_last_update_unix: Optional[int] = None
    time_last_update_utc: Optional[str] = None
    time_next_update_unix: Optional[int] = None
    time_next_update_utc: Optional[str] = None
    base_code: str
    target_code: str
    conversion_rate: float
    target_data: TargetData


class HistoricalData(BaseResponseModel):
    year: int
    month: int
    day: int
    base_code: str
    requested_amount: int
    conversion_amounts: Dict[str, float]


class APIQuotaStatus(BaseResponseModel):
    plan_quota: int
    requests_remaining: int
    refresh_day_of_month: int
