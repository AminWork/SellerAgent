# Docker Compose Setup for E-commerce AI Application

This Docker Compose setup provides a complete development environment with:
- **Frontend**: React/TypeScript (Vite) on port 5173
- **Backend**: Django REST API on port 8000  
- **Database**: MongoDB on port 27017
- **Nginx**: Reverse proxy on port 80

## Prerequisites

1. Docker and Docker Compose installed
2. OpenAI API key (optional, for AI features)

## Quick Start

1. **Set up environment variables**:
   ```bash
   # Edit the .env file and add your OpenAI API key
   OPENAI_API_KEY=your-actual-openai-api-key-here
   ```

2. **Build and start all services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - **Main Application**: http://localhost (via Nginx)
   - **Frontend Direct**: http://localhost:5173
   - **Backend API**: http://localhost:8000
   - **Django Admin**: http://localhost/admin

## Service Details

### Frontend (React/Vite)
- Container: `ecommerce_frontend`
- Port: 5173
- Hot reload enabled for development

### Backend (Django)
- Container: `ecommerce_backend`
- Port: 8000
- Auto-reloads on code changes

### Database (MongoDB)
- Container: `ecommerce_mongodb`
- Port: 27017
- Credentials: admin/password123
- Database: ecommerce_ai

### Nginx (Reverse Proxy)
- Container: `ecommerce_nginx`
- Port: 80
- Routes:
  - `/` → Frontend
  - `/api/` → Backend API
  - `/admin/` → Django Admin

## Development Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Shell into containers
docker-compose exec backend bash
docker-compose exec frontend sh
```

## Database Management

```bash
# Access MongoDB shell
docker-compose exec mongodb mongosh -u admin -p password123

# Run Django migrations
docker-compose exec backend python manage.py migrate

# Create Django superuser
docker-compose exec backend python manage.py createsuperuser
```

## Network Architecture

All services communicate through the `app-network` Docker network:
- Frontend connects to backend via Nginx proxy
- Backend connects to MongoDB using container name resolution
- Nginx routes traffic between frontend and backend

## Troubleshooting

1. **Port conflicts**: Change ports in docker-compose.yml if needed
2. **Permission issues**: Ensure Docker has proper permissions
3. **MongoDB connection**: Check MongoDB container logs if backend can't connect
4. **Hot reload not working**: Ensure volume mounts are correct

## Production Notes

For production deployment:
1. Change MongoDB credentials
2. Set DEBUG=False in backend environment
3. Use production-grade secrets management
4. Configure proper SSL certificates
5. Use production builds for frontend
