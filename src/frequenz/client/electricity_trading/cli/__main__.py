# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""CLI tool to interact with the trading API."""

import asyncio
import os
from datetime import datetime, time, timedelta
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import click

from frequenz.client.electricity_trading.cli.day_ahead import list_day_ahead_prices
from frequenz.client.electricity_trading.cli.etrading import (
    cancel_order as run_cancel_order,
)
from frequenz.client.electricity_trading.cli.etrading import (
    create_order as run_create_order,
)
from frequenz.client.electricity_trading.cli.etrading import (
    get_gridpool_order as run_get_gridpool_order,
)
from frequenz.client.electricity_trading.cli.etrading import (
    list_gridpool_orders as run_list_gridpool_orders,
)
from frequenz.client.electricity_trading.cli.etrading import (
    list_gridpool_trades as run_list_gridpool_trades,
)
from frequenz.client.electricity_trading.cli.etrading import (
    receive_public_orders as run_receive_public_orders,
)
from frequenz.client.electricity_trading.cli.etrading import (
    receive_public_trades as run_receive_public_trades,
)

TZ = ZoneInfo("Europe/Berlin")

ORDER_CREATION_HOSTS = frozenset(
    {
        "electricity-trading-testing.api.frequenz.com",
        "electricity-trading.eu-1.testing.api.frequenz.com",
        "electricity-trading-staging.api.frequenz.com",
        "electricity-trading.eu-1.staging.api.frequenz.com",
    }
)
"""Hosts that accept order creation from the CLI."""

iso = datetime.fromisoformat

AUTH_KEY_HELP = (
    "API auth key. If neither key nor secret is given, both are read from "
    "FREQUENZ_API_KEY and FREQUENZ_API_SECRET."
)


def _resolve_credentials(
    auth_key: str | None, sign_secret: str | None
) -> tuple[str, str | None]:
    """Return the auth key and sign secret, both from the same source.

    Args:
        auth_key: The auth key given on the command line.
        sign_secret: The sign secret given on the command line.

    Returns:
        The auth key and sign secret to use.

    Raises:
        click.UsageError: If no auth key is available.
    """
    # Take the fallback as a pair so a key and secret from different sources
    # are never combined.
    if not auth_key and not sign_secret:
        auth_key = os.environ.get("FREQUENZ_API_KEY")
        sign_secret = os.environ.get("FREQUENZ_API_SECRET")

    if not auth_key:
        raise click.UsageError(
            "You must provide an API auth key using --auth_key or the "
            "FREQUENZ_API_KEY environment variable."
        )
    return auth_key, sign_secret


def midnight(days: int = 0) -> str:
    """Return today's midnight."""
    return (
        datetime.combine(datetime.now(TZ), time.min, tzinfo=TZ) + timedelta(days)
    ).isoformat()


@click.group()
def cli() -> None:
    """CLI tool to interact with the trading API."""


@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", default=None, type=str, help=AUTH_KEY_HELP)
@click.option("--delivery-start", default=None, type=iso)
@click.option("--execution-from", default=None, type=iso)
@click.option("--execution-to", default=None, type=iso)
@click.option("--sign_secret", default=None, type=str)
def receive_public_trades(  # pylint: disable=too-many-arguments
    url: str,
    auth_key: str | None,
    *,
    execution_from: datetime,
    execution_to: datetime,
    delivery_start: datetime,
    sign_secret: str | None = None,
) -> None:
    """List and/or stream public trades."""
    auth_key, sign_secret = _resolve_credentials(auth_key, sign_secret)
    asyncio.run(
        run_receive_public_trades(
            url=url,
            auth_key=auth_key,
            delivery_start=delivery_start,
            start=execution_from,
            end=execution_to,
            sign_secret=sign_secret,
        )
    )


@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", default=None, type=str, help=AUTH_KEY_HELP)
@click.option("--delivery-start", default=None, type=iso)
@click.option("--execution-from", default=None, type=iso)
@click.option("--execution-to", default=None, type=iso)
@click.option("--sign_secret", default=None, type=str)
def receive_public_orders(  # pylint: disable=too-many-arguments
    url: str,
    auth_key: str | None,
    *,
    execution_from: datetime,
    execution_to: datetime,
    delivery_start: datetime,
    sign_secret: str | None = None,
) -> None:
    """List and/or stream public orders."""
    auth_key, sign_secret = _resolve_credentials(auth_key, sign_secret)
    asyncio.run(
        run_receive_public_orders(
            url=url,
            auth_key=auth_key,
            delivery_start=delivery_start,
            start=execution_from,
            end=execution_to,
            sign_secret=sign_secret,
        )
    )


# pylint: disable=too-many-arguments
@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", default=None, type=str, help=AUTH_KEY_HELP)
@click.option("--gid", required=True, type=int)
@click.option(
    "--delivery-from",
    default=None,
    type=iso,
    help="Start timestamp (inclusive) to filter delivery start times.",
)
@click.option(
    "--delivery-to",
    default=None,
    type=iso,
    help="End timestamp (exclusive) to filter delivery start times.",
)
@click.option("--sign_secret", default=None, type=str)
def receive_gridpool_trades(
    url: str,
    auth_key: str | None,
    gid: int,
    *,
    delivery_from: datetime | None,
    delivery_to: datetime | None,
    sign_secret: str | None = None,
) -> None:
    """List and/or stream gridpool trades."""
    auth_key, sign_secret = _resolve_credentials(auth_key, sign_secret)
    asyncio.run(
        run_list_gridpool_trades(
            url=url,
            auth_key=auth_key,
            gid=gid,
            delivery_from=delivery_from,
            delivery_to=delivery_to,
            sign_secret=sign_secret,
        )
    )


