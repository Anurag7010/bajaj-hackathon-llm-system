import google.generativeai as genai
from app.core.config import settings
import json
import re
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class QueryParser:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Use the current Gemini model (gemini-pro is deprecated)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    async def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query to extract structured information"""
        prompt = f"""
        Analyze the following query and extract structured information:
        Query: "{query}"
        
        Extract and return JSON with:
        - "intent": main purpose (coverage_check, waiting_period, amount_calculation, etc.)
        - "keywords": important terms and phrases
        - "entities": specific items mentioned (surgeries, diseases, amounts, etc.)
        - "conditions": any conditional requirements mentioned
        - "time_references": time periods, dates, durations mentioned
        
        Return only valid JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_str = response.text.strip()
            
            # Clean JSON response
            if json_str.startswith('```json'):
                json_str = json_str[7:-3]
            elif json_str.startswith('```'):
                json_str = json_str[3:-3]
            
            parsed = json.loads(json_str)
            logger.info(f"Successfully parsed query with intent: {parsed.get('intent')}")
            return parsed
        except Exception as e:
            logger.warning(f"Query parsing failed, using fallback: {str(e)}")
            # Fallback parsing
            return {
                "intent": "general_inquiry",
                "keywords": re.findall(r'\b\w+\b', query.lower()),
                "entities": [],
                "conditions": [],
                "time_references": []
            }