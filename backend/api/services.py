import openai
from django.conf import settings
from .models import Product
import logging
import random
import re

logger = logging.getLogger(__name__)

class AIRecommendationService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    def get_recommendation(self, user_message, conversation_history=None):
        """
        Get AI-powered product recommendations
        """
        if self.client and settings.OPENAI_API_KEY:
            return self._get_openai_recommendation(user_message, conversation_history)
        else:
            return self._get_fallback_recommendation(user_message)
    
    def _get_openai_recommendation(self, user_message, conversation_history):
        """
        Get recommendations using OpenAI API
        """
        try:
            # Get all products for context
            products = Product.objects.all()
            product_context = []
            
            for product in products:
                product_context.append({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': float(product.price),
                    'category': product.category,
                    'tags': product.tags
                })
            
            # Build conversation context
            messages = [
                {
                    "role": "system",
                    "content": f"""You are an AI shopping assistant for an ecommerce platform. 
                    Your job is to recommend products based on user queries.
                    
                    Available products: {product_context}
                    
                    Rules:
                    1. Always respond in a friendly, helpful manner
                    2. Recommend 3-5 products that best match the user's request
                    3. Provide brief justifications for your recommendations
                    4. Return your response in this exact JSON format:
                    {{
                        "response": "Your natural language response here",
                        "products": [list of product IDs as integers]
                    }}
                    
                    Example response:
                    {{
                        "response": "I'd be happy to help you find the perfect product! Based on what you're looking for, here are my top recommendations:",
                        "products": [1, 5, 12, 8]
                    }}"""
                }
            ]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-6:]:  # Last 6 messages for context
                    messages.append({
                        "role": "user" if msg.get('type') == 'user' else "assistant",
                        "content": msg.get('content', '')
                    })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            # Parse the response
            response_content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            import json
            try:
                # Look for JSON in the response
                json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return {
                        'response': result.get('response', response_content),
                        'products': result.get('products', [])
                    }
            except json.JSONDecodeError:
                pass
            
            # Fallback if JSON parsing fails
            return self._get_fallback_recommendation(user_message)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._get_fallback_recommendation(user_message)
    
    def _get_fallback_recommendation(self, user_message):
        """
        Fallback recommendation system when OpenAI is not available
        """
        # Simple keyword matching
        keywords = user_message.lower().split()
        
        # Find relevant products
        relevant_products = []
        all_products = list(Product.objects.all())
        
        for product in all_products:
            score = 0
            search_text = f"{product.name} {product.description} {' '.join(product.tags)}".lower()
            
            for keyword in keywords:
                if keyword in search_text:
                    score += 1
            
            if score > 0:
                relevant_products.append((product, score))
        
        # Sort by relevance and take top 5
        relevant_products.sort(key=lambda x: x[1], reverse=True)
        recommended_products = [p[0] for p in relevant_products[:5]]
        
        # If no relevant products found, return random selection
        if not recommended_products:
            recommended_products = random.sample(all_products, min(4, len(all_products)))
        
        # Generate response
        responses = [
            "I'd be happy to help you find the perfect product! Based on what you're looking for, here are my top recommendations:",
            "Great choice! I've found some fantastic options that match your needs perfectly:",
            "Excellent! Let me show you some products I think you'll love:",
            "Perfect! I've curated these items specifically for you:",
            "Wonderful! Here are some great options that fit your criteria:",
        ]
        
        return {
            'response': random.choice(responses),
            'products': [p.id for p in recommended_products]
        }