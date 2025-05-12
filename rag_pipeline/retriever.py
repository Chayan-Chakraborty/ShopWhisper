from embedder import Embedder
from vector_store import VectorStore
from config import TOP_K

class Retriever:
    def __init__(self, texts: list[str]):
        self.embedder = Embedder()
        self.texts = texts
        self.embeddings = self.embedder.embed(texts)

        self.store = VectorStore(dimension=len(self.embeddings[0]))
        self.store.add(self.embeddings, self.texts)

    def get_relevant_chunks(self, query: str):
        query_embedding = self.embedder.embed([query])
        return self.store.search(query_embedding, TOP_K)
