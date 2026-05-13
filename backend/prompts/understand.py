UNDERSTAND_SYSTEM = """You are a video content analyst. Deeply understand this video from its transcript and frames.

Generate a VIDEO UNDERSTANDING — a dense, specific text that captures:
• Exactly what this video is about (use actual names, places, products, commands — never generic descriptions)
• Who appears and what they say or do
• The narrative arc with approximate timestamps for key transitions
• Every topic, entity, and concept mentioned
• Implied audience and purpose
• Anything still unclear or ambiguous

Be specific. If the transcript says "the city" and frames show a recognisable skyline, name it. Extract every useful detail. This drives visual overlay generation.

Return plain text only — no headers, no JSON, no markdown."""


def build_questions_prompt(video_info: str) -> str:
    return f"""Here is an AI's understanding of a video:

{video_info}

Ask 2–4 SHORT questions that ONLY the video creator could answer — things NOT derivable from the transcript or frames, such as:
- Why was this made? (purpose/intent)
- Who is this for? (audience)
- What should a viewer take away?
- Any context the creator wants emphasised?

Rules:
- Each question must be ≤ 8 words
- Each question must include 3–4 specific answer options covering the realistic range
- Do NOT ask about content facts, history, or technical details — the AI determines those from the video
- If purpose and audience are already obvious from the video, return fewer questions

Return ONLY a JSON array (no markdown):
[{{"id": "q1", "question": "Short question?", "options": ["Option A", "Option B", "Option C"]}}]"""


def build_refine_prompt(video_info: str, answers: list) -> str:
    answered = [a for a in answers if str(a.get("answer", "")).strip()]
    if not answered:
        return video_info

    answers_text = "\n".join(
        f"Q: {a['question']}\nA: {a['answer']}"
        for a in answered
    )
    return f"""You have analyzed a video. The creator has answered your clarifying questions.

CURRENT VIDEO UNDERSTANDING:
{video_info}

CREATOR'S ANSWERS (treat as ground truth — never contradict these):
{answers_text}

Update and enrich your VIDEO UNDERSTANDING to incorporate these answers. Use the exact names, details, and context provided. Return the updated understanding as plain text."""
