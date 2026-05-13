# Checkpoint Overlay Generator — Codebase Guide

## What this project does

Takes a user-uploaded video, analyses it with AI, and produces:
1. **Overlaid video** — the original video with checkpoint annotations burned in via FFmpeg
2. **Interactive HTML player** — side panel with facts, quiz points, and section summaries

Run everything: `./start.sh`

---

## Ubiquitous language

These terms are used consistently everywhere — code, docs, and UI. When in doubt, use these exact words.

| Term | Meaning |
|------|---------|
| **Job** | The unit of work. Created on upload, persists all state from upload through export. |
| **Checkpoint** | A single timed annotation: text, position, role, template, confidence. The core domain object. |
| **Overlay** | A checkpoint rendered visually onto a video frame. Use this term only in the rendering/FFmpeg context. |
| **Transcript** | Audio-to-text output — a list of `TranscriptSegment` (start, end, text). |
| **Clarification context** | The user's answers from the Clarify step, compiled into a string passed to all downstream prompts. |
| **Learning content** | The structured side-panel output: sections (title, summary, key facts) + quiz points. Called `learning_script` in code. |
| **AI quality review** | The automated LLM pass that improves checkpoint quality before the user sees results. Not the same as the Review step. |
| **Pre-analysis** | Transcribe + generate clarifying questions. Runs during the Clarify step. |
| **Analysis** | The main processing pipeline: transcribe (cached) → generate checkpoints → AI quality review → generate learning content. Runs during the Process step. |
| **Export** | The rendering pipeline: burn checkpoints onto video + build HTML player. Runs during the Export step. |

---

## Pipeline

```
Upload      job created, video stored
Configure   user sets VideoType, Style, Audience, Format
Clarify     pre-analysis: transcribe + generate targeted questions; user confirms AI's guesses
Process     Analysis: transcribe (cached) → checkpoints → AI quality review → learning content
Review      user edits checkpoints and learning content
Export      Rendering: burn checkpoints onto video → build HTML player
```

Phases run as background threads. Progress streams to the frontend via SSE.

```
[Clarify]   backend/api/pipeline.py → run_clarify()
[Process]   backend/api/pipeline.py → run_analysis()
[Export]    backend/api/pipeline.py → run_export()
```

---

## Directory structure

```
backend/
  settings.py      ← Process-wide constants (LLM_MODEL). No layer restrictions — any layer may import.

  domain/          ← DOMAIN LAYER. The problem domain expressed in code.
  |                   Pure Python only: Pydantic models, enums, constants. No I/O, no frameworks.
    models.py        Checkpoint, CheckpointAlternative, ProcessConfig, TranscriptSegment,
                     JobStatus, VideoType, Style, Audience, OverlayRole, OverlayTemplate, …

  prompts/         ← PROMPT LAYER. LLM instructions — what the AI is asked to do and how.
  |                   Strings only. No business logic, no I/O, no model instantiation.
    checkpoints.py   TYPE_PROMPTS, STYLE_NOTES, _QUALITY_MANDATES, _AUDIENCE_GUIDANCE
    learning.py      build_learning_prompt() → str
    clarify.py       build_clarify_prompt() → str, question type configs
    review.py        build_review_prompt() → str

  services/        ← APPLICATION LAYER. Orchestrates domain + prompts + infrastructure.
  |                   Pure functions: typed inputs → typed outputs. No HTTP, no store access.
    checkpoint_service.py   generate_checkpoints()  → (summary, checkpoints, source_urls)
    learning_service.py     generate_learning_script() → dict (learning content)
    review_service.py       review_checkpoints()    → (checkpoints, review_notes)
    clarify_service.py      generate_questions(), transcribe_for_clarify()
    _llm.py                 make_client(), strip_fences(), re-exports LLM_MODEL

  infrastructure/  ← INFRASTRUCTURE LAYER. All external I/O. No business logic.
  |                   Wraps FFmpeg, Whisper, Pillow, Wikipedia, HTML generation.
    transcriber.py    transcribe() → list[TranscriptSegment], get_video_duration()
    frames.py         extract_frames() → list of base64 JPEG frames
    scene_cuts.py     detect_scene_cuts(), snap_to_cut()
    overlay.py        apply_overlays() — burns checkpoints onto video via Pillow + FFmpeg
    enricher.py       enrich_video() — Wikipedia facts for named entities
    player.py         build_player_html() — self-contained interactive HTML player

  api/             ← INTERFACE LAYER. HTTP handlers, job lifecycle, SSE streaming.
  |                   Thin: validate → dispatch → return. No business logic.
    config.py         UPLOAD_DIR, ALLOWED_VIDEO_EXTENSIONS (HTTP-layer constants only)
    job_store.py      JobDict (TypedDict), JobStore — typed in-memory job state
    events.py         emit(), emit_clarify() — write status + push to SSE queue
    pipeline.py       run_clarify(), run_analysis(), run_export() — phase orchestration
    schemas.py        HTTP request/response schemas (Pydantic). Not domain models.
    routes.py         FastAPI route handlers — one function per endpoint

  main.py          ← App entry point: FastAPI instance, CORS, router. Nothing else.

frontend/
  src/
    types.ts         TypeScript mirrors of domain/models.py — keep in sync manually
    App.tsx          Step state machine: Upload → Configure → Clarify → Process → Review → Export
    components/
      StepUpload.tsx
      StepConfigure.tsx
      StepClarify.tsx    SSE from /pre-analyze-events/{job_id} — streams clarifying questions
      StepProcess.tsx    SSE from /events/{job_id} — streams analysis progress
      StepReview.tsx     User edits checkpoints and learning content; calls /regenerate endpoints
      StepExport.tsx     SSE from /export-events/{job_id} — streams export progress
```

