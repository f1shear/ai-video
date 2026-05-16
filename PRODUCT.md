# Product Strategy

## Vision

Turn any educational video into a complete learning experience — automatically.

---

## The Problem

Video is the dominant format for teaching online. But most educational videos are 30% as effective as they could be:

- Viewers watch passively and retain ~30% after 24 hours (Ebbinghaus forgetting curve)
- No feedback loop — the creator never knows which concepts landed
- No way for the viewer to identify or fix their own gaps
- The "educational layer" — chapters, annotations, quizzes, summaries — is entirely manual and usually skipped

The tools creators use today don't solve this. They either automate the wrong thing or require skills most creators don't have.

---

## Market Landscape

### Who creators use today

| Approach | Cost | What it does | What it doesn't do |
|---|---|---|---|
| **Freelance editor** | $500–2000/video, 3–7 days | Everything creative | Chapters, quiz, annotations, learning content — still manual |
| **Premiere / Final Cut** | $0–55/mo | Full control | Requires skill; blank canvas; no content understanding |
| **CapCut / Filmora** | Free–$50/mo | Templates, effects, easy | Aesthetic only; no educational intelligence |
| **Descript** | $12–24/mo | Transcript-based editing, silence removal | No content understanding; still mechanic |
| **Opus Clip / Vidyo** | $15–50/mo | Repurpose long video to shorts | No understanding of what the content means |
| **Rev / Kapwing** | $1.50/min or manual | Captions, transcripts | That's all |
| **Manual (most common)** | Time | Total control | Takes 4–8 hours per 10-minute video |

### The gap no one owns

Existing tools automate **mechanics** — removing silences, adding captions, generating clips. None of them understand *what a video is teaching* and produce the educational layer from that understanding.

That gap is the product.

---

## Target Customers

### Primary: The Solo Educator

A person teaching something on YouTube or through a course platform. No editing budget. Values their time. Measures success by whether students understand.

- Output: 2–4 videos/month
- Current workflow: edits in CapCut or iMovie, manually writes chapters and show notes, skips quiz and annotations
- Pain: the educational layer takes as long as filming
- Willingness to pay: $20–80/month
- Example: a developer teaching React, a teacher making history content, a nutritionist running a course

### Secondary: The Course Creator

Selling structured courses on Teachable, Kajabi, or Thinkific. Has some budget. Needs professional output. LMS compatibility matters.

- Output: 1–2 courses/quarter (5–20 videos each)
- Current workflow: may hire an editor for cutting, still manually creates all learning content
- Pain: the editor does aesthetics, the creator still does everything educational
- Willingness to pay: $80–200/month or per-course pricing
- Example: a coach selling a $500 course, a consultant running corporate training

### Tertiary: The Educational YouTuber

Finance, tech, science, history channels competing on information quality. Has an audience. Wants to stand out and improve retention metrics.

- Output: 2–4 videos/month, larger productions
- Current workflow: editor on retainer or Descript for mechanics, chapters written manually
- Pain: looks polished but leaves learning effectiveness on the table
- Willingness to pay: $50–100/month
- Example: a 100k-subscriber finance channel, a coding tutorial creator

### Enterprise: L&D Professional

Learning and Development at a mid-to-large company. Compliance, onboarding, product training. Needs SCORM, analytics, accessibility, multi-language.

- Output: 10–50 videos/quarter
- Current workflow: internal production team or agency, dedicated LMS
- Pain: production is expensive; tracking whether employees actually learned anything is hard
- Willingness to pay: $500–5000/month depending on seat count

---

## Core Insight

**The creator is not the customer. The viewer is.**

Every tool in this market serves the person making the video. This product serves the person watching it — and gives the creator data proving it worked.

The creator pays. The viewer learns. The creator sees the results. The creator keeps paying.

This is a fundamentally different value proposition than any editing tool.

---

## The Two Flywheels

### Acquisition flywheel

```
Free YouTube chapters tool
  → creator signs up (no friction, immediate value)
  → upgrades for full pipeline
  → shares interactive player URL with their audience
  → viewers watch the enhanced video
  → "Powered by [product]" — viewers become creators
  → they search for chapters tool
  → cycle repeats
```

### Retention flywheel

```
Creator processes a video
  → analytics show concept retention breakdown
  → creator sees which explanations didn't land
  → improves the explanation and re-processes
  → viewer quiz scores go up
  → creator sees the improvement
  → creator trusts the product
  → creator processes every video
```

---

## Feature Set

### Tier 1 — Acquisition (free, viral, no friction)

These exist to bring creators in. No signup required for the core action; signup required to save or share results.

