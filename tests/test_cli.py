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
