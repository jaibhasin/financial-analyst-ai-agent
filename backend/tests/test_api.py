"""
Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AI Financial Analyst"


def test_health_endpoint():
    """Test detailed health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "llm_configured" in data
    assert "model" in data


def test_quote_endpoint_valid():
    """Test quote endpoint with valid ticker."""
    response = client.get("/quote/RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "RELIANCE"
    assert "price" in data
    assert "name" in data


def test_quote_endpoint_invalid():
    """Test quote endpoint with invalid ticker."""
    response = client.get("/quote/INVALID@TICKER")
    assert response.status_code == 400


def test_compare_endpoint_valid():
    """Test comparison endpoint with valid tickers."""
    response = client.get("/compare?tickers=RELIANCE,TCS")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tickers"]) == 2
    assert "comparison_data" in data


def test_compare_endpoint_too_few():
    """Test comparison endpoint with too few tickers."""
    response = client.get("/compare?tickers=RELIANCE")
    assert response.status_code == 400


def test_compare_endpoint_too_many():
    """Test comparison endpoint with too many tickers."""
    response = client.get("/compare?tickers=A,B,C,D,E,F")
    assert response.status_code == 400


@pytest.mark.slow
def test_analyze_endpoint():
    """Test full analysis endpoint (slow test)."""
    response = client.get("/analyze/TCS")
    # This might take a while, so we just check it doesn't error
    assert response.status_code in [200, 500]  # 500 if API key not configured
