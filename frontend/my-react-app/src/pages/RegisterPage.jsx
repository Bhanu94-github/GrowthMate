import React from 'react';
import AuthForm from '../components/AuthForm';
import './AuthPages.css'; // Common CSS for auth forms

function RegisterPage() {
  return (
    <div className="auth-page register-page">
      <AuthForm isLogin={false} />
    </div>
  );
}

export default RegisterPage;