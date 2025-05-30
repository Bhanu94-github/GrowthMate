import React from 'react';
import { Link } from 'react-router-dom';
import './ModulesPage.css'; // Create this CSS file

function ModulesPage() {
  return (
    <div className="modules-page">
      <h2>Our AI Modules</h2>
      <p className="module-intro">
        Explore GrowthMate AI's powerful modules designed to enhance your skills and provide
        intelligent feedback.
      </p>

      <div className="module-grid">
        <div className="module-card">
          <h3>Text to Text</h3>
          <p>
            Engage with AI through text-based interactions for learning, content generation,
            and comprehensive assessments. Receive detailed feedback on your written responses.
          </p>
          <Link to="/modules/text-to-text" className="btn module-btn">Start Text Module</Link>
        </div>

        <div className="module-card">
          <h3>Voice to Voice</h3>
          <p>
            Practice your communication skills with an AI interviewer. Upload your resume,
            answer questions verbally, and get instant voice-based feedback.
          </p>
          <Link to="/modules/voice-to-voice" className="btn module-btn">Start Voice Module</Link>
        </div>

        <div className="module-card coming-soon">
          <h3>Face to Face</h3>
          <p>
            Experience realistic AI interviews with facial expression analysis and real-time
            interactive feedback. (Coming Soon!)
          </p>
          <button className="btn module-btn disabled" disabled>Coming Soon</button>
        </div>
      </div>

      <p className="module-cta">
        To access these modules, please <Link to="/signin">sign in</Link> or <Link to="/register">register</Link>.
      </p>
    </div>
  );
}

export default ModulesPage;