# Bajaj Hackathon 2025 - Intelligent Document Query System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Project Overview

An intelligent document analysis system that processes PDF/DOCX files and answers questions using LLM-powered query understanding and decision making. Built for the Bajaj Hackathon 2025, this system combines advanced NLP techniques with modern API architecture.

## ✨ Key Features

- **📄 Multi-format Document Processing**: Supports PDF and DOCX file analysis
- **🔍 Vector Similarity Search**: Efficient document chunk retrieval using embeddings
- **🤖 LLM Integration**: Powered by Google's Gemini API for intelligent responses
- **🚀 RESTful API**: FastAPI-based with comprehensive error handling
- **⚡ Production Ready**: Includes monitoring, logging, and performance optimization
- **🔄 Real-time Processing**: Handles multiple queries simultaneously

## 🏗️ System Architecture

```
Input Document → Document Loader → Text Chunking → Vector Store → Query Processing
                                                        ↓
Response Builder ← Logic Evaluator ← Clause Matcher ← Query Parser
```

### Technical Stack

- **Backend**: FastAPI, Pydantic
- **ML/AI**: Google Gemini API, Sentence Transformers
- **Document Processing**: PyPDF2, pdfplumber, python-docx
- **Vector Search**: Custom vector store with cosine similarity
- **Deployment**: Uvicorn ASGI server

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bajaj-hackathon-llm-system.git
   cd bajaj-hackathon-llm-system
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📡 API Usage

### Health Check
```bash
GET /api/v1/hackrx/health
```

### Document Query Processing
```bash
POST /api/v1/hackrx/run
```

**Request Format:**
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

**Response Format:**
```json
{
  "answers": [
    "The grace period for premium payment is thirty days.",
    "Coverage limits include maximum amounts per claim...",
    "Exclusions include pre-existing conditions..."
  ]
}
```

### Testing the API

Run the included test script:
```bash
python test_api.py
```

## 🛠️ Project Structure

```
bajaj-hackathon/
├── app/
│   ├── api/v1/
│   │   └── endpoints.py         # API route definitions
│   ├── core/
│   │   └── config.py           # Configuration settings
│   ├── models/
│   │   └── models.py           # Pydantic data models
│   ├── services/
│   │   ├── document_loader.py  # Document processing
│   │   ├── query_parser.py     # Query understanding
│   │   ├── vector_store.py     # Vector embeddings
│   │   ├── clause_matcher.py   # Similarity search
│   │   ├── logic_evaluator.py  # LLM integration
│   │   └── response_builder.py # Response formatting
│   ├── utils/
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── logging_config.py   # Logging setup
│   │   └── monitoring.py       # Performance monitoring
│   └── main.py                 # FastAPI application
├── test_api.py                 # API testing script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

## 🔧 Configuration

Create a `.env` file with:
```env
GEMINI_API_KEY=your-gemini-api-key-here
```

Optional configuration in `app/core/config.py`:
- `MAX_CHUNK_SIZE`: Text chunk size (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `TOP_K_RESULTS`: Number of similar chunks to retrieve (default: 5)

## 🧪 Development & Testing

### Running Tests
```bash
python test_api.py
```

### Development Mode
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 📈 Performance Features

- **Caching**: Global service initialization for optimal performance
- **Monitoring**: Built-in performance tracking and logging
- **Error Handling**: Comprehensive exception handling with meaningful messages
- **Async Processing**: Non-blocking API operations

## 🏆 Hackathon Achievements

- ✅ Successfully processes complex policy documents
- ✅ Accurate question-answering with high confidence scores
- ✅ Sub-30 second processing time for 5 complex queries
- ✅ Production-ready architecture with monitoring
- ✅ Clean, maintainable codebase following best practices

## 🤝 Contributing

This project was developed for the Bajaj Hackathon 2025. Feel free to fork and enhance!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Bajaj Hackathon 2025 organizers
- Google Gemini API for LLM capabilities
- FastAPI and Python ecosystem
