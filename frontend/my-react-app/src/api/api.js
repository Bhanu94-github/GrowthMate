import axios from 'axios';

const API_BASE_URL = '/api'; // Your Django API base URL

// --- Authentication ---
export const loginStudent = async (username, password) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/student/login/`, { username, password });
    return response;
  } catch (error) {
    throw error;
  }
};

export const registerStudent = async (name, email, phone, username, password, confirm_password) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/student/register/`, { name, email, phone, username, password, confirm_password });
    return response;
  } catch (error) {
    throw error;
  }
};

// --- Student Dashboard ---
export const getStudentDashboardData = async (token) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/student/dashboard/`, {
      headers: { Authorization: `Bearer ${token}` } // Or however you send the token
    });
    return response;
  } catch (error) {
    throw error;
  }
};

// --- Instructor Dashboard ---
export const getInstructorDashboardData = async (token) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/instructor/dashboard/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response;
  } catch (error) {
    throw error;
  }
};

// --- Admin Dashboard ---
export const getAdminDashboardData = async (token) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/admin/dashboard/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response;
  } catch (error) {
    throw error;
  }
};

// --- AI Modules ---
export const processTextToText = async (inputText) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/modules/text-to-text/`, { input_text: inputText });
    return response;
  } catch (error) {
    throw error;
  }
};

export const processVoiceToVoice = async (audioFile) => {
  try {
    const formData = new FormData();
    formData.append('audio', audioFile);
    const response = await axios.post(`${API_BASE_URL}/modules/voice-to-voice/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response;
  } catch (error) {
    throw error;
  }
};

export const processFaceToFace = async (videoFile) => {
  try {
    const formData = new FormData();
    formData.append('video', videoFile);
    const response = await axios.post(`${API_BASE_URL}/modules/face-to-face/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response;
  } catch (error) {
    throw error;
  }
};