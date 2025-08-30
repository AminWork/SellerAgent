from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Product, ChatSession, ChatMessage, CartItem
from .serializers import (
    ProductSerializer, 
    ChatSessionSerializer, 
    ChatMessageSerializer,
    CartItemSerializer,
    AIRecommendationRequest,
    AIRecommendationResponse
)
from .services import AIRecommendationService
import uuid
import logging
from decimal import Decimal
from .rag import semantic_search as rag_semantic_search, ensure_embeddings_for_all_products

logger = logging.getLogger(__name__)

# Create dedicated logger for API debugging
api_logger = logging.getLogger('api_debug')
api_logger.setLevel(logging.DEBUG)

# Create file handler for API logs
if not api_logger.handlers:
    handler = logging.FileHandler('/app/api_debug.log')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    api_logger.addHandler(handler)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        api_logger.info(f"ProductViewSet: Total products in queryset: {queryset.count()}")
        for product in queryset[:5]:  # Log first 5 products
            api_logger.info(f"ProductViewSet: Product {product.pk} - {product.name}")
        category = self.request.query_params.get('category', None)
        search = self.request.query_params.get('search', None)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        
        return queryset

    @action(detail=False, methods=['get'], url_path='semantic_search')
    def semantic_search(self, request):
        """Semantic search over products using embeddings."""
        query = request.query_params.get('q', '')
        try:
            top_k = int(request.query_params.get('top_k', 8))
        except ValueError:
            top_k = 8
            
        api_logger.info(f"Semantic search request: query='{query}', top_k={top_k}")
        
        if not query:
            api_logger.warning("Empty query provided to semantic search")
            return Response({"results": []}, status=status.HTTP_200_OK)
        try:
            api_logger.info(f"Calling RAG semantic search")
            pks = rag_semantic_search(query, top_k=top_k)
            api_logger.info(f"RAG returned {len(pks)} product IDs: {pks}")
            
            products = Product.objects.filter(pk__in=pks)
            api_logger.info(f"Found {len(products)} products in database")
            
            data = ProductSerializer(products, many=True).data
            api_logger.info(f"Serialized {len(data)} products for response")
            
            return Response({"results": data, "count": len(data)}, status=status.HTTP_200_OK)
        except Exception as e:
            api_logger.error(f"semantic_search error: {e}")
            return Response({"results": []}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='index_embeddings')
    def index_embeddings(self, request):
        """Ensure embeddings exist for all products (on-demand)."""
        try:
            created = ensure_embeddings_for_all_products()
            return Response({"created": created}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"index_embeddings error: {e}")
            return Response({"error": "failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='advanced_search')
    def advanced_search(self, request):
        """Combination of filters: category, price range, tags, text query."""
        qs = Product.objects.all()
        category = request.query_params.get('category')
        q = request.query_params.get('q')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        tags = request.query_params.get('tags')  # comma-separated

        if category:
            qs = qs.filter(category=category)
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(tags__icontains=q))
        try:
            if min_price is not None:
                qs = qs.filter(price__gte=Decimal(str(min_price)))
            if max_price is not None:
                qs = qs.filter(price__lte=Decimal(str(max_price)))
        except Exception:
            pass
        if tags:
            for tag in [t.strip() for t in tags.split(',') if t.strip()]:
                qs = qs.filter(tags__icontains=tag)
        data = ProductSerializer(qs[:50], many=True).data
        return Response({"results": data, "count": len(data)}, status=status.HTTP_200_OK)


class AdminProductViewSet(viewsets.ModelViewSet):
    """
    Admin-only product management viewset with full CRUD operations
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def create(self, request):
        """Create a new product"""
        try:
            api_logger.info(f"Admin creating product: {request.data}")
            
            # Handle tags if provided as string
            tags = request.data.get('tags', [])
            if isinstance(tags, str):
                # Split comma-separated string into list
                tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
            
            product_data = {
                'name': request.data.get('name'),
                'description': request.data.get('description'),
                'price': request.data.get('price'),
                'image_url': request.data.get('image_url'),
                'category': request.data.get('category'),
                'tags': tags
            }
            
            product = Product.objects.create(**product_data)
            api_logger.info(f"Successfully created product: {product.pk}")
            
            serializer = self.get_serializer(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            api_logger.error(f"Error creating product: {e}")
            return Response(
                {"error": f"Failed to create product: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, pk=None):
        """Update an existing product"""
        try:
            api_logger.info(f"Admin updating product {pk}: {request.data}")
            
            product = get_object_or_404(Product, pk=pk)
            
            # Handle tags if provided as string
            if 'tags' in request.data:
                tags = request.data['tags']
                if isinstance(tags, str):
                    request.data['tags'] = [tag.strip() for tag in tags.split(',') if tag.strip()]
            
            # Update fields
            for field, value in request.data.items():
                if hasattr(product, field):
                    setattr(product, field, value)
            
            product.save()
            api_logger.info(f"Successfully updated product: {product.pk}")
            
            serializer = self.get_serializer(product)
            return Response(serializer.data)
            
        except Exception as e:
            api_logger.error(f"Error updating product {pk}: {e}")
            return Response(
                {"error": f"Failed to update product: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, pk=None):
        """Delete a product"""
        try:
            api_logger.info(f"Admin deleting product {pk}")
            
            product = get_object_or_404(Product, pk=pk)
            product.delete()
            
            api_logger.info(f"Successfully deleted product: {pk}")
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            api_logger.error(f"Error deleting product {pk}: {e}")
            return Response(
                {"error": f"Failed to delete product: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    lookup_field = 'session_id'
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def create(self, request):
        session = ChatSession.objects.create()
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Completely disable authentication and CSRF for this endpoint
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def recommend_products(request):
    """
    AI-powered product recommendation endpoint
    """
    try:
        # Validate request data
        request_serializer = AIRecommendationRequest(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                {'error': 'Invalid request data', 'details': request_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = request_serializer.validated_data
        message = validated_data['message']
        session_id = validated_data['session_id']
        conversation_history = validated_data.get('conversation_history', [])
        
        # Get or create chat session
        session, created = ChatSession.objects.get_or_create(session_id=session_id)
        
        # Retrieve conversation history from database (last 10 messages for context)
        previous_messages = ChatMessage.objects.filter(session=session).order_by('-timestamp')[:10]
        conversation_history = []
        
        for msg in reversed(previous_messages):  # Reverse to get chronological order
            conversation_history.append({
                'type': msg.message_type,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'products': msg.products if msg.products else []
            })
        
        api_logger.info(f"Retrieved {len(conversation_history)} messages for conversation history")
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message
        )
        
        # Get AI recommendation with retrieved conversation history
        ai_service = AIRecommendationService()
        ai_response = ai_service.get_recommendation(message, conversation_history)
        
        # Get recommended products - convert string IDs to ObjectId for MongoDB
        from bson import ObjectId
        try:
            # Convert string IDs to ObjectId for proper MongoDB querying
            object_ids = [ObjectId(pid) for pid in ai_response['products']]
            recommended_products = Product.objects.filter(_id__in=object_ids)
            api_logger.info(f"Found {recommended_products.count()} products from {len(ai_response['products'])} recommended IDs")
        except Exception as e:
            api_logger.error(f"Error converting product IDs to ObjectId: {e}")
            # Fallback to empty queryset if conversion fails
            recommended_products = Product.objects.none()
        
        # Save AI message with recommended products
        ai_message = ChatMessage.objects.create(
            session=session,
            message_type='ai',
            content=ai_response['response'],
            products=list(ai_response['products'])
        )
        
        # Serialize products first, then prepare response data
        products_serializer = ProductSerializer(recommended_products, many=True)
        
        # Prepare response with already-serialized product data
        response_data = {
            'response': ai_response['response'],
            'products': products_serializer.data,  # Pre-serialized product data
            'session_id': session_id
        }
        
        response_serializer = AIRecommendationResponse(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            api_logger.error(f"Response serializer validation errors: {response_serializer.errors}")
            api_logger.error(f"Response data: {response_data}")
            return Response(
                {'error': 'Invalid response data', 'details': response_serializer.errors},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error in recommend_products: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_conversation(request, session_id):
    """
    Get conversation history for a session
    """
    try:
        session = get_object_or_404(ChatSession, session_id=session_id)
        messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
        
        conversation_data = []
        for message in messages:
            message_data = {
                'id': str(message._id),
                'type': message.message_type,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'products': []
            }
            
            if message.products:
                products = Product.objects.filter(pk__in=message.products)
                message_data['products'] = ProductSerializer(products, many=True).data
            
            conversation_data.append(message_data)
        
        return Response({
            'session_id': session_id,
            'messages': conversation_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in get_conversation: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        session_id = self.request.query_params.get('session_id')
        if session_id:
            return CartItem.objects.filter(session_id=session_id)
        return CartItem.objects.none()
    
    def create(self, request):
        session_id = request.data.get('session_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not session_id or not product_id:
            return Response(
                {'error': 'session_id and product_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check if item already exists in cart
            cart_item, created = CartItem.objects.get_or_create(
                session_id=session_id,
                product_id=product_id,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Update quantity if item already exists
                cart_item.quantity += quantity
                cart_item.save()
            
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error adding to cart: {str(e)}")
            return Response(
                {'error': 'Failed to add item to cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        session_id = request.query_params.get('session_id')
        if session_id:
            CartItem.objects.filter(session_id=session_id).delete()
            return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)
        return Response(
            {'error': 'session_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )