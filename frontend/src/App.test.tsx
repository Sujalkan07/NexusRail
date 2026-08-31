import { render, screen } from '@testing-library/react';
import App from './App';
import { vi } from 'vitest';

vi.mock('./api/dashboard', () => ({
  fetchDashboardOverview: vi.fn().mockResolvedValue({
    generated_at: '2026-08-31T00:00:00Z',
    system_status: { solver: 'available' },
    overview: { total_tasks: 10, tasks_selected: 4, tasks_rejected: 2, priority_total: 80, priority_captured: 65 },
    records: {
      tms_defects: [{ id: 1, section_code: 'SEC-12', defect_type: 'track_crack', priority_score: 64 }],
      smms_failures: [{ id: 2, section_code: 'SEC-18', failure_type: 'signal_fault', priority_score: 58 }],
      tdms_equipment: [{ id: 3, section_code: 'SEC-27', equipment_type: 'overhead_equipment', priority_score: 72 }],
      train_schedule: [{ id: 9, section_code: 'SEC-12', train_no: 'T120', arrival_time: '2026-08-31T06:00:00', departure_time: '2026-08-31T07:00:00' }],
    },
    recommendations: {
      feasible: true,
      selected_tasks: ['TMS-0-SEC-12'],
      rejected_tasks: [{ task_id: 'SMMS-0-SEC-18', reason: 'conflict' }],
      blocks: [{ block_id: 'mega-block-SEC-12', section_code: 'SEC-12', start_hour: 10, end_hour: 14, task_ids: ['TMS-0-SEC-12'], priority_captured: 64, train_conflicts: [{ train_no: 'T120', section_code: 'SEC-12' }] }],
      explanation: 'Selected one high-priority task.',
    },
    approval: { required: true, auth_required: true, status: 'pending_review', message: 'Approval required.' },
  }),
}));

describe('dashboard rendering', () => {
  it('renders the main dashboard shell and summary elements', async () => {
    render(<App />);

    expect(await screen.findByText('NexusRail')).toBeInTheDocument();
    expect(screen.getByText('System status')).toBeInTheDocument();
    expect(screen.getByText('Unified operational overview')).toBeInTheDocument();
    expect(screen.getByText('Timeline')).toBeInTheDocument();
  });
});
