# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""Tests for the type conversions used with the client."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Callable, TypeVar

import pytest
from deepdiff import DeepDiff

# pylint: disable=no-member
from frequenz.api.common.v1alpha8.grid import delivery_area_pb2, delivery_duration_pb2
from frequenz.api.common.v1alpha8.market import power_pb2, price_pb2
from frequenz.api.common.v1alpha8.types import decimal_pb2, interval_pb2
from frequenz.api.electricity_trading.v1 import electricity_trading_pb2
from google.protobuf import timestamp_pb2

from frequenz.client.electricity_trading import (
    Currency,
    DeliveryArea,
    DeliveryDuration,
    DeliveryPeriod,
    EnergyMarketCodeType,
    GridpoolOrderFilter,
    MarketActor,
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
    StateDetail,
    StateReason,
    Trade,
    TradeState,
    UpdateOrder,
)
from frequenz.client.electricity_trading._types import DeliveryTimeFilter, Interval

T = TypeVar("T")

# Set up some constants for reusability
START_TIME = datetime.fromisoformat("2023-01-01T12:00:00+00:00")
START_TIME_PB = timestamp_pb2.Timestamp(seconds=1672574400)
EXECUTION_TIME = datetime.fromisoformat("2024-01-03T10:00:00+00:00")
EXECUTION_TIME_PB = timestamp_pb2.Timestamp(seconds=1704276000)
CREATE_TIME = datetime.fromisoformat("2023-01-01T12:00:00+00:00")
CREATE_TIME_PB = timestamp_pb2.Timestamp(seconds=1672574400)
MODIFICATION_TIME = datetime.fromisoformat("2023-01-01T12:00:00+00:00")
MODIFICATION_TIME_PB = timestamp_pb2.Timestamp(seconds=1672574400)
ORDER = Order(
    delivery_area=DeliveryArea(code="XYZ", code_type=EnergyMarketCodeType.EUROPE_EIC),
    delivery_period=DeliveryPeriod(
        start=START_TIME, duration=DeliveryDuration.MINUTES_15
    ),
    type=OrderType.LIMIT,
    side=MarketSide.BUY,
    price=Price(amount=Decimal("100.00"), currency=Currency.USD),
    quantity=Power(mw=Decimal("5.00")),
)
ORDER_PB = electricity_trading_pb2.Order(
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
        currency=price_pb2.Price.Currency.CURRENCY_USD,
    ),
    quantity=power_pb2.Power(mw=decimal_pb2.Decimal(value="5.00")),
)
TRADE = Trade(
    id=1,
    order_id=2,
    side=MarketSide.BUY,
    execution_time=EXECUTION_TIME,
    delivery_area=DeliveryArea(code="XYZ", code_type=EnergyMarketCodeType.EUROPE_EIC),
    delivery_period=DeliveryPeriod(START_TIME, duration=DeliveryDuration.MINUTES_15),
    price=Price(amount=Decimal("100.00"), currency=Currency.USD),
    quantity=Power(mw=Decimal("5.00")),
    state=TradeState.ACTIVE,
)

TRADE_PB = electricity_trading_pb2.Trade(
    id=1,
    order_id=2,
    side=electricity_trading_pb2.MarketSide.MARKET_SIDE_BUY,
    execution_time=EXECUTION_TIME_PB,
    delivery_area=delivery_area_pb2.DeliveryArea(
        code="XYZ",
        code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
    ),
    delivery_period=delivery_duration_pb2.DeliveryPeriod(
        start=START_TIME_PB,
        duration=delivery_duration_pb2.DeliveryDuration.DELIVERY_DURATION_15,
    ),
    price=price_pb2.Price(
        amount=decimal_pb2.Decimal(value="100.00"),
        currency=price_pb2.Price.Currency.CURRENCY_USD,
    ),
    quantity=power_pb2.Power(mw=decimal_pb2.Decimal(value="5.00")),
    state=electricity_trading_pb2.TradeState.TRADE_STATE_ACTIVE,
)

