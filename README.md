rag-doc/
├── app/                          # 🐍 FastAPI Backend
│   ├── __init__.py
│   ├── main.py                   # App entry point (FastAPI app initialization)
│   ├── api/                      # API Route Controllers
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py            # Main router aggregator
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── ingest.py     # Upload & processing endpoints
│   │           └── chat.py       # Chat & Q&A endpoints
│   ├── core/                     # Core Infrastructure
│   │   ├── __init__.py
│   │   ├── config.py             # Env variables & settings (Pydantic BaseSettings)
│   │   ├── logging.py            # Custom logging config
│   │   └── exceptions.py         # Global exception handlers
│   ├── schemas/                  # Pydantic Models (Data validation)
│   │   ├── __init__.py
│   │   ├── chat.py               # Request/Response models for chat
│   │   └── document.py           # Models for file metadata
│   └── services/                 # Business Logic (The "Brain")
│       ├── __init__.py
│       ├── vector_store.py       # Logic to talk to Pinecone/Chroma/Qdrant
│       ├── llm_service.py        # Logic to talk to OpenAI/DeepSeek/Anthropic
│       └── document_parser.py    # PDF/Docx parsing logic
│
├── ui/                           # 🎨 Streamlit Frontend
│   ├── app.py                    # Streamlit entry point
│   ├── components/               # Reusable UI components
│   │   ├── chat_interface.py     # Chat bubble rendering
│   │   └── sidebar.py            # File uploader sidebar
│   └── api_client.py             # Helper to call FastAPI backend from Streamlit
│
├── tests/                        # Test Suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   └── test_services/
│
├── data/                         # (Optional) Local storage for uploads/vectors
├── .env                          # Secrets (API Keys)
├── .gitignore
├── docker-compose.yml            # Orchestrate Backend + Frontend + VectorDB
├── Dockerfile.backend
├── Dockerfile.frontend
├── pyproject.toml                # Dependencies
└── README.md