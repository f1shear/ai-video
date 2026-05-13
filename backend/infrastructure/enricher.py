"""
Travel-vlog enrichment: extract places → Wikipedia facts → research brief.
Two cheap LLM calls (haiku, text-only) + parallel Wikipedia lookups.

Returns: (context_text: str, source_urls: dict[str, str])
  context_text — formatted block injected into the checkpoint-generation prompt
  source_urls  — {place_name: wikipedia_url} for companion HTML generation
"""
import json
import logging
import os
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
from anthropic import Anthropic
from settings import FAST_MODEL

logger = logging.getLogger("checkpoint_overlay")

_WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
_WIKI_SEARCH = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={}&srlimit=1&format=json"
_UA = "CheckpointOverlayGenerator/1.0 (educational)"


def _wiki_fetch(title: str) -> Optional[tuple[str, str]]:
    """Direct lookup by title. Returns (extract_text, canonical_url) or None."""
    try:
        url = _WIKI_API.format(urllib.parse.quote(title, safe=""))
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        if data.get("type") == "disambiguation":
            return None
        extract = data.get("extract", "").strip()
        description = data.get("description", "").strip()
        page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
        if not extract:
            return None
        sentences = re.split(r"(?<=[.!?])\s+", extract)
        short = " ".join(sentences[:2]).strip()
        if description and description.lower() not in short.lower():
            short = f"{description}. {short}"
        return short, page_url
    except Exception as e:
        logger.debug("wiki direct fetch failed '%s': %s", title, e)
        return None


def _wiki_search_then_fetch(query: str) -> Optional[tuple[str, str]]:
    """Search Wikipedia then fetch the top result."""
    try:
        url = _WIKI_SEARCH.format(urllib.parse.quote(query, safe=""))
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        results = data.get("query", {}).get("search", [])
        if not results:
            return None
        top_title = results[0]["title"]
        return _wiki_fetch(top_title)
    except Exception as e:
        logger.debug("wiki search failed '%s': %s", query, e)
        return None


def fetch_fact(place: str) -> Optional[tuple[str, str]]:
    """Try direct lookup, fall back to search. Returns (text, url) or None."""
    result = _wiki_fetch(place)
    if not result:
        result = _wiki_search_then_fetch(place)
    return result


def _extract_entities_llm(transcript_text: str, entity_prompt: str) -> list[str]:
    """
    Haiku (text-only): extract entities from the transcript using the given extraction prompt.
    Returns a deduplicated list capped at 12.
    """
    client = Anthropic()
    response = client.messages.create(
        model=FAST_MODEL,
        max_tokens=400,
        system=(
            "You extract proper nouns from video transcripts. "
            "Return ONLY a JSON array of strings — no explanation, no markdown."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"{entity_prompt} "
                "Include alternate names/spellings if used. Return [] if none found.\n\n"
                f"Transcript:\n{transcript_text[:5000]}"
            ),
        }],
    )
    raw = response.content[0].text.strip()  # type: ignore[union-attr]
    logger.info("entity-extraction LLM raw: %s", raw[:200])
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        return []
    entities = json.loads(match.group(0))
    seen: set[str] = set()
    unique: list[str] = []
    for p in entities:
        if isinstance(p, str) and p.strip() and p.strip().lower() not in seen:
            seen.add(p.strip().lower())
            unique.append(p.strip())
    return unique[:12]


def _extract_places_llm(transcript_text: str) -> list[str]:
    """
    Haiku (text-only): extract every specific place name from the transcript.
    Returns a deduplicated list capped at 12.
    """
    return _extract_entities_llm(
        transcript_text,
        "List every specific place name, city, neighbourhood, island, landmark, "
        "historical site, monument, museum, or named attraction mentioned below.",
    )


