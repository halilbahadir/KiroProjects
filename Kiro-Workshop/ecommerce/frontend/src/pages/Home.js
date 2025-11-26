import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
  const [products, setProducts] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:3001/api/products')
      .then(res => res.json())
      .then(data => setProducts(data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="container">
      <h2>Featured Products</h2>
      <div className="product-grid">
        {products.map(product => (
          <div key={product.id} className="product-card" onClick={() => navigate(`/product/${product.id}`)}>
            <div className="product-emoji">{product.emoji}</div>
            <h3>{product.name}</h3>
            <p className="price">${product.price}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Home;