ORDER_DETAIL = OrderDetail(
    order_id=1,
    order=ORDER,
    state_detail=StateDetail(
        state=OrderState.ACTIVE,
        state_reason=StateReason.ADD,
        market_actor=MarketActor.USER,
    ),
    open_quantity=Power(mw=Decimal("5.00")),
    filled_quantity=Power(mw=Decimal("0.00")),
    create_time=CREATE_TIME,
    modification_time=MODIFICATION_TIME,
)
ORDER_DETAIL_PB = electricity_trading_pb2.OrderDetail(
    order_id=1,
    order=ORDER_PB,
    state_detail=electricity_trading_pb2.OrderDetail.StateDetail(
        state=electricity_trading_pb2.OrderState.ORDER_STATE_ACTIVE,
        state_reason=electricity_trading_pb2.OrderDetail.StateDetail.StateReason.STATE_REASON_ADD,
        market_actor=electricity_trading_pb2.OrderDetail.StateDetail.MarketActor.MARKET_ACTOR_USER,
    ),
    open_quantity=power_pb2.Power(mw=decimal_pb2.Decimal(value="5.00")),
    filled_quantity=power_pb2.Power(mw=decimal_pb2.Decimal(value="0.00")),
    create_time=CREATE_TIME_PB,
    modification_time=MODIFICATION_TIME_PB,
)
PUBLIC_TRADE = PublicTrade(
    public_trade_id=1,
    buy_delivery_area=DeliveryArea(
        code="XYZ", code_type=EnergyMarketCodeType.EUROPE_EIC
    ),
    sell_delivery_area=DeliveryArea(
        code="ABC", code_type=EnergyMarketCodeType.EUROPE_EIC
    ),
    delivery_period=DeliveryPeriod(
        start=START_TIME, duration=DeliveryDuration.MINUTES_15
    ),
    execution_time=EXECUTION_TIME,
    price=Price(amount=Decimal("100.00"), currency=Currency.USD),
    quantity=Power(mw=Decimal("5.00")),
    state=TradeState.ACTIVE,
)
PUBLIC_TRADE_PB = electricity_trading_pb2.PublicTrade(
    id=1,
    buy_delivery_area=delivery_area_pb2.DeliveryArea(
        code="XYZ",
        code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
    ),
    sell_delivery_area=delivery_area_pb2.DeliveryArea(
        code="ABC",
        code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
    ),
    delivery_period=delivery_duration_pb2.DeliveryPeriod(
        start=START_TIME_PB,
        duration=delivery_duration_pb2.DeliveryDuration.DELIVERY_DURATION_15,
    ),
    execution_time=EXECUTION_TIME_PB,
    price=price_pb2.Price(
        amount=decimal_pb2.Decimal(value="100.00"),
        currency=price_pb2.Price.Currency.CURRENCY_USD,
    ),
    quantity=power_pb2.Power(mw=decimal_pb2.Decimal(value="5.00")),
    state=electricity_trading_pb2.TradeState.TRADE_STATE_ACTIVE,
)
PUBLIC_ORDER = PublicOrder(
    public_order_id=42,
    delivery_area=DeliveryArea(code="XYZ", code_type=EnergyMarketCodeType.EUROPE_EIC),
    delivery_period=DeliveryPeriod(
        start=START_TIME, duration=DeliveryDuration.MINUTES_15
    ),
    type=OrderType.LIMIT,
    side=MarketSide.BUY,
    price=Price(amount=Decimal("100.00"), currency=Currency.EUR),
    quantity=Power(mw=Decimal("5.00")),
    execution_option=OrderExecutionOption.AON,
    create_time=CREATE_TIME,
    update_time=MODIFICATION_TIME,
)
PUBLIC_ORDER_PB = electricity_trading_pb2.PublicOrderBookRecord(
    id=42,
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
    execution_option=electricity_trading_pb2.OrderExecutionOption.ORDER_EXECUTION_OPTION_AON,
    create_time=CREATE_TIME_PB,
    update_time=MODIFICATION_TIME_PB,
)
PUBLIC_ORDER_BOOK_FILTER = PublicOrderBookFilter(
    delivery_area=DeliveryArea(code="XYZ", code_type=EnergyMarketCodeType.EUROPE_EIC),
    delivery_period=DeliveryPeriod(
        start=START_TIME, duration=DeliveryDuration.MINUTES_15
    ),
    side=MarketSide.SELL,
)
PUBLIC_ORDER_BOOK_FILTER_PB = electricity_trading_pb2.PublicOrderBookFilter(
    delivery_area=delivery_area_pb2.DeliveryArea(
        code="XYZ",
        code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
    ),
    delivery_period=delivery_duration_pb2.DeliveryPeriod(
        start=START_TIME_PB,
        duration=delivery_duration_pb2.DeliveryDuration.DELIVERY_DURATION_15,
    ),
    side=electricity_trading_pb2.MarketSide.MARKET_SIDE_SELL,
)
GRIDPOOL_ORDER_FILTER = GridpoolOrderFilter(
    order_states=[OrderState.ACTIVE, OrderState.CANCELED],
    side=MarketSide.BUY,
    delivery_time_filter=DeliveryTimeFilter(
        time_interval=Interval(
            start_time=START_TIME, end_time=START_TIME + timedelta(minutes=15)
        ),
        duration_filters=[DeliveryDuration.MINUTES_15],
    ),
    delivery_area=DeliveryArea(code="XYZ", code_type=EnergyMarketCodeType.EUROPE_EIC),
    tag="test",
)
GRIDPOOL_ORDER_FILTER_PB = electricity_trading_pb2.GridpoolOrderFilter(
    states=[
        electricity_trading_pb2.OrderState.ORDER_STATE_ACTIVE,
        electricity_trading_pb2.OrderState.ORDER_STATE_CANCELED,
    ],
    side=electricity_trading_pb2.MarketSide.MARKET_SIDE_BUY,
    delivery_time_filter=electricity_trading_pb2.DeliveryTimeFilter(
        time_interval=interval_pb2.Interval(
            start_time=START_TIME_PB,
            end_time=timestamp_pb2.Timestamp(seconds=START_TIME_PB.seconds + 15 * 60),
        ),
        duration_filters=[delivery_duration_pb2.DeliveryDuration.DELIVERY_DURATION_15],
    ),
    delivery_area=delivery_area_pb2.DeliveryArea(
        code="XYZ",
        code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
    ),
    tag="test",
)

