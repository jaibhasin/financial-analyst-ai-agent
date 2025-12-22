"""
Utility functions for the AI Financial Analyst backend.
Provides logging, caching, and retry mechanisms.
"""

import logging
import functools
from typing import Any, Callable
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Module name
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Create a TTL cache for market data (5 minutes TTL, max 100 items)
market_data_cache = TTLCache(maxsize=100, ttl=settings.cache_ttl)


def cached(cache: TTLCache):
    """
    Decorator to cache function results.
    
    Args:
        cache: TTLCache instance to use
        
    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check if result is in cache
            if cache_key in cache:
                logger = get_logger(__name__)
                logger.debug(f"Cache hit for {cache_key}")
                return cache[cache_key]
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = result
            return result
        
        return wrapper
    return decorator


def retry_on_failure(max_attempts: int = 3):
    """
    Decorator to retry function on failure with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        
    Returns:
        Decorated function with retry logic
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )


def safe_get(dictionary: dict, *keys, default=None) -> Any:
    """
    Safely get nested dictionary values.
    
    Args:
        dictionary: Dictionary to extract from
        *keys: Nested keys to traverse
        default: Default value if key not found
        
    Returns:
        Value at nested key or default
        
    Example:
        safe_get(data, 'user', 'profile', 'name', default='Unknown')
    """
    result = dictionary
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
            if result is None:
                return default
        else:
            return default
    return result if result is not None else default


def format_number(value: Any, decimals: int = 2) -> str:
    """
    Safely format a number with specified decimals.
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted string or '--' if invalid
    """
    try:
        if value is None or value == '':
            return '--'
        return f"{float(value):.{decimals}f}"
    except (ValueError, TypeError):
        return '--'


def format_percentage(value: Any, decimals: int = 2) -> str:
    """
    Safely format a percentage value.
    
    Args:
        value: Percentage value (as decimal, e.g., 0.15 for 15%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string or '--' if invalid
    """
    try:
        if value is None or value == '':
            return '--'
        return f"{float(value) * 100:.{decimals}f}%"
    except (ValueError, TypeError):
        return '--'


def validate_ticker(ticker: str) -> bool:
    """
    Validate ticker symbol format.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if valid, False otherwise
    """
    if not ticker or not isinstance(ticker, str):
        return False
    
    # Remove .NS or .BO suffix for validation
    clean_ticker = ticker.replace('.NS', '').replace('.BO', '')
    
    # Check if alphanumeric and reasonable length
    return clean_ticker.isalnum() and 1 <= len(clean_ticker) <= 20
