'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

const API_BASE = 'http://localhost:8000';

export default function ReceiptPage() {
  const { id } = useParams();
  const router = useRouter();
  const [receipt, setReceipt] = useState<any>(null);

  useEffect(() => {
    fetch(`${API_BASE}/schedule/receipt/${id}`, {
      credentials: 'include',
    })
      .then(res => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then(setReceipt)
      .catch(() => router.push('/dashboard/user/appointments'));
  }, [id, router]);

  if (!receipt) {
    return <p className="text-gray-400">Loading receipt…</p>;
  }

  return (
    <div className="max-w-xl mx-auto bg-gray-900 p-8 rounded-2xl border border-gray-700 space-y-4">
      <h1 className="text-2xl font-bold text-white">
        Appointment Receipt
      </h1>

      <p className="text-gray-400">
        Receipt ID: {receipt.receipt_id}
      </p>

      <div className="space-y-2">
        <p className="text-white font-semibold">
          {receipt.vehicle.name} ({receipt.vehicle.model})
        </p>
        <p className="text-gray-400">
          Reg No: {receipt.vehicle.registration}
        </p>
      </div>

      <div className="border-t border-gray-700 pt-4 space-y-2">
        <p className="text-gray-300">
          🛠 Service: {receipt.service_type}
        </p>
        <p className="text-gray-300">
          📅 {receipt.appointment_date} ⏰ {receipt.appointment_time}
        </p>
        <p className="text-gray-300">
          Urgency: {receipt.urgency}
        </p>
      </div>

      <button
        onClick={() => router.back()}
        className="mt-4 px-4 py-2 bg-blue-600 rounded-lg text-white"
      >
        Back
      </button>
    </div>
  );
}