def _build_deeper_context_llm(
    transcript_text: str,
    facts_block: str,
    video_type: str,
    researcher_role: str = (
        "You are a travel-content researcher. Your output will be injected into a "
        "video-overlay generation prompt, so write dense, factual bullet notes — "
        "not prose paragraphs. Use '•' bullets. No headers, no markdown, no filler."
    ),
) -> str:
    """
    Haiku (text-only): given the transcript + Wikipedia facts, produce a
    dense bullet research brief injected into the main prompt.
    """
    client = Anthropic()
    response = client.messages.create(
        model=FAST_MODEL,
        max_tokens=600,
        system=researcher_role,
        messages=[{
            "role": "user",
            "content": (
                f"Video type: {video_type}\n\n"
                f"Transcript (partial):\n{transcript_text[:4000]}\n\n"
                f"Wikipedia facts already retrieved:\n{facts_block}\n\n"
                "Produce a compact research brief:\n"
                "1. One-line narrative summary of what happens in the video.\n"
                "2. For each entity: one additional interesting fact "
                "   the viewer would find surprising or memorable.\n"
                "3. Any cultural context, historical periods, or political entities "
                "   mentioned (e.g. USSR, empires, wars) — include founding dates, "
                "   key events, superlatives.\n"
                "Keep each bullet under 20 words. Total response under 500 words."
            ),
        }],
    )
    return response.content[0].text.strip()  # type: ignore[union-attr]


def enrich_travel(transcript_text: str) -> tuple[str, dict[str, str]]:
    """
    Full enrichment pipeline for travel vlogs:
      1. Extract places (haiku, text-only)
      2. Parallel Wikipedia lookups
      3. Deeper context brief (haiku, text-only)

    Returns:
      (context_block, source_urls)
      context_block — formatted string for the main prompt ('' if nothing found)
      source_urls   — {place_name: wikipedia_url} (empty dict if nothing found)
    """
    if not os.getenv("ANTHROPIC_API_KEY"):
        return "", {}

    try:
        places = _extract_places_llm(transcript_text)
    except Exception as e:
        logger.warning("enricher: place extraction failed: %s", e)
        return "", {}

    if not places:
        logger.info("enricher: no places found in transcript")
        return "", {}

    logger.info("enricher: %d places to look up: %s", len(places), places)

    facts: dict[str, str] = {}
    source_urls: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=8) as pool:
        future_to_place = {pool.submit(fetch_fact, p): p for p in places}
        for future in as_completed(future_to_place):
            place = future_to_place[future]
            try:
                result = future.result()
                if result:
                    text, url = result
                    facts[place] = text
                    if url:
                        source_urls[place] = url
                    logger.info("enricher: ✓ '%s' → %s", place, text[:80])
                else:
                    logger.debug("enricher: no fact for '%s'", place)
            except Exception as e:
                logger.debug("enricher: error for '%s': %s", place, e)

    if not facts:
        logger.info("enricher: Wikipedia returned no usable facts")
        return "", {}

    facts_block = "\n".join(f"• {place}: {fact}" for place, fact in facts.items())

    try:
        deeper = _build_deeper_context_llm(transcript_text, facts_block, "travel_vlog")
    except Exception as e:
        logger.warning("enricher: deeper context LLM failed: %s", e)
        deeper = ""

    parts = [
        "═══ TRAVEL ENRICHMENT CONTEXT ═══",
        "",
        "Wikipedia facts about places in this video:",
        facts_block,
    ]
    if deeper:
        parts += ["", "Additional research brief:", deeper]
    parts += ["", "═══ END ENRICHMENT ═══"]

    return "\n".join(parts), source_urls


# ─── Per-type entity extraction configs ───────────────────────────────────────

