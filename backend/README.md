# AI-Powered Ecommerce Backend

Django REST API backend with MongoDB integration for the AI-powered ecommerce platform.

## Features

- **Django REST Framework** - RESTful API endpoints
- **MongoDB Integration** - Using djongo for MongoDB support
- **AI-Powered Recommendations** - OpenAI GPT integration for product recommendations
- **Chat System** - Conversation history and session management
- **Shopping Cart** - Session-based cart functionality
- **Product Management** - Full CRUD operations for products

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_NAME=ecommerce_ai
MONGODB_USERNAME=
MONGODB_PASSWORD=
MONGODB_AUTH_SOURCE=admin

# OpenAI Configuration (optional)
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Database Setup

Make sure MongoDB is running, then run migrations:

```bash
python manage.py migrate
```

### 4. Seed Sample Data

Load sample products into the database:

```bash
python manage.py seed_products
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Products
- `GET /api/products/` - List all products
- `GET /api/products/{id}/` - Get product details
- `GET /api/products/?category=fashion` - Filter by category
- `GET /api/products/?search=wireless` - Search products

### Chat & Recommendations
- `POST /api/recommend/` - Get AI product recommendations
- `POST /api/sessions/` - Create new chat session
- `GET /api/conversation/{session_id}/` - Get conversation history

### Shopping Cart
- `GET /api/cart/?session_id={uuid}` - Get cart items
- `POST /api/cart/` - Add item to cart
- `PUT /api/cart/{id}/` - Update cart item
- `DELETE /api/cart/{id}/` - Remove cart item
- `DELETE /api/cart/clear/?session_id={uuid}` - Clear cart

## AI Recommendation System

The system supports two modes:

1. **OpenAI Integration** (when API key is provided)
   - Uses GPT-3.5-turbo for intelligent product recommendations
   - Considers conversation context and product database
   - Returns natural language responses with product suggestions

2. **Fallback System** (when OpenAI is not available)
   - Keyword-based product matching
   - Relevance scoring algorithm
   - Random selection when no matches found

## Request/Response Examples

### Get AI Recommendations

**Request:**
```json
POST /api/recommend/
{
  "message": "I need wireless headphones for working out",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "I'd be happy to help you find the perfect wireless headphones for your workouts! Here are my top recommendations:",
  "products": [9, 15, 22],
  "session_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Add to Cart

**Request:**
```json
POST /api/cart/
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "product_id": 9,
  "quantity": 1
}
```

## MongoDB Collections

- **products** - Product catalog
- **chat_sessions** - User chat sessions
- **chat_messages** - Conversation history
- **cart_items** - Shopping cart items

## Development Notes

- The system uses session-based authentication (no user accounts required)
- All cart and chat data is tied to session UUIDs
- CORS is configured for frontend development
- Comprehensive logging for debugging
- Admin interface available at `/admin/`

## Deployment

For production deployment:

1. Set `DEBUG=False` in environment
2. Configure proper MongoDB connection string
3. Set up proper CORS origins
4. Use a production WSGI server like Gunicorn
5. Set up proper logging and monitoring