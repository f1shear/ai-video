from anthropic import Anthropic
from anthropic.types import Message, TextBlock
from settings import LLM_MODEL, MODEL_COSTS, MODELS_WITHOUT_THINKING, EXTENDED_THINKING_BUDGET


def make_client() -> Anthropic:
    """Return a new Anthropic client. Call inside the function body, not at module level."""
    return Anthropic()


def get_response_text(response: Message) -> str:
    """Return the first TextBlock from a response — works for both normal and thinking responses."""
    for block in response.content:
        if isinstance(block, TextBlock):
            return block.text
    raise ValueError(f"No TextBlock in response (got {[type(b).__name__ for b in response.content]})")


def thinking_kwargs(model: str, thinking_budget: int, max_tokens: int) -> dict:
    """Return extra kwargs for messages.create when extended thinking is requested."""
    if thinking_budget <= 0 or model in MODELS_WITHOUT_THINKING:
        return {"max_tokens": max_tokens}
    return {
        "max_tokens": thinking_budget + max_tokens,
        "thinking": {"type": "enabled", "budget_tokens": thinking_budget},
    }


def strip_fences(raw: str) -> str:
    """Remove markdown code fences that LLMs sometimes wrap JSON responses in."""
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if "```" in raw:
            raw = raw[:raw.rfind("```")]
    return raw.strip()


def tally(acc: dict, response: Message, model: str = LLM_MODEL) -> None:
    """Accumulate token counts + estimated cost + model name from one Anthropic response into acc."""
    costs = MODEL_COSTS.get(model, {"input": 3.00, "output": 15.00})
    acc["input_tokens"] = acc.get("input_tokens", 0) + response.usage.input_tokens
    acc["output_tokens"] = acc.get("output_tokens", 0) + response.usage.output_tokens
    acc["cost_usd"] = acc.get("cost_usd", 0.0) + (
        response.usage.input_tokens * costs["input"] / 1_000_000
        + response.usage.output_tokens * costs["output"] / 1_000_000
    )
    models: list = acc.get("models", [])
    if model not in models:
        models.append(model)
    acc["models"] = models
