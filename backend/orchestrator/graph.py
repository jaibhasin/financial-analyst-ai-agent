"""
LangGraph Orchestrator - Coordinates multi-agent analysis pipeline.
Manages agent workflow, parallel execution, and result aggregation.
"""

import asyncio
from typing import Any, Dict, TypedDict

from agents.market_data_agent import MarketDataAgent
from agents.fundamental_agent import FundamentalAgent
from agents.technical_agent import TechnicalAgent
from agents.strategy_agent import StrategyAgent


class AnalysisState(TypedDict):
    """State object passed through the analysis pipeline."""
    ticker: str
    company_name: str
    market_data: Dict[str, Any]
    fundamental_analysis: Dict[str, Any]
    technical_analysis: Dict[str, Any]
    recommendation: Dict[str, Any]


async def run_analysis_pipeline(ticker: str) -> Dict[str, Any]:
    """
    Run the full multi-agent analysis pipeline.
    
    Pipeline flow:
    1. Market Data Agent (required first - provides base data)
    2. Fundamental & Technical Agents (run in parallel)
    3. Strategy Agent (aggregates all and generates recommendation)
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE', 'TCS')
        
    Returns:
        Complete analysis results from all agents
    """
    # Initialize agents
    market_agent = MarketDataAgent()
    fundamental_agent = FundamentalAgent()
    technical_agent = TechnicalAgent()
    strategy_agent = StrategyAgent()
    
    # Step 1: Fetch market data (required for other agents)
    print(f"[Orchestrator] Starting analysis for {ticker}")
    print(f"[Orchestrator] Step 1: Fetching market data...")
    
    market_data = await market_agent.analyze(ticker)
    
    if market_data.get("status") == "error":
        return {
            "error": f"Failed to fetch market data: {market_data.get('error')}",
            "status": "failed"
        }
    
    # Extract company name
    company_name = market_data.get("data", {}).get("basic_info", {}).get("name", ticker)
    
    # Step 2: Run fundamental and technical analysis in parallel
    print(f"[Orchestrator] Step 2: Running parallel analysis...")
    
    fundamental_task = fundamental_agent.analyze(ticker)
    technical_task = technical_agent.analyze(ticker)
    
    # Wait for both to complete
    fundamental_analysis, technical_analysis = await asyncio.gather(
        fundamental_task,
        technical_task
    )
    
    # Step 3: Generate final recommendation
    print(f"[Orchestrator] Step 3: Generating recommendation...")
    
    recommendation = await strategy_agent.analyze(
        ticker=ticker,
        market_data=market_data,
        fundamental_analysis=fundamental_analysis,
        technical_analysis=technical_analysis
    )
    
    print(f"[Orchestrator] Analysis complete for {ticker}")
    
    # Compile final result
    return {
        "ticker": ticker,
        "company_name": company_name,
        "market_data": market_data,
        "fundamental_analysis": fundamental_analysis,
        "technical_analysis": technical_analysis,
        "recommendation": recommendation,
        "status": "success"
    }


async def run_quick_analysis(ticker: str) -> Dict[str, Any]:
    """
    Run a quick analysis with just market data and key metrics.
    Faster than full pipeline, good for screening.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Quick analysis results
    """
    market_agent = MarketDataAgent()
    
    try:
        quote = await market_agent.get_quick_quote(ticker)
        company_info = await market_agent.get_company_info(ticker)
        
        return {
            "ticker": ticker,
            "quote": quote,
            "company": company_info,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }
