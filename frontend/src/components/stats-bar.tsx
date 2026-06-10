"use client";

import { Activity, AlertTriangle, Eye, Users } from "lucide-react";
import type { Camera, VisionEvent } from "@/lib/types";

interface StatsBarProps {
  cameras: Camera[];
  events: VisionEvent[];
}

export function StatsBar({ cameras, events }: StatsBarProps) {
  const connected = cameras.filter((c) => c.status === "connected").length;
  const detections = events.filter((e) => e.type === "detection").length;
  const alerts = events.filter(
    (e) => e.type === "zone_enter" || e.type === "zone_exit"
  ).length;

  return (
    <div className="grid grid-cols-4 gap-4 border-b border-gray-800 px-6 py-3">
      <StatCard
        icon={<Eye className="h-4 w-4 text-brand-400" />}
        label="Cameras Online"
        value={`${connected}/${cameras.length}`}
      />
      <StatCard
        icon={<Activity className="h-4 w-4 text-green-400" />}
        label="Detections"
        value={detections.toString()}
      />
      <StatCard
        icon={<Users className="h-4 w-4 text-blue-400" />}
        label="People Counted"
        value="—"
      />
      <StatCard
        icon={<AlertTriangle className="h-4 w-4 text-yellow-400" />}
        label="Zone Alerts"
        value={alerts.toString()}
      />
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-3 rounded-lg bg-gray-900 px-4 py-2">
      {icon}
      <div>
        <p className="text-xs text-gray-400">{label}</p>
        <p className="text-sm font-semibold">{value}</p>
      </div>
    </div>
  );
}
