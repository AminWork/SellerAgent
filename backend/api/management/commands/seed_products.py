from django.core.management.base import BaseCommand
from api.models import Product

class Command(BaseCommand):
    help = 'Seed the database with sample products'

    def handle(self, *args, **options):
        products_data = [
            # Fashion Items
            {
                "name": "Classic Denim Jacket",
                "description": "Timeless denim jacket with vintage wash and modern fit",
                "price": 89.99,
                "image_url": "https://images.pexels.com/photos/1040949/pexels-photo-1040949.jpeg",
                "tags": ["casual", "denim", "vintage", "versatile"],
                "category": "fashion"
            },
            {
                "name": "Silk Blouse",
                "description": "Elegant silk blouse perfect for professional and evening wear",
                "price": 129.99,
                "image_url": "https://images.pexels.com/photos/1065084/pexels-photo-1065084.jpeg",
                "tags": ["professional", "silk", "elegant", "formal"],
                "category": "fashion"
            },
            {
                "name": "Running Sneakers",
                "description": "High-performance running shoes with advanced cushioning",
                "price": 149.99,
                "image_url": "https://images.pexels.com/photos/2529148/pexels-photo-2529148.jpeg",
                "tags": ["athletic", "running", "comfort", "performance"],
                "category": "fashion"
            },
            {
                "name": "Wool Sweater",
                "description": "Cozy merino wool sweater for cold weather comfort",
                "price": 79.99,
                "image_url": "https://images.pexels.com/photos/1040949/pexels-photo-1040949.jpeg",
                "tags": ["warm", "wool", "comfort", "winter"],
                "category": "fashion"
            },
            {
                "name": "Summer Dress",
                "description": "Light and breezy summer dress with floral pattern",
                "price": 69.99,
                "image_url": "https://images.pexels.com/photos/1065084/pexels-photo-1065084.jpeg",
                "tags": ["summer", "casual", "floral", "light"],
                "category": "fashion"
            },
            {
                "name": "Leather Boots",
                "description": "Handcrafted leather boots with durable construction",
                "price": 199.99,
                "image_url": "https://images.pexels.com/photos/2529148/pexels-photo-2529148.jpeg",
                "tags": ["leather", "durable", "handcrafted", "boots"],
                "category": "fashion"
            },
            {
                "name": "Designer Handbag",
                "description": "Luxury handbag with premium materials and elegant design",
                "price": 299.99,
                "image_url": "https://images.pexels.com/photos/1040949/pexels-photo-1040949.jpeg",
                "tags": ["luxury", "designer", "handbag", "premium"],
                "category": "fashion"
            },
            {
                "name": "Athletic Shorts",
                "description": "Breathable athletic shorts for workout and casual wear",
                "price": 39.99,
                "image_url": "https://images.pexels.com/photos/1065084/pexels-photo-1065084.jpeg",
                "tags": ["athletic", "breathable", "casual", "shorts"],
                "category": "fashion"
            },
            
            # Electronics
            {
                "name": "Wireless Earbuds",
                "description": "Premium wireless earbuds with noise cancellation",
                "price": 199.99,
                "image_url": "https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg",
                "tags": ["wireless", "audio", "noise-cancellation", "premium"],
                "category": "electronics"
            },
            {
                "name": "Smart Watch",
                "description": "Advanced smartwatch with health monitoring and GPS",
                "price": 299.99,
                "image_url": "https://images.pexels.com/photos/437037/pexels-photo-437037.jpeg",
                "tags": ["smartwatch", "health", "GPS", "fitness"],
                "category": "electronics"
            },
            {
                "name": "Laptop Stand",
                "description": "Ergonomic aluminum laptop stand for better posture",
                "price": 49.99,
                "image_url": "https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg",
                "tags": ["ergonomic", "aluminum", "laptop", "accessory"],
                "category": "electronics"
            },
            {
                "name": "Mechanical Keyboard",
                "description": "Premium mechanical keyboard with RGB backlighting",
                "price": 129.99,
                "image_url": "https://images.pexels.com/photos/437037/pexels-photo-437037.jpeg",
                "tags": ["mechanical", "RGB", "gaming", "typing"],
                "category": "electronics"
            },
            {
                "name": "Wireless Charger",
                "description": "Fast wireless charging pad compatible with all devices",
                "price": 29.99,
                "image_url": "https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg",
                "tags": ["wireless", "charging", "fast", "compatible"],
                "category": "electronics"
            },
            {
                "name": "4K Webcam",
                "description": "Professional 4K webcam for streaming and video calls",
                "price": 149.99,
                "image_url": "https://images.pexels.com/photos/437037/pexels-photo-437037.jpeg",
                "tags": ["4K", "webcam", "streaming", "professional"],
                "category": "electronics"
            },
            {
                "name": "Bluetooth Speaker",
                "description": "Portable Bluetooth speaker with exceptional sound quality",
                "price": 89.99,
                "image_url": "https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg",
                "tags": ["bluetooth", "portable", "speaker", "sound"],
                "category": "electronics"
            },
            {
                "name": "Phone Case",
                "description": "Protective phone case with wireless charging support",
                "price": 24.99,
                "image_url": "https://images.pexels.com/photos/437037/pexels-photo-437037.jpeg",
                "tags": ["protection", "wireless", "phone", "case"],
                "category": "electronics"
            },
            {
                "name": "Gaming Mouse",
                "description": "High-precision gaming mouse with customizable buttons",
                "price": 79.99,
                "image_url": "https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg",
                "tags": ["gaming", "precision", "customizable", "mouse"],
                "category": "electronics"
            },
            {
                "name": "USB-C Hub",
                "description": "Multi-port USB-C hub with HDMI and SD card slots",
                "price": 59.99,
                "image_url": "https://images.pexels.com/photos/437037/pexels-photo-437037.jpeg",
                "tags": ["USB-C", "hub", "HDMI", "connectivity"],
                "category": "electronics"
            },
            {
                "name": "Monitor Light Bar",
                "description": "LED light bar designed for computer monitors",
                "price": 69.99,
                "image_url": "https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg",
                "tags": ["LED", "monitor", "lighting", "ergonomic"],
                "category": "electronics"
            },
            {
                "name": "Cable Organizer",
                "description": "Magnetic cable organizer for desk cable management",
                "price": 19.99,
                "image_url": "https://images.pexels.com/photos/437037/pexels-photo-437037.jpeg",
                "tags": ["organization", "magnetic", "cable", "desk"],
                "category": "electronics"
            },
            {
                "name": "Vintage Sunglasses",
                "description": "Classic aviator sunglasses with UV protection",
                "price": 45.99,
                "image_url": "https://images.pexels.com/photos/1040949/pexels-photo-1040949.jpeg",
                "tags": ["vintage", "sunglasses", "aviator", "UV-protection"],
                "category": "fashion"
            },
            {
                "name": "Fitness Tracker",
                "description": "Advanced fitness tracker with heart rate monitoring",
                "price": 99.99,
                "image_url": "https://images.pexels.com/photos/437037/pexels-photo-437037.jpeg",
                "tags": ["fitness", "tracker", "heart-rate", "health"],
                "category": "electronics"
            }
        ]

        # Clear existing products
        Product.objects.all().delete()
        
        # Create new products
        for product_data in products_data:
            Product.objects.create(**product_data)
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(products_data)} products')
        )