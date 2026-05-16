# Technical Roadmap

## Current State

The core AI pipeline is built and working end-to-end:
- Transcription → checkpoint generation → overlay rendering → export
- SSE streaming for real-time progress
- Clarify step (pre-analysis with questions)
- Review step (user edits checkpoints)
- In-memory job store (lost on restart)
- Runs on localhost only
- No auth, no billing, no persistence

**What exists is the hard part. What's missing is the business layer around it.**

---

## Architecture Overview (Target)

```
Frontend (React + Vite)
  └── deployed on Vercel / Netlify
  └── API_URL from environment variable

Backend (FastAPI)
  ├── api/          HTTP handlers, SSE, auth, billing
  ├── domain/       Pydantic models, enums
  ├── services/     Pure functions: LLM orchestration
  ├── infrastructure/ FFmpeg, Whisper, S3, external APIs
  └── prompts/      All LLM prompt strings

Storage
  ├── PostgreSQL     Job metadata, user accounts, billing state
  ├── S3 (or R2)    Video files, rendered outputs, ZIPs
  └── Redis (later) Queue for batch processing

External APIs
  ├── Anthropic      Checkpoint generation, repurposing, chapters
  ├── Whisper        Transcription (OpenAI API or local)
  ├── Dolby.io       Noise removal
  ├── ElevenLabs     Dubbing
  ├── DeepL          Translation (captions, chapters)
  └── Stripe         Billing
```

---

## Phase 1 — MVP (Weeks 1–8)

**Goal:** A deployed product a stranger can pay for and use.

### 1.1 Infrastructure — Database + Storage

**Replace in-memory JobStore with persistent storage.**

New files:
- `backend/infrastructure/database.py` — SQLAlchemy setup, session factory
- `backend/infrastructure/storage.py` — abstraction over S3/local (upload, download, presigned URL)
- `backend/domain/models.py` — add `User`, `Job` SQLAlchemy models alongside Pydantic models

Modify:
- `backend/api/job_store.py` — rewrite to read/write from DB; keep same interface so pipeline.py is unaffected
- `backend/api/config.py` — add `DATABASE_URL`, `S3_BUCKET`, `STORAGE_BACKEND` env vars

File retention policy: delete raw uploads after 7 days, keep outputs for 30 days.

---

### 1.2 Auth

New files:
- `backend/api/auth.py` — JWT-based auth (FastAPI-Users or custom); email + password
- `frontend/src/components/AuthGate.tsx` — login / signup pages
- `frontend/src/components/Dashboard.tsx` — authenticated landing page

Modify:
- `backend/api/routes.py` — add `current_user` dependency to all job routes
- `frontend/src/App.tsx` — add React Router; protected routes behind auth

Keep it simple: email + password, JWT in httpOnly cookie. No OAuth for MVP.

---

### 1.3 Billing — Stripe

New files:
- `backend/api/billing.py` — Stripe webhook handler; `/billing/portal`, `/billing/checkout`
- `backend/services/billing_service.py` — `get_user_tier()`, `check_quota()`, `record_usage()`
- `frontend/src/components/Upgrade.tsx` — upgrade prompt; pricing page

Modify:
- `backend/api/routes.py` — gate `/upload` behind quota check
- `backend/domain/models.py` — add `tier: Tier` and `videos_this_month: int` to User

Tiers: `free` (1 video/month), `pro` (3 videos/month), `creator` (8 videos/month), `pay_per_video`.

Stripe products: Pro subscription ($69/month), Creator subscription ($129/month), one-time video credit ($29).

---

### 1.4 Deployment + Shareable URL

Modify:
- `frontend/src/components/*.tsx` — replace all `http://localhost:8000` with `import.meta.env.VITE_API_URL`
- `backend/api/config.py` — add `BASE_URL` env var; used in shareable link generation
- `backend/api/routes.py` — `/player/{job_id}` already exists; ensure it works from deployed BASE_URL

