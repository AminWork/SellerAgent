import os
import logging
from typing import List, Tuple
from datetime import datetime
import json

import numpy as np
import requests
from django.conf import settings
from pymongo import MongoClient

from .models import Product

# Create dedicated logger for RAG debugging
logger = logging.getLogger(__name__)
rag_logger = logging.getLogger('rag_debug')
rag_logger.setLevel(logging.DEBUG)

# Create file handler for RAG logs
if not rag_logger.handlers:
    handler = logging.FileHandler('/app/rag_debug.log')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    rag_logger.addHandler(handler)


def _get_mongo_db():
    """Connect to Mongo using same env as Django djongo settings."""
    uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    username = os.getenv('MONGODB_USERNAME', '')
    password = os.getenv('MONGODB_PASSWORD', '')
    auth_source = os.getenv('MONGODB_AUTH_SOURCE', 'admin')
    db_name = os.getenv('MONGODB_NAME', 'ecommerce_ai')

    rag_logger.info(f"Connecting to MongoDB: uri={uri}, db_name={db_name}, username={username}, auth_source={auth_source}")

    try:
        if username and password:
            client = MongoClient(uri, username=username, password=password, authSource=auth_source)
        else:
            client = MongoClient(uri)
        
        db = client[db_name]
        # Test connection
        db.command('ping')
        rag_logger.info(f"Successfully connected to MongoDB database: {db_name}")
        return db
    except Exception as e:
        rag_logger.error(f"Failed to connect to MongoDB: {e}")
        raise


def _simple_text_embedding(text: str, dim: int = 384) -> List[float]:
    """Simple hash-based embedding for fallback when OpenRouter is unavailable."""
    import hashlib
    import struct
    
    # Create a hash of the text
    hash_obj = hashlib.sha256(text.lower().encode('utf-8'))
    hash_bytes = hash_obj.digest()
    
    # Convert hash bytes to float vector
    embedding = []
    for i in range(0, min(len(hash_bytes), dim * 4), 4):
        chunk = hash_bytes[i:i+4]
        if len(chunk) == 4:
            val = struct.unpack('f', chunk)[0]
        else:
            val = float(sum(chunk))
        embedding.append(val)
    
    # Pad or truncate to desired dimension
    while len(embedding) < dim:
        embedding.append(0.0)
    embedding = embedding[:dim]
    
    # Normalize the vector
    norm = sum(x*x for x in embedding) ** 0.5
    if norm > 0:
        embedding = [x / norm for x in embedding]
    
    return embedding


