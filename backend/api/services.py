import openai
from django.conf import settings
from .models import Product
import logging
import random
import re
import requests
import json
import time
from urllib.parse import urlparse
from .rag import semantic_search

logger = logging.getLogger(__name__)

# Create dedicated logger for AI recommendation debugging
ai_logger = logging.getLogger('ai_debug')
ai_logger.setLevel(logging.DEBUG)

# Create dedicated logger for OpenRouter connectivity debugging
openrouter_logger = logging.getLogger('openrouter_debug')
openrouter_logger.setLevel(logging.DEBUG)

# Create file handler for AI logs
if not ai_logger.handlers:
    import os
    log_dir = '/app' if os.path.exists('/app') else '/tmp'
    handler = logging.FileHandler(f'{log_dir}/ai_debug.log')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    ai_logger.addHandler(handler)

# Create file handler for OpenRouter logs
if not openrouter_logger.handlers:
    import os
    log_dir = '/app' if os.path.exists('/app') else '/tmp'
    handler = logging.FileHandler(f'{log_dir}/openrouter_debug.log')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    openrouter_logger.addHandler(handler)

class AIRecommendationService:
    def __init__(self):
        # Configure for OpenRouter API with token rotation
        self.openrouter_model = getattr(settings, 'OPENROUTER_MODEL', 'deepseek/deepseek-r1:free')
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        
        # Load all available OpenRouter API keys for rotation
        self.openrouter_api_keys = []
        for i in range(1, 11):  # Keys 1-10
            key = getattr(settings, f'OPENROUTER_API_KEY_{i}', None)
            if key:
                self.openrouter_api_keys.append(key)
        
        # Also include the main key if present
        main_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        if main_key and main_key not in self.openrouter_api_keys:
            self.openrouter_api_keys.insert(0, main_key)
        
        if self.openrouter_api_keys:
            openrouter_logger.info(f"🔧 OpenRouter configured with {len(self.openrouter_api_keys)} API keys and model: {self.openrouter_model}")
            openrouter_logger.info(f"🔧 Base URL: {self.openrouter_base_url}")
            # Log masked API keys for debugging
            for i, key in enumerate(self.openrouter_api_keys, 1):
                masked_key = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "[INVALID_KEY]"
                openrouter_logger.info(f"🔑 API Key {i}: {masked_key}")
            self.client = "openrouter"  # Flag to indicate OpenRouter is available
            
            # Test network connectivity to OpenRouter
            self._test_openrouter_connectivity()
        else:
            openrouter_logger.error("❌ No OpenRouter API keys found in settings!")
            self.client = None
    
    def get_recommendation(self, user_message, conversation_history=None):
        """
        Get AI-powered product recommendations
        """
        if self.client == "openrouter":
            return self._get_openrouter_recommendation(user_message, conversation_history)
        else:
            return self._get_fallback_recommendation(user_message)
    
    def _get_openrouter_recommendation(self, user_message, conversation_history):
        """
        Get recommendations using OpenRouter API
        """
        ai_logger.info(f"Starting OpenRouter recommendation for message: '{user_message}'")
        
        try:
            # RAG: retrieve most relevant products for the user_message
            ai_logger.info(f"Starting RAG semantic search for: '{user_message}'")
            top_ids = semantic_search(user_message, top_k=12)
            ai_logger.info(f"RAG semantic search returned {len(top_ids)} product IDs: {top_ids}")
            
            if top_ids:
                # Convert string IDs to ObjectId for MongoDB querying
                from bson import ObjectId
                try:
                    object_ids = [ObjectId(pid) for pid in top_ids if pid]
                    retrieved = list(Product.objects.filter(_id__in=object_ids))
                    ai_logger.info(f"Retrieved {len(retrieved)} products from database using {len(object_ids)} RAG ObjectIDs")
                except Exception as e:
                    ai_logger.error(f"Error converting RAG IDs to ObjectId: {e}")
                    retrieved = list(Product.objects.all()[:20])
                    ai_logger.warning(f"ObjectId conversion failed, using fallback: first 20 products")
            else:
                retrieved = list(Product.objects.all()[:20])
                ai_logger.warning(f"RAG returned no results, using fallback: first 20 products")
            
            product_context = []
            for product in retrieved:
                try:
                    price_value = float(str(product.price))
                except (ValueError, TypeError):
                    price_value = 0.0
                    ai_logger.warning(f"Failed to parse price for product {product.pk}: {product.price}")
                
                product_data = {
                    'id': str(product.pk),  # Use string IDs for MongoDB
                    'name': product.name,
                    'description': product.description,
                    'price': price_value,
                    'category': product.category,
                    'tags': product.tags,
                }
                product_context.append(product_data)
                ai_logger.debug(f"Added product to context: {product.pk} - {product.name}")
            
            ai_logger.info(f"Built product context with {len(product_context)} products")
            
            # Build conversation context
            messages = [
                {
                    "role": "system",
                    "content": f"""You are an expert AI shopping consultant for a premium e-commerce platform. Your mission is to understand customer needs and recommend products that perfectly match their specific requirements, budget, and shopping intent.

**CONVERSATION CONTEXT TRACKING:**
- ALWAYS pay attention to previous conversation history to understand context
- For follow-up requests (e.g., "cheaper", "smaller", "different color"), maintain the SAME product category from previous recommendations
- When users say "cheaper", "less expensive", or mention price concerns, find similar products in the SAME category with lower prices
- When users say "something else" or "different", stay within the SAME category unless they explicitly specify a new category
- Track user preferences and constraints mentioned earlier in the conversation

**AVAILABLE PRODUCT INVENTORY:**
{product_context}

**CONVERSATION CONTINUITY RULES:**
1. **Context Memory**: Remember what the user was previously looking at (category, type, price range)
2. **Follow-up Handling**: 
   - "cheaper T-shirt" → find T-shirts with lower prices than previously shown
   - "different jacket" → find other jackets, not unrelated items
   - "something under $50" → filter current category by price constraint
3. **Category Consistency**: Maintain product category unless user explicitly changes topic
4. **Price Refinement**: When users mention budget concerns, adjust recommendations within the same category

**PRODUCT MATCHING PROTOCOL:**
1. **Context First**: Check conversation history for category/type continuity
2. **Primary Match**: User's exact request (e.g., "gaming laptop" → only laptops suitable for gaming)
3. **Intent Analysis**: Consider use case, occasion, recipient (work, personal, gift, etc.)
4. **Feature Alignment**: Match specific requirements (budget, size, color, performance)
5. **Category Discipline**: NEVER cross categories unless explicitly requested

**STRICT REJECTION RULES:**
- DO NOT recommend products from different categories unless user explicitly changes topic
- DO NOT suggest items that don't match the established conversation context
- DO NOT include products just to fill quota - quality over quantity
- DO NOT ignore previous conversation when handling follow-up requests

**RESPONSE REQUIREMENTS:**
1. Provide 1-3 highly relevant products (never more unless specifically requested)
2. Reference previous conversation when relevant ("Based on your interest in T-shirts...")
3. Explain WHY each product fits their updated requirements
4. Use confident, consultative language that shows context awareness
5. Include price context, especially for follow-up price-related requests

**MANDATORY JSON FORMAT:**
```json
{{
    "response": "Based on [previous context + current request], I recommend these perfectly matched options: [brief explanation of why these specific products solve their problem]",
    "products": ["product_id_1", "product_id_2"]
}}
```

**CONTEXT-AWARE EXAMPLES:**

Initial: "I need a T-shirt"
Response: "I recommend the Classic White T-shirt - comfortable cotton perfect for everyday wear."

Follow-up: "something cheaper"
Response: "Based on your interest in T-shirts, here are more budget-friendly options: [cheaper T-shirt recommendations]"

Follow-up: "different color"  
Response: "Since you're looking at T-shirts, here are other color options: [T-shirt in different colors]"

**Remember**: You're a trusted advisor with perfect memory. Always consider the conversation flow and maintain context continuity."""
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
            
            # Try each API key until one works (token rotation)
            payload = {
                "model": self.openrouter_model,
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            openrouter_logger.info(f"🚀 Attempting OpenRouter request with {len(self.openrouter_api_keys)} available tokens")
            import json as json_module
            openrouter_logger.debug(f"📝 Request payload: {json_module.dumps(payload, indent=2)[:500]}...")
            
            # Log network connectivity check
            self._check_network_connectivity()
            
            for i, api_key in enumerate(self.openrouter_api_keys, 1):
                try:
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost",
                        "X-Title": "SellerAgent E-commerce"
                    }
                    
                    masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "[INVALID_KEY]"
                    openrouter_logger.info(f"🔑 Trying token {i}/{len(self.openrouter_api_keys)}: {masked_key}")
                    import json as json_module
                    openrouter_logger.debug(f"📋 Request headers: {json_module.dumps({k: v if k != 'Authorization' else f'Bearer {masked_key}' for k, v in headers.items()}, indent=2)}")
                    
                    # Log request timing
                    start_time = time.time()
                    openrouter_logger.info(f"⏱️ Starting request to {self.openrouter_base_url}/chat/completions at {time.strftime('%H:%M:%S')}")
                    
                    response = requests.post(
                        f"{self.openrouter_base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    
                    request_duration = time.time() - start_time
                    openrouter_logger.info(f"⏱️ Request completed in {request_duration:.2f}s with status: {response.status_code}")
                    
                    # Log response headers for debugging
                    openrouter_logger.debug(f"📥 Response headers: {dict(response.headers)}")
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        response_content = response_data['choices'][0]['message']['content'].strip()
                        openrouter_logger.info(f"✅ SUCCESS with token {i}! Response length: {len(response_content)} chars")
                        openrouter_logger.debug(f"📄 AI response preview: {response_content[:200]}...")
                        
                        # Log usage info if available
                        if 'usage' in response_data:
                            usage = response_data['usage']
                            openrouter_logger.info(f"📊 Token usage - Prompt: {usage.get('prompt_tokens', 'N/A')}, Completion: {usage.get('completion_tokens', 'N/A')}, Total: {usage.get('total_tokens', 'N/A')}")
                        
                        break  # Success! Use this response
                    else:
                        error_text = response.text[:500] if response.text else 'No error text'
                        openrouter_logger.warning(f"❌ Token {i} failed: HTTP {response.status_code}")
                        openrouter_logger.warning(f"❌ Error response: {error_text}")
                        
                        # Log specific error types
                        if response.status_code == 401:
                            openrouter_logger.error(f"🔐 Authentication failed for token {i} - API key may be invalid")
                        elif response.status_code == 429:
                            openrouter_logger.error(f"⏳ Rate limit exceeded for token {i}")
                        elif response.status_code == 403:
                            openrouter_logger.error(f"🚫 Forbidden - token {i} may not have access to model {self.openrouter_model}")
                        elif response.status_code >= 500:
                            openrouter_logger.error(f"🔥 Server error {response.status_code} - OpenRouter may be experiencing issues")
                        
                        continue  # Try next token
                        
                except requests.exceptions.Timeout as e:
                    openrouter_logger.error(f"⏰ Token {i} timeout after 30s: {str(e)}")
                    continue
                except requests.exceptions.ConnectionError as e:
                    openrouter_logger.error(f"🌐 Token {i} connection error: {str(e)}")
                    continue
                except requests.exceptions.RequestException as e:
                    openrouter_logger.error(f"📡 Token {i} request exception: {str(e)}")
                    continue
                except Exception as e:
                    openrouter_logger.error(f"💥 Token {i} unexpected exception: {str(e)}")
                    continue
            
            else:
                # All tokens failed
                openrouter_logger.error(f"💀 ALL {len(self.openrouter_api_keys)} TOKENS FAILED - falling back to keyword matching")
                openrouter_logger.error(f"🔍 Troubleshooting suggestions:")
                openrouter_logger.error(f"   1. Check API key validity at https://openrouter.ai/keys")
                openrouter_logger.error(f"   2. Verify model '{self.openrouter_model}' is available")
                openrouter_logger.error(f"   3. Check network connectivity to {self.openrouter_base_url}")
                openrouter_logger.error(f"   4. Review rate limits and billing status")
                return self._get_fallback_recommendation(user_message)
            
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
            openrouter_logger.error(f"💥 Unexpected error in OpenRouter recommendation: {str(e)}")
            openrouter_logger.error(f"🔍 Error type: {type(e).__name__}")
            import traceback
            openrouter_logger.error(f"📚 Full traceback: {traceback.format_exc()}")
            return self._get_fallback_recommendation(user_message)
    
    def _test_openrouter_connectivity(self):
        """Test basic connectivity to OpenRouter API"""
        try:
            openrouter_logger.info("🔍 Testing OpenRouter connectivity...")
            response = requests.get(f"{self.openrouter_base_url}/models", timeout=10)
            if response.status_code == 200:
                openrouter_logger.info("✅ OpenRouter API is reachable")
                # Log available models if possible
                try:
                    models_data = response.json()
                    if 'data' in models_data:
                        model_count = len(models_data['data'])
                        openrouter_logger.info(f"📋 Found {model_count} available models")
                        # Check if our configured model is available
                        available_models = [m.get('id', '') for m in models_data['data']]
                        if self.openrouter_model in available_models:
                            openrouter_logger.info(f"✅ Configured model '{self.openrouter_model}' is available")
                        else:
                            openrouter_logger.warning(f"⚠️ Configured model '{self.openrouter_model}' not found in available models")
                            openrouter_logger.debug(f"📋 Available models: {available_models[:10]}...")  # Log first 10
                except Exception as e:
                    openrouter_logger.warning(f"⚠️ Could not parse models response: {e}")
            else:
                openrouter_logger.warning(f"⚠️ OpenRouter API returned {response.status_code}: {response.text[:200]}")
        except requests.exceptions.Timeout:
            openrouter_logger.error("⏰ Timeout connecting to OpenRouter API")
        except requests.exceptions.ConnectionError as e:
            openrouter_logger.error(f"🌐 Connection error to OpenRouter API: {e}")
        except Exception as e:
            openrouter_logger.error(f"💥 Unexpected error testing OpenRouter connectivity: {e}")
    
    def _check_network_connectivity(self):
        """Check general network connectivity before making requests"""
        try:
            # Parse the OpenRouter URL to get the domain
            parsed_url = urlparse(self.openrouter_base_url)
            domain = parsed_url.netloc
            
            openrouter_logger.debug(f"🌐 Checking network connectivity to {domain}...")
            
            # Simple connectivity test
            response = requests.head(f"https://{domain}", timeout=5)
            openrouter_logger.debug(f"✅ Network connectivity to {domain} confirmed (status: {response.status_code})")
            
        except requests.exceptions.Timeout:
            openrouter_logger.warning(f"⏰ Network timeout to {domain}")
        except requests.exceptions.ConnectionError as e:
            openrouter_logger.warning(f"🌐 Network connection issue to {domain}: {e}")
        except Exception as e:
            openrouter_logger.debug(f"🔍 Network check completed with minor issue: {e}")
    
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
            'products': [p.pk for p in recommended_products]  # Use pk instead of id for MongoDB
        }