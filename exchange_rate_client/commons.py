from typing import Optional, Mapping, Any, Dict

from dataclasses import dataclass, field


@dataclass
class PairConversion:
    time_last_update_unix: Optional[int] = field(default=None)
    time_last_update_utc: Optional[str] = field(default=None)
    time_next_update_unix: Optional[int] = field(default=None)
    time_next_update_utc: Optional[str] = field(default=None)
    base_code: str = ""
    target_code: str = ""
    conversion_rate: float = 0.0
    conversion_result: Optional[float] = field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_last_update_unix": self.time_last_update_unix,
            "time_last_update_utc": self.time_last_update_utc,
            "time_next_update_unix": self.time_next_update_unix,
            "time_next_update_utc": self.time_next_update_utc,
            "base_code": self.base_code,
            "target_code": self.target_code,
            "conversion_rate": self.conversion_rate,
            "conversion_result": self.conversion_result,
        }

    @staticmethod
    def from_api_response(data: Mapping[str, Any]) -> "PairConversion":
        obj = PairConversion()

        obj.time_last_update_unix = data.get("time_last_update_unix")
        obj.time_last_update_utc = data.get("time_last_update_utc")
        obj.time_next_update_unix = data.get("time_next_update_unix")
        obj.time_next_update_utc = data.get("time_next_update_utc")
        obj.base_code = data.get("base_code")
        obj.target_code = data.get("target_code")
        obj.conversion_rate = data.get("conversion_rate")
        obj.conversion_result = data.get("conversion_result")

        return obj


@dataclass
class APIQuotaStatus:
    plan_quota: int = 0
    requests_remaining: int = 0
    refresh_day_of_month: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            "plan_quota": self.plan_quota,
            "requests_remaining": self.requests_remaining,
            "refresh_day_of_month": self.refresh_day_of_month,
        }

    @staticmethod
    def from_api_response(data: Mapping[str, Any]) -> "APIQuotaStatus":
        return APIQuotaStatus(
            plan_quota=data.get("plan_quota", 0),
            requests_remaining=data.get("requests_remaining", 0),
            refresh_day_of_month=data.get("refresh_day_of_month", 0),
        )
