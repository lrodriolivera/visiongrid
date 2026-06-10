"use client";

import { VideoOff } from "lucide-react";
import type { Camera } from "@/lib/types";

interface CameraGridProps {
  cameras: Camera[];
}

export function CameraGrid({ cameras }: CameraGridProps) {
  if (cameras.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <VideoOff className="mx-auto h-12 w-12 text-gray-600" />
          <h3 className="mt-4 text-lg font-medium text-gray-300">
            No cameras configured
          </h3>
          <p className="mt-2 text-sm text-gray-500">
            Add cameras via the API or configuration file to get started.
          </p>
          <code className="mt-4 inline-block rounded bg-gray-900 px-3 py-2 text-xs text-gray-400">
            POST /api/v1/cameras
          </code>
        </div>
      </div>
    );
  }

  const gridCols =
    cameras.length === 1
      ? "grid-cols-1"
      : cameras.length <= 4
        ? "grid-cols-2"
        : "grid-cols-3";

  return (
    <div className={`grid ${gridCols} gap-4`}>
      {cameras.map((camera) => (
        <CameraCard key={camera.name} camera={camera} />
      ))}
    </div>
  );
}

function CameraCard({ camera }: { camera: Camera }) {
  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const streamUrl = `${apiUrl}/api/v1/stream/${camera.name}`;

  return (
    <div className="grid-camera relative group">
      {camera.status === "connected" ? (
        <img
          src={streamUrl}
          alt={camera.name}
          className="h-full w-full object-cover"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center bg-gray-900">
          <div className="text-center">
            <VideoOff className="mx-auto h-8 w-8 text-gray-600" />
            <p className="mt-2 text-xs text-gray-500">{camera.status}</p>
          </div>
        </div>
      )}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">{camera.name}</span>
          <span
            className={
              camera.status === "connected" ? "badge-green" : "badge-red"
            }
          >
            {camera.status}
          </span>
        </div>
      </div>
    </div>
  );
}
