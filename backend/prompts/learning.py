import json

_AUDIENCE_PROMPTS: dict[str, str] = {
    "kids": "Write for children aged 8-12: simple words, fun facts, wonder-based framing.",
    "teens": "Write for teenagers aged 13-17: engaging, direct, include surprising stats.",
    "young_adults": "Write for young adults aged 18-30: authentic depth, unexpected connections.",
    "adults": "Write for adults aged 31-60: substantive, accurate, historically contextual.",
    "seniors": "Write for seniors aged 60+: clear language, historical perspective, living memory context.",
}


def build_learning_prompt(
    transcript_text: str,
    cp_lines: list,
    video_summary: str,
    urls_snippet: str,
    video_duration: float,
    audience: str,
    feedback: str = "",
) -> str:
    """Build the full prompt string for learning script generation."""
    prompt = f"""You are an expert educational content designer. Generate an interactive learning script that powers a side panel alongside a video.

GROUND RULE: Everything you write must be about the VIDEO'S SUBJECT MATTER — the actual topic, places, concepts, or story being discussed. Never write about the video's own structure, the presenter's choices, or how the video teaches. A viewer reading your content should learn facts about the TOPIC, not observations about the VIDEO.

VIDEO SUMMARY:
{video_summary}

CHECKPOINT OVERLAYS ({len(cp_lines)} total):
{chr(10).join(cp_lines)}

FULL TRANSCRIPT:
{transcript_text[:5000]}

VIDEO DURATION: {video_duration:.0f} seconds
TARGET AUDIENCE: {_AUDIENCE_PROMPTS.get(audience, _AUDIENCE_PROMPTS['adults'])}

REFERENCE URLS:
{urls_snippet}

Generate a JSON learning script with this exact structure:
{{
  "title": "engaging 5-8 word title for the learning experience",
  "sections": [
    {{
      "start": <float>,
      "end": <float>,
      "title": "section title, max 6 words",
      "summary": "2-3 sentences — engaging, specific, tells the viewer WHY this part matters",
      "summary_concise": "1-2 sentence condensed version of the summary",
      "summary_detailed": "4-5 sentence expanded version with more context and nuance",
      "key_facts": ["concrete surprising fact", "specific statistic or detail", "contextual insight"],
      "deep_dive": "1-2 extra sentences for curious viewers wanting more context",
      "links": [{{"text": "short label", "url": "full url"}}]
    }}
  ],
  "quiz_points": [
    {{
      "timestamp": <float — when to pause, ideally right after a key fact or chapter end>,
      "question": "clear, engaging question testing comprehension or insight",
      "options": ["option A", "option B", "option C", "option D"],
      "correct_index": <0-3>,
      "explanation": "2-3 sentences: why correct, what makes it interesting, what to remember",
      "hint": "subtle clue without giving away the answer",
      "difficulty": "easy|medium|hard",
      "related_fact": "one surprising related fact the viewer probably does not know",
      "easier_version": "a simpler version of this question suitable for beginners",
      "harder_version": "a more challenging version requiring deeper knowledge or inference"
    }}
  ]
}}

{f"USER FEEDBACK (apply this to improve the output):{chr(10)}{feedback}{chr(10)}{chr(10)}" if feedback else ""}CRITICAL RULES — CONTENT FOCUS:
• Write about the SUBJECT MATTER of the video, NOT about the video's structure or the presenter's choices
• BANNED patterns — never write these:
  - "The presenter explains...", "The speaker demonstrates...", "This section covers..."
  - "Why does the presenter...", "What technique does the speaker use..."
  - "This video teaches...", "The lesson introduces...", "The narrator shows..."
  - Meta-questions about pedagogy, teaching methods, or video structure
• GOOD: key_fact = "Mitochondria produce ATP via oxidative phosphorylation" — about the TOPIC
• BAD: key_fact = "The presenter walks through the concept step by step" — about the VIDEO STRUCTURE
• GOOD quiz question: "What is the primary function of ATP synthase?" — tests CONTENT knowledge
• BAD quiz question: "Why does the presenter establish context before the main lesson?" — tests nothing real
• Quiz questions MUST be answerable from the VIDEO'S SUBJECT MATTER alone — not from watching how it's presented

STRUCTURAL RULES:
1. Sections: use CHAPTER checkpoints as section dividers. If none, divide into logical 30-90s chunks.
2. Section start/end must be floats covering 0 to {video_duration:.0f} with no gaps.
3. Quiz points: 1 per 45-60s of video, minimum 2, maximum 12. Space them at least 25s apart.
4. Quiz questions: mix factual recall, inference, and application. Avoid trivial yes/no.
5. Links: only use URLs from REFERENCE URLS above. Omit links array if no relevant URLs.
6. key_facts: concrete and specific — dates, numbers, names, consequences. Not vague claims.
7. Return ONLY valid JSON. No markdown fences, no extra text."""
    return prompt
