from rest_framework import serializers
from .models import Product, ChatSession, ChatMessage, CartItem
from decimal import Decimal

class ProductSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image_url', 'tags', 'category', 'created_at']
    
    def get_price(self, obj):
        """Convert Decimal/Decimal128 to string for proper JSON serialization"""
        if obj.price:
            # Convert to string to preserve precision, frontend will parse it
            return str(obj.price)
        return "0.00"

    def get_id(self, obj):
        # Return ObjectId/PK as string for frontend stability
        return str(obj.pk)
    
    def get_tags(self, obj):
        """Ensure tags are returned as proper JSON array"""
        if obj.tags:
            # If tags is already a list, return it
            if isinstance(obj.tags, list):
                return obj.tags
            # If tags is a string representation of a list, try to parse it
            import ast
            try:
                return ast.literal_eval(obj.tags) if isinstance(obj.tags, str) else obj.tags
            except (ValueError, SyntaxError):
                # If parsing fails, split by comma as fallback
                return [tag.strip().strip("'\"") for tag in str(obj.tags).strip("[]").split(",") if tag.strip()]
        return []

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
    product_id = serializers.CharField(write_only=True)
    
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
    products = serializers.ListField(child=serializers.DictField())  # Accept pre-serialized product data
    session_id = serializers.UUIDField()