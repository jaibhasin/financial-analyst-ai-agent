"""
Technical Analysis Agent - Analyzes price patterns and indicators.
Uses pandas-ta for technical indicator calculations.
"""

from typing import Any, Dict, List, Optional
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

from agents.base_agent import BaseAgent


class TechnicalAgent(BaseAgent):
    """
    Agent responsible for technical analysis of stocks.
    
    Capabilities:
    - Moving averages (SMA, EMA)
    - Momentum indicators (RSI, MACD, Stochastic)
    - Volatility indicators (Bollinger Bands, ATR)
    - Trend analysis
    - Support/Resistance levels
    - Volume analysis
    """
    
    def __init__(self):
        super().__init__(
            name="Technical Analyst",
            description="expert technical analyst specializing in chart patterns, indicators, and price action analysis"
        )
    
    def _get_ticker_symbol(self, ticker: str) -> str:
        """Convert ticker to yfinance format for NSE."""
        ticker = ticker.upper().strip()
        if ticker.endswith('.NS') or ticker.endswith('.BO'):
            return ticker
        return f"{ticker}.NS"
    
    async def analyze(self, ticker: str) -> Dict[str, Any]:
        """
        Perform comprehensive technical analysis.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Technical analysis with indicators and signals
        """
        try:
            symbol = self._get_ticker_symbol(ticker)
            stock = yf.Ticker(symbol)
            
            # Get historical data (1 year for indicator calculations)
            hist = stock.history(period="1y")
            
            if hist.empty:
                return self.format_error("No historical data available")
            
            # Calculate all indicators
            indicators = self._calculate_indicators(hist)
            
            # Analyze trends
            trend_analysis = self._analyze_trend(hist, indicators)
            
            # Calculate support/resistance
            sr_levels = self._calculate_support_resistance(hist)
            
            # Volume analysis
            volume_analysis = self._analyze_volume(hist)
            
            # Generate signals
            signals = self._generate_signals(indicators, trend_analysis)
            
            data = {
                "indicators": indicators,
                "trend": trend_analysis,
                "support_resistance": sr_levels,
                "volume": volume_analysis,
                "signals": signals,
                "current_price": round(hist['Close'].iloc[-1], 2),
                "analysis_date": datetime.now().strftime('%Y-%m-%d')
            }
            
            # Generate LLM insight
            insight = await self.generate_insight(
                prompt=f"""Analyze the technical setup for {ticker} based on the following indicators and signals.

Evaluate:
1. What is the current trend?
2. Are there any bullish or bearish signals?
3. What are key support and resistance levels?
4. What is the overall technical outlook?

Provide actionable insights for a trader.""",
                data={
                    "current_price": data["current_price"],
                    "trend": trend_analysis["overall_trend"],
                    "rsi": indicators["rsi"]["current"],
                    "macd_signal": indicators["macd"]["signal_type"],
                    "above_200_sma": indicators["moving_averages"]["price_vs_200sma"],
                    "signals": signals
                }
            )
            
            # Confidence based on indicator agreement
            confidence = self._calculate_confidence(signals)
            
            return self.format_output(data, insight, confidence)
            
        except Exception as e:
            return self.format_error(str(e))
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all technical indicators."""
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        
        # Moving Averages
        sma_20 = ta.sma(close, length=20)
        sma_50 = ta.sma(close, length=50)
        sma_200 = ta.sma(close, length=200)
        ema_12 = ta.ema(close, length=12)
        ema_26 = ta.ema(close, length=26)
        
        current_price = close.iloc[-1]
        
        # RSI
        rsi = ta.rsi(close, length=14)
        current_rsi = rsi.iloc[-1] if not rsi.empty else None
        
        # MACD
        macd_result = ta.macd(close)
        if macd_result is not None and not macd_result.empty:
            macd_line = macd_result.iloc[-1, 0]
            macd_signal = macd_result.iloc[-1, 1]
            macd_hist = macd_result.iloc[-1, 2]
        else:
            macd_line, macd_signal, macd_hist = None, None, None
        
        # Bollinger Bands
        bbands = ta.bbands(close, length=20, std=2)
        if bbands is not None and not bbands.empty:
            bb_upper = bbands.iloc[-1, 0]
            bb_middle = bbands.iloc[-1, 1]
            bb_lower = bbands.iloc[-1, 2]
        else:
            bb_upper, bb_middle, bb_lower = None, None, None
        
        # Stochastic
        stoch = ta.stoch(high, low, close)
        if stoch is not None and not stoch.empty:
            stoch_k = stoch.iloc[-1, 0]
            stoch_d = stoch.iloc[-1, 1]
        else:
            stoch_k, stoch_d = None, None
        
        # ATR (Average True Range)
        atr = ta.atr(high, low, close, length=14)
        current_atr = atr.iloc[-1] if atr is not None and not atr.empty else None
        
        return {
            "moving_averages": {
                "sma_20": round(sma_20.iloc[-1], 2) if sma_20 is not None and not sma_20.empty else None,
                "sma_50": round(sma_50.iloc[-1], 2) if sma_50 is not None and not sma_50.empty else None,
                "sma_200": round(sma_200.iloc[-1], 2) if sma_200 is not None and not sma_200.empty else None,
                "ema_12": round(ema_12.iloc[-1], 2) if ema_12 is not None and not ema_12.empty else None,
                "ema_26": round(ema_26.iloc[-1], 2) if ema_26 is not None and not ema_26.empty else None,
                "price_vs_20sma": "Above" if sma_20 is not None and current_price > sma_20.iloc[-1] else "Below",
                "price_vs_50sma": "Above" if sma_50 is not None and current_price > sma_50.iloc[-1] else "Below",
                "price_vs_200sma": "Above" if sma_200 is not None and current_price > sma_200.iloc[-1] else "Below"
            },
            "rsi": {
                "current": round(current_rsi, 2) if current_rsi else None,
                "condition": self._interpret_rsi(current_rsi)
            },
            "macd": {
                "macd_line": round(macd_line, 4) if macd_line else None,
                "signal_line": round(macd_signal, 4) if macd_signal else None,
                "histogram": round(macd_hist, 4) if macd_hist else None,
                "signal_type": self._interpret_macd(macd_line, macd_signal, macd_hist)
            },
            "bollinger_bands": {
                "upper": round(bb_upper, 2) if bb_upper else None,
                "middle": round(bb_middle, 2) if bb_middle else None,
                "lower": round(bb_lower, 2) if bb_lower else None,
                "position": self._bb_position(current_price, bb_upper, bb_lower)
            },
            "stochastic": {
                "k": round(stoch_k, 2) if stoch_k else None,
                "d": round(stoch_d, 2) if stoch_d else None,
                "condition": self._interpret_stochastic(stoch_k)
            },
            "atr": {
                "value": round(current_atr, 2) if current_atr else None,
                "volatility": self._interpret_atr(current_atr, current_price)
            }
        }
    
    def _analyze_trend(self, df: pd.DataFrame, indicators: dict) -> Dict[str, Any]:
        """Analyze the overall trend."""
        close = df['Close']
        
        # Short-term trend (20 days)
        short_trend = "Bullish" if close.iloc[-1] > close.iloc[-20] else "Bearish"
        short_change = ((close.iloc[-1] - close.iloc[-20]) / close.iloc[-20]) * 100
        
        # Medium-term trend (50 days)
        if len(close) >= 50:
            medium_trend = "Bullish" if close.iloc[-1] > close.iloc[-50] else "Bearish"
            medium_change = ((close.iloc[-1] - close.iloc[-50]) / close.iloc[-50]) * 100
        else:
            medium_trend = "N/A"
            medium_change = 0
        
        # Long-term trend (200 days)
        if len(close) >= 200:
            long_trend = "Bullish" if close.iloc[-1] > close.iloc[-200] else "Bearish"
            long_change = ((close.iloc[-1] - close.iloc[-200]) / close.iloc[-200]) * 100
        else:
            long_trend = "N/A"
            long_change = 0
        
        # Overall trend based on moving averages
        ma = indicators["moving_averages"]
        bullish_signals = sum([
            ma["price_vs_20sma"] == "Above",
            ma["price_vs_50sma"] == "Above",
            ma["price_vs_200sma"] == "Above"
        ])
        
        if bullish_signals == 3:
            overall = "Strong Bullish"
        elif bullish_signals == 2:
            overall = "Bullish"
        elif bullish_signals == 1:
            overall = "Neutral"
        else:
            overall = "Bearish"
        
        return {
            "short_term": {"direction": short_trend, "change_pct": round(short_change, 2)},
            "medium_term": {"direction": medium_trend, "change_pct": round(medium_change, 2)},
            "long_term": {"direction": long_trend, "change_pct": round(long_change, 2)},
            "overall_trend": overall,
            "trend_strength": bullish_signals
        }
    
    def _calculate_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate support and resistance levels."""
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        current_price = close.iloc[-1]
        
        # Recent highs and lows (last 3 months)
        recent = df.tail(66)
        
        # Pivot points
        pivot = (high.iloc[-1] + low.iloc[-1] + close.iloc[-1]) / 3
        r1 = (2 * pivot) - low.iloc[-1]
        r2 = pivot + (high.iloc[-1] - low.iloc[-1])
        s1 = (2 * pivot) - high.iloc[-1]
        s2 = pivot - (high.iloc[-1] - low.iloc[-1])
        
        # 52-week high/low
        week_52_high = high.max()
        week_52_low = low.min()
        
        return {
            "resistance_levels": [
                {"level": round(r1, 2), "type": "R1 (Pivot)"},
                {"level": round(r2, 2), "type": "R2 (Pivot)"},
                {"level": round(week_52_high, 2), "type": "52-Week High"}
            ],
            "support_levels": [
                {"level": round(s1, 2), "type": "S1 (Pivot)"},
                {"level": round(s2, 2), "type": "S2 (Pivot)"},
                {"level": round(week_52_low, 2), "type": "52-Week Low"}
            ],
            "pivot_point": round(pivot, 2),
            "nearest_resistance": round(r1, 2),
            "nearest_support": round(s1, 2)
        }
    
    def _analyze_volume(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume patterns."""
        volume = df['Volume']
        close = df['Close']
        
        avg_volume_20 = volume.tail(20).mean()
        avg_volume_50 = volume.tail(50).mean()
        current_volume = volume.iloc[-1]
        
        # Volume trend
        volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1
        
        # Price-volume relationship
        price_change = close.iloc[-1] - close.iloc[-2]
        
        if price_change > 0 and volume_ratio > 1.2:
            pv_signal = "Bullish (Up on high volume)"
        elif price_change < 0 and volume_ratio > 1.2:
            pv_signal = "Bearish (Down on high volume)"
        elif price_change > 0 and volume_ratio < 0.8:
            pv_signal = "Weak bullish (Up on low volume)"
        elif price_change < 0 and volume_ratio < 0.8:
            pv_signal = "Potential reversal (Down on low volume)"
        else:
            pv_signal = "Neutral"
        
        return {
            "current_volume": int(current_volume),
            "avg_volume_20": int(avg_volume_20),
            "avg_volume_50": int(avg_volume_50),
            "volume_ratio": round(volume_ratio, 2),
            "volume_trend": "Above Average" if volume_ratio > 1 else "Below Average",
            "price_volume_signal": pv_signal
        }
    
    def _generate_signals(self, indicators: dict, trend: dict) -> Dict[str, Any]:
        """Generate trading signals based on indicators."""
        bullish_signals = []
        bearish_signals = []
        
        # RSI signals
        rsi = indicators["rsi"]["current"]
        if rsi and rsi < 30:
            bullish_signals.append("RSI Oversold")
        elif rsi and rsi > 70:
            bearish_signals.append("RSI Overbought")
        
        # MACD signals
        macd_signal = indicators["macd"]["signal_type"]
        if "Bullish" in macd_signal:
            bullish_signals.append(f"MACD {macd_signal}")
        elif "Bearish" in macd_signal:
            bearish_signals.append(f"MACD {macd_signal}")
        
        # Moving average signals
        ma = indicators["moving_averages"]
        if ma["price_vs_200sma"] == "Above":
            bullish_signals.append("Price above 200 SMA")
        else:
            bearish_signals.append("Price below 200 SMA")
        
        # Stochastic signals
        stoch = indicators["stochastic"]["condition"]
        if stoch == "Oversold":
            bullish_signals.append("Stochastic Oversold")
        elif stoch == "Overbought":
            bearish_signals.append("Stochastic Overbought")
        
        # Bollinger Band signals
        bb_pos = indicators["bollinger_bands"]["position"]
        if bb_pos == "Near Lower Band":
            bullish_signals.append("Price near lower Bollinger Band")
        elif bb_pos == "Near Upper Band":
            bearish_signals.append("Price near upper Bollinger Band")
        
        # Determine overall signal
        bull_count = len(bullish_signals)
        bear_count = len(bearish_signals)
        
        if bull_count > bear_count + 1:
            overall = "Bullish"
        elif bear_count > bull_count + 1:
            overall = "Bearish"
        else:
            overall = "Neutral"
        
        return {
            "bullish_signals": bullish_signals,
            "bearish_signals": bearish_signals,
            "overall_signal": overall,
            "signal_strength": abs(bull_count - bear_count)
        }
    
    # Interpretation helper methods
    def _interpret_rsi(self, rsi: Optional[float]) -> str:
        if rsi is None:
            return "N/A"
        if rsi > 70:
            return "Overbought"
        elif rsi < 30:
            return "Oversold"
        elif rsi > 50:
            return "Bullish"
        else:
            return "Bearish"
    
    def _interpret_macd(self, macd: Optional[float], signal: Optional[float], hist: Optional[float]) -> str:
        if macd is None or signal is None:
            return "N/A"
        if macd > signal and hist and hist > 0:
            return "Bullish Crossover"
        elif macd < signal and hist and hist < 0:
            return "Bearish Crossover"
        elif macd > 0:
            return "Bullish"
        else:
            return "Bearish"
    
    def _interpret_stochastic(self, stoch_k: Optional[float]) -> str:
        if stoch_k is None:
            return "N/A"
        if stoch_k > 80:
            return "Overbought"
        elif stoch_k < 20:
            return "Oversold"
        else:
            return "Neutral"
    
    def _interpret_atr(self, atr: Optional[float], price: float) -> str:
        if atr is None or price == 0:
            return "N/A"
        atr_pct = (atr / price) * 100
        if atr_pct > 3:
            return "High Volatility"
        elif atr_pct > 1.5:
            return "Moderate Volatility"
        else:
            return "Low Volatility"
    
    def _bb_position(self, price: float, upper: Optional[float], lower: Optional[float]) -> str:
        if upper is None or lower is None:
            return "N/A"
        range_size = upper - lower
        if range_size == 0:
            return "N/A"
        position = (price - lower) / range_size
        if position > 0.9:
            return "Near Upper Band"
        elif position < 0.1:
            return "Near Lower Band"
        else:
            return "Middle"
    
    def _calculate_confidence(self, signals: dict) -> float:
        """Calculate confidence based on signal agreement."""
        strength = signals.get("signal_strength", 0)
        base_confidence = 0.5
        confidence = base_confidence + min(strength * 0.1, 0.4)
        return round(confidence, 2)
