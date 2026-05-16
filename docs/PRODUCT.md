# Product Documentation

## What This Product Does

Takes a raw video. Returns everything a creator needs to publish it — overlaid video, social reels, trailer, chapters, captions, and all repurposed content — in any language, in 15 minutes.

The creator films. The product handles everything after.

---

## Core Pipeline

```
Upload raw video
    │
    ▼
Enhance
  ├── Background noise removal
  └── Colour filter / grade preset

    │
    ▼
Understand
  ├── Transcribe audio → transcript
  ├── Analyse frames → visual understanding
  ├── Generate video_info (what this video teaches)
  └── Optional: clarifying questions → user confirms intent

    │
    ▼
Annotate
  ├── Generate checkpoints (timed annotations)
  ├── Burn overlays onto video
  ├── Generate YouTube chapters
  └── Generate captions (SRT)

    │
    ▼
Distribute
  ├── Extract 3–5 social media reels (10–30 seconds, vertical)
  └── Generate trailer (60–90 seconds)

    │
    ▼
Repurpose
  ├── Title suggestions (5 options)
  ├── YouTube description (SEO, with timestamps)
  ├── Tags / keywords
  ├── Twitter/X thread
  ├── LinkedIn post
  ├── Instagram captions (per reel)
  └── Clean formatted transcript

    │
    ▼
Translate (optional)
  ├── Translate overlays → re-render into video
  ├── Translate captions → SRT per language
  ├── Translate chapters + description
  └── Dub audio in original voice (ElevenLabs)

    │
    ▼
Package
  └── ZIP: all outputs, all languages, ready to upload
```

---

## User Personas

### Alex — Solo Course Creator
**Context:** Teaches productivity systems. Sells a $497 course on Kajabi. Makes 10–12 videos per course. No editor.

**Job to be done:** *Make my course look professional and not spend 4 hours per video on the stuff that isn't teaching.*

**Current pain:** Writes chapters and show notes manually. Never adds overlays or reels. Quiz and interactive content are aspirational but never happen.

**What they get:** Complete course-ready video package in 15 minutes. Chapters, captions, overlays, and a formatted transcript for the course platform.

---

### Maya — Educational YouTuber (22k subscribers)
**Context:** Tech and coding tutorials. Has AdSense and one sponsor. Posts twice a month. No editor — uses Descript for silence removal.

**Job to be done:** *Look as professional as channels 10x my size without spending 6 hours editing.*

**Current pain:** Manually writes chapters (45 min each video). Wants to post Shorts but never has time to clip them. No captions.

**What they get:** Chapters done automatically. 3–5 Shorts ready to post. Captions. Reels captioned and cropped for vertical. Saves 3+ hours per video.

---

### James — Travel Vlogger (8k subscribers)
**Context:** Travels and vlogs. Posts lifestyle + destination content. Edits in CapCut on his phone.

**Job to be done:** *Get my content on Instagram and TikTok without re-editing everything from scratch.*

**Current pain:** Clips reels manually in CapCut. Has to write captions for each one. No chapters. No colour grading consistency.

**What they get:** 3–5 vertical reels with captions and location overlays. Colour preset applied. Instagram captions generated. Trailer for YouTube channel page.

---

### Sarah — Freelance Video Editor
**Context:** Charges $300–400/video. Has 8 regular clients. Uses Premiere Pro + Descript + ChatGPT.

**Job to be done:** *Add more value to my clients without working more hours.*

**Current pain:** Clients ask for chapters, show notes, reels — she does it manually and either eats the time or charges extra and risks losing the client.

**What they get:** Adds "full content package" as a $100–150 upsell. Delivers chapters, reels, captions, description, and repurposed content alongside the edited video. Product cost: $29. Revenue gain: $100–150 per client.

---

## User Journey

### Creator journey

```
Discovery
  "YouTube chapters generator" → free tool, no signup
  → gets chapters in 90 seconds
  → signs up to save

Activation
  Uploads first full video (free tier)
  → sees overlaid video, reels, trailer, chapters, description
  → shares player URL with audience
  → hits watermark in shared player

Conversion
  Upgrade prompt: "Remove watermark + unlock all outputs"
  → upgrades to Pro ($69/month)
  → processes 2–3 videos/month

Retention
  Builds a habit — every video goes through here
  → video library becomes their content archive
  → adds translation for Spanish audience

Expansion
  Starts a new course → needs 12 videos processed
  → upgrades to Creator ($129/month) for volume
  → asks: "can my editor also access this?" → Teams conversation
```

### Output journey (what the creator does with each output)

| Output | Where it goes | Time saved |
|---|---|---|
| Overlaid video | YouTube / course platform upload | 3–6 hours |
| Chapters (.txt) | Paste into YouTube description | 45 min |
| Captions (.srt) | Upload to YouTube / course | 30 min |
| Reel 1–5 (.mp4) | Post to Instagram / TikTok / Shorts | 2 hours |
| Trailer (.mp4) | Channel page / course sales page | 1 hour |
| Title suggestions | A/B test on YouTube | 20 min |
| Description (.txt) | Paste into YouTube | 30 min |
| Tags (.txt) | Paste into YouTube | 15 min |
| Twitter thread (.txt) | Schedule in Buffer/Hypefury | 45 min |
| LinkedIn post (.txt) | Post directly | 20 min |
| Instagram captions | Post with each reel | 15 min/reel |
| Transcript (.txt) | Show notes / course resource | 30 min |
| **Total** | | **~8–10 hours saved** |

---

## Key Design Principles

**1. Output-first, not feature-first**
The product is measured by what comes out, not what went in. Every feature exists to improve or add to the output package.

**2. One upload, everything out**
The creator should never need to re-upload or re-process. One job produces every output they need for that video across all platforms.

**3. 15 minutes or less**
If processing takes longer than 15 minutes for a 10-minute video, it feels slow. Every pipeline stage should be optimised for this ceiling.

**4. The ZIP is the product**
The final deliverable is a folder with everything labelled, ready to upload. The creator should be able to open it and go.

**5. Language is a multiplier, not a feature**
Translation and dubbing don't add a new output — they multiply every existing output by the number of languages selected. Architecture and pricing should reflect this.

---

## What the Product Is Not

- Not a full video editor (no B-roll, no cut decisions, no music sync)
- Not a thumbnail generator (suggests the frame; doesn't generate AI images)
- Not a learning management system (no student accounts, no course hosting)
- Not a streaming platform (no hosting of the original video long-term)
- Not a social scheduler (generates content; doesn't post it)
