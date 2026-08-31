import { DashboardBlock, DashboardOverview, DashboardTask, DashboardTrain, DashboardViewModel } from '../types/dashboard';

function safeNumber(value: unknown, fallback = 0): number {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? numberValue : fallback;
}

function safePriorityNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === '') return null;
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? numberValue : null;
}

function safeString(value: unknown, fallback = 'Unavailable'): string {
  if (typeof value === 'string' && value.trim()) return value.trim();
  if (typeof value === 'number' && Number.isFinite(value)) return String(value);
  return fallback;
}

function formatPriority(value: unknown): string {
  const parsed = safePriorityNumber(value);
  return parsed === null ? 'Not scored' : `P ${parsed.toFixed(1)}`;
}

function formatHour(value: number | string | undefined, fallback = '00:00'): string {
  const totalMinutes = Math.max(0, Math.round(safeNumber(value, 0) * 60));
  const hour = Math.floor(totalMinutes / 60) % 24;
  const minute = totalMinutes % 60;
  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
}

function formatHourRange(start: number | string | undefined, end: number | string | undefined): string {
  return `${formatHour(start)}–${formatHour(end)}`;
}

function formatIsoDate(value: unknown): string {
  if (typeof value !== 'string' || !value) return 'Unavailable';
  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' });
  } catch {
    return value;
  }
}

function extractSectionCodes(snapshot: DashboardOverview): string[] {
  const sections = new Set<string>();
  const records = snapshot.records ?? {};
  for (const collection of [records.tms_defects, records.smms_failures, records.tdms_equipment, records.train_schedule]) {
    for (const item of collection ?? []) {
      const section = typeof item?.section_code === 'string' ? item.section_code : '';
      if (section) sections.add(section);
    }
  }
  return Array.from(sections).sort();
}

function makeTaskId(source: string, id: unknown, section: unknown): string {
  return `${source}-${String(id ?? 'unknown')}-${String(section ?? 'unknown')}`;
}

