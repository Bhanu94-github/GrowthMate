import React from 'react';
import AuthForm from '../components/AuthForm';
import './AuthPages.css'; // Common CSS for auth forms

function SignInPage() {
  return (
    <div className="auth-page signin-page">
      <AuthForm isLogin={true} />
    </div>
  );
}

export default SignInPage;