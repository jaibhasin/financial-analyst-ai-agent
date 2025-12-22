"""
Market Data Agent - Fetches and structures market data from Indian exchanges.
Primary data sources: yfinance (with .NS/.BO suffix for NSE/BSE)
"""

from typing import Any, Dict, Optional
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent
from config import settings
from utils import cached, market_data_cache, retry_on_failure, get_logger, safe_get

logger = get_logger(__name__)


class MarketDataAgent(BaseAgent):
    """
    Agent responsible for fetching market data from NSE/BSE.
    
    Capabilities:
    - Real-time stock quotes
    - Historical OHLCV data
    - Company information
    - Market statistics
    """
    
    def __init__(self):
        super().__init__(
            name="Market Data Agent",
            description="specialist in fetching and interpreting Indian stock market data"
        )
    
    def _get_ticker_symbol(self, ticker: str) -> str:
        """
        Convert ticker to yfinance format for NSE.
        
        Args:
            ticker: Stock symbol (e.g., 'RELIANCE')
            
        Returns:
            yfinance-compatible symbol (e.g., 'RELIANCE.NS')
        """
        ticker = ticker.upper().strip()
        # If already has exchange suffix, return as-is
        if ticker.endswith('.NS') or ticker.endswith('.BO'):
            return ticker
        # Default to NSE
        return f"{ticker}.NS"
    
    @cached(market_data_cache)
    @retry_on_failure(max_attempts=3)
    async def get_quick_quote(self, ticker: str) -> Dict[str, Any]:
        """
        Get a quick quote for display.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with current price info
        """
        symbol = self._get_ticker_symbol(ticker)
        logger.debug(f"Fetching quote for {symbol}")
        stock = yf.Ticker(symbol)
        
        try:
            info = stock.info
            
            # Validate that we got meaningful data
            if not info or len(info) < 5:
                raise ValueError(f"Insufficient data returned for {ticker}")
            
            # Handle potential missing data gracefully using safe_get
            current_price = safe_get(info, 'currentPrice', default=0) or safe_get(info, 'regularMarketPrice', default=0)
            previous_close = safe_get(info, 'previousClose', default=0) or safe_get(info, 'regularMarketPreviousClose', default=0)
            
            if current_price == 0:
                raise ValueError(f"No price data available for {ticker}")
            
            change = current_price - previous_close if previous_close else 0
            change_pct = (change / previous_close * 100) if previous_close else 0
            
            logger.info(f"Successfully fetched quote for {ticker}: ₹{current_price}")
            
            return {
                "ticker": ticker,
                "name": safe_get(info, 'longName', default=safe_get(info, 'shortName', default=ticker)),
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_pct, 2),
                "volume": safe_get(info, 'volume', default=0),
                "market_cap": safe_get(info, 'marketCap')
            }
        except ValueError as e:
            logger.error(f"Validation error for {ticker}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch quote for {ticker}: {str(e)}")
            raise Exception(f"Failed to fetch quote for {ticker}. Please verify the ticker symbol.")
    
    @cached(market_data_cache)
    @retry_on_failure(max_attempts=3)
    async def get_historical_data(
        self,
        ticker: str,
        period: str = "1y"
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            
        Returns:
            DataFrame with OHLCV data
        """
        symbol = self._get_ticker_symbol(ticker)
        logger.debug(f"Fetching {period} historical data for {symbol}")
        stock = yf.Ticker(symbol)
        
        try:
            hist = stock.history(period=period)
            
            if hist.empty:
                raise ValueError(f"No historical data available for {ticker}")
            
            logger.info(f"Fetched {len(hist)} days of historical data for {ticker}")
            return hist
        except ValueError as e:
            logger.error(f"Validation error for {ticker}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch historical data for {ticker}: {str(e)}")
            raise Exception(f"Failed to fetch historical data for {ticker}")
    
    async def get_company_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive company information.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with company details
        """
        symbol = self._get_ticker_symbol(ticker)
        stock = yf.Ticker(symbol)
        
        try:
            info = stock.info
            
            return {
                "name": info.get('longName', ticker),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "description": info.get('longBusinessSummary', '')[:500],
                "website": info.get('website', ''),
                "employees": info.get('fullTimeEmployees', 0),
                "exchange": "NSE" if symbol.endswith('.NS') else "BSE"
            }
        except Exception as e:
            return {"name": ticker, "error": str(e)}
    
    async def analyze(self, ticker: str) -> Dict[str, Any]:
        """
        Perform complete market data analysis.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Comprehensive market data analysis
        """
        try:
            symbol = self._get_ticker_symbol(ticker)
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Get historical data for analysis
            hist = await self.get_historical_data(ticker, period="1y")
            
            # Calculate key statistics
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            high_52w = info.get('fiftyTwoWeekHigh', 0)
            low_52w = info.get('fiftyTwoWeekLow', 0)
            
            # Calculate position in 52-week range
            range_52w = high_52w - low_52w if high_52w and low_52w else 0
            position_in_range = ((current_price - low_52w) / range_52w * 100) if range_52w else 50
            
            # Prepare data for analysis
            data = {
                "basic_info": {
                    "name": info.get('longName', ticker),
                    "sector": info.get('sector', 'N/A'),
                    "industry": info.get('industry', 'N/A'),
                    "exchange": "NSE"
                },
                "price_data": {
                    "current_price": current_price,
                    "previous_close": info.get('previousClose', 0),
                    "open": info.get('open', 0),
                    "day_high": info.get('dayHigh', 0),
                    "day_low": info.get('dayLow', 0),
                    "volume": info.get('volume', 0),
                    "avg_volume": info.get('averageVolume', 0)
                },
                "valuation": {
                    "market_cap": info.get('marketCap', 0),
                    "market_cap_formatted": self._format_market_cap(info.get('marketCap', 0)),
                    "enterprise_value": info.get('enterpriseValue', 0),
                    "pe_ratio": round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else None,
                    "forward_pe": round(info.get('forwardPE', 0), 2) if info.get('forwardPE') else None,
                    "pb_ratio": round(info.get('priceToBook', 0), 2) if info.get('priceToBook') else None
                },
                "52_week": {
                    "high": high_52w,
                    "low": low_52w,
                    "position_percent": round(position_in_range, 1)
                },
                "returns": {
                    "ytd": self._calculate_return(hist, 'YTD'),
                    "1_month": self._calculate_return(hist, '1M'),
                    "3_month": self._calculate_return(hist, '3M'),
                    "6_month": self._calculate_return(hist, '6M'),
                    "1_year": self._calculate_return(hist, '1Y')
                },
                "historical_prices": self._prepare_chart_data(hist)
            }
            
            # Generate LLM insight
            insight = await self.generate_insight(
                prompt=f"Analyze the market data for {ticker} and provide key observations about its current market position, valuation, and recent performance.",
                data={
                    "price": current_price,
                    "pe_ratio": data["valuation"]["pe_ratio"],
                    "52_week_position": f"{position_in_range:.1f}% of 52-week range",
                    "sector": data["basic_info"]["sector"],
                    "returns": data["returns"]
                }
            )
            
            return self.format_output(data, insight, confidence=0.85)
            
        except Exception as e:
            return self.format_error(str(e))
    
    def _format_market_cap(self, value: float) -> str:
        """Format market cap in readable format (Cr)."""
        if not value:
            return "N/A"
        cr = value / 10_000_000  # Convert to Crores
        if cr >= 100000:
            return f"₹{cr/100000:.2f}L Cr"
        elif cr >= 1000:
            return f"₹{cr/1000:.2f}K Cr"
        else:
            return f"₹{cr:.2f} Cr"
    
    def _calculate_return(self, hist: pd.DataFrame, period: str) -> Optional[float]:
        """Calculate return for a given period."""
        if hist.empty:
            return None
            
        try:
            if period == 'YTD':
                start_date = datetime(datetime.now().year, 1, 1)
                subset = hist[hist.index >= start_date.strftime('%Y-%m-%d')]
            elif period == '1M':
                subset = hist.tail(22)  # ~22 trading days
            elif period == '3M':
                subset = hist.tail(66)
            elif period == '6M':
                subset = hist.tail(132)
            elif period == '1Y':
                subset = hist
            else:
                return None
            
            if len(subset) < 2:
                return None
                
            start_price = subset['Close'].iloc[0]
            end_price = subset['Close'].iloc[-1]
            return round(((end_price - start_price) / start_price) * 100, 2)
        except:
            return None
    
    def _prepare_chart_data(self, hist: pd.DataFrame) -> list:
        """Prepare historical data for charting."""
        if hist.empty:
            return []
        
        chart_data = []
        for idx, row in hist.iterrows():
            chart_data.append({
                "date": idx.strftime('%Y-%m-%d'),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume'])
            })
        
        return chart_data
