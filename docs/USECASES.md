# Use Cases

Each use case walks through a real person, their video, the features they use, and what they get out.

---

## Use Case 1 — Educational YouTuber

**Who:** Marcus, 28k subscribers, teaches coding tutorials. Posts twice a month. Records himself at his desk. Uses OBS. No editor.

**The video:** 22-minute tutorial on Docker containers. Raw recording — some background hum from his PC fan, a few tangents where he loses his train of thought, no intro.

---

### Step-by-step

**1. Upload**
Marcus drops his raw `.mp4` into the product. The AI transcribes it and generates a full understanding of the video: what it teaches, who it's for, the structure.

---

**2. Noise Reduction**
Background hum from the PC fan removed automatically using Dolby audio enhancement. The recording goes from "recorded in a bedroom" to "recorded in a studio" in one step.

> Before: noticeable hiss underneath every sentence
> After: clean, broadcast-quality audio

---

**3. Trim — Remove Irrelevant Parts**
The AI identifies sections where Marcus loses his thread, repeats himself, or goes off on a tangent unrelated to Docker. It flags 4 sections totalling 3 minutes and 20 seconds.

Marcus reviews each flagged section with a preview clip, approves 3 of the 4 cuts. The video is re-rendered at 18 minutes and 40 seconds.

> Before: 22 minutes with dead weight
> After: 18:40, tight and on-topic

---

**4. Filters**
Marcus selects "Subtle" — a light contrast boost and slight warmth to make the screen recording look less flat. Applied across the entire video via FFmpeg.

---

**5. Overlays**
The AI generates 9 checkpoint overlays — key commands, concept definitions, architecture diagrams described in text. Each one is timed to the exact moment Marcus explains it.

Examples:
- at 2:14 — *"Container vs VM: containers share the OS kernel, VMs emulate full hardware"*
- at 8:45 — *"`docker run -d -p 8080:80 nginx` — detached mode, port mapping"*
- at 14:22 — *"Volumes persist data beyond container lifecycle"*

---

**6. Preview — Hook Appended to Start**
The AI generates a 25-second hook intro from the best moments in the video:
- Shows 3 quick clips of the most visually interesting moments
- Overlays text: *"By the end of this video: containers, images, volumes, networking"*
- Appended to the front of the final video

Marcus now has an industry-standard YouTube hook that would have taken him 45 minutes to create manually.

---

**7. Thumbnail Generation**
The AI identifies the frame with the highest visual impact — Marcus at his clearest, on-screen terminal showing a clean command. Surfaces it as the suggested thumbnail frame with a one-click download at full resolution.

Marcus opens it in Canva, adds his usual title text. Done in 5 minutes instead of 30.

---

**8. Generate Description + SEO**
Output:

```
Title options (pick one):
  1. Docker Containers in 20 Minutes — Everything You Need to Know
  2. Docker for Beginners: Containers, Images & Volumes Explained
  3. Stop Being Confused by Docker — Full Beginner Tutorial
  4. Docker Crash Course 2026 — The Only Guide You Need
  5. I Learned Docker in 20 Minutes. Here's What Actually Matters.

Description:
  In this video I walk you through Docker containers from scratch —
  no prior knowledge needed. We cover containers vs VMs, images,
  volumes, networking, and how to run your first container.

  00:00 What is Docker?
  02:14 Containers vs Virtual Machines
  05:30 Your first docker run command
  08:45 Port mapping and detached mode
  [... full chapters ...]

  🔔 Subscribe for weekly dev tutorials.
  📦 Starter repo: [link]

Tags:
  docker tutorial, docker for beginners, docker containers explained,
  docker vs vm, docker run command, containerisation, devops beginner,
  [... 20 tags total]
```

---

**9. Social Media Clips**
The AI selects the 5 most self-contained, shareable moments — places where Marcus explains a single concept clearly in under 30 seconds. Each clip is:
- Cropped to 9:16 vertical
- Captions burned in (always-on for social)
- Ready to post on TikTok, Instagram Reels, YouTube Shorts

Instagram captions generated for each:

> *"Most people think containers are like virtual machines. They're not. Here's the actual difference in 20 seconds. 🐳 #docker #devops #coding"*

---

**10. Audio Translation + Subtitles**
Marcus selects Spanish and Portuguese — he knows he has a large Latin American audience.

- Spanish `.srt` generated and translated
- Portuguese `.srt` generated and translated
- Overlay text translated and re-rendered into separate video versions

