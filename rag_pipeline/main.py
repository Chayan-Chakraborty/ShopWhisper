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
import pandas as pd
import numpy as np
from config import PDF_PATH
import openai
from config import FALL_BACK_DATA

app = FastAPI()

# Initialize recommendation system
recommendation_system = RecommendationSystem(data_path="data/products.csv")

# In-memory session store
sessions = {}

class QueryRequest(BaseModel):
    question: str

@app.post("/product/load-fliter")
def query_handler(request: QueryRequest, user_id: str = Header(..., alias="user-id")):
    # try:
        if request.question.lower() == "exit":
            return {"message": "Use /session/end to end the session."}

        chunks = load_and_split_csv(PDF_PATH)

        if user_id not in sessions:
            sessions[user_id] = Retriever(chunks)

        retriever = sessions[user_id]
        relevant_chunks = retriever.get_relevant_chunks(request.question)
        context = "\n\n".join(relevant_chunks)

        try:
            answer = generate_answer(context, request.question)
        except openai.error.AuthenticationError:
            raise HTTPException(status_code=401, detail="Invalid or expired OpenAI API key.")
        except openai.error.OpenAIError as e:
            raise HTTPException(status_code=502, detail=f"OpenAI API error: {str(e)}")

        try:
            parsed_answer = json.loads(answer)
        except json.JSONDecodeError:
            parsed_answer = {"raw_answer": answer}

        return JSONResponse(content={
            "user_id": user_id,
            "question": request.question,
            "answer": parsed_answer
        })

    # except HTTPException as http_ex:
    #     # Let FastAPI handle known HTTP exceptions
    #     raise http_ex
    # except Exception as e:
    #     # Fallback: return default product data from CSV
    #     try:
    #         return JSONResponse(content={
    #         "user_id": user_id,
    #         "question": request.question,
    #         "answer": FALL_BACK_DATA
    #     })
    #     except Exception as fallback_error:
    #         return JSONResponse(status_code=500, content={
    #             "error": f"Critical failure: {str(e)} | Fallback also failed: {fallback_error}"
    #         })

def convert_numpy_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj

@app.get("/")
async def root():
    return {"message": "Welcome to the Product Recommendation API"}

@app.get("/api/user/behavior")
async def get_user_behavior(user_id: Optional[str] = Header(None)):
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    try:
        # Clean user_id to ensure it's just the number
        user_id = str(user_id).replace('USER_', '')
        
        # Get recommended products based on behavior
        recommendations = recommendation_system.get_recommendations(user_id, num_recommendations=5)
        
        # Convert NumPy types and ensure reasons is a list
        converted_recommendations = convert_numpy_types(recommendations)
        for rec in converted_recommendations:
            if isinstance(rec.get('reasons'), str):
                rec['reasons'] = [rec['reasons']]
            elif not isinstance(rec.get('reasons'), list):
                rec['reasons'] = []
        
        return {
            "recommended_products": converted_recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
