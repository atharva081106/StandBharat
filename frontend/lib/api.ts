
const API_URL = "http://localhost:8000/api";

export async function fetchApi(endpoint: string, options: RequestInit = {}) {
    options.credentials = "include"; // For cookies
    if (!options.headers) {
        options.headers = {};
    }
    (options.headers as any)["Content-Type"] = "application/json";
    
    const response = await fetch(`${API_URL}${endpoint}`, options);
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "API Error");
    }
    return response.json();
}


export const notificationsApi = {
  getNotifications: async () => {
    return fetchApi('/api/notifications');
  },
  getUnreadCount: async () => {
    return fetchApi('/api/notifications/unread-count');
  },
  markAsRead: async (id: string) => {
    return fetchApi('/api/notifications/' + id + '/read', { method: 'PATCH' });
  },
  markAllAsRead: async () => {
    return fetchApi('/api/notifications/read-all', { method: 'POST' });
  }
};
