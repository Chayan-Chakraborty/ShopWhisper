import faiss
import numpy as np

class VectorStore:
    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []

    def add(self, embeddings, docs):
        self.index.add(np.array(embeddings))
        self.documents.extend(docs)

    def search(self, embedding, top_k=5):
        D, I = self.index.search(np.array(embedding), k=top_k)
        return [self.documents[i] for i in I[0]]
