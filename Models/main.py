from Product import Session
from search_index import build_product_search_corpus, build_faiss_index, search_products
from rag import generate_answer

def main():
    session = Session()

    print("Building product corpus and FAISS index...")
    texts, ids = build_product_search_corpus(session)
    index, _ = build_faiss_index(texts)

    keywords = input("Enter search keywords (space-separated): ").split()
    query = ' '.join(keywords)

    results = search_products(keywords, index, texts, ids, session)

    if not results:
        print("No matching products found.")
        return

    print("\nTop matching products:")
    for product in results:
        print(f"- {product.name} | SKU: {product.sku} | Price: {product.selling_price}")

    print("\nGPT Summary:")
    explanation = generate_answer(query, results)
    print(explanation)

if __name__ == '__main__':
    main()
