# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""Module to define the client class."""

# pylint: disable=too-many-lines

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, AsyncIterator, Awaitable, Callable, cast
from zoneinfo import ZoneInfo

import grpc
from frequenz.api.common.v1.pagination.pagination_params_pb2 import PaginationParams

# pylint: disable=no-member
from frequenz.api.electricity_trading.v1 import (
    electricity_trading_pb2,
    electricity_trading_pb2_grpc,
)
from frequenz.api.electricity_trading.v1.electricity_trading_pb2_grpc import (
    ElectricityTradingServiceStub,
)
from frequenz.client.base.client import BaseApiClient
from frequenz.client.base.exception import ClientNotConnected
from frequenz.client.base.streaming import GrpcStreamBroadcaster
from frequenz.client.common.pagination import Params
from google.protobuf import field_mask_pb2, struct_pb2
from google.protobuf.timestamp_pb2 import Timestamp

from ._types import (
    DeliveryArea,
    DeliveryPeriod,
    GridpoolOrderFilter,
    GridpoolTradeFilter,
    MarketSide,
    Order,
    OrderDetail,
    OrderExecutionOption,
    OrderState,
    OrderType,
    Power,
    Price,
    PublicOrder,
    PublicOrderBookFilter,
    PublicTrade,
    PublicTradeFilter,
    Trade,
    TradeState,
    UpdateOrder,
)

_logger = logging.getLogger(__name__)


class _NoValue:
    """A unique object to signify 'no value passed'."""


NO_VALUE = _NoValue()
PRECISION_DECIMAL_PRICE = 2
PRECISION_DECIMAL_QUANTITY = 1

MIN_QUANTITY_MW = Decimal("0.1")
MIN_PRICE = Decimal(-9999.0)
MAX_PRICE = Decimal(9999.0)


def validate_decimal_places(value: Decimal, decimal_places: int, name: str) -> None:
    """
    Validate that the decimal places of a given value do not exceed a specified limit.

    Args:
        value: The value to be checked.
        decimal_places: The maximum allowed decimal places.
        name: The name of the value (for error messages).

    Raises:
        ValueError: If the value has more decimal places than allowed.
                    or the value is not a valid decimal number.
    """
    if decimal_places < 0:
        raise ValueError("The decimal places must be a non-negative integer.")

    try:
        exponent = int(value.as_tuple().exponent)
        if abs(exponent) > decimal_places:
            raise ValueError(
                f"The {name} cannot have more than {decimal_places} decimal places."
            )
    except InvalidOperation as exc:
        raise ValueError(
            f"The value {value} for {name} is not a valid decimal number."
        ) from exc


async def grpc_call_with_timeout(
    call: Callable[..., Awaitable[Any]],
    *args: Any,
    timeout: timedelta | None = None,
    **kwargs: Any,
) -> Any:
    """
    Call a gRPC function with a timeout (in seconds).

    Args:
        call: The gRPC method to be called.
        *args: Positional arguments for the gRPC call.
        timeout: Timeout duration, defaults to None.
        **kwargs: Keyword arguments for the gRPC call.

    Returns:
        The result of the gRPC call.

    Raises:
        asyncio.TimeoutError: If the call exceeds the timeout.
    """
    if timeout is None:
        return await call(*args, **kwargs)
    try:
        return await asyncio.wait_for(
            call(*args, **kwargs), timeout=timeout.total_seconds()
        )
    except asyncio.TimeoutError:
        _logger.exception("Timeout while calling %s", call)
        raise


def dt_to_pb_timestamp_utc(dt: datetime) -> Timestamp:
    """
    Convert a Python datetime object to a UTC Protobuf Timestamp.

    The input datetime 'dt' MUST be timezone-aware.

    Args:
        dt: The Python datetime object to convert.

    Returns:
        A Protobuf Timestamp object representing the time in UTC.

    Raises:
        TypeError: If dt is not a datetime.datetime object.
        ValueError: If the input datetime object is naive (lacks timezone info).
    """
    if not isinstance(dt, datetime):
        raise TypeError("Input must be a datetime.datetime object")

    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise ValueError("Input datetime object must be timezone-aware.")

    timestamp = Timestamp()
    timestamp.FromDatetime(dt.astimezone(ZoneInfo("UTC")))

    return timestamp