GRIDPOOL_ORDER_FILTER_EMPTY = GridpoolOrderFilter()
GRIDPOOL_ORDER_FILTER_EMPTY_PB = electricity_trading_pb2.GridpoolOrderFilter()

PUBLIC_TRADE_FILTER = PublicTradeFilter(
    states=[TradeState.ACTIVE, TradeState.CANCELED],
    buy_delivery_area=DeliveryArea(
        code="XYZ", code_type=EnergyMarketCodeType.EUROPE_EIC
    ),
    sell_delivery_area=None,
    delivery_period=DeliveryPeriod(
        start=START_TIME, duration=DeliveryDuration.MINUTES_15
    ),
)
PUBLIC_TRADE_FILTER_PB = electricity_trading_pb2.PublicTradeFilter(
    states=[
        electricity_trading_pb2.TradeState.TRADE_STATE_ACTIVE,
        electricity_trading_pb2.TradeState.TRADE_STATE_CANCELED,
    ],
    buy_delivery_area=delivery_area_pb2.DeliveryArea(
        code="XYZ",
        code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
    ),
    delivery_period=delivery_duration_pb2.DeliveryPeriod(
        start=START_TIME_PB,
        duration=delivery_duration_pb2.DeliveryDuration.DELIVERY_DURATION_15,
    ),
)

UPDATE_ORDER = UpdateOrder(price=Price(amount=Decimal("100.00"), currency=Currency.USD))
UPDATE_ORDER_PB = electricity_trading_pb2.UpdateGridpoolOrderRequest.UpdateOrder(
    price=price_pb2.Price(
        amount=decimal_pb2.Decimal(value="100.00"),
        currency=price_pb2.Price.Currency.CURRENCY_USD,
    )
)


