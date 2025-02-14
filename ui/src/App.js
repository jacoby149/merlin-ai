import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [products, setProducts] = useState([]);
  const [newProduct, setNewProduct] = useState({ name: '', description: '', price: '', stock: '' });
  const [updateProductId, setUpdateProductId] = useState(null);
  const [updateProduct, setUpdateProduct] = useState({ name: '', description: '', price: '', stock: '' });
  const [isAddProductVisible, setIsAddProductVisible] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/products')
      .then(response => response.json())
      .then(data => setProducts(data))
      .catch(error => console.error('Error fetching products:', error));
  }, []);

  const handleAddProduct = () => {
    const product = {
      id: products.length + 1, // Simple ID generation
      ...newProduct,
      price: parseFloat(newProduct.price),
      stock: parseInt(newProduct.stock),
    };
    fetch('http://localhost:8000/products', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(product),
    })
      .then(response => response.json())
      .then(data => {
        setProducts([...products, data]);
        setNewProduct({ name: '', description: '', price: '', stock: '' });
      })
      .catch(error => console.error('Error adding product:', error));
  };

  const handleUpdateProduct = () => {
    const updatedProduct = {
      id: updateProductId,
      ...updateProduct,
      price: parseFloat(updateProduct.price),
      stock: parseInt(updateProduct.stock),
    };
    fetch(`http://localhost:8000/products/${updateProductId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedProduct),
    })
      .then(response => response.json())
      .then(data => {
        setProducts(products.map(product => (product.id === updateProductId ? data : product)));
        setUpdateProductId(null);
        setUpdateProduct({ name: '', description: '', price: '', stock: '' });
      })
      .catch(error => console.error('Error updating product:', error));
  };

  const handleDeleteProduct = (id) => {
    fetch(`http://localhost:8000/products/${id}`, {
      method: 'DELETE',
    })
      .then(() => {
        setProducts(products.filter(product => product.id !== id));
      })
      .catch(error => console.error('Error deleting product:', error));
  };

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <div style={{ display: 'flex', fontFamily: 'Arial, sans-serif', backgroundColor: isDarkMode ? '#121212' : '#E8F0FE', minHeight: '100vh', color: isDarkMode ? 'white' : '#333' }}>
      <div style={{ flex: 1, padding: '20px' }}>
        <div style={{ backgroundColor: '#4A90E2', padding: '10px', color: 'white', textAlign: 'center', borderRadius: '8px', marginBottom: '20px' }}>
          <h1>🧙 Merlin Auto Generated App</h1>
        </div>
        <div style={{ marginTop: '20px', maxWidth: '600px', margin: '0 auto' }}>
          <h2 onClick={() => setIsAddProductVisible(!isAddProductVisible)} style={{ cursor: 'pointer', color: '#4A90E2' }}>
            {isAddProductVisible ? 'Hide New Product' : 'Add New Product'}
          </h2>
          {isAddProductVisible && (
            <div style={{ display: 'flex', flexDirection: 'column', marginBottom: '20px', backgroundColor: '#fff', padding: '15px', borderRadius: '5px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <input style={{ marginBottom: '10px', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', flex: '1', marginRight: '10px' }} type="text" placeholder="Name" value={newProduct.name} onChange={e => setNewProduct({ ...newProduct, name: e.target.value })} />
                <input style={{ marginBottom: '10px', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', flex: '1' }} type="text" placeholder="Description" value={newProduct.description} onChange={e => setNewProduct({ ...newProduct, description: e.target.value })} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <input style={{ marginBottom: '10px', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', flex: '1', marginRight: '10px' }} type="number" placeholder="Price" value={newProduct.price} onChange={e => setNewProduct({ ...newProduct, price: e.target.value })} />
                <input style={{ marginBottom: '10px', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', flex: '1' }} type="number" placeholder="Stock" value={newProduct.stock} onChange={e => setNewProduct({ ...newProduct, stock: e.target.value })} />
              </div>
              <button style={{ padding: '10px', backgroundColor: '#5C6BC0', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }} onClick={handleAddProduct}>Add Product</button>
            </div>
          )}

          <h2 style={{ color: '#4A90E2' }}>Available Products</h2>
          <ul style={{ listStyleType: 'none', padding: 0 }}>
            {products.map(product => (
              <li key={product.id} style={{ backgroundColor: '#fff', margin: '10px 0', padding: '15px', borderRadius: '5px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
                <h3 style={{ color: '#4A90E2' }}>{product.name}</h3>
                <p>{product.description}</p>
                <p><strong>Price:</strong> ${product.price.toFixed(2)}</p>
                <p><strong>Stock:</strong> {product.stock}</p>
                <button style={{ marginRight: '10px', padding: '10px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }} onClick={() => handleDeleteProduct(product.id)}>Delete</button>
                <button style={{ padding: '10px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }} onClick={() => { setUpdateProductId(product.id); setUpdateProduct({ name: product.name, description: product.description, price: product.price, stock: product.stock }); }}>Edit</button>
              </li>
            ))}
          </ul>

          {updateProductId && (
            <div style={{ marginTop: '20px' }}>
              <h2 style={{ color: '#4A90E2' }}>Update Product</h2>
              <div style={{ display: 'flex', flexDirection: 'column', maxWidth: '400px' }}>
                <input style={{ marginBottom: '10px', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} type="text" placeholder="Name" value={updateProduct.name} onChange={e => setUpdateProduct({ ...updateProduct, name: e.target.value })} />
                <input style={{ marginBottom: '10px', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} type="text" placeholder="Description" value={updateProduct.description} onChange={e => setUpdateProduct({ ...updateProduct, description: e.target.value })} />
                <input style={{ marginBottom: '10px', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} type="number" placeholder="Price" value={updateProduct.price} onChange={e => setUpdateProduct({ ...updateProduct, price: e.target.value })} />
                <input style={{ marginBottom: '10px', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} type="number" placeholder="Stock" value={updateProduct.stock} onChange={e => setUpdateProduct({ ...updateProduct, stock: e.target.value })} />
                <button style={{ padding: '10px', backgroundColor: '#FFC107', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }} onClick={handleUpdateProduct}>Update Product</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;