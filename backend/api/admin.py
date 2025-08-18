from django.contrib import admin
from .models import Product, ChatSession, ChatMessage, CartItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description', 'tags']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'created_at']
    readonly_fields = ['session_id', 'created_at', 'updated_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    readonly_fields = ['timestamp']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'product', 'quantity', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']