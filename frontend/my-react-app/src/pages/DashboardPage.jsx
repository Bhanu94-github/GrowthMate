import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import toast from 'react-hot-toast';

function DashboardPage() {
  const [userData, setUserData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/student/dashboard/', {
          withCredentials: true
        });
        setUserData(response.data);
      } catch (error) {
        toast.error('Failed to fetch dashboard data');
        navigate('/login');
      }
    };

    fetchDashboard();
  }, [navigate]);

  const handleLogout = () => {
    navigate('/login');
  };

  if (!userData) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Welcome, {userData.name}!</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            Logout
          </button>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Your Tokens</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded">
              <p className="text-sm text-blue-600">General Tokens</p>
              <p className="text-2xl font-bold">{userData.tokens}</p>
            </div>
            {Object.entries(userData.ai_tokens || {}).map(([module, count]) => (
              <div key={module} className="bg-green-50 p-4 rounded">
                <p className="text-sm text-green-600">{module.replace(/_/g, ' ')}</p>
                <p className="text-2xl font-bold">{count}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;