_VIDEO_TYPE_CONFIG: dict[str, dict] = {
    "travel_vlog": {
        "entity_prompt": (
            "List every specific place name, city, neighbourhood, island, landmark, "
            "historical site, monument, museum, or named attraction mentioned below."
        ),
        "researcher_role": (
            "You are a travel-content researcher. Your output will be injected into a "
            "video-overlay generation prompt, so write dense, factual bullet notes — "
            "not prose paragraphs. Use '•' bullets. No headers, no markdown, no filler."
        ),
        "context_header": "TRAVEL ENRICHMENT CONTEXT",
    },
    "coding_tutorial": {
        "entity_prompt": (
            "List every specific framework, library, programming language, tool, "
            "open-source project, or company name mentioned below."
        ),
        "researcher_role": (
            "You are a software engineering educator who explains adoption rates, "
            "performance benchmarks, and technical context. Your output will be injected "
            "into a video-overlay generation prompt, so write dense, factual bullet notes — "
            "not prose paragraphs. Use '•' bullets. No headers, no markdown, no filler."
        ),
        "context_header": "TECH ENRICHMENT CONTEXT",
    },
    "lecture": {
        "entity_prompt": (
            "List every specific person, historical event, scientific theory, institution, "
            "time period, or discovery mentioned below."
        ),
        "researcher_role": (
            "You are an academic researcher who provides historical/scientific context, "
            "dates, and significance. Your output will be injected into a "
            "video-overlay generation prompt, so write dense, factual bullet notes — "
            "not prose paragraphs. Use '•' bullets. No headers, no markdown, no filler."
        ),
        "context_header": "ACADEMIC ENRICHMENT CONTEXT",
    },
    "product_demo": {
        "entity_prompt": (
            "List every specific product name, company, technology, standard, "
            "or platform mentioned below."
        ),
        "researcher_role": (
            "You are a market researcher who knows adoption stats, founding dates, and "
            "market context. Your output will be injected into a video-overlay generation "
            "prompt, so write dense, factual bullet notes — "
            "not prose paragraphs. Use '•' bullets. No headers, no markdown, no filler."
        ),
        "context_header": "PRODUCT ENRICHMENT CONTEXT",
    },
    "sales_demo": {
        "entity_prompt": (
            "List every specific product name, company, technology, standard, "
            "or platform mentioned below."
        ),
        "researcher_role": (
            "You are a market researcher who knows adoption stats, founding dates, and "
            "market context. Your output will be injected into a video-overlay generation "
            "prompt, so write dense, factual bullet notes — "
            "not prose paragraphs. Use '•' bullets. No headers, no markdown, no filler."
        ),
        "context_header": "PRODUCT ENRICHMENT CONTEXT",
    },
    "onboarding": {
        "entity_prompt": (
            "List every specific tool, platform, software product, process, "
            "company name, or product name mentioned below."
        ),
        "researcher_role": (
            "You are a market researcher who knows adoption stats, founding dates, and "
            "market context. Your output will be injected into a video-overlay generation "
            "prompt, so write dense, factual bullet notes — "
            "not prose paragraphs. Use '•' bullets. No headers, no markdown, no filler."
        ),
        "context_header": "PRODUCT ENRICHMENT CONTEXT",
    },
}


