"use client";

interface Citation {
  index: number;
  source_name: string;
  source_file: string;
  asset_type: string;
  chunk_type: string;
  page?: string;
  start?: string;
  end?: string;
  speaker?: string;
  table_title?: string;
  relevance: number;
  submission_id?: string;
  feedback_score?: number;
  feedback_text?: string;
}

const typeIcons: Record<string, string> = {
  pdf: "PDF",
  video: "VID",
  image: "IMG",
  audio: "AUD",
  text: "TXT",
  submission: "SUB",
};

const typeColors: Record<string, string> = {
  pdf: "#ef4444",
  video: "#8b5cf6",
  image: "#10b981",
  audio: "#f59e0b",
  text: "#3b82f6",
  submission: "#ec4899",
};

export default function CitationCard({ citations }: { citations: Citation[] }) {
  if (!citations.length) return null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, color: "#6b7280", margin: 0 }}>
        Sources ({citations.length})
      </h3>
      {citations.map((c) => (
        <div
          key={c.index}
          style={{
            background: "white",
            borderRadius: 10,
            padding: "12px 14px",
            boxShadow: "0 1px 2px rgba(0,0,0,0.06)",
            borderLeft: `3px solid ${typeColors[c.asset_type] || "#6b7280"}`,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <span style={{
              fontSize: 10, fontWeight: 700, color: "white",
              background: typeColors[c.asset_type] || "#6b7280",
              padding: "2px 6px", borderRadius: 4,
            }}>
              {typeIcons[c.asset_type] || c.asset_type.toUpperCase()}
            </span>
            <span style={{ fontSize: 13, fontWeight: 600 }}>
              [{c.index}] {c.source_name}
            </span>
          </div>
          <div style={{ fontSize: 12, color: "#6b7280" }}>
            {c.page && <span>Page {c.page} </span>}
            {c.start && <span>{c.start} - {c.end} </span>}
            {c.speaker && <span>Speaker: {c.speaker} </span>}
            {c.table_title && <span>Table: {c.table_title} </span>}
            {c.feedback_score != null && (
              <span>Score: {c.feedback_score}/10 </span>
            )}
            <span style={{ float: "right", color: "#9ca3af" }}>
              {Math.round(c.relevance * 100)}% match
            </span>
          </div>
          {c.feedback_text && (
            <div style={{ fontSize: 12, color: "#4b5563", marginTop: 4, fontStyle: "italic" }}>
              {c.feedback_text}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
