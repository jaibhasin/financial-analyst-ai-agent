# API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### Health Check

#### `GET /`
Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Financial Analyst",
  "version": "1.0.0"
}
```

#### `GET /health`
Returns detailed health information including LLM configuration.

**Response:**
```json
{
  "status": "healthy",
  "llm_configured": true,
  "model": "gemini-2.0-flash"
}
```

---

### Stock Quote

#### `GET /quote/{ticker}`
Get a quick quote for a single stock.

**Parameters:**
- `ticker` (path): Stock ticker symbol (e.g., RELIANCE, TCS, INFY)

**Example Request:**
```bash
curl http://localhost:8000/quote/RELIANCE
```

**Response:**
```json
{
  "ticker": "RELIANCE",
  "name": "Reliance Industries Limited",
  "price": 2456.75,
  "change": 23.50,
  "change_percent": 0.97,
  "volume": 5234567,
  "market_cap": 16500000000000
}
```

**Error Responses:**
- `400 Bad Request`: Invalid ticker format
- `404 Not Found`: Ticker not found or data unavailable

---

### Stock Analysis

#### `GET /analyze/{ticker}`
Perform comprehensive multi-agent analysis on a stock.

**Parameters:**
- `ticker` (path): Stock ticker symbol

**Example Request:**
```bash
curl http://localhost:8000/analyze/TCS
```

**Response:**
```json
{
  "ticker": "TCS",
  "name": "Tata Consultancy Services Limited",
  "market_data": {
    "agent": "Market Data Agent",
    "data": {
      "basic_info": {
        "name": "Tata Consultancy Services Limited",
        "sector": "Technology",
        "industry": "Information Technology Services",
        "exchange": "NSE"
      },
      "price_data": {
        "current_price": 3456.80,
        "previous_close": 3445.20,
        "open": 3450.00,
        "day_high": 3478.50,
        "day_low": 3442.10,
        "volume": 2345678,
        "avg_volume": 2100000
      },
      "valuation": {
        "market_cap": 12500000000000,
        "market_cap_formatted": "₹12.50L Cr",
        "pe_ratio": 28.5,
        "forward_pe": 26.3,
        "pb_ratio": 12.4
      },
      "52_week": {
        "high": 3750.00,
        "low": 3100.00,
        "position_percent": 54.8
      },
      "returns": {
        "ytd": 12.5,
        "1_month": 3.2,
        "3_month": 8.7,
        "6_month": 15.3,
        "1_year": 22.1
      },
      "historical_prices": [...]
    },
    "insight": "AI-generated market analysis...",
    "confidence": 0.85,
    "status": "success"
  },
  "fundamental_analysis": {
    "agent": "Fundamental Agent",
    "data": {
      "profitability": {
        "roe": 45.2,
        "roa": 28.5,
        "profit_margin": 19.8,
        "operating_margin": 25.3,
        "assessment": "Strong"
      },
      "valuation": {
        "pe_ratio": 28.5,
        "pb_ratio": 12.4,
        "ev_ebitda": 22.1,
        "peg_ratio": 1.8,
        "assessment": "Fair Valuation"
      },
      "financial_health": {
        "current_ratio": 2.8,
        "quick_ratio": 2.7,
        "debt_to_equity": 0.05,
        "net_debt": -50000000000,
        "assessment": "Strong"
      },
      "growth": {
        "revenue_growth": 15.2,
        "earnings_growth": 18.5,
        "assessment": "High Growth"
      }
    },
    "insight": "AI-generated fundamental analysis...",
    "confidence": 0.82,
    "status": "success"
  },
  "technical_analysis": {
    "agent": "Technical Agent",
    "data": {
      "trend": {
        "overall_trend": "Bullish",
        "short_term": {
          "direction": "Bullish",
          "change_pct": 2.5
        },
        "medium_term": {
          "direction": "Bullish"
        },
        "long_term": {
          "direction": "Bullish"
        },
        "trend_strength": 3
      },
      "indicators": {
        "rsi": {
          "current": 58.5,
          "condition": "Neutral"
        },
        "macd": {
          "signal_type": "Bullish Crossover"
        },
        "stochastic": {
          "condition": "Neutral"
        },
        "atr": {
          "volatility": "Moderate"
        },
        "moving_averages": {
          "sma_20": 3420.50,
          "sma_50": 3380.20,
          "sma_200": 3250.80,
          "price_vs_20sma": "Above",
          "price_vs_50sma": "Above",
          "price_vs_200sma": "Above"
        },
        "bollinger_bands": {
          "position": "Middle"
        }
      },
      "support_resistance": {
        "nearest_resistance": 3500.00,
        "nearest_support": 3400.00,
        "pivot_point": 3450.00
      },
      "volume": {
        "current_volume": 2345678,
        "avg_volume_20": 2100000,
        "volume_ratio": 1.12,
        "volume_trend": "Increasing",
        "price_volume_signal": "Bullish"
      },
      "signals": {
        "bullish_signals": [
          "Price above all major moving averages",
          "MACD bullish crossover",
          "Volume increasing with price"
        ],
        "bearish_signals": []
      }
    },
    "insight": "AI-generated technical analysis...",
    "confidence": 0.78,
    "status": "success"
  },
  "recommendation": {
    "agent": "Strategy Agent",
    "data": {
      "recommendation": {
        "action": "BUY"
      },
      "scores": {
        "fundamental_score": 82,
        "technical_score": 75,
        "overall_score": 79
      },
      "target_price": {
        "low": 3600,
        "high": 3850,
        "upside_percent": 8.5
      },
      "risk_assessment": {
        "level": "Moderate"
      },
      "key_factors": {
        "bullish": [
          "Strong profitability metrics",
          "Healthy balance sheet",
          "Positive technical momentum"
        ],
        "bearish": [
          "Premium valuation",
          "Market volatility"
        ]
      }
    },
    "insight": "AI-generated final recommendation...",
    "confidence": 0.80,
    "status": "success"
  },
  "generated_at": "2025-12-22T18:52:18.123456"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid ticker format
- `500 Internal Server Error`: Analysis failed

---

### Stock Comparison

#### `GET /compare?tickers={ticker1,ticker2,...}`
Compare multiple stocks side-by-side.

**Parameters:**
- `tickers` (query): Comma-separated list of ticker symbols (min: 2, max: 5)

**Example Request:**
```bash
curl "http://localhost:8000/compare?tickers=RELIANCE,TCS,INFY"
```

**Response:**
```json
{
  "tickers": ["RELIANCE", "TCS", "INFY"],
  "comparison_data": {
    "stocks": [
      {
        "ticker": "RELIANCE",
        "name": "Reliance Industries Limited",
        "price": 2456.75,
        "change": 23.50,
        "change_percent": 0.97,
        "volume": 5234567,
        "market_cap": 16500000000000
      },
      {
        "ticker": "TCS",
        "name": "Tata Consultancy Services Limited",
        "price": 3456.80,
        "change": 11.60,
        "change_percent": 0.34,
        "volume": 2345678,
        "market_cap": 12500000000000
      },
      {
        "ticker": "INFY",
        "name": "Infosys Limited",
        "price": 1567.90,
        "change": -8.30,
        "change_percent": -0.53,
        "volume": 4567890,
        "market_cap": 6500000000000
      }
    ],
    "metrics": {
      "highest_price": "TCS",
      "lowest_price": "INFY",
      "best_performer": "RELIANCE",
      "worst_performer": "INFY"
    }
  },
  "generated_at": "2025-12-22T18:52:18.123456"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid ticker format, too few/many tickers
- `404 Not Found`: No data available for any ticker
- `500 Internal Server Error`: Comparison failed

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently, there is no rate limiting implemented. This may be added in future versions.

## Authentication

No authentication is required for the current version. This is a development/demo API.

## Notes

- All ticker symbols should be for NSE (National Stock Exchange) listed companies
- The API automatically appends `.NS` suffix for NSE stocks
- Historical data is cached for 5 minutes to improve performance
- LLM-generated insights require a valid Google Gemini API key
- Analysis typically takes 10-30 seconds depending on the stock and data availability
