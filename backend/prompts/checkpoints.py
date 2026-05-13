from domain.models import OverlayRole

ANNOTATION_GUIDANCE = """
Think of yourself as a knowledgeable guide watching this specific video with the viewer.
Your job is to surface what's genuinely interesting or worth knowing at each moment — drawn from the actual content above, not invented.

Ask yourself at each moment: "What is actually happening here, and what would a curious viewer want to know about it?"

A good overlay names or explains something specific to THIS video:
  "Split's Diocletian Palace, 305 AD"
  "Adriatic depth here: under 50m — unusually clear"
  "git rebase -i rewrites commit history non-destructively"

A poor overlay describes the video's own structure rather than its content:
  "Opening", "Key concept", "Important moment", "Conclusion"

The test: if the same label could appear in a completely different video, it is not specific enough.
Only annotate when you have something concrete and interesting to say. Fewer precise annotations beat many vague ones.
"""

STYLE_NOTES: dict = {
    "clean":     "Use clear, neutral wording. No hype. Simple labels.",
    "cinematic": "Use restrained, elegant wording. Fewer checkpoints. Evocative but brief.",
    "bold":      "Use punchy, energetic wording. Strong action verbs. Short and impactful.",
    "minimal":   "Use very short labels only. No sub_text if possible.",
}

CHECKPOINT_INTERVAL = 20  # seconds between checkpoints (soft guide)

MOCK_CHECKPOINTS = [
    ("Opening", None, OverlayRole.label),
    ("Key concept", None, OverlayRole.fact),
    ("Part 2", None, OverlayRole.chapter),
    ("Important detail", "Context here", OverlayRole.annotation),
    ("Call to action", None, OverlayRole.cta),
    ("Closing", None, OverlayRole.label),
]

# ─── Duration caps per role ────────────────────────────────────────────────────

_DURATION_CAPS: dict = {
    OverlayRole.label:      (3.0, 7.0),
    OverlayRole.fact:       (3.5, 7.0),
    OverlayRole.chapter:    (2.0, 3.5),
    OverlayRole.annotation: (3.0, 6.0),
    OverlayRole.cta:        (5.0, 10.0),
}
