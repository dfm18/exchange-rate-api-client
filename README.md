# Exchange Rate API Client

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/exchange-rate-api-client)
![PyPI - License](https://img.shields.io/pypi/l/exchange-rate-api-client)
![PyPI](https://img.shields.io/pypi/v/exchange-rate-api-client)
![Downloads](https://img.shields.io/pypi/dm/exchange-rate-api-client)

Unofficial client to interact with the [Exchange Rate API](https://www.exchangerate-api.com/) V6.

- **Simple API client:** Easy-to-use interface to interact with the Exchange Rate API.
- **Open Access Support:** Fetch exchange rates without requiring an API key.

## Installation

Install package from PyPi with:

```bash
pip install exchange-rate-api-client
```

## Usage

### API Client

You can initializate a api client with your API key to access all endpoints:

```python
from exchange_rate_api_client import ExchangeRateApiV6Client

client = ExchangeRateApiV6Client(api_key="<YOUR_API_KEY>")

# Example: Convert 100 USD to EUR
conversion = client.pair_conversion(
    base_code="USD",
    target_code="EUR",
    amount=100,
)
print(conversion)
```

### Open Access

For basic access without an API key, fetch the latest exchange rates:

```python
from exchange_rate_api_client import fetch_exchange_rates

# Example: Fetch exchange rates for USD
data = fetch_exchange_rates(base_code="USD")
print(data)
```

### Additional Examples

#### Fetch enriched data:

```python
data = client.fetch_enriched_data(
    base_code="USD",
    target_code="JPY",
)
print(data)
```

#### Fetch historical data:

```python
from datetime import date

data = client.fetch_historical_data(
    base_code="USD",
    date_obj=date(2023, 1, 1),
    amount=100,
)
print(data)
```

## Requirements

- Python 3.7 or higher
- An API key from [Exchange Rate API](https://www.exchangerate-api.com/) for full access.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the client.

## Links

- [API Documentation](https://www.exchangerate-api.com/docs/overview)
- [Project Page](https://pypi.org/project/exchange-rate-api-client/)