Deploy targets:
- Backend: Railway or Fly.io (handles long-running video processing)
- Frontend: Vercel
- DB: Railway Postgres or Supabase
- Storage: Cloudflare R2 (cheaper than S3, S3-compatible)

---

### 1.5 Export Outputs — Chapters, Captions, Reels, Trailer

**Chapters and captions** (already generated, just need download endpoints):

New routes in `backend/api/routes.py`:
- `GET /chapters/{job_id}` → plain text file download
- `GET /captions/{job_id}` → .srt file download
- `GET /captions/{job_id}/{language}` → translated .srt (Phase 2)

**Reels extraction:**

New files:
- `backend/services/reels_service.py` — selects best clip moments from checkpoints
- `backend/infrastructure/reels.py` — FFmpeg: trim clip, crop to 9:16, burn captions
- `backend/prompts/reels.py` — prompt to select 3–5 best moments for social

Modify:
- `backend/api/pipeline.py` — add `run_reels()` step after overlay export
- `backend/api/job_store.py` — add `reels: list[Path]` to job dict
- `backend/api/routes.py` — `GET /reels/{job_id}` → ZIP of reel clips

**Trailer:**

New files:
- `backend/services/trailer_service.py` — selects best moments (highest confidence checkpoints)
- `backend/infrastructure/trailer.py` — FFmpeg: concat clips with crossfade, add title card

Modify:
- `backend/api/pipeline.py` — add `run_trailer()` step
- `backend/api/routes.py` — `GET /trailer/{job_id}` → MP4 download

---

### 1.6 Noise Removal

New files:
- `backend/infrastructure/noise_removal.py` — Dolby.io Media Enhance API wrapper

Modify:
- `backend/api/pipeline.py` — add noise removal as first step in `run_analysis()`, before transcription
- `backend/api/schemas.py` — add `enhance_audio: bool = True` to request

---

### 1.7 Content Repurposing

New files:
- `backend/services/repurpose_service.py` — `generate_content_pack(transcript, video_info, checkpoints, chapters) → ContentPack`
- `backend/prompts/repurpose.py` — prompts for title, description, tags, thread, LinkedIn, Instagram captions

New domain model in `backend/domain/models.py`:
```python
class ContentPack(BaseModel):
    titles: list[str]           # 5 title options
    description: str            # full YouTube description
    tags: list[str]             # 20 tags
    twitter_thread: str         # formatted thread
    linkedin_post: str          # LinkedIn-ready post
    instagram_captions: list[str]  # one per reel
    transcript: str             # clean formatted transcript
```

Modify:
- `backend/api/pipeline.py` — add repurpose step after reels
- `backend/api/routes.py` — `GET /content-pack/{job_id}` → ContentPack JSON
- `backend/api/job_store.py` — add `content_pack: ContentPack | None`

Frontend:
- New `frontend/src/components/StepExport.tsx` section: "Content Pack" tab showing all text outputs with copy buttons

---

### 1.8 ZIP Download

New files:
- `backend/infrastructure/packager.py` — assembles all outputs into a structured ZIP

```
{job_id}_package.zip
  ├── video_with_overlays.mp4
  ├── reels/
  │   ├── reel_1.mp4 ... reel_5.mp4
  ├── trailer.mp4
  ├── chapters.txt
  ├── captions.srt
  ├── description.txt
  ├── tags.txt
  ├── twitter_thread.txt
  ├── linkedin_post.txt
  ├── instagram_captions/
  │   ├── reel_1.txt ... reel_5.txt
  └── transcript.txt
```

New route:
- `GET /download-all/{job_id}` → ZIP file

---

### 1.9 Video Library (Dashboard)

New files:
- `frontend/src/components/VideoLibrary.tsx` — grid of past jobs, thumbnail, title, date, download links

