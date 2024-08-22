# Frequenz Electricity Trading API Client

[![Build Status](https://github.com/frequenz-floss/frequenz-client-electricity-trading-python/actions/workflows/ci.yaml/badge.svg)](https://github.com/frequenz-floss/frequenz-client-electricity-trading-python/actions/workflows/ci.yaml)
[![PyPI Package](https://img.shields.io/pypi/v/frequenz-client-electricity-trading)](https://pypi.org/project/frequenz-client-electricity-trading/)
[![Docs](https://img.shields.io/badge/docs-latest-informational)](https://frequenz-floss.github.io/frequenz-client-electricity-trading-python/)

## Introduction

Electricity Trading API client for Python
The Frequenz Electricity Trading API client for Python is an easy-to-use Python interface built to interact with the Frequenz Electricity Trading API. It allows you to create orders, get market data, and manage your orders.

## Features
* **Create and manage gridpool orders**: Place new orders, update existing ones, and cancel orders when necessary.
* **Stream live data**: Get real-time updates on market data, including order books, trades, and market prices.
* **Retrieve historical data**: Access historical data on market trades.

## Supported Platforms

The following platforms are officially supported (tested):

- **Python:** 3.11
- **Operating System:** Ubuntu Linux 20.04
- **Architectures:** amd64, arm64

## Usage

### Installation

You can install the Frequenz Electricity Trading API client via pip. Replace `VERSION` with the specific version you wish to install.

```
# Choose the version you want to install
VERSION=0.2.2
pip install frequenz-client-electricity-trading==$VERSION
```

### Initialization

First, initialize the client with the appropriate server URL and API key.
```python
from frequenz.client.electricity_trading import Client

# Change server address if needed
SERVICE_URL = "grpc://electricity-trading.api.frequenz.com:443?ssl=true"
API_KEY = open('/path/to/api_key.txt').read().strip()
client = Client(
    server_url=SERVICE_URL,
    auth_key=API_KEY
)
```

### Create an Order

Here's an example of how one can create a limit order to buy energy.
```python
from frequenz.client.electricity_trading import (
    Currency,
    DeliveryArea,
    DeliveryPeriod,
    Energy,
    EnergyMarketCodeType,
    MarketSide,
    OrderType,
    Price,
)
from datetime import datetime, timedelta
from decimal import Decimal

# Define order parameters
gridpool_id = 1
delivery_area = DeliveryArea(
    code="10YDE-EON------1", # TenneT
    code_type=EnergyMarketCodeType.EUROPE_EIC
)
delivery_period = DeliveryPeriod(
    start=datetime.fromisoformat("2024-05-01T00:00:00"),
    duration=datetime.timedelta(minutes=15)
)
price = Price(amount=Decimal("50.0"), currency=Currency.EUR)
quantity = Energy(mwh=Decimal("0.1"))
order = await client.create_gridpool_order(
    gridpool_id=gridpool_id,
    delivery_area=delivery_area,
    delivery_period=delivery_period,
    order_type=OrderType.LIMIT,
    side=MarketSide.BUY,
    price=quantity,
    quantity=quantity,
)
```

### List Orders for a Gridpool

Orders for a given gridpool can be listed using various filters.

```python
from frequenz.client.electricity_trading import MarketSide

# List all orders for a given gridpool
orders = await self._client.list_gridpool_orders(
    gridpool_id=gridpool_id,
)

# List only the buy orders for a given gridpool
buy_orders = await self._client.list_gridpool_orders(
    gridpool_id=gridpool_id,
    side=MarketSide.BUY,
)
```

### Streaming Public Trades

To get real-time updates on market trades, one can use the following code snippet.

```python
async for public_trade in client.stream_public_trades():
    print(f"Received public trade: {public_trade}")
```

## Contributing

If you want to know how to build this project and contribute to it, please
check out the [Contributing Guide](CONTRIBUTING.md).
