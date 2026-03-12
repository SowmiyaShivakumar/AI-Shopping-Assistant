# Code Structure

## Microservices Overview

The application is split into **3 logical microservices** within a single FastAPI app:

---

### Microservice 1 — Product Catalog (`/products`)
**File:** `app/services/products_data.py`

- Stores 64 products across categories: ethnic, western, formal, party, activewear, footwear, accessories, winterwear, kids, nightwear, swimwear
- Each product has: id, name, description, category, occasion[], price, image_url, in_stock
- `get_all_products()` — returns full catalog
- `get_product_by_id(id)` — single product lookup

**Routes in `main.py`:**
- `GET /products` — list all
- `GET /products/{id}` — get one
- `POST /products` — add new (also re-indexes ChromaDB)

---

### Microservice 2 — AI Semantic Search (`/products/recommend`)
**File:** `app/services/embedding_service.py`

- `EmbeddingService` class wraps OpenAI + ChromaDB
- `build_index(products)` — called at app startup; generates embeddings for all products and loads into ChromaDB
- `get_embedding(text)` — calls OpenAI `text-embedding-3-small`
- `search(query, top_k=5)` — embeds the query, queries ChromaDB with cosine similarity, returns ranked results

**Route in `main.py`:**
- `POST /products/recommend` — accepts `{ "prompt": "..." }`, returns top 5 recommendations

---

### Microservice 3 — Analytics & Logging (`/analytics`)
**File:** `app/services/log_service.py`

- `log_search(query, model_version, latency_ms, results)` — records each AI search event
- `get_history()` — returns all logged events
- Stores: timestamp, query, model version, latency (ms), result count, similarity scores

**Route in `main.py`:**
- `GET /analytics/history` — returns full search history

---

## Data Flow

```
User types prompt
      ↓
POST /products/recommend
      ↓
EmbeddingService.search(prompt)
      ↓
OpenAI text-embedding-3-small → query vector
      ↓
ChromaDB cosine similarity search
      ↓
Rank by similarity score
      ↓
log_service.log_search(...)
      ↓
Return top 5 products + metadata + scores
```
