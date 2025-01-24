import requests

from .exceptions import UnsupportedCode

from .commons import ExchangeRates


def fetch_exchange_rates(base_code: str):
    if base_code is None or not isinstance(base_code, str):
        raise ValueError("The base code must be a str")

    url = f"https://open.er-api.com/v6/latest/{base_code}"

    response = requests.get(url)

    data = response.json()

    if "error-type" in data:
        if data["error-type"] == "unsupported-code":
            raise UnsupportedCode(f"The base code {base_code} is not supported")

    obj = ExchangeRates(**data)

    return obj
