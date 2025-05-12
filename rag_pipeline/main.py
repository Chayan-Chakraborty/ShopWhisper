from document_loader import load_and_split_csv
from retriever import Retriever
from generator import generate_answer
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Header
from typing import List, Dict, Any, Optional
import uvicorn
from fastapi.responses import JSONResponse
import json
from recommendation_system import RecommendationSystem
from config import PDF_PATH
    
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
    chunks = load_and_split_csv(PDF_PATH)

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

recommendation_system = RecommendationSystem()

@app.get("/")
async def root():
    return {"message": "Welcome to the Product Recommendation API"}

@app.get("/user/behavior", response_model=Dict[str, Any])
async def get_user_behavior(user_id: str = Header(..., alias="user-id")):
    """
    Analyze and return user's purchasing behavior based on their user ID.
    """
    print(user_id)
    try:
        return recommendation_system.analyze_user_behavior(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze user behavior: {str(e)}")

@app.get("/user/recommendations", response_model=List[Dict[str, Any]])
async def get_recommendations(
    user_id: Optional[str] = Header(None),
    num_recommendations: int = 5
):
    """Get product recommendations for a user"""
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required in headers")
        
    try:
        recommendations = recommendation_system.get_recommendations(user_id, num_recommendations)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/popular-products", response_model=List[Dict[str, Any]])
async def get_popular_products(num_products: int = 5):
    """Get popular products based on all users' order history"""
    try:
        popular_products = recommendation_system.get_popular_products(num_products)
        return popular_products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
       

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
