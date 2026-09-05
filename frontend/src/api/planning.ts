const API_BASE = (import.meta as ImportMeta & { env?: { VITE_API_BASE_URL?: string } }).env?.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!response.ok) throw new Error(`NexusRail request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export type ProductDashboard = {
  summary: { active_requests: number; high_priority_requests: number; conflicts: number; recommended_blocks: number; approved_plans: number; trains_affected: number; database_status: string; optimization_status: string; approval_status: string };
  requests: MaintenanceRequest[];
  sections: Section[];
  recent_activity: { label: string; detail: string; timestamp: string }[];
};

export type MaintenanceRequest = {
  id: number; request_code: string; title: string; department: string; maintenance_type: string; description: string; priority_score: number; priority_factors: Record<string, number>; status: string; estimated_duration_hours: number; required_crew: number; window_start: string; window_end: string; section_code: string; section_name: string; route_name: string; asset_name: string; asset_type: string; conflicts: { severity: string; cause: string; resolution: string }[];
};

export type Section = { id: number; section_code: string; name: string; route_name: string; from_station: string; to_station: string; length_km: number; traffic_intensity: string; operational_importance: string; status: string; asset_count: number; active_request_count: number };
export type Recommendation = { id: number; recommendation_code: string; section_code: string; section_name: string; route_name: string; recommended_start: string; recommended_end: string; duration_hours: number; priority_score: number; operational_impact: string; explanation: string; status: string; request_codes: string[]; train_count: number };
export type OptimizationRun = { id: number; run_code: string; planning_start: string; planning_end: string; available_hours: number; available_crew: number; objective: string; solver_status: string; tasks_submitted: number; tasks_selected: number; priority_captured: number; recommendations: Recommendation[] };

export const fetchProductDashboard = () => request<ProductDashboard>('/dashboard');
export const runOptimization = (payload: { available_hours: number; available_crew: number; planning_start: string; planning_end: string }) => request<OptimizationRun>('/optimization/run', { method: 'POST', body: JSON.stringify(payload) });
export const approveRecommendation = (id: number) => request<OptimizationRun>(`/recommendations/${id}/approve`, { method: 'POST', body: JSON.stringify({ reviewed_by: 'Demo Planner', comments: 'Approved from control room.' }) });
export const rejectRecommendation = (id: number) => request<OptimizationRun>(`/recommendations/${id}/reject`, { method: 'POST', body: JSON.stringify({ reviewed_by: 'Demo Planner', comments: 'Deferred for review.' }) });
