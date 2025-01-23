import unittest

from unittest.mock import patch, Mock

from exchange_rate_client._open import fetch_exchange_rates

from exchange_rate_client.commons import ExchangeRates

from exchange_rate_client.exceptions import UnsupportedCode


class TestFetchExchangeRates(unittest.TestCase):
    @patch("exchange_rate_client._open.requests.get")
    def test_fetch_exchange_rates(self, mock_get: Mock):
        mock_get.return_value.json.return_value = {
            "time_last_update_unix": 1585872397,
            "time_last_update_utc": "Fri, 02 Apr 2020 00:06:37 +0000",
            "time_next_update_unix": 1585959987,
            "time_next_update_utc": "Sat, 03 Apr 2020 00:26:27 +0000",
            "time_eol_unix": 0,
            "base_code": "USD",
            "rates": {
                "USD": 1,
                "AED": 3.67,
                "ARS": 64.51,
                "AUD": 1.65,
                "CAD": 1.42,
                "CHF": 0.97,
                "CLP": 864.53,
                "CNY": 7.1,
                "EUR": 0.919,
                "GBP": 0.806,
                "HKD": 7.75,
                "...": 7.85,
                "...": 1.31,
                "...": 7.47,
            },
        }

        expected = ExchangeRates(
            time_last_update_unix=1585872397,
            time_last_update_utc="Fri, 02 Apr 2020 00:06:37 +0000",
            time_next_update_unix=1585959987,
            time_next_update_utc="Sat, 03 Apr 2020 00:26:27 +0000",
            time_eol_unix=0,
            base_code="USD",
            rates={
                "USD": 1,
                "AED": 3.67,
                "ARS": 64.51,
                "AUD": 1.65,
                "CAD": 1.42,
                "CHF": 0.97,
                "CLP": 864.53,
                "CNY": 7.1,
                "EUR": 0.919,
                "GBP": 0.806,
                "HKD": 7.75,
                "...": 7.85,
                "...": 1.31,
                "...": 7.47,
            },
        )

        result = fetch_exchange_rates("USD")

        self.assertEqual(result.model_dump(), expected.model_dump())

    def test_on_invalid_argument_raises_exception(self):
        with self.assertRaises(ValueError):
            fetch_exchange_rates(None)

        with self.assertRaises(ValueError):
            fetch_exchange_rates(221323)  # Not str

    @patch("exchange_rate_client._open.requests.get")
    def test_on_unsupported_code_raises_exception(self, mock_get: Mock):
        mock_get.return_value.json.return_value = {"error-type": "unsupported-code"}

        with self.assertRaises(UnsupportedCode):
            fetch_exchange_rates("USD")
