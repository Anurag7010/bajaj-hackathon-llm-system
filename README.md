# Bajaj Hackathon 2025 - Intelligent Document Query System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Project Overview

This project is an intelligent document analysis system built for the **Bajaj Hackathon 2025**. It processes PDF and DOCX files and answers user queries by combining document retrieval with large language model (LLM) reasoning. The system is designed with a modular architecture and provides a RESTful API for integration.

## Features

- Support for multiple document formats (PDF, DOCX)
- Document chunking and vector-based similarity search for efficient retrieval
- Integration with Google Gemini API for question answering
- FastAPI backend with clear error handling and validation
- Real-time query handling with async processing
- Logging and monitoring for performance tracking

## System Architecture

```
Input Document → Document Loader → Text Chunking → Vector Store → Query Processing
                                                        ↓
Response Builder ← Logic Evaluator ← Clause Matcher ← Query Parser
```

### Technology Stack

- **Backend:** FastAPI, Pydantic
- **ML/NLP:** Google Gemini API, Sentence Transformers
- **Document Processing:** PyPDF2, pdfplumber, python-docx
- **Vector Search:** Custom cosine similarity implementation
- **Deployment:** Uvicorn ASGI server

## Quick Start

### Prerequisites

- Python 3.11 or later
- Google Gemini API key

### Installation

```bash
git clone https://github.com/yourusername/bajaj-hackathon-llm-system.git
cd bajaj-hackathon-llm-system

python -m venv venv
source venv/bin/activate   # Windows: .\venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Add your GEMINI_API_KEY in .env

uvicorn app.main:app --reload
```

## API Usage

### Health Check

```bash
GET /api/v1/hackrx/health
```

### Document Query

```bash
POST /api/v1/hackrx/run
```

**Request Example**

```json
{
  "documents": "https://example.com/policy.pdf",
  "questions": [
    "What is the grace period for premium payment?",
    "What are the coverage limits?",
    "What are the exclusions?"
  ]
}
```

**Response Example**

```json
{
  "answers": [
    "The grace period for premium payment is thirty days.",
    "Coverage limits include maximum amounts per claim...",
    "Exclusions include pre-existing conditions..."
  ]
}
```

### Testing

```bash
python test_api.py
```

## Project Structure

```
bajaj-hackathon/
├── app/
│   ├── api/v1/endpoints.py      # API routes
│   ├── core/config.py           # Settings
│   ├── models/models.py         # Pydantic models
│   ├── services/
│   │   ├── document_loader.py
│   │   ├── query_parser.py
│   │   ├── vector_store.py
│   │   ├── clause_matcher.py
│   │   ├── logic_evaluator.py
│   │   └── response_builder.py
│   ├── utils/
│   │   ├── exceptions.py
│   │   ├── logging_config.py
│   │   └── monitoring.py
│   └── main.py
├── test_api.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Configuration

`.env` file should include:

```env
GEMINI_API_KEY=your-gemini-api-key-here
```

Configurable options in `app/core/config.py`:

- `MAX_CHUNK_SIZE` (default: 1000)
- `CHUNK_OVERLAP` (default: 200)
- `TOP_K_RESULTS` (default: 5)

## Development and Testing

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
python test_api.py
```

## Performance

- Caching for faster repeated queries
- Asynchronous request handling
- Structured error handling with descriptive messages
- Logging and monitoring for debugging and analysis

## Hackathon Outcomes

- Processed complex insurance and policy documents successfully
- Delivered accurate answers to natural language queries
- Achieved sub-30 second response time for multiple queries
- Built with modular, production-ready structure

## License

This project is available under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- Bajaj Hackathon 2025 team
- Google Gemini API
- FastAPI and the Python open-source community
