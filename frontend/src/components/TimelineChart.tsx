import { DashboardBlock, DashboardTrain } from '../types/dashboard';

type TimelineChartProps = {
  blocks: DashboardBlock[];
  trains: DashboardTrain[];
};

function normalizeWindow(value: string): number {
  const parts = value.match(/(\d{1,2}):?(\d{2})?/g);
  if (!parts) return 0;
  const timeString = parts[0];
  const [hours, minutes] = timeString.split(':').map(Number);
  return hours + (minutes ?? 0) / 60;
}

export function TimelineChart({ blocks, trains }: TimelineChartProps) {
  const timelineSegments = blocks.map((block) => {
    const start = normalizeWindow(block.window.split('–')[0] ?? '00:00');
    const end = normalizeWindow(block.window.split('–')[1] ?? '24:00');
    return { ...block, start, end };
  });

  return (
    <div className="timeline-chart" aria-label="Maintenance timeline">
      <div className="timeline-legend">
        <span><i className="swatch block" /> Recommended block</span>
        <span><i className="swatch train" /> Train window</span>
      </div>
      <div className="timeline-grid">
        {timelineSegments.length ? timelineSegments.map((block) => (
          <div key={block.id} className="timeline-row">
            <div className="timeline-label">{block.section}</div>
            <div className="timeline-track">
              <div className="bar maintenance" style={{ left: `${Math.max(4, (block.start / 24) * 100)}%`, width: `${Math.max(12, ((block.end - block.start) / 24) * 100)}%` }}>
                {block.name}
              </div>
              {trains.filter((train) => train.section === block.section).map((train) => {
                const trainWindow = train.window.split('→')[0];
                const trainHour = normalizeWindow(trainWindow);
                const width = 8;
                return (
                  <div key={`${block.id}-${train.id}`} className="bar train-window" style={{ left: `${Math.max(2, (trainHour / 24) * 100)}%`, width: `${width}%` }}>
                    {train.trainNo}
                  </div>
                );
              })}
            </div>
          </div>
        )) : <p>No timeline data available.</p>}
      </div>
    </div>
  );
}
