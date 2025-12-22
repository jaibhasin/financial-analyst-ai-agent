"""
Unit tests for utility functions.
"""

import pytest
from utils import (
    safe_get,
    format_number,
    format_percentage,
    validate_ticker
)


def test_safe_get_simple():
    """Test safe_get with simple dictionary."""
    data = {"key": "value"}
    assert safe_get(data, "key") == "value"
    assert safe_get(data, "missing", default="default") == "default"


def test_safe_get_nested():
    """Test safe_get with nested dictionary."""
    data = {
        "user": {
            "profile": {
                "name": "John"
            }
        }
    }
    assert safe_get(data, "user", "profile", "name") == "John"
    assert safe_get(data, "user", "profile", "age", default=0) == 0


def test_format_number():
    """Test number formatting."""
    assert format_number(123.456) == "123.46"
    assert format_number(123.456, decimals=1) == "123.5"
    assert format_number(None) == "--"
    assert format_number("invalid") == "--"


def test_format_percentage():
    """Test percentage formatting."""
    assert format_percentage(0.1234) == "12.34%"
    assert format_percentage(0.1234, decimals=1) == "12.3%"
    assert format_percentage(None) == "--"
    assert format_percentage("invalid") == "--"


def test_validate_ticker():
    """Test ticker validation."""
    # Valid tickers
    assert validate_ticker("RELIANCE") == True
    assert validate_ticker("TCS") == True
    assert validate_ticker("RELIANCE.NS") == True
    assert validate_ticker("INFY.BO") == True
    
    # Invalid tickers
    assert validate_ticker("") == False
    assert validate_ticker(None) == False
    assert validate_ticker("A" * 25) == False  # Too long
    assert validate_ticker("INVALID@TICKER") == False  # Special chars
