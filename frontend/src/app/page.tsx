"use client";
import { useState } from "react";
import CompanySelector from "@/components/CompanySelector";
import UserSelector from "@/components/UserSelector";
import SearchBar from "@/components/SearchBar";
import StreamingAnswer from "@/components/StreamingAnswer";
import CitationCard from "@/components/CitationCard";
import RecommendationPanel from "@/components/RecommendationPanel";
import ThoughtTrace from "@/components/ThoughtTrace";
import { streamSearch } from "@/lib/api";

export default function Home() {
  const [companyId, setCompanyId] = useState("");
  const [userId, setUserId] = useState("");
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState("");
  const [intent, setIntent] = useState("");
  const [reasoning, setReasoning] = useState("");
  const [citations, setCitations] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [error, setError] = useState("");

  const handleCompanyChange = (id: string) => {
    setCompanyId(id);
    setUserId("");
    clearResults();
  };

  const clearResults = () => {
    setAnswer("");
    setIntent("");
    setReasoning("");
    setCitations([]);
    setRecommendations([]);
    setError("");
  };

  const handleSearch = async (query: string) => {
    clearResults();
    setLoading(true);

    try {
      await streamSearch(userId, query, {
        onIntent: (data) => {
          setIntent(data.intent);
          setReasoning(data.reasoning);
        },
        onAnswerChunk: (text) => {
          setAnswer((prev) => prev + text);
        },
        onCitations: (cites) => {
          setCitations(cites);
        },
        onRecommendations: (recs) => {
          setRecommendations(recs);
        },
        onDone: () => {
          setLoading(false);
        },
        onError: (err) => {
          setError(err);
          setLoading(false);
        },
      });
    } catch (e: any) {
      setError(e.message || "An error occurred");
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#f5f7fa" }}>
      {/* Header */}
      <header style={{
        background: "white",
        borderBottom: "1px solid #e5e7eb",
        padding: "16px 24px",
      }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: "#1a1a2e" }}>
              BigSpring Knowledge Search
            </h1>
            <p style={{ margin: 0, fontSize: 13, color: "#6b7280" }}>
              AI-powered search for your sales training materials
            </p>
          </div>
          <div style={{ display: "flex", gap: 16 }}>
            <CompanySelector value={companyId} onChange={handleCompanyChange} />
            <UserSelector companyId={companyId} value={userId} onChange={setUserId} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "24px" }}>
        {/* Search Bar */}
        <div style={{ marginBottom: 20 }}>
          <SearchBar
            onSearch={handleSearch}
            disabled={!userId}
            loading={loading}
          />
        </div>

        {/* Error */}
        {error && (
          <div style={{
            background: "#fef2f2", border: "1px solid #fecaca",
            borderRadius: 8, padding: "12px 16px", marginBottom: 16,
            color: "#dc2626", fontSize: 14,
          }}>
            {error}
          </div>
        )}

        {/* Results Area */}
        {(intent || answer || loading) && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 320px", gap: 20, alignItems: "start" }}>
            {/* Left: Answer */}
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {intent && <ThoughtTrace intent={intent} reasoning={reasoning} />}
              <StreamingAnswer text={answer} loading={loading} />
            </div>

            {/* Right: Citations & Recommendations */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <CitationCard citations={citations} />
              <RecommendationPanel recommendations={recommendations} />
            </div>
          </div>
        )}

        {/* Empty State */}
        {!intent && !answer && !loading && !error && (
          <div style={{
            textAlign: "center", padding: "80px 20px", color: "#9ca3af",
          }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>Search</div>
            <p style={{ fontSize: 16, maxWidth: 500, margin: "0 auto", lineHeight: 1.6 }}>
              {!userId
                ? "Select a company and user above to get started."
                : "Ask a question about your training materials, past submissions, or general sales topics."}
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
