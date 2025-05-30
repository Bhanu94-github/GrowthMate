import apiClient from './config';

// --- Authentication ---
export const loginStudent = async (username, password) => {
  try {
    const response = await apiClient.post('/student/login/', { username, password });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const registerStudent = async (name, email, phone, username, password, confirm_password) => {
  try {
    const response = await apiClient.post('/student/register/', {
      name,
      email,
      phone,
      username,
      password,
      confirm_password
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

// --- Student Dashboard ---
export const getStudentDashboardData = async () => {
  try {
    const response = await apiClient.get('/student/dashboard/');
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

// --- Instructor Dashboard ---
export const getInstructorDashboardData = async () => {
  try {
    const response = await apiClient.get('/instructor/dashboard/');
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

// --- Admin Dashboard ---
export const getAdminDashboardData = async () => {
  try {
    const response = await apiClient.get('/admin/dashboard/');
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

// --- AI Modules ---
export const processTextToText = async (inputText) => {
  try {
    const response = await apiClient.post('/modules/text-to-text/', { input_text: inputText });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const processVoiceToVoice = async (audioFile) => {
  try {
    const formData = new FormData();
    formData.append('audio', audioFile);
    const response = await apiClient.post('/modules/voice-to-voice/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const processFaceToFace = async (videoFile) => {
  try {
    const formData = new FormData();
    formData.append('video', videoFile);
    const response = await apiClient.post('/modules/face-to-face/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};