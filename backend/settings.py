LLM_MODEL = "claude-sonnet-4-6"
FAST_MODEL = "claude-haiku-4-5-20251001"
OPUS_MODEL = "claude-opus-4-7"

# USD per million tokens — used for cost estimation shown to the user
MODEL_COSTS: dict[str, dict[str, float]] = {
    LLM_MODEL:  {"input":  3.00, "output": 15.00},
    FAST_MODEL: {"input":  0.80, "output":  4.00},
    OPUS_MODEL: {"input": 15.00, "output": 75.00},
}

# Models that do not support extended thinking
MODELS_WITHOUT_THINKING: set[str] = {FAST_MODEL}

# Thinking token budget when reasoning_effort == "extended"
EXTENDED_THINKING_BUDGET = 8_000
