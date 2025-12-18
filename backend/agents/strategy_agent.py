"""
Strategy Agent - Aggregates all analysis and generates final recommendation.
This is the final agent in the pipeline that synthesizes all insights.
"""

from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent


class StrategyAgent(BaseAgent):
    """
    Agent responsible for generating final investment recommendation.
    
    Capabilities:
    - Aggregates insights from all other agents
    - Generates buy/sell/hold recommendation
    - Calculates target price range
    - Provides risk-adjusted analysis
    - Generates confidence-weighted verdict
    """
    
    def __init__(self):
        super().__init__(
            name="Investment Strategist",
            description="senior investment strategist who synthesizes market data, fundamental analysis, and technical analysis to provide actionable investment recommendations"
        )
    
    async def analyze(
        self,
        ticker: str,
        market_data: Dict[str, Any],
        fundamental_analysis: Dict[str, Any],
        technical_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate final recommendation based on all agent outputs.
        
        Args:
            ticker: Stock ticker symbol
            market_data: Output from Market Data Agent
            fundamental_analysis: Output from Fundamental Agent
            technical_analysis: Output from Technical Agent
            
        Returns:
            Final recommendation with rationale
        """
        try:
            # Extract key signals from each agent
            market_signals = self._extract_market_signals(market_data)
            fundamental_signals = self._extract_fundamental_signals(fundamental_analysis)
            technical_signals = self._extract_technical_signals(technical_analysis)
            
            # Calculate aggregate scores
            scores = self._calculate_aggregate_scores(
                fundamental_signals,
                technical_signals,
                market_signals
            )
            
            # Determine recommendation
            recommendation = self._generate_recommendation(scores)
            
            # Calculate target price
            target_price = self._calculate_target_price(
                market_data,
                fundamental_analysis,
                technical_analysis
            )
            
            # Risk assessment
            risk_assessment = self._assess_risk(
                fundamental_analysis,
                technical_analysis
            )
            
            data = {
                "scores": scores,
                "recommendation": recommendation,
                "target_price": target_price,
                "risk_assessment": risk_assessment,
                "key_factors": {
                    "bullish": self._collect_bullish_factors(fundamental_signals, technical_signals),
                    "bearish": self._collect_bearish_factors(fundamental_signals, technical_signals)
                }
            }
            
            # Generate comprehensive LLM insight
            insight = await self.generate_insight(
                prompt=f"""As a senior investment strategist, provide a comprehensive investment recommendation for {ticker}.

Based on the analysis:
- Fundamental Score: {scores['fundamental_score']}/100
- Technical Score: {scores['technical_score']}/100
- Overall Score: {scores['overall_score']}/100

Key Bullish Factors: {data['key_factors']['bullish']}
Key Bearish Factors: {data['key_factors']['bearish']}

Recommendation: {recommendation['action']}
Target Price Range: ₹{target_price['low']} - ₹{target_price['high']}
Risk Level: {risk_assessment['level']}

Provide:
1. Clear investment thesis
2. Key reasons for your recommendation
3. What would change your view
4. Suggested investment horizon
5. Position sizing advice based on risk

Be specific and actionable.""",
                data={
                    "current_price": market_data.get('data', {}).get('price_data', {}).get('current_price'),
                    "pe_ratio": fundamental_analysis.get('data', {}).get('valuation', {}).get('pe_ratio'),
                    "roe": fundamental_analysis.get('data', {}).get('profitability', {}).get('roe'),
                    "trend": technical_analysis.get('data', {}).get('trend', {}).get('overall_trend'),
                    "rsi": technical_analysis.get('data', {}).get('indicators', {}).get('rsi', {}).get('current')
                }
            )
            
            # Weighted confidence from all agents
            confidence = self._calculate_weighted_confidence(
                market_data.get('confidence', 0.5),
                fundamental_analysis.get('confidence', 0.5),
                technical_analysis.get('confidence', 0.5)
            )
            
            return self.format_output(data, insight, confidence)
            
        except Exception as e:
            return self.format_error(str(e))
    
    def _extract_market_signals(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract signals from market data."""
        market = data.get('data', {})
        price_data = market.get('price_data', {})
        valuation = market.get('valuation', {})
        week_52 = market.get('52_week', {})
        returns = market.get('returns', {})
        
        return {
            "current_price": price_data.get('current_price', 0),
            "volume_trend": "high" if price_data.get('volume', 0) > price_data.get('avg_volume', 1) else "low",
            "pe_ratio": valuation.get('pe_ratio'),
            "position_in_52w": week_52.get('position_percent', 50),
            "ytd_return": returns.get('ytd', 0),
            "momentum": "positive" if returns.get('1_month', 0) > 0 else "negative"
        }
    
    def _extract_fundamental_signals(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract signals from fundamental analysis."""
        fund = data.get('data', {})
        
        return {
            "profitability": fund.get('profitability', {}).get('assessment', 'Unknown'),
            "valuation": fund.get('valuation', {}).get('assessment', 'Unknown'),
            "financial_health": fund.get('financial_health', {}).get('assessment', 'Unknown'),
            "growth": fund.get('growth', {}).get('assessment', 'Unknown'),
            "roe": fund.get('profitability', {}).get('roe'),
            "pe_ratio": fund.get('valuation', {}).get('pe_ratio'),
            "debt_equity": fund.get('financial_health', {}).get('debt_to_equity'),
            "revenue_growth": fund.get('growth', {}).get('revenue_growth')
        }
    
    def _extract_technical_signals(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract signals from technical analysis."""
        tech = data.get('data', {})
        indicators = tech.get('indicators', {})
        signals = tech.get('signals', {})
        
        return {
            "trend": tech.get('trend', {}).get('overall_trend', 'Neutral'),
            "rsi_condition": indicators.get('rsi', {}).get('condition', 'Neutral'),
            "macd_signal": indicators.get('macd', {}).get('signal_type', 'Neutral'),
            "overall_signal": signals.get('overall_signal', 'Neutral'),
            "bullish_signals": signals.get('bullish_signals', []),
            "bearish_signals": signals.get('bearish_signals', []),
            "support": tech.get('support_resistance', {}).get('nearest_support'),
            "resistance": tech.get('support_resistance', {}).get('nearest_resistance')
        }
    
    def _calculate_aggregate_scores(
        self,
        fundamental: Dict[str, Any],
        technical: Dict[str, Any],
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate aggregate scores for each dimension."""
        # Fundamental score (0-100)
        fund_score = 50  # Base score
        
        profit_map = {"Strong": 20, "Good": 15, "Moderate": 5, "Weak": -10}
        fund_score += profit_map.get(fundamental.get('profitability'), 0)
        
        val_map = {"Undervalued (PEG < 1)": 20, "Attractively valued": 15, "Fairly valued": 5, 
                   "Premium valuation": -5, "Expensive": -15}
        fund_score += val_map.get(fundamental.get('valuation'), 0)
        
        health_map = {"Strong": 15, "Healthy": 10, "Moderate": 0, "Needs Attention": -15}
        fund_score += health_map.get(fundamental.get('financial_health'), 0)
        
        growth_map = {"High Growth": 15, "Moderate Growth": 10, "Low Growth": 0, "Declining": -15}
        fund_score += growth_map.get(fundamental.get('growth'), 0)
        
        fund_score = max(0, min(100, fund_score))
        
        # Technical score (0-100)
        tech_score = 50
        
        trend_map = {"Strong Bullish": 25, "Bullish": 15, "Neutral": 0, "Bearish": -20}
        tech_score += trend_map.get(technical.get('trend'), 0)
        
        signal_map = {"Bullish": 15, "Neutral": 0, "Bearish": -15}
        tech_score += signal_map.get(technical.get('overall_signal'), 0)
        
        # Add points for bullish signals, subtract for bearish
        tech_score += len(technical.get('bullish_signals', [])) * 3
        tech_score -= len(technical.get('bearish_signals', [])) * 3
        
        tech_score = max(0, min(100, tech_score))
        
        # Overall score (weighted average)
        overall_score = int(fund_score * 0.6 + tech_score * 0.4)
        
        return {
            "fundamental_score": fund_score,
            "technical_score": tech_score,
            "overall_score": overall_score
        }
    
    def _generate_recommendation(self, scores: Dict[str, Any]) -> Dict[str, Any]:
        """Generate buy/sell/hold recommendation."""
        overall = scores['overall_score']
        
        if overall >= 75:
            action = "Strong Buy"
            description = "Excellent fundamentals and favorable technical setup"
        elif overall >= 60:
            action = "Buy"
            description = "Good investment opportunity with positive outlook"
        elif overall >= 45:
            action = "Hold"
            description = "Maintain existing positions, wait for better entry"
        elif overall >= 30:
            action = "Reduce"
            description = "Consider reducing exposure, elevated risks"
        else:
            action = "Sell"
            description = "Unfavorable outlook, consider exiting position"
        
        return {
            "action": action,
            "description": description,
            "score": overall
        }
    
    def _calculate_target_price(
        self,
        market_data: Dict[str, Any],
        fundamental: Dict[str, Any],
        technical: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate target price range."""
        current_price = market_data.get('data', {}).get('price_data', {}).get('current_price', 0)
        
        if current_price == 0:
            return {"low": 0, "mid": 0, "high": 0, "upside_percent": 0}
        
        # Get support/resistance levels
        tech_data = technical.get('data', {})
        sr = tech_data.get('support_resistance', {})
        resistance = sr.get('nearest_resistance', current_price * 1.1)
        
        # Calculate based on PE and growth
        fund_data = fundamental.get('data', {})
        pe = fund_data.get('valuation', {}).get('pe_ratio')
        growth = fund_data.get('growth', {}).get('revenue_growth')
        
        # Simple target estimation
        if pe and growth and growth > 0:
            # PEG-based target
            fair_pe = min(pe * 1.2, 40)  # Cap at 40
            target_mid = current_price * (fair_pe / pe) if pe > 0 else current_price
        else:
            # Resistance-based target
            target_mid = resistance
        
        target_low = current_price * 0.95  # Downside case
        target_high = min(target_mid * 1.1, resistance * 1.05)
        
        upside = ((target_mid - current_price) / current_price) * 100
        
        return {
            "low": round(target_low, 2),
            "mid": round(target_mid, 2),
            "high": round(target_high, 2),
            "upside_percent": round(upside, 1)
        }
    
    def _assess_risk(
        self,
        fundamental: Dict[str, Any],
        technical: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess investment risk."""
        risk_factors = []
        risk_score = 0  # Lower is better
        
        # Fundamental risks
        fund = fundamental.get('data', {})
        
        debt = fund.get('financial_health', {}).get('debt_to_equity')
        if debt and debt > 1:
            risk_factors.append("High debt levels")
            risk_score += 20
        
        profit = fund.get('profitability', {}).get('assessment')
        if profit in ['Weak', 'Moderate']:
            risk_factors.append("Weak profitability")
            risk_score += 15
        
        growth = fund.get('growth', {}).get('assessment')
        if growth == 'Declining':
            risk_factors.append("Declining growth")
            risk_score += 15
        
        # Technical risks
        tech = technical.get('data', {})
        
        volatility = tech.get('indicators', {}).get('atr', {}).get('volatility')
        if volatility == 'High Volatility':
            risk_factors.append("High price volatility")
            risk_score += 15
        
        trend = tech.get('trend', {}).get('overall_trend')
        if trend == 'Bearish':
            risk_factors.append("Bearish price trend")
            risk_score += 20
        
        # Determine risk level
        if risk_score >= 50:
            level = "High"
        elif risk_score >= 30:
            level = "Moderate"
        else:
            level = "Low"
        
        return {
            "level": level,
            "score": risk_score,
            "factors": risk_factors
        }
    
    def _collect_bullish_factors(self, fundamental: Dict, technical: Dict) -> List[str]:
        """Collect bullish factors from all analyses."""
        factors = []
        
        if fundamental.get('profitability') in ['Strong', 'Good']:
            factors.append("Strong profitability")
        if fundamental.get('valuation') in ['Undervalued (PEG < 1)', 'Attractively valued']:
            factors.append("Attractive valuation")
        if fundamental.get('growth') in ['High Growth', 'Moderate Growth']:
            factors.append("Growing revenue")
        if fundamental.get('financial_health') in ['Strong', 'Healthy']:
            factors.append("Healthy balance sheet")
        
        factors.extend(technical.get('bullish_signals', [])[:3])
        
        return factors[:5]
    
    def _collect_bearish_factors(self, fundamental: Dict, technical: Dict) -> List[str]:
        """Collect bearish factors from all analyses."""
        factors = []
        
        if fundamental.get('profitability') == 'Weak':
            factors.append("Weak profitability")
        if fundamental.get('valuation') == 'Expensive':
            factors.append("Expensive valuation")
        if fundamental.get('growth') == 'Declining':
            factors.append("Revenue decline")
        if fundamental.get('financial_health') == 'Needs Attention':
            factors.append("Balance sheet concerns")
        
        factors.extend(technical.get('bearish_signals', [])[:3])
        
        return factors[:5]
    
    def _calculate_weighted_confidence(self, market_conf: float, fund_conf: float, tech_conf: float) -> float:
        """Calculate weighted confidence from all agents."""
        weights = [0.2, 0.5, 0.3]  # Market, Fundamental, Technical
        return round(market_conf * weights[0] + fund_conf * weights[1] + tech_conf * weights[2], 2)
