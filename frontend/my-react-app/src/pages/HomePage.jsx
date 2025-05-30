import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css'; // Create this CSS file

function HomePage() {
  return (
    <div className="home-page">
      <section className="hero-section">
        <h1>Welcome to GrowthMate AI</h1>
        <p className="tagline">Unlock Your Potential with AI-Driven Learning</p>
        <div className="hero-buttons">
          <Link to="/register" className="btn primary-btn">Get Started</Link>
          <Link to="/about" className="btn secondary-btn">Learn More</Link>
        </div>
      </section>

      <section className="intro-section">
        <h2>Your Journey to Mastery Begins Here</h2>
        <p>
          GrowthMate AI is a cutting-edge platform designed to revolutionize how you learn,
          assess, and grow. Leveraging advanced artificial intelligence, we provide
          personalized experiences that adapt to your unique needs and pace.
        </p>
      </section>

      <section className="cta-section">
        <h3>Ready to Transform Your Learning?</h3>
        <Link to="/modules" className="btn cta-btn">Explore AI Modules</Link>
      </section>
    </div>
  );
}

export default HomePage;