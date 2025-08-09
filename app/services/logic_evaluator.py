import google.generativeai as genai
from app.core.config import settings
from typing import List, Dict, Any, Optional
import json
import logging
import re
import os

logger = logging.getLogger(__name__)

class EnhancedLogicEvaluator:
    def __init__(self):
        # Check if we should use local/mock mode for fast testing (disabled for production)
        self.use_local_mode = os.getenv('USE_LOCAL_MODE', 'false').lower() == 'true'
        # Hackathon optimization: use more efficient prompting for speed
        self.hackathon_mode = os.getenv('HACKATHON_MODE', 'true').lower() == 'true'
        
        if not self.use_local_mode:
            try:
                if settings.GEMINI_API_KEY:
                    genai.configure(api_key=settings.GEMINI_API_KEY)
                    # Use the current Gemini model (gemini-pro is deprecated)
                    self.model = genai.GenerativeModel('gemini-2.0-flash')
                    logger.info("Initialized Gemini API for production mode with gemini-1.5-flash")
                else:
                    logger.warning("No Gemini API key found, falling back to local mode")
                    self.use_local_mode = True
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini API, falling back to local mode: {e}")
                self.use_local_mode = True
        
        if self.use_local_mode:
            logger.info("Using local/mock mode for fast testing")

    async def evaluate_clauses(self, query: str, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate clauses against query using structured document analysis approach
        
        This method acts as the intelligent document analysis assistant that:
        1. Reads and understands the document chunks
        2. Provides grounded answers based only on document content
        3. Returns structured JSON responses with proper citations
        """
        
        try:
            # Use local/mock mode for fast testing
            if self.use_local_mode:
                return self._evaluate_clauses_local_mode(query, clauses)
            
            # Format clauses for structured analysis
            formatted_clauses = self._format_clauses_for_analysis(clauses)
            
            # Create structured prompt for document analysis
            analysis_prompt = self._create_analysis_prompt(query, formatted_clauses)
            
            # Get LLM response with timeout
            response = self.model.generate_content(analysis_prompt)
            json_str = self._clean_json_response(response.text)
            
            # Parse and validate response
            result = json.loads(json_str)
            
            # Enhance with source information
            result = self._enhance_with_sources(result, clauses)
            
            # Validate response structure
            result = self._validate_response_structure(result, query)
            
            logger.info(f"Successfully analyzed document with confidence: {result.get('confidence')}")
            return result
            
        except Exception as e:
            logger.error(f"Document analysis failed: {str(e)}")
            return self._create_error_response(query, str(e))

    def _format_clauses_for_analysis(self, clauses: List[Dict[str, Any]]) -> str:
        """Format clauses with proper numbering and context"""
        formatted_chunks = []
        
        for i, clause in enumerate(clauses, 1):
            chunk_text = clause['text']
            metadata = clause.get('metadata', {})
            relevance = clause.get('relevance_score', 0.0)
            
            formatted_chunk = f"""
**Chunk {i}** (Relevance: {relevance:.2f})
{chunk_text}
---
"""
            formatted_chunks.append(formatted_chunk)
        
        return '\n'.join(formatted_chunks)

    def _create_analysis_prompt(self, query: str, formatted_clauses: str) -> str:
        """Create structured prompt for document analysis"""
        return f"""
You are an intelligent document analysis assistant. Your role is to analyze document chunks and answer questions based ONLY on the provided content.

**STRICT INSTRUCTIONS:**
1. Read and understand the document chunks carefully
2. Answer the question using ONLY information from the provided chunks
3. Never hallucinate or invent details not in the document
4. If information is insufficient, clearly state that
5. Provide precise citations from the chunks

**USER QUESTION:** "{query}"

**DOCUMENT CHUNKS:**
{formatted_clauses}

**ANALYSIS REQUIREMENTS:**
- Provide a direct, factual answer based only on the document content
- Identify which specific chunks support your answer
- Determine confidence level based on clarity of information
- Include relevant citations/quotes from the chunks

**RESPONSE FORMAT (JSON only):**
{{
    "question": "{query}",
    "answer": "Direct answer based only on document content",
    "source": "Specific chunk or sentence that supports the answer",
    "confidence": "High/Medium/Low",
    "decision": "approved/denied/not_applicable/insufficient_info",
    "amount": numeric_value_or_null,
    "justification": "Clear explanation referencing specific chunks",
    "supporting_chunks": ["Chunk 1", "Chunk 2"],
    "key_quotes": ["Relevant quote from document"]
}}

**IMPORTANT:** Return only valid JSON. No additional text or commentary.
"""

    def _clean_json_response(self, response_text: str) -> str:
        """Clean and extract JSON from LLM response"""
        json_str = response_text.strip()
        
        # Remove markdown formatting
        if json_str.startswith('```json'):
            json_str = json_str[7:-3]
        elif json_str.startswith('```'):
            json_str = json_str[3:-3]
        
        # Remove any trailing text after JSON
        try:
            # Find the last closing brace
            last_brace = json_str.rfind('}')
            if last_brace != -1:
                json_str = json_str[:last_brace + 1]
        except:
            pass
        
        return json_str.strip()

    def _enhance_with_sources(self, result: Dict[str, Any], clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance response with detailed source information"""
        # Add full source clauses
        result['source_clauses'] = [clause['text'] for clause in clauses[:3]]
        
        # Add metadata information
        result['source_metadata'] = [clause.get('metadata', {}) for clause in clauses[:3]]
        
        # Extract and validate amounts from text
        if 'amount' not in result or result['amount'] is None:
            amount = self._extract_amount_from_text(result.get('answer', ''))
            if amount:
                result['amount'] = amount
        
        return result

    def _extract_amount_from_text(self, text: str) -> Optional[float]:
        """Extract monetary amounts from text"""
        # Pattern for Indian currency formats
        patterns = [
            r'(?:Rs\.?\s*|INR\s*|₹\s*)(\d+(?:,\d+)*(?:\.\d{2})?)',  # Rs. 1,00,000
            r'(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:rupees|rs|inr)',       # 100000 rupees
            r'(\d+(?:,\d+)*)\s*(?:lakh|lakhs|crore|crores)'          # 5 lakh
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None

    def _validate_response_structure(self, result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Validate and ensure proper response structure"""
        # Ensure required fields
        required_fields = {
            'question': query,
            'answer': 'The document does not provide enough information to answer this question.',
            'source': 'No specific source identified',
            'confidence': 'Low',
            'decision': 'insufficient_info',
            'amount': None,
            'justification': 'Unable to determine from provided document chunks',
            'supporting_chunks': [],
            'key_quotes': []
        }
        
        for field, default_value in required_fields.items():
            if field not in result:
                result[field] = default_value
        
        # Validate confidence levels
        valid_confidence = ['High', 'Medium', 'Low']
        if result['confidence'] not in valid_confidence:
            result['confidence'] = 'Low'
        
        # Validate decision types
        valid_decisions = ['approved', 'denied', 'not_applicable', 'insufficient_info']
        if result['decision'] not in valid_decisions:
            result['decision'] = 'insufficient_info'
        
        return result

    def _create_error_response(self, query: str, error_msg: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "question": query,
            "answer": "Unable to process the document due to a technical error.",
            "source": "System error",
            "confidence": "Low",
            "decision": "error",
            "amount": None,
            "justification": f"Processing error: {error_msg}",
            "supporting_chunks": [],
            "key_quotes": [],
            "source_clauses": [],
            "source_metadata": []
        }

    async def analyze_document_chunks(self, query: str, chunks: List[str], metadata: List[Dict] = None) -> Dict[str, Any]:
        """
        Direct method for analyzing document chunks
        
        This method provides a simpler interface for document analysis
        when you already have processed chunks
        """
        # Convert chunks to clause format
        clauses = []
        for i, chunk in enumerate(chunks):
            clause_data = {
                'text': chunk,
                'relevance_score': 1.0,  # Assume high relevance
                'metadata': metadata[i] if metadata and i < len(metadata) else {},
                'clause_type': 'general',
                'key_phrases': []
            }
            clauses.append(clause_data)
        
        return await self.evaluate_clauses(query, clauses)

    def extract_key_information(self, text: str) -> Dict[str, Any]:
        """Extract key information from document text"""
        key_info = {
            'amounts': [],
            'time_periods': [],
            'percentages': [],
            'dates': [],
            'conditions': []
        }
        
        # Extract monetary amounts
        amount_pattern = r'(?:Rs\.?\s*|INR\s*|₹\s*)(\d+(?:,\d+)*(?:\.\d{2})?)'
        key_info['amounts'] = re.findall(amount_pattern, text)
        
        # Extract time periods
        time_pattern = r'(\d+)\s*(days?|months?|years?|weeks?)'
        key_info['time_periods'] = re.findall(time_pattern, text, re.IGNORECASE)
        
        # Extract percentages
        percent_pattern = r'(\d+(?:\.\d+)?)\s*%'
        key_info['percentages'] = re.findall(percent_pattern, text)
        
        # Extract conditions (basic pattern matching)
        condition_keywords = ['if', 'provided', 'subject to', 'condition', 'requirement']
        for keyword in condition_keywords:
            if keyword in text.lower():
                # Extract sentence containing the condition
                sentences = text.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        key_info['conditions'].append(sentence.strip())
        
        return key_info
    
    def _evaluate_clauses_local_mode(self, query: str, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fast local evaluation for testing without external API calls
        """
        logger.info(f"Using local mode to evaluate query: {query[:50]}...")
        
        # Extract relevant text from clauses
        relevant_text = ""
        source_pages = []
        
        for clause in clauses[:3]:  # Use top 3 most relevant clauses
            relevant_text += clause.get('content', '') + " "
            if 'metadata' in clause and 'page' in clause['metadata']:
                source_pages.append(clause['metadata']['page'])
        
        # Simple keyword-based analysis for common insurance queries
        answer = self._generate_local_answer(query, relevant_text)
        
        # Create structured response
        result = {
            "answer": answer,
            "confidence": 0.85,  # Mock confidence score
            "reasoning": "Analysis based on document content using local processing",
            "sources": {
                "pages": list(set(source_pages)),
                "chunks_analyzed": len(clauses),
                "relevant_sections": min(3, len(clauses))
            },
            "metadata": {
                "processing_mode": "local",
                "query_type": self._classify_query_type(query),
                "document_coverage": f"{min(100, len(clauses) * 10)}%"
            }
        }
        
        logger.info(f"Local evaluation completed with {result['confidence']} confidence")
        return result
    
    def _generate_local_answer(self, query: str, relevant_text: str) -> str:
        """
        Generate a simple answer based on keyword matching and text analysis
        """
        query_lower = query.lower()
        text_lower = relevant_text.lower()
        
        # Common insurance query patterns
        if any(keyword in query_lower for keyword in ['age', 'year', 'old']):
            if 'age' in text_lower or 'year' in text_lower:
                return f"Based on the document analysis, the age-related information shows: {relevant_text[:200]}..."
        
        if any(keyword in query_lower for keyword in ['surgery', 'treatment', 'medical']):
            if any(keyword in text_lower for keyword in ['surgery', 'treatment', 'medical', 'hospital']):
                return f"Regarding medical/surgery coverage: {relevant_text[:200]}..."
        
        if any(keyword in query_lower for keyword in ['policy', 'insurance', 'coverage']):
            if any(keyword in text_lower for keyword in ['policy', 'coverage', 'benefit']):
                return f"Policy information found: {relevant_text[:200]}..."
        
        if any(keyword in query_lower for keyword in ['month', 'time', 'period']):
            if any(keyword in text_lower for keyword in ['month', 'day', 'year', 'period']):
                return f"Time period information: {relevant_text[:200]}..."
        
        # Default response
        return f"Based on the document analysis: {relevant_text[:300]}..."
    
    def _classify_query_type(self, query: str) -> str:
        """
        Simple query classification for metadata
        """
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['age', 'year', 'old']):
            return "age_verification"
        elif any(keyword in query_lower for keyword in ['surgery', 'treatment', 'medical']):
            return "medical_coverage"
        elif any(keyword in query_lower for keyword in ['policy', 'insurance']):
            return "policy_inquiry"
        elif any(keyword in query_lower for keyword in ['time', 'period', 'month']):
            return "temporal_query"
        else:
            return "general_inquiry"