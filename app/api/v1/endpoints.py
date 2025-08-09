from fastapi import APIRouter, HTTPException
from app.models import QueryRequest, QueryResponse
from app.services.document_loader import DocumentLoader
from app.services.query_parser import QueryParser
from app.services.vector_store import VectorStore
from app.services.clause_matcher import ClauseMatcher
from app.services.logic_evaluator import EnhancedLogicEvaluator
from app.services.response_builder import EnhancedResponseBuilder  
from app.core.config import settings
from app.utils.monitoring import monitor_performance
import asyncio
from typing import List
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()

# ==============================================================================
# GLOBAL INITIALIZATION
# ==============================================================================
# Initialize all services once on startup to avoid reloading models on every request.
# This is a critical optimization for performance and stability.

logger.info("Initializing services globally...")

try:
    DOC_LOADER = DocumentLoader()
    QUERY_PARSER = QueryParser()
    VECTOR_STORE = VectorStore()
    LOGIC_EVALUATOR = EnhancedLogicEvaluator()
    CLAUSE_MATCHER = ClauseMatcher(VECTOR_STORE)
    logger.info("All services initialized successfully.")
except Exception as e:
    logger.critical(f"Fatal error during global service initialization: {e}", exc_info=True)
    # In a real production scenario, you might want to prevent the app from starting.
    # For the hackathon, we'll log the error and let it proceed.
    DOC_LOADER, QUERY_PARSER, VECTOR_STORE, LOGIC_EVALUATOR, CLAUSE_MATCHER = (None, None, None, None, None)

# ==============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "Bajaj Hackathon API is running",
        "version": "1.0.0"
    }

@router.post("/run", response_model=QueryResponse)
@monitor_performance
async def process_queries(request: QueryRequest):
    """Main endpoint to process document queries"""
    start_time = time.time()
    
    try:
        logger.info(f"Processing request with {len(request.questions)} questions")

        # Check if services were initialized correctly
        if not all([DOC_LOADER, QUERY_PARSER, VECTOR_STORE, LOGIC_EVALUATOR, CLAUSE_MATCHER]):
            logger.error("One or more services failed to initialize. Cannot process request.")
            raise HTTPException(status_code=503, detail="A core service is unavailable. Please try again later.")
        
        # Download and process document
        logger.info(f"Downloading document from: {request.documents}")
        doc_content = await DOC_LOADER.download_document(request.documents)
        
        # Determine document type and extract text
        try:
            # Extract the base URL without query parameters for type detection
            base_url = request.documents.split('?')[0].lower()
            
            if base_url.endswith('.pdf'):
                logger.info(f"Processing PDF document, size: {len(doc_content)} bytes")
                text_chunks = DOC_LOADER.extract_text_from_pdf(doc_content)
                logger.info(f"Extracted {len(text_chunks) if text_chunks else 0} text chunks from PDF")
            elif base_url.endswith('.docx'):
                logger.info(f"Processing DOCX document, size: {len(doc_content)} bytes")
                text_chunks = DocumentLoader.extract_text_from_docx(doc_content)  # Keep static for DOCX
                logger.info(f"Extracted {len(text_chunks) if text_chunks else 0} text chunks from DOCX")
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported document format. Please use PDF or DOCX. Detected URL: {base_url}")
            
            if not text_chunks:
                logger.error("No text chunks extracted from document - document may be empty or corrupted")
                raise HTTPException(status_code=400, detail="No text could be extracted from the document. The document may be empty, corrupted, or contain only images.")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Document processing failed: {str(e)}")
        
        # Process text chunks
        all_chunks = []
        chunk_metadata = []
        
        logger.info("Starting text chunking process...")
        for text, page_num in text_chunks:
            chunks = DOC_LOADER.chunk_text(text, settings.MAX_CHUNK_SIZE, settings.CHUNK_OVERLAP)
            all_chunks.extend(chunks)
            chunk_metadata.extend([{'page': page_num, 'source': 'document'}] * len(chunks))
        
        logger.info(f"Created {len(all_chunks)} text chunks")
        
        # Add to vector store
        # IMPORTANT: We create a temporary, request-specific vector store for each document.
        # The global VECTOR_STORE is used as a template for its model, but not for storing data between requests.
        request_vector_store = VectorStore()
        logger.info("Adding documents to request-specific vector store...")
        request_vector_store.add_documents(all_chunks, chunk_metadata)
        logger.info("Vector store populated successfully for this request")

        # Initialize a clause matcher for this specific request
        request_clause_matcher = ClauseMatcher(request_vector_store)
        
        # Process each query
        answers = []
        
        logger.info(f"Starting to process {len(request.questions)} queries...")
        for i, query in enumerate(request.questions):
            logger.info(f"Processing query {i+1}/{len(request.questions)}: {query[:50]}...")
            
            try:
                # Parse query
                logger.info(f"Parsing query {i+1}...")
                parsed_query = await QUERY_PARSER.parse_query(query)
                logger.info(f"Query {i+1} parsed successfully")
                
                # Find relevant clauses
                logger.info(f"Finding relevant clauses for query {i+1}...")
                relevant_clauses = await request_clause_matcher.find_relevant_clauses(
                    parsed_query, k=settings.TOP_K_RESULTS
                )
                logger.info(f"Found {len(relevant_clauses) if relevant_clauses else 0} relevant clauses for query {i+1}")
                
                if not relevant_clauses:
                    logger.warning(f"No relevant clauses found for query: {query}")
                    answers.append("No relevant information found in the document for this query.")
                    continue
                
                # Evaluate clauses
                logger.info(f"Evaluating clauses for query {i+1} using Gemini API...")
                evaluation_result = await LOGIC_EVALUATOR.evaluate_clauses(query, relevant_clauses)
                logger.info(f"Gemini API evaluation completed for query {i+1}")
                
                # Extract answer
                answer = evaluation_result.get('answer', 'Unable to find relevant information')
                answers.append(answer)
                
            except Exception as e:
                logger.error(f"Error processing query '{query}': {str(e)}")
                answers.append(f"Error processing query: {str(e)}")

        processing_time = time.time() - start_time
        logger.info(f"Successfully processed all queries in {processing_time:.2f} seconds")
        
        # Return simple string answers as required by hackathon format
        return QueryResponse(answers=answers)
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Fatal error after {processing_time:.2f} seconds: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")