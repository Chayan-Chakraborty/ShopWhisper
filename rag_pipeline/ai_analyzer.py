import openai
import pandas as pd
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
import json
from config import OPENAI_API_KEY

load_dotenv()  # Load environment variables from .env file

class AIAnalyzer:
    def __init__(self):
        """Initialize the AI analyzer with OpenAI client"""
        openai.api_key = OPENAI_API_KEY
        
    def analyze_user_behavior(self, user_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze user behavior using AI to generate insights
        
        Args:
            user_orders: DataFrame containing user's order history
            
        Returns:
            Dictionary containing AI-generated insights and recommendations
        """
        if user_orders.empty:
            return {
                "user_type": "new",
                "insights": [],
                "preferences": {},
                "recommendation_strategy": "Show popular products and trending items"
            }
            
        # Prepare order history for AI analysis
        orders_summary = []
        for _, order in user_orders.iterrows():
            orders_summary.append({
                "product": order['product_name'],
                "category": order['category'],
                "brand": order['brand'],
                "price": float(order['price_per_unit']),
                "quantity": int(order['quantity']),
                "date": order['order_date'],
                "rating": float(order['rating']) if pd.notna(order['rating']) else None
            })
            
        # Create prompt for AI analysis
        prompt = f"""
        Analyze this user's purchase history and provide detailed insights:
        
        Order History:
        {json.dumps(orders_summary, indent=2)}
        
        Please analyze:
        1. Shopping patterns and preferences
        2. Price sensitivity
        3. Brand loyalty
        4. Category interests
        5. Potential future needs
        6. Recommended product types
        
        Provide the analysis in the following JSON format:
        {{
            "user_type": "type of shopper (frequent/occasional/new)",
            "insights": ["list of key insights"],
            "preferences": {{
                "preferred_categories": ["list"],
                "preferred_brands": ["list"],
                "price_sensitivity": "low/medium/high",
                "quality_preference": "low/medium/high"
            }},
            "recommendation_strategy": "strategy for recommendations"
        }}
        """
        
        try:
            # Get AI analysis
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a retail analytics expert analyzing customer purchase behavior."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse AI response
            analysis = json.loads(response.choices[0].message.content)
            
            # Add additional metrics
            analysis.update({
                "total_spent": user_orders['total_amount'].sum(),
                "average_order_value": user_orders['total_amount'].mean(),
                "total_orders": len(user_orders),
                "average_rating": user_orders['rating'].mean() if user_orders['rating'].notna().any() else None
            })
            
            return analysis
            
        except Exception as e:
            print(f"Error in AI analysis: {str(e)}")
            # Fallback to basic analysis
            return self._basic_analysis(user_orders)
            
    def get_recommendation_prompt(self, user_analysis: Dict[str, Any], available_products: List[Dict[str, Any]]) -> str:
        """
        Generate a prompt for AI to recommend products
        """
        return f"""
        Based on this user analysis:
        {json.dumps(user_analysis, indent=2)}
        
        And these available products:
        {json.dumps(available_products, indent=2)}
        
        Recommend 5 products with reasoning. Format as JSON:
        {{
            "recommendations": [
                {{
                    "product_id": "id",
                    "reasoning": "detailed explanation",
                    "confidence_score": 0-1
                }}
            ]
        }}
        
        Consider:
        1. User's preferred categories and brands
        2. Price sensitivity
        3. Quality preferences
        4. Past purchase patterns
        5. Potential future needs
        """
        
    def _basic_analysis(self, user_orders: pd.DataFrame) -> Dict[str, Any]:
        """Fallback basic analysis when AI analysis fails"""
        return {
            "user_type": "frequent" if len(user_orders) > 5 else "occasional",
            "insights": [
                f"Made {len(user_orders)} purchases",
                f"Spent total of {user_orders['total_amount'].sum():.2f}"
            ],
            "preferences": {
                "preferred_categories": user_orders['category'].value_counts().index.tolist()[:3],
                "preferred_brands": user_orders['brand'].value_counts().index.tolist()[:3],
                "price_sensitivity": "medium",
                "quality_preference": "medium"
            },
            "recommendation_strategy": "Based on most purchased categories and brands"
        } 