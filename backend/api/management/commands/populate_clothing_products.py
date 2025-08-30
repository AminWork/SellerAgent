from django.core.management.base import BaseCommand
from api.models import Product
import json
import random

class Command(BaseCommand):
    help = 'Clean database and populate with 200 clothing products'

    def handle(self, *args, **options):
        # Clear existing products
        Product.objects.all().delete()
        self.stdout.write('Cleared existing products from database')

        # Define clothing categories and items
        clothing_items = [
            # T-Shirts & Tops
            {"name": "Classic White T-Shirt", "base_price": 19.99, "tags": ["casual", "basic", "cotton", "everyday", "unisex"]},
            {"name": "Vintage Graphic Tee", "base_price": 24.99, "tags": ["casual", "vintage", "graphic", "trendy", "cotton"]},
            {"name": "V-Neck T-Shirt", "base_price": 22.99, "tags": ["casual", "v-neck", "comfortable", "everyday", "cotton"]},
            {"name": "Long Sleeve Tee", "base_price": 29.99, "tags": ["casual", "long-sleeve", "layering", "cotton", "comfortable"]},
            {"name": "Striped T-Shirt", "base_price": 26.99, "tags": ["casual", "striped", "classic", "nautical", "cotton"]},
            {"name": "Henley Shirt", "base_price": 32.99, "tags": ["casual", "henley", "buttons", "comfortable", "cotton"]},
            {"name": "Tank Top", "base_price": 18.99, "tags": ["casual", "sleeveless", "summer", "cotton", "basic"]},
            {"name": "Polo Shirt", "base_price": 39.99, "tags": ["casual", "polo", "collar", "preppy", "cotton"]},
            {"name": "Button-Up Shirt", "base_price": 49.99, "tags": ["formal", "button-up", "collar", "professional", "cotton"]},
            {"name": "Flannel Shirt", "base_price": 44.99, "tags": ["casual", "flannel", "checkered", "warm", "cotton"]},
            
            # Dresses
            {"name": "Summer Maxi Dress", "base_price": 69.99, "tags": ["dress", "maxi", "summer", "flowy", "feminine"]},
            {"name": "Little Black Dress", "base_price": 89.99, "tags": ["dress", "formal", "elegant", "versatile", "classic"]},
            {"name": "Floral Print Dress", "base_price": 59.99, "tags": ["dress", "floral", "spring", "feminine", "casual"]},
            {"name": "Wrap Dress", "base_price": 64.99, "tags": ["dress", "wrap", "flattering", "versatile", "elegant"]},
            {"name": "Shift Dress", "base_price": 54.99, "tags": ["dress", "shift", "simple", "classic", "professional"]},
            {"name": "A-Line Dress", "base_price": 57.99, "tags": ["dress", "a-line", "flattering", "classic", "versatile"]},
            {"name": "Midi Dress", "base_price": 62.99, "tags": ["dress", "midi", "elegant", "sophisticated", "versatile"]},
            {"name": "Cocktail Dress", "base_price": 94.99, "tags": ["dress", "cocktail", "formal", "party", "elegant"]},
            
            # Pants & Jeans
            {"name": "Skinny Jeans", "base_price": 79.99, "tags": ["jeans", "skinny", "denim", "casual", "fitted"]},
            {"name": "Straight Leg Jeans", "base_price": 74.99, "tags": ["jeans", "straight", "denim", "classic", "comfortable"]},
            {"name": "High-Waisted Jeans", "base_price": 84.99, "tags": ["jeans", "high-waisted", "denim", "trendy", "flattering"]},
            {"name": "Bootcut Jeans", "base_price": 77.99, "tags": ["jeans", "bootcut", "denim", "classic", "flared"]},
            {"name": "Wide Leg Jeans", "base_price": 82.99, "tags": ["jeans", "wide-leg", "denim", "trendy", "comfortable"]},
            {"name": "Black Leggings", "base_price": 29.99, "tags": ["leggings", "black", "stretchy", "comfortable", "versatile"]},
            {"name": "Yoga Pants", "base_price": 39.99, "tags": ["activewear", "yoga", "stretchy", "comfortable", "athletic"]},
            {"name": "Dress Pants", "base_price": 59.99, "tags": ["pants", "formal", "professional", "tailored", "work"]},
            {"name": "Cargo Pants", "base_price": 54.99, "tags": ["pants", "cargo", "utility", "pockets", "casual"]},
            {"name": "Chinos", "base_price": 49.99, "tags": ["pants", "chinos", "casual", "cotton", "versatile"]},
            
            # Sweaters & Knitwear
            {"name": "Cashmere Sweater", "base_price": 149.99, "tags": ["sweater", "cashmere", "luxury", "warm", "soft"]},
            {"name": "Cable Knit Sweater", "base_price": 89.99, "tags": ["sweater", "cable-knit", "cozy", "winter", "textured"]},
            {"name": "Cardigan", "base_price": 69.99, "tags": ["cardigan", "layering", "buttons", "versatile", "warm"]},
            {"name": "Turtleneck Sweater", "base_price": 79.99, "tags": ["sweater", "turtleneck", "warm", "classic", "sophisticated"]},
            {"name": "Pullover Hoodie", "base_price": 49.99, "tags": ["hoodie", "casual", "comfortable", "cotton", "relaxed"]},
            {"name": "Zip-Up Hoodie", "base_price": 54.99, "tags": ["hoodie", "zip-up", "casual", "layering", "cotton"]},
            {"name": "Crew Neck Sweater", "base_price": 64.99, "tags": ["sweater", "crew-neck", "classic", "warm", "versatile"]},
            {"name": "V-Neck Sweater", "base_price": 62.99, "tags": ["sweater", "v-neck", "elegant", "layering", "warm"]},
            
            # Jackets & Outerwear
            {"name": "Denim Jacket", "base_price": 89.99, "tags": ["jacket", "denim", "casual", "layering", "classic"]},
            {"name": "Leather Jacket", "base_price": 199.99, "tags": ["jacket", "leather", "edgy", "durable", "stylish"]},
            {"name": "Blazer", "base_price": 119.99, "tags": ["blazer", "formal", "professional", "tailored", "versatile"]},
            {"name": "Trench Coat", "base_price": 159.99, "tags": ["coat", "trench", "classic", "sophisticated", "waterproof"]},
            {"name": "Puffer Jacket", "base_price": 139.99, "tags": ["jacket", "puffer", "warm", "winter", "insulated"]},
            {"name": "Bomber Jacket", "base_price": 94.99, "tags": ["jacket", "bomber", "casual", "trendy", "lightweight"]},
            {"name": "Windbreaker", "base_price": 74.99, "tags": ["jacket", "windbreaker", "lightweight", "waterproof", "athletic"]},
            {"name": "Peacoat", "base_price": 179.99, "tags": ["coat", "peacoat", "warm", "classic", "wool"]},
            
            # Skirts & Shorts
            {"name": "Mini Skirt", "base_price": 39.99, "tags": ["skirt", "mini", "short", "trendy", "youthful"]},
            {"name": "Pencil Skirt", "base_price": 49.99, "tags": ["skirt", "pencil", "fitted", "professional", "elegant"]},
            {"name": "A-Line Skirt", "base_price": 44.99, "tags": ["skirt", "a-line", "flattering", "classic", "versatile"]},
            {"name": "Pleated Skirt", "base_price": 52.99, "tags": ["skirt", "pleated", "textured", "feminine", "classic"]},
            {"name": "Denim Shorts", "base_price": 34.99, "tags": ["shorts", "denim", "casual", "summer", "comfortable"]},
            {"name": "High-Waisted Shorts", "base_price": 32.99, "tags": ["shorts", "high-waisted", "flattering", "trendy", "summer"]},
            {"name": "Athletic Shorts", "base_price": 29.99, "tags": ["shorts", "athletic", "sporty", "comfortable", "activewear"]},
            {"name": "Bermuda Shorts", "base_price": 37.99, "tags": ["shorts", "bermuda", "longer", "casual", "modest"]},
        ]

        # Color variations
        colors = ["Black", "White", "Navy", "Gray", "Beige", "Brown", "Blue", "Green", "Red", "Pink", "Purple", "Yellow", "Orange"]
        
        # Material variations
        materials = ["Cotton", "Polyester", "Wool", "Silk", "Linen", "Denim", "Leather", "Cashmere", "Bamboo", "Modal"]
        
        # Size variations
        sizes = ["XS", "S", "M", "L", "XL", "XXL"]
        
        # Unsplash clothing image URLs
        clothing_images = [
            "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=500&h=500&fit=crop",  # Denim jacket
            "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=500&h=500&fit=crop",  # Silk blouse
            "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=500&h=500&fit=crop",  # Sweater
            "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=500&h=500&fit=crop",  # Dress
            "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=500&h=500&fit=crop",  # T-shirt
            "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=500&h=500&fit=crop",  # Clothing rack
            "https://images.unsplash.com/photo-1445205170230-053b83016050?w=500&h=500&fit=crop",  # Jeans
            "https://images.unsplash.com/photo-1562157873-818bc0726f68?w=500&h=500&fit=crop",  # Dress shirt
            "https://images.unsplash.com/photo-1503341504253-dff4815485f1?w=500&h=500&fit=crop",  # Hoodie
            "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=500&h=500&fit=crop",  # Fashion
            "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=500&h=500&fit=crop",  # Blazer
            "https://images.unsplash.com/photo-1506629905607-53e91acd8407?w=500&h=500&fit=crop",  # Jacket
            "https://images.unsplash.com/photo-1520006403909-838d56ac2662?w=500&h=500&fit=crop",  # Skirt
            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&h=500&fit=crop",  # Pants
            "https://images.unsplash.com/photo-1559582927-62cddd4dfa49?w=500&h=500&fit=crop",  # Shorts
        ]

        created_count = 0
        target_count = 200

        # Generate 200 clothing products
        while created_count < target_count:
            base_item = random.choice(clothing_items)
            color = random.choice(colors)
            material = random.choice(materials)
            size_range = f"Available in {', '.join(random.sample(sizes, random.randint(3, 6)))}"
            
            # Create variations
            name = f"{color} {base_item['name']}"
            if random.choice([True, False]):
                name = f"{material} {name}"
            
            # Price variation
            price_variation = random.uniform(0.8, 1.3)
            price = round(base_item['base_price'] * price_variation, 2)
            
            # Enhanced description
            quality_adjectives = ["Premium", "High-quality", "Comfortable", "Stylish", "Durable", "Soft", "Elegant"]
            occasion_contexts = ["perfect for everyday wear", "ideal for special occasions", "great for work or casual outings", 
                               "suitable for any season", "perfect for layering", "ideal for weekend activities"]
            
            description = f"{random.choice(quality_adjectives)} {material.lower()} {base_item['name'].lower()} in {color.lower()}. {random.choice(occasion_contexts).capitalize()}. {size_range}."
            
            # Enhanced tags
            enhanced_tags = base_item['tags'] + [color.lower(), material.lower(), "clothing"]
            if "formal" not in enhanced_tags and random.choice([True, False]):
                enhanced_tags.append("fashion")
            
            product_data = {
                "name": name,
                "description": description,
                "price": price,
                "image_url": random.choice(clothing_images),
                "tags": enhanced_tags,
                "category": "clothes"
            }
            
            try:
                product = Product.objects.create(**product_data)
                created_count += 1
                
                if created_count % 20 == 0:
                    self.stdout.write(f'Created {created_count}/{target_count} products...')
                    
            except Exception as e:
                self.stdout.write(f'Error creating product {name}: {str(e)}')
                continue

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} clothing products and cleared old data')
        )
