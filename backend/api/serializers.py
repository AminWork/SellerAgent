from rest_framework import serializers
from .models import Product, ChatSession, ChatMessage, CartItem

class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image_url', 'tags', 'category', 'created_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'message_type', 'content', 'products', 'timestamp']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['session_id', 'messages', 'created_at']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'created_at']

class AIRecommendationRequest(serializers.Serializer):
    message = serializers.CharField(max_length=1000)
    session_id = serializers.UUIDField()
    conversation_history = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )

class AIRecommendationResponse(serializers.Serializer):
    response = serializers.CharField()
    products = serializers.ListField(child=serializers.IntegerField())
    session_id = serializers.UUIDField()