def assert_conversion_to_pb(
    original: Any,
    expected_pb: T,
    assert_func: Callable[[T, T], None],
) -> None:
    """
    Test conversion from a custom type to protobuf (generic utility function).

    original: The original instance of the custom type.
    expected_pb: The expected protobuf instance.
    assert_func: Function to assert equality between two protobuf instances.
    """
    converted_pb = original.to_pb()
    assert_func(converted_pb, expected_pb)


def assert_conversion_from_pb(
    original_pb: T,
    expected: Any,
    assert_func: Callable[[Any, Any], None],
) -> None:
    """
    Test conversion from protobuf to a custom type (generic utility function).

    original_pb: The original protobuf instance.
    expected: The expected instance of the custom type.
    assert_func: Function to assert equality between two instances of the custom type.
    """
    converted = expected.from_pb(original_pb)
    assert_func(converted, expected)


def assert_equal(actual: Any, expected: Any) -> None:
    """
    Assert that two instances are equal, using DeepDiff for detailed comparison.

    actual_pb: The actual instance.
    expected_pb: The expected instance.
    """
    assert isinstance(expected, type(actual))
    diff = DeepDiff(actual, expected, ignore_order=True)
    assert not diff, f"Differences found in comparison: {diff}"


def test_currency_from_pb() -> None:
    """Test the currency conversion from protobuf to enum."""
    assert Currency.from_pb(price_pb2.Price.Currency.CURRENCY_EUR) == Currency.EUR
    assert (
        Currency.from_pb(price_pb2.Price.Currency.CURRENCY_UNSPECIFIED)
        == Currency.UNSPECIFIED
    )


def test_currency_to_pb() -> None:
    """Test the currency conversion from enum to protobuf."""
    assert Currency.EUR.to_pb() == price_pb2.Price.Currency.CURRENCY_EUR
    assert Currency.UNSPECIFIED.to_pb() == price_pb2.Price.Currency.CURRENCY_UNSPECIFIED


def test_price_to_pb() -> None:
    """Test the client price type conversions to protobuf."""
    assert_conversion_to_pb(
        original=Price(amount=Decimal("100"), currency=Currency.USD),
        expected_pb=price_pb2.Price(
            amount=decimal_pb2.Decimal(value="100"),
            currency=price_pb2.Price.Currency.CURRENCY_USD,
        ),
        assert_func=assert_equal,
    )


def test_price_from_pb() -> None:
    """Test the client price type conversions from protobuf."""
    assert_conversion_from_pb(
        original_pb=price_pb2.Price(
            amount=decimal_pb2.Decimal(value="100"),
            currency=price_pb2.Price.Currency.CURRENCY_EUR,
        ),
        expected=Price(amount=Decimal("100"), currency=Currency.EUR),
        assert_func=assert_equal,
    )


def test_price_formatting() -> None:
    """Test the client price type formatting."""
    price = Price(amount=Decimal("800"), currency=Currency.JPY)
    assert str(price) == "800 JPY"
    price = Price(amount=Decimal("-100.3"), currency=Currency.CHF)
    assert str(price) == "-100.3 CHF"
    price = Price(amount=Decimal("-103.00"), currency=Currency.USD)
    assert str(price) == "-103.00 USD"
    price = Price(amount=Decimal("400.123"), currency=Currency.EUR)
    assert str(price) == "400.123 EUR"


def test_power_to_pb() -> None:
    """Test the client power type conversions to protobuf."""
    assert_conversion_to_pb(
        original=Power(mw=Decimal("5")),
        expected_pb=power_pb2.Power(mw=decimal_pb2.Decimal(value="5")),
        assert_func=assert_equal,
    )


def test_power_from_pb() -> None:
    """Test the client power type conversions from protobuf."""
    assert_conversion_from_pb(
        original_pb=power_pb2.Power(mw=decimal_pb2.Decimal(value="5")),
        expected=Power(mw=Decimal("5")),
        assert_func=assert_equal,
    )


def test_power_formatting() -> None:
    """Test the client power type formatting."""
    power = Power(mw=Decimal("5"))
    assert str(power) == "5 MW"
    power = Power(mw=Decimal("5.1"))
    assert str(power) == "5.1 MW"
    power = Power(mw=Decimal("5.100"))
    assert str(power) == "5.100 MW"
    power = Power(mw=Decimal("-5.123"))
    assert str(power) == "-5.123 MW"


