from flask import Flask, request, jsonify
from Product import Session
from search_index import build_product_search_corpus, build_faiss_index, search_products
from rag import generate_answer

app = Flask(__name__)

# Load and build everything once at startup
session = Session()
texts, ids = build_product_search_corpus(session)
index, _ = build_faiss_index(texts)

@app.route('/search', methods=['GET'])
def search():
    keywords = request.args.getlist('keyword')  # ?keyword=plywood&keyword=oak
    query = ' '.join(keywords)
    results = search_products(keywords, index, texts, ids, session)

    if not results:
        return jsonify({"message": "No matching products found."}), 404

    products = [{
        "name": product.name,
        "sku": product.sku,
        "price": product.selling_price
    } for product in results]

    explanation = generate_answer(query, results)

    return jsonify({
        "products": products,
        "summary": explanation
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