---

## Data flow rules

**Explicit in, explicit out.** Every function takes typed inputs and returns typed values.
No function reads from or writes to the `JobStore` except `pipeline.py`.

```
HTTP request → routes.py
    ↓ reads job from store (JobDict)
    ↓ starts threading.Thread(target=pipeline.run_analysis, args=(job_id, config))
    ↓ returns {"status": "started"} immediately

threading.Thread runs:
    pipeline.run_analysis(job_id, config)
        ↓ store.require(job_id) → JobDict
        ↓ services.generate_checkpoints(transcript, ...) → (summary, checkpoints, source_urls)
        ↓ store.update(job_id, checkpoints=checkpoints, ...)
        ↓ events.emit(job_id, status, message, progress)
            ↓ writes to job status + puts JSON onto job["queue"] asyncio.Queue

SSE endpoint /events/{job_id}:
    async for event in queue: yield f"data: {event}\n\n"
```

**Key rule**: `pipeline.py` is the only place that writes to the store during processing. Routes read from the store to build HTTP responses — they do not write during a running phase.

---

## Adding a new pipeline step

1. **Add domain models** to `domain/models.py` — Pydantic classes, enums, constants
2. **Add prompt strings** to the relevant file in `prompts/` — no logic, strings only
3. **Add the service function** to `services/` — pure function, typed in/out, no HTTP, no store access
4. **Orchestrate it** in `api/pipeline.py` inside `run_analysis` or `run_export`
5. **Add the route** to `api/routes.py` if user interaction is needed — thin handler only
6. **Mirror new model fields** in `frontend/src/types.ts`
7. **Update the relevant Step component** in `frontend/src/components/`

---

## Adding a new video type

1. Add the enum value to `VideoType` in `domain/models.py`
2. Add the checkpoint generation prompt to `TYPE_PROMPTS` in `prompts/checkpoints.py`
3. Add entity/intent question configs to `prompts/clarify.py`
4. Add the card to `VIDEO_TYPES` array in `frontend/src/components/StepConfigure.tsx`
5. Add mock checkpoints to `MOCK_CHECKPOINTS` in `prompts/checkpoints.py`

---

## Changing AI behaviour

All prompt strings live in `prompts/`. No prompt content belongs in services or infrastructure.

| What to change | Where |
|---|---|
| Checkpoint content, roles, confidence rules | `prompts/checkpoints.py` |
| Learning content structure, quiz point rules | `prompts/learning.py` |
| Clarifying questions, answer options | `prompts/clarify.py` |
| AI quality review criteria | `prompts/review.py` |

The LLM model is set in `settings.py` (backend root) as `LLM_MODEL`. Change it once, affects all services.

---

## Job lifecycle

A `JobDict` lives in `JobStore` from upload to export. Canonical schema (see `api/job_store.py`):

```python
{
  "status": str,                # JobStatus value — current pipeline state
  "message": str,               # human-readable status for the UI
  "progress": int,              # 0–100
  "video_path": Path,           # uploaded file on disk
  "filename": str,              # original filename
  "duration": float,            # video duration in seconds
  "config": ProcessConfig | None,       # user's configuration (set on /process)
  "transcript": list[TranscriptSegment],
  "checkpoints": list[Checkpoint],
  "video_summary": str,
  "source_urls": dict[str, str],        # entity name → Wikipedia URL
  "learning_script": dict | None,       # {title, sections, quiz_points} — learning content
  "output": Path | None,                # rendered video path (set after export)
  "player_html": str | None,            # self-contained HTML player (set after export)
  "queue_analysis": asyncio.Queue,      # analysis SSE events
  "queue_export": asyncio.Queue,        # export SSE events
  "queue_clarify": asyncio.Queue,       # clarify SSE events
  "loop": asyncio.AbstractEventLoop,
  # optional — set by /export route when user submits edited learning content:
  "_export_learning_script": dict,
}
```