Three video files exported: English (with overlays), Spanish (translated overlays + subtitles), Portuguese (translated overlays + subtitles).

---

**11. ZIP Download**
```
marcus_docker_tutorial_package/
  ├── video_en.mp4                  ← overlaid + trimmed + filtered
  ├── video_es.mp4                  ← Spanish overlays + subtitles
  ├── video_pt.mp4                  ← Portuguese overlays + subtitles
  ├── reels/
  │   ├── reel_containers_vs_vms.mp4
  │   ├── reel_docker_run.mp4
  │   ├── reel_volumes.mp4
  │   ├── reel_networking.mp4
  │   └── reel_first_container.mp4
  ├── trailer.mp4
  ├── thumbnail_frame.jpg
  ├── chapters.txt
  ├── captions_en.srt
  ├── captions_es.srt
  ├── captions_pt.srt
  ├── description.txt
  ├── tags.txt
  ├── twitter_thread.txt
  ├── linkedin_post.txt
  ├── instagram_captions/
  │   └── reel_1.txt ... reel_5.txt
  └── transcript.txt
```

---

### Time comparison

| Task | Manual (Marcus today) | With product |
|---|---|---|
| Noise removal | 0 (skips it) | Automatic |
| Trimming tangents | 1.5 hrs | 5 min (review suggested cuts) |
| Overlays / annotations | 0 (skips it) | Automatic |
| Hook intro | 45 min | Automatic |
| Thumbnail shortlisting | 30 min | 1 click |
| Description + chapters | 45 min | Automatic |
| Tags | 15 min | Automatic |
| 5 social reels | 2 hrs | Automatic |
| Instagram captions | 30 min | Automatic |
| Spanish + Portuguese subtitles | Never done | Automatic |
| **Total** | **~6 hours** | **~20 minutes** |

---

---

## Use Case 2 — Travel Vlogger

**Who:** Priya, 14k Instagram followers, 6k YouTube subscribers. Travels full time. Films on Sony ZV-E10. Edits on her laptop between flights. Posts 2–3 times a week.

**The video:** 18 minutes of raw footage from her 3 days in Kyoto, Japan. Wind noise on some outdoor shots. Slow sections where she was just walking.

---

### Step-by-step

**1. Upload**
Raw `.mov` from camera. AI understands: travel content, Japan, specific locations (Fushimi Inari, Arashiyama bamboo grove, Nishiki Market), tone is personal and exploratory.

**2. Noise Reduction**
Wind noise removed from outdoor walking sections. Café background noise reduced without removing ambient atmosphere.

**3. Trim — Remove Irrelevant Parts**
AI identifies 4 minutes of walking footage with no dialogue or notable visual. Flags for removal. Priya approves 3 of the 4 — she keeps one atmospheric walk scene. Video trims to 14.5 minutes.

**4. Filters**
Priya selects "Travel Warm" — lifted shadows, boosted saturation, golden tone. Every frame consistently colour-graded without her touching Premiere.

**5. Overlays — Location Tags**
The AI detects location mentions from the transcript and generates location overlays at each mention:
- at 1:40 — *"Fushimi Inari Taisha — 10,000 torii gates, built 711 AD"*
- at 7:15 — *"Arashiyama Bamboo Grove — best before 8am to avoid crowds"*
- at 12:30 — *"Nishiki Market — 400 years old, 100+ vendors"*

These appear as clean lower-third overlays, styled like travel documentary callouts.

**6. Preview — Hook Appended to Start**
AI generates a 20-second highlight teaser: the most visually stunning frames from the video stitched together with the text overlay *"3 Days in Kyoto — what nobody tells you"* and music beat markers. Prepended to the video.

**7. Blur / Censor**
Priya notices her hotel room door number is visible in one shot. She marks the region in the review UI. That region is blurred across the 8 seconds it's on screen.

**8. Social Media Clips — Instagram + TikTok**
5 clips extracted:
- The Fushimi Inari gate walk (vertical, captioned, 28 seconds)
- Tasting street food at Nishiki Market (22 seconds)
- Sunrise at the bamboo grove (18 seconds)
- Her hotel room tour (25 seconds, door number blurred)
- "Things I wish I knew before visiting Kyoto" — a talking head section (30 seconds)

Each cropped to 9:16. Instagram captions generated:
> *"Woke up at 5am to beat the crowds at Arashiyama. Worth every second 🎋 #kyoto #japan #travelvlog #solotravel"*

