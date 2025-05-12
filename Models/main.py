from product import Session
from search_index import build_product_search_corpus, build_faiss_index, search_products

def main():
    session = Session()

    print("Building search index...")
    texts, ids = build_product_search_corpus(session)
    index, _ = build_faiss_index(texts)

    keywords = input("Enter search keywords (space-separated): ").split()

    results = search_products(keywords, index, texts, ids, session)

    print("\nTop results:")
    for product in results:
        print(f"- {product.name} | SKU: {product.sku} | Status: {product.status}")

if __name__ == '__main__':
    main()
