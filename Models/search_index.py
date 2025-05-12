import faiss
import numpy as np
from embeddings import get_embedding
import product

def build_product_corpus(session):
    products = session.query(product).all()
    texts, ids = [], []

    for available_product in products:
        text = f"{available_product.name} {available_product.description or ''} {available_product.status or ''} " \
               f"{available_product.unit_type or ''} {available_product.sku or ''}"
        for attr in available_product.attributes:
            text += f" {attr.value or ''} {attr.variant_tag or ''} {attr.description or ''}"
        if available_product.category:
            text += f" {available_product.category.name or ''} {available_product.category.description or ''} {available_product.category.meta_keywords or ''}"
            for cat_attr in available_product.category.category_attributes:
                text += f" {cat_attr.filter_values or ''}"

        texts.append(text.strip())
        ids.append(available_product.id)

    return texts, ids

def build_faiss_index(texts):
    embeddings = [get_embedding(text) for text in texts]
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    return index, embeddings

def search_products(keywords, index, texts, ids, session, top_k=5):
    query = ' '.join(keywords)  # Combine keyword list into single string
    query_embedding = get_embedding(query)
    D, I = index.search(np.array([query_embedding], dtype='float32'), top_k)

    results = []
    for idx in I[0]:
        product_id = ids[idx]
        product = session.query(product).get(product_id)
        results.append(product)
    return results
