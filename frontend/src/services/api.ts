import axios from "axios";

const API_BASE = "http://localhost:8000";

export const API_BASE_URL = API_BASE;

export const api = axios.create({
  baseURL: API_BASE
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
