from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'sessions', views.ChatSessionViewSet)
router.register(r'cart', views.CartViewSet, basename='cart')

# Admin router for product management
admin_router = DefaultRouter()
admin_router.register(r'products', views.AdminProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', include(admin_router.urls)),
    path('recommend/', views.recommend_products, name='recommend_products'),
    path('conversation/<uuid:session_id>/', views.get_conversation, name='get_conversation'),
]