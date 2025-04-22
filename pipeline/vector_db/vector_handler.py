# vector_handler.py
from sentence_transformers import SentenceTransformer
import qdrant_client

model = SentenceTransformer("all-MiniLM-L6-v2")
client = qdrant_client.QdrantClient(":memory:")

def embed_and_store(documents: list[str], collection="silent_docs"):
    vectors = model.encode(documents).tolist()
    payloads = [{"text": doc} for doc in documents]
    client.upload_collection(collection_name=collection, vectors=vectors, payload=payloads)

def query_collection(query: str, collection="silent_docs"):
    query_vec = model.encode([query])[0].tolist()
    hits = client.search(collection_name=collection, query_vector=query_vec, limit=5)
    return [hit.payload["text"] for hit in hits]