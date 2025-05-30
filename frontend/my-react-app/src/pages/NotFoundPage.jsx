import React from 'react';
import { Link } from 'react-router-dom';
import './NotFoundPage.css'; // Create this CSS file

function NotFoundPage() {
  return (
    <div className="not-found-page">
      <h1>404</h1>
      <h2>Page Not Found</h2>
      <p>Oops! The page you are looking for does not exist.</p>
      <Link to="/" className="btn home-btn">Go to Home</Link>
    </div>
  );
}

export default NotFoundPage;