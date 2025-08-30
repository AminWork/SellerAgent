const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || '/api';

export interface APIProduct {
  id: number;
  name: string;
  description: string;
  price: string;
  image_url: string;
  tags: string[];
  category: string;
}

export interface APIResponse<T> {
  data: T;
  message?: string;
}

export interface ChatRecommendationRequest {
  message: string;
  session_id?: string;
}

export interface ChatRecommendationResponse {
  response: string;
  products: APIProduct[];
  session_id: string;
}

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Product API methods
  async getProducts(params?: { category?: string; search?: string }): Promise<APIProduct[]> {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.append('category', params.category);
    if (params?.search) searchParams.append('search', params.search);
    
    const queryString = searchParams.toString();
    const endpoint = `/products/${queryString ? `?${queryString}` : ''}`;
    
    console.log('API: Fetching products from endpoint:', `${API_BASE_URL}${endpoint}`);
    const result = await this.request<APIProduct[]>(endpoint);
    console.log('API: Raw response from products endpoint:', result);
    return result;
  }

  async getProduct(id: number): Promise<APIProduct> {
    return this.request<APIProduct>(`/products/${id}/`);
  }

  // Admin Product API methods
  async createProduct(product: Omit<APIProduct, 'id'>): Promise<APIProduct> {
    return this.request<APIProduct>('/admin/products/', {
      method: 'POST',
      body: JSON.stringify(product),
    });
  }

  async updateProduct(id: number, product: Partial<APIProduct>): Promise<APIProduct> {
    return this.request<APIProduct>(`/admin/products/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(product),
    });
  }

  async deleteProduct(id: number): Promise<void> {
    return this.request<void>(`/admin/products/${id}/`, {
      method: 'DELETE',
    });
  }

  // Chat API methods
  async createChatSession(): Promise<{ session_id: string }> {
    return this.request<{ session_id: string }>('/sessions/', {
      method: 'POST',
    });
  }

  async getChatRecommendations(data: ChatRecommendationRequest): Promise<ChatRecommendationResponse> {
    return this.request<ChatRecommendationResponse>('/recommend/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getConversation(sessionId: string): Promise<any[]> {
    return this.request<any[]>(`/conversation/${sessionId}/`);
  }

  // Cart API methods
  async getCartItems(sessionId?: string): Promise<any[]> {
    const endpoint = sessionId ? `/cart/?session_id=${sessionId}` : '/cart/';
    return this.request<any[]>(endpoint);
  }

  async addToCart(productId: number, quantity: number = 1, sessionId?: string): Promise<any> {
    return this.request<any>('/cart/', {
      method: 'POST',
      body: JSON.stringify({
        product_id: productId,
        quantity,
        session_id: sessionId,
      }),
    });
  }

  async updateCartItem(id: number, quantity: number): Promise<any> {
    return this.request<any>(`/cart/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify({ quantity }),
    });
  }

  async removeFromCart(id: number): Promise<void> {
    return this.request<void>(`/cart/${id}/`, {
      method: 'DELETE',
    });
  }

  async clearCart(sessionId?: string): Promise<void> {
    const endpoint = sessionId ? `/cart/clear/?session_id=${sessionId}` : '/cart/clear/';
    return this.request<void>(endpoint, {
      method: 'POST',
    });
  }
}

export const apiService = new ApiService();
