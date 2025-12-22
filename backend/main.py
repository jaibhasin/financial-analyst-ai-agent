"""
AI Financial Analyst - FastAPI Backend
Multi-agent system for comprehensive stock analysis of Indian markets.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from config import settings

# Create FastAPI app
app = FastAPI(
    title="AI Financial Analyst",
    description="Multi-agent AI system for comprehensive stock analysis of Indian markets",
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response Models
class QuoteResponse(BaseModel):
    """Basic stock quote response."""
    ticker: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None


class AnalysisResponse(BaseModel):
    """Full analysis response from all agents."""
    ticker: str
    name: str
    market_data: dict
    fundamental_analysis: dict
    technical_analysis: dict
    recommendation: dict
    generated_at: str


# Health check
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Financial Analyst",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "llm_configured": bool(settings.google_api_key),
        "model": settings.model_name
    }


@app.get("/quote/{ticker}")
async def get_quote(ticker: str) -> QuoteResponse:
    """
    Get a quick quote for a stock.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE', 'TCS')
    """
    # Import here to avoid circular imports
    from agents.market_data_agent import MarketDataAgent
    from utils import validate_ticker, get_logger
    
    logger = get_logger(__name__)
    
    # Validate ticker
    if not validate_ticker(ticker):
        logger.warning(f"Invalid ticker format: {ticker}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ticker format: {ticker}. Please provide a valid stock symbol."
        )
    
    try:
        ticker_upper = ticker.upper()
        logger.info(f"Fetching quote for {ticker_upper}")
        
        agent = MarketDataAgent()
        quote = await agent.get_quick_quote(ticker_upper)
        
        logger.info(f"Successfully fetched quote for {ticker_upper}")
        return QuoteResponse(**quote)
    except ValueError as e:
        logger.error(f"Validation error for {ticker}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching quote for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch quote for {ticker}. Please verify the ticker symbol and try again."
        )


@app.get("/analyze/{ticker}")
async def analyze_stock(ticker: str) -> AnalysisResponse:
    """
    Perform full multi-agent analysis on a stock.
    
    This endpoint triggers all agents:
    1. Market Data Agent - Fetches current and historical data
    2. Fundamental Analyst - Analyzes financial health
    3. Technical Analyst - Analyzes price patterns and indicators
    4. Strategy Agent - Generates final recommendation
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE', 'TCS')
    """
    from orchestrator.graph import run_analysis_pipeline
    from datetime import datetime
    from utils import validate_ticker, get_logger
    
    logger = get_logger(__name__)
    
    # Validate ticker
    if not validate_ticker(ticker):
        logger.warning(f"Invalid ticker format for analysis: {ticker}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ticker format: {ticker}. Please provide a valid stock symbol."
        )
    
    try:
        ticker_upper = ticker.upper()
        logger.info(f"Starting full analysis for {ticker_upper}")
        
        # Run the multi-agent analysis pipeline
        result = await run_analysis_pipeline(ticker_upper)
        
        # Check if analysis failed
        if result.get("status") == "failed":
            logger.error(f"Analysis pipeline failed for {ticker_upper}: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Analysis failed')
            )
        
        logger.info(f"Successfully completed analysis for {ticker_upper}")
        
        return AnalysisResponse(
            ticker=ticker_upper,
            name=result.get("company_name", ticker_upper),
            market_data=result.get("market_data", {}),
            fundamental_analysis=result.get("fundamental_analysis", {}),
            technical_analysis=result.get("technical_analysis", {}),
            recommendation=result.get("recommendation", {}),
            generated_at=datetime.now().isoformat()
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during analysis of {ticker}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed for {ticker}. Please try again later."
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
