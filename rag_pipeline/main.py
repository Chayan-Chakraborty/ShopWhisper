from document_loader import load_and_split_csv
from retriever import Retriever
from generator import generate_answer

def main():
    chunks = load_and_split_csv("/Users/chayanchakraborty/Downloads/Dummy Data Pdf - Sheet1.csv")
    
    retriever = Retriever(chunks)

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
