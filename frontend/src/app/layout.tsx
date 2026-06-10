import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VisionGrid — Real-time Computer Vision",
  description:
    "Open-source real-time computer vision platform for any camera",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-gray-950 text-gray-100 antialiased">
        {children}
      </body>
    </html>
  );
}
