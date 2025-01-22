import unittest

from unittest.mock import patch, Mock

from exchange_rate_client._client import ExchangeRateV6Client

from exchange_rate_client.commons import APIQuotaStatus

from exchange_rate_client.exceptions import (
    InvalidKey,
    InactiveAccount,
    QuotaReached,
)


class TestExchangeRateV6Client(unittest.TestCase):
    def setUp(self):
        self.client = ExchangeRateV6Client("mock-api-key")

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_quota_info(self, mock_get: Mock):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "plan_quota": 30000,
            "requests_remaining": 25623,
            "refresh_day_of_month": 17,
            "extra_attribute": "extra",  # Extra attribute that will be ignored
        }

        expected = APIQuotaStatus(
            plan_quota=30000, requests_remaining=25623, refresh_day_of_month=17
        )

        result = self.client.fetch_quota_info()

        self.assertEqual(result.model_dump(), expected.model_dump())

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_quota_info_on_invalid_key_raises_exception(self, mock_get: Mock):
        mock_get.return_value.status_code = 403
        mock_get.return_value.json.return_value = {"error-type": "invalid-key"}

        with self.assertRaises(InvalidKey):
            self.client.fetch_quota_info()

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_quota_info_on_inactive_account_raises_exception(
        self, mock_get: Mock
    ):
        mock_get.return_value.status_code = 403
        mock_get.return_value.json.return_value = {"error-type": "inactive-account"}

        with self.assertRaises(InactiveAccount):
            self.client.fetch_quota_info()

    @patch("exchange_rate_client._client.requests.get")
    def test_fetch_quota_info_on_quota_reached_raises_exception(self, mock_get: Mock):
        mock_get.return_value.status_code = 403
        mock_get.return_value.json.return_value = {"error-type": "quota-reached"}

        with self.assertRaises(QuotaReached):
            self.client.fetch_quota_info()
