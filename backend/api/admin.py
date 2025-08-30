from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Product, ChatSession, ChatMessage, CartItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_display', 'tags_display', 'image_preview', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    list_per_page = 20
    ordering = ['-created_at']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'category', 'price')
        }),
        ('Media', {
            'fields': ('image_url', 'image_preview')
        }),
        ('Metadata', {
            'fields': ('tags', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def price_display(self, obj):
        return f"${obj.price}"
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'

    def tags_display(self, obj):
        if obj.tags:
            return ', '.join(obj.tags[:3])  # Show first 3 tags
        return 'No tags'
    tags_display.short_description = 'Tags'

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px;" />',
                obj.image_url
            )
        return "No image"
    image_preview.short_description = 'Preview'

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'messages_count', 'created_at', 'updated_at']
    readonly_fields = ['session_id', 'created_at', 'updated_at', 'messages_count']
    list_per_page = 20
    ordering = ['-created_at']

    def messages_count(self, obj):
        count = obj.messages.count()
        if count > 0:
            url = reverse('admin:api_chatmessage_changelist') + f'?session__id__exact={obj.pk}'
            return format_html('<a href="{}">{} messages</a>', url, count)
        return "0 messages"
    messages_count.short_description = 'Messages'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session_link', 'message_type', 'content_preview', 'products_count', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    readonly_fields = ['timestamp']
    list_per_page = 20
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Message Details', {
            'fields': ('session', 'message_type', 'content')
        }),
        ('AI Response Data', {
            'fields': ('products', 'timestamp'),
            'classes': ('collapse',)
        }),
    )

    def session_link(self, obj):
        url = reverse('admin:api_chatsession_change', args=[obj.session.pk])
        return format_html('<a href="{}">{}</a>', url, obj.session.session_id)
    session_link.short_description = 'Session'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

    def products_count(self, obj):
        if obj.products:
            return f"{len(obj.products)} products"
        return "No products"
    products_count.short_description = 'Products'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'product_link', 'quantity', 'total_price', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at', 'total_price']
    list_per_page = 20
    ordering = ['-created_at']

    def product_link(self, obj):
        url = reverse('admin:api_product_change', args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'

    def total_price(self, obj):
        total = float(obj.product.price) * obj.quantity
        return f"${total:.2f}"
    total_price.short_description = 'Total Price'

# Customize admin site header and title
admin.site.site_header = "SellerAgent Administration"
admin.site.site_title = "SellerAgent Admin Portal"
admin.site.index_title = "Welcome to SellerAgent Administration"