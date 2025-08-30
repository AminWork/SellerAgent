import React from 'react';

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex items-start gap-4 animate-pulse">
      <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex-shrink-0 flex items-center justify-center shadow-lg">
        <span className="text-white text-sm font-bold">AI</span>
      </div>
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl px-6 py-4 max-w-xs border border-blue-100 shadow-sm">
        <div className="flex gap-1.5">
          <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce"></div>
          <div className="w-2.5 h-2.5 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
        <p className="text-xs text-gray-500 mt-2 font-medium">AI is thinking...</p>
      </div>
    </div>
  );
};