# Business Documentation

## Vision

One upload. Every output a creator needs — in any language, in minutes.

## Mission

Replace the human + AI editing workflow for the educational and informational layer of video content. Faster, cheaper, globally accessible.

---

## The Problem

A creator in 2026 competing against other human + AI workflows:

| Task | Human + AI today | Time | Cost |
|---|---|---|---|
| Chapters + description | ChatGPT + manual | 45 min | $0 + time |
| Captions | Descript / YouTube | 30 min | $24/mo |
| Social reels | Opus Clip | 20 min | $49/mo |
| Overlays / annotations | Manual or skipped | 2–4 hrs | $200–500 freelancer |
| Translation | Agency / manual | Days | $200–2000/language |
| Dubbing | Agency | Weeks | $500–2000/language |
| Content repurposing | ChatGPT + manual | 1–2 hrs | $0 + time |

Total: **5–8 hours per video**, **$73–150/month in tools**, **$200–500 if outsourced per video**.

This product does all of it in **15 minutes for $29/video**.

---

## Target Customers

### Primary — Solo Educator / Course Creator
- Makes 2–4 videos/month or 1–2 courses/year
- Earns from courses ($200–2000/student), coaching, or YouTube monetisation
- Currently spends 3–5 hours on the non-creative layer per video
- Pays for at least one creator tool already (signal: treats content as a business)
- Willingness to pay: $29–69/month

### Secondary — Educational YouTuber (1k–100k subscribers)
- Finance, tech, science, history, language channels
- Competes on information quality, not production value
- Needs chapters (YouTube algorithm), captions (accessibility), reels (Shorts)
- Has a small budget for tools; may have a part-time editor
- Willingness to pay: $29–129/month

### Tertiary — Travel Vlogger / Content Creator
- Creates lifestyle and travel content, needs fast turnaround
- Wants social reels, location overlays, colour presets, captions
- Less focused on educational layer, more on repurposing and reach
- Willingness to pay: $29–69/month

### Opportunity — Freelance Video Editor
- Currently charges $200–400/video using human + AI tools
- Can use this product to add an "educational package" upsell (+$50–100)
- 1 editor with 10 clients = 10 effective customers
- Product pays for itself on first video of the month

---

## Competitive Landscape

| Competitor | What they do | Price | Gap |
|---|---|---|---|
| Descript | Silence removal, transcript editing | $24/mo | No content understanding, no overlays, no reels |
| Opus Clip | Auto-generated social clips | $49/mo | No educational layer, no chapters, no translation |
| Rev.com | Transcription + captions | $1.50/min | Captions only |
| HeyGen | AI avatar dubbing | $29–89/mo | Avatars only, not for real human video |
| CapCut | Template-based editing | Free–$10/mo | Aesthetic only, no intelligence |
| Human + AI freelancer | Full video editing | $200–400/video | 1–2 days, no overlays, no translation at scale |

**The gap:** No single tool produces overlaid video + chapters + captions + reels + trailer + content repurposing + translation from one upload. We own that.

### Positioning

```
                     High content intelligence
                              │
              THIS PRODUCT    │
                              │
Low creator         ──────────┼──────────   High creator
effort                        │             effort
                              │
       CapCut / iMovie   Descript │  Premiere / Final Cut
                              │
                     Low content intelligence
```

One-line against each:
- vs. Descript: *"Descript removes silences. This adds meaning."*
- vs. Opus Clip: *"Opus Clip makes clips. This makes content."*
- vs. human + AI freelancer: *"Same output, 15 minutes, not 2 days."*
- vs. doing it manually: *"You're spending 5 hours on what this does automatically."*

---

## Pricing

### Per Video (default for direct sales)

| Output | Price |
|---|---|
| Full package (overlaid video + chapters + captions + 3 reels + trailer) | **$29/video** |
| + Translation per language (overlays + captions + chapters) | **+$5/language** |
| + Dubbing per language (audio in original voice) | **+$20/language** |

### Subscription (after 2–3 per-video purchases)

| Plan | Price | Videos/month | Effective per video |
|---|---|---|---|
| Pro | $69/month | 3 | $23 |
| Creator | $129/month | 8 | $16 |

### Free Tier
- 1 video/month
- Watermarked player
- Chapters + captions export only
- No reels, no trailer

---

## Unit Economics

### Per video cost breakdown

| Item | Cost |
|---|---|
| Claude API (checkpoints, chapters, repurposing) | $1.20 |
| Whisper transcription | $0.30 |
| Dolby noise removal | $0.60 |
| FFmpeg compute (overlays, reels, trailer) | $0.50 |
| Storage + CDN | $0.35 |
| Fixed cost allocation (server ÷ volume) | $1.50 |
| **Total** | **~$4.50** |

At $29/video: **84% gross margin** (intentional — the margin premium funds product quality and speed of development).

Translation add-on: cost ~$1, charge $5 → 80% margin.
Dubbing add-on: cost ~$8, charge $20 → 60% margin.

### Revenue projections (solo founder, no team)

| Customers | Monthly Revenue | Monthly Costs | Monthly Profit |
|---|---|---|---|
| 10 | $650 | $280 | $370 |
| 50 | $3,500 | $1,050 | $2,450 |
| 100 | $7,500 | $2,050 | $5,450 |
| 500 | $45,000 | $10,800 | $34,200 |
| 1,000 | $100,000 | $21,800 | $78,200 |
| 10,000 | $1,200,000 | $218,000 | $982,000 |

---

## Go-To-Market — Stealth Direct

No public launch. No ProductHunt. No SEO waiting game.

### The opening move

Process their video before contacting them. Send the output first.

> *"Hey [Name] — I watched your video on [topic]. I built a tool and ran it through. Here's the enhanced version, your YouTube chapters, and 3 reels ready to post. No pitch — want the files?"*

The output sells itself. One response is worth 100 cold emails about features.

### Acquisition sequence

```
Week 1–2    Build a list of 50 targets (YouTubers with no chapters = the signal)
Week 3      Process 10 of their videos — no contact yet
Week 4      Send 10 personalised messages with output attached
Week 5      Follow up, get on calls, understand objections
Week 6      Close first 5 paying customers
Month 3     Ask each: "Who else should use this?"
```

### Target list criteria
- Educational content (YouTube, course platform, LinkedIn)
- Active in last 30 days
- No chapters in video descriptions (obvious gap)
- 1k–100k subscribers (big enough to care, small enough to not have a team)
- Contact email visible

### Referral trigger (month 3+)
Creator communities are tight. One customer in a Skool group or YouTube creator Discord is worth 50 cold emails.

After a successful first video:
> *"Do you know 2–3 creators who'd get value from this? Happy to give them their first video free."*

---

## The Acquisition Flywheel

```
Free chapters tool (no signup)
  → creator signs up to save
  → processes first full video
  → shares player URL with audience ("powered by [product]")
  → every viewer is a product impression
  → viewer is also a creator
  → viewer searches "YouTube chapters generator"
  → cycle repeats
```

---

## Defensibility

1. **Speed compounds trust** — creators build a habit of uploading here because it's the fastest option. Switching cost grows with each video processed.
2. **Content library becomes an asset** — a creator with 50 processed videos has their content intelligence history here. They won't leave.
3. **Translation at scale is genuinely hard to replicate** — end-to-end dubbing pipeline that preserves voice and timing takes months to build. Once live, it's a real moat.
4. **The output is the distribution** — every shared player URL is a product ad. Organic acquisition compounds without paid spend.
