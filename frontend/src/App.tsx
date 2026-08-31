import { useEffect, useMemo, useState } from 'react';
import { fetchDashboardOverview } from './api/dashboard';
import { buildDashboardViewModel } from './data/dashboardViewModel';
import { DashboardOverview, DashboardViewModel } from './types/dashboard';
import { TimelineChart } from './components/TimelineChart';
import { RecommendationDetails } from './components/RecommendationDetails';
import { ApprovePanel } from './components/ApprovePanel';

const EMPTY_VIEW: DashboardViewModel = {
  header: { title: 'NexusRail', subtitle: 'Operations control', systemMode: 'Review' },
  summary: [],
  sections: [],
  blocks: [],
  tasks: [],
  trains: [],
  approvals: { required: true, authRequired: true, status: 'pending_review', message: 'Awaiting review' },
  details: { selectedTaskIds: [], explanation: 'No recommendation available yet.' },
};

type NavTab = 'overview' | 'maintenance' | 'train' | 'approvals';

function App() {
  const [snapshot, setSnapshot] = useState<DashboardOverview | null>(null);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [selectedBlockId, setSelectedBlockId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<NavTab>('overview');

  const loadDashboard = () => {
    setStatus('loading');
    setErrorMessage('');

    fetchDashboardOverview()
      .then((data) => {
        setSnapshot(data);
        setStatus('ready');
        if (data.recommendations?.blocks?.length) {
          const firstBlockId = data.recommendations.blocks[0]?.block_id;
          if (typeof firstBlockId === 'string') {
            setSelectedBlockId(firstBlockId);
          }
        }
      })
      .catch((error: unknown) => {
        setStatus('error');
        setErrorMessage(error instanceof Error ? error.message : 'Failed to fetch operational data.');
      });
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const viewModel = useMemo(() => {
    if (!snapshot) return EMPTY_VIEW;
    return buildDashboardViewModel(snapshot, selectedBlockId);
  }, [snapshot, selectedBlockId]);

  const selectedBlock = viewModel.blocks.find((block) => block.id === selectedBlockId) ?? viewModel.blocks[0];

  const isEmptyState = status === 'ready' && !viewModel.summary.length && !viewModel.blocks.length && !viewModel.tasks.length;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <div className="eyebrow">NexusRail Control</div>
          <h1>{viewModel.header.title}</h1>
        </div>
        <div className="topbar-meta">
          <span className="badge status-pill">{viewModel.header.systemMode}</span>
          <span className="badge neutral">{viewModel.header.subtitle}</span>
        </div>
      </header>

      {status === 'error' && (
        <div className="error-banner" role="alert">
          <span>Backend unavailable</span>
          <button type="button" className="action retry" onClick={loadDashboard}>Retry</button>
          <small>{errorMessage}</small>
        </div>
      )}

      <aside className="sidebar">
        <nav className="nav-list">
          {['Overview', 'Maintenance', 'Train plan', 'Approvals'].map((label, index) => {
            const values: NavTab[] = ['overview', 'maintenance', 'train', 'approvals'];
            const isActive = activeTab === values[index];
            return (
              <button
                key={label}
                type="button"
                className={`nav-item ${isActive ? 'active' : ''}`}
                onClick={() => setActiveTab(values[index])}
              >
                {label}
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="content-grid">
        {status === 'loading' ? (
          <section className="panel loading-panel">
            <div className="panel-header">
              <h2>Operational data</h2>
            </div>
            <p>Loading operational data...</p>
          </section>
        ) : status === 'error' ? (
          <section className="panel empty-panel">
            <h2>Backend unavailable</h2>
            <p>Unable to reach the NexusRail backend.</p>
          </section>
        ) : isEmptyState ? (
          <section className="panel empty-panel">
            <h2>No operational records available.</h2>
          </section>
        ) : (
          <>
            <section className="panel summary-panel">
              <div className="panel-header">
                <h2>System status</h2>
              </div>
              <div className="stats-grid">
                {viewModel.summary.map((item) => (
                  <article key={item.label} className="stat-card">
                    <div className="stat-label">{item.label}</div>
                    <div className="stat-value">{item.value}</div>
                    <div className="stat-trend">{item.note}</div>
                  </article>
                ))}
              </div>
            </section>

            {activeTab === 'overview' && (
              <>
                <section className="panel overview-panel">
                  <div className="panel-header">
                    <h2>Unified operational overview</h2>
                  </div>
                  <div className="overview-grid">
                    <article>
                      <h3>Sections</h3>
                      <ul>
                        {viewModel.sections.length ? viewModel.sections.map((section) => (
                          <li key={section}>{section}</li>
                        )) : <li>No operational records available.</li>}
                      </ul>
                    </article>
                    <article>
                      <h3>Priority summary</h3>
                      <ul>
                        {viewModel.tasks.length ? viewModel.tasks.slice(0, 4).map((task) => (
                          <li key={task.id}>{task.name} · {task.priority}</li>
                        )) : <li>No operational records available.</li>}
                      </ul>
                    </article>
                  </div>
                </section>

                <section className="panel maintenance-panel">
                  <div className="panel-header">
                    <h2>Maintenance / task area</h2>
                  </div>
                  <ul className="task-list">
                    {viewModel.tasks.length ? viewModel.tasks.map((task) => (
                      <li key={task.id}>
                        <span>{task.name}</span>
                        <strong>{task.priority}</strong>
                      </li>
                    )) : <li>No operational records available.</li>}
                  </ul>
                </section>

                <section className="panel priority-panel">
                  <div className="panel-header">
                    <h2>Priority / risk area</h2>
                  </div>
                  <ul className="risk-list">
                    {viewModel.blocks.length ? viewModel.blocks.map((block) => (
                      <li key={block.id}>
                        <button type="button" className="block-link" onClick={() => setSelectedBlockId(block.id)}>
                          {block.name}
                        </button>
                        <span>{block.priority}</span>
                      </li>
                    )) : <li>No operational records available.</li>}
                  </ul>
                </section>

                <section className="panel blocks-panel">
                  <div className="panel-header">
                    <h2>Recommended blocks</h2>
                  </div>
                  <div className="block-stack">
                    {viewModel.blocks.length ? viewModel.blocks.map((block) => (
                      <div key={block.id} className={`block-card ${selectedBlock?.id === block.id ? 'selected' : ''}`}>
                        <div className="block-title-row">
                          <strong>{block.name}</strong>
                          <span>{block.priority}</span>
                        </div>
                        <div>{block.section}</div>
                        <div>{block.window}</div>
                      </div>
                    )) : <div>No operational records available.</div>}
                  </div>
                </section>

                <section className="panel timeline-panel">
                  <div className="panel-header">
                    <h2>Timeline</h2>
                  </div>
                  <TimelineChart blocks={viewModel.blocks} trains={viewModel.trains} />
                </section>

                <section className="panel details-panel">
                  <div className="panel-header">
                    <h2>Recommendation details</h2>
                  </div>
                  {selectedBlock ? (
                    <RecommendationDetails block={selectedBlock} details={viewModel.details} />
                  ) : (
                    <p>No operational records available.</p>
                  )}
                </section>
              </>
            )}

            {activeTab === 'maintenance' && (
              <section className="panel full-width-panel">
                <div className="panel-header">
                  <h2>Maintenance</h2>
                </div>
                <div className="table-wrap">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Type</th>
                        <th>Section</th>
                        <th>Route</th>
                        <th>Priority</th>
                        <th>Status</th>
                        <th>Source</th>
                      </tr>
                    </thead>
                    <tbody>
                      {viewModel.tasks.length ? viewModel.tasks.map((task) => (
                        <tr key={task.id}>
                          <td>{task.id}</td>
                          <td>{task.name}</td>
                          <td>{task.section}</td>
                          <td>{task.route}</td>
                          <td>{task.priority}</td>
                          <td><span className="status-chip">{task.status}</span></td>
                          <td>{task.source}</td>
                        </tr>
                      )) : <tr><td colSpan={7}>No operational records available.</td></tr>}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

            {activeTab === 'train' && (
              <section className="panel full-width-panel">
                <div className="panel-header">
                  <h2>Train Plan</h2>
                </div>
                <div className="table-wrap">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Train</th>
                        <th>Type</th>
                        <th>Origin</th>
                        <th>Destination</th>
                        <th>Section</th>
                        <th>Scheduled</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {viewModel.trains.length ? viewModel.trains.map((train) => (
                        <tr key={train.id}>
                          <td>{train.trainNo}</td>
                          <td>{train.serviceType}</td>
                          <td>{train.origin}</td>
                          <td>{train.destination}</td>
                          <td>{train.section}</td>
                          <td>{train.window}</td>
                          <td><span className="status-chip neutral">{train.status}</span></td>
                        </tr>
                      )) : <tr><td colSpan={7}>No train schedule available.</td></tr>}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

            {activeTab === 'approvals' && (
              <section className="panel full-width-panel">
                <div className="panel-header">
                  <h2>Approvals</h2>
                </div>
                <ApprovePanel data={viewModel.approvals} />
              </section>
            )}

            <section className="panel approval-panel">
              <div className="panel-header">
                <h2>Human approval</h2>
              </div>
              <ApprovePanel data={viewModel.approvals} />
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