| Feature | What it does | Why it acquires customers |
|---|---|---|
| **YouTube chapters generator** | Upload video → AI generates timestamps + titles → paste-ready text | High search volume. Every YouTuber needs this. Takes 2 minutes instead of 30. |
| **Free transcript + timestamps** | Full transcript with word-level timestamps | Commodity with high search intent. Gets creators into the product. |
| **Learning score** | AI rates how educational a video is, explains why, suggests improvements | Shareable, opinionated, creates conversation. "My video scored 71/100." |
| **Interactive player (watermarked)** | Full player with overlays + quiz, free with branding | Creator shares URL to audience. Every viewer sees the product. |
| **Quiz score share card** | Viewer completes quiz, gets a shareable result card | "I scored 9/10 on [Creator]'s Docker video." Creator's audience sees it and wants it. |
| **Free tier: 1 video/month** | Full pipeline once per month, watermarked | Standard freemium. Removes first-use friction. Upgrade wall hits on second video. |

### Tier 2 — Core Paid (replaces the educational layer of an editor)

What creators pay for. The pitch: cheaper than a freelancer, faster than doing it yourself, more effective than either.

| Feature | What it does | Who pays |
|---|---|---|
| **Full AI pipeline** | Transcript → checkpoints → overlays → learning content → interactive player | Everyone |
| **Shareable player URL** | Permanent URL for the interactive learning player, no watermark | Everyone — without this, output is a downloaded file |
| **YouTube chapters export** | One-click formatted timestamps for YouTube description | YouTubers |
| **SRT/VTT captions export** | Styled subtitle file for any platform | All creators |
| **Pre-questions (think-first)** | Question appears before a key concept is explained, not after | Educators — proven to improve retention |
| **Anki/flashcard export** | Key facts from the video as a flashcard deck | Educators, course creators |
| **Multiple style modes** | Minimal, detailed, tutorial, documentary — changes overlay density and format | All paid users |
| **Custom branding** | Logo, colors, font — player and overlays match the creator's brand | Course creators, educators |
| **Model + reasoning control** | Choose Haiku (fast/cheap), Sonnet (balanced), Opus (deep) | Power users who want cost or quality control |

### Tier 3 — Analytics (retention and upsell)

The data layer that creates ongoing value and makes the product irreplaceable.

| Feature | What it does | Value |
|---|---|---|
| **Concept retention breakdown** | Which concepts had high/low quiz scores across all viewers | Creator knows exactly which explanations need reworking |
| **Drop-off map** | Where viewers stopped watching, overlaid on timeline | Identifies the moment confusion or boredom hits |
| **Quiz performance by concept** | Not just overall score — per-concept accuracy | Pinpoints weak explanations |
| **Completion rate by segment** | Which sections hold attention | Informs future content structure |
| **A/B overlay testing** | Run two versions of an annotation, see which gets better quiz scores | Optimization for educators who care about effectiveness |
| **Video library + history** | All processed videos in one place, with analytics over time | Retention — the product becomes their content intelligence hub |

### Tier 4 — Learning Loop (premium, viewer-facing)

Transforms the product from a video tool into a learning platform.

| Feature | What it does | Value |
|---|---|---|
| **Knowledge gap summary** | Post-watch screen: concepts you got right/wrong, with re-watch clips for misses | Viewer knows exactly what to revisit — 90 second clip not 20 minute video |
| **Spaced repetition follow-up** | Email viewer 5 questions 3 days after watching, weighted to weak areas | Retention jumps from ~30% to ~75%. Product extends beyond the video. |
| **Viewer confidence rating** | On each quiz answer, viewer rates confidence (Sure / Think so / Guessing) | Metacognition — reveals shaky knowledge even when the answer was correct |
| **Concept dependency graph** | Visual map of how concepts in the video build on each other | Creator sees if prerequisite knowledge is missing; viewer navigates non-linearly |
| **Viewer progress tracking** | Viewer account — tracks completion and quiz scores across multiple videos | Unlocks course-like experiences for creators without an LMS |

### Tier 5 — Enterprise

The compliance, integration, and scale tier.

| Feature | What it does |
|---|---|
| **SCORM / xAPI export** | LMS-compatible package — works with Moodle, Canvas, Cornerstone |
| **LMS integrations** | Direct publish to Teachable, Kajabi, Thinkific |
| **API access** | Embed the pipeline into the creator's own product or workflow |
| **White-label player** | Their domain, their brand — no product mention |
| **Team accounts + roles** | Multiple editors, admin controls, shared video library |
| **SSO** | SAML/OAuth for corporate IT requirements |
| **Multi-language overlays** | Translate overlays and captions into target language — not just subtitles |
| **Dedicated analytics dashboard** | Per-department, per-course, per-learner reporting |
| **Bulk upload + batch processing** | Process 50 videos overnight |

