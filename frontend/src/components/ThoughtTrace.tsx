"use client";
import { useState } from "react";

const intentLabels: Record<string, { label: string; color: string }> = {
  KNOWLEDGE_SEARCH: { label: "Knowledge Search", color: "#6366f1" },
  HISTORY_SEARCH: { label: "History Search", color: "#ec4899" },
  GENERAL_PROFESSIONAL: { label: "General Professional", color: "#f59e0b" },
  OUT_OF_SCOPE: { label: "Out of Scope", color: "#ef4444" },
};

export default function ThoughtTrace({
  intent,
  reasoning,
}: {
  intent: string;
  reasoning: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const info = intentLabels[intent] || { label: intent, color: "#6b7280" };

  return (
    <div
      style={{
        background: "#f8fafc",
        borderRadius: 8,
        padding: "8px 12px",
        fontSize: 13,
        cursor: "pointer",
        userSelect: "none",
      }}
      onClick={() => setExpanded(!expanded)}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ color: "#9ca3af", fontSize: 11 }}>
          {expanded ? "v" : ">"}
        </span>
        <span style={{ color: "#6b7280" }}>Intent:</span>
        <span style={{
          background: info.color, color: "white",
          padding: "2px 8px", borderRadius: 4,
          fontSize: 11, fontWeight: 600,
        }}>
          {info.label}
        </span>
      </div>
      {expanded && reasoning && (
        <div style={{ marginTop: 6, paddingLeft: 20, color: "#6b7280", fontSize: 12, lineHeight: 1.5 }}>
          {reasoning}
        </div>
      )}
    </div>
  );
}
