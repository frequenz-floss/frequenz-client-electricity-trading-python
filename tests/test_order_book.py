# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the receive_public_order_book rpc."""

import asyncio
import datetime as dt
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

import grpc
import pytest
from frequenz.api.common.v1alpha8.grid import delivery_area_pb2, delivery_duration_pb2
from frequenz.api.common.v1alpha8.market import power_pb2, price_pb2
from frequenz.api.common.v1alpha8.types import decimal_pb2
from frequenz.api.electricity_trading.v1 import (
    electricity_trading_pb2,
    electricity_trading_pb2_grpc,
)
from google.protobuf import timestamp_pb2
from grpc.aio import ServicerContext

from frequenz.client.electricity_trading import (
    Client,
    DeliveryArea,
    EnergyMarketCodeType,
    PublicOrder,
)

START_TIME = datetime.fromisoformat("2023-01-01T12:00:00+00:00")
START_TIME_PB = timestamp_pb2.Timestamp(seconds=1672574400)
CREATE_TIME = datetime.fromisoformat("2023-01-01T12:00:00+00:00")
CREATE_TIME_PB = timestamp_pb2.Timestamp(seconds=1672574400)
MODIFICATION_TIME = datetime.fromisoformat("2023-01-01T12:00:00+00:00")
MODIFICATION_TIME_PB = timestamp_pb2.Timestamp(seconds=1672574400)