def test_delivery_duration_to_pb() -> None:
    """Test the client delivery duration type conversions to protobuf."""
    assert_conversion_to_pb(
        original=DeliveryDuration.MINUTES_15,
        expected_pb=delivery_duration_pb2.DeliveryDuration.DELIVERY_DURATION_15,
        assert_func=assert_equal,
    )


def test_delivery_duration_from_pb() -> None:
    """Test the client delivery duration type conversions from protobuf."""
    assert_conversion_from_pb(
        original_pb=delivery_duration_pb2.DeliveryDuration.DELIVERY_DURATION_15,
        expected=DeliveryDuration.MINUTES_15,
        assert_func=assert_equal,
    )


def test_delivery_period_to_pb() -> None:
    """Test the client delivery period type conversions to protobuf."""
    assert_conversion_to_pb(
        original=DeliveryPeriod(start=START_TIME, duration=DeliveryDuration.MINUTES_15),
        expected_pb=delivery_duration_pb2.DeliveryPeriod(
            start=START_TIME_PB,
            duration=delivery_duration_pb2.DeliveryDuration.DELIVERY_DURATION_15,
        ),
        assert_func=assert_equal,
    )


def test_delivery_period_from_pb() -> None:
    """Test the client delivery period type conversions from protobuf."""
    assert_conversion_from_pb(
        original_pb=delivery_duration_pb2.DeliveryPeriod(
            start=START_TIME_PB,
            duration=delivery_duration_pb2.DeliveryDuration.DELIVERY_DURATION_15,
        ),
        expected=DeliveryPeriod(start=START_TIME, duration=DeliveryDuration.MINUTES_15),
        assert_func=assert_equal,
    )


def test_invalid_duration_raises_value_error() -> None:
    """Test that an invalid duration raises a ValueError."""
    with pytest.raises(ValueError):
        DeliveryPeriod(
            start=datetime.now(timezone.utc),
            duration=DeliveryDuration.from_timedelta(timedelta(minutes=10)),
        )


def test_no_timezone_raises_value_error() -> None:
    """Test that a datetime without timezone raises a ValueError."""
    with pytest.raises(ValueError):
        DeliveryPeriod(
            start=datetime.now(),
            duration=DeliveryDuration.MINUTES_5,
        )


def test_invalid_timezone() -> None:
    """Test that non-UTC timezones are converted to UTC."""
    with pytest.raises(ValueError):
        DeliveryPeriod(
            start=datetime.now(timezone(timedelta(hours=1))),
            duration=DeliveryDuration.MINUTES_5,
        )


def test_delivery_area_to_pb() -> None:
    """Test the client delivery area type conversions to protobuf."""
    assert_conversion_to_pb(
        original=DeliveryArea(code="XYZ", code_type=EnergyMarketCodeType.EUROPE_EIC),
        expected_pb=delivery_area_pb2.DeliveryArea(
            code="XYZ",
            code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
        ),
        assert_func=assert_equal,
    )


def test_delivery_area_from_pb() -> None:
    """Test the client delivery area type conversions from protobuf."""
    assert_conversion_from_pb(
        original_pb=delivery_area_pb2.DeliveryArea(
            code="XYZ",
            code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
        ),
        expected=DeliveryArea(code="XYZ", code_type=EnergyMarketCodeType.EUROPE_EIC),
        assert_func=assert_equal,
    )


def test_order_to_pb() -> None:
    """Test the client order type conversions to protobuf."""
    assert_conversion_to_pb(
        original=ORDER,
        expected_pb=ORDER_PB,
        assert_func=assert_equal,
    )


def test_order_from_pb() -> None:
    """Test the client order type conversions from protobuf."""
    assert_conversion_from_pb(
        original_pb=ORDER_PB,
        expected=ORDER,
        assert_func=assert_equal,
    )


