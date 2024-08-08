# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""Tests for the methods in the client."""
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

# pylint: disable=no-member
from frequenz.api.electricity_trading.v1 import electricity_trading_pb2
from google.protobuf import timestamp_pb2
from typing_extensions import Any, Generator

from frequenz.client.electricity_trading import (
    Client,
    Currency,
    DeliveryArea,
    DeliveryPeriod,
    Energy,
    EnergyMarketCodeType,
    MarketActor,
    MarketSide,
    Order,
    OrderDetail,
    OrderExecutionOption,
    OrderState,
    OrderType,
    Price,
    StateDetail,
    StateReason,
    TradeState,
)


@pytest.fixture
def set_up() -> Generator[Any, Any, Any]:
    """Set up the test suite."""
    # Create a mock client and stub
    _ = Client("grpc://unknown.host", connect=False)
    mock_stub = AsyncMock()
    _._stub = mock_stub  # pylint: disable=protected-access

    # Create a new event loop for each test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Set up the parameters for the orders
    gridpool_id = 123
    delivery_area = DeliveryArea(code="DE", code_type=EnergyMarketCodeType.EUROPE_EIC)
    delivery_period = DeliveryPeriod(
        start=datetime.fromisoformat("2023-01-01T00:00:00+00:00"),
        duration=timedelta(minutes=15),
    )
    order_type = OrderType.LIMIT
    side = MarketSide.BUY
    price = Price(amount=Decimal("50"), currency=Currency.EUR)
    quantity = Energy(mwh=Decimal("0.1"))
    order_execution_option = OrderExecutionOption.AON
    valid_until = datetime.fromisoformat("2023-01-01T00:00:00+00:00")

    yield {
        "client": _,
        "mock_stub": mock_stub,
        "loop": loop,
        "gridpool_id": gridpool_id,
        "delivery_area": delivery_area,
        "delivery_period": delivery_period,
        "order_type": order_type,
        "side": side,
        "price": price,
        "quantity": quantity,
        "order_execution_option": order_execution_option,
        "valid_until": valid_until,
    }

    loop.close()


# pylint: disable=redefined-outer-name
def set_up_order_detail_response(
    set_up: dict[str, Any],
    order_id: int = 1,
) -> electricity_trading_pb2.OrderDetail:
    """Set up an order detail response."""
    return OrderDetail(
        order_id=order_id,
        order=Order(
            delivery_area=set_up["delivery_area"],
            delivery_period=set_up["delivery_period"],
            type=set_up["order_type"],
            side=set_up["side"],
            price=set_up["price"],
            quantity=set_up["quantity"],
            execution_option=set_up["order_execution_option"],
        ),
        state_detail=StateDetail(
            state=OrderState.ACTIVE,
            state_reason=StateReason.ADD,
            market_actor=MarketActor.USER,
        ),
        open_quantity=Energy(mwh=Decimal("5.00")),
        filled_quantity=Energy(mwh=Decimal("0.00")),
        create_time=datetime.fromisoformat("2024-01-03T12:00:00+00:00"),
        modification_time=datetime.fromisoformat("2024-01-03T12:00:00+00:00"),
    ).to_pb()


def test_stream_gridpool_orders(set_up: dict[str, Any]) -> None:
    """Test the method streaming gridpool orders."""
    set_up["loop"].run_until_complete(
        set_up["client"].stream_gridpool_orders(set_up["gridpool_id"])
    )

    set_up["mock_stub"].ReceiveGridpoolOrdersStream.assert_called_once()
    args, _ = set_up["mock_stub"].ReceiveGridpoolOrdersStream.call_args
    assert args[0].gridpool_id == set_up["gridpool_id"]


def test_stream_gridpool_orders_with_optional_inputs(set_up: dict[str, Any]) -> None:
    """Test the method streaming gridpool orders with some fields to filter for."""
    # Fields to filter for
    order_states = [OrderState.ACTIVE]

    set_up["loop"].run_until_complete(
        set_up["client"].stream_gridpool_orders(
            set_up["gridpool_id"], order_states=order_states
        )
    )

    set_up["mock_stub"].ReceiveGridpoolOrdersStream.assert_called_once()
    args, _ = set_up["mock_stub"].ReceiveGridpoolOrdersStream.call_args
    assert args[0].gridpool_id == set_up["gridpool_id"]
    assert args[0].filter.states == [
        order_state.to_pb() for order_state in order_states
    ]


def test_stream_gridpool_trades(
    set_up: dict[str, Any],
) -> None:
    """Test the method streaming gridpool trades."""
    set_up["loop"].run_until_complete(
        set_up["client"].stream_gridpool_trades(
            gridpool_id=set_up["gridpool_id"], market_side=set_up["side"]
        )
    )

    set_up["mock_stub"].ReceiveGridpoolTradesStream.assert_called_once()
    args, _ = set_up["mock_stub"].ReceiveGridpoolTradesStream.call_args
    assert args[0].gridpool_id == set_up["gridpool_id"]
    assert args[0].filter.side == set_up["side"].to_pb()


def test_stream_public_trades(
    set_up: dict[str, Any],
) -> None:
    """Test the method streaming public trades."""
    # Fields to filter for
    trade_states = [TradeState.ACTIVE]

    set_up["loop"].run_until_complete(
        set_up["client"].stream_public_trades(states=trade_states)
    )

    set_up["mock_stub"].ReceivePublicTradesStream.assert_called_once()
    args, _ = set_up["mock_stub"].ReceivePublicTradesStream.call_args
    assert args[0].filter.states == [
        trade_state.to_pb() for trade_state in trade_states
    ]


