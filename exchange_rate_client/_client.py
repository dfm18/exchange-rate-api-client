from typing import Optional, List, Any

from .commons import (
    ExclusiveExchangeRates,
    PairConversion,
    TargetData,
    EnrichedData,
    HistoricalData,
    APIQuotaStatus,
)

from .exceptions import (
    UnsupportedCode,
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
                handle_unsupported_code("The base code is not supported"),
                handle_malformed_request,
                handle_invalid_key,
                handle_inactive_account,
                handle_quota_reached,
            ],
            "pair": [
                handle_unsupported_code("One or both codes are not supported"),
                handle_malformed_request,
                handle_invalid_key,
                handle_inactive_account,
                handle_quota_reached,
            ],
            "enriched": [
                handle_unsupported_code("One or both codes are not supported"),
                handle_malformed_request,
                handle_invalid_key,
                handle_inactive_account,
                handle_quota_reached,
                handle_required_plan_upgrade,
            ],
            "historical": [
                handle_no_data(
                    "The database doesn't have any exchange rates for the specific date supplied"
                ),
                handle_unsupported_code("The base code is not supported"),
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

    def fetch_exchange_rates(self, base_code: str) -> ExclusiveExchangeRates:
        """
        Fetch the latest exchange rates for a given base currency.

        Args:
            base_code (str): The ISO 4217 currency code for the base currency.

        Returns:
            ExclusiveExchangeRates: An object containing the latest exchange rate data, including:
                - The timestamp of the last update.
                - The timestamp for the next scheduled update.
                - The base currency code.
                - A dictionary of conversion rates to supported currencies.

        Raises:
            ValueError: If one of the given arguments is invalid
            UnsupportedCode: If the provided base_code is not a supported currency code.
            MalformedRequest: If the request is malformed and cannot be processed by the API.
            InvalidKey: If the provided API key is invalid.
            InactiveAccount: If the account associated with the API key is inactive.
            QuotaReached: If the API quota has been exceeded.

        Example:
            ```python
            client = ExchangeRateV6Client(api_key="your_api_key")
            exchange_rates = client.fetch_exchange_rates(base_code="USD")
            print(exchange_rates.base_code)  # Output: USD
            print(exchange_rates.conversion_rates)  # Output: Dictionary of conversion rates for USD
            ```
        """
        if not isinstance(base_code, str):
            raise ValueError("Base code must be a str")

        if not self._is_supported_code(base_code):
            raise UnsupportedCode(f"Base code {base_code} is not supported")

        url = self._build_endpoint_url("latest", base_code)

        data = self._make_request_and_get_data(
            url, self._response_error_handlers["latest"]
        )

        obj = ExclusiveExchangeRates(**data)

        return obj

    def pair_conversion(
        self,
        base_code: str,
        target_code: str,
        amount: Optional[float] = None,
    ) -> PairConversion:
        """
        Convert an amount from one currency to another using the latest exchange rate.

        Args:
            base_code (str): The ISO 4217 currency code for the base currency.
            target_code (str): The ISO 4217 currency code for the target currency.
            amount (Optional[float]): The amount to convert. If None, the conversion is done with a default value of 1.

        Returns:
            PairConversion: Contains the base and target currency codes, conversion rate,
            and optionally the converted amount.

        Raises:
            ValueError: If one of the given arguments is invalid
            UnsupportedCode: If the provided base_code or target_code is not a supported currency code.
            MalformedRequest: If the request is malformed and cannot be processed by the API.
            InvalidKey: If the provided API key is invalid.
            InactiveAccount: If the account associated with the API key is inactive.
            QuotaReached: If the API quota has been exceeded.
            ValueError: If the provided amount is less than 0.

        Example:
            ```python
            client = ExchangeRateV6Client(api_key="your_api_key")
            conversion = client.pair_conversion(base_code="USD", target_code="EUR", amount=100)
            print(conversion.base_code)  # Output: USD
            print(conversion.target_code)  # Output: EUR
            print(conversion.conversion_result)  # Output: 85.0 (depending on the exchange rate)
            ```
        """
        if not isinstance(base_code, str) or not isinstance(target_code, str):
            raise ValueError("Base code and target code must be a str")

        if amount is not None and not isinstance(amount, (int, float)):
            raise ValueError("Amount must be an integer or float")

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
        """
        Fetch enriched exchange rate data for a pair of currencies.

        Args:
            base_code (str): The ISO 4217 currency code for the base currency.
            target_code (str): The ISO 4217 currency code for the target currency.

        Returns:
            EnrichedData: An object containing the enriched exchange rate data, including:
                - Conversion rate from the base currency to the target currency.
                - Additional details about the target currency (e.g., name, symbol, flag, etc.).

        Raises:
            ValueError: If one of the given arguments is invalid
            UnsupportedCode: If the provided base_code or target_code is not a supported currency code.
            MalformedRequest: If the request is malformed and cannot be processed by the API.
            InvalidKey: If the provided API key is invalid.
            InactiveAccount: If the account associated with the API key is inactive.
            QuotaReached: If the API quota has been exceeded.
            PlanUpgradeRequired: If the user needs to upgrade their plan to access this data.

        Example:
            ```python
            client = ExchangeRateV6Client(api_key="your_api_key")
            enriched_data = client.fetch_enriched_data(base_code="USD", target_code="EUR")
            print(enriched_data.base_code)  # Output: USD
            print(enriched_data.target_code)  # Output: EUR
            print(enriched_data.conversion_rate)  # Output: Conversion rate between USD and EUR
            ```
        """
        if not isinstance(base_code, str) or not isinstance(target_code, str):
            raise ValueError("Base code and target code must be a str")

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
        """
        Fetch historical exchange rates for a specific date.

        Args:
            base_code (str): The base currency code.
            date_obj (date): The date for which historical data is requested.
            amount (float): The amount of the base currency to convert.

        Returns:
            HistoricalData: Contains the historical exchange rate data for the requested date,
            including conversion amounts for different currencies.

        Raises:
            ValueError: If one of the given arguments is invalid
            UnsupportedCode: If the base currency code is not supported.
            MalformedRequest: If the request structure does not follow the expected format.
            InvalidKey: If the API key provided is invalid.
            InactiveAccount: If the account associated with the API key is not active.
            QuotaReached: If the request exceeds the number of allowed API requests for the account's plan.
            NoDataAvailable: If no exchange rates are available for the specific date provided.
            PlanUpgradeRequired: If the current plan does not support the requested data.
        """
        if not isinstance(base_code, str):
            raise ValueError("Base code must be a str")

        if not isinstance(date_obj, date):
            raise ValueError("Data must be a datetime.date instance")

        if not isinstance(amount, (int, float)):
            raise ValueError("Amount must be an integer or a float")

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
        """
        Fetch the API quota status to determine the number of requests remaining.

        Returns:
            APIQuotaStatus: Contains information about the current API quota, such as the
            remaining requests and the reset time.

        Raises:
            InvalidKey: If the API key provided is invalid.
            InactiveAccount: If the account associated with the API key is not active.
            QuotaReached: If the account has reached the limit of allowed API requests.
        """
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
