from typing import Optional, List, Any

from .commons import (
    StandardResponse,
    PairConversion,
    TargetData,
    EnrichedData,
    HistoricalData,
    APIQuotaStatus,
)

from .exceptions import (
    UnsupportedCode,
    InvalidKey,
    InactiveAccount,
    QuotaReached,
    PlanUpgradeRequired,
    NoDataAvailable,
    MalformedRequest,
)

from ._error_handlers import (
    ResponseErrorHandler,
    handle_unsupported_code,
    handle_invalid_key,
    handle_inactive_account,
    handle_quota_reached,
    handle_required_plan_upgrade,
    handle_malformed_request,
    handle_no_data,
)

import requests

import time

from datetime import date


class ExchangeRateV6Client:
    _EXCHANGE_RATE_API_V6_URL = "https://v6.exchangerate-api.com/v6"
    _CACHE_TIMEOUT = 3600

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._supported_codes_cache = None
        self._cache_timestamp = 0
        self._response_error_handlers = {
            "latest": [
                handle_unsupported_code(),
                handle_malformed_request,
                handle_invalid_key,
                handle_inactive_account,
                handle_quota_reached,
            ],
            "pair": [
                handle_unsupported_code(),
                handle_malformed_request,
                handle_invalid_key,
                handle_inactive_account,
                handle_quota_reached,
            ],
            "enriched": [
                handle_unsupported_code(),
                handle_malformed_request,
                handle_invalid_key,
                handle_inactive_account,
                handle_quota_reached,
                handle_required_plan_upgrade,
            ],
            "historical": [
                handle_no_data(),
                handle_unsupported_code(),
                handle_malformed_request,
                handle_invalid_key,
                handle_inactive_account,
                handle_quota_reached,
                handle_required_plan_upgrade,
            ],
            "quota": [
                handle_invalid_key,
                handle_inactive_account,
                handle_quota_reached,
            ],
            "codes": [
                handle_invalid_key,
                handle_inactive_account,
                handle_quota_reached,
            ],
        }

    def fetch_standard_response(self, base_code: str) -> StandardResponse:
        if not self._is_supported_code(base_code):
            raise UnsupportedCode(f"Base code {base_code} is not supported")

        url = self._build_endpoint_url("latest", base_code)

        data = self._make_request_and_get_data(
            url, self._response_error_handlers["latest"]
        )

        obj = StandardResponse(**data)

        return obj

    def pair_conversion(
        self,
        base_code: str,
        target_code: str,
        amount: Optional[float] = None,
    ) -> PairConversion:
        if not self._is_supported_code(base_code):
            raise UnsupportedCode(f"Base code {base_code} is not supported")

        if not self._is_supported_code(target_code):
            raise UnsupportedCode(f"Target code {target_code} is not supported")

        if amount is not None and amount < 0:
            raise ValueError("Amount must be a greater than or equal to 0")

        url = self._build_endpoint_url("pair", base_code, target_code, amount)

        data = self._make_request_and_get_data(
            url, self._response_error_handlers["pair"]
        )

        obj = PairConversion(**data)

        return obj

    def fetch_enriched_data(self, base_code: str, target_code: str) -> EnrichedData:
        if not self._is_supported_code(base_code):
            raise UnsupportedCode(f"Base code {base_code} is not supported")

        if not self._is_supported_code(target_code):
            raise UnsupportedCode(f"Target code {target_code} is not supported")

        url = self._build_endpoint_url("enriched", base_code, target_code)

        data = self._make_request_and_get_data(
            url, self._response_error_handlers["enriched"]
        )

        target_data = TargetData(**data["target_data"])

        data_without_target = {
            key: value for key, value in data.items() if key != "target_data"
        }

        obj = EnrichedData(target_data=target_data, **data_without_target)

        return obj

    def fetch_historical_data(
        self, base_code: str, date_obj: date, amount: float
    ) -> HistoricalData:
        if not self._is_supported_code(base_code):
            raise UnsupportedCode(f"Base code {base_code} is not supported")

        year, month, day = (date_obj.year, date_obj.month, date_obj.day)

        url = self._build_endpoint_url("history", base_code, year, month, day, amount)

        data = self._make_request_and_get_data(
            url, self._response_error_handlers["historical"]
        )

        obj = HistoricalData(**data)

        return obj

    def fetch_quota_info(self) -> APIQuotaStatus:
        url = self._build_endpoint_url("quota")

        data = self._make_request_and_get_data(
            url, [handle_invalid_key, handle_inactive_account, handle_quota_reached]
        )

        obj = APIQuotaStatus(**data)

        return obj

    def _build_endpoint_url(self, endpoint: str, *params):
        url = f"{self._build_api_key_url()}/{endpoint}"
        present_params = filter(lambda p: p is not None, params)
        if params:
            url = f"{url}/{'/'.join([str(param) for param in present_params])}"
        return url

    def _make_request_and_get_data(
        self, url: str, error_handlers: List[ResponseErrorHandler]
    ) -> Any:
        try:
            response = requests.get(url, timeout=10)

            data = response.json()

            if not (200 <= response.status_code <= 299):
                error_type = data.get("error-type")
                if error_type:
                    for error_handler in error_handlers:
                        error_handler(response)
                raise Exception("Unknown error ocurred")

            return data
        except requests.exceptions.Timeout:
            raise Exception("The request to the Exchange Rate API timed out")
        except Exception as e:
            raise e

    def _is_supported_code(self, code: str) -> bool:
        if (
            self._supported_codes_cache is None
            or time.time() - self._cache_timestamp > self._CACHE_TIMEOUT
        ):
            self._udpate_supported_codes_cache()

        return code in self._supported_codes_cache

    def _udpate_supported_codes_cache(self):
        url = self._build_endpoint_url("codes")

        data = self._make_request_and_get_data(
            url, self._response_error_handlers["codes"]
        )

        supported_codes = data.get("supported_codes", [])

        self._supported_codes_cache = {code for code, _ in supported_codes}
        self._cache_timestamp = time.time()

    def _build_api_key_url(self) -> str:
        return f"{self._EXCHANGE_RATE_API_V6_URL}/{self._api_key}"
