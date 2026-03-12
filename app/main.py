# app/main.py

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

from app.services.products_data import get_all_products, get_product_by_id
from app.services.embedding_service import EmbeddingService
from app.services.log_service import log_search, get_history
from app.schemas import ProductCreate, RecommendRequest 

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING) 

# ── Global embedding service ────────────────────────────────────────────────
embedding_service: EmbeddingService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the vector index once at startup."""
    global embedding_service
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment variables.")

    embedding_service = EmbeddingService(openai_api_key=api_key)
    products = get_all_products()
    embedding_service.build_index(products)
    yield


app = FastAPI(
    title="AI Outfit Recommendation API",
    version="1.0.0",
    description="Semantic search-powered outfit recommendations",
    lifespan=lifespan,
)

# ── Static files & templates ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))





# ════════════════════════════════════════════════════════════════════════════
# FRONTEND ROUTES
# ════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request):
    return templates.TemplateResponse("cart.html", {"request": request})


# ════════════════════════════════════════════════════════════════════════════
# PRODUCT APIs (Microservice 1 – Product Catalog)
# ════════════════════════════════════════════════════════════════════════════

@app.get("/products", tags=["Products"])
async def list_products():
    """Return all products in the catalog."""
    return {"products": get_all_products(), "total": len(get_all_products())}


@app.get("/products/{product_id}", tags=["Products"])
async def get_product(product_id: int):
    """Return a single product by ID."""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products", tags=["Products"], status_code=201)
async def add_product(product: ProductCreate):
    """Add a new product to the in-memory catalog."""
    products = get_all_products()
    new_id = max(p["id"] for p in products) + 1
    new_product = {"id": new_id, **product.model_dump()}
    products.append(new_product)
    # Re-index with new product
    embedding_service.build_index(products)
    return {"message": "Product added successfully", "product": new_product}


# ════════════════════════════════════════════════════════════════════════════
# AI RECOMMENDATION API (Microservice 2 – Semantic Search)
# ════════════════════════════════════════════════════════════════════════════

@app.post("/products/recommend", tags=["AI Recommendations"])
async def recommend_products(body: RecommendRequest):
    """
    Accept a natural language prompt and return top 5 outfit recommendations
    using semantic similarity search.
    """
    if not body.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    # ── Gender check — dataset is women's fashion only ───────────────────
    MEN_KEYWORDS = [
        "men", "man", "male", "boys", "boy", "groom",
        "mens", "men's", "shirt for men", "suit for men",
        "kurta for men", "trousers for men", "sherwani"
    ]
    prompt_lower = body.prompt.lower()
    if any(kw in prompt_lower for kw in MEN_KEYWORDS):
        return {
            "query": body.prompt,
            "model_version": None,
            "latency_ms": 0,
            "result_count": 0,
            "recommendations": [],
            "message": "Sorry, this platform only features women's fashion. Try searching for women's outfits instead!",
        }
    result = embedding_service.search(query=body.prompt, top_k=10)

    # Log the search
    log_search(
        query=result["query"],
        model_version=result["model_version"],
        latency_ms=result["latency_ms"],
        results=result["top_products"],
    )

    return {
        "query": result["query"],
        "model_version": result["model_version"],
        "latency_ms": result["latency_ms"],
        "recommendations": result["top_products"],
    }


# ════════════════════════════════════════════════════════════════════════════
# ANALYTICS API (Microservice 3 – Logging & History)
# ════════════════════════════════════════════════════════════════════════════

@app.get("/analytics/history", tags=["Analytics"])
async def search_history():
    """Return all logged AI search queries with metadata."""
    return {"history": get_history(), "total": len(get_history())}
