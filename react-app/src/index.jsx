/**
 * Entry point — renders App into #root and imports global styles.
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/style.css';
import './styles/product.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
