class DocumentProcessingError(Exception):
    """Raised when document processing fails"""
    pass

class VectorStoreError(Exception):
    """Raised when vector store operations fail"""
    pass

class LLMError(Exception):
    """Raised when LLM operations fail"""
    pass

class QueryParsingError(Exception):
    """Raised when query parsing fails"""
    pass