def _openrouter_embed(texts: List[str]) -> List[List[float]]:
    # Load all available API keys for rotation
    api_keys = []
    for i in range(1, 11):  # Keys 1-10
        key = getattr(settings, f'OPENROUTER_API_KEY_{i}', None)
        if key:
            api_keys.append(key)
    
    # Also include the main key if present
    main_key = getattr(settings, 'OPENROUTER_API_KEY', None)
    if main_key and main_key not in api_keys:
        api_keys.insert(0, main_key)
    
    if not api_keys:
        rag_logger.error("No OPENROUTER_API_KEY configured")
        raise RuntimeError("No OPENROUTER_API_KEY configured")
    
    model = getattr(settings, 'OPENROUTER_EMBEDDING_MODEL', 'openai/text-embedding-3-small')
    base_url = "https://openrouter.ai/api/v1"
    
    rag_logger.info(f"OpenRouter embedding request: model={model}, texts_count={len(texts)}, available_keys={len(api_keys)}")
    
    payload = {
        "model": model,
        "input": texts,
    }
    
    # Try each API key until one works
    for i, api_key in enumerate(api_keys, 1):
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "SellerAgent E-commerce",
            }
            
            rag_logger.info(f"Trying embedding token {i}/{len(api_keys)}: {api_key[:20]}...")
            
            resp = requests.post(f"{base_url}/embeddings", headers=headers, json=payload, timeout=60)
            rag_logger.info(f"Embedding token {i} response status: {resp.status_code}")
            
            # Log response details for debugging
            rag_logger.debug(f"Response headers: {dict(resp.headers)}")
            rag_logger.debug(f"Response content length: {len(resp.content)} bytes")
            rag_logger.debug(f"Response content preview: {resp.text[:200]}...")
            
            if resp.status_code == 200:
                try:
                    # Check if response is empty
                    if not resp.text.strip():
                        rag_logger.error(f"❌ Embedding token {i} returned empty response")
                        continue
                    
                    data = resp.json()
                    rag_logger.debug(f"OpenRouter response data keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                    
                    if "data" not in data:
                        rag_logger.error(f"OpenRouter response missing 'data' field: {data}")
                        continue  # Try next token
                    
                    embeddings = [item["embedding"] for item in data.get("data", [])]
                    rag_logger.info(f"✅ Embedding SUCCESS with token {i}! Got {len(embeddings)} embeddings")
                    return embeddings
                    
                except json.JSONDecodeError as e:
                    rag_logger.error(f"❌ Embedding token {i} JSON decode error: {e}")
                    rag_logger.error(f"❌ Raw response text: '{resp.text}'")
                    rag_logger.error(f"❌ Response content type: {resp.headers.get('content-type', 'unknown')}")
                    continue  # Try next token
            else:
                rag_logger.warning(f"❌ Embedding token {i} failed: {resp.status_code} - {resp.text[:100]}")
                continue  # Try next token
                
        except Exception as e:
            rag_logger.error(f"❌ Embedding token {i} exception: {e}")
            continue  # Try next token
    
    # All tokens failed - fall back to simple embeddings
    rag_logger.error(f"❌ ALL {len(api_keys)} EMBEDDING TOKENS FAILED - falling back to simple embeddings")
    rag_logger.warning(f"Falling back to simple text embeddings for {len(texts)} texts")
    return [_simple_text_embedding(text) for text in texts]


def _product_text(product: Product) -> str:
    tags = product.tags if isinstance(product.tags, list) else []
    tags_str = ", ".join(map(str, tags))
    return f"Name: {product.name}\nDescription: {product.description}\nCategory: {product.category}\nTags: {tags_str}"


def ensure_embeddings_for_all_products(batch_size: int = 32) -> int:
    """Create embeddings for products missing in the embeddings collection.
    Returns number of new embeddings created.
    """
    rag_logger.info(f"Starting ensure_embeddings_for_all_products with batch_size={batch_size}")
    
    try:
        db = _get_mongo_db()
        coll = db["product_embeddings"]
        rag_logger.info(f"Connected to embeddings collection: {coll.name}")

        # Get total product count
        total_products = Product.objects.count()
        rag_logger.info(f"Total products in database: {total_products}")

        # Collect products without embeddings
        missing: List[Tuple[str, str]] = []  # (pk, text)
        for p in Product.objects.all():
            pk = str(p.pk)
            existing = coll.find_one({"_id": pk})
            if existing is None:
                product_text = _product_text(p)
                missing.append((pk, product_text))
                rag_logger.debug(f"Missing embedding for product {pk}: {p.name}")
            else:
                rag_logger.debug(f"Embedding exists for product {pk}: {p.name}")

        rag_logger.info(f"Found {len(missing)} products without embeddings")

        if not missing:
            rag_logger.info("All products already have embeddings")
            return 0

        created = 0
        i = 0
        while i < len(missing):
            chunk = missing[i : i + batch_size]
            texts = [t for _, t in chunk]
            pks = [pk for pk, _ in chunk]
            
            rag_logger.info(f"Processing batch {i//batch_size + 1}: {len(chunk)} products")
            rag_logger.debug(f"Batch product IDs: {pks}")
            
            try:
                vectors = _openrouter_embed(texts)
                rag_logger.info(f"Got {len(vectors)} embeddings from OpenRouter")
                
                if len(vectors) != len(chunk):
                    rag_logger.error(f"Mismatch: expected {len(chunk)} embeddings, got {len(vectors)}")
                    break
                    
            except Exception as e:
                rag_logger.error(f"Embedding batch failed: {e}")
                break
                
            now = datetime.utcnow()
            for (pk, _), vec in zip(chunk, vectors):
                try:
                    result = coll.replace_one(
                        {"_id": pk},
                        {"_id": pk, "embedding": vec, "updated_at": now},
                        upsert=True,
                    )
                    rag_logger.debug(f"Saved embedding for product {pk}: matched={result.matched_count}, modified={result.modified_count}, upserted={result.upserted_id}")
                    created += 1
                except Exception as e:
                    rag_logger.error(f"Failed to save embedding for product {pk}: {e}")
                    
            i += batch_size
            
        rag_logger.info(f"Completed embedding creation: {created} new embeddings created")
        return created
        
    except Exception as e:
        rag_logger.error(f"Error in ensure_embeddings_for_all_products: {e}")
        raise


def _cosine_sim_matrix(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    # A: (n, d), b: (d,)
    A_norm = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-8)
    b_norm = b / (np.linalg.norm(b) + 1e-8)
    return A_norm @ b_norm


def semantic_search(query: str, top_k: int = 8) -> List[str]:
    """Return product PKs (as strings) most similar to the query."""
    rag_logger.info(f"Starting semantic_search: query='{query}', top_k={top_k}")
    
    if not query:
        rag_logger.warning("Empty query provided to semantic_search")
        return []

    try:
        db = _get_mongo_db()
        coll = db["product_embeddings"]
        rag_logger.info(f"Connected to embeddings collection for search")

        # Ensure all products have embeddings
        try:
            created = ensure_embeddings_for_all_products()
            rag_logger.info(f"Ensured embeddings: {created} new embeddings created")
        except Exception as e:
            rag_logger.warning(f"Could not ensure all embeddings: {e}")

        # Load all embeddings
        docs = list(coll.find({}, {"_id": 1, "embedding": 1}))
        rag_logger.info(f"Loaded {len(docs)} embeddings from database")
        
        if not docs:
            rag_logger.warning("No embeddings found in database")
            return []

        # Compute query embedding
        try:
            rag_logger.info(f"Computing embedding for query: '{query}'")
            embeddings = _openrouter_embed([query])
            if not embeddings:
                rag_logger.error("OpenRouter returned empty embeddings for query")
                return []
            q_vec = embeddings[0]
            rag_logger.info(f"Got query embedding vector of length {len(q_vec)}")
        except Exception as e:
            rag_logger.error(f"Query embedding failed: {e}")
            return []

        # Prepare embedding matrix
        try:
            A = np.array([d["embedding"] for d in docs], dtype=np.float32)
            rag_logger.info(f"Created embedding matrix: shape={A.shape}")
            
            scores = _cosine_sim_matrix(A, np.array(q_vec, dtype=np.float32))
            rag_logger.info(f"Computed similarity scores: shape={scores.shape}, min={scores.min():.4f}, max={scores.max():.4f}")

            # Rank and select top_k
            idxs = np.argsort(-scores)[:top_k]
            pks = [str(docs[int(i)]["_id"]) for i in idxs]
            scores_top = [float(scores[i]) for i in idxs]
            
            rag_logger.info(f"Top {len(pks)} results: {list(zip(pks, scores_top))}")
            return pks
            
        except Exception as e:
            rag_logger.error(f"Error in similarity computation: {e}")
            return []
            
    except Exception as e:
        rag_logger.error(f"Error in semantic_search: {e}")
        return []
