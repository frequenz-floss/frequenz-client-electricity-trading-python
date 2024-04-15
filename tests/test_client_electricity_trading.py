# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Tests for the frequenz.client.electricity_trading package."""


def test_package_import() -> None:
    """Test that the package can be imported."""
    # pylint: disable=import-outside-toplevel
    from frequenz.client import electricity_trading

    assert electricity_trading is not None


def test_module_import_components() -> None:
    """Test that the modules can be imported."""
    # pylint: disable=import-outside-toplevel
    from frequenz.api.electricity_trading.v1 import electricity_trading_pb2

    assert electricity_trading_pb2 is not None

    # pylint: disable=import-outside-toplevel
    from frequenz.api.electricity_trading.v1 import electricity_trading_pb2_grpc

    assert electricity_trading_pb2_grpc is not None
