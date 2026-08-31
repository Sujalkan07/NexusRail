export type DashboardOverview = {
  generated_at?: string;
  system_status?: {
    database?: string;
    backend?: string;
    solver?: string;
    approval?: string;
  };
  overview?: {
    total_tasks?: number;
    tasks_selected?: number;
    tasks_rejected?: number;
    priority_total?: number;
    priority_captured?: number;
    active_train_conflicts?: number;
    sections_monitoring?: number;
  };
  records?: {
    tms_defects?: Array<Record<string, unknown>>;
    smms_failures?: Array<Record<string, unknown>>;
    tdms_equipment?: Array<Record<string, unknown>>;
    train_schedule?: Array<Record<string, unknown>>;
  };
  recommendations?: {
    feasible?: boolean;
    status?: string;
    objective_value?: number;
    selected_tasks?: string[];
    rejected_tasks?: Array<Record<string, unknown>>;
    blocks?: Array<Record<string, unknown>>;
    explanation?: string;
    train_conflicts?: Array<Record<string, unknown>>;
  };
  timeline?: {
    sections?: Array<Record<string, unknown>>;
    available?: boolean;
  };
  approval?: {
    required?: boolean;
    auth_required?: boolean;
    status?: string;
    message?: string;
  };
};

export type DashboardSummaryItem = {
  label: string;
  value: string;
  note: string;
};

export type DashboardTask = {
  id: string;
  name: string;
  priority: string;
  section: string;
  route: string;
  status: string;
  source: string;
  detail: string;
};

export type DashboardBlock = {
  id: string;
  name: string;
  priority: string;
  section: string;
  route: string;
  window: string;
  tasks: string[];
  trainConflicts: string[];
  explanation: string;
  powerBlockRequired: boolean;
  powerIsolationCovered: boolean;
  taskCount: number;
};

export type DashboardTrain = {
  id: string;
  trainNo: string;
  serviceType: string;
  section: string;
  route: string;
  origin: string;
  destination: string;
  scheduledDate: string;
  window: string;
  status: string;
};

export type DashboardViewModel = {
  header: {
    title: string;
    subtitle: string;
    systemMode: string;
  };
  summary: DashboardSummaryItem[];
  sections: string[];
  blocks: DashboardBlock[];
  tasks: DashboardTask[];
  trains: DashboardTrain[];
  approvals: {
    required: boolean;
    authRequired: boolean;
    status: string;
    message: string;
  };
  details: {
    selectedTaskIds: string[];
    rejectedTasks: Array<{ taskId: string; reason: string; priority: string }>;
    explanation: string;
    trainConflicts: string[];
    constraints: string[];
  };
};
