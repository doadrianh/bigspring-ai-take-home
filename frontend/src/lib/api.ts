const API_BASE = "http://localhost:8000";

export async function fetchCompanies() {
  const res = await fetch(`${API_BASE}/api/companies`);
  return res.json();
}

export async function fetchUsers(companyId: string) {
  const res = await fetch(`${API_BASE}/api/companies/${companyId}/users`);
  return res.json();
}

export async function fetchUserDetail(userId: string) {
  const res = await fetch(`${API_BASE}/api/users/${userId}`);
  return res.json();
}

export interface SearchCallbacks {
  onIntent: (data: { intent: string; reasoning: string }) => void;
  onAnswerChunk: (text: string) => void;
  onCitations: (citations: any[]) => void;
  onRecommendations: (recs: any[]) => void;
  onDone: () => void;
  onError: (error: string) => void;
}

export async function streamSearch(
  userId: string,
  query: string,
  callbacks: SearchCallbacks
) {
  const res = await fetch(`${API_BASE}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, query }),
  });

  if (!res.ok) {
    callbacks.onError(`Search failed: ${res.statusText}`);
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) {
    callbacks.onError("No response stream");
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    let eventType = "";
    for (const line of lines) {
      if (line.startsWith("event: ")) {
        eventType = line.slice(7).trim();
      } else if (line.startsWith("data: ") && eventType) {
        try {
          const data = JSON.parse(line.slice(6));
          switch (eventType) {
            case "intent":
              callbacks.onIntent(data);
              break;
            case "answer_chunk":
              callbacks.onAnswerChunk(data.text || "");
              break;
            case "citations":
              callbacks.onCitations(data.citations || []);
              break;
            case "recommendations":
              callbacks.onRecommendations(data.recommendations || []);
              break;
            case "done":
              callbacks.onDone();
              break;
          }
        } catch {
          // Skip malformed JSON
        }
        eventType = "";
      }
    }
  }
}
