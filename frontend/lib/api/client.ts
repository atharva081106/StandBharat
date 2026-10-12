const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class ApiClient {
  static defaultHeaders: Record<string, string> = {}

  static async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${BASE_URL}${endpoint}`
    const headers = {
      'Content-Type': 'application/json',
      ...this.defaultHeaders,
      ...options.headers,
    }
    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include' // required for HTTP-only cookies
    })
    
    if (!response.ok) {
      let message = `API Error (${response.status})`
      try {
        const errData = await response.json()
        if (typeof errData.detail === 'string') {
          message = errData.detail
        } else if (Array.isArray(errData.detail)) {
          message = errData.detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ')
        } else if (errData.message) {
          message = errData.message
        }
      } catch (e) {}
      throw new Error(message)
    }
    return response.json()
  }

  static get<T>(endpoint: string, options: RequestInit = {}) { return this.request<T>(endpoint, { method: 'GET', ...options }) }
  static post<T>(endpoint: string, body: any, options: RequestInit = {}) { return this.request<T>(endpoint, { method: 'POST', body: JSON.stringify(body), ...options }) }
  static put<T>(endpoint: string, body: any, options: RequestInit = {}) { return this.request<T>(endpoint, { method: 'PUT', body: JSON.stringify(body), ...options }) }
  static patch<T>(endpoint: string, body: any, options: RequestInit = {}) { return this.request<T>(endpoint, { method: 'PATCH', body: JSON.stringify(body), ...options }) }
  static delete<T>(endpoint: string, options: RequestInit = {}) { return this.request<T>(endpoint, { method: 'DELETE', ...options }) }
}