---

## Frontend ↔ Backend contract

Keep `frontend/src/types.ts` in sync with `backend/domain/models.py`.
The TypeScript types are manual mirrors — there is no codegen.

When you change a Pydantic model field:
1. Update `domain/models.py`
2. Update the matching interface in `types.ts`
3. Update any component that reads/writes that field

Key endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/upload` | POST | Upload video, create job |
| `/pre-analyze/{id}` | POST | Start Clarify step |
| `/pre-analyze-events/{id}` | GET SSE | Stream clarify progress + questions |
| `/process/{id}` | POST | Start analysis (Process step) |
| `/events/{id}` | GET SSE | Stream analysis progress |
| `/checkpoints/{id}` | GET | Fetch analysis results |
| `/regenerate/{id}` | POST | Re-run checkpoints + learning content with feedback |
| `/regenerate-learning/{id}` | POST | Re-run learning content only with feedback |
| `/export/{id}` | POST | Start export (render video) |
| `/export-events/{id}` | GET SSE | Stream export progress |
| `/frame/{id}?t=N` | GET | Extract single video frame as JPEG |
| `/download/{id}` | GET | Download rendered MP4 |
| `/player/{id}` | GET | Serve self-contained HTML player |

---

## Conventions

### Python
- One public function per service module, named after its action: `generate_checkpoints()`, `review_checkpoints()`, `generate_questions()`
- Private helpers: prefix with `_`, live in the same file as their only caller
- LLM client: import `Anthropic` at module top; call `make_client()` (from `services/_llm.py`) inside the function body — never at module level
- JSON parsing: always wrap in `try/except`; fall back to a safe default rather than surfacing a raw exception to the user
- Type hints on all public functions
- No `import *`

### TypeScript / React
- All shared types in `types.ts` — no inline interfaces in component files for domain objects
- Each Step component owns its own state; passes results up via `onComplete(result)` callback
- SSE streams: open in `useEffect` with `started = useRef(false)` guard to prevent double-fire in dev
- API base URL: `http://localhost:8000` hardcoded in each component — fine for local MVP

### General
- No comments explaining WHAT code does — name things well instead
- Comments only for WHY: hidden constraints, workarounds, non-obvious invariants
- No error handling for scenarios that cannot happen — trust Pydantic validation
- Do not add logging beyond what's already there unless debugging a specific issue

---

## What NOT to do

- **Don't add business logic to `api/routes.py`** — routes call pipeline/store, that's all
- **Don't put prompt strings in `services/`** — all AI instructions belong in `prompts/`
- **Don't access the job store directly** — always use `store.get()` / `store.update()`
- **Don't call `store.update()` from `services/`** — services are pure functions; only `pipeline.py` writes to the store
- **Don't add domain models to `api/schemas.py`** — HTTP schemas only; domain objects go in `domain/models.py`
- **Don't use "overlay" as a synonym for "checkpoint"** — checkpoint is the domain object; overlay is its rendered form
- **Don't invent specifics the transcript doesn't support** — keep checkpoints general rather than hallucinating names or facts
- **Don't duplicate prompt content** across files — one source of truth per concern in `prompts/`

---

## Common debugging

**"No questions generated in Clarify step"**
→ `services/clarify_service.py` — `_pad_with_standard()` always produces ≥ 3 questions; if it's returning 0, the LLM call itself is failing and the exception path goes to `_fallback_questions()`.

**"Checkpoints are generic / meta-commentary"**
→ `prompts/checkpoints.py` — `_QUALITY_MANDATES` has the banned labels list.
→ Ensure `clarification_context` is non-empty and being passed from `ProcessConfig` through to `generate_checkpoints()`.

**"Wrong audience in learning content"**
→ Confirm `config.audience.value` is passed to `generate_learning_script()` in both `api/pipeline.py` (`run_analysis`) and the `/regenerate-learning` route.

**"AI quality review undoes correct content"**
→ `review_checkpoints()` in `services/review_service.py` must receive `clarification_context` — check the call site in `api/pipeline.py`.

**"SSE stream never closes"**
→ Every code path in `run_clarify`, `run_analysis`, `run_export` — including exception handlers — must put `None` on the correct queue: `asyncio.run_coroutine_threadsafe(job["queue_analysis"].put(None), job["loop"])`.
