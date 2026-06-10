"use client";

import { AlertCircle, LogIn, LogOut, Scan } from "lucide-react";
import type { VisionEvent } from "@/lib/types";

interface EventPanelProps {
  events: VisionEvent[];
}

export function EventPanel({ events }: EventPanelProps) {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-gray-800 px-4 py-3">
        <h2 className="text-sm font-semibold">Live Events</h2>
        <p className="text-xs text-gray-500">{events.length} events</p>
      </div>
      <div className="flex-1 overflow-auto">
        {events.length === 0 ? (
          <div className="flex h-32 items-center justify-center">
            <p className="text-xs text-gray-500">
              Waiting for events...
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-800/50">
            {events.map((event, i) => (
              <EventRow key={`${event.timestamp}-${i}`} event={event} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function EventRow({ event }: { event: VisionEvent }) {
  const icon = getEventIcon(event.type);
  const time = new Date(event.timestamp * 1000).toLocaleTimeString();

  return (
    <div className="flex items-start gap-3 px-4 py-2.5 hover:bg-gray-900/50 transition-colors">
      <div className="mt-0.5">{icon}</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium truncate">
            {formatEventType(event.type)}
          </p>
          <span className="text-[10px] text-gray-500 whitespace-nowrap ml-2">
            {time}
          </span>
        </div>
        <p className="text-[11px] text-gray-400 truncate">
          {event.camera_name}
          {event.data?.count !== undefined && ` — ${event.data.count} objects`}
        </p>
      </div>
    </div>
  );
}

function getEventIcon(type: string) {
  switch (type) {
    case "detection":
      return <Scan className="h-3.5 w-3.5 text-blue-400" />;
    case "zone_enter":
      return <LogIn className="h-3.5 w-3.5 text-yellow-400" />;
    case "zone_exit":
      return <LogOut className="h-3.5 w-3.5 text-green-400" />;
    default:
      return <AlertCircle className="h-3.5 w-3.5 text-gray-400" />;
  }
}

function formatEventType(type: string): string {
  const labels: Record<string, string> = {
    detection: "Object Detected",
    zone_enter: "Zone Entry",
    zone_exit: "Zone Exit",
    zone_present: "Zone Presence",
    count_crossing: "Line Crossing",
    camera_connected: "Camera Connected",
    camera_disconnected: "Camera Disconnected",
  };
  return labels[type] || type;
}
