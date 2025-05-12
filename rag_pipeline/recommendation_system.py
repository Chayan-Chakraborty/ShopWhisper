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
from config import PDF_PATH

class RecommendationSystem:
    def __init__(self, pdf_path: str = PDF_PATH):
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
        user_ids = list(range(1, 101))  # 100 users with IDs from 1 to 100
        
        for _ in range(1000):
            user_id = str(random.choice(user_ids))  # Convert to string for consistency
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
        # Handle both string and integer user IDs
        user_id = str(user_id).replace('USER_', '')  # Remove USER_ prefix if present
        return self.order_history[self.order_history['user_id'] == user_id].copy()
        
    def analyze_user_behavior(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's purchasing behavior using AI"""
        user_purchases = self.get_user_orders(user_id)
        return self.ai_analyzer.analyze_user_behavior(user_purchases)
    
    def get_recommendations(self, user_id: str, num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Get AI-powered product recommendations"""
        if self.products.empty:
            return []
            
        # Get user's behavior analysis
        user_analysis = self.analyze_user_behavior(user_id)
        
        if user_analysis["user_type"] == "new":
            return self._get_basic_recommendations(user_analysis, num_recommendations)
        
        try:
            # Get AI recommendations
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a retail recommendation expert."},
                    {"role": "user", "content": self.ai_analyzer.get_recommendation_prompt(
                        user_analysis,
                        self.products.to_dict('records')
                    )}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse AI recommendations
            ai_recommendations = json.loads(response.choices[0].message.content)
            
            # Convert to final format with multiple reasons
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
                    'reasons': rec['reasons'] if isinstance(rec['reasons'], list) else [rec['reasoning']]
                })
                
            return recommendations
            
        except Exception as e:
            print(f"Error getting AI recommendations: {str(e)}")
            # Fallback to basic recommendations
            return self._get_basic_recommendations(user_analysis, num_recommendations)
    
    def _get_basic_recommendations(self, user_analysis: Dict[str, Any], num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Fallback method for basic recommendations"""
        recommendations = []
        
        # Get product stats for scoring
        product_stats = self.order_history.groupby('product_id').agg({
            'order_id': 'count',
            'rating': ['mean', 'count']
        }).reset_index()
        product_stats.columns = ['product_id', 'order_count', 'avg_rating', 'rating_count']
        
        for _, product in self.products.iterrows():
            stats = product_stats[product_stats['product_id'] == product['ID']].iloc[0] if len(product_stats[product_stats['product_id'] == product['ID']]) > 0 else None
            reasons = []
            score = 0
            
            # Add popularity-based reasons
            if stats is not None:
                if stats['order_count'] > 100:
                    score += 2
                    reasons.append(f"Highly popular with {int(stats['order_count'])} recent orders")
                if stats['avg_rating'] >= 4.0 and stats['rating_count'] > 50:
                    score += 1.5
                    reasons.append(f"Highly rated with {stats['avg_rating']:.1f}/5 stars")
                elif stats['avg_rating'] >= 3.5 and stats['rating_count'] > 20:
                    score += 1
                    reasons.append(f"Well rated with {stats['avg_rating']:.1f}/5 stars")
            
            # Add category-based reasons
            if product['Category'] == 'Plywood':
                if product['Price'] < 1500:
                    reasons.append("Affordable plywood option")
                    score += 0.5
                elif product['Price'] >= 2000:
                    reasons.append("Premium quality plywood")
                    score += 0.5
            elif product['Category'] == 'Hardware':
                if product['Price'] < 50:
                    reasons.append("Essential hardware at competitive price")
                    score += 0.5
            
            # Add brand-based reasons
            if product['Brand'] in ['GreenPly', 'Century', 'Kitply']:
                reasons.append("From a trusted manufacturer")
                score += 0.5
            elif product['Brand'] in ['Hafele', 'Hettich']:
                reasons.append("Premium brand known for quality")
                score += 0.5
            
            # Add price-based reasons
            similar_products = self.products[self.products['Category'] == product['Category']]
            avg_price = similar_products['Price'].mean()
            if product['Price'] < avg_price * 0.8:
                reasons.append("Great value for money")
                score += 0.5
            
            if reasons:  # Only add products with at least one reason
                recommendations.append({
                    'product_id': product['ID'],
                    'product_name': product['Product_Name'],
                    'category': product['Category'],
                    'brand': product['Brand'],
                    'price': product['Price'],
                    'order_count': int(stats['order_count']) if stats is not None else 0,
                    'avg_rating': float(stats['avg_rating']) if stats is not None and not pd.isna(stats['avg_rating']) else None,
                    'confidence_score': min(score / 5, 1),  # Normalize to 0-1
                    'reasons': reasons
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