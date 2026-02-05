import axios from 'axios';

const API_BASE = '/monday/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchStatus = async () => {
  const response = await api.get('/status');
  return response.data;
};

export const fetchTodos = async () => {
  const response = await api.get('/todos');
  return response.data;
};

export const fetchIdeas = async () => {
  const response = await api.get('/ideas');
  return response.data;
};

export const fetchProjects = async () => {
  const response = await api.get('/projects');
  return response.data;
};
