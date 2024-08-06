# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Tests for the function validating the amount of decimal places."""
import unittest
from decimal import Decimal

from frequenz.client.electricity_trading._client import validate_decimal_places


class TestValidateDecimalPlaces(unittest.TestCase):
    """Test the validation of the decimal places of a decimal number."""

    def test_valid_decimal_places(self) -> None:
        """Test cases where the decimal places are within the allowed limit."""
        validate_decimal_places(Decimal("123.45"), 2, "Test Value")
        validate_decimal_places(Decimal("0.01"), 2, "Test Value")
        validate_decimal_places(Decimal("123"), 0, "Test Value")
        validate_decimal_places(Decimal("-123.45"), 2, "Test Value")
        validate_decimal_places(Decimal("0.12345"), 5, "Test Value")

    def test_exceed_decimal_places(self) -> None:
        """Test cases where the decimal places exceed the allowed limit."""
        with self.assertRaises(ValueError):
            validate_decimal_places(Decimal("123.456"), 2, "Test Value")
        with self.assertRaises(ValueError):
            validate_decimal_places(Decimal("0.0123"), 2, "Test Value")
        with self.assertRaises(ValueError):
            validate_decimal_places(Decimal("123.1"), 0, "Test Value")

    def test_invalid_inputs(self) -> None:
        """Tests for invalid input values and decimal places."""
        with self.assertRaises(ValueError):
            validate_decimal_places(Decimal("NaN"), 2, "Test Value")
        with self.assertRaises(ValueError):
            validate_decimal_places(Decimal("Infinity"), 2, "Test Value")
        with self.assertRaises(AssertionError):
            validate_decimal_places(Decimal("123.45"), -1, "Test Value")
