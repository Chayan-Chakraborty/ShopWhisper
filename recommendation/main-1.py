from fastapi import FastAPI, HTTPException, Header
from typing import List, Dict, Any, Optional
from rag_pipeline.recommendation_system import RecommendationSystem
import uvicorn

app = FastAPI(title="Product Recommendation API",
             description="API for analyzing user behavior and getting product recommendations")

# Initialize the recommendation system
recommendation_system = RecommendationSystem()

@app.get("/")
async def root():
    return {"message": "Welcome to the Product Recommendation API"}

@app.get("/user/behavior", response_model=Dict[str, Any])
async def get_user_behavior(user_id: Optional[str] = Header(None)):
    """Get analysis of user's purchasing behavior"""
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required in headers")
        
    try:
        behavior = recommendation_system.analyze_user_behavior(user_id)
        return behavior
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
    uvicorn.run(app, host="0.0.0.0", port=8000) 