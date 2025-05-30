import React from 'react';
import { Navigate } from 'react-router-dom';

function PrivateRoute({ children }) {
  const isAuthenticated = localStorage.getItem('token'); // Check if the user is authenticated

  return isAuthenticated ? children : <Navigate to="/signin" />;
}

export default PrivateRoute;