import { DashboardOverview } from '../types/dashboard';

const API_BASE = (import.meta as ImportMeta & { env?: { VITE_API_BASE_URL?: string } }).env?.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

export async function fetchDashboardOverview(): Promise<DashboardOverview> {
  const response = await fetch(`${API_BASE}/dashboard/overview`);
  if (!response.ok) {
    throw new Error(`Dashboard request failed: ${response.status}`);
  }
  return response.json();
}
