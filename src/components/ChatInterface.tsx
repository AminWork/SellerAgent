import React, { useState, useRef, useEffect } from 'react';
import { Send, RotateCcw, MessageCircle } from 'lucide-react';
import { ChatMessage as ChatMessageType } from '../types';
import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';
import { productService } from '../services/productService';

interface ChatInterfaceProps {
  onAddToCart: (product: any) => void;
  isExpanded: boolean;
  onToggleExpand: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  onAddToCart, 
  isExpanded, 
  onToggleExpand 
}) => {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    if (!isExpanded) {
      onToggleExpand();
    }

    try {
      const aiResponse = await productService.getChatRecommendations(userMessage.content);
      
      const aiMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: aiResponse.response,
        timestamp: new Date(),
        products: aiResponse.products
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error getting AI response:', error);
      const errorMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: "I'm sorry, I encountered an error. Please try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const resetChat = () => {
    setMessages([]);
    setInputValue('');
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const hasMessages = messages.length > 0 || isLoading;

  return (
    <div className={`transition-all duration-500 ease-out ${
      isExpanded 
        ? 'fixed inset-4 md:inset-8 bg-white/90 backdrop-blur-md rounded-3xl shadow-2xl border border-gray-200/30 z-30 flex flex-col' 
        : 'w-full max-w-3xl mx-auto'
    }`}>
      {!isExpanded && !hasMessages && (
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl mb-8 shadow-lg">
            <MessageCircle size={36} className="text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            AI Shopping Assistant
          </h1>
          <p className="text-gray-600 text-xl font-medium mb-2">
            Find your perfect products with AI
          </p>
          <p className="text-gray-500 text-base">
            Just describe what you're looking for and I'll help you discover amazing products
          </p>
        </div>
      )}

      {isExpanded && hasMessages && (
        <div className="flex items-center justify-between p-6 border-b border-gray-100 rounded-t-3xl bg-gradient-to-r from-blue-50/80 to-purple-50/80">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <MessageCircle size={18} className="text-white" />
            </div>
            <h2 className="font-bold text-gray-900">AI Shopping Assistant</h2>
          </div>
          <button
            onClick={resetChat}
            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-white/80 rounded-xl transition-all duration-200 hover:scale-105 shadow-sm border border-gray-200/50"
          >
            <RotateCcw size={16} />
            New Chat
          </button>
        </div>
      )}

      {isExpanded && hasMessages && (
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-transparent to-gray-50/30">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              onAddToCart={onAddToCart}
            />
          ))}
          {isLoading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>
      )}

      <div className={`${isExpanded && hasMessages ? 'border-t border-gray-100 rounded-b-3xl bg-white/80' : ''} p-6`}>
        <form onSubmit={handleSubmit} className="relative">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="What are you looking for today? 🛍️"
            className="w-full px-6 py-4 pr-16 border-2 border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 bg-white/80 backdrop-blur-sm shadow-sm transition-all duration-200 hover:shadow-md"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:hover:from-blue-600 disabled:hover:to-purple-600 transition-all duration-200 hover:scale-105 shadow-lg"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};