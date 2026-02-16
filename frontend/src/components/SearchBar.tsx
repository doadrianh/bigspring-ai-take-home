"use client";
import { useState } from "react";

export default function SearchBar({
  onSearch,
  disabled,
  loading,
}: {
  onSearch: (query: string) => void;
  disabled: boolean;
  loading: boolean;
}) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !disabled && !loading) {
      onSearch(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", gap: 8 }}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={disabled ? "Select a company and user first..." : "Ask a question about your training materials..."}
        disabled={disabled || loading}
        style={{
          flex: 1,
          padding: "12px 16px",
          borderRadius: 12,
          border: "2px solid #e5e7eb",
          fontSize: 15,
          outline: "none",
          transition: "border-color 0.2s",
          background: disabled ? "#f3f4f6" : "white",
        }}
        onFocus={(e) => (e.target.style.borderColor = "#6366f1")}
        onBlur={(e) => (e.target.style.borderColor = "#e5e7eb")}
      />
      <button
        type="submit"
        disabled={disabled || loading || !query.trim()}
        style={{
          padding: "12px 24px",
          borderRadius: 12,
          border: "none",
          background: disabled || loading || !query.trim() ? "#d1d5db" : "#6366f1",
          color: "white",
          fontSize: 15,
          fontWeight: 600,
          cursor: disabled || loading ? "not-allowed" : "pointer",
          transition: "background 0.2s",
          minWidth: 100,
        }}
      >
        {loading ? "Searching..." : "Search"}
      </button>
    </form>
  );
}
