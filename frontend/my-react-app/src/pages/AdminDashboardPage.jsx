import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAdminDashboardData } from '../api/api'; // Assuming this API function
import './DashboardPage.css';

function AdminDashboardPage() {
  const [adminData, setAdminData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/signin');
          return;
        }

        const response = await getAdminDashboardData(token);
        setAdminData(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching admin dashboard data:', err);
        setError(err.message || 'Failed to fetch dashboard data.');
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [navigate]);

  if (loading) {
    return <div>Loading admin dashboard data...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!adminData) {
    return <div>Unauthorized or data not found.</div>;
  }

  return (
    <div className="dashboard-page">
      <h2>Welcome, {adminData.username}! (Admin)</h2>
      <div className="dashboard-section">
        <h3>Pending Registrations</h3>
        {adminData.pendingRegistrations && adminData.pendingRegistrations.length > 0 ? (
          <ul>
            {adminData.pendingRegistrations.map(registration => (
              <li key={registration.id}>
                {registration.name} ({registration.email}) -
                <button onClick={() => handleApproveRegistration(registration.id)}>Approve</button>
                <button onClick={() => handleRejectRegistration(registration.id)}>Reject</button>
              </li>
            ))}
          </ul>
        ) : (
          <p>No pending registrations.</p>
        )}
      </div>

      {/* Add sections for managing courses, users, etc. */}
    </div>
  );

  // Implement these functions to call your API
  async function handleApproveRegistration(registrationId) {
    // API call to approve registration
  }

  async function handleRejectRegistration(registrationId) {
    // API call to reject registration
  }
}

export default AdminDashboardPage;