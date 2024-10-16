# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""
Electricity Trading API client for Python.

## Frequenz Electricity Trading API Client

This module provides an easy-to-use Python interface to interact with the Frequenz Electricity
Trading API. It allows you to create orders, manage market data, and interact with the electricity
trading ecosystem.

### Features

- **Create and manage gridpool orders**: Place new orders, update existing ones, and cancel orders
when necessary.
- **Stream live data**: Get real-time updates on market data, including order books, trades,
and market prices.
- **Retrieve historical data**: Access historical data on market trades.

### Installation

You can install the Frequenz Electricity Trading API client via pip. Replace `VERSION`
with the specific version you wish to install.

# Choose the version you want to install
```bash
VERSION=0.2.3
pip install frequenz-client-electricity-trading==$VERSION
```

### Initialization

First, initialize the client with the appropriate server URL and API key.

???+ example "Initialize the client"

    ```python
    from frequenz.client.electricity_trading import Client

    # Change server address if needed
    SERVICE_URL = "grpc://electricity-trading.api.frequenz.com:443?ssl=true"
    with open('/path/to/api_key.txt', 'r', encoding='utf-8') as f:
        API_KEY = f.read().strip()
    client = Client(
        server_url=SERVICE_URL,
        auth_key=API_KEY
    )
    ```

### Example Usage

#### Create an Order

Here's an example of how to create a limit order to buy energy.


???+ example "Create a limit order"

    ```python
    from frequenz.client.electricity_trading import (
        Client,
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

    # Change server address if needed
    SERVICE_URL = "grpc://electricity-trading.api.frequenz.com:443?ssl=true"
    with open('/path/to/api_key.txt', 'r', encoding='utf-8') as f:
        API_KEY = f.read().strip()
    client = Client(
        server_url=SERVICE_URL,
        auth_key=API_KEY
    )

    # Define order parameters
    GRIDPOOL_ID = 1
    delivery_area = DeliveryArea(
        code="10YDE-EON------1",  # TenneT
        code_type=EnergyMarketCodeType.EUROPE_EIC
    )
    delivery_period = DeliveryPeriod(
        start=datetime.fromisoformat("2024-05-01T00:00:00+00:00"),
        duration=timedelta(minutes=15)
    )
    price = Price(amount=Decimal("50.0"), currency=Currency.EUR)
    quantity = Energy(mwh=Decimal("0.1"))
    order = await client.create_gridpool_order(
        gridpool_id=GRIDPOOL_ID,
        delivery_area=delivery_area,
        delivery_period=delivery_period,
        order_type=OrderType.LIMIT,
        side=MarketSide.BUY,
        price=price,
        quantity=quantity,
    )
    ```

#### List Orders for a Gridpool

Orders for a given gridpool can be listed using various filters.
???+ example "List orders for a gridpool"

    ```python
    from frequenz.client.electricity_trading import ( Client, MarketSide )

    # Change server address if needed
    SERVICE_URL = "grpc://electricity-trading.api.frequenz.com:443?ssl=true"
    with open('/path/to/api_key.txt', 'r', encoding='utf-8') as f:
        API_KEY = f.read().strip()
    client = Client(
        server_url=SERVICE_URL,
        auth_key=API_KEY
    )

    gridpool_id: int = 1

    # List all orders for a given gridpool
    orders = await client.list_gridpool_orders(
        gridpool_id=gridpool_id,
    )

    # List only the buy orders for a given gridpool
    buy_orders = await client.list_gridpool_orders(
        gridpool_id=gridpool_id,
        side=MarketSide.BUY,
    )
    ```


#### Streaming Public Trades

To get real-time updates on market trades, use the following code:

???+ example "Stream public trades"
    ```python
    from frequenz.client.electricity_trading import Client

    # Change server address if needed
    SERVICE_URL = "grpc://electricity-trading.api.frequenz.com:443?ssl=true"
    with open('/path/to/api_key.txt', 'r', encoding='utf-8') as f:
        API_KEY = f.read().strip()
    client = Client(
        server_url=SERVICE_URL,
        auth_key=API_KEY
    )
    stream_public_trades = await client.stream_public_trades()
    async for public_trade in stream_public_trades:
        print(f"Received public trade: {public_trade}")
    ```

"""

from ._client import Client
from ._types import (
    Currency,
    DeliveryArea,
    DeliveryDuration,
    DeliveryPeriod,
    EnergyMarketCodeType,
    GridpoolOrderFilter,
    GridpoolTradeFilter,
    MarketActor,
    MarketSide,
    Order,
    OrderDetail,
    OrderExecutionOption,
    OrderState,
    OrderType,
    Power,
    Price,
    PublicTrade,
    PublicTradeFilter,
    StateDetail,
    StateReason,
    Trade,
    TradeState,
    UpdateOrder,
)

__all__ = [
    "Client",
    "Currency",
    "DeliveryArea",
    "DeliveryDuration",
    "DeliveryPeriod",
    "EnergyMarketCodeType",
    "GridpoolOrderFilter",
    "GridpoolTradeFilter",
    "MarketSide",
    "MarketActor",
    "Order",
    "OrderDetail",
    "OrderExecutionOption",
    "OrderState",
    "OrderType",
    "Power",
    "Price",
    "PublicTrade",
    "PublicTradeFilter",
    "UpdateOrder",
    "StateDetail",
    "StateReason",
    "Trade",
    "TradeState",
]
