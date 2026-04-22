// Backend API integration
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
   withCredentials: true, // ✅ THIS IS REQUIRED
});


// Response interceptor for error handling
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401 && typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);


// Authentication API
export const authAPI = {
  login: (email: string, password: string, userType: string) =>
    api.post('/auth/login', { email, password, userType }),
  
  register: (userData: any) =>
    api.post('/auth/register', userData),
  
  logout: () =>
    api.post('/auth/logout'),
};

// Vehicle API
export const vehicleAPI = {
  getVehicles: () =>
    api.get('/vehicles/me'),

  addVehicle: (vehicleData: any) =>
    api.post('/vehicles', vehicleData),

  updateVehicle: (vehicleId: string, vehicleData: any) =>
    api.put(`/vehicles/${vehicleId}`, vehicleData),

  deleteVehicle: (vehicleId: string) =>
    api.delete(`/vehicles/${vehicleId}`),
};

// Prediction API
export const predictionAPI = {
  predictFailure: (sensorData: any) =>
    api.post('/predict', sensorData),
  
  analyzeVehicle: (vehicleId: string, sensorData: any) =>
    api.post(`/analyze/${vehicleId}`, sensorData),
  
  getPredictions: (vehicleId: string) =>
    api.get(`/predictions/${vehicleId}`),
};

// Service API
export const serviceAPI = {
  scheduleService: (serviceData: any) =>
    api.post('/services/schedule', serviceData),
  
  getServices: (vehicleId?: string) =>
    api.get('/services', { params: { vehicleId } }),
  
  updateService: (serviceId: string, serviceData: any) =>
    api.put(`/services/${serviceId}`, serviceData),
  
  cancelService: (serviceId: string) =>
    api.delete(`/services/${serviceId}`),
};

// Admin API
export const adminAPI = {
  getFleetOverview: () =>
    api.get('/admin/fleet'),
  
  getSystemMetrics: () =>
    api.get('/admin/metrics'),
  
  getAgentStatus: () =>
    api.get('/admin/agents'),
  
  getAlerts: () =>
    api.get('/admin/alerts'),
  
  triggerDiagnostics: () =>
    api.post('/admin/diagnostics'),
  
  getRCAInsights: () =>
    api.get('/admin/rca'),
};

// Real-time WebSocket
export const setupWebSocket = (vehicleId: string) => {
  const ws = new WebSocket(`ws://${API_BASE_URL}/ws/vehicle/${vehicleId}`);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Handle real-time data
    return data;
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };
  
  return ws;
};

export default api;