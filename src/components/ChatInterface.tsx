import React, { useState, useRef, useEffect } from 'react';
import { Send, RotateCcw, MessageCircle } from 'lucide-react';
import { ChatMessage as ChatMessageType } from '../types';
import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';
import { simulateAIResponse } from '../utils/aiSimulator';

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
      const aiResponse = await simulateAIResponse(userMessage.content);
      
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
        ? 'fixed inset-4 md:inset-8 bg-white rounded-2xl shadow-2xl z-30 flex flex-col' 
        : 'w-full max-w-2xl mx-auto'
    }`}>
      {!isExpanded && !hasMessages && (
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-black rounded-full mb-6">
            <MessageCircle size={32} className="text-white" />
          </div>
          <h1 className="text-3xl md:text-4xl font-light text-gray-900 mb-3">
            AI Shopping Assistant
          </h1>
          <p className="text-gray-500 text-lg font-light">
            Describe what you're looking for
          </p>
        </div>
      )}

      {isExpanded && hasMessages && (
        <div className="flex items-center justify-between p-4 border-b rounded-t-2xl">
          <h2 className="font-medium text-gray-900">AI Shopping Assistant</h2>
          <button
            onClick={resetChat}
            className="flex items-center gap-2 px-3 py-1 text-sm text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <RotateCcw size={16} />
            Reset
          </button>
        </div>
      )}

      {isExpanded && hasMessages && (
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
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

      <div className={`${isExpanded && hasMessages ? 'border-t rounded-b-2xl' : ''} p-4`}>
        <form onSubmit={handleSubmit} className="relative">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Describe your perfect product..."
            className="w-full px-4 py-3 pr-12 border border-gray-200 rounded-2xl focus:outline-none focus:ring-1 focus:ring-black focus:border-transparent text-gray-900 placeholder-gray-400"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-black text-white rounded-full hover:bg-gray-800 disabled:opacity-50 disabled:hover:bg-black transition-colors"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};