**9. Audio Translation + Subtitles**
Priya adds Japanese subtitles — she wants her content accessible to local Japanese viewers and the Japanese travel community. Also adds Spanish for her growing Latin American audience.

**10. ZIP Download**
Complete package: filtered video, 5 reels, captions in 3 languages, Instagram captions, description with location links, tags.

---

### Time comparison

| Task | Priya today | With product |
|---|---|---|
| Colour grading | 45 min (CapCut) | Automatic |
| Trimming slow sections | 1.5 hrs | 5 min review |
| Location overlays | 0 (skips) | Automatic |
| Clipping 5 reels | 2 hrs | Automatic |
| Writing 5 Instagram captions | 45 min | Automatic |
| Japanese + Spanish subtitles | Never done | Automatic |
| Description + tags | 30 min | Automatic |
| **Total** | **~5.5 hours** | **~15 minutes** |

---

---

## Use Case 3 — Course Creator

**Who:** Daniel, sells a $697 course on personal finance. Hosts it on Kajabi. Makes 8–10 videos per module. Records in his home office. Has a small following on LinkedIn.

**The video:** 28-minute lesson on compound interest and investment fundamentals. Dense, educational. Recorded in one take with some stumbles.

---

### Step-by-step

**1. Upload + Clarify**
AI understands: financial education, beginner audience, core concepts are compound interest, index funds, time in market. Asks two clarifying questions — Daniel confirms audience is 25–35 year olds new to investing.

**2. Noise Reduction**
HVAC hum removed. Recording becomes clean.

**3. Trim — Remove Irrelevant Parts**
AI flags two sections: a 90-second moment where Daniel restarts an explanation, and a 2-minute tangent about cryptocurrency he decides not to include. Both trimmed. Video goes from 28 to 24 minutes.

**4. Overlays**
12 overlays generated — definitions, formulas, worked examples:
- at 3:20 — *"Compound interest: earning returns on your returns. Einstein called it the 8th wonder of the world."*
- at 9:45 — *"£1,000 at 7% for 30 years = £7,612 — without adding a single pound more"*
- at 16:30 — *"Index fund: owns a slice of every company in an index. No stock-picking required."*

**5. Preview — Hook Appended to Start**
AI generates a 30-second preview showing what the student will learn in the lesson. Styled as a "Learning objectives" intro card:
- *"In this lesson: how compound interest works, the maths behind it, and exactly where to put your first £100"*

This is standard in professional online courses. Daniel was never doing this.

**6. Thumbnail Suggestion**
Best frame: Daniel pointing at a whiteboard diagram. Surfaced as suggested thumbnail at full resolution.

**7. Generate Description + SEO**

- 5 title options for the course module
- Full chapter breakdown (12 chapters)
- Learning objectives formatted for Kajabi module description
- Tags and keywords for the course platform

**8. Social Media Clips**
4 clips for LinkedIn — the platform where Daniel's audience is. Each under 30 seconds, cropped to square (1:1) for LinkedIn feed:
- "The maths of compound interest in 25 seconds"
- "Why starting at 25 vs 35 makes a £200k difference"
- "Index funds explained in 20 seconds"
- "The one thing most people get wrong about investing"

LinkedIn captions generated for each.

**9. Audio Translation + Subtitles**
Daniel adds Spanish subtitles — he has a Spanish-speaking audience segment from his LinkedIn presence. Spanish-translated overlay version also exported.

**10. ZIP Download**
Course-ready package: trimmed video, 12 overlays, chapters formatted for Kajabi, captions, LinkedIn clips, module description copy, learning objectives.

---

---

## Use Case 4 — Corporate / Product Demo

**Who:** Lena, product marketer at a B2B SaaS company. Records product demos for the sales team and onboarding. No video editor on the team.

**The video:** 15-minute product walkthrough of their analytics dashboard. Screen recording + talking head. Sensitive customer data visible on some screens.

---

### Step-by-step

**1. Upload**
Screen recording + webcam composite. AI understands: SaaS product demo, analytics features, target audience is existing customers learning the product.

**2. Noise Reduction**
Office background noise removed.

**3. Trim — Remove Irrelevant Parts**
AI flags 3 minutes of navigation dead time (loading screens, switching between windows). Trimmed. Video goes from 15 to 12 minutes.

