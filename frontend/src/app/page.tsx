"use client";

import { useEffect, useState } from "react";
import { CameraGrid } from "@/components/camera-grid";
import { EventPanel } from "@/components/event-panel";
import { Header } from "@/components/header";
import { StatsBar } from "@/components/stats-bar";
import { useWebSocket } from "@/hooks/use-websocket";
import { useApi } from "@/hooks/use-api";
import type { Camera, VisionEvent } from "@/lib/types";

export default function Dashboard() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [events, setEvents] = useState<VisionEvent[]>([]);
  const { data: camerasData, refetch } = useApi<Camera[]>("/api/v1/cameras");
  const { lastEvent } = useWebSocket();

  useEffect(() => {
    if (camerasData) {
      setCameras(camerasData);
    }
  }, [camerasData]);

  useEffect(() => {
    if (lastEvent) {
      setEvents((prev) => [lastEvent, ...prev].slice(0, 200));
    }
  }, [lastEvent]);

  return (
    <div className="flex h-screen flex-col">
      <Header cameraCount={cameras.length} />
      <StatsBar cameras={cameras} events={events} />
      <div className="flex flex-1 overflow-hidden">
        <main className="flex-1 overflow-auto p-4">
          <CameraGrid cameras={cameras} />
        </main>
        <aside className="w-96 border-l border-gray-800 overflow-auto">
          <EventPanel events={events} />
        </aside>
      </div>
    </div>
  );
}
