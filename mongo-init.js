// MongoDB initialization script
db = db.getSiblingDB('ecommerce_ai');

// Create a user for the application database
db.createUser({
  user: 'admin',
  pwd: 'password123',
  roles: [
    {
      role: 'readWrite',
      db: 'ecommerce_ai'
    }
  ]
});

// Create initial collections if needed
db.createCollection('products');
db.createCollection('users');
db.createCollection('orders');

print('Database initialized successfully');
