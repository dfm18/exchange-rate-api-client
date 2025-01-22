from typing import Optional

from .commons import StandardResponse, PairConversion, HistoricalData, APIQuotaStatus

from .exceptions import (
    UnsupportedCode,
    InvalidKey,
    InactiveAccount,
    QuotaReached,
    PlanUpgradeRequired,
    NoDataAvailable,
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

    def fetch_standard_response(self, base_code: str) -> StandardResponse:
        if not self._is_supported_code(base_code):
            raise UnsupportedCode(f"Base code {base_code} is not supported")

        url = f"{self._build_api_key_url()}/latest/{base_code}"

        try:
            response = requests.get(url, timeout=10)

            data = response.json()

            if response.status_code != 200:
                error_type = data.get("error-type")
                if error_type:
                    self._raise_exception_from_error_type(error_type)
                else:
                    raise Exception("Unknown error ocurred")

            obj = StandardResponse(**data)

            return obj
        except requests.exceptions.Timeout:
            raise Exception("The request to the Exchange Rate API timed out")

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

        url = f"{self._build_api_key_url()}/pair/{base_code}/{target_code}"

        if amount is not None:
            url += f"/{amount}"

        try:
            response = requests.get(url, timeout=10)

            data = response.json()

            if response.status_code != 200:
                error_type = data.get("error-type")
                if error_type:
                    self._raise_exception_from_error_type(error_type)
                else:
                    raise Exception("Unknown error ocurred")

            obj = PairConversion(**data)

            return obj
        except requests.exceptions.Timeout:
            raise Exception("The request to the Exchange Rate API timed out")

    def fetch_historical_data(
        self, base_code: str, date_obj: date, amount: float
    ) -> HistoricalData:
        if not self._is_supported_code(base_code):
            raise UnsupportedCode(f"Base code {base_code} is not supported")

        year, month, day = (date_obj.year, date_obj.month, date_obj.day)

        url = f"{self._build_api_key_url()}/history/{base_code}/{year}/{month}/{day}/{amount}"

        try:
            response = requests.get(url, timeout=10)

            data = response.json()

            if response.status_code != 200:
                error_type = data.get("error-type")
                if error_type:
                    #  Special case
                    if error_type == "no-data-available":
                        raise NoDataAvailable(
                            "The database doesn't have any exchange rates for the specific date supplied"
                        )
                    else:
                        self._raise_exception_from_error_type(error_type)
                else:
                    raise Exception("Unknown error ocurred")

            obj = HistoricalData(**data)

            return obj
        except requests.exceptions.Timeout:
            raise Exception("The request to the Exchange Rate API timed out")

    def fetch_quota_info(self) -> APIQuotaStatus:
        url = f"{self._build_api_key_url()}/quota"

        try:
            response = requests.get(url, timeout=10)

            data = response.json()

            if response.status_code != 200:
                error_type = data.get("error-type")
                if error_type:
                    self._raise_exception_from_error_type(error_type)
                else:
                    raise Exception("Unknown error ocurred")

            obj = APIQuotaStatus(**data)

            return obj
        except requests.exceptions.Timeout:
            raise Exception("The request to the Exchange Rate API timed out")

    def _is_supported_code(self, code: str) -> bool:
        if (
            self._supported_codes_cache is None
            or time.time() - self._cache_timestamp > self._CACHE_TIMEOUT
        ):
            self._udpate_supported_codes_cache()

        return code in self._supported_codes_cache

    def _udpate_supported_codes_cache(self):
        url = f"{self._build_api_key_url()}/codes"

        try:
            response = requests.get(url, timeout=10)

            data = response.json()

            if response.status_code != 200:
                error_type = data.get("error-type")
                if error_type:
                    self._raise_exception_from_error_type(error_type)
                else:
                    raise Exception("Unknown error ocurred")

            supported_codes = data.get("supported_codes", [])

            self._supported_codes_cache = {code for code, _ in supported_codes}
            self._cache_timestamp = time.time()
        except requests.exceptions.Timeout:
            raise Exception("The request to the Exchange Rate API timed out")

    def _build_api_key_url(self) -> str:
        return f"{self._EXCHANGE_RATE_API_V6_URL}/{self._api_key}"

    def _raise_exception_from_error_type(self, error_type: str):
        if error_type == "unsupported-code":
            raise UnsupportedCode(
                "One or both of the supplied codes are not supported"
            )
        elif error_type == "invalid-key":
            raise InvalidKey("The api key is not valid")
        elif error_type == "inactive-account":
            raise InactiveAccount("The account's email wasn't confirmed")
        elif error_type == "quota-reached":
            raise QuotaReached(
                "Reached the number of requests allowed in the plan"
            )
        elif error_type == "plan-upgrade-required":
            raise PlanUpgradeRequired(
                "The account plan doesn't support this type of request"
            )
        else:
            raise Exception(f"Unexpected error type: {error_type}")
