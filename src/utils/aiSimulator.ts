import { products } from '../data/products';
import { Product, AIResponse } from '../types';

const responses = [
  "I'd be happy to help you find the perfect product! Based on what you're looking for, here are my top recommendations:",
  "Great choice! I've found some fantastic options that match your needs perfectly:",
  "Excellent! Let me show you some products I think you'll love:",
  "Perfect! I've curated these items specifically for you:",
  "Wonderful! Here are some great options that fit your criteria:",
];

const getRandomResponse = (): string => {
  return responses[Math.floor(Math.random() * responses.length)];
};

const findRelevantProducts = (query: string): Product[] => {
  const keywords = query.toLowerCase().split(' ');
  const scored = products.map(product => {
    let score = 0;
    const searchText = `${product.name} ${product.description} ${product.tags.join(' ')}`
      .toLowerCase();
    
    keywords.forEach(keyword => {
      if (searchText.includes(keyword)) {
        score += 1;
      }
    });
    
    return { product, score };
  });
  
  // Sort by score and return top 5
  return scored
    .filter(item => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)
    .map(item => item.product);
};

const getFallbackProducts = (): Product[] => {
  // Return random selection if no matches found
  const shuffled = [...products].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, 4);
};

export const simulateAIResponse = async (query: string): Promise<AIResponse> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
  
  const relevantProducts = findRelevantProducts(query);
  const finalProducts = relevantProducts.length > 0 ? relevantProducts : getFallbackProducts();
  
  return {
    response: getRandomResponse(),
    products: finalProducts
  };
};