class Client(BaseApiClient[ElectricityTradingServiceStub]):
    """Electricity trading client."""

    _instances: dict[tuple[str, str | None, str | None], "Client"] = {}

    def __new__(
        cls,
        server_url: str,
        connect: bool = True,
        auth_key: str | None = None,
        sign_secret: str | None = None,
    ) -> "Client":
        """
        Create a new instance of the client or return an existing one if it already exists.

        Args:
            server_url: The URL of the Electricity Trading service.
            connect: Whether to connect to the server immediately.
            auth_key: The API key for the authorization.
            sign_secret: The cryptographic secret to use for HMAC generation.

        Returns:
            The client instance.
        """
        key = (server_url, auth_key, sign_secret)

        # Check if an instance already exists for this key
        if key not in cls._instances:
            # If not, create a new instance and store it in the cache
            instance = super(Client, cls).__new__(cls)
            cls._instances[key] = instance

        return cls._instances[key]

    def __init__(
        self,
        server_url: str,
        connect: bool = True,
        auth_key: str | None = None,
        sign_secret: str | None = None,
    ) -> None:
        """Initialize the client.

        Args:
            server_url: The URL of the Electricity Trading service.
            connect: Whether to connect to the server immediately.
            auth_key: The API key for the authorization.
            sign_secret: The cryptographic secret to use for HMAC generation.
        """
        if not hasattr(
            self, "_initialized"
        ):  # Prevent re-initialization of existing instances
            super().__init__(
                server_url,
                connect=connect,
                create_stub=ElectricityTradingServiceStub,
                auth_key=auth_key,
                sign_secret=sign_secret,
            )
            self._initialized = True

        self._gridpool_orders_streams: dict[
            tuple[int, GridpoolOrderFilter],
            GrpcStreamBroadcaster[
                electricity_trading_pb2.ReceiveGridpoolOrdersStreamResponse, OrderDetail
            ],
        ] = {}

        self._gridpool_trades_streams: dict[
            tuple[int, GridpoolTradeFilter],
            GrpcStreamBroadcaster[
                electricity_trading_pb2.ReceiveGridpoolTradesStreamResponse, Trade
            ],
        ] = {}

        self._public_trades_streams: dict[
            PublicTradeFilter,
            GrpcStreamBroadcaster[
                electricity_trading_pb2.ReceivePublicTradesStreamResponse, PublicTrade
            ],
        ] = {}

        self._public_orders_streams: dict[
            PublicOrderBookFilter,
            GrpcStreamBroadcaster[
                electricity_trading_pb2.ReceivePublicOrderBookStreamResponse,
                list[PublicOrder],
            ],
        ] = {}

    @property
    def stub(self) -> electricity_trading_pb2_grpc.ElectricityTradingServiceAsyncStub:
        """
        Get the gRPC stub for the Electricity Trading service.

        Returns:
            The gRPC stub.

        Raises:
            ClientNotConnected: If the client is not connected to the server.
        """
        if self._stub is None:
            raise ClientNotConnected(server_url=self.server_url, operation="stub")
        # This type: ignore is needed because we need to cast the sync stub to
        # the async stub, but we can't use cast because the async stub doesn't
        # actually exists to the eyes of the interpreter, it only exists for the
        # type-checker, so it can only be used for type hints.
        return self._stub  # type: ignore

    def gridpool_orders_stream(
        # pylint: disable=too-many-arguments
        self,
        gridpool_id: int,
        *,
        order_states: list[OrderState] | None = None,
        market_side: MarketSide | None = None,
        delivery_area: DeliveryArea | None = None,
        delivery_period: DeliveryPeriod | None = None,
        tag: str | None = None,
    ) -> GrpcStreamBroadcaster[
        electricity_trading_pb2.ReceiveGridpoolOrdersStreamResponse, OrderDetail
    ]:
        """
        Stream gridpool orders.

        Args:
            gridpool_id: ID of the gridpool to stream orders for.
            order_states: List of order states to filter for.
            market_side: Market side to filter for.
            delivery_area: Delivery area to filter for.
            delivery_period: Delivery period to filter for.
            tag: Tag to filter for.

        Returns:
            Async generator of orders.

        Raises:
            grpc.RpcError: If an error occurs while streaming the orders.
        """
        self.validate_params(delivery_period=delivery_period)

        gridpool_order_filter = GridpoolOrderFilter(
            order_states=order_states,
            side=market_side,
            delivery_area=delivery_area,
            delivery_period=delivery_period,
            tag=tag,
        )

        stream_key = (gridpool_id, gridpool_order_filter)

        if (
            stream_key not in self._gridpool_orders_streams
            or not self._gridpool_orders_streams[stream_key].is_running
        ):
            try:
                self._gridpool_orders_streams[stream_key] = GrpcStreamBroadcaster(
                    f"electricity-trading-{stream_key}",
                    lambda: self.stub.ReceiveGridpoolOrdersStream(
                        electricity_trading_pb2.ReceiveGridpoolOrdersStreamRequest(
                            gridpool_id=gridpool_id,
                            filter=gridpool_order_filter.to_pb(),
                        ),
                    ),
                    lambda response: OrderDetail.from_pb(response.order_detail),
                )
            except grpc.RpcError as e:
                _logger.exception(
                    "Error occurred while streaming gridpool orders: %s", e
                )
                raise
        return self._gridpool_orders_streams[stream_key]

    def gridpool_trades_stream(
        # pylint: disable=too-many-arguments
        self,
        gridpool_id: int,
        *,
        trade_states: list[TradeState] | None = None,
        trade_ids: list[int] | None = None,
        market_side: MarketSide | None = None,
        delivery_period: DeliveryPeriod | None = None,
        delivery_area: DeliveryArea | None = None,
    ) -> GrpcStreamBroadcaster[
        electricity_trading_pb2.ReceiveGridpoolTradesStreamResponse, Trade
    ]:
        """
        Stream gridpool trades.

        Args:
            gridpool_id: The ID of the gridpool to stream trades for.
            trade_states: List of trade states to filter for.
            trade_ids: List of trade IDs to filter for.
            market_side: The market side to filter for.
            delivery_period: The delivery period to filter for.
            delivery_area: The delivery area to filter for.

        Returns:
            The gridpool trades streamer.

        Raises:
            grpc.RpcError: If an error occurs while streaming gridpool trades.
        """
        self.validate_params(delivery_period=delivery_period)

        gridpool_trade_filter = GridpoolTradeFilter(
            trade_states=trade_states,
            trade_ids=trade_ids,
            side=market_side,
            delivery_period=delivery_period,
            delivery_area=delivery_area,
        )

        stream_key = (gridpool_id, gridpool_trade_filter)

        if (
            stream_key not in self._gridpool_trades_streams
            or not self._gridpool_trades_streams[stream_key].is_running
        ):
            try:
                self._gridpool_trades_streams[stream_key] = GrpcStreamBroadcaster(
                    f"electricity-trading-{stream_key}",
                    lambda: self.stub.ReceiveGridpoolTradesStream(
                        electricity_trading_pb2.ReceiveGridpoolTradesStreamRequest(
                            gridpool_id=gridpool_id,
                            filter=gridpool_trade_filter.to_pb(),
                        ),
                    ),
                    lambda response: Trade.from_pb(response.trade),
                )
            except grpc.RpcError as e:
                _logger.exception(
                    "Error occurred while streaming gridpool trades: %s", e
                )
                raise
        return self._gridpool_trades_streams[stream_key]

    def validate_params(
        # pylint: disable=too-many-arguments, too-many-branches
        self,
        *,
        price: Price | None | _NoValue = NO_VALUE,
        quantity: Power | None | _NoValue = NO_VALUE,
        stop_price: Price | None | _NoValue = NO_VALUE,
        peak_price_delta: Price | None | _NoValue = NO_VALUE,
        display_quantity: Power | None | _NoValue = NO_VALUE,
        delivery_period: DeliveryPeriod | None = None,
        valid_until: datetime | None | _NoValue = NO_VALUE,
        execution_option: OrderExecutionOption | None | _NoValue = NO_VALUE,
        order_type: OrderType | None = None,
    ) -> None:
        """
        Validate the parameters of an order.

        This method ensures the following:
        - Price and quantity values have the correct number of decimal places and are positive.
        - The delivery_start and valid_until values are in the future.

        Args:
            price: The price of the order.
            quantity: The quantity of the order.
            stop_price: The stop price of the order.
            peak_price_delta: The peak price delta of the order.
            display_quantity: The display quantity of the order.
            delivery_period: The delivery period of the order.
            valid_until: The valid until of the order.
            execution_option: The execution option of the order.
            order_type: The order type.

        Raises:
            ValueError: If the parameters are invalid.
            NotImplementedError: If the order type is not supported.
        """
        if not isinstance(price, _NoValue) and price is not None:
            if price.amount < MIN_PRICE or price.amount > MAX_PRICE:
                raise ValueError(f"Price must be between {MIN_PRICE} and {MAX_PRICE}.")
            validate_decimal_places(price.amount, PRECISION_DECIMAL_PRICE, "price")
        if not isinstance(quantity, _NoValue) and quantity is not None:
            if quantity.mw <= 0:
                raise ValueError("Quantity must be strictly positive")
            if quantity.mw < MIN_QUANTITY_MW:
                raise ValueError(f"Quantity must be at least {MIN_QUANTITY_MW} MW.")
            validate_decimal_places(quantity.mw, PRECISION_DECIMAL_QUANTITY, "quantity")
        if not isinstance(stop_price, _NoValue) and stop_price is not None:
            raise NotImplementedError(
                "STOP_LIMIT orders are not supported yet, so stop_price cannot be set."
            )
        if not isinstance(peak_price_delta, _NoValue) and peak_price_delta is not None:
            raise NotImplementedError(
                "ICEBERG orders are not supported yet, so peak_price_delta cannot be set."
            )
        if not isinstance(display_quantity, _NoValue) and display_quantity is not None:
            raise NotImplementedError(
                "ICEBERG orders are not supported yet, so display_quantity cannot be set."
            )
        if delivery_period is not None:
            if delivery_period.start < datetime.now(timezone.utc):
                raise ValueError("delivery_period must be in the future")
        if not isinstance(valid_until, _NoValue) and valid_until is not None:
            if (
                not isinstance(execution_option, _NoValue)
                and execution_option is not None
            ):
                if execution_option in [
                    OrderExecutionOption.AON,
                    OrderExecutionOption.FOK,
                    OrderExecutionOption.IOC,
                ]:
                    raise ValueError(
                        "valid_until must be None when execution_option is set to AON, FOK, or IOC"
                    )

            if valid_until < datetime.now(timezone.utc):
                raise ValueError("valid_until must be in the future")
        if order_type is not None:
            if order_type != OrderType.LIMIT:
                raise NotImplementedError("Currently only limit orders are supported.")

    async def create_gridpool_order(
        # pylint: disable=too-many-arguments, too-many-locals
        self,
        gridpool_id: int,
        *,
        delivery_area: DeliveryArea,
        delivery_period: DeliveryPeriod,
        order_type: OrderType,
        side: MarketSide,
        price: Price,
        quantity: Power,
        stop_price: Price | None = None,
        peak_price_delta: Price | None = None,
        display_quantity: Power | None = None,
        execution_option: OrderExecutionOption | None = None,
        valid_until: datetime | None = None,
        payload: dict[str, struct_pb2.Value] | None = None,
        tag: str | None = None,
        timeout: timedelta | None = None,
    ) -> OrderDetail:
        """
        Create a gridpool order.

        Args:
            gridpool_id: ID of the gridpool to create the order for.
            delivery_area: Delivery area of the order.
            delivery_period: Delivery period of the order.
            order_type: Type of the order.
            side: Side of the order.
            price: Price of the order.
            quantity: Quantity of the order.
            stop_price: Stop price of the order.
            peak_price_delta: Peak price delta of the order.
            display_quantity: Display quantity of the order.
            execution_option: Execution option of the order.
            valid_until: Valid until of the order.
            payload: Payload of the order.
            tag: Tag of the order.
            timeout: Timeout duration, defaults to None.

        Returns:
            The created order.

        Raises:
            grpc.RpcError: An error occurred while creating the order.
        """
        self.validate_params(
            price=price,
            quantity=quantity,
            stop_price=stop_price,
            peak_price_delta=peak_price_delta,
            display_quantity=display_quantity,
            delivery_period=delivery_period,
            valid_until=valid_until,
            execution_option=execution_option,
            order_type=order_type,
        )
        order = Order(
            delivery_area=delivery_area,
            delivery_period=delivery_period,
            type=order_type,
            side=side,
            price=price,
            quantity=quantity,
            stop_price=stop_price,
            peak_price_delta=peak_price_delta,
            display_quantity=display_quantity,
            execution_option=execution_option,
            valid_until=valid_until,
            payload=payload,
            tag=tag,
        )

        try:
            response = await cast(
                Awaitable[electricity_trading_pb2.CreateGridpoolOrderResponse],
                grpc_call_with_timeout(
                    self.stub.CreateGridpoolOrder,
                    electricity_trading_pb2.CreateGridpoolOrderRequest(
                        gridpool_id=gridpool_id, order=order.to_pb()
                    ),
                    timeout=timeout,
                ),
            )
        except grpc.RpcError as e:
            _logger.exception("Error occurred while creating gridpool order: %s", e)
            raise

        return OrderDetail.from_pb(response.order_detail)

    async def update_gridpool_order(
        # pylint: disable=too-many-arguments, too-many-locals
        self,
        gridpool_id: int,
        *,
        order_id: int,
        price: Price | None | _NoValue = NO_VALUE,
        quantity: Power | None | _NoValue = NO_VALUE,
        stop_price: Price | None | _NoValue = NO_VALUE,
        peak_price_delta: Price | None | _NoValue = NO_VALUE,
        display_quantity: Power | None | _NoValue = NO_VALUE,
        execution_option: OrderExecutionOption | None | _NoValue = NO_VALUE,
        valid_until: datetime | None | _NoValue = NO_VALUE,
        payload: dict[str, struct_pb2.Value] | None | _NoValue = NO_VALUE,
        tag: str | None | _NoValue = NO_VALUE,
        timeout: timedelta | None = None,
    ) -> OrderDetail:
        """
        Update an existing order for a given Gridpool.

        Args:
            gridpool_id: ID of the Gridpool the order belongs to.
            order_id: Order ID.
            price: The updated limit price at which the contract is to be traded.
                This is the maximum price for a BUY order or the minimum price for a SELL order.
            quantity: The updated quantity of the contract being traded, specified in MW.
            stop_price: Applicable for STOP_LIMIT orders. This is the updated stop price that
                triggers the limit order.
            peak_price_delta: Applicable for ICEBERG orders. This is the updated price difference
                between the peak price and the limit price.
            display_quantity: Applicable for ICEBERG orders. This is the updated quantity of the
                order to be displayed in the order book.
            execution_option: Updated execution options such as All or None, Fill or Kill, etc.
            valid_until: This is an updated timestamp defining the time after which the order
                should be cancelled if not filled. The timestamp is in UTC.
            payload: Updated user-defined payload individual to a specific order. This can be any
                data that the user wants to associate with the order.
            tag: Updated user-defined tag to group related orders.
            timeout: Timeout duration, defaults to None.

        Returns:
            The updated order.

        Raises:
            ValueError: If no fields to update are provided.
            grpc.RpcError: An error occurred while updating the order.
        """
        self.validate_params(
            price=price,
            quantity=quantity,
            stop_price=stop_price,
            peak_price_delta=peak_price_delta,
            display_quantity=display_quantity,
            valid_until=valid_until,
            execution_option=execution_option,
        )

        params = {
            "price": price,
            "quantity": quantity,
            "stop_price": stop_price,
            "peak_price_delta": peak_price_delta,
            "display_quantity": display_quantity,
            "execution_option": execution_option,
            "valid_until": valid_until,
            "payload": payload,
            "tag": tag,
        }

        if all(value is NO_VALUE for value in params.values()):
            raise ValueError("At least one field to update must be provided.")

        paths = [param for param, value in params.items() if value is not NO_VALUE]

        # Field mask specifying which fields should be updated
        # This is used so that we can update parameters with None values
        update_mask = field_mask_pb2.FieldMask(paths=paths)

        update_order_fields = UpdateOrder(
            price=None if isinstance(price, _NoValue) else price,
            quantity=None if isinstance(quantity, _NoValue) else quantity,
            stop_price=None if isinstance(stop_price, _NoValue) else stop_price,
            peak_price_delta=(
                None if isinstance(peak_price_delta, _NoValue) else peak_price_delta
            ),
            display_quantity=(
                None if isinstance(display_quantity, _NoValue) else display_quantity
            ),
            execution_option=(
                None if isinstance(execution_option, _NoValue) else execution_option
            ),
            valid_until=(None if isinstance(valid_until, _NoValue) else valid_until),
            payload=None if isinstance(payload, _NoValue) else payload,
            tag=None if isinstance(tag, _NoValue) else tag,
        )

        try:
            response = await cast(
                Awaitable[electricity_trading_pb2.UpdateGridpoolOrderResponse],
                grpc_call_with_timeout(
                    self.stub.UpdateGridpoolOrder,
                    electricity_trading_pb2.UpdateGridpoolOrderRequest(
                        gridpool_id=gridpool_id,
                        order_id=order_id,
                        update_order_fields=update_order_fields.to_pb(),
                        update_mask=update_mask,
                    ),
                    timeout=timeout,
                ),
            )
            return OrderDetail.from_pb(response.order_detail)

        except grpc.RpcError as e:
            _logger.exception("Error occurred while updating gridpool order: %s", e)
            raise

    async def cancel_gridpool_order(
        self,
        gridpool_id: int,
        *,
        order_id: int,
        timeout: timedelta | None = None,
    ) -> OrderDetail:
        """
        Cancel a single order for a given Gridpool.

        Args:
            gridpool_id: The Gridpool to cancel the order for.
            order_id: The order to cancel.
            timeout: Timeout duration, defaults to None.

        Returns:
            The cancelled order.

        Raises:
            grpc.RpcError: If an error occurs while cancelling the gridpool order.
        """
        try:
            response = await cast(
                Awaitable[electricity_trading_pb2.CancelGridpoolOrderResponse],
                grpc_call_with_timeout(
                    self.stub.CancelGridpoolOrder,
                    electricity_trading_pb2.CancelGridpoolOrderRequest(
                        gridpool_id=gridpool_id, order_id=order_id
                    ),
                    timeout=timeout,
                ),
            )
            return OrderDetail.from_pb(response.order_detail)
        except grpc.RpcError as e:
            _logger.exception("Error occurred while cancelling gridpool order: %s", e)
            raise

    async def cancel_all_gridpool_orders(
        self,
        gridpool_id: int,
        *,
        timeout: timedelta | None = None,
    ) -> int:
        """
        Cancel all orders for a specific Gridpool.

        Args:
            gridpool_id: The Gridpool to cancel the orders for.
            timeout: Timeout duration, defaults to None.

        Returns:
            The ID of the Gridpool for which the orders were cancelled.

        Raises:
            grpc.RpcError: If an error occurs while cancelling all gridpool orders.
        """
        try:
            response = await cast(
                Awaitable[electricity_trading_pb2.CancelAllGridpoolOrdersResponse],
                grpc_call_with_timeout(
                    self.stub.CancelAllGridpoolOrders,
                    electricity_trading_pb2.CancelAllGridpoolOrdersRequest(
                        gridpool_id=gridpool_id
                    ),
                    timeout=timeout,
                ),
            )

            return response.gridpool_id
        except grpc.RpcError as e:
            _logger.exception(
                "Error occurred while cancelling all gridpool orders: %s", e
            )
            raise

    async def get_gridpool_order(
        self,
        gridpool_id: int,
        *,
        order_id: int,
        timeout: timedelta | None = None,
    ) -> OrderDetail:
        """
        Get a single order from a given gridpool.

        Args:
            gridpool_id: The Gridpool to retrieve the order for.
            order_id: The order to retrieve.
            timeout: Timeout duration, defaults to None.

        Returns:
            The order.

        Raises:
            grpc.RpcError: If an error occurs while getting the order.
        """
        try:
            response = await cast(
                Awaitable[electricity_trading_pb2.GetGridpoolOrderResponse],
                grpc_call_with_timeout(
                    self.stub.GetGridpoolOrder,
                    electricity_trading_pb2.GetGridpoolOrderRequest(
                        gridpool_id=gridpool_id, order_id=order_id
                    ),
                    timeout=timeout,
                ),
            )

            return OrderDetail.from_pb(response.order_detail)
        except grpc.RpcError as e:
            _logger.exception("Error occurred while getting gridpool order: %s", e)
            raise

    async def list_gridpool_orders(
        # pylint: disable=too-many-arguments, too-many-locals
        self,
        gridpool_id: int,
        *,
        order_states: list[OrderState] | None = None,
        side: MarketSide | None = None,
        delivery_period: DeliveryPeriod | None = None,
        delivery_area: DeliveryArea | None = None,
        tag: str | None = None,
        page_size: int | None = None,
        timeout: timedelta | None = None,
    ) -> AsyncIterator[OrderDetail]:
        """
        List orders for a specific Gridpool with optional filters.

        Args:
            gridpool_id: The Gridpool to retrieve the orders for.
            order_states: List of order states to filter by.
            side: The side of the market to filter by.
            delivery_period: The delivery period to filter by.
            delivery_area: The delivery area to filter by.
            tag: The tag to filter by.
            page_size: The number of orders to return per page.
            timeout: Timeout duration, defaults to None.

        Yields:
            The list of orders for the given gridpool.

        Raises:
            grpc.RpcError: If an error occurs while listing the orders.
        """
        gridpool_order_filter = GridpoolOrderFilter(
            order_states=order_states,
            side=side,
            delivery_period=delivery_period,
            delivery_area=delivery_area,
            tag=tag,
        )

        request = electricity_trading_pb2.ListGridpoolOrdersRequest(
            gridpool_id=gridpool_id,
            filter=gridpool_order_filter.to_pb(),
            pagination_params=(
                Params(page_size=page_size, page_token="").to_proto()
                if page_size
                else None
            ),
        )
        while True:
            try:
                response = await cast(
                    Awaitable[electricity_trading_pb2.ListGridpoolOrdersResponse],
                    grpc_call_with_timeout(
                        self.stub.ListGridpoolOrders,
                        request,
                        timeout=timeout,
                    ),
                )

                for order_detail in response.order_details:
                    yield OrderDetail.from_pb(order_detail)

                if response.pagination_info.next_page_token:
                    request.pagination_params.CopyFrom(
                        PaginationParams(
                            page_token=response.pagination_info.next_page_token
                        )
                    )
                else:
                    break

            except grpc.RpcError as e:
                _logger.exception("Error occurred while listing gridpool orders: %s", e)
                raise

    async def list_gridpool_trades(
        # pylint: disable=too-many-arguments
        self,
        gridpool_id: int,
        *,
        trade_states: list[TradeState] | None = None,
        trade_ids: list[int] | None = None,
        market_side: MarketSide | None = None,
        delivery_period: DeliveryPeriod | None = None,
        delivery_area: DeliveryArea | None = None,
        page_size: int | None = None,
        timeout: timedelta | None = None,
    ) -> AsyncIterator[Trade]:
        """
        List trades for a specific Gridpool with optional filters.

        Args:
            gridpool_id: The Gridpool to retrieve the trades for.
            trade_states: List of trade states to filter by.
            trade_ids: List of trade IDs to filter by.
            market_side: The side of the market to filter by.
            delivery_period: The delivery period to filter by.
            delivery_area: The delivery area to filter by.
            page_size: The number of trades to return per page.
            timeout: Timeout duration, defaults to None.

        Yields:
            The list of trades for the given gridpool.

        Raises:
            grpc.RpcError: If an error occurs while listing gridpool trades.
        """
        gridpool_trade_filter = GridpoolTradeFilter(
            trade_states=trade_states,
            trade_ids=trade_ids,
            side=market_side,
            delivery_period=delivery_period,
            delivery_area=delivery_area,
        )

        request = electricity_trading_pb2.ListGridpoolTradesRequest(
            gridpool_id=gridpool_id,
            filter=gridpool_trade_filter.to_pb(),
            pagination_params=(
                Params(page_size=page_size, page_token="").to_proto()
                if page_size
                else None
            ),
        )

        while True:
            try:
                response = await cast(
                    Awaitable[electricity_trading_pb2.ListGridpoolTradesResponse],
                    grpc_call_with_timeout(
                        self.stub.ListGridpoolTrades,
                        request,
                        timeout=timeout,
                    ),
                )

                for trade in response.trades:
                    yield Trade.from_pb(trade)

                if response.pagination_info.next_page_token:
                    request.pagination_params.CopyFrom(
                        PaginationParams(
                            page_token=response.pagination_info.next_page_token
                        )
                    )
                else:
                    break

            except grpc.RpcError as e:
                _logger.exception("Error occurred while listing gridpool trades: %s", e)
                raise

    def receive_public_trades(
        # pylint: disable=too-many-arguments
        self,
        *,
        states: list[TradeState] | None = None,
        delivery_period: DeliveryPeriod | None = None,
        buy_delivery_area: DeliveryArea | None = None,
        sell_delivery_area: DeliveryArea | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> GrpcStreamBroadcaster[
        electricity_trading_pb2.ReceivePublicTradesStreamResponse, PublicTrade
    ]:
        """
        Stream public trades with optional filters and time range.

        Args:
            states: List of order states to filter for.
            delivery_period: Delivery period to filter for.
            buy_delivery_area: Buy delivery area to filter for.
            sell_delivery_area: Sell delivery area to filter for.
            start_time: The starting timestamp to stream trades from. If None, streams from now.
            end_time: The ending timestamp to stop streaming trades. If None, streams indefinitely.

        Returns:
            Async generator of orders.

        Raises:
            grpc.RpcError: If an error occurs while streaming public trades.
        """

        def dt_to_pb_timestamp(dt: datetime) -> Timestamp:
            ts = Timestamp()
            ts.FromDatetime(dt)
            return ts

        public_trade_filter = PublicTradeFilter(
            states=states,
            delivery_period=delivery_period,
            buy_delivery_area=buy_delivery_area,
            sell_delivery_area=sell_delivery_area,
        )

        if (
            public_trade_filter not in self._public_trades_streams
            or not self._public_trades_streams[public_trade_filter].is_running
        ):
            try:
                self._public_trades_streams[public_trade_filter] = (
                    GrpcStreamBroadcaster(
                        f"electricity-trading-{public_trade_filter}",
                        lambda: self.stub.ReceivePublicTradesStream(
                            electricity_trading_pb2.ReceivePublicTradesStreamRequest(
                                filter=public_trade_filter.to_pb(),
                                start_time=(
                                    dt_to_pb_timestamp(start_time)
                                    if start_time
                                    else None
                                ),
                                end_time=(
                                    dt_to_pb_timestamp(end_time) if end_time else None
                                ),
                            ),
                        ),
                        lambda response: PublicTrade.from_pb(response.public_trade),
                    )
                )
            except grpc.RpcError as e:
                _logger.exception("Error occurred while streaming public trades: %s", e)
                raise
        return self._public_trades_streams[public_trade_filter]

    def receive_public_order_book(
        # pylint: disable=too-many-arguments
        self,
        *,
        delivery_period: DeliveryPeriod | None = None,
        delivery_area: DeliveryArea | None = None,
        side: MarketSide | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> GrpcStreamBroadcaster[
        electricity_trading_pb2.ReceivePublicOrderBookStreamResponse, list[PublicOrder]
    ]:
        """
        Stream public orders with optional filters and time range.

        Args:
            delivery_period: Delivery period to filter for.
            delivery_area: Delivery area to filter for.
            side: Side of the market to filter for.
            start_time: The starting timestamp to stream orders from. If None, streams from now.
            end_time: The ending timestamp to stop streaming orders. If None, streams indefinitely.

        Returns:
            Async generator of orders.

        Raises:
            grpc.RpcError: If an error occurs while streaming public orders.
        """
        public_order_filter = PublicOrderBookFilter(
            delivery_period=delivery_period,
            delivery_area=delivery_area,
            side=side,
        )

        start_time_utc = dt_to_pb_timestamp_utc(start_time) if start_time else None
        end_time_utc = dt_to_pb_timestamp_utc(end_time) if end_time else None

        if (
            public_order_filter not in self._public_orders_streams
            or not self._public_orders_streams[public_order_filter].is_running
        ):
            try:
                self._public_orders_streams[public_order_filter] = (
                    GrpcStreamBroadcaster(
                        f"electricity-trading-{public_order_filter}",
                        lambda: self.stub.ReceivePublicOrderBookStream(
                            electricity_trading_pb2.ReceivePublicOrderBookStreamRequest(
                                filter=public_order_filter.to_pb(),
                                start_time=start_time_utc,
                                end_time=end_time_utc,
                            ),
                        ),
                        lambda response: [
                            PublicOrder.from_pb(public_order)
                            for public_order in response.public_order_book_records
                        ],
                    )
                )
            except grpc.RpcError as e:
                _logger.exception("Error occurred while streaming public orders: %s", e)
                raise
        return self._public_orders_streams[public_order_filter]
