# DRAPE — AI-Powered Outfit Recommendation Platform

A semantic search-powered outfit recommendation system built with **FastAPI**, **OpenAI Embeddings**, and **ChromaDB**.

---

## Quick Start

### 1. Clone & Install
```bash
cd FastApi
pip install -r requirements.txt
```

### 2. Set Environment Variable
Create a `.env` file in the `FastApi/` directory:
```env
OPENAI_API_KEY=sk-your-openai-key-here
```

### 3. Run the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Open in Browser
```
http://localhost:8000
```

---

## Project Structure
```
ai-product-search/
└── FastApi/
    ├── README.md
    ├── CODE_STRUCTURE.md
    ├── DESIGN_DECISIONS.md
    ├── API_DOCUMENTATION.md
    ├── requirements.txt
    └── app/
        ├── main.py                     # FastAPI app + all routes
        ├── __init__.py
        ├── services/
        │   ├── products_data.py        # Product catalog (64 products)
        │   ├── embedding_service.py    # OpenAI + ChromaDB semantic search
        │   └── log_service.py          # Query logging & history
        ├── static/
        │   ├── css/style.css
        │   └── js/cart.js
        └── templates/
            ├── base.html
            ├── index.html
            └── cart.html
```

---

## Features
- Natural language outfit search (e.g. "What to wear to a temple?")
- 64 products across 10 categories
- Cosine similarity ranking via ChromaDB
- Cart system with quantity management
- Search history & analytics logging
- Category filtering in product catalog
