import React, { useState, useEffect } from 'react';
import { ShoppingCart } from 'lucide-react';
import { ChatInterface } from './components/ChatInterface';
import { CartDrawer } from './components/CartDrawer';
import { AdminPanel } from './components/AdminPanel';
import { useCart } from './hooks/useCart';

function App() {
  const [isChatExpanded, setIsChatExpanded] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [showAddedToCart, setShowAddedToCart] = useState(false);
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  const {
    cartItems,
    addToCart,
    removeFromCart,
    updateQuantity,
    getTotalItems,
    getTotalPrice
  } = useCart();

  const handleAddToCart = (product: any) => {
    addToCart(product);
    setShowAddedToCart(true);
    setTimeout(() => setShowAddedToCart(false), 2000);
  };

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const toggleChatExpand = () => {
    setIsChatExpanded(!isChatExpanded);
  };

  // If we're on /admin route, show only the admin panel
  if (currentPath === '/admin') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white">
        <AdminPanel />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white">
      {/* Header */}
      <header className="relative z-20 flex items-center justify-between p-4 md:p-6 bg-white/95 border-b border-gray-100 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
            <span className="text-white font-bold text-lg">🛍️</span>
          </div>
          <div>
            <span className="font-bold text-xl text-gray-900">ShopAI</span>
            <p className="text-xs text-gray-500 -mt-1">Your Smart Shopping Assistant</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Cart Button */}
          <button
            onClick={() => setIsCartOpen(true)}
            className="relative p-3 hover:bg-blue-50 rounded-xl transition-all duration-200 hover:scale-105 bg-white shadow-sm border border-gray-100"
          >
            <ShoppingCart size={24} className="text-blue-600" />
            {getTotalItems() > 0 && (
              <span className="absolute -top-2 -right-2 bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold shadow-lg animate-pulse">
                {getTotalItems()}
              </span>
            )}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className={`relative z-10 ${isChatExpanded ? '' : 'flex items-center justify-center min-h-[calc(100vh-120px)] p-4'}`}>
        <ChatInterface
          onAddToCart={handleAddToCart}
          isExpanded={isChatExpanded}
          onToggleExpand={toggleChatExpand}
        />
      </main>

      {/* Cart Drawer */}
      <CartDrawer
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        cartItems={cartItems}
        onUpdateQuantity={updateQuantity}
        onRemoveItem={removeFromCart}
        totalPrice={getTotalPrice()}
      />

      {/* Added to Cart Notification */}
      {showAddedToCart && (
        <div className="fixed bottom-6 right-6 bg-gradient-to-r from-green-500 to-emerald-500 text-white px-6 py-3 rounded-xl shadow-lg z-50 transform transition-all duration-300 animate-bounce">
          <div className="flex items-center gap-2">
            <span className="text-lg">✓</span>
            <span className="font-medium">Added to cart!</span>
          </div>
        </div>
      )}


    </div>
  );
}

export default App;