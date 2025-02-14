import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/products')
      .then(response => response.json())
      .then(data => setProducts(data))
      .catch(error => console.error('Error fetching products:', error));
  }, []);

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', backgroundColor: '#f4f4f4', minHeight: '100vh', padding: '20px' }}>
      <div style={{ backgroundColor: '#282c34', padding: '10px', color: 'white', textAlign: 'center' }}>
        <h1>Product Store</h1>
      </div>
      <div style={{ marginTop: '20px' }}>
        <h2>Available Products</h2>
        <ul style={{ listStyleType: 'none', padding: 0 }}>
          {products.map(product => (
            <li key={product.id} style={{ backgroundColor: '#fff', margin: '10px 0', padding: '15px', borderRadius: '5px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
              <h3>{product.name}</h3>
              <p>{product.description}</p>
              <p><strong>Price:</strong> ${product.price.toFixed(2)}</p>
              <p><strong>Stock:</strong> {product.stock}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;