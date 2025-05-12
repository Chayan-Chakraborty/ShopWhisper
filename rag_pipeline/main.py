from document_loader import load_and_split
from retriever import Retriever
from generator import generate_answer

def main():
    chunks = load_and_split("my_docs/data.txt")
    texts = [chunk.page_content for chunk in chunks]

    retriever = Retriever(texts)

    while True:
        query = input("\nAsk a question (or type 'exit'): ")
        if query.lower() == "exit":
            break

        relevant_chunks = retriever.get_relevant_chunks(query)
        context = "\n\n".join(relevant_chunks)

        answer = generate_answer(context, query)
        print("\n🔍 Answer:\n", answer)

if __name__ == "__main__":
    main()
