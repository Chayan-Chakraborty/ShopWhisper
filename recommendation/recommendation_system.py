import pandas as pd
import numpy as np
from collections import defaultdict
from typing import List, Dict, Any
from pdf_processor import get_products
from datetime import datetime, timedelta
import random
from ai_analyzer import AIAnalyzer
import json
import openai

class RecommendationSystem:
    def __init__(self, pdf_path: str = "products.pdf"):
        try:
            # Get products from PDF
            products_list = get_products(pdf_path)
            self.products = pd.DataFrame(products_list)
        except FileNotFoundError:
            print(f"Warning: Products PDF not found at {pdf_path}. Using empty product list.")
            self.products = pd.DataFrame([])
            
        # Initialize in-memory order history
        self.order_history = self._generate_dummy_orders()
        
        # Initialize AI analyzer
        self.ai_analyzer = AIAnalyzer()
        
    def _generate_dummy_orders(self) -> pd.DataFrame:
        """Generate dummy order history data"""
        if self.products.empty:
            return pd.DataFrame()
            
        orders = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Generate 1000 random orders
        user_ids = [f"USER_{i}" for i in range(1, 101)]  # 100 users
        
        for _ in range(1000):
            user_id = random.choice(user_ids)
            product = self.products.iloc[random.randint(0, len(self.products)-1)]
            
            # Generate order date
            order_date = start_date + timedelta(days=random.randint(0, 365))
            
            # Generate quantity based on category
            if product['Category'] in ['Hardware', 'Adhesive']:
                quantity = random.randint(1, 10)
            else:
                quantity = random.randint(1, 3)
                
            # Calculate total amount
            total_amount = float(product['Price']) * quantity
            
            # Generate rating (70% of orders have ratings)
            rating = random.choice([None] + [i/2 for i in range(6, 11)]) if random.random() > 0.3 else None
            
            order = {
                'order_id': f"ORD_{len(orders)+1}",
                'user_id': user_id,
                'product_id': product['ID'],
                'product_name': product['Product_Name'],
                'category': product['Category'],
                'sub_category': product['Sub_Category'],
                'brand': product['Brand'],
                'quantity': quantity,
                'price_per_unit': product['Price'],
                'total_amount': total_amount,
                'order_date': order_date.strftime("%Y-%m-%d"),
                'rating': rating
            }
            orders.append(order)
        
        return pd.DataFrame(orders)
        
    def get_user_orders(self, user_id: str) -> pd.DataFrame:
        """Get order history for a specific user"""
        return self.order_history[self.order_history['user_id'] == user_id].copy()
        
    def analyze_user_behavior(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's purchasing behavior using AI"""
        user_purchases = self.get_user_orders(user_id)
        return self.ai_analyzer.analyze_user_behavior(user_purchases)
    
    def get_recommendations(self, user_id: str, num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Get AI-powered product recommendations"""
        if self.products.empty:
            return []
            
        # Get AI analysis of user behavior
        user_analysis = self.analyze_user_behavior(user_id)
        
        if user_analysis["user_type"] == "new":
            return self.get_popular_products(num_recommendations)
        
        try:
            # Get AI recommendations
            prompt = self.ai_analyzer.get_recommendation_prompt(
                user_analysis,
                self.products.to_dict('records')
            )
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a retail recommendation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse AI recommendations
            ai_recommendations = json.loads(response.choices[0].message.content)
            
            # Convert to final format
            recommendations = []
            for rec in ai_recommendations["recommendations"][:num_recommendations]:
                product = self.products[self.products['ID'] == int(rec['product_id'])].iloc[0]
                recommendations.append({
                    'product_id': product['ID'],
                    'product_name': product['Product_Name'],
                    'category': product['Category'],
                    'brand': product['Brand'],
                    'price': product['Price'],
                    'confidence_score': rec['confidence_score'],
                    'reason': rec['reasoning']
                })
                
            return recommendations
            
        except Exception as e:
            print(f"Error getting AI recommendations: {str(e)}")
            # Fallback to basic recommendations
            return self._get_basic_recommendations(user_analysis, num_recommendations)
    
    def _get_basic_recommendations(self, user_analysis: Dict[str, Any], num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Fallback method for basic recommendations"""
        recommendations = []
        preferred_categories = user_analysis['preferences'].get('preferred_categories', [])
        preferred_brands = user_analysis['preferences'].get('preferred_brands', [])
        
        for _, product in self.products.iterrows():
            score = 0
            reasons = []
            
            if product['Category'] in preferred_categories:
                score += 2
                reasons.append(f"Matches your preferred category: {product['Category']}")
                
            if product['Brand'] in preferred_brands:
                score += 1
                reasons.append(f"From your preferred brand: {product['Brand']}")
                
            recommendations.append({
                'product_id': product['ID'],
                'product_name': product['Product_Name'],
                'category': product['Category'],
                'brand': product['Brand'],
                'price': product['Price'],
                'confidence_score': min(score / 3, 1),  # Normalize to 0-1
                'reason': " • ".join(reasons) if reasons else "Based on your shopping patterns"
            })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)
        return recommendations[:num_recommendations]
    
    def get_popular_products(self, num_products: int = 5) -> List[Dict[str, Any]]:
        """Get popular products based on all users' order history"""
        if self.products.empty or self.order_history.empty:
            return []
            
        # Calculate product popularity based on order count and ratings
        product_stats = self.order_history.groupby('product_id').agg({
            'order_id': 'count',
            'rating': 'mean'
        }).reset_index()
        
        product_stats.columns = ['product_id', 'order_count', 'avg_rating']
        
        # Sort by order count and average rating
        product_stats = product_stats.sort_values(
            ['order_count', 'avg_rating'],
            ascending=[False, False]
        )
        
        # Get top products
        popular_products = []
        for _, stat in product_stats.head(num_products).iterrows():
            product = self.products[self.products['ID'] == stat['product_id']].iloc[0]
            popular_products.append({
                'product_id': product['ID'],
                'product_name': product['Product_Name'],
                'category': product['Category'],
                'brand': product['Brand'],
                'price': product['Price'],
                'order_count': int(stat['order_count']),
                'avg_rating': round(stat['avg_rating'], 1) if not pd.isna(stat['avg_rating']) else None,
                'reason': "Popular product with high customer satisfaction"
            })
            
        return popular_products 