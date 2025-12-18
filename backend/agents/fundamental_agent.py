"""
Fundamental Analysis Agent - Analyzes company financials and health.
Evaluates income statement, balance sheet, cash flows, and key ratios.
"""

from typing import Any, Dict, Optional
import yfinance as yf

from agents.base_agent import BaseAgent


class FundamentalAgent(BaseAgent):
    """
    Agent responsible for fundamental analysis of stocks.
    
    Capabilities:
    - Income statement analysis
    - Balance sheet health check
    - Cash flow analysis
    - Key financial ratios
    - Peer comparison insights
    """
    
    def __init__(self):
        super().__init__(
            name="Fundamental Analyst",
            description="expert financial analyst specializing in fundamental analysis, financial statements, and valuation metrics"
        )
    
    def _get_ticker_symbol(self, ticker: str) -> str:
        """Convert ticker to yfinance format for NSE."""
        ticker = ticker.upper().strip()
        if ticker.endswith('.NS') or ticker.endswith('.BO'):
            return ticker
        return f"{ticker}.NS"
    
    async def analyze(self, ticker: str) -> Dict[str, Any]:
        """
        Perform comprehensive fundamental analysis.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Fundamental analysis with key metrics and insights
        """
        try:
            symbol = self._get_ticker_symbol(ticker)
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Fetch financial statements
            income_stmt = stock.income_stmt
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            
            # Calculate key ratios and metrics
            data = {
                "profitability": self._analyze_profitability(info, income_stmt),
                "valuation": self._analyze_valuation(info),
                "financial_health": self._analyze_financial_health(info, balance_sheet),
                "growth": self._analyze_growth(info, income_stmt),
                "cash_flow": self._analyze_cash_flow(info, cash_flow),
                "dividends": self._analyze_dividends(info),
                "summary_metrics": self._get_summary_metrics(info)
            }
            
            # Generate LLM insight
            insight = await self.generate_insight(
                prompt=f"""Analyze the fundamental health of {ticker} based on the following key metrics.
                
Evaluate:
1. Is the company profitable and growing?
2. Is the valuation reasonable compared to growth?
3. Is the balance sheet healthy?
4. What are the key strengths and concerns?

Provide a clear, structured analysis suitable for an investor.""",
                data=data["summary_metrics"]
            )
            
            # Calculate confidence based on data completeness
            confidence = self._calculate_confidence(data)
            
            return self.format_output(data, insight, confidence)
            
        except Exception as e:
            return self.format_error(str(e))
    
    def _analyze_profitability(self, info: dict, income_stmt) -> Dict[str, Any]:
        """Analyze profitability metrics."""
        return {
            "gross_margin": self._safe_percent(info.get('grossMargins')),
            "operating_margin": self._safe_percent(info.get('operatingMargins')),
            "profit_margin": self._safe_percent(info.get('profitMargins')),
            "roe": self._safe_percent(info.get('returnOnEquity')),
            "roa": self._safe_percent(info.get('returnOnAssets')),
            "assessment": self._assess_profitability(info)
        }
    
    def _analyze_valuation(self, info: dict) -> Dict[str, Any]:
        """Analyze valuation metrics."""
        pe = info.get('trailingPE')
        forward_pe = info.get('forwardPE')
        peg = info.get('pegRatio')
        pb = info.get('priceToBook')
        ps = info.get('priceToSalesTrailing12Months')
        ev_ebitda = info.get('enterpriseToEbitda')
        
        return {
            "pe_ratio": round(pe, 2) if pe else None,
            "forward_pe": round(forward_pe, 2) if forward_pe else None,
            "peg_ratio": round(peg, 2) if peg else None,
            "pb_ratio": round(pb, 2) if pb else None,
            "ps_ratio": round(ps, 2) if ps else None,
            "ev_ebitda": round(ev_ebitda, 2) if ev_ebitda else None,
            "assessment": self._assess_valuation(pe, peg, pb)
        }
    
    def _analyze_financial_health(self, info: dict, balance_sheet) -> Dict[str, Any]:
        """Analyze balance sheet health."""
        current_ratio = info.get('currentRatio')
        quick_ratio = info.get('quickRatio')
        debt_equity = info.get('debtToEquity')
        
        return {
            "current_ratio": round(current_ratio, 2) if current_ratio else None,
            "quick_ratio": round(quick_ratio, 2) if quick_ratio else None,
            "debt_to_equity": round(debt_equity / 100, 2) if debt_equity else None,
            "total_debt": info.get('totalDebt'),
            "total_cash": info.get('totalCash'),
            "net_debt": self._calculate_net_debt(info),
            "assessment": self._assess_financial_health(current_ratio, debt_equity)
        }
    
    def _analyze_growth(self, info: dict, income_stmt) -> Dict[str, Any]:
        """Analyze growth metrics."""
        return {
            "revenue_growth": self._safe_percent(info.get('revenueGrowth')),
            "earnings_growth": self._safe_percent(info.get('earningsGrowth')),
            "earnings_quarterly_growth": self._safe_percent(info.get('earningsQuarterlyGrowth')),
            "revenue_per_share": info.get('revenuePerShare'),
            "assessment": self._assess_growth(info)
        }
    
    def _analyze_cash_flow(self, info: dict, cash_flow) -> Dict[str, Any]:
        """Analyze cash flow metrics."""
        operating_cf = info.get('operatingCashflow')
        free_cf = info.get('freeCashflow')
        
        return {
            "operating_cashflow": operating_cf,
            "free_cashflow": free_cf,
            "fcf_margin": self._calculate_fcf_margin(info),
            "assessment": "Positive" if free_cf and free_cf > 0 else "Needs Attention"
        }
    
    def _analyze_dividends(self, info: dict) -> Dict[str, Any]:
        """Analyze dividend metrics."""
        dividend_yield = info.get('dividendYield')
        payout_ratio = info.get('payoutRatio')
        
        return {
            "dividend_yield": self._safe_percent(dividend_yield),
            "payout_ratio": self._safe_percent(payout_ratio),
            "dividend_rate": info.get('dividendRate'),
            "ex_dividend_date": str(info.get('exDividendDate', 'N/A')),
            "is_dividend_payer": dividend_yield is not None and dividend_yield > 0
        }
    
    def _get_summary_metrics(self, info: dict) -> Dict[str, Any]:
        """Get summary of key metrics for LLM analysis."""
        return {
            "pe_ratio": round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else None,
            "pb_ratio": round(info.get('priceToBook', 0), 2) if info.get('priceToBook') else None,
            "roe": self._safe_percent(info.get('returnOnEquity')),
            "debt_to_equity": round(info.get('debtToEquity', 0) / 100, 2) if info.get('debtToEquity') else None,
            "revenue_growth": self._safe_percent(info.get('revenueGrowth')),
            "profit_margin": self._safe_percent(info.get('profitMargins')),
            "current_ratio": round(info.get('currentRatio', 0), 2) if info.get('currentRatio') else None,
            "free_cashflow": info.get('freeCashflow'),
            "dividend_yield": self._safe_percent(info.get('dividendYield'))
        }
    
    # Helper methods
    def _safe_percent(self, value: Optional[float]) -> Optional[float]:
        """Convert decimal to percentage safely."""
        if value is None:
            return None
        return round(value * 100, 2)
    
    def _calculate_net_debt(self, info: dict) -> Optional[float]:
        """Calculate net debt (total debt - cash)."""
        debt = info.get('totalDebt')
        cash = info.get('totalCash')
        if debt is not None and cash is not None:
            return debt - cash
        return None
    
    def _calculate_fcf_margin(self, info: dict) -> Optional[float]:
        """Calculate free cash flow margin."""
        fcf = info.get('freeCashflow')
        revenue = info.get('totalRevenue')
        if fcf and revenue and revenue > 0:
            return round((fcf / revenue) * 100, 2)
        return None
    
    def _assess_profitability(self, info: dict) -> str:
        """Assess overall profitability."""
        roe = info.get('returnOnEquity')
        margin = info.get('profitMargins')
        
        if roe and roe > 0.15 and margin and margin > 0.10:
            return "Strong"
        elif roe and roe > 0.10 and margin and margin > 0.05:
            return "Good"
        elif roe and roe > 0:
            return "Moderate"
        else:
            return "Weak"
    
    def _assess_valuation(self, pe, peg, pb) -> str:
        """Assess valuation."""
        if pe is None:
            return "Unable to assess"
        if pe < 0:
            return "Negative earnings"
        if peg and peg < 1:
            return "Undervalued (PEG < 1)"
        if pe < 15:
            return "Attractively valued"
        elif pe < 25:
            return "Fairly valued"
        elif pe < 40:
            return "Premium valuation"
        else:
            return "Expensive"
    
    def _assess_financial_health(self, current_ratio, debt_equity) -> str:
        """Assess financial health."""
        if current_ratio and current_ratio > 1.5 and debt_equity and debt_equity < 50:
            return "Strong"
        elif current_ratio and current_ratio > 1 and debt_equity and debt_equity < 100:
            return "Healthy"
        elif current_ratio and current_ratio > 0.8:
            return "Moderate"
        else:
            return "Needs Attention"
    
    def _assess_growth(self, info: dict) -> str:
        """Assess growth profile."""
        rev_growth = info.get('revenueGrowth')
        earn_growth = info.get('earningsGrowth')
        
        if rev_growth and rev_growth > 0.20:
            return "High Growth"
        elif rev_growth and rev_growth > 0.10:
            return "Moderate Growth"
        elif rev_growth and rev_growth > 0:
            return "Low Growth"
        elif rev_growth and rev_growth < 0:
            return "Declining"
        else:
            return "Unable to assess"
    
    def _calculate_confidence(self, data: dict) -> float:
        """Calculate confidence based on data availability."""
        required_fields = ['profitability', 'valuation', 'financial_health', 'growth']
        available = sum(1 for f in required_fields if data.get(f))
        return 0.5 + (available / len(required_fields)) * 0.4
