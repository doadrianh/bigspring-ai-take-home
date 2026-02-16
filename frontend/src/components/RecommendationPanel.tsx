"use client";

interface Recommendation {
  asset_id: string;
  asset_type: string;
  rep_title: string;
  play_title: string;
  file_name: string;
  relevance: number;
}

const typeIcons: Record<string, string> = {
  pdf: "PDF",
  video: "VID",
  image: "IMG",
  audio: "AUD",
};

export default function RecommendationPanel({
  recommendations,
}: {
  recommendations: Recommendation[];
}) {
  if (!recommendations.length) return null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, color: "#6b7280", margin: 0 }}>
        Related Training
      </h3>
      {recommendations.map((r, i) => (
        <div
          key={i}
          style={{
            background: "white",
            borderRadius: 10,
            padding: "12px 14px",
            boxShadow: "0 1px 2px rgba(0,0,0,0.06)",
            cursor: "pointer",
            transition: "box-shadow 0.2s",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.boxShadow = "0 2px 8px rgba(0,0,0,0.12)")}
          onMouseLeave={(e) => (e.currentTarget.style.boxShadow = "0 1px 2px rgba(0,0,0,0.06)")}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <span style={{
              fontSize: 10, fontWeight: 700, color: "white",
              background: "#6366f1", padding: "2px 6px", borderRadius: 4,
            }}>
              {typeIcons[r.asset_type] || r.asset_type.toUpperCase()}
            </span>
            <span style={{ fontSize: 13, fontWeight: 600 }}>
              {r.rep_title}
            </span>
          </div>
          <div style={{ fontSize: 12, color: "#6b7280" }}>
            {r.play_title}
          </div>
        </div>
      ))}
    </div>
  );
}