def test_trade_to_pb() -> None:
    """Test the client trade type conversions to protobuf."""
    assert_conversion_to_pb(
        original=TRADE,
        expected_pb=TRADE_PB,
        assert_func=assert_equal,
    )


def test_trade_from_pb() -> None:
    """Test the client trade type conversions from protobuf."""
    converted_trade = Trade.from_pb(TRADE_PB)

    assert isinstance(converted_trade, Trade)
    diff = DeepDiff(converted_trade, TRADE, ignore_order=True)
    assert not diff


def test_order_detail_to_pb() -> None:
    """Test the client order detail type conversions to protobuf."""
    assert_conversion_to_pb(
        original=ORDER_DETAIL,
        expected_pb=ORDER_DETAIL_PB,
        assert_func=assert_equal,
    )


def test_order_detail_from_pb() -> None:
    """Test the client order detail type conversion from protobuf."""
    assert_conversion_from_pb(
        original_pb=ORDER_DETAIL_PB,
        expected=ORDER_DETAIL,
        assert_func=assert_equal,
    )


def test_order_detail_from_pb_missing_fields() -> None:
    """Test the client order detail type conversion from protobuf with missing fields."""
    # Previously missing price or quantity raised an error, now it is handled gracefully.
    # Missing price
    od_pb1 = electricity_trading_pb2.OrderDetail()
    od_pb1.CopyFrom(ORDER_DETAIL_PB)
    od_pb1.order.ClearField("price")
    OrderDetail.from_pb(od_pb1)
    od_pb1.state_detail.state = electricity_trading_pb2.OrderState.ORDER_STATE_CANCELED
    OrderDetail.from_pb(od_pb1)

    # Missing quantity (same logic as above)
    od_pb2 = electricity_trading_pb2.OrderDetail()
    od_pb2.CopyFrom(ORDER_DETAIL_PB)
    od_pb2.order.ClearField("quantity")
    OrderDetail.from_pb(od_pb2)
    od_pb2.state_detail.state = electricity_trading_pb2.OrderState.ORDER_STATE_CANCELED
    OrderDetail.from_pb(od_pb2)


def test_order_detail_no_timezone_error() -> None:
    """Test that an order detail with inputs with no timezone raises a ValueError."""
    with pytest.raises(ValueError):
        OrderDetail(
            order_id=1,
            order=ORDER,
            state_detail=StateDetail(
                state=OrderState.ACTIVE,
                state_reason=StateReason.ADD,
                market_actor=MarketActor.USER,
            ),
            open_quantity=Power(mw=Decimal("5.00")),
            filled_quantity=Power(mw=Decimal("0.00")),
            create_time=datetime.now(),
            modification_time=datetime.now(),
        )


def test_order_detail_timezone_converted_to_utc() -> None:
    """Test that an order detail with inputs with non-UTC timezone is converted to UTC."""
    start = datetime.now(timezone(timedelta(hours=1)))
    order_detail = OrderDetail(
        order_id=1,
        order=ORDER,
        state_detail=StateDetail(
            state=OrderState.ACTIVE,
            state_reason=StateReason.ADD,
            market_actor=MarketActor.USER,
        ),
        open_quantity=Power(mw=Decimal("5.00")),
        filled_quantity=Power(mw=Decimal("0.00")),
        create_time=start,
        modification_time=start,
    )

    assert order_detail.create_time.tzinfo == timezone.utc
    assert order_detail.modification_time.tzinfo == timezone.utc


def test_gridpool_order_filter_to_pb() -> None:
    """Test the client gridpool order filter type conversion to protobuf."""
    assert_conversion_to_pb(
        original=GRIDPOOL_ORDER_FILTER,
        expected_pb=GRIDPOOL_ORDER_FILTER_PB,
        assert_func=assert_equal,
    )


def test_gridpool_order_filter_from_pb() -> None:
    """Test the client gridpool order filter type conversion from protobuf."""
    assert_conversion_from_pb(
        original_pb=GRIDPOOL_ORDER_FILTER_PB,
        expected=GRIDPOOL_ORDER_FILTER,
        assert_func=assert_equal,
    )


