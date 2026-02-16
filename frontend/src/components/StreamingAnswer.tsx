"use client";
import ReactMarkdown from "react-markdown";

export default function StreamingAnswer({
  text,
  loading,
}: {
  text: string;
  loading: boolean;
}) {
  if (!text && !loading) return null;

  return (
    <div
      style={{
        background: "white",
        borderRadius: 12,
        padding: "20px 24px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
        lineHeight: 1.7,
        fontSize: 15,
      }}
    >
      {loading && !text && (
        <div style={{ display: "flex", alignItems: "center", gap: 8, color: "#9ca3af" }}>
          <div style={{
            width: 8, height: 8, borderRadius: "50%", background: "#6366f1",
            animation: "pulse 1.5s infinite",
          }} />
          Searching and generating answer...
          <style>{`@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }`}</style>
        </div>
      )}
      {text && (
        <div className="markdown-body">
          <ReactMarkdown>{text}</ReactMarkdown>
        </div>
      )}
      {loading && text && (
        <span style={{
          display: "inline-block", width: 6, height: 16,
          background: "#6366f1", marginLeft: 2,
          animation: "blink 0.8s infinite",
          verticalAlign: "text-bottom",
        }}>
          <style>{`@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }`}</style>
        </span>
      )}
    </div>
  );
}