def test_create_gridpool_order(
    set_up: dict[str, Any],
) -> None:
    """
    Test the method creating a gridpool order.

    The input parameters are all the mandatory fields and one optional field.
    """
    # Setup the expected response with valid values,
    # especially so that the DeliveryPeriod does not raise an error
    order_detail_response = set_up_order_detail_response(set_up)
    mock_response = electricity_trading_pb2.CreateGridpoolOrderResponse(
        order_detail=order_detail_response
    )
    set_up["mock_stub"].CreateGridpoolOrder.return_value = mock_response

    set_up["loop"].run_until_complete(
        set_up["client"].create_gridpool_order(
            gridpool_id=set_up["gridpool_id"],
            delivery_area=set_up["delivery_area"],
            delivery_period=set_up["delivery_period"],
            order_type=set_up["order_type"],
            side=set_up["side"],
            price=set_up["price"],
            quantity=set_up["quantity"],
            execution_option=set_up["order_execution_option"],  # optional field
        )
    )

    set_up["mock_stub"].CreateGridpoolOrder.assert_called_once()
    args, _ = set_up["mock_stub"].CreateGridpoolOrder.call_args
    assert args[0].gridpool_id == set_up["gridpool_id"]
    assert args[0].order.type == set_up["order_type"].to_pb()
    assert args[0].order.quantity == set_up["quantity"].to_pb()
    assert args[0].order.price == set_up["price"].to_pb()
    assert args[0].order.delivery_period == set_up["delivery_period"].to_pb()
    assert args[0].order.delivery_area == set_up["delivery_area"].to_pb()
    assert args[0].order.execution_option == set_up["order_execution_option"].to_pb()


def test_update_gridpool_order(
    set_up: dict[str, Any],
) -> None:
    """Test the method updating a gridpool order."""
    # Setup the expected response with valid values,
    # especially so that the DeliveryPeriod does not raise an error
    order_detail_response = set_up_order_detail_response(set_up)
    mock_response = electricity_trading_pb2.UpdateGridpoolOrderResponse(
        order_detail=order_detail_response
    )
    set_up["mock_stub"].UpdateGridpoolOrder.return_value = mock_response

    set_up["loop"].run_until_complete(
        set_up["client"].update_gridpool_order(
            gridpool_id=set_up["gridpool_id"],
            order_id=1,
            quantity=set_up["quantity"],
            valid_until=set_up["valid_until"],
        )
    )

    valid_until_pb = timestamp_pb2.Timestamp()
    valid_until_pb.FromDatetime(set_up["valid_until"])

    set_up["mock_stub"].UpdateGridpoolOrder.assert_called_once()
    args, _ = set_up["mock_stub"].UpdateGridpoolOrder.call_args
    assert args[0].update_order_fields.quantity == set_up["quantity"].to_pb()
    assert args[0].update_order_fields.valid_until == valid_until_pb
    # Test that other fields e.g. price are not set
    assert not args[0].update_order_fields.HasField(
        "price"
    ), "Price field should not be set."


def test_cancel_gridpool_order(
    set_up: dict[str, Any],
) -> None:
    """Test the method cancelling gridpool orders."""
    # Setup the expected response with valid values,
    # especially so that the DeliveryPeriod does not raise an error
    order_detail_response = set_up_order_detail_response(set_up)
    mock_response = electricity_trading_pb2.CancelGridpoolOrderResponse(
        order_detail=order_detail_response
    )

    # Order to cancel
    order_id = 1

    set_up["mock_stub"].CancelGridpoolOrder.return_value = mock_response

    set_up["loop"].run_until_complete(
        set_up["client"].cancel_gridpool_order(
            gridpool_id=set_up["gridpool_id"], order_id=order_id
        )
    )

    set_up["mock_stub"].CancelGridpoolOrder.assert_called_once()
    args, _ = set_up["mock_stub"].CancelGridpoolOrder.call_args
    assert args[0].gridpool_id == set_up["gridpool_id"]
    assert args[0].order_id == order_id


def test_list_gridpool_orders(
    set_up: dict[str, Any],
) -> None:
    """Test the method listing gridpool orders."""
    # Setup the expected response with valid values,
    # especially so that the DeliveryPeriod does not raise an error
    order_detail_response = set_up_order_detail_response(set_up)
    mock_response = electricity_trading_pb2.ListGridpoolOrdersResponse(
        order_details=[order_detail_response]
    )
    set_up["mock_stub"].ListGridpoolOrders.return_value = mock_response

    # Fields to filter for
    side = MarketSide.BUY
    order_states = [OrderState.ACTIVE]

    set_up["loop"].run_until_complete(
        set_up["client"].list_gridpool_orders(
            gridpool_id=set_up["gridpool_id"], side=side, order_states=order_states
        )
    )

    set_up["mock_stub"].ListGridpoolOrders.assert_called_once()
    args, _ = set_up["mock_stub"].ListGridpoolOrders.call_args
    assert args[0].filter.states == [
        order_state.to_pb() for order_state in order_states
    ]
    assert args[0].filter.side == side.to_pb()
