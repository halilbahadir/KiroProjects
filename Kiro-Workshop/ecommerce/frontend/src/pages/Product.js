import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function Product() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    fetch(`http://localhost:3001/api/products/${id}`)
      .then(res => res.json())
      .then(data => setProduct(data))
      .catch(err => console.error(err));
  }, [id]);

  const addToCart = () => {
    fetch('http://localhost:3001/api/cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: id, quantity })
    })
      .then(() => {
        alert('Added to cart!');
        navigate('/cart');
      })
      .catch(err => console.error(err));
  };

  if (!product) return <div className="container">Loading...</div>;

  const reviews = [
    { name: 'John D.', rating: 5, comment: 'Excellent product! Highly recommend.' },
    { name: 'Sarah M.', rating: 4, comment: 'Good quality, fast shipping.' },
    { name: 'Mike R.', rating: 5, comment: 'Best purchase I made this year!' }
  ];

  return (
    <div className="container">
      <div className="product-detail">
        <div className="product-detail-content">
          <div className="product-detail-emoji">{product.emoji}</div>
          <div className="product-info">
            <h1>{product.name}</h1>
            <p className="price">${product.price}</p>
            <p>{product.description}</p>
            <p><strong>Category:</strong> {product.category}</p>
            
            <div className="quantity-selector">
              <button onClick={() => setQuantity(Math.max(1, quantity - 1))}>-</button>
              <input type="number" value={quantity} onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))} />
              <button onClick={() => setQuantity(quantity + 1)}>+</button>
            </div>
            
            <button className="btn btn-primary" onClick={addToCart}>Add to Cart</button>
          </div>
        </div>

        <div className="reviews">
          <h2>Customer Reviews</h2>
          {reviews.map((review, idx) => (
            <div key={idx} className="review">
              <div className="review-header">
                <strong>{review.name}</strong>
                <span className="stars">{'⭐'.repeat(review.rating)}</span>
              </div>
              <p>{review.comment}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Product;
