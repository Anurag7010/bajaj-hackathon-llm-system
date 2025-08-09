from typing import List, Dict, Any, Tuple
import re
import logging

logger = logging.getLogger(__name__)

class ClauseMatcher:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    async def find_relevant_clauses(self, parsed_query: Dict[str, Any], k: int = 5) -> List[Dict[str, Any]]:
        """Find clauses relevant to the parsed query"""
        try:
            # Create search query from parsed components
            search_terms = []
            
            if parsed_query.get('keywords'):
                search_terms.extend(parsed_query['keywords'][:10])
            
            if parsed_query.get('entities'):
                search_terms.extend(parsed_query['entities'])
            
            search_query = ' '.join(search_terms) if search_terms else "general policy information"
            
            # Search vector store
            results = self.vector_store.search(search_query, k=k)
            
            # Format results
            clauses = []
            for text, score, metadata in results:
                clauses.append({
                    'text': text,
                    'relevance_score': score,
                    'metadata': metadata,
                    'clause_type': self._classify_clause(text),
                    'key_phrases': self._extract_key_phrases(text)
                })
            
            logger.info(f"Found {len(clauses)} relevant clauses")
            return clauses
            
        except Exception as e:
            logger.error(f"Clause matching failed: {e}")
            return []

    def _classify_clause(self, text: str) -> str:
        """Classify clause type based on content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['cover', 'coverage', 'benefit']):
            return 'coverage'
        elif any(word in text_lower for word in ['waiting', 'period', 'wait']):
            return 'waiting_period'
        elif any(word in text_lower for word in ['premium', 'payment', 'due']):
            return 'premium'
        elif any(word in text_lower for word in ['exclude', 'exclusion', 'not covered']):
            return 'exclusion'
        elif any(word in text_lower for word in ['amount', 'sum', 'limit']):
            return 'amount'
        else:
            return 'general'

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from clause text"""
        phrases = []
        
        # Extract monetary amounts
        money_pattern = r'(?:Rs\.?|INR|₹)\s*[\d,]+(?:\.\d{2})?'
        phrases.extend(re.findall(money_pattern, text))
        
        # Extract time periods
        time_pattern = r'\d+\s*(?:days?|months?|years?)'
        phrases.extend(re.findall(time_pattern, text))
        
        # Extract percentages
        percent_pattern = r'\d+(?:\.\d+)?%'
        phrases.extend(re.findall(percent_pattern, text))
        
        return phrases
