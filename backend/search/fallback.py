from openai import OpenAI
from config import OPENAI_API_KEY, ANSWER_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

DISCLAIMER = (
    "**Note:** This response is based on general professional knowledge, "
    "not your specific BigSpring training materials.\n\n"
)


def generate_fallback_answer(query: str):
    system = """You are a helpful professional sales assistant. The user is a sales representative
asking a general professional question that is NOT about their specific training materials.

Provide a helpful, concise answer based on general sales and professional knowledge.
Keep it practical and actionable. Do NOT reference any specific company products or training materials."""

    stream = client.chat.completions.create(
        model=ANSWER_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": query},
        ],
        temperature=0.3,
        stream=True,
    )
    return stream