**4. Blur / Censor**
Critical step for this use case. AI identifies all screens showing customer data — names, email addresses, revenue figures. All text regions auto-blurred throughout. Lena reviews and confirms 6 blur zones across the video.

Zero chance of a GDPR or data leak issue in the final video.

**5. Overlays**
Feature callouts generated for each product section demonstrated:
- *"Cohort analysis — compare retention across acquisition channels"*
- *"Custom date ranges support up to 3 years of historical data"*
- *"Export to CSV or connect directly via API"*

**6. Captions**
For accessibility compliance and for viewers watching without sound (common in office environments).

**7. Social Media Clips**
2 LinkedIn clips extracted: the most impressive feature moments, suitable for the company's LinkedIn page.

**8. Audio Translation + Subtitles**
Lena adds French and German subtitles — the company has customers in France and Germany.

---

---

## Use Case 5 — Freelance Editor Serving a Client

**Who:** Tom, freelance video editor. 12 regular clients. Charges £300–400 per video. Uses Premiere Pro + Descript + ChatGPT. Wants to offer more value without working more hours.

**The client video:** A 20-minute interview with a business coach. Raw footage. Two camera angles. Some awkward silences and a rambling section at the end.

---

### Step-by-step

**1. Upload**
Tom uploads the primary camera angle. AI understands: interview-style content, business/professional development topic.

**2. Noise Reduction**
Room reverb and HVAC noise removed. Both voices cleaned up.

**3. Trim — Remove Irrelevant Parts**
AI flags 5 minutes of content: the rambling conclusion, a long pause while the subject collects their thoughts, and a repeated question. Tom reviews and approves all cuts. Interview tightens to 15 minutes.

**4. Filters**
Tom selects "Professional" — neutral grade, clean skin tones, natural contrast. Consistent across the whole video.

**5. Blur / Censor**
The client's branded presentation was visible in the background with some confidential figures. Tom blurs the presentation screen throughout.

**6. Overlays**
Key quotes and concepts from the interview generated as overlay cards:
- *"The biggest mistake founders make: optimising for revenue before retention"*
- *"First 100 customers tell you everything — if you listen"*

**7. Social Media Clips**
5 clips — the most quotable, standalone moments from the interview. Each under 30 seconds, vertical.

**8. Generate Description + SEO**
Full YouTube description, chapters, tags, and 5 title options — ready for the client to paste directly.

**9. Twitter Thread + LinkedIn Post**
Generated from the interview's key insights. Tom delivers these to the client as bonus assets.

**10. ZIP**
Tom delivers to the client:
- Trimmed, colour-graded video
- 5 social clips
- Description, chapters, tags
- Twitter thread + LinkedIn post
- Captions

---

### What this does for Tom's business

| | Before | After |
|---|---|---|
| Deliverables per video | Edited video only | Video + 5 clips + description + chapters + thread + LinkedIn + captions |
| Time per video | 6–8 hours | 3–4 hours (creative editing) + 20 min review |
| What he charges | £350 | £350 base + £100 "content package" upsell |
| Product cost | £0 | £29 |
| Additional profit per client | — | £71 |
| With 10 clients/month | — | +£710/month for 20 minutes of extra work |

---

---

## Feature × Use Case Coverage

| Feature | YouTuber | Travel Vlogger | Course Creator | Corporate | Freelancer |
|---|---|---|---|---|---|
| Upload | ✅ | ✅ | ✅ | ✅ | ✅ |
| Noise Reduction | ✅ | ✅ | ✅ | ✅ | ✅ |
| Trim irrelevant parts | ✅ | ✅ | ✅ | ✅ | ✅ |
| Filters | ✅ | ✅ | — | ✅ | ✅ |
| Overlays | ✅ | ✅ | ✅ | ✅ | ✅ |
| Preview / Hook intro | ✅ | ✅ | ✅ | — | — |
| Thumbnail suggestion | ✅ | — | ✅ | — | — |
| Description + SEO | ✅ | ✅ | ✅ | — | ✅ |
| Social media clips | ✅ | ✅ | ✅ | ✅ | ✅ |
| Audio translation | ✅ | ✅ | ✅ | ✅ | — |
| Subtitles / captions | ✅ | ✅ | ✅ | ✅ | ✅ |
| Blur / Censor | — | ✅ | — | ✅ | ✅ |
| ZIP package | ✅ | ✅ | ✅ | ✅ | ✅ |
