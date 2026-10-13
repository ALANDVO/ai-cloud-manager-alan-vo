const BASE = ''

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = { 'Content-Type': 'application/json', ...(options?.headers as Record<string, string> || {}) }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const resp = await fetch(`${BASE}${path}`, { ...options, headers })
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}))
    throw new Error(body.detail || `HTTP ${resp.status}`)
  }
  return resp.json()
}

export const api = {
  me: () => request<any>('/api/auth/me'),
  health: () => request<any>('/api/health'),
  costSummary: () => request<any>('/api/costs/summary'),
  costTrends: (params: string) => request<any[]>(`/api/costs/trends?${params}`),
  costBreakdown: (params: string) => request<any[]>(`/api/costs/breakdown?${params}`),
  costAnomalies: () => request<any[]>('/api/costs/anomalies'),
  recommendations: () => request<any[]>('/api/recommendations'),
  generateRecs: () => request<any[]>('/api/recommendations/generate', { method: 'POST' }),
  rightsizing: () => request<any[]>('/api/rightsizing'),
  securityAudit: () => request<any>('/api/security/audit'),
  compliance: () => request<any[]>('/api/security/compliance'),
  posture: () => request<any>('/api/security/posture'),
  resources: (params: string) => request<any[]>(`/api/resources?${params}`),
  utilization: () => request<any>('/api/resources/utilization'),
  scalingPolicies: () => request<any[]>('/api/scaling/policies'),
  scalingPredictions: () => request<any[]>('/api/scaling/predictions'),
  workloads: () => request<any[]>('/api/orchestration/workloads'),
  tenants: () => request<any[]>('/api/tenants'),
  createTenant: (t: any) => request<any>('/api/tenants', { method: 'POST', body: JSON.stringify(t) }),
  tenant: (id: string) => request<any>(`/api/tenants/${id}`),
  tenantConnections: (id: string) => request<any[]>(`/api/tenants/${id}/connections`),
}
