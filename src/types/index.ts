export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
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