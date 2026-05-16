# Feature Documentation — MoSCoW Prioritisation

MoSCoW: **M**ust Have · **S**hould Have · **C**ould Have · **W**on't Have (now)

---

## Must Have — MVP (ship these or the product doesn't exist)

These are the features without which we cannot charge money or deliver the core value proposition.

### Infrastructure

| Feature | Why it's Must Have |
|---|---|
| **User accounts + auth** | Cannot bill without identity |
| **Persistent job storage (database)** | Jobs lost on server restart = unusable product |
| **Cloud deployment (not localhost)** | Product is inaccessible otherwise |
| **File storage (S3 or equivalent)** | Videos must persist beyond the session |
| **Stripe billing** | Cannot take payment without it |
| **Free tier enforcement** (1 video/month, watermarked) | Acquisition funnel entry point |
| **Pro subscription** ($69/month, 3 videos) | Primary monetisation |
| **Per-video payment** ($29) | Primary monetisation for irregular users |
| **Shareable URL** for overlaid video | The #1 conversion trigger; without it output is a file on a hard drive |
| **Video library** (past jobs, re-downloadable) | Retention; creators need to retrieve past work |

### Core Pipeline (already built, needs hardening)

| Feature | Why it's Must Have |
|---|---|
| **AI overlay generation** | The core differentiator |
| **Overlay burn-in to video** | The main deliverable |
| **Transcription** (Whisper) | Foundation for everything else |
| **Checkpoint generation** (Claude) | Powers overlays, chapters, repurposing |
| **Noise removal** (Dolby.io API) | Most raw recordings need this; affects perceived quality |

### Export Outputs

| Feature | Why it's Must Have |
|---|---|
| **YouTube chapters export** (.txt, paste-ready) | Top acquisition driver; every YouTuber needs this |
| **Captions export** (.srt) | Accessibility and reach requirement for all platforms |
| **Social media reels** (3–5 clips, vertical, captioned) | Core output for distribution; major time save |
| **Trailer** (60–90 second highlight reel) | High perceived value; used on channel pages and course sales pages |

### Content Repurposing (quick wins — 1 LLM call each)

| Feature | Why it's Must Have |
|---|---|
| **Title suggestions** (5 options) | Every YouTuber needs this; takes seconds to generate |
| **YouTube description** (SEO, with timestamps) | Saves 30–45 min per video; data already available from transcript |
| **Tags / keywords** | Saves 15 min; trivial to generate |
| **Twitter/X thread** | Repurposing is a core creator need; data already available |
| **LinkedIn post** | Same source data, different format |
| **Instagram captions** (per reel) | Generated alongside each reel |
| **Clean formatted transcript** | Zero extra AI cost; reformats existing transcript |
| **ZIP download** (all outputs in one package) | Closes the loop; the final deliverable |

---

## Should Have — Phase 2 (important, high value, build within 3 months of launch)

These features significantly increase value and retention but are not blockers for first payment.

### Translation Layer

| Feature | Notes |
|---|---|
| **Multi-language overlay translation** | Translate overlay text → re-render into video. Major differentiator vs. human+AI. |
| **Caption translation** (.srt per language) | DeepL or Claude; fast and cheap |
| **Chapter + description translation** | Same pipeline as captions |
| **Language picker UI** | Select 1–3 target languages at export |

### Dubbing

| Feature | Notes |
|---|---|
| **Audio dubbing** (ElevenLabs, original voice preserved) | Premium add-on ($20/language); biggest differentiator vs. any competitor |
| **Dubbed video export** (one file per language) | Replaces the audio track; same overlays |

### Enhancement

| Feature | Notes |
|---|---|
| **Colour filter presets** (4–5 LUT options) | FFmpeg-based; quick to build. "Cinematic", "warm", "vibrant", "muted", "travel" |
| **Thumbnail frame suggestion** | Identify the best frame from existing frame extraction; surface in UI |

### Platform

| Feature | Notes |
|---|---|
| **Custom branding** (logo + accent colour on player + overlays) | Upsell; makes creators proud to share |
| **Creator subscription** ($129/month, 8 videos) | Volume tier for active creators |
| **Basic analytics** (views, completion rate per video) | Retention driver; creators want to know if it's working |

### Educator-specific

| Feature | Notes |
|---|---|
| **Learning objectives** ("by the end of this video you will be able to…") | One extra LLM call; high value for course creators |
| **Key terms / glossary** | Extract technical terms and define them; valuable for courses |
| **Formatted lesson notes** | Structured document derived from transcript + checkpoints |