Modify:
- `backend/api/routes.py` — `GET /jobs` → paginated list of user's jobs
- `backend/api/schemas.py` — `JobSummary` response model

---

### 1.10 Colour Filter Presets

New files:
- `backend/infrastructure/filters.py` — apply FFmpeg LUT or filter chain
- `assets/luts/` — 5 LUT files: cinematic, warm, cool, vibrant, travel

Presets: `none` (default), `cinematic` (desaturated + contrast), `warm` (golden hour), `cool` (blue shift), `travel` (vibrant + lifted shadows).

Modify:
- `backend/domain/models.py` — add `ColorPreset` enum to `ProcessConfig`
- `backend/api/pipeline.py` — apply filter after noise removal, before overlay rendering
- `frontend/src/components/StepConfigure.tsx` — add colour preset picker

---

## Phase 2 — Growth (Weeks 9–16)

**Goal:** Translation, dubbing, custom branding, analytics.

### 2.1 Translation Pipeline

New files:
- `backend/services/translation_service.py` — translate text blocks via DeepL or Claude
- `backend/infrastructure/overlay_translate.py` — translate overlay text → re-render overlay images
- `backend/infrastructure/caption_translate.py` — translate .srt file preserving timing

Modify:
- `backend/api/pipeline.py` — add translation step post-export if languages selected
- `backend/domain/models.py` — add `target_languages: list[str]` to `ProcessConfig`
- `backend/api/schemas.py` — `ExportRequest` includes language list
- `backend/infrastructure/packager.py` — add per-language subdirectory to ZIP

Frontend:
- `frontend/src/components/StepConfigure.tsx` — language selector (multi-select, flags)

---

### 2.2 Audio Dubbing

New files:
- `backend/infrastructure/dubbing.py` — ElevenLabs dubbing API; takes video + target language; returns dubbed audio
- `backend/services/dubbing_service.py` — orchestrate: extract audio → send to ElevenLabs → replace audio track via FFmpeg

Modify:
- `backend/api/pipeline.py` — optional dubbing step, runs per language selected
- `backend/api/job_store.py` — `dubbed_videos: dict[str, Path]` (language → video path)
- `backend/api/routes.py` — `GET /download/{job_id}/{language}` → dubbed MP4

---

### 2.3 Custom Branding

New files:
- `backend/services/branding_service.py` — apply logo + colour to overlays and player
- `backend/domain/models.py` — `BrandingConfig(logo_url, accent_colour, font)`

Modify:
- `backend/infrastructure/overlay.py` — accept `BrandingConfig`; composite logo onto overlay cards
- `backend/infrastructure/player.py` — inject brand colours into player HTML
- `backend/api/routes.py` — `POST /branding/{job_id}` or stored at user account level
- `frontend/src/components/Settings.tsx` — logo upload, colour picker

---

### 2.4 Basic Analytics

New files:
- `backend/api/analytics.py` — event ingestion endpoint; simple counters
- `backend/infrastructure/database.py` — `VideoView`, `QuizEvent` tables

New routes:
- `POST /analytics/view/{job_id}` — called by player on load
- `POST /analytics/complete/{job_id}` — called by player on video end
- `GET /analytics/{job_id}` → view count, completion rate

Frontend:
- `frontend/src/components/Analytics.tsx` — per-video stats card in library view

---

### 2.5 Thumbnail Frame Suggestion

Modify:
- `backend/services/checkpoint_service.py` — tag one checkpoint as `thumbnail_candidate: True` (highest visual impact + information density)
- `backend/api/routes.py` — `GET /thumbnail-frame/{job_id}` → JPEG of suggested frame
- `frontend/src/components/StepExport.tsx` — "Suggested thumbnail" section with download button

---

## Phase 3 — Scale (Weeks 17–24)

**Goal:** Advanced features, enterprise readiness, volume processing.

### 3.1 Blur / Censor

