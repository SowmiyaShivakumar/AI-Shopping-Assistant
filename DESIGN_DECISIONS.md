# Design Decisions

## 1. Embedding Model — `text-embedding-3-small`
- Chosen for cost-effectiveness and speed
- 1536-dimensional vectors with strong semantic understanding
- Better multilingual and domain generalization than `ada-002`
- Consistent model used for both indexing (startup) and querying (runtime)

## 2. Vector Database — ChromaDB (In-Memory)
- No external database setup required for learning purposes
- ChromaDB's in-memory mode is ideal for prototypes and demos
- `hnsw:space: cosine` ensures cosine similarity ranking
- Re-indexed every startup since product data is static

## 3. Product Text Representation
Each product is embedded as a rich composite string:
```
{name}. {description} Category: {category}. Occasions: {occasions}. Price: ₹{price}.
```
This maximizes semantic overlap with natural language user queries.

## 4. Microservice Separation (Logical)
Three distinct service files are kept separate for clarity:
- `products_data.py` — pure data layer
- `embedding_service.py` — AI/vector operations
- `log_service.py` — observability

In production, these could be deployed as independent services.

## 5. Similarity Score Display
ChromaDB returns cosine distance (0 = identical, 2 = opposite).
We convert to similarity: `score = 1 - distance` and display as a percentage bar.

## 6. No Database (Simple by Design)
Products are stored as a Python list. This is intentional for simplicity.
For production: replace with SQLite, PostgreSQL, or MongoDB Atlas.

## 7. Cart — Session Storage
Cart state uses `sessionStorage` (in-memory per tab). This avoids backend complexity and satisfies the demo requirement without a real user auth system.

## 8. Frontend — Server-Side Templates + Vanilla JS
Jinja2 templates with vanilla JavaScript keep the frontend dependency-free and easy to understand. No React or bundler needed.
