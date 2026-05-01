'use client';

export default function UserLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-900">
      {children}
    </div>
  );
}
