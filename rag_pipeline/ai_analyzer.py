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
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
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
                "recommendation_strategy": "Show popular products and trending items",
                "purchased_products": []
            }
            
        # Prepare order history for AI analysis
        orders_summary = []
        purchased_products = []
        
        for _, order in user_orders.iterrows():
            # Convert numpy types to Python native types
            quantity = int(order['quantity'])
            price = float(order['price_per_unit'])
            total = float(order['total_amount'])
            rating = float(order['rating']) if pd.notna(order['rating']) else None
            
            # Add to orders summary for AI analysis
            orders_summary.append({
                "product": str(order['product_name']),
                "category": str(order['category']),
                "brand": str(order['brand']),
                "price": price,
                "quantity": quantity,
                "date": str(order['order_date']),
                "rating": rating
            })
            
            # Add to purchased products list
            purchased_products.append({
                "order_id": str(order['order_id']),
                "product_name": str(order['product_name']),
                "category": str(order['category']),
                "brand": str(order['brand']),
                "quantity": quantity,
                "price_per_unit": price,
                "total_amount": total,
                "order_date": str(order['order_date']),
                "rating": rating
            })
            
        try:
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
            
            Return ONLY a valid JSON object in the following format:
            {{
                "user_type": "frequent",
                "insights": [
                    "Makes regular purchases of plywood products",
                    "Shows preference for premium brands"
                ],
                "preferences": {{
                    "preferred_categories": ["Plywood", "Hardware"],
                    "preferred_brands": ["GreenPly", "Century"],
                    "price_sensitivity": "medium",
                    "quality_preference": "high"
                }},
                "recommendation_strategy": "Focus on premium quality products in preferred categories"
            }}
            """
            
            # Get AI analysis using new OpenAI API format
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a retail analytics expert. Analyze customer behavior and return ONLY valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Get response content
            response_text = response.choices[0].message.content.strip()
            if not response_text:
                raise ValueError("Empty response from OpenAI API")
                
            # Parse AI response
            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"Failed to parse OpenAI response: {response_text}")
                raise ValueError(f"Invalid JSON in OpenAI response: {str(e)}")
            
            # Add additional metrics and purchased products
            analysis.update({
                "total_spent": float(user_orders['total_amount'].sum()),
                "average_order_value": float(user_orders['total_amount'].mean()),
                "total_orders": int(len(user_orders)),
                "average_rating": float(user_orders['rating'].mean()) if user_orders['rating'].notna().any() else None,
                "purchased_products": sorted(purchased_products, key=lambda x: x['order_date'], reverse=True)  # Most recent first
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
        
        Return ONLY a valid JSON object in the following format:
        {{
            "recommendations": [
                {{
                    "product_id": "1",
                    "reasoning": "Matches user's preference for premium plywood",
                    "confidence_score": 0.95
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
        purchased_products = []
        for _, order in user_orders.iterrows():
            # Convert numpy types to Python native types
            quantity = int(order['quantity'])
            price = float(order['price_per_unit'])
            total = float(order['total_amount'])
            rating = float(order['rating']) if pd.notna(order['rating']) else None
            
            purchased_products.append({
                "order_id": str(order['order_id']),
                "product_name": str(order['product_name']),
                "category": str(order['category']),
                "brand": str(order['brand']),
                "quantity": quantity,
                "price_per_unit": price,
                "total_amount": total,
                "order_date": str(order['order_date']),
                "rating": rating
            })
            
        return {
            "user_type": "frequent" if len(user_orders) > 5 else "occasional",
            "insights": [
                f"Made {len(user_orders)} purchases",
                f"Spent total of {float(user_orders['total_amount'].sum()):.2f}"
            ],
            "preferences": {
                "preferred_categories": user_orders['category'].value_counts().index.tolist()[:3],
                "preferred_brands": user_orders['brand'].value_counts().index.tolist()[:3],
                "price_sensitivity": "medium",
                "quality_preference": "medium"
            },
            "recommendation_strategy": "Based on most purchased categories and brands",
            "purchased_products": sorted(purchased_products, key=lambda x: x['order_date'], reverse=True)  # Most recent first
        } 