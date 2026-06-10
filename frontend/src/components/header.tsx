"use client";

import { Camera, Shield } from "lucide-react";

interface HeaderProps {
  cameraCount: number;
}

export function Header({ cameraCount }: HeaderProps) {
  return (
    <header className="flex items-center justify-between border-b border-gray-800 px-6 py-3">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600">
          <Shield className="h-5 w-5 text-white" />
        </div>
        <h1 className="text-lg font-semibold">VisionGrid</h1>
        <span className="badge-green">
          <Camera className="mr-1 h-3 w-3" />
          {cameraCount} cameras
        </span>
      </div>
      <nav className="flex items-center gap-4 text-sm text-gray-400">
        <button className="hover:text-white transition-colors">Dashboard</button>
        <button className="hover:text-white transition-colors">Cameras</button>
        <button className="hover:text-white transition-colors">Zones</button>
        <button className="hover:text-white transition-colors">Settings</button>
      </nav>
    </header>
  );
}
