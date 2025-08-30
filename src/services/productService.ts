import { apiService, APIProduct } from './api';
import { Product, AIResponse } from '../types';

// Transform API product to frontend product format
const transformProduct = (apiProduct: APIProduct): Product => ({
  id: apiProduct.id,
  name: apiProduct.name,
  description: apiProduct.description,
  price: parseFloat(apiProduct.price),
  image_url: apiProduct.image_url,
  tags: apiProduct.tags,
  category: apiProduct.category,
});

export class ProductService {
  private sessionId: string | null = null;

  async initializeSession(): Promise<string> {
    if (!this.sessionId) {
      try {
        const response = await apiService.createChatSession();
        this.sessionId = response.session_id;
      } catch (error) {
        console.error('Failed to create session:', error);
        // Generate a fallback session ID
        this.sessionId = `fallback-${Date.now()}`;
      }
    }
    return this.sessionId;
  }

  async getProducts(filters?: { category?: string; search?: string }): Promise<Product[]> {
    try {
      console.log('ProductService: Fetching products with filters:', filters);
      const apiResponse = await apiService.getProducts(filters);
      console.log('ProductService: Raw API response:', apiResponse);
      console.log('ProductService: API response type:', typeof apiResponse);
      console.log('ProductService: Is array?', Array.isArray(apiResponse));
      
      // Handle different response formats
      let apiProducts = apiResponse;
      
      // Check if response is wrapped (e.g., { results: [], count: 10 })
      if (apiResponse && typeof apiResponse === 'object' && !Array.isArray(apiResponse)) {
        if (apiResponse.results && Array.isArray(apiResponse.results)) {
          apiProducts = apiResponse.results;
          console.log('ProductService: Using results array from wrapped response');
        } else if (apiResponse.data && Array.isArray(apiResponse.data)) {
          apiProducts = apiResponse.data;
          console.log('ProductService: Using data array from wrapped response');
        } else {
          console.error('ProductService: API response is not an array and has no results/data array:', apiResponse);
          return [];
        }
      }
      
      if (!Array.isArray(apiProducts)) {
        console.error('ProductService: API response is not an array:', apiProducts);
        return [];
      }
      
      console.log('ProductService: Processing products array:', apiProducts);
      console.log('ProductService: Array length:', apiProducts.length);
      
      const transformedProducts = apiProducts.map(transformProduct);
      console.log('ProductService: Transformed products:', transformedProducts);
      return transformedProducts;
    } catch (error) {
      console.error('Failed to fetch products:', error);
      return [];
    }
  }

  async getProduct(id: number): Promise<Product | null> {
    try {
      const apiProduct = await apiService.getProduct(id);
      return transformProduct(apiProduct);
    } catch (error) {
      console.error('Failed to fetch product:', error);
      return null;
    }
  }

  async getChatRecommendations(message: string): Promise<AIResponse> {
    try {
      await this.initializeSession();
      
      const response = await apiService.getChatRecommendations({
        message,
        session_id: this.sessionId!,
      });

      return {
        response: response.response,
        products: response.products.map(transformProduct),
      };
    } catch (error) {
      console.error('Failed to get AI recommendations:', error);
      
      // Fallback response
      return {
        response: "I'm having trouble connecting to our recommendation service right now. Here are some popular products you might like:",
        products: await this.getProducts(),
      };
    }
  }

  async addToCart(product: Product, quantity: number = 1): Promise<boolean> {
    try {
      await this.initializeSession();
      await apiService.addToCart(product.id, quantity, this.sessionId!);
      return true;
    } catch (error) {
      console.error('Failed to add to cart:', error);
      return false;
    }
  }

  getSessionId(): string | null {
    return this.sessionId;
  }

  // Admin methods
  async createProduct(product: Omit<Product, 'id'>): Promise<Product | null> {
    try {
      const apiProduct = await apiService.createProduct({
        name: product.name,
        description: product.description,
        price: product.price.toString(),
        image_url: product.image_url,
        tags: product.tags,
        category: product.category,
      });
      return transformProduct(apiProduct);
    } catch (error) {
      console.error('Failed to create product:', error);
      return null;
    }
  }

  async updateProduct(id: string, updates: Partial<Product>): Promise<Product | null> {
    try {
      const apiUpdates: Partial<APIProduct> = {};
      if (updates.name !== undefined) apiUpdates.name = updates.name;
      if (updates.description !== undefined) apiUpdates.description = updates.description;
      if (updates.price !== undefined) apiUpdates.price = updates.price.toString();
      if (updates.image_url !== undefined) apiUpdates.image_url = updates.image_url;
      if (updates.tags !== undefined) apiUpdates.tags = updates.tags;
      if (updates.category !== undefined) apiUpdates.category = updates.category;

      const apiProduct = await apiService.updateProduct(parseInt(id), apiUpdates);
      return transformProduct(apiProduct);
    } catch (error) {
      console.error('Failed to update product:', error);
      return null;
    }
  }

  async deleteProduct(id: string): Promise<boolean> {
    try {
      await apiService.deleteProduct(parseInt(id));
      return true;
    } catch (error) {
      console.error('Failed to delete product:', error);
      return false;
    }
  }
}

export const productService = new ProductService();