def test_gridpool_order_filter_empty_to_pb() -> None:
    """Test the client empty gridpool order filter type conversion to protobuf."""
    assert_conversion_to_pb(
        original=GRIDPOOL_ORDER_FILTER_EMPTY,
        expected_pb=GRIDPOOL_ORDER_FILTER_EMPTY_PB,
        assert_func=assert_equal,
    )


def test_gridpool_order_filter_empty_from_pb() -> None:
    """Test the client empty gridpool order filter type conversion from protobuf."""
    assert_conversion_from_pb(
        original_pb=GRIDPOOL_ORDER_FILTER_EMPTY_PB,
        expected=GRIDPOOL_ORDER_FILTER_EMPTY,
        assert_func=assert_equal,
    )


def test_public_trade_filter_to_pb() -> None:
    """Test the client public trade filter type conversion to protobuf."""
    assert_conversion_to_pb(
        original=PUBLIC_TRADE_FILTER,
        expected_pb=PUBLIC_TRADE_FILTER_PB,
        assert_func=assert_equal,
    )


def test_public_trade_filter_from_pb() -> None:
    """Test the client public trade filter type conversion from protobuf."""
    assert_conversion_from_pb(
        original_pb=PUBLIC_TRADE_FILTER_PB,
        expected=PUBLIC_TRADE_FILTER,
        assert_func=assert_equal,
    )


def test_update_order_to_pb() -> None:
    """Test the client update order type conversion to protobuf."""
    converted_update_order = UPDATE_ORDER.to_pb()

    assert isinstance(
        converted_update_order,
        electricity_trading_pb2.UpdateGridpoolOrderRequest.UpdateOrder,
    )
    diff = DeepDiff(converted_update_order, UPDATE_ORDER_PB, ignore_order=True)
    assert not diff
    # Make sure the number of fields in original and converted are the same
    assert len(converted_update_order.ListFields()) == len(UPDATE_ORDER_PB.ListFields())


def test_update_order_from_pb() -> None:
    """Test the client update order type conversion from protobuf."""
    converted_update_order = UpdateOrder.from_pb(UPDATE_ORDER_PB)

    assert isinstance(converted_update_order, UpdateOrder)
    diff = DeepDiff(converted_update_order, UPDATE_ORDER, ignore_order=True)
    assert not diff
    # Make sure the number of non-None attributes in original and converted are the same
    non_none_attrs_converted = sum(
        1 for v in vars(converted_update_order).values() if v is not None
    )
    non_none_attrs_original = sum(
        1 for v in vars(UPDATE_ORDER).values() if v is not None
    )
    assert non_none_attrs_converted == non_none_attrs_original


def test_update_order_to_pb_with_empty_values() -> None:
    """Test the client update order type conversion to protobuf with empty values."""
    original_update_order = UpdateOrder()
    converted_update_order = original_update_order.to_pb()

    # Make sure all attributes are None
    non_none_attrs = converted_update_order.ListFields()
    assert len(non_none_attrs) == 0


def test_public_order_to_pb() -> None:
    """Test the client public order type conversion to protobuf."""
    assert_conversion_to_pb(
        original=PUBLIC_ORDER,
        expected_pb=PUBLIC_ORDER_PB,
        assert_func=assert_equal,
    )


def test_public_order_from_pb() -> None:
    """Test the client public order type conversion from protobuf."""
    assert_conversion_from_pb(
        original_pb=PUBLIC_ORDER_PB,
        expected=PUBLIC_ORDER,
        assert_func=assert_equal,
    )


def test_public_order_book_filter_to_pb() -> None:
    """Test the client public order book filter type conversion to protobuf."""
    assert_conversion_to_pb(
        original=PUBLIC_ORDER_BOOK_FILTER,
        expected_pb=PUBLIC_ORDER_BOOK_FILTER_PB,
        assert_func=assert_equal,
    )


def test_public_order_book_filter_from_pb() -> None:
    """Test the client public order book filter type conversion from protobuf."""
    assert_conversion_from_pb(
        original_pb=PUBLIC_ORDER_BOOK_FILTER_PB,
        expected=PUBLIC_ORDER_BOOK_FILTER,
        assert_func=assert_equal,
    )
