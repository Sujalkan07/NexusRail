import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import App from './App';

vi.mock('./api/planning', () => ({
  fetchProductDashboard: vi.fn().mockResolvedValue({
    summary: { active_requests: 4, high_priority_requests: 2, conflicts: 2, recommended_blocks: 0, approved_plans: 0, trains_affected: 3, database_status: 'Connected', optimization_status: 'Ready', approval_status: 'Up to date' },
    requests: [],
    sections: [],
    recent_activity: [],
  }),
  runOptimization: vi.fn(),
  approveRecommendation: vi.fn(),
  rejectRecommendation: vi.fn(),
}));

describe('NexusRail control room', () => {
  it('renders the product shell and connected dashboard state', async () => {
    render(<App />);
    expect(await screen.findByText('NEXUSRAIL')).toBeInTheDocument();
    expect(screen.getByText('Active requests')).toBeInTheDocument();
    expect(screen.getByText('Railway maintenance coordination')).toBeInTheDocument();
  });
});