New files:
- `backend/infrastructure/censor.py` — face detection (OpenCV or AWS Rekognition) + region tracking + FFmpeg blur filter

Heavy engineering: face detection per frame, bounding box tracking across the clip, FFmpeg drawbox/boxblur filter applied. Expect 3–4 weeks solo.

---

### 3.2 Hook Scoring

New files:
- `backend/services/hook_service.py` — send first 30-second transcript + frames to Claude; score engagement and suggest improvements
- `backend/prompts/hook.py` — scoring rubric prompt

New route: `GET /hook-score/{job_id}` → score (0–100) + specific suggestions

---

### 3.3 Location Overlays (Travel)

Modify:
- `backend/services/checkpoint_service.py` — tag checkpoints that mention place names (`location_name: str | None`)
- `backend/infrastructure/geocoding.py` — resolve place names to coordinates (Nominatim / Google Maps)
- `backend/infrastructure/overlay.py` — special location overlay template with pin icon + name

---

### 3.4 Batch Processing

New files:
- `backend/api/batch.py` — `POST /batch` accepts list of video URLs or upload IDs; queues all jobs
- `backend/infrastructure/queue.py` — Redis + RQ or Celery for async job queue

Modify:
- `backend/api/pipeline.py` — extract `run_analysis()` to be queue-compatible (no thread.start() directly)

This is a significant architecture change — background jobs move from threads to a proper queue. Worth doing when batch processing becomes a real customer need.

---

### 3.5 Advanced Analytics + A/B Testing

New files:
- `backend/services/ab_service.py` — store two overlay versions per checkpoint; route viewers randomly
- `backend/infrastructure/database.py` — `ABTest`, `ABResult` tables

---

## Dependency Map

```
Phase 1 (must ship together)
  Database + Storage
      └── Auth
          └── Billing
              └── Deployment (shareable URL)

  Noise Removal
      └── Overlay pipeline (already built)
          ├── Reels + Trailer
          └── Content Repurposing
              └── ZIP Download

  Colour Presets (independent, any time)

Phase 2 (each independent after Phase 1)
  Translation
      └── Dubbing (depends on translation pipeline)
  Custom Branding (independent)
  Analytics (independent)
  Thumbnail suggestion (independent)

Phase 3 (all depend on Phase 2 analytics)
  Blur/Censor (independent)
  Hook Scoring (independent)
  Location Overlays (depends on checkpoint model change)
  Batch Processing (architecture change — do last)
```

---

## Environment Variables

```env
# API
BASE_URL=https://api.yourdomain.com
FRONTEND_URL=https://yourdomain.com

# Database
DATABASE_URL=postgresql://...

# Storage
STORAGE_BACKEND=s3          # or "local" for dev
S3_BUCKET=your-bucket
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Auth
JWT_SECRET=...
JWT_EXPIRY_DAYS=30

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRO_PRICE_ID=price_...
STRIPE_CREATOR_PRICE_ID=price_...
STRIPE_VIDEO_PRICE_ID=price_...

# AI / Media APIs (already in settings.py)
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...           # Whisper
DOLBY_API_KEY=...            # Noise removal
ELEVENLABS_API_KEY=...       # Dubbing
DEEPL_API_KEY=...            # Translation
```

---

## Milestones

| Milestone | Target | Definition of done |
|---|---|---|
| **MVP shipped** | Week 8 | Stranger can sign up, pay, upload a video, download ZIP |
| **First 5 paying customers** | Week 10 | 5 people pay $29 without being asked twice |
| **Translation live** | Week 14 | Creator can download translated captions + overlays in 2 languages |
| **Dubbing live** | Week 16 | Audio dubbed in original voice, exported as separate MP4 |
| **First $5k MRR** | Month 5 | ~70 paying customers on Pro or pay-per-video |
| **First $10k MRR** | Month 8 | ~140 paying customers |
| **Batch processing** | Month 9 | Course creator can submit 12 videos and get them overnight |
