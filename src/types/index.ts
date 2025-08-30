export interface Product {
  id: string;  // Changed to string for MongoDB ObjectId
  name: string;
  description: string;
  price: number | string;  // Allow both number and string for price
  image_url: string;
  tags: string[];
  category: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  products?: Product[];
}

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface AIResponse {
  response: string;
  products: Product[];
}