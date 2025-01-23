from typing import List, Tuple

import unittest

from unittest.mock import MagicMock

from exchange_rate_client._error_handlers import (
    ResponseErrorHandler,
    handle_unsupported_code,
    handle_invalid_key,
    handle_inactive_account,
    handle_quota_reached,
    handle_required_plan_upgrade,
    handle_malformed_request,
    handle_no_data,
)

from exchange_rate_client.exceptions import (
    UnsupportedCode,
    InvalidKey,
    InactiveAccount,
    QuotaReached,
    PlanUpgradeRequired,
    MalformedRequest,
    NoDataAvailable,
)


class TestResponseErrorHandlers(unittest.TestCase):
    def test_all_error_handlers(self):
        error_handlers_and_exceptions_raised: List[
            Tuple[ResponseErrorHandler, Exception, str]
        ] = [
            (handle_unsupported_code(), UnsupportedCode, "unsupported-code"),
            (handle_invalid_key, InvalidKey, "invalid-key"),
            (handle_inactive_account, InactiveAccount, "inactive-account"),
            (handle_quota_reached, QuotaReached, "quota-reached"),
            (
                handle_required_plan_upgrade,
                PlanUpgradeRequired,
                "plan-upgrade-required",
            ),
            (handle_malformed_request, MalformedRequest, "malformed-request"),
            (handle_no_data("No data available"), NoDataAvailable, "no-data-available"),
        ]

        for (
            error_handler,
            exception,
            error_type,
        ) in error_handlers_and_exceptions_raised:
            with self.subTest(error_type=error_type):
                with self.assertRaises(exception):
                    mock_response = MagicMock()
                    mock_response.json.return_value = {"error-type": error_type}
                    error_handler(mock_response)
