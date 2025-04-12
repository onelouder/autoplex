import requests
import json
import time
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class PerplexityAPIManager:
    """Manager for Perplexity API interactions
    
    Provides methods for making API calls with rate limiting, budget management,
    and response processing.
    """
    
    def __init__(self, api_key, daily_budget=5.0):
        """Initialize the Perplexity API Manager
        
        Args:
            api_key (str): Perplexity API key
            daily_budget (float, optional): Maximum daily budget for API calls. Defaults to 5.0.
        """
        self.api_key = api_key
        self.daily_budget = daily_budget
        self.daily_usage = 0
        self.request_count = 0
        self.last_reset = time.time()
        self.reset_interval = 86400  # 24 hours in seconds
    
    def check_budget(self):
        """Check if current usage is within budget, reset if needed
        
        Returns:
            bool: True if within budget, False if exceeded
        """
        current_time = time.time()
        if current_time - self.last_reset >= self.reset_interval:
            self.daily_usage = 0
            self.last_reset = current_time
            return True
        
        return self.daily_usage < self.daily_budget
    
    def query(self, query_text, model="sonar", system_message=None, max_tokens=1000):
        """Make a query to the Perplexity API
        
        Args:
            query_text (str): The search query text
            model (str, optional): Perplexity model to use. Defaults to "sonar".
            system_message (str, optional): System message to guide the response.
                Defaults to None.
            max_tokens (int, optional): Maximum tokens in response. Defaults to 1000.
        
        Returns:
            dict: API response data or error information
        """
        if not self.check_budget():
            logger.warning("Budget limit reached")
            return {"error": "Budget limit reached"}
        
        # Use default system message if none provided
        if system_message is None:
            system_message = (
                "You are a research assistant. Provide comprehensive answers with citations "
                "to reliable sources. Be factual, objective, and thorough."
            )
        
        # Prepare the API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": query_text
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.5,
            "top_p": 0.9
        }
        
        # Make the API call with retry logic
        max_retries = 3
        backoff_factor = 1.5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Making Perplexity API call: {query_text[:50]}...")
                response = requests.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.request_count += 1
                    
                    # Update estimated usage (simple estimate, adjust based on actual billing)
                    # Assuming approximately $0.01 per request for simple calculation
                    self.daily_usage += 0.01
                    
                    logger.info(f"API call successful: {self.request_count} calls made today")
                    return self._process_response(result)
                elif response.status_code == 429:
                    # Rate limit exceeded
                    logger.warning("Rate limit exceeded, backing off...")
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
                else:
                    error_info = f"API Error: {response.status_code}: {response.text}"
                    logger.error(error_info)
                    return {"error": error_info}
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                wait_time = backoff_factor ** attempt
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    return {"error": f"Max retries exceeded: {str(e)}"}
        
        return {"error": "Failed to get response after retries"}
    
    def _process_response(self, response):
        """Process and extract relevant information from API response
        
        Args:
            response (dict): Raw API response
            
        Returns:
            dict: Processed response with content and extracted citations
        """
        try:
            content = response["choices"][0]["message"]["content"]
            
            # Extract citations from content
            citations = self._extract_citations(content)
            
            return {
                "content": content,
                "citations": citations,
                "request_id": response.get("id"),
                "model": response.get("model"),
                "raw_response": response  # Include raw response for debugging
            }
        
        except (KeyError, IndexError) as e:
            logger.error(f"Error processing response: {e}")
            return {"error": f"Response processing error: {str(e)}"}
    
    def _extract_citations(self, text):
        """Extract citation references from response text
        
        Args:
            text (str): Response text containing citations
            
        Returns:
            list: Extracted citation references
        """
        # Extract citations with pattern matching
        # Perplexity tends to provide citations in [number] format
        citation_pattern = r'\[([^\]]+)\]'
        citation_matches = re.findall(citation_pattern, text)
        
        # Process and deduplicate citations
        unique_citations = []
        for citation in citation_matches:
            # Skip if citation is just a number without text
            if citation.isdigit():
                continue
            
            # Add to unique citations if not already there
            if citation not in unique_citations:
                unique_citations.append(citation)
        
        return unique_citations
    
    def get_usage_stats(self):
        """Get current API usage statistics
        
        Returns:
            dict: Usage statistics
        """
        return {
            "request_count": self.request_count,
            "daily_usage": self.daily_usage,
            "daily_budget": self.daily_budget,
            "last_reset": datetime.fromtimestamp(self.last_reset).isoformat()
        }
