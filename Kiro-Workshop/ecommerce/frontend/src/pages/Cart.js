import React, { useState, useEffect } from 'react';

function Cart() {
  const [cartItems, setCartItems] = useState([]);

  const fetchCart = () => {
    fetch('http://localhost:3001/api/cart')
      .then(res => res.json())
      .then(data => setCartItems(data))
      .catch(err => console.error(err));
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const updateQuantity = (id, quantity) => {
    fetch(`http://localhost:3001/api/cart/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ quantity })
    })
      .then(() => fetchCart())
      .catch(err => console.error(err));
  };

  const removeItem = (id) => {
    fetch(`http://localhost:3001/api/cart/${id}`, { method: 'DELETE' })
      .then(() => fetchCart())
      .catch(err => console.error(err));
  };

  const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return (
    <div className="container">
      <h2>Shopping Cart</h2>
      {cartItems.length === 0 ? (
        <p>Your cart is empty</p>
      ) : (
        <>
          <div className="cart-items">
            {cartItems.map(item => (
              <div key={item.id} className="cart-item">
                <div className="cart-item-emoji">{item.emoji}</div>
                <div className="cart-item-info">
                  <h3>{item.name}</h3>
                  <p className="price">${item.price}</p>
                </div>
                <div className="cart-item-actions">
                  <div className="quantity-selector">
                    <button onClick={() => updateQuantity(item.id, Math.max(1, item.quantity - 1))}>-</button>
                    <input type="number" value={item.quantity} onChange={(e) => updateQuantity(item.id, Math.max(1, parseInt(e.target.value) || 1))} />
                    <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>+</button>
                  </div>
                  <button className="btn btn-danger" onClick={() => removeItem(item.id)}>Remove</button>
                </div>
              </div>
            ))}
          </div>
          <div className="cart-summary">
            <h2>Total: ${total.toFixed(2)}</h2>
            <button className="btn btn-primary">Proceed to Checkout</button>
          </div>
        </>
      )}
    </div>
  );
}

export default Cart;
