# API Documentation

Base URL: `http://localhost:8000`

---

## Product APIs

### GET `/products`
Returns all products in the catalog.

**Response:**
```json
{
  "products": [...],
  "total": 1000
}
```

---

### GET `/products/{id}`
Returns a single product by numeric ID.

**Response:**
```json
{
  "id": 1,
  "name": "White Cotton Kurta",
  "description": "...",
  "category": "ethnic",
  "occasion": ["temple", "religious"],
  "price": 899,
  "image_url": "https://...",
  "in_stock": true
}
```

**Error (404):**
```json
{ "detail": "Product not found" }
```

---

### POST `/products`
Add a new product and re-index the vector store.

**Request Body:**
```json
{
  "name": "Floral Summer Dress",
  "description": "Light and breezy dress for summer outings.",
  "category": "western",
  "occasion": ["casual", "beach"],
  "price": 1299,
  "image_url": "https://images.unsplash.com/...",
  "in_stock": true
}
```

**Response (201):**
```json
{
  "message": "Product added successfully",
  "product": { "id": 1001, ... }
}
```

---

## AI Recommendation API

### POST `/products/recommend`
Returns the top 5 outfit recommendations for a natural language query.

**Request Body:**
```json
{
  "prompt": "Suggest the best outfit to wear to a temple"
}
```

**Response:**
```json
{
  "query": "Suggest the best outfit to wear to a temple",
  "model_version": "openai/text-embedding-3-small-v1",
  "latency_ms": 312.5,
  "recommendations": [
    {
      "id": 1,
      "name": "White Cotton Kurta",
      "description": "...",
      "category": "ethnic",
      "price": 899,
      "image_url": "https://...",
      "in_stock": true,
      "similarity_score": 0.8742
    },
    ...
  ]
}
```

---

## Analytics API

### GET `/analytics/history`
Returns all logged search queries with metadata.

**Response:**
```json
{
  "history": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "query": "temple outfit",
      "model_version": "openai/text-embedding-3-small-v1",
      "latency_ms": 312.5,
      "result_count": 5,
      "top_similarity": 0.8742,
      "scores": [0.8742, 0.8511, 0.8203, 0.7991, 0.7744]
    }
  ],
  "total": 1
}
```

---

## Interactive Docs

FastAPI auto-generates interactive documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
