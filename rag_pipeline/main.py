from document_loader import load_and_split_csv
from retriever import Retriever
from generator import generate_answer
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Header
from typing import List, Dict, Any, Optional
import uvicorn
from fastapi.responses import JSONResponse
import json
    
app = FastAPI()

# In-memory session store
sessions = {}

class QueryRequest(BaseModel):
    question: str

@app.post("/product/load-fliter")
def query_handler(request: QueryRequest, user_id: str = Header(..., alias="user-id")):
    if request.question.lower() == "exit":
        return {"message": "Use /session/end to end the session."}

    # Load and split product data CSV
    chunks = load_and_split_csv("/Users/chayanchakraborty/Downloads/dummy-data.csv")

    # Create or fetch user session
    if user_id not in sessions:
        sessions[user_id] = Retriever(chunks)

    retriever = sessions[user_id]

    relevant_chunks = retriever.get_relevant_chunks(request.question)
    context = "\n\n".join(relevant_chunks)

    answer = generate_answer(context, request.question)

    try:
        parsed_answer = json.loads(answer)  # Convert JSON string to dict
    except json.JSONDecodeError:
        parsed_answer = {"raw_answer": answer}  # fallback if answer is not JSON

    return JSONResponse(content={
        "user_id": user_id,
        "question": request.question,
        "answer": parsed_answer
    })
       

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
