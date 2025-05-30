import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getInstructorDashboardData, updateStudentTokens, getInstructorAnalytics } from '../api/api';
import './DashboardPage.css'; // Common dashboard CSS
import './InstructorDashboardPage.css'; // Specific instructor dashboard CSS

function InstructorDashboardPage() {
  const [instructorData, setInstructorData] = useState(null);
  const [students, setStudents] = useState([]);
  const [tokenLogs, setTokenLogs] = useState([]);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('management'); // 'management', 'logs', 'analytics'

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/signin');
          return;
        }

        // Fetch main dashboard data (students, etc.)
        const dashboardResponse = await getInstructorDashboardData(token);
        setStudents(dashboardResponse.data); // Assuming this endpoint returns a list of students

        // Fetch token logs
        const logsResponse = await getInstructorAnalytics(token); // Re-using analytics endpoint for logs
        setTokenLogs(logsResponse.data.token_logs || []);
        setAnalyticsData(logsResponse.data); // Store full analytics data

        setLoading(false);
      } catch (err) {
        console.error('Error fetching instructor dashboard data:', err);
        setError(err.response?.data?.error || err.message || 'Failed to fetch dashboard data.');
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [navigate]);

  const handleTokenUpdate = async (studentUsername, action, module = null) => {
    try {
      const token = localStorage.getItem('token');
      await updateStudentTokens(token, studentUsername, action, module);
      // Re-fetch data to update UI
      const dashboardResponse = await getInstructorDashboardData(token);
      setStudents(dashboardResponse.data);
      const logsResponse = await getInstructorAnalytics(token);
      setTokenLogs(logsResponse.data.token_logs || []);
      setAnalyticsData(logsResponse.data);
    } catch (err) {
      console.error('Error updating tokens:', err);
      setError(err.response?.data?.error || err.message || 'Failed to update tokens.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user'); // Clear any stored user data
    navigate('/signin');
  };

  if (loading) {
    return <div className="loading-spinner">Loading instructor dashboard...</div>;
  }

  if (error) {
    return <div className="error-message">Error: {error}</div>;
  }

  return (
    <div className="dashboard-page instructor-dashboard">
      <div className="dashboard-header">
        <h2>Instructor Dashboard</h2>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>

      <div className="tab-navigation">
        <button className={activeTab === 'management' ? 'active' : ''} onClick={() => setActiveTab('management')}>Token Management</button>
        <button className={activeTab === 'logs' ? 'active' : ''} onClick={() => setActiveTab('logs')}>Token Logs</button>
        <button className={activeTab === 'analytics' ? 'active' : ''} onClick={() => setActiveTab('analytics')}>Analytics</button>
      </div>

      {activeTab === 'management' && (
        <div className="dashboard-section">
          <h3>Approved Students</h3>
          {students.length === 0 ? (
            <p>No approved students found.</p>
          ) : (
            <div className="student-list">
              {students.map(student => (
                <div key={student.username} className="student-card">
                  <h4>{student.name} ({student.username})</h4>
                  <p>General Tokens: {student.tokens}</p>
                  <div className="token-controls">
                    <button onClick={() => handleTokenUpdate(student.username, 'increment_general_token')}>+1</button>
                    <button onClick={() => handleTokenUpdate(student.username, 'decrement_general_token')}>-1</button>
                    <button onClick={() => handleTokenUpdate(student.username, 'reset_all_tokens')}>Reset All to 15</button>
                  </div>
                  <h5>AI Module Tokens:</h5>
                  <div className="ai-token-grid">
                    {Object.entries(student.ai_tokens || {}).map(([module, count]) => (
                      <div key={module} className="ai-token-item">
                        <span>{module.replace(/_/g, ' ')}: {count}</span>
                        <button onClick={() => handleTokenUpdate(student.username, 'increment_module_token', module)}>+</button>
                        <button onClick={() => handleTokenUpdate(student.username, 'decrement_module_token', module)}>-</button>
                        <button onClick={() => handleTokenUpdate(student.username, 'reset_module_token', module)}>Reset</button>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'logs' && (
        <div className="dashboard-section">
          <h3>Token Change History</h3>
          {tokenLogs.length === 0 ? (
            <p>No token logs found.</p>
          ) : (
            <div className="token-logs-list">
              {tokenLogs.map((log, index) => (
                <div key={index} className="log-item">
                  <p><strong>Student:</strong> {log.student}</p>
                  <p><strong>Action:</strong> {log.action}</p>
                  <p><strong>Module:</strong> {log.module}</p>
                  <p><strong>Tokens Changed:</strong> {log.tokens_changed}</p>
                  <p><strong>Timestamp:</strong> {new Date(log.timestamp).toLocaleString()}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'analytics' && analyticsData && (
        <div className="dashboard-section">
          <h3>Student Performance Analytics</h3>
          {analyticsData.assessment_message ? (
            <p>{analyticsData.assessment_message}</p>
          ) : (
            <>
              <h4>Overall Performance: Average Score {analyticsData.overall_performance?.average_score?.toFixed(2)}</h4>

              <h4>Skill Average Scores</h4>
              <ul>
                {analyticsData.skill_average_scores?.map(item => (
                  <li key={item.skill}>{item.skill}: {item.score?.toFixed(2)}</li>
                ))}
              </ul>

              <h4>Difficulty Average Scores</h4>
              <ul>
                {analyticsData.difficulty_average_scores?.map(item => (
                  <li key={item.difficulty}>{item.difficulty}: {item.score?.toFixed(2)}</li>
                ))}
              </ul>

              <h4>Student Ranking</h4>
              <table>
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Attempts</th>
                    <th>Average Score</th>
                    <th>Max Score</th>
                  </tr>
                </thead>
                <tbody>
                  {analyticsData.student_ranking?.map(student => (
                    <tr key={student.Username}>
                      <td>{student.Username}</td>
                      <td>{student.Attempts}</td>
                      <td>{student['Average Score']?.toFixed(2)}</td>
                      <td>{student['Max Score']}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <h4>Per-Student Skill Breakdown</h4>
              {analyticsData.unique_students_for_comparison && analyticsData.unique_students_for_comparison.length > 0 && (
                <select onChange={(e) => { /* Handle selected student for pie chart */ }}>
                  {analyticsData.unique_students_for_comparison.map(student => (
                    <option key={student} value={student}>{student}</option>
                  ))}
                </select>
              )}
              {/* You would integrate a charting library like Chart.js or Recharts here
                  to render the pie chart and comparison bar chart based on the data.
                  For simplicity, I'm just listing the data. */}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default InstructorDashboardPage;