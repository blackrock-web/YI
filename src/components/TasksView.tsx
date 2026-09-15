import React, { useState } from "react";
import { Plus, Check, Calendar, Clock, AlertCircle, CheckCircle2 } from "lucide-react";
import { TaskItem, ScheduleSlot } from "../types";

interface TasksViewProps {
  tasks: TaskItem[];
  schedule: ScheduleSlot[];
  onCreateTask: (title: string, priority: string) => Promise<void>;
  onCompleteTask: (taskId: string) => Promise<void>;
}

export const TasksView: React.FC<TasksViewProps> = ({
  tasks,
  schedule,
  onCreateTask,
  onCompleteTask,
}) => {
  const [newTitle, setNewTitle] = useState("");
  const [newPriority, setNewPriority] = useState("MEDIUM");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || isSubmitting) return;
    setIsSubmitting(true);
    await onCreateTask(newTitle.trim(), newPriority);
    setNewTitle("");
    setIsSubmitting(false);
  };

  const getPriorityBadge = (pri: string) => {
    const p = pri.toUpperCase();
    if (p.includes("URGENT")) {
      return "bg-rose-50 text-rose-700 border-rose-200";
    }
    if (p.includes("HIGH")) {
      return "bg-amber-50 text-amber-700 border-amber-200";
    }
    if (p.includes("LOW")) {
      return "bg-neutral-100 text-neutral-600 border-neutral-200";
    }
    return "bg-blue-50 text-blue-700 border-blue-200";
  };

  const pendingTasks = tasks.filter((t) => !t.status.toUpperCase().includes("COMPLETED"));
  const completedTasks = tasks.filter((t) => t.status.toUpperCase().includes("COMPLETED"));

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Quick Add Form */}
      <div className="bg-white rounded-xl border border-neutral-200 p-5 shadow-2xs">
        <h2 className="text-sm font-semibold text-neutral-900 mb-3 flex items-center gap-2">
          <Plus className="w-4 h-4 text-neutral-700" />
          Add New Task
        </h2>
        <form onSubmit={handleCreate} className="flex flex-col sm:flex-row gap-3">
          <input
            id="task-title-input"
            type="text"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="What needs to be done?"
            className="flex-1 px-3.5 py-2 text-sm bg-neutral-50 border border-neutral-300 rounded-lg focus:outline-none focus:border-neutral-900 focus:ring-1 focus:ring-neutral-900"
          />
          <select
            id="task-priority-select"
            value={newPriority}
            onChange={(e) => setNewPriority(e.target.value)}
            className="px-3 py-2 text-sm bg-neutral-50 border border-neutral-300 rounded-lg focus:outline-none focus:border-neutral-900"
          >
            <option value="LOW">Low Priority</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="HIGH">High Priority</option>
            <option value="URGENT">Urgent Priority</option>
          </select>
          <button
            type="submit"
            id="create-task-submit"
            disabled={!newTitle.trim() || isSubmitting}
            className="px-4 py-2 bg-neutral-900 text-white rounded-lg text-sm font-medium hover:bg-neutral-800 disabled:opacity-40 transition-colors"
          >
            {isSubmitting ? "Adding..." : "Add Task"}
          </button>
        </form>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: Tasks */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-neutral-900 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-neutral-700" />
              Active Tasks ({pendingTasks.length})
            </h3>
          </div>

          <div className="space-y-2.5">
            {pendingTasks.length === 0 ? (
              <div className="text-center py-8 border border-dashed border-neutral-200 rounded-xl text-neutral-400 text-sm">
                No active tasks. You're completely caught up!
              </div>
            ) : (
              pendingTasks.map((t) => (
                <div
                  key={t.id}
                  className="bg-white border border-neutral-200 rounded-xl p-3.5 flex items-center justify-between gap-3 shadow-2xs hover:border-neutral-300 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-neutral-900 truncate">{t.title}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`text-2xs px-2 py-0.5 rounded border font-medium ${getPriorityBadge(t.priority)}`}>
                        {t.priority.replace("Priority.", "")}
                      </span>
                      {t.estimated_duration_min && (
                        <span className="text-2xs text-neutral-400 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {t.estimated_duration_min} min
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => onCompleteTask(t.id)}
                    title="Mark task completed"
                    className="p-1.5 rounded-lg border border-neutral-200 hover:border-emerald-300 hover:bg-emerald-50 text-neutral-500 hover:text-emerald-700 transition-colors"
                  >
                    <Check className="w-4 h-4" />
                  </button>
                </div>
              ))
            )}
          </div>

          {completedTasks.length > 0 && (
            <div className="pt-4 border-t border-neutral-200">
              <h4 className="text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-3">
                Completed ({completedTasks.length})
              </h4>
              <div className="space-y-2 opacity-60">
                {completedTasks.slice(0, 4).map((t) => (
                  <div
                    key={t.id}
                    className="bg-neutral-50 border border-neutral-200 rounded-lg p-2.5 flex items-center justify-between"
                  >
                    <span className="text-xs line-through text-neutral-600 truncate">{t.title}</span>
                    <span className="text-2xs text-neutral-400">Done</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Algorithmic Daily Schedule */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-neutral-900 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-neutral-700" />
              Algorithmic Day Plan
            </h3>
            <span className="text-2xs bg-neutral-100 text-neutral-600 px-2 py-0.5 rounded border border-neutral-200 font-mono">
              Interval Optimization
            </span>
          </div>

          <div className="space-y-2.5">
            {schedule.length === 0 ? (
              <div className="text-center py-8 border border-dashed border-neutral-200 rounded-xl text-neutral-400 text-sm">
                No schedule slots planned for today yet.
              </div>
            ) : (
              schedule.map((slot, idx) => (
                <div
                  key={idx}
                  className="bg-white border border-neutral-200 rounded-xl p-3.5 flex items-center gap-4 shadow-2xs"
                >
                  <div className="w-24 shrink-0 font-mono text-xs font-semibold text-neutral-600">
                    {slot.start_time} - {slot.end_time}
                  </div>
                  <div className="w-px h-8 bg-neutral-200" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-neutral-900 truncate">{slot.title}</p>
                    <span className="text-2xs text-neutral-400 capitalize">{slot.slot_type.toLowerCase()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
