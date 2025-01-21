import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:51313/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['x-access-token'] = token;
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const auth = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    localStorage.setItem('token', response.data.token);
    return response.data;
  },

  register: async (username, password) => {
    const response = await api.post('/auth/register', { username, password });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
  },
};

export const bots = {
  getAll: async () => {
    const response = await api.get('/bots');
    return response.data;
  },

  add: async (botToken, botName) => {
    const response = await api.post('/bots', { bot_token: botToken, bot_name: botName });
    return response.data;
  },

  start: async (botId) => {
    const response = await api.post(`/bots/${botId}/start`);
    return response.data;
  },

  stop: async (botId) => {
    const response = await api.post(`/bots/${botId}/stop`);
    return response.data;
  },

  restart: async (botId) => {
    const response = await api.post(`/bots/${botId}/restart`);
    return response.data;
  },

  getStatus: async (botId) => {
    const response = await api.get(`/bots/${botId}/status`);
    return response.data;
  },

  getMetrics: async (botId) => {
    const response = await api.get(`/bots/${botId}/metrics`);
    return response.data;
  },
};

export const advertisements = {
  getAll: async () => {
    const response = await api.get('/advertisements');
    return response.data;
  },

  create: async (data) => {
    const response = await api.post('/advertisements', data);
    return response.data;
  },

  broadcast: async (adId, botIds) => {
    const response = await api.post(`/advertisements/${adId}/broadcast`, { bot_ids: botIds });
    return response.data;
  },

  getStatus: async (adId) => {
    const response = await api.get(`/advertisements/${adId}/status`);
    return response.data;
  },
};

export const analytics = {
  getDashboard: async () => {
    const response = await api.get('/analytics/dashboard');
    return response.data;
  },

  getBotAnalytics: async (botId, days = 7) => {
    const response = await api.get(`/analytics/bots/${botId}?days=${days}`);
    return response.data;
  },

  exportData: async (days = 30) => {
    const response = await api.get(`/analytics/export?days=${days}`);
    return response.data;
  },
};