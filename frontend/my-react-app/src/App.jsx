import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import FeaturesPage from './pages/FeaturesPage';
import ModulesPage from './pages/ModulesPage';
import SignInPage from './pages/SignInPage';
import RegisterPage from './pages/RegisterPage';
import StudentDashboardPage from './pages/StudentDashboardPage';
import InstructorDashboardPage from './pages/InstructorDashboardPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import NotFoundPage from './pages/NotFoundPage';
import Layout from './components/Layout';
import PrivateRoute from './components/PrivateRoute';
import TextToTextModule from './pages/TextToTextModule';
import VoiceToVoiceModule from './pages/VoiceToVoiceModule';
import FaceToFaceModule from './pages/FaceToFaceModule';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout><HomePage /></Layout>} />
        <Route path="/about" element={<Layout><AboutPage /></Layout>} />
        <Route path="/features" element={<Layout><FeaturesPage /></Layout>} />
        <Route path="/modules" element={<Layout><ModulesPage /></Layout>} />
        <Route path="/signin" element={<Layout><SignInPage /></Layout>} />
        <Route path="/register" element={<Layout><RegisterPage /></Layout>} />

        {/* AI Module Routes (Protected) */}
        <Route path="/modules/text-to-text" element={<PrivateRoute><Layout><TextToTextModule /></Layout></PrivateRoute>} />
        <Route path="/modules/voice-to-voice" element={<PrivateRoute><Layout><VoiceToVoiceModule /></Layout></PrivateRoute>} />
        <Route path="/modules/face-to-face" element={<PrivateRoute><Layout><FaceToFaceModule /></Layout></PrivateRoute>} />

        {/* Dashboard Routes (Protected) */}
        <Route path="/student/dashboard" element={<PrivateRoute><Layout><StudentDashboardPage /></Layout></PrivateRoute>} />
        <Route path="/instructor/dashboard" element={<PrivateRoute><Layout><InstructorDashboardPage /></Layout></PrivateRoute>} />
        <Route path="/admin/dashboard" element={<PrivateRoute><Layout><AdminDashboardPage /></Layout></PrivateRoute>} />

        <Route path="*" element={<Layout><NotFoundPage /></Layout>} />
      </Routes>
    </Router>
  );
}

export default App;