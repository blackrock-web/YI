export interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  intent?: string;
  confidence?: number;
  emotion?: string;
  valence?: number;
  arousal?: number;
  timestamp: string;
}

export interface TaskItem {
  id: string;
  title: string;
  priority: string;
  status: string;
  category?: string;
  estimated_duration_min?: number;
  created_at: string;
}

export interface ScheduleSlot {
  start_time: string;
  end_time: string;
  title: string;
  slot_type: string;
  priority?: string;
}

export interface DashboardState {
  tasks: TaskItem[];
  schedule: ScheduleSlot[];
  relationship: {
    level: string;
    rapport_score: number;
    interactions_count: number;
    shared_memories_count: number;
  };
  recent_memories: { key: string; value: string }[];
  privacy: {
    strict_privacy_mode: boolean;
    cloud_telemetry_disabled: boolean;
    local_database_only: boolean;
    allow_external_model_calls: boolean;
    compliance_status: string;
  };
}

export interface BenchmarkResult {
  intent_classification: {
    total_tests: number;
    passed: number;
    accuracy_pct: number;
  };
  planner_performance: {
    slots_planned: number;
    latency_ms: number;
    status: string;
  };
  privacy_compliance: {
    offline_strict: boolean;
    no_external_models: boolean;
    status: string;
  };
  overall_status: string;
}
