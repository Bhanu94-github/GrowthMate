import React from 'react';
import Navbar from './Navbar';
import './Layout.css'; // You can add basic layout styles

function Layout({ children }) {
  return (
    <div className="layout">
      <Navbar />
      <div className="content">
        {children}
      </div>
      {/* You can add a Footer component here if needed */}
    </div>
  );
}

export default Layout;