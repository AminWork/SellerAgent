from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
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

logger = logging.getLogger(__name__)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
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

class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    lookup_field = 'session_id'
    
    def create(self, request):
        session = ChatSession.objects.create()
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
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
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message
        )
        
        # Get AI recommendation
        ai_service = AIRecommendationService()
        ai_response = ai_service.get_recommendation(message, conversation_history)
        
        # Get recommended products
        recommended_products = Product.objects.filter(id__in=ai_response['products'])
        
        # Save AI message with recommended products
        ai_message = ChatMessage.objects.create(
            session=session,
            message_type='ai',
            content=ai_response['response'],
            products=list(ai_response['products'])
        )
        
        # Prepare response
        response_data = {
            'response': ai_response['response'],
            'products': list(ai_response['products']),
            'session_id': session_id
        }
        
        response_serializer = AIRecommendationResponse(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid response data'},
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
                products = Product.objects.filter(id__in=message.products)
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