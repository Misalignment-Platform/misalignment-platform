export type SystemRecord = {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive';
};

export type EvaluationRecord = {
  id: string;
  risk_level: 'low' | 'medium' | 'high';
  compliance_status: 'compliant' | 'violation';
};

export type MetricAverage = {
  metric_id: string;
  metric_name: string;
  average: number;
};

export type EventRecord = {
  id: string;
  system_id: string;
  source: string;
  content: string;
  risk_category: 'low' | 'medium' | 'high';
  state: 'open' | 'in-progress' | 'resolved';
  incident_type: string;
};

const API_PREFIX = '/api';

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_PREFIX}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const apiClient = {
  listSystems: () => request<SystemRecord[]>('/systems'),
  listSystemEvaluations: (systemId: string) => request<EvaluationRecord[]>(`/systems/${systemId}/evaluations`),
  listSystemInterventions: (systemId: string) => request(`/systems/${systemId}/interventions`),
  listSystemMetrics: (systemId: string) => request(`/systems/${systemId}/metrics`),
  listEvents: () => request<EventRecord[]>('/events'),
  listMetricTrends: (systemId?: string) => {
    const suffix = systemId ? `?system_id=${encodeURIComponent(systemId)}` : '';
    return request<{ averages: MetricAverage[] }>(`/metrics/trends${suffix}`);
  },
  listPolicyMetrics: (policyId?: string) => {
    const suffix = policyId ? `?policy_id=${encodeURIComponent(policyId)}` : '';
    return request<{ averages: MetricAverage[] }>(`/metrics/trends${suffix}`);
  }
};
