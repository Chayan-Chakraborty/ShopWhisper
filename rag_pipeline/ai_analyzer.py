from openai import OpenAI
import pandas as pd
from typing import Dict, Any, List
import json
from config import OPENAI_API_KEY
from pydantic import BaseModel

client = OpenAI(api_key=OPENAI_API_KEY)

class AIAnalyzer:
    def analyze_user_behavior(self, user_orders: pd.DataFrame) -> Dict[str, Any]:
        if user_orders.empty:
            return {
                "user_type": "new",
                "insights": [],
                "preferences": {},
                "recommendation_strategy": "Show popular products and trending items",
                "purchased_products": []
            }

        orders_summary = []
        purchased_products = []

        for _, order in user_orders.iterrows():
            quantity = int(order['quantity'])
            price = float(order['price_per_unit'])
            total = float(order['total_amount'])
            rating = float(order['rating']) if pd.notna(order['rating']) else None

            orders_summary.append({
                "product": str(order['product_name']),
                "category": str(order['category']),
                "brand": str(order['brand']),
                "price": price,
                "quantity": quantity,
                "date": str(order['order_date']),
                "rating": rating
            })

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
                "insights": ["Makes regular purchases of plywood products"],
                "preferences": {{
                    "preferred_categories": ["Plywood", "Hardware"],
                    "preferred_brands": ["GreenPly", "Century"],
                    "price_sensitivity": "medium",
                    "quality_preference": "high"
                }},
                "recommendation_strategy": "Focus on premium quality products in preferred categories"
            }}
            """

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a retail analytics expert. Analyze customer behavior and return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            response_text = response.choices[0].message.content.strip()
            if not response_text:
                raise ValueError("Empty response from OpenAI API")

            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"Failed to parse OpenAI response: {response_text}")
                raise ValueError(f"Invalid JSON in OpenAI response: {str(e)}")

            analysis.update({
                "total_spent": float(user_orders['total_amount'].sum()),
                "average_order_value": float(user_orders['total_amount'].mean()),
                "total_orders": int(len(user_orders)),
                "average_rating": float(user_orders['rating'].mean()) if user_orders['rating'].notna().any() else None,
                "purchased_products": sorted(purchased_products, key=lambda x: x['order_date'], reverse=True)
            })

            return analysis

        except Exception as e:
            print(f"Error in AI analysis: {str(e)}")
            return self._basic_analysis(user_orders)
        

    class UserAnalysis(BaseModel):
        product_id: int
        product_name: str
        category: str
        brand: str
        price: float
        rating: float
        discount: str
        stock: int
        confidence_score: float
        reasons: List[str]

    def get_recommendation_prompt(self, user_analysis: Dict[str, Any], available_products: List[Dict[str, Any]]) -> UserAnalysis:
        return f"""
        Based on this user analysis:
        {json.dumps(user_analysis, indent=2)}

        And these available products:
        {json.dumps(available_products, indent=2)}

        Strictly Return JSON object in the following format:
        {{
            "recommendations": [
                {{
                    "product_id": "1",
                     "product_name": "Anti-Termite Adhesive 1kg",
                    "category": "Adhesive",
                    "brand": "Fevicol",
                    "price": 28,
                    "rating": 4.7,
                    "discount": "0%",
                    "stock": 80,
                    "confidence_score": 0.3,
                    "reasons": [
                "Excellent customer rating of 4.7/5"
                }}
            ]
        }}

        Strictly follow the format and data types.

        "product_id": 8,
            "product_name": "Anti-Termite Adhesive 1kg",
            "category": "Adhesive",
            "brand": "Fevicol",
            "price": 28,
            "rating": 4.7,
            "discount": "0%",
            "stock": 80,
            "confidence_score": 0.3,
            "reasons": [
                "Excellent customer rating of 4.7/5"
        ]

        Maintain consistent data types for each field.

        Important:
        1. The 'reasons' field must be a list of strings
        2. Each recommendation must have at least one reason
        3. Product IDs must match the available products
        4. Confidence scores should be between 0 and 1
        """

    def _basic_analysis(self, user_orders: pd.DataFrame) -> Dict[str, Any]:
        purchased_products = []
        for _, order in user_orders.iterrows():
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
            "purchased_products": sorted(purchased_products, key=lambda x: x['order_date'], reverse=True)
        }
