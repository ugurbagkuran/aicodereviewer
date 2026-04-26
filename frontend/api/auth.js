import { apiRequest, saveTokens, clearTokens } from './client.js';

export async function login(email, password) {
  const data = await apiRequest('POST', '/auth/login', { email, password }, { auth: false });
  saveTokens(data.access_token, data.refresh_token);
  const user = await apiRequest('GET', '/auth/me');
  localStorage.setItem('user', JSON.stringify(user));
  return user;
}

export async function register(username, email, password) {
  return apiRequest('POST', '/auth/register', { username, email, password }, { auth: false });
}

export async function logout() {
  const refresh = localStorage.getItem('refresh_token');
  try {
    if (refresh) await apiRequest('POST', '/auth/logout', { refresh_token: refresh });
  } finally {
    clearTokens();
  }
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem('user'));
  } catch {
    return null;
  }
}

export function isAuthenticated() {
  return !!localStorage.getItem('access_token');
}
