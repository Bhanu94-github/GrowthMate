import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getStudentDashboardData } from '../api/api';
import './DashboardPage.css'; // Common dashboard CSS
import './StudentDashboardPage.css'; // Specific student dashboard CSS

function StudentDashboardPage() {
  const [studentData, setStudentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('token'); // Retrieve token
        if (!token) {
          navigate('/signin'); // Redirect if not authenticated
          return;
        }

        const response = await getStudentDashboardData(token);
        setStudentData(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching student dashboard data:', err);
        setError(err.response?.data?.error || err.message || 'Failed to fetch dashboard data.');
        setLoading(false);
        // If 401 Unauthorized, clear token and redirect to login
        if (err.response && err.response.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          navigate('/signin');
        }
      }
    };

    fetchDashboardData();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/signin');
  };

  if (loading) {
    return <div className="loading-spinner">Loading student dashboard...</div>;
  }

  if (error) {
    return <div className="error-message">Error: {error}</div>;
  }

  if (!studentData) {
    return <div className="unauthorized-message">Unauthorized or data not found. Please log in.</div>;
  }

  const aiTokens = studentData.ai_tokens || {};

  return (
    <div className="dashboard-page student-dashboard">
      <div className="dashboard-header">
        <h2>Welcome, {studentData.name || studentData.username}!</h2>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>

      <div className="token-summary">
        <div className="token-card">
          <h3>Overall Tokens</h3>
          <p>{studentData.tokens || 0}</p>
        </div>
        <div className="token-card">
          <h3>AI Module Tokens</h3>
          <p>{(aiTokens['Text_to_Text'] || 0) + (aiTokens['Voice_to_Voice'] || 0) + (aiTokens['Face_to_Face'] || 0)}</p>
        </div>
        <div className="token-card">
          <h3>Exams Taken</h3>
          <p>{studentData.exam_attempts || 0}</p>
        </div>
      </div>

      <div className="module-token-details">
        <h4>Module-wise Token Balance</h4>
        <div className="module-token-grid">
          <div className="module-token-item">
            <span>Text-to-Text:</span> <strong>{aiTokens['Text_to_Text'] || 0}</strong>
          </div>
          <div className="module-token-item">
            <span>Voice-to-Voice:</span> <strong>{aiTokens['Voice_to_Voice'] || 0}</strong>
          </div>
          <div className="module-token-item">
            <span>Face-to-Face:</span> <strong>{aiTokens['Face_to_Face'] || 0}</strong>
          </div>
        </div>
      </div>

      <div className="dashboard-section">
        <h3>Your Progress</h3>
        {studentData.progress && studentData.progress.length > 0 ? (
          <ul>
            {studentData.progress.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        ) : (
          <p>No progress recorded yet.</p>
        )}
      </div>

      {/* Add more sections like submitted essays, feedback, notifications */}
    </div>
  );
}

export default StudentDashboardPage;