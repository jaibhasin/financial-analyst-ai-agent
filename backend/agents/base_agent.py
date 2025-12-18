"""
Base Agent class that all specialized agents inherit from.
Provides common LLM interface and utility methods.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import google.generativeai as genai
from config import settings


class BaseAgent(ABC):
    """
    Abstract base class for all financial analysis agents.
    
    Provides:
    - LLM integration via Gemini API
    - Common logging and error handling
    - Standard output format
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize the agent.
        
        Args:
            name: Agent name for identification
            description: Description of what this agent does
        """
        self.name = name
        self.description = description
        self._setup_llm()
    
    def _setup_llm(self):
        """Configure the Gemini LLM."""
        if settings.google_api_key:
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel(settings.model_name)
        else:
            self.model = None
            print(f"Warning: {self.name} - No API key configured, LLM features disabled")
    
    async def generate_insight(
        self,
        prompt: str,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate insights using the LLM.
        
        Args:
            prompt: The analysis prompt
            data: Optional data to include in the prompt
            
        Returns:
            LLM-generated insight text
        """
        if not self.model:
            return "LLM not configured - unable to generate insights"
        
        try:
            # Build the full prompt with data context
            full_prompt = f"""You are a {self.description}.

{prompt}

"""
            if data:
                full_prompt += f"Here is the data to analyze:\n{data}\n\n"
            
            full_prompt += "Provide a clear, concise analysis. Focus on key insights and actionable information."
            
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error generating insight: {str(e)}"
    
    @abstractmethod
    async def analyze(self, ticker: str) -> Dict[str, Any]:
        """
        Perform analysis for a given stock ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing analysis results
        """
        pass
    
    def format_output(
        self,
        data: Dict[str, Any],
        insight: str,
        confidence: float = 0.0
    ) -> Dict[str, Any]:
        """
        Format the agent's output in a standard structure.
        
        Args:
            data: Raw analysis data
            insight: LLM-generated insight
            confidence: Confidence score (0-1)
            
        Returns:
            Standardized output dictionary
        """
        return {
            "agent": self.name,
            "data": data,
            "insight": insight,
            "confidence": confidence,
            "status": "success"
        }
    
    def format_error(self, error: str) -> Dict[str, Any]:
        """Format an error response."""
        return {
            "agent": self.name,
            "data": {},
            "insight": "",
            "confidence": 0.0,
            "status": "error",
            "error": error
        }
