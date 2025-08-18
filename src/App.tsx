import React, { useState } from 'react';
import { ShoppingCart } from 'lucide-react';
import { ChatInterface } from './components/ChatInterface';
import { CartDrawer } from './components/CartDrawer';
import { useCart } from './hooks/useCart';

function App() {
  const [isChatExpanded, setIsChatExpanded] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [showAddedToCart, setShowAddedToCart] = useState(false);

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

  const toggleChatExpand = () => {
    setIsChatExpanded(!isChatExpanded);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="relative z-20 flex items-center justify-between p-4 md:p-6">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">AI</span>
          </div>
          <span className="font-medium text-gray-900">ShopAI</span>
        </div>
        
        <button
          onClick={() => setIsCartOpen(true)}
          className="relative p-2 hover:bg-gray-50 rounded-full transition-colors"
        >
          <ShoppingCart size={24} className="text-gray-700" />
          {getTotalItems() > 0 && (
            <span className="absolute -top-1 -right-1 bg-black text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
              {getTotalItems()}
            </span>
          )}
        </button>
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
        <div className="fixed bottom-4 right-4 bg-black text-white px-4 py-2 rounded-lg shadow-sm z-50 transform transition-all duration-300">
          ✓ Added to cart!
        </div>
      )}

      {/* Overlay for expanded chat */}
      {isChatExpanded && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-20"
          onClick={toggleChatExpand}
        />
      )}
    </div>
  );
}

export default App;