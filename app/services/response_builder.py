from typing import List, Dict, Any
from app.models import QueryResponse, DetailedResponse

class EnhancedResponseBuilder:
    @staticmethod
    def build_simple_response(answers: List[str]) -> QueryResponse:
        """Build simple response with just answers"""
        return QueryResponse(answers=answers)

    @staticmethod
    def build_detailed_response(evaluation_result: Dict[str, Any]) -> DetailedResponse:
        """Build detailed response with enhanced decision logic"""
        return DetailedResponse(
            decision=evaluation_result.get('decision'),
            amount=evaluation_result.get('amount'),
            justification=evaluation_result.get('justification', ''),
            confidence=evaluation_result.get('confidence', 0.0),
            source_clauses=evaluation_result.get('source_clauses', [])
        )

    @staticmethod
    def build_structured_response(evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Build structured response maintaining all analysis details"""
        return {
            "question": evaluation_result.get('question', ''),
            "answer": evaluation_result.get('answer', ''),
            "source": evaluation_result.get('source', ''),
            "confidence": evaluation_result.get('confidence', 'Low'),
            "decision": evaluation_result.get('decision', 'insufficient_info'),
            "amount": evaluation_result.get('amount'),
            "justification": evaluation_result.get('justification', ''),
            "supporting_chunks": evaluation_result.get('supporting_chunks', []),
            "key_quotes": evaluation_result.get('key_quotes', []),
            "metadata": {
                "source_clauses": evaluation_result.get('source_clauses', []),
                "source_metadata": evaluation_result.get('source_metadata', []),
                "processing_info": {
                    "total_chunks_analyzed": len(evaluation_result.get('source_clauses', [])),
                    "analysis_method": "enhanced_logic_evaluator"
                }
            }
        }
