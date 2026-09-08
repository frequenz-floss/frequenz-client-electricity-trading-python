# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Tests for the electricity trading CLI."""

from typing import AsyncIterator
from unittest.mock import AsyncMock, Mock

import pytest
from click.testing import CliRunner

from frequenz.client.electricity_trading.cli import __main__ as cli_main
from frequenz.client.electricity_trading.cli import etrading


async def _empty_async_iterator() -> AsyncIterator[object]:
    """Return an empty async iterator."""
    items: tuple[object, ...] = ()
    for item in items:
        yield item


def _create_order_args(url: str) -> list[str]:
    """Build the required arguments for the create-order command."""
    return [
        "create-order",
        "--url",
        url,
        "--auth_key",
        "secret",
        "--start",
        "2026-10-01T00:00:00+00:00",
        "--gid",
        "123",
        "--quantity",
        "1.0",
        "--price",
        "50.0",
        "--area",
        "10YDE-VE-------2",
    ]


@pytest.mark.parametrize("environment", ["testing", "staging"])
def test_create_order_allows_non_production_instances(
    environment: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test creating orders in testing and staging instances."""
    create_order = AsyncMock()
    monkeypatch.setattr(cli_main, "run_create_order", create_order)
    url = f"grpc://electricity-trading-{environment}.api.frequenz.com:443?ssl=true"

    result = CliRunner().invoke(cli_main.cli, _create_order_args(url))

    assert result.exit_code == 0, result.output
    create_order.assert_awaited_once()


def test_create_order_rejects_production_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that creating orders in production remains disabled."""
    create_order = AsyncMock()
    monkeypatch.setattr(cli_main, "run_create_order", create_order)
    url = "grpc://electricity-trading.api.frequenz.com:443"

    result = CliRunner().invoke(cli_main.cli, _create_order_args(url))

    assert result.exit_code == 1
    assert isinstance(result.exception, ValueError)
    assert str(result.exception) == (
        "Creating orders is only allowed in testing or staging instances."
    )
    create_order.assert_not_awaited()


@pytest.mark.parametrize(
    "url",
    [
        "grpc://electricity-trading.api.frequenz.com:443?environment=staging",
        "grpc://staging@electricity-trading.api.frequenz.com:443",
        "grpc://electricity-trading.api.frequenz.com:443#testing",
        "grpc://electricity-trading-staging.api.frequenz.com.example.com:443",
    ],
)
def test_create_order_rejects_non_production_text_in_production_url(
    url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that non-production text outside the hostname is not accepted."""
    create_order = AsyncMock()
    monkeypatch.setattr(cli_main, "run_create_order", create_order)

    result = CliRunner().invoke(cli_main.cli, _create_order_args(url))

    assert result.exit_code == 1
    assert isinstance(result.exception, ValueError)
    create_order.assert_not_awaited()


def test_receive_gridpool_orders_tag_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test forwarding a tag filter from the CLI."""
    list_gridpool_orders = AsyncMock()
    monkeypatch.setattr(cli_main, "run_list_gridpool_orders", list_gridpool_orders)

    result = CliRunner().invoke(
        cli_main.cli,
        [
            "receive-gridpool-orders",
            "--url",
            "grpc://example.com",
            "--auth_key",
            "secret",
            "--gid",
            "123",
            "--tag",
            "portfolio-a",
        ],
    )

    assert result.exit_code == 0, result.output
    list_gridpool_orders.assert_awaited_once_with(
        url="grpc://example.com",
        auth_key="secret",
        delivery_from=None,
        delivery_to=None,
        gid=123,
        tag="portfolio-a",
        order_ids=None,
        sign_secret=None,
    )


def test_receive_gridpool_orders_order_id_filter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test forwarding order ID filters from the CLI."""
    list_gridpool_orders = AsyncMock()
    monkeypatch.setattr(cli_main, "run_list_gridpool_orders", list_gridpool_orders)

    result = CliRunner().invoke(
        cli_main.cli,
        [
            "receive-gridpool-orders",
            "--url",
            "grpc://example.com",
            "--auth_key",
            "secret",
            "--gid",
            "123",
            "--order-id",
            "41",
            "--order-id",
            "42",
        ],
    )

    assert result.exit_code == 0, result.output
    list_gridpool_orders.assert_awaited_once_with(
        url="grpc://example.com",
        auth_key="secret",
        delivery_from=None,
        delivery_to=None,
        gid=123,
        tag=None,
        order_ids=(41, 42),
        sign_secret=None,
    )


async def test_list_gridpool_orders_applies_tag_to_list_and_stream(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test applying the same tag filter to historical and live results."""
    client = Mock()
    client.list_gridpool_orders.return_value = _empty_async_iterator()
    stream = Mock()
    stream.new_receiver.return_value = _empty_async_iterator()
    client.gridpool_orders_stream.return_value = stream
    monkeypatch.setattr(etrading, "Client", Mock(return_value=client))

    await etrading.list_gridpool_orders(
        url="grpc://example.com",
        auth_key="secret",
        delivery_from=None,
        delivery_to=None,
        gid=123,
        tag="portfolio-a",
    )

    list_call = client.list_gridpool_orders.call_args
    stream_call = client.gridpool_orders_stream.call_args
    assert list_call.args == (123,)
    assert stream_call.args == (123,)
    assert list_call.kwargs == stream_call.kwargs
    assert list_call.kwargs["tag"] == "portfolio-a"


async def test_list_gridpool_orders_applies_order_ids_to_list_and_stream(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test applying order ID filters to historical and live results."""
    client = Mock()
    client.list_gridpool_orders.return_value = _empty_async_iterator()
    stream = Mock()
    stream.new_receiver.return_value = _empty_async_iterator()
    client.gridpool_orders_stream.return_value = stream
    monkeypatch.setattr(etrading, "Client", Mock(return_value=client))

    await etrading.list_gridpool_orders(
        url="grpc://example.com",
        auth_key="secret",
        delivery_from=None,
        delivery_to=None,
        gid=123,
        order_ids=(41, 42),
    )

    list_call = client.list_gridpool_orders.call_args
    stream_call = client.gridpool_orders_stream.call_args
    assert list_call.args == (123,)
    assert stream_call.args == (123,)
    assert list_call.kwargs == stream_call.kwargs
    assert list_call.kwargs["order_ids"] == (41, 42)