def enrich_from_video_info(video_info: str) -> tuple[str, dict[str, str]]:
    """
    Enrichment pipeline driven by the pre-generated video understanding.
    Extracts named entities from video_info, looks them up on Wikipedia,
    and builds a research brief injected into the checkpoint-generation prompt.

    Returns (context_block, source_urls).
    """
    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        return "", {}

    entity_prompt = (
        "List every specific named entity mentioned below: places, people, products, "
        "technologies, historical events, institutions, or concepts with a proper name."
    )
    researcher_role = (
        "You are a research analyst. Your output will be injected into a video-overlay "
        "generation prompt, so write dense, factual bullet notes — not prose paragraphs. "
        "Use '•' bullets. No headers, no markdown, no filler."
    )

    try:
        entities = _extract_entities_llm(video_info, entity_prompt)
    except Exception as e:
        logger.warning("enricher: entity extraction failed: %s", e)
        return "", {}

    if not entities:
        logger.info("enricher: no entities found in video_info")
        return "", {}

    logger.info("enricher: %d entities to look up: %s", len(entities), entities)

    facts: dict[str, str] = {}
    source_urls: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=8) as pool:
        future_to_entity = {pool.submit(fetch_fact, e): e for e in entities}
        for future in as_completed(future_to_entity):
            entity = future_to_entity[future]
            try:
                result = future.result()
                if result:
                    text, url = result
                    facts[entity] = text
                    if url:
                        source_urls[entity] = url
                    logger.info("enricher: ✓ '%s' → %s", entity, text[:80])
                else:
                    logger.debug("enricher: no fact for '%s'", entity)
            except Exception as e:
                logger.debug("enricher: error for '%s': %s", entity, e)

    if not facts:
        logger.info("enricher: Wikipedia returned no usable facts")
        return "", {}

    facts_block = "\n".join(f"• {entity}: {fact}" for entity, fact in facts.items())

    try:
        deeper = _build_deeper_context_llm(video_info, facts_block, "video", researcher_role=researcher_role)
    except Exception as e:
        logger.warning("enricher: deeper context LLM failed: %s", e)
        deeper = ""

    parts = [
        "═══ ENRICHMENT CONTEXT ═══",
        "",
        "Wikipedia facts about entities in this video:",
        facts_block,
    ]
    if deeper:
        parts += ["", "Additional research brief:", deeper]
    parts += ["", "═══ END ENRICHMENT ═══"]

    return "\n".join(parts), source_urls


def enrich_video(transcript_text: str, video_type: str) -> tuple[str, dict[str, str]]:
    """
    Full enrichment pipeline for any supported video type.
    Dispatches to enrich_travel for travel_vlog; handles all other types generically.

    Returns:
      (context_block, source_urls)
      context_block — formatted string for the main prompt ('' if nothing found)
      source_urls   — {entity_name: wikipedia_url} (empty dict if nothing found)
    """
    if video_type == "travel_vlog":
        return enrich_travel(transcript_text)

    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        return "", {}

    # Fall back to lecture config for unknown types
    cfg = _VIDEO_TYPE_CONFIG.get(video_type, _VIDEO_TYPE_CONFIG["lecture"])
    entity_prompt = cfg["entity_prompt"]
    researcher_role = cfg["researcher_role"]
    context_header = cfg["context_header"]

    try:
        entities = _extract_entities_llm(transcript_text, entity_prompt)
    except Exception as e:
        logger.warning("enricher: entity extraction failed for %s: %s", video_type, e)
        return "", {}

    if not entities:
        logger.info("enricher: no entities found in transcript for %s", video_type)
        return "", {}

    logger.info("enricher: %d entities to look up for %s: %s", len(entities), video_type, entities)

    facts: dict[str, str] = {}
    source_urls: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=8) as pool:
        future_to_entity = {pool.submit(fetch_fact, e): e for e in entities}
        for future in as_completed(future_to_entity):
            entity = future_to_entity[future]
            try:
                result = future.result()
                if result:
                    text, url = result
                    facts[entity] = text
                    if url:
                        source_urls[entity] = url
                    logger.info("enricher: ✓ '%s' → %s", entity, text[:80])
                else:
                    logger.debug("enricher: no fact for '%s'", entity)
            except Exception as e:
                logger.debug("enricher: error for '%s': %s", entity, e)

    if not facts:
        logger.info("enricher: Wikipedia returned no usable facts for %s", video_type)
        return "", {}

    facts_block = "\n".join(f"• {entity}: {fact}" for entity, fact in facts.items())

    try:
        deeper = _build_deeper_context_llm(
            transcript_text, facts_block, video_type, researcher_role=researcher_role
        )
    except Exception as e:
        logger.warning("enricher: deeper context LLM failed: %s", e)
        deeper = ""

    parts = [
        f"═══ {context_header} ═══",
        "",
        "Wikipedia facts about entities in this video:",
        facts_block,
    ]
    if deeper:
        parts += ["", "Additional research brief:", deeper]
    parts += ["", f"═══ END {context_header} ═══"]

    return "\n".join(parts), source_urls
