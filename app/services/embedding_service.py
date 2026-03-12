# app/services/embedding_service.py
# Handles: generating embeddings, building ChromaDB index, and querying

import time, os 
import logging
from openai import OpenAI
import chromadb
from chromadb.config import Settings 

logger = logging.getLogger(__name__)

EMBEDDING_MODEL         = "text-embedding-3-small"
EMBEDDING_MODEL_VERSION = "openai/text-embedding-3-small-v1"
COLLECTION_NAME         = "products"
CHROMA_BATCH_SIZE       = 100   # ChromaDB max is 166, using 100 to be safe

def _build_product_text(product: dict) -> str:
    return (
        f"{product['name']}. {product['description']} "
        f"Category: {product['category']}. "
        f"Brand: {product.get('brand', '')}. "
        f"Color: {product.get('color', '')}. "
        f"Price: ₹{product['price']}."
    )


class EmbeddingService:
    def __init__(self, openai_api_key: str, db_path: str = "./chroma_db"):
        self.client = OpenAI(api_key=openai_api_key)
        # Persistent ChromaDB — data survives server restarts
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = None

    def get_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text string."""
        response = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text.strip()
        )
        return response.data[0].embedding

    def build_index(self, products: list[dict]):
        """Index all products into ChromaDB. Skips if already indexed."""
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

        if self.collection.count() == len(products):
            logger.info("Index already up-to-date. Skipping re-indexing.")
            return

        # Clear stale data and rebuild
        self.chroma_client.delete_collection(COLLECTION_NAME)
        self.collection = self.chroma_client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

        ids, embeddings, documents, metadatas = [], [], [], []

        logger.info(f"Building index for {len(products)} products...")
        for product in products:
            text = _build_product_text(product)
            embedding = self.get_embedding(text)
            ids.append(str(product["id"]))
            embeddings.append(embedding)
            documents.append(text)
            metadatas.append({
                "id":            product["id"],
                "name":          product["name"],
                "category":      product["category"],
                "price":         product["price"],
                "image_url":     product["image_url"],
                "in_stock":      product["in_stock"],
                "description":   product["description"],
                "brand":         product.get("brand", ""),
                "color":         product.get("color", ""),
                "rating":        product.get("rating", 0),
                "reviews_count": product.get("reviews_count", 0),
            })

        # Insert in chunks — ChromaDB max batch size is 166
        total = len(ids)
        for i in range(0, total, CHROMA_BATCH_SIZE):
            end = min(i + CHROMA_BATCH_SIZE, total)
            self.collection.add(
                ids=ids[i:end],
                embeddings=embeddings[i:end],
                documents=documents[i:end],
                metadatas=metadatas[i:end],
            )
            logger.info(f"Indexed {end}/{total} products...")

        logger.info("Index built and persisted successfully.")

    def search(self, query: str, top_k: int = 5) -> dict:
        """
        Search products by semantic similarity.
        Returns structured response with scores and metadata.
        """
        start_time = time.time()

        query_embedding = self.get_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["metadatas", "distances", "documents"]
        )

        latency_ms = round((time.time() - start_time) * 1000, 2)

        products = []
        for meta, distance in zip(results["metadatas"][0], results["distances"][0]):
            similarity = round(1 - distance, 4)
            products.append({
                "id":               meta["id"],
                "name":             meta["name"],
                "description":      meta["description"],
                "category":         meta["category"],
                "price":            meta["price"],
                "image_url":        meta["image_url"],
                "in_stock":         meta["in_stock"],
                "brand":            meta.get("brand", ""),
                "color":            meta.get("color", ""),
                "rating":           meta.get("rating", 0),
                "reviews_count":    meta.get("reviews_count", 0),
                "similarity_score": similarity,
            })

        return {
            "query":         query,
            "model_version": EMBEDDING_MODEL_VERSION,
            "latency_ms":    latency_ms,
            "top_products":  products,
        }