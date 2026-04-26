import { apiRequest, wsUrl, getTokens } from './client.js';

export const runAgent = (projectId, message) =>
  apiRequest('POST', '/agent/run', { project_id: projectId, message });

export const listSessions = (projectId) =>
  apiRequest('GET', `/agent/sessions/${projectId}`);

export function createAgentStream(sessionId) {
  return new WebSocket(wsUrl(`/agent/${sessionId}/stream`));
}

export function createLogsStream(projectId) {
  return new WebSocket(wsUrl(`/agent/logs/${projectId}/stream`));
}
