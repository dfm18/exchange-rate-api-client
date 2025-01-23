from typing import Callable, Optional

from .exceptions import (
    UnsupportedCode,
    InvalidKey,
    InactiveAccount,
    QuotaReached,
    PlanUpgradeRequired,
    NoDataAvailable,
    MalformedRequest,
)

import requests


ResponseErrorHandler = Callable[[requests.Response], None]


ErrorTypeHandler = Callable[[str], None]


def error_type_handler(func: ErrorTypeHandler) -> ResponseErrorHandler:
    def handler(response: requests.Response):
        data = response.json()
        if data and "error-type" in data:
            func(data["error-type"])

    return handler


def handle_unsupported_code(
    error_message: Optional[str] = None,
) -> ResponseErrorHandler:
    @error_type_handler
    def handler(error_type: str):
        if error_type == "unsupported-code":
            if error_message:
                raise UnsupportedCode(error_message)
            else:
                raise UnsupportedCode("The supplied code is not supported")

    return handler


@error_type_handler
def handle_invalid_key(error_type: str):
    if error_type == "invalid-key":
        raise InvalidKey("The api key is not valid")


@error_type_handler
def handle_inactive_account(error_type: str):
    if error_type == "inactive-account":
        raise InactiveAccount("The account's email wasn't confirmed")


@error_type_handler
def handle_quota_reached(error_type: str):
    if error_type == "quota-reached":
        raise QuotaReached("Reached the number of requests allowed in the plan")


@error_type_handler
def handle_required_plan_upgrade(error_type: str):
    if error_type == "plan-upgrade-required":
        raise PlanUpgradeRequired(
            "The account plan doesn't support this type of request"
        )


@error_type_handler
def handle_malformed_request(error_type: str):
    if error_type == "malformed-request":
        raise MalformedRequest(
            "Invalid request structure. May be an invalid API key or another request argument"
        )


def handle_no_data(error_message: str) -> ResponseErrorHandler:
    @error_type_handler
    def handler(error_type: str):
        if error_type == "no-data-available":
            raise NoDataAvailable(error_message)

    return handler
