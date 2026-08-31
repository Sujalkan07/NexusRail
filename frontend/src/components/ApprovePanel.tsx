type ApprovePanelProps = {
  data: {
    required: boolean;
    authRequired: boolean;
    status: string;
    message: string;
  };
};

export function ApprovePanel({ data }: ApprovePanelProps) {
  return (
    <div className="approve-panel">
      <div className="approval-status">Status: {data.status}</div>
      <p>{data.message}</p>
      <div className="approval-meta">
        <span className="pill">{data.required ? 'Review required' : 'No review required'}</span>
        <span className="pill muted">{data.authRequired ? 'Permission-aware prototype' : 'No auth gate'}</span>
      </div>
      <div className="approval-actions">
        <button type="button" className="action approve" disabled={!data.required}>Approve</button>
        <button type="button" className="action reject" disabled={!data.required}>Reject</button>
      </div>
      <small>Prototype approval state only. The backend contract currently exposes review status and solver guidance but does not persist approvals.</small>
    </div>
  );
}
