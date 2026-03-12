from pydantic import BaseModel

# ── Pydantic models ──────────────────────────────────────────────────────────
class ProductCreate(BaseModel):
    name:          str
    description:   str
    category:      str
    price:         float
    image_url:     str
    color:         str = "N/A"
    brand:         str = "Unknown"
    rating:        float = 0.0
    reviews_count: int = 0
    in_stock:      bool = True

class RecommendRequest(BaseModel):
    prompt: str