"use client";
import { useEffect, useState } from "react";
import { fetchUsers } from "@/lib/api";

interface User {
  id: string;
  username: string;
  display_name: string;
  role: string;
  segment: string;
  is_active: boolean;
}

export default function UserSelector({
  companyId,
  value,
  onChange,
}: {
  companyId: string;
  value: string;
  onChange: (id: string) => void;
}) {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    if (companyId) {
      fetchUsers(companyId).then(setUsers).catch(console.error);
    } else {
      setUsers([]);
    }
  }, [companyId]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <label style={{ fontSize: 12, fontWeight: 600, color: "#6b7280" }}>
        User
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={!companyId}
        style={{
          padding: "8px 12px",
          borderRadius: 8,
          border: "1px solid #d1d5db",
          fontSize: 14,
          background: companyId ? "white" : "#f3f4f6",
          cursor: companyId ? "pointer" : "not-allowed",
        }}
      >
        <option value="">Select a user...</option>
        {users.map((u) => (
          <option key={u.id} value={u.id}>
            {u.display_name} ({u.username}) {!u.is_active ? "[inactive]" : ""}
          </option>
        ))}
      </select>
    </div>
  );
}
