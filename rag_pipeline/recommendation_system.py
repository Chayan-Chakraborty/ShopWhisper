import pandas as pd
import numpy as np
from collections import defaultdict
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
from ai_analyzer import AIAnalyzer
import json
from openai import OpenAI
from config import OPENAI_API_KEY
from config import PDF_PATH

class RecommendationSystem:
    def __init__(self, data_path: str = PDF_PATH):
        try:
            # Load products directly from CSV
            print("Loading products from CSV...")
            self.products = pd.read_csv(data_path)
            print(f"Loaded {len(self.products)} products")
            
            # Initialize in-memory order history
            print("Generating dummy orders...")
            self.order_history = self._generate_dummy_orders()
            print(f"Generated {len(self.order_history)} orders")
            
        except FileNotFoundError:
            print(f"Warning: Products CSV not found at {data_path}. Using empty product list.")
            self.products = pd.DataFrame([])
            
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
                'product_name': product['Product Name'],
                'category': product['Category'],
                'sub_category': product['Sub-Category'],
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
        print(f"Getting recommendations for user {user_id}")
        
        if self.products.empty:
            print("No products available")
            return []
            
        # Get user's behavior analysis
        user_analysis = self.analyze_user_behavior(user_id)
        print(f"User analysis: {user_analysis}")
        
        if user_analysis["user_type"] == "new":
            print("New user, getting basic recommendations")
            recommendations = self._get_basic_recommendations(user_analysis, num_recommendations)
            print(f"Generated {len(recommendations)} basic recommendations")
            return recommendations
        
        try:
            print("Getting AI recommendations")
            # Get AI recommendations
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a retail recommendation expert."},
                    {"role": "user", "content": self.ai_analyzer.get_recommendation_prompt(
                        user_analysis,
                        self.products.to_dict('records')
                    )}
                ]
            )
            
            # Parse AI recommendations
            ai_recommendations = json.loads(response.choices[0].message.content)
            print(f"Got {len(ai_recommendations.get('recommendations', []))} AI recommendations")
            
            # Convert to final format with multiple reasons
            recommendations = []
            for rec in ai_recommendations["recommendations"][:num_recommendations]:
                try:
                    product = self.products[self.products['ID'] == int(rec['product_id'])].iloc[0]
                    
                    # Ensure reasons is a list
                    reasons = rec.get('reasons', [])
                    if isinstance(reasons, str):
                        reasons = [reasons]
                    elif not isinstance(reasons, list):
                        reasons = [str(reasons)]
                    
                    recommendations.append({
                        'product_id': product['ID'],
                        'product_name': product['Product Name'],
                        'category': product['Category'],
                        'brand': product['Brand'],
                        'price': product['Price'],
                        'confidence_score': float(rec.get('confidence_score', 0.5)),
                        'reasons': reasons
                    })
                except (KeyError, ValueError, IndexError) as e:
                    print(f"Error processing recommendation: {str(e)}")
                    continue
            
            if not recommendations:
                raise ValueError("No valid recommendations generated")
                
            print(f"Returning {len(recommendations)} AI recommendations")
            return recommendations
            
        except Exception as e:
            print(f"Error getting AI recommendations: {str(e)}")
            print("Falling back to basic recommendations")
            # Fallback to basic recommendations
            recommendations = self._get_basic_recommendations(user_analysis, num_recommendations)
            print(f"Generated {len(recommendations)} fallback recommendations")
            return recommendations
    
    def _get_basic_recommendations(self, user_analysis: Dict[str, Any], num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Fallback method for basic recommendations"""
        print("Starting basic recommendations")
        recommendations = []
        
        if self.products.empty:
            print("No products available for basic recommendations")
            return []
            
        if self.order_history.empty:
            print("No order history available for basic recommendations")
            return []
        
        # Get product stats for scoring
        product_stats = self.order_history.groupby('product_id').agg({
            'order_id': 'count',
            'rating': ['mean', 'count']
        }).reset_index()
        product_stats.columns = ['product_id', 'order_count', 'avg_rating', 'rating_count']
        print(f"Calculated stats for {len(product_stats)} products")
        
        # Get user preferences from analysis
        preferred_categories = user_analysis.get('preferences', {}).get('preferred_categories', [])
        preferred_brands = user_analysis.get('preferences', {}).get('preferred_brands', [])
        price_sensitivity = user_analysis.get('preferences', {}).get('price_sensitivity', 'medium')
        quality_preference = user_analysis.get('preferences', {}).get('quality_preference', 'medium')
        
        # Get user's purchased products to avoid immediate repeats
        purchased_products = {item['product_name'] for item in user_analysis.get('purchased_products', [])}
        
        for _, product in self.products.iterrows():
            # Skip if user recently purchased this product
            if product['Product Name'] in purchased_products:
                continue
                
            stats = product_stats[product_stats['product_id'] == product['ID']].iloc[0] if len(product_stats[product_stats['product_id'] == product['ID']]) > 0 else None
            reasons = []
            score = 0
            
            # Add category preference reasons
            if product['Category'] in preferred_categories:
                score += 2
                reasons.append(f"Matches your frequently purchased category: {product['Category']}")
            
            # Add brand preference reasons
            if product['Brand'] in preferred_brands:
                score += 1.5
                reasons.append(f"From {product['Brand']}, one of your preferred brands")
            
            # Add rating-based reasons
            if product['Rating'] >= 4.5:
                score += 1.5
                reasons.append(f"Excellent customer rating of {product['Rating']}/5")
            elif product['Rating'] >= 4.0:
                score += 1
                reasons.append(f"High customer rating of {product['Rating']}/5")
            
            # Add price sensitivity based reasons
            avg_category_price = self.products[self.products['Category'] == product['Category']]['Price'].mean()
            if price_sensitivity == 'high' and product['Price'] < avg_category_price:
                score += 1
                reasons.append("Competitively priced for its category")
            elif price_sensitivity == 'low' and product['Price'] > avg_category_price:
                score += 1
                reasons.append("Premium quality product")
            
            # Add quality preference based reasons
            if quality_preference == 'high':
                if product['Rating'] >= 4.5:
                    score += 1
                    reasons.append("Meets your preference for high-quality products")
                if product['Brand'] in ['GreenPly', 'Century', 'Kitply', 'Hafele', 'Hettich']:
                    score += 0.5
                    reasons.append("From a premium quality manufacturer")
            
            # Add category-specific features
            if product['Category'] == 'Plywood':
                if product['Waterproof'] == 'Yes':
                    reasons.append("Waterproof plywood suitable for wet areas")
                    score += 0.5
                if product['Termite-Proof'] == 'Yes':
                    reasons.append("Termite-resistant for longer life")
                    score += 0.5
            elif product['Category'] == 'Hardware':
                if product['Price'] < 50:
                    reasons.append("Essential hardware at competitive price")
                    score += 0.5
            
            # Add discount-based reasons
            if product['Discount'] != '0%':
                reasons.append(f"Special {product['Discount']} discount available")
                score += 0.5
            
            # Add stock-based reasons
            if product['Stock'] < 50:
                reasons.append("Limited stock available")
                score += 0.3
            
            if reasons:  # Only add products with at least one reason
                recommendations.append({
                    'product_id': product['ID'],
                    'product_name': product['Product Name'],
                    'category': product['Category'],
                    'brand': product['Brand'],
                    'price': product['Price'],
                    'rating': float(product['Rating']),
                    'discount': product['Discount'],
                    'stock': int(product['Stock']),
                    'confidence_score': min(score / 5, 1),  # Normalize to 0-1
                    'reasons': reasons
                })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)
        print(f"Generated {len(recommendations)} recommendations before filtering")
        final_recommendations = recommendations[:num_recommendations]
        print(f"Returning {len(final_recommendations)} final recommendations")
        return final_recommendations
    
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