class MockElectricityTradingService(
    electricity_trading_pb2_grpc.ElectricityTradingServiceServicer
):
    """A mock gRPC service to simulate historic vs real-time streams."""

    @staticmethod
    def _construct_public_order_book_record(
        order_id: int,
    ) -> electricity_trading_pb2.PublicOrderBookRecord:
        return electricity_trading_pb2.PublicOrderBookRecord(
            id=order_id,
            delivery_area=delivery_area_pb2.DeliveryArea(
                code="XYZ",
                code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
            ),
            delivery_period=delivery_duration_pb2.DeliveryPeriod(
                start=START_TIME_PB,
                duration=delivery_duration_pb2.DeliveryDuration.DELIVERY_DURATION_15,
            ),
            type=electricity_trading_pb2.OrderType.ORDER_TYPE_LIMIT,
            side=electricity_trading_pb2.MarketSide.MARKET_SIDE_BUY,
            price=price_pb2.Price(
                amount=decimal_pb2.Decimal(value="100.00"),
                currency=price_pb2.Price.Currency.CURRENCY_EUR,
            ),
            quantity=power_pb2.Power(mw=decimal_pb2.Decimal(value="5.00")),
            execution_option=(
                electricity_trading_pb2.OrderExecutionOption.ORDER_EXECUTION_OPTION_AON
            ),
            create_time=CREATE_TIME_PB,
            update_time=MODIFICATION_TIME_PB,
        )

    def _mark_as_unimplemented(self, context: Any) -> None:
        """Set the context to UNIMPLEMENTED."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented in the mock servicer.")

    async def ReceivePublicOrderBookStream(  # pylint: disable=invalid-overridden-method
        self,
        request: electricity_trading_pb2.ReceivePublicOrderBookStreamRequest,
        context: ServicerContext[
            electricity_trading_pb2.ReceivePublicOrderBookStreamRequest,
            electricity_trading_pb2.ReceivePublicOrderBookStreamResponse,
        ],
    ) -> AsyncIterator[electricity_trading_pb2.ReceivePublicOrderBookStreamResponse]:
        """Send different data based on whether start_time is set."""
        is_historic = request.HasField("start_time") and request.start_time.seconds > 0

        if is_historic:
            yield electricity_trading_pb2.ReceivePublicOrderBookStreamResponse(
                public_order_book_records=[
                    self._construct_public_order_book_record(1),
                    self._construct_public_order_book_record(2),
                ]
            )
            return

        yield electricity_trading_pb2.ReceivePublicOrderBookStreamResponse(
            public_order_book_records=[
                self._construct_public_order_book_record(9),
            ]
        )
        await asyncio.sleep(5)

    # --- Placeholder implementations for ALL other abstract methods ---

    async def CancelAllGridpoolOrders(  # pylint: disable=invalid-overridden-method
        self, request: Any, context: Any
    ) -> electricity_trading_pb2.CancelAllGridpoolOrdersResponse:
        """Handle CancelAllGridpoolOrders request."""
        self._mark_as_unimplemented(context)
        return electricity_trading_pb2.CancelAllGridpoolOrdersResponse()

    async def CancelGridpoolOrder(  # pylint: disable=invalid-overridden-method
        self, request: Any, context: Any
    ) -> electricity_trading_pb2.CancelGridpoolOrderResponse:
        """Handle CancelGridpoolOrder request."""
        self._mark_as_unimplemented(context)
        return electricity_trading_pb2.CancelGridpoolOrderResponse()

    async def CreateGridpoolOrder(  # pylint: disable=invalid-overridden-method
        self, request: Any, context: Any
    ) -> electricity_trading_pb2.CreateGridpoolOrderResponse:
        """Handle CreateGridpoolOrder request."""
        self._mark_as_unimplemented(context)
        return electricity_trading_pb2.CreateGridpoolOrderResponse()

    async def GetGridpoolOrder(  # pylint: disable=invalid-overridden-method
        self, request: Any, context: Any
    ) -> electricity_trading_pb2.GetGridpoolOrderResponse:
        """Handle GetGridpoolOrder request."""
        self._mark_as_unimplemented(context)
        return electricity_trading_pb2.GetGridpoolOrderResponse()

    async def ListGridpoolOrders(  # pylint: disable=invalid-overridden-method
        self, request: Any, context: Any
    ) -> electricity_trading_pb2.ListGridpoolOrdersResponse:
        """Handle ListGridpoolOrders request."""
        self._mark_as_unimplemented(context)
        return electricity_trading_pb2.ListGridpoolOrdersResponse()

    async def ListGridpoolTrades(  # pylint: disable=invalid-overridden-method
        self, request: Any, context: Any
    ) -> electricity_trading_pb2.ListGridpoolTradesResponse:
        """Handle ListGridpoolTrades request."""
        self._mark_as_unimplemented(context)
        return electricity_trading_pb2.ListGridpoolTradesResponse()

    async def ReceiveGridpoolOrdersStream(  # pylint: disable=invalid-overridden-method
        self, request: Any, context: Any
    ) -> AsyncIterator[electricity_trading_pb2.ReceiveGridpoolOrdersStreamResponse]:
        """Handle ReceiveGridpoolOrdersStream request."""
        self._mark_as_unimplemented(context)
        # The if False: part ensures that the yield statement is never actually executed.
        # The result is an empty—asynchronous generator that satisfies the type system and
        # the gRPC framework's requirements for an unimplemented streaming method.
        if False:  # pylint: disable=using-constant-test
            yield

    async def ReceiveGridpoolTradesStream(  # pylint: disable=invalid-overridden-method
        self, request: Any, context: Any
    ) -> AsyncIterator[electricity_trading_pb2.ReceiveGridpoolTradesStreamResponse]:
        """Handle ReceiveGridpoolTradesStream request."""
        self._mark_as_unimplemented(context)
        if False:  # pylint: disable=using-constant-test
            yield

    async def ReceivePublicTradesStream(  # pylint: disable=invalid-overridden-method
        self, request: Any, context: Any
    ) -> AsyncIterator[electricity_trading_pb2.ReceivePublicTradesStreamResponse]:
        """Handle ReceivePublicTradesStream request."""
        self._mark_as_unimplemented(context)
        if False:  # pylint: disable=using-constant-test
            yield

    async def UpdateGridpoolOrder(  # pylint: disable=invalid-overridden-method
        self, request: Any, context: Any
    ) -> electricity_trading_pb2.UpdateGridpoolOrderResponse:
        """Handle UpdateGridpoolOrder request."""
        self._mark_as_unimplemented(context)
        return electricity_trading_pb2.UpdateGridpoolOrderResponse()


@pytest.fixture
async def mock_server() -> AsyncIterator[str]:
    """Set up and tear down a mock gRPC server for the test session."""
    servicer = MockElectricityTradingService()
    server = grpc.aio.server()
    electricity_trading_pb2_grpc.add_ElectricityTradingServiceServicer_to_server(
        servicer, server
    )
    port = server.add_insecure_port("[::]:0")
    address = f"[::1]:{port}"
    await server.start()
    try:
        yield address
    finally:
        await server.stop(0)


@pytest.mark.asyncio
async def test_concurrent_historic_and_realtime_streams(mock_server: str) -> None:
    """Verify that historic and real-time streams from one client instance are distinct."""
    client = Client(server_url=f"grpc://{mock_server}?ssl=false")

    delivery_area = DeliveryArea(
        code="DE-TENNET", code_type=EnergyMarketCodeType.EUROPE_EIC
    )

    end_time = dt.datetime.now(dt.timezone.utc)
    start_time = end_time - dt.timedelta(hours=1)

    historic_stream = client.receive_public_order_book(
        delivery_area=delivery_area, start_time=start_time, end_time=end_time
    )
    realtime_stream = client.receive_public_order_book(delivery_area=delivery_area)

    historic_orders_received: list[PublicOrder] = []
    realtime_orders_received: list[PublicOrder] = []

    async def consume_historic() -> None:
        """Consume all items from the historic stream."""
        async for batch in historic_stream.new_receiver():
            historic_orders_received.extend(batch)

    async def consume_realtime() -> None:
        """Consume the first item from the real-time stream."""
        async for batch in realtime_stream.new_receiver():
            realtime_orders_received.extend(batch)
            break

    try:
        await asyncio.wait_for(
            asyncio.gather(consume_historic(), consume_realtime()), timeout=2.0
        )
    except asyncio.TimeoutError:
        pytest.fail(
            "Test timed out. The streams did not produce the expected data in time."
        )

    assert (
        len(historic_orders_received) == 2
    ), "Historic stream should receive a batch of 2"
    assert [order.public_order_id for order in historic_orders_received] == [1, 2]

    assert len(realtime_orders_received) == 1, "Real-time stream should receive 1 item"
    assert realtime_orders_received[0].public_order_id == 9