# pylint: disable=too-many-arguments
@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", default=None, type=str, help=AUTH_KEY_HELP)
@click.option(
    "--delivery-from",
    default=None,
    type=iso,
    help="Start timestamp (inclusive) to filter delivery start times.",
)
@click.option(
    "--delivery-to",
    default=None,
    type=iso,
    help="End timestamp (exclusive) to filter delivery start times.",
)
@click.option("--gid", required=True, type=int)
@click.option("--tag", default=None, type=str, help="Tag to filter by.")
@click.option(
    "--order-id",
    "order_ids",
    multiple=True,
    type=int,
    help="Gridpool order ID to filter by. Can be specified multiple times.",
)
@click.option("--sign_secret", default=None, type=str)
def receive_gridpool_orders(
    url: str,
    auth_key: str | None,
    *,
    delivery_from: datetime | None,
    delivery_to: datetime | None,
    gid: int,
    tag: str | None,
    order_ids: tuple[int, ...],
    sign_secret: str | None = None,
) -> None:
    """List and/or stream gridpool orders."""
    auth_key, sign_secret = _resolve_credentials(auth_key, sign_secret)
    asyncio.run(
        run_list_gridpool_orders(
            url=url,
            auth_key=auth_key,
            delivery_from=delivery_from,
            delivery_to=delivery_to,
            gid=gid,
            tag=tag,
            order_ids=order_ids if len(order_ids) > 0 else None,
            sign_secret=sign_secret,
        )
    )


@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", default=None, type=str, help=AUTH_KEY_HELP)
@click.option("--start", required=True, type=iso)
@click.option("--gid", required=True, type=int)
@click.option("--quantity", required=True, type=str)
@click.option("--price", required=True, type=str)
@click.option("--area", required=True, type=str)
@click.option("--currency", default="EUR", type=str)
@click.option("--duration", default=900, type=int)
@click.option("--sign_secret", default=None, type=str)
@click.option("--tag", default=None, type=str)
def create_order(
    # pylint: disable=too-many-arguments
    url: str,
    auth_key: str | None,
    *,
    start: datetime,
    gid: int,
    quantity: str,
    price: str,
    area: str,
    currency: str,
    duration: int,
    sign_secret: str | None = None,
    tag: str | None = None,
) -> None:
    """Create an order.

    This is only allowed in testing and staging instances.
    """
    auth_key, sign_secret = _resolve_credentials(auth_key, sign_secret)
    # Prevent accidental order creation in production instances.
    if urlparse(url).hostname not in ORDER_CREATION_HOSTS:
        raise ValueError(
            "Creating orders is only allowed in testing or staging instances."
        )

    asyncio.run(
        run_create_order(
            url=url,
            auth_key=auth_key,
            delivery_start=start,
            gid=gid,
            quantity_mw=quantity,
            price=price,
            delivery_area=area,
            currency=currency,
            duration=timedelta(seconds=duration),
            sign_secret=sign_secret,
            tag=tag,
        )
    )


@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", default=None, type=str, help=AUTH_KEY_HELP)
@click.option("--gid", required=True, type=int)
@click.option("--order", required=True, type=int)
@click.option("--sign_secret", default=None, type=str)
def cancel_order(
    url: str, auth_key: str | None, gid: int, order: int, sign_secret: str | None = None
) -> None:
    """Cancel an order."""
    auth_key, sign_secret = _resolve_credentials(auth_key, sign_secret)
    asyncio.run(
        run_cancel_order(
            url=url,
            auth_key=auth_key,
            gridpool_id=gid,
            order_id=order,
            sign_secret=sign_secret,
        )
    )


@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", default=None, type=str, help=AUTH_KEY_HELP)
@click.option("--gid", required=True, type=int)
@click.option("--sign_secret", default=None, type=str)
def cancel_all_orders(
    url: str, auth_key: str | None, gid: int, sign_secret: str | None = None
) -> None:
    """Cancel all orders for a gridpool ID."""
    auth_key, sign_secret = _resolve_credentials(auth_key, sign_secret)
    asyncio.run(
        run_cancel_order(
            url=url,
            auth_key=auth_key,
            gridpool_id=gid,
            order_id=None,
            sign_secret=sign_secret,
        )
    )


@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", default=None, type=str, help=AUTH_KEY_HELP)
@click.option("--gid", required=True, type=int)
@click.option("--order", required=True, type=int)
@click.option("--sign_secret", default=None, type=str)
def get_gridpool_order(
    url: str, auth_key: str | None, gid: int, order: int, sign_secret: str | None = None
) -> None:
    """Get a single order for a gridpool ID."""
    auth_key, sign_secret = _resolve_credentials(auth_key, sign_secret)
    asyncio.run(
        run_get_gridpool_order(
            url=url,
            auth_key=auth_key,
            gridpool_id=gid,
            order_id=order,
            sign_secret=sign_secret,
        )
    )


@cli.command()
@click.option("--entsoe-key", required=True, type=str)
@click.option("--start", default=midnight(), type=iso)
@click.option("--end", default=midnight(days=2), type=iso)
@click.option("--country-code", type=str, default="DE_LU")
def list_day_ahead(
    entsoe_key: str, *, start: datetime, end: datetime, country_code: str
) -> None:
    """List day-ahead prices."""
    list_day_ahead_prices(
        entsoe_key=entsoe_key, start=start, end=end, country_code=country_code
    )


def main() -> None:
    """Run the main Click CLI."""
    cli()


if __name__ == "__main__":
    main()
