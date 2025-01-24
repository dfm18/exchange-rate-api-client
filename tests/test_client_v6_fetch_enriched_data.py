import unittest

from unittest.mock import patch, Mock, MagicMock

from exchange_rate_api_client._client import ExchangeRateApiV6Client

from exchange_rate_api_client.commons import EnrichedData, TargetData

from exchange_rate_api_client.exceptions import (
    UnsupportedCode,
    InvalidKey,
    InactiveAccount,
    QuotaReached,
    NoDataAvailable,
    PlanUpgradeRequired,
    MalformedRequest,
)


class TestExchangeRateV6Client(unittest.TestCase):
    def setUp(self):
        self.client = ExchangeRateApiV6Client("mock-api-key")

    @patch("exchange_rate_api_client._client.requests.get")
    def test_fetch_enriched_data(self, mock_get: Mock):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["GBP", "Pound Sterling"], ["JPY", "Japanese Yen"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "time_last_update_unix": 1585267200,
            "time_last_update_utc": "Fri, 27 Mar 2020 00:00:00 +0000",
            "time_next_update_unix": 1585270800,
            "time_next_update_utc": "Sat, 28 Mar 2020 01:00:00 +0000",
            "base_code": "GBP",
            "target_code": "JPY",
            "conversion_rate": 142.0543,
            "target_data": {
                "locale": "Japan",
                "two_letter_code": "JP",
                "currency_name": "Japanese Yen",
                "currency_name_short": "Yen",
                "display_symbol": "00A5",
                "flag_url": "https://www.exchangerate-api.com/img/docs/JP.gif",
            },
        }

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        expected = EnrichedData(
            time_last_update_unix=1585267200,
            time_last_update_utc="Fri, 27 Mar 2020 00:00:00 +0000",
            time_next_update_unix=1585270800,
            time_next_update_utc="Sat, 28 Mar 2020 01:00:00 +0000",
            base_code="GBP",
            target_code="JPY",
            conversion_rate=142.0543,
            target_data=TargetData(
                locale="Japan",
                two_letter_code="JP",
                currency_name="Japanese Yen",
                currency_name_short="Yen",
                display_symbol="00A5",
                flag_url="https://www.exchangerate-api.com/img/docs/JP.gif",
            ),
        )

        result = self.client.fetch_enriched_data("GBP", "JPY")

        self.assertEqual(expected.model_dump(), result.model_dump())

    def test_fetch_enriched_data_on_invalid_arguments_raises_exception(self):
        with self.assertRaises(ValueError):
            self.client.fetch_enriched_data(10, "EUR")

        with self.assertRaises(ValueError):
            self.client.fetch_enriched_data(None, "EUR")

        with self.assertRaises(ValueError):
            self.client.fetch_enriched_data("USD", 10)

        with self.assertRaises(ValueError):
            self.client.fetch_enriched_data("USD", None)

    @patch("exchange_rate_api_client._client.requests.get")
    def test_fetch_enriched_data_on_unsupported_code_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"]]
        }

        mock_get.return_value = mock_supported_codes_response

        with self.assertRaises(UnsupportedCode):
            result = self.client.fetch_enriched_data("GBP", "JPY")

    @patch("exchange_rate_api_client._client.requests.get")
    def test_fetch_enriched_data_exceptions_by_checking_supported_codes(
        self, mock_get: Mock
    ):
        mock_invalid_key_response = MagicMock()
        mock_invalid_key_response.status_code = 403
        mock_invalid_key_response.json.return_value = {"error-type": "invalid-key"}

        mock_inactive_account_response = MagicMock()
        mock_inactive_account_response.status_code = 403
        mock_inactive_account_response.json.return_value = {
            "error-type": "inactive-account"
        }

        mock_quota_reached_response = MagicMock()
        mock_quota_reached_response.status_code = 403
        mock_quota_reached_response.json.return_value = {"error-type": "quota-reached"}

        mock_unknown_error_type_response = MagicMock()
        mock_unknown_error_type_response.status_code = 400
        mock_unknown_error_type_response.json.return_value = {"error-type": "unknown"}

        mock_no_error_type_response = MagicMock()
        mock_no_error_type_response.status_code = 0
        mock_no_error_type_response.json.return_value = {}

        mock_get.side_effect = [
            mock_invalid_key_response,
            mock_inactive_account_response,
            mock_quota_reached_response,
            mock_unknown_error_type_response,
            mock_no_error_type_response,
        ]

        with self.assertRaises(InvalidKey):
            self.client.fetch_enriched_data("GBP", "JPY")

        with self.assertRaises(InactiveAccount):
            self.client.fetch_enriched_data("GBP", "JPY")

        with self.assertRaises(QuotaReached):
            self.client.fetch_enriched_data("GBP", "JPY")

        with self.assertRaises(Exception) as context:
            self.client.fetch_enriched_data("GBP", "JPY")

        self.assertEqual(str(context.exception), "Unknown error ocurred")

        with self.assertRaises(Exception) as context:
            self.client.fetch_enriched_data("GBP", "JPY")

        self.assertEqual(str(context.exception), "Unknown error ocurred")

    @patch("exchange_rate_api_client._client.requests.get")
    def test_fetch_enriched_data_on_unsupported_code_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["GBP", "Pound Sterling"], ["JPY", "Japanese Yen"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error-type": "unsupported-code"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(UnsupportedCode):
            self.client.fetch_enriched_data("GBP", "JPY")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/enriched/GBP/JPY",
            timeout=10,
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_fetch_enriched_data_on_invalid_key_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["GBP", "Pound Sterling"], ["JPY", "Japanese Yen"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error-type": "invalid-key"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(InvalidKey):
            self.client.fetch_enriched_data("GBP", "JPY")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/enriched/GBP/JPY",
            timeout=10,
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_fetch_enriched_data_on_inactive_account_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["GBP", "Pound Sterling"], ["JPY", "Japanese Yen"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error-type": "inactive-account"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(InactiveAccount):
            self.client.fetch_enriched_data("GBP", "JPY")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/enriched/GBP/JPY",
            timeout=10,
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_fetch_enriched_data_on_quota_reached_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["GBP", "Pound Sterling"], ["JPY", "Japanese Yen"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error-type": "quota-reached"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(QuotaReached):
            self.client.fetch_enriched_data("GBP", "JPY")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/enriched/GBP/JPY",
            timeout=10,
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_fetch_enriched_data_on_malformed_request_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["GBP", "Pound Sterling"], ["JPY", "Japanese Yen"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error-type": "malformed-request"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(MalformedRequest):
            self.client.fetch_enriched_data("GBP", "JPY")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/enriched/GBP/JPY",
            timeout=10,
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_fetch_enriched_data_on_plan_upgrade_required_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["GBP", "Pound Sterling"], ["JPY", "Japanese Yen"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error-type": "plan-upgrade-required"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(PlanUpgradeRequired):
            self.client.fetch_enriched_data("GBP", "JPY")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/enriched/GBP/JPY",
            timeout=10,
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_fetch_enriched_data_on_unknown_error_type_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["GBP", "Pound Sterling"], ["JPY", "Japanese Yen"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error-type": "unknown"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(Exception) as context:
            self.client.fetch_enriched_data("GBP", "JPY")

        self.assertEqual(str(context.exception), "Unknown error ocurred")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/enriched/GBP/JPY",
            timeout=10,
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_fetch_enriched_data_on_no_error_type_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["GBP", "Pound Sterling"], ["JPY", "Japanese Yen"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 0
        mock_response.json.return_value = {}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(Exception) as context:
            self.client.fetch_enriched_data("GBP", "JPY")

        self.assertEqual(str(context.exception), "Unknown error ocurred")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/enriched/GBP/JPY",
            timeout=10,
        )
