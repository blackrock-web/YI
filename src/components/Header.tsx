import React from "react";
import { ShieldCheck, Cpu, Heart, CheckCircle2, Terminal } from "lucide-react";
import { DashboardState } from "../types";

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  dashboard: DashboardState | null;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, dashboard }) => {
  const tabs = [
    { id: "chat", label: "Assistant Chat", icon: Terminal },
    { id: "tasks", label: "Tasks & Planner", icon: CheckCircle2 },
    { id: "companion", label: "Memory & Companion", icon: Heart },
    { id: "benchmarks", label: "In-House ML Models", icon: Cpu }
  ];

  return (
    <header className="border-b border-neutral-200 bg-white sticky top-0 z-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        {/* Brand & Privacy Status */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-neutral-900 flex items-center justify-center text-white font-bold text-sm tracking-wider shadow-sm">
            AI
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-neutral-900 tracking-tight">MY AI</h1>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                <ShieldCheck className="w-3.5 h-3.5" />
                Local-First & Private
              </span>
            </div>
            <p className="text-xs text-neutral-500">
              In-House Neural Models & Deterministic Engines • 0 External LLMs
            </p>
          </div>
        </div>

        {/* Rapport & Relationship Indicator */}
        {dashboard?.relationship && (
          <div className="hidden lg:flex items-center gap-4 bg-neutral-50 px-3 py-1.5 rounded-lg border border-neutral-200 text-xs text-neutral-600">
            <div className="flex items-center gap-1.5">
              <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" />
              <span>Rapport: <strong>{Math.round(dashboard.relationship.rapport_score * 100)}%</strong></span>
            </div>
            <span className="text-neutral-300">|</span>
            <span>Status: <strong className="text-neutral-800 capitalize">{dashboard.relationship.level.toLowerCase().replace('_', ' ')}</strong></span>
            <span className="text-neutral-300">|</span>
            <span>Interactions: <strong>{dashboard.relationship.interactions_count}</strong></span>
          </div>
        )}

        {/* Tab Navigation */}
        <nav className="flex items-center gap-1 overflow-x-auto pb-1 md:pb-0">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                id={`tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors whitespace-nowrap ${
                  isActive
                    ? "bg-neutral-900 text-white shadow-xs"
                    : "text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
