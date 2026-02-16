from openai import OpenAI
from config import OPENAI_API_KEY, CLASSIFIER_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an intent classifier for a sales training search engine called BigSpring.
Users are sales representatives searching their assigned training materials and personal practice history.

Classify the user's query into exactly one of these intents:

1. KNOWLEDGE_SEARCH - The user wants to find information from their assigned training materials (product guides, videos, specs, diagrams). Examples:
   - "What is the eradication rate for Streptococcus pneumoniae?"
   - "Show me the GridMaster PUE efficiency table"
   - "What is the dosage for Lydrenex?"
   - "Sentilink acceleration speed"
   - "How does Amproxin work?"

2. HISTORY_SEARCH - The user wants to search their OWN past submissions, practice recordings, or feedback they received. Key signals: "my", "I", "my pitch", "my submission", "my feedback", "my score", "when did I", "how did I do". Examples:
   - "When did I mention cooling energy costs?"
   - "What was my score on the last pitch?"
   - "Show me my submission about antibiotics"
   - "What feedback did I get?"

3. GENERAL_PROFESSIONAL - A professional/sales-related question that is NOT about specific training materials or personal history. General sales techniques, industry knowledge, professional development. Examples:
   - "What are common objection handling techniques?"
   - "How do I improve my cold calling?"
   - "What is consultative selling?"

4. OUT_OF_SCOPE - Non-professional, personal, or completely unrelated queries. Examples:
   - "How do I make a chocolate cake?"
   - "What's the weather today?"
   - "Tell me a joke"
   - "Who won the Super Bowl?"

IMPORTANT: If the query references another person's submissions/pitches by name (e.g. "Show me Aaron's pitch"), classify as KNOWLEDGE_SEARCH since they would be searching training materials, not their own history.

Respond with ONLY a JSON object:
{"intent": "<INTENT>", "reasoning": "<brief explanation>"}"""


def classify_intent(query: str) -> dict:
    response = client.chat.completions.create(
        model=CLASSIFIER_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    import json
    result = json.loads(response.choices[0].message.content)
    return {
        "intent": result.get("intent", "KNOWLEDGE_SEARCH"),
        "reasoning": result.get("reasoning", ""),
    }
