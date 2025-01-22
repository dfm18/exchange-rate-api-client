import unittest

from unittest.mock import patch, Mock, MagicMock

from exchange_rate_client._client import ExchangeRateV6Client

from exchange_rate_client.commons import HistoricalData

from exchange_rate_client.exceptions import (
    UnsupportedCode,
    InvalidKey,
    InactiveAccount,
    QuotaReached,
    NoDataAvailable,
    MalformedRequest,
)

from datetime import date


class TestExchangeRateV6Client(unittest.TestCase):
    def setUp(self):
        self.client = ExchangeRateV6Client("mock-api-key")

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_historical_data(self, mock_get: Mock):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "year": 2015,
            "month": 2,
            "day": 22,
            "base_code": "USD",
            "requested_amount": 4.00,
            "conversion_amounts": {
                "AUD": 5.664,
                "BRL": 16.0012,
                "CAD": 5.296,
                "CHF": 3.8976,
                "CNY": 25.4236,
                "DKK": 26.6404,
                "EUR": 3.5716,
                "GBP": 2.638,
            },
            "extra_attribute": "extra",  # Extra attribute that will be ignored
        }

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        expected = HistoricalData(
            year=2015,
            month=2,
            day=22,
            base_code="USD",
            requested_amount=4.00,
            conversion_amounts={
                "AUD": 5.664,
                "BRL": 16.0012,
                "CAD": 5.296,
                "CHF": 3.8976,
                "CNY": 25.4236,
                "DKK": 26.6404,
                "EUR": 3.5716,
                "GBP": 2.638,
            },
        )

        result = self.client.fetch_historical_data("USD", date(2015, 2, 22), 4.00)

        self.assertEqual(result.model_dump(), expected.model_dump())

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_historical_data_on_unsupported_code_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"]]
        }

        mock_get.return_value = mock_supported_codes_response

        with self.assertRaises(UnsupportedCode):
            self.client.fetch_historical_data("EUR", date(2015, 1, 1), 4.00)

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_historical_data_exceptions_by_checking_supported_codes(
        self, mock_get: Mock
    ):
        mock_unsupported_code_response = MagicMock()
        mock_unsupported_code_response.status_code = 400
        mock_unsupported_code_response.json.return_value = {
            "error-type": "unsupported-code"
        }

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
            mock_unsupported_code_response,
            mock_invalid_key_response,
            mock_inactive_account_response,
            mock_quota_reached_response,
            mock_unknown_error_type_response,
            mock_no_error_type_response,
        ]

        with self.assertRaises(UnsupportedCode):
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

        with self.assertRaises(InvalidKey):
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

        with self.assertRaises(InactiveAccount):
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

        with self.assertRaises(QuotaReached):
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

        with self.assertRaises(Exception):
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

        with self.assertRaises(Exception) as context:
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

        self.assertEqual(str(context.exception), "Unknown error ocurred")

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_historical_data_on_no_data_available_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error-type": "no-data-available"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(NoDataAvailable):
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_historical_data_on_unsupported_code_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error-type": "unsupported-code"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(UnsupportedCode):
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_historical_data_on_invalid_key_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error-type": "invalid-key"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(InvalidKey):
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_historical_data_on_inactive_account_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error-type": "inactive-account"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(InactiveAccount):
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_historical_data_on_quota_reached_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error-type": "quota-reached"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(QuotaReached):
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_historical_data_on_malformed_request_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error-type": "malformed-request"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(MalformedRequest):
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_historical_data_on_unknown_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error-type": "unknown"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(Exception) as context:
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

        self.assertIn("Unexpected error type", str(context.exception))

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_historical_data_on_no_error_type_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 0
        mock_response.json.return_value = {}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(Exception) as context:
            self.client.fetch_historical_data("USD", date(2015, 1, 1), 4.00)

        self.assertEqual(str(context.exception), "Unknown error ocurred")