---

## Could Have — Phase 3 (valuable, but can wait until Phase 2 is proven)

These features are coherent with the product direction but are not urgent for the first 6 months.

### Advanced Analytics

| Feature | Notes |
|---|---|
| Concept retention breakdown (quiz scores per topic) | Requires viewer quiz data; needs viewer accounts first |
| Drop-off map (where viewers stopped) | Requires video player telemetry |
| A/B overlay testing | Test two versions of an annotation; needs analytics infrastructure |

### Advanced Enhancement

| Feature | Notes |
|---|---|
| Blur / censor faces and sensitive regions | High value for corporate and news content; heavy ML engineering (object tracking) |
| Smooth transitions between cuts | Complex; requires understanding edit structure |
| Hook scoring ("your first 30 seconds is weak") | Interesting for YouTubers; needs benchmarking data to be credible |

### Creator-specific

| Feature | Notes |
|---|---|
| Location overlays for travel content | NLP entity extraction + geocoding; good for travel vloggers |
| Music mood suggestion (royalty-free) | Text suggestion only (no licensing complexity); one LLM call |
| Worksheet / printable study guide | PDF export; good for educators; needs design work |
| Posting schedule suggestion | Based on content type and platform best practices |

### Platform

| Feature | Notes |
|---|---|
| Batch processing (10+ videos overnight) | High value for course creators doing a full launch |
| Completion webhook / notifications | Email when processing is done |
| Spaced repetition email follow-up | Email viewers quiz questions 3 days after watching |
| Knowledge gap summary for viewers | Post-watch screen showing concept gaps with re-watch clips |

---

## Won't Have — Explicitly Out of Scope

These are good ideas that would take the product in the wrong direction right now.

| Feature | Why not |
|---|---|
| **Full video editing** (cut decisions, B-roll, music sync) | Requires creative judgment humans + AI still do better; different product |
| **AI thumbnail generation** (generative images with text) | Requires image generation pipeline (DALL-E, Stable Diffusion); separate product |
| **Thumbnail design tool** | Full design tooling (Canva territory); out of scope |
| **Social media scheduling / posting** | Generates content; doesn't post it. Integration risk with platform TOS. |
| **Course hosting / LMS** | Not a platform; we produce assets for existing platforms |
| **Live streaming support** | Different use case entirely |
| **Mobile app** | Web-first; mobile later if usage data supports it |
| **SCORM / xAPI export** | Enterprise-only need; post-Series A |
| **Team collaboration** (multi-seat, shared library) | Post-product-market-fit |
| **API access** | Enterprise; when there's demand |
| **White-label** | Enterprise; when there's demand |
| **Original video long-term hosting** | Not a CDN; delete processed jobs after 30 days |
| **Music licensing** | Legal and rights complexity; out of scope |

---

## Feature → Customer Matrix

Which features matter most to which customer:

| Feature | Course Creator | YouTuber | Travel Vlogger | Freelance Editor |
|---|---|---|---|---|
| Overlaid video | ★★★ | ★★★ | ★★ | ★★★ |
| Chapters | ★★ | ★★★ | ★ | ★★★ |
| Captions | ★★★ | ★★★ | ★★ | ★★★ |
| Reels | ★★ | ★★★ | ★★★ | ★★★ |
| Trailer | ★★★ | ★★ | ★★ | ★★ |
| Noise removal | ★★★ | ★★★ | ★★★ | ★★★ |
| Colour presets | ★ | ★★ | ★★★ | ★★ |
| Title suggestions | ★★ | ★★★ | ★★ | ★★★ |
| Description + tags | ★★ | ★★★ | ★★ | ★★★ |
| Twitter thread | ★ | ★★★ | ★★ | ★★ |
| LinkedIn post | ★★★ | ★★ | ★ | ★★ |
| Instagram captions | ★★ | ★★ | ★★★ | ★★★ |
| Translation | ★★★ | ★★★ | ★★ | ★★★ |
| Dubbing | ★★★ | ★★★ | ★ | ★★★ |
| Learning objectives | ★★★ | ★★ | ✗ | ★ |
| Glossary / key terms | ★★★ | ★★ | ✗ | ★ |
| Location overlays | ✗ | ★ | ★★★ | ★ |
| ZIP download | ★★★ | ★★★ | ★★★ | ★★★ |

★★★ = core need · ★★ = strong nice-to-have · ★ = marginal · ✗ = not relevant