---

## Customer Journey (Refined)

### Creator journey

```
Discovery
  YouTube search: "youtube chapters generator"
  → Lands on free tool, no signup
  → Uploads video, gets chapters in 90 seconds
  → Signs up to save

Activation
  Processes first full video on free tier
  → Sees interactive player, quiz, learning content
  → Shares player URL with their audience
  → Viewers complete quiz

Conversion
  Tries to process second video
  → Hits free tier limit
  → Sees upgrade page with analytics preview
  → Upgrades (sees clear ROI vs. hiring an editor)

Retention
  Checks analytics after 1 week
  → Concept retention breakdown shows "Docker networking" at 41%
  → Re-records that section, reprocesses video
  → Score improves to 78%
  → Creator is now invested in the feedback loop

Expansion
  Wants to remove watermark and add logo → Custom branding
  Starts a course with 10 videos → Batch processing
  Company asks for SCORM → Enterprise conversation
```

### Viewer journey

```
Discovery
  Clicks shared player URL from creator
  → Watches video with overlays
  → Quiz pauses the video at key moment

Engagement
  Answers quiz questions with confidence ratings
  → Pre-question before key concept ("what do you think happens when...")
  → Active engagement instead of passive watching

Post-watch
  Knowledge gap summary screen
  → Sees they got 7/10 — "Docker networking" was shaky
  → Clicks re-watch clip → 90 seconds, not 20 minutes

Retention
  Day 3 email: 5 spaced repetition questions
  → Answers from memory, gets feedback
  → Concept solidified

Conversion (viewer → creator)
  "Powered by [product]" on player
  → Viewer is also a creator
  → Searches "youtube chapters generator"
  → Acquisition flywheel completes
```

---

## Business Model

| Tier | Price | Limits | Key features |
|---|---|---|---|
| **Free** | $0 | 1 video/month, watermark | Chapters export, full pipeline, shareable player (watermarked) |
| **Pro** | $29/month | 8 videos/month | No watermark, custom branding, all export formats, shareable URL |
| **Creator** | $79/month | Unlimited videos | Analytics, A/B testing, spaced repetition, knowledge gap summary |
| **Teams** | $199/month | 5 seats, unlimited videos | White-label, collaboration, priority support |
| **Enterprise** | Custom | Custom | SCORM, API, SSO, LMS integrations, multi-language, dedicated CSM |

**Per-video pricing** as an alternative to subscriptions: $8/video for Pro features, $18/video for Creator features. Targets creators with irregular output who won't commit to a monthly plan.

---

## Competitive Positioning

```
                    High educational intelligence
                              │
                              │
           THIS PRODUCT       │
                              │
                              │
Low creator          ─────────┼─────────  High creator
effort required               │           effort required
                              │
         CapCut / iMovie      │    Premiere / Final Cut
                              │
                              │    Descript
                              │
                    Low educational intelligence
```

The product owns a quadrant no one else is in: high educational intelligence, low creator effort.

**One-line against each competitor:**

- vs. freelance editor: *"Same educational output, 95% cheaper, delivered in 15 minutes."*
- vs. Descript: *"Descript removes silences. This adds meaning."*
- vs. CapCut: *"CapCut makes it look good. This makes it teach."*
- vs. doing it manually: *"You're already spending 3 hours on the educational layer. This takes 15 minutes."*

---

## Build Roadmap

### Now — Foundation
- Shareable player URL (permanent, no localhost)
- YouTube chapters export (free, no-signup tool)
- Free tier enforcement
- Basic viewer analytics (completion rate, quiz score)

### Next — Retention
- Creator analytics dashboard (concept retention, drop-off map)
- Knowledge gap summary screen for viewers
- Custom branding (logo, colors)
- Spaced repetition email follow-up

### Then — Expansion
- A/B overlay testing
- Multi-language overlays
- Batch processing
- LMS integrations (Teachable, Kajabi)
- Anki/flashcard export

### Enterprise
- SCORM/xAPI export
- API access
- White-label player
- Team accounts + SSO
- Dedicated analytics

---

## What Makes This Defensible

1. **The feedback loop is the moat.** Once creators have 6 months of concept retention data, they won't leave — it's their content intelligence history.

2. **The viewer experience is the distribution.** Every shared player is a product ad. No paid acquisition needed at scale.

3. **The educational layer is genuinely hard to copy.** Generating chapters is a feature. Understanding what a video teaches and producing a complete learning experience from that understanding is a product.

4. **Network effects at the content level.** As more videos are processed, the product gets better signal on what effective educational content looks like — feeding back into prompt quality and benchmark scores.