export function buildDashboardViewModel(snapshot: DashboardOverview, selectedBlockId: string | null): DashboardViewModel {
  const overview = snapshot.overview ?? {};
  const recommendations = snapshot.recommendations ?? {};
  const recordCollections = snapshot.records ?? {};

  const tasks: DashboardTask[] = [
    ...(recordCollections.tms_defects ?? []).map((task: any, index: number) => ({
      id: makeTaskId('TMS', task?.id ?? index, task?.section_code ?? 'unknown'),
      name: safeString(task?.defect_type ?? 'Track defect'),
      priority: formatPriority(task?.priority_score),
      section: safeString(task?.section_code, 'Unknown'),
      route: safeString(task?.route_code, 'Unknown'),
      status: safeString(task?.status, 'open'),
      source: 'TMS',
      detail: safeString(task?.defect_description ?? task?.severity ?? 'Track defect', 'Track defect'),
    })),
    ...(recordCollections.smms_failures ?? []).map((task: any, index: number) => ({
      id: makeTaskId('SMMS', task?.id ?? index, task?.section_code ?? 'unknown'),
      name: safeString(task?.failure_type ?? 'Signal issue'),
      priority: formatPriority(task?.priority_score),
      section: safeString(task?.section_code, 'Unknown'),
      route: safeString(task?.route_code, 'Unknown'),
      status: safeString(task?.status, 'active'),
      source: 'SMMS',
      detail: safeString(task?.failure_description ?? task?.severity ?? 'Signal issue', 'Signal issue'),
    })),
    ...(recordCollections.tdms_equipment ?? []).map((task: any, index: number) => ({
      id: makeTaskId('TDMS', task?.id ?? index, task?.section_code ?? 'unknown'),
      name: safeString(task?.equipment_type ?? 'Equipment issue'),
      priority: formatPriority(task?.priority_score ?? task?.criticality_score),
      section: safeString(task?.section_code, 'Unknown'),
      route: safeString(task?.route_code, 'Unknown'),
      status: safeString(task?.health_status ?? task?.status, 'degraded'),
      source: 'TDMS',
      detail: safeString(task?.equipment_notes ?? task?.equipment_id ?? 'Equipment issue', 'Equipment issue'),
    })),
  ];

  const blocks: DashboardBlock[] = (recommendations.blocks ?? []).map((block: any, index: number) => ({
    id: String(block?.block_id ?? `block-${index}`),
    name: String(block?.block_id ?? `Block ${index + 1}`),
    priority: safePriorityNumber(block?.priority_captured) === null ? 'Priority N/A' : `Priority ${safePriorityNumber(block?.priority_captured)?.toFixed(1)}`,
    section: safeString(block?.section_code, 'Unknown'),
    route: safeString(block?.route_code, 'Unknown'),
    window: formatHourRange(block?.start_hour, block?.end_hour),
    tasks: Array.isArray(block?.task_ids) ? block.task_ids.map(String) : [],
    trainConflicts: Array.isArray(block?.train_conflicts)
      ? block.train_conflicts.map((train: any) => `${safeString(train?.train_no, 'Train')} · ${safeString(train?.section_code, 'Unknown')} · ${formatHourRange(train?.start_hour, train?.end_hour)}`)
      : [],
    explanation: safeString(block?.explanation ?? recommendations.explanation ?? 'Recommendation available', 'Recommendation available'),
    powerBlockRequired: Boolean(block?.power_block_required ?? block?.power_isolation_covered),
    powerIsolationCovered: Boolean(block?.power_isolation_covered ?? block?.power_block_required),
    taskCount: Array.isArray(block?.task_ids) ? block.task_ids.length : 0,
  }));

  const trains: DashboardTrain[] = (recordCollections.train_schedule ?? []).map((train: any, index: number) => ({
    id: makeTaskId('TRAIN', train?.id ?? index, train?.train_no ?? 'unknown'),
    trainNo: safeString(train?.train_no, 'Unknown'),
    serviceType: safeString(train?.service_type, 'Unknown'),
    section: safeString(train?.section_code, 'Unknown'),
    route: safeString(train?.route_code, 'Unknown'),
    origin: safeString(train?.origin_station, 'Unknown'),
    destination: safeString(train?.destination_station, 'Unknown'),
    scheduledDate: safeString(train?.scheduled_date, 'Unavailable'),
    window: `${formatIsoDate(train?.arrival_time)} → ${formatIsoDate(train?.departure_time)}`,
    status: safeString(train?.status, 'unknown'),
  }));

  const summary = [
    { label: 'Total tasks', value: String(overview.total_tasks ?? tasks.length), note: 'Live backlog' },
    { label: 'Selected', value: String(overview.tasks_selected ?? blocks.length), note: 'Solver picks' },
    { label: 'Rejected', value: String(overview.tasks_rejected ?? 0), note: 'Conflict / deferred' },
    { label: 'Captured priority', value: safePriorityNumber(overview.priority_captured) === null ? 'N/A' : `${safePriorityNumber(overview.priority_captured)?.toFixed(1)}`, note: 'Priority value' },
    { label: 'Database', value: safeString(snapshot.system_status?.database, 'unknown'), note: 'availability' },
    { label: 'Solver', value: safeString(snapshot.system_status?.solver, 'unknown'), note: 'optimization status' },
    { label: 'Approval', value: safeString(snapshot.system_status?.approval ?? snapshot.approval?.status, 'pending_review'), note: 'workflow state' },
  ];

  return {
    header: {
      title: 'NexusRail',
      subtitle: 'Operations control',
      systemMode: snapshot.system_status?.solver === 'available' ? 'Operational' : 'Review',
    },
    summary,
    sections: extractSectionCodes(snapshot),
    blocks: blocks.length ? blocks : [{
      id: 'unavailable',
      name: 'No recommended blocks',
      priority: 'Priority 0.0',
      section: 'Unavailable',
      route: 'Unavailable',
      window: '00:00–00:00',
      tasks: [],
      trainConflicts: [],
      explanation: 'Recommendation data unavailable from backend.',
      powerBlockRequired: false,
      powerIsolationCovered: false,
      taskCount: 0,
    }],
    tasks: tasks.length ? tasks : [{
      id: 'unavailable',
      name: 'No maintenance tasks',
      priority: 'P 0.0',
      section: 'Unavailable',
      route: 'Unavailable',
      status: 'unknown',
      source: 'N/A',
      detail: 'No maintenance records available.',
    }],
    trains: trains.length ? trains : [{
      id: 'unavailable',
      trainNo: 'Unavailable',
      serviceType: 'Unavailable',
      section: 'Unavailable',
      route: 'Unavailable',
      origin: 'Unavailable',
      destination: 'Unavailable',
      scheduledDate: 'Unavailable',
      window: 'Unavailable',
      status: 'unknown',
    }],
    approvals: {
      required: snapshot.approval?.required ?? true,
      authRequired: snapshot.approval?.auth_required ?? true,
      status: snapshot.approval?.status ?? 'pending_review',
      message: snapshot.approval?.message ?? 'Approval required.',
    },
    details: {
      selectedTaskIds: Array.isArray(recommendations.selected_tasks) ? recommendations.selected_tasks.map(String) : [],
      rejectedTasks: Array.isArray(recommendations.rejected_tasks)
        ? recommendations.rejected_tasks.map((task: any) => ({
            taskId: safeString(task?.task_id, 'Unknown'),
            reason: safeString(task?.reason, 'Deferred by optimization constraints'),
            priority: `P ${safeNumber(task?.priority_score, 0).toFixed(1)}`,
          }))
        : [],
      explanation: safeString(recommendations.explanation, 'No explanation available.'),
      trainConflicts: Array.isArray(recommendations.train_conflicts)
        ? recommendations.train_conflicts.map((train: any) => `${safeString(train?.train_no, 'Train')} · ${safeString(train?.section_code, 'Unknown')} · ${safeString(train?.status, 'unknown')}`)
        : [],
      constraints: [
        safeString(snapshot.system_status?.solver, 'unknown'),
        `${safeNumber(overview.active_train_conflicts ?? 0, 0)} active train conflicts`,
      ],
    },
  };
}
