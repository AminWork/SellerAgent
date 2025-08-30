from django.core.management.base import BaseCommand
from api.models import Product
import json

class Command(BaseCommand):
    help = 'Populate the database with sample products'

    def handle(self, *args, **options):
        # Clear existing products
        Product.objects.all().delete()
        self.stdout.write('Cleared existing products')

        products_data = [
            # Fashion Items
            {
                "name": "Classic Denim Jacket",
                "description": "Timeless denim jacket with vintage wash and modern fit. Perfect for layering and casual outfits.",
                "price": 89.99,
                "image_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=500",
                "tags": ["casual", "denim", "vintage", "versatile", "jacket"],
                "category": "fashion"
            },
            {
                "name": "Silk Blouse",
                "description": "Elegant silk blouse perfect for professional and evening wear. Luxurious feel with sophisticated design.",
                "price": 129.99,
                "image_url": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=500",
                "tags": ["professional", "silk", "elegant", "formal", "blouse"],
                "category": "fashion"
            },
            {
                "name": "Running Sneakers",
                "description": "High-performance running shoes with advanced cushioning and breathable mesh upper.",
                "price": 149.99,
                "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
                "tags": ["athletic", "running", "comfort", "performance", "shoes"],
                "category": "fashion"
            },
            {
                "name": "Merino Wool Sweater",
                "description": "Cozy merino wool sweater for cold weather comfort. Soft, warm, and naturally odor-resistant.",
                "price": 79.99,
                "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=500",
                "tags": ["warm", "wool", "comfort", "winter", "sweater"],
                "category": "fashion"
            },
            {
                "name": "Summer Maxi Dress",
                "description": "Light and breezy summer dress with beautiful floral pattern. Perfect for warm weather.",
                "price": 69.99,
                "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=500",
                "tags": ["summer", "casual", "floral", "light", "dress"],
                "category": "fashion"
            },
            
            # Electronics
            {
                "name": "Wireless Bluetooth Headphones",
                "description": "Premium wireless headphones with noise cancellation and 30-hour battery life.",
                "price": 199.99,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
                "tags": ["wireless", "bluetooth", "music", "noise-cancelling", "headphones"],
                "category": "electronics"
            },
            {
                "name": "Smartphone",
                "description": "Latest smartphone with advanced camera system, fast processor, and all-day battery.",
                "price": 799.99,
                "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500",
                "tags": ["mobile", "smartphone", "camera", "technology", "communication"],
                "category": "electronics"
            },
            {
                "name": "Laptop Computer",
                "description": "High-performance laptop for work and entertainment. Fast SSD, plenty of RAM, and great display.",
                "price": 1299.99,
                "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500",
                "tags": ["laptop", "computer", "work", "productivity", "technology"],
                "category": "electronics"
            },
            {
                "name": "Smart Watch",
                "description": "Advanced fitness tracking smartwatch with heart rate monitor and GPS.",
                "price": 299.99,
                "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
                "tags": ["smartwatch", "fitness", "health", "wearable", "technology"],
                "category": "electronics"
            },
            {
                "name": "Wireless Charger",
                "description": "Fast wireless charging pad compatible with all Qi-enabled devices.",
                "price": 39.99,
                "image_url": "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=500",
                "tags": ["wireless", "charger", "convenient", "fast-charging", "accessory"],
                "category": "electronics"
            },

            # Home & Living
            {
                "name": "Coffee Maker",
                "description": "Programmable coffee maker with built-in grinder and thermal carafe. Perfect morning brew.",
                "price": 159.99,
                "image_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=500",
                "tags": ["coffee", "kitchen", "appliance", "morning", "brewing"],
                "category": "home"
            },
            {
                "name": "Throw Pillow Set",
                "description": "Set of 4 decorative throw pillows in modern colors. Soft and comfortable.",
                "price": 49.99,
                "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500",
                "tags": ["pillows", "decor", "comfort", "living-room", "soft"],
                "category": "home"
            },
            {
                "name": "Essential Oil Diffuser",
                "description": "Ultrasonic aromatherapy diffuser with LED lights and timer settings.",
                "price": 79.99,
                "image_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500",
                "tags": ["aromatherapy", "relaxation", "wellness", "home", "diffuser"],
                "category": "home"
            },
            {
                "name": "Indoor Plant Collection",
                "description": "Set of 3 low-maintenance indoor plants perfect for beginners. Includes pots.",
                "price": 89.99,
                "image_url": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=500",
                "tags": ["plants", "indoor", "green", "air-purifying", "decor"],
                "category": "home"
            },
            {
                "name": "Kitchen Knife Set",
                "description": "Professional 8-piece knife set with wooden block. Sharp, durable, and balanced.",
                "price": 199.99,
                "image_url": "https://images.unsplash.com/photo-1593618998160-e34014e67546?w=500",
                "tags": ["kitchen", "knives", "cooking", "professional", "sharp"],
                "category": "home"
            },

            # Books & Media
            {
                "name": "Bestselling Novel",
                "description": "Award-winning fiction novel that topped bestseller lists. Engaging story and memorable characters.",
                "price": 14.99,
                "image_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500",
                "tags": ["book", "fiction", "bestseller", "reading", "novel"],
                "category": "books"
            },
            {
                "name": "Cookbook Collection",
                "description": "Set of 3 cookbooks covering international cuisine, healthy eating, and desserts.",
                "price": 59.99,
                "image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=500",
                "tags": ["cookbook", "cooking", "recipes", "food", "international"],
                "category": "books"
            },
            {
                "name": "Self-Help Guide",
                "description": "Popular self-improvement book with practical strategies for personal growth.",
                "price": 19.99,
                "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500",
                "tags": ["self-help", "personal-growth", "motivation", "success", "guide"],
                "category": "books"
            },

            # Sports & Fitness
            {
                "name": "Yoga Mat",
                "description": "Premium non-slip yoga mat with extra cushioning. Perfect for yoga, pilates, and stretching.",
                "price": 49.99,
                "image_url": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=500",
                "tags": ["yoga", "fitness", "exercise", "mat", "wellness"],
                "category": "sports"
            },
            {
                "name": "Resistance Bands Set",
                "description": "Complete resistance band set with multiple resistance levels and door anchor.",
                "price": 29.99,
                "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=500",
                "tags": ["resistance", "bands", "fitness", "strength", "portable"],
                "category": "sports"
            },
            {
                "name": "Water Bottle",
                "description": "Insulated stainless steel water bottle that keeps drinks cold for 24 hours.",
                "price": 24.99,
                "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500",
                "tags": ["water", "bottle", "hydration", "insulated", "eco-friendly"],
                "category": "sports"
            }
        ]

        created_count = 0
        for product_data in products_data:
            product = Product.objects.create(**product_data)
            created_count += 1
            self.stdout.write(f'Created product: {product.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} products')
        )
