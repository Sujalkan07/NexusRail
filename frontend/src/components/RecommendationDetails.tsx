import { DashboardBlock, DashboardViewModel } from '../types/dashboard';

type RecommendationDetailsProps = {
  block: DashboardBlock;
  details: DashboardViewModel['details'];
};

export function RecommendationDetails({ block, details }: RecommendationDetailsProps) {
  return (
    <div className="recommendation-details">
      <h3>{block.name}</h3>
      <div className="detail-grid">
        <div><strong>Section:</strong> {block.section}</div>
        <div><strong>Route:</strong> {block.route}</div>
        <div><strong>Window:</strong> {block.window}</div>
        <div><strong>Priority:</strong> {block.priority}</div>
        <div><strong>Power block:</strong> {block.powerBlockRequired ? 'Required' : 'Not required'}</div>
        <div><strong>Isolation coverage:</strong> {block.powerIsolationCovered ? 'Covered' : 'Not covered'}</div>
      </div>

      <div className="detail-section">
        <strong>Selected tasks:</strong>
        <ul>
          {details.selectedTaskIds.length ? details.selectedTaskIds.map((taskId) => <li key={taskId}>{taskId}</li>) : <li>None selected</li>}
        </ul>
      </div>

      <div className="detail-section">
        <strong>Rejected tasks:</strong>
        <ul>
          {details.rejectedTasks.length ? details.rejectedTasks.map((task) => (
            <li key={`${task.taskId}-${task.reason}`}>{task.taskId} — {task.reason} ({task.priority})</li>
          )) : <li>No rejections recorded</li>}
        </ul>
      </div>

      <div className="detail-section">
        <strong>Train conflicts:</strong>
        <ul>
          {block.trainConflicts.length ? block.trainConflicts.map((conflict) => <li key={conflict}>{conflict}</li>) : <li>No train conflicts</li>}
        </ul>
      </div>

      <div className="detail-section">
        <strong>Explanation:</strong>
        <p>{details.explanation}</p>
      </div>

      <div className="detail-section">
        <strong>Block constraints:</strong>
        <ul>
          {details.constraints.length ? details.constraints.map((constraint) => <li key={constraint}>{constraint}</li>) : <li>No additional constraints</li>}
        </ul>
      </div>
    </div>
  );
}
