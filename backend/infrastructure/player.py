import json


def build_player_html(job_id: str, learning_script: dict) -> str:
    """Generate a self-contained interactive learning player HTML page."""
    title = learning_script.get("title", "Interactive Learning Player")

    # Safely embed JSON in a <script> block
    script_json = json.dumps(learning_script, ensure_ascii=False)
    script_json = script_json.replace("</", "<\\/")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_esc(title)}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0f0f13;color:#e2e2e8;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;height:100dvh;display:flex;flex-direction:column;overflow:hidden}}
header{{display:flex;align-items:center;justify-content:space-between;padding:10px 18px;background:#1a1a24;border-bottom:1px solid rgba(255,255,255,.08);flex-shrink:0;gap:12px}}
.hdr-title{{font-size:14px;font-weight:600;color:#e2e2e8;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.score-badge{{display:flex;align-items:center;gap:6px;background:rgba(99,102,241,.12);border:1px solid rgba(99,102,241,.28);border-radius:20px;padding:4px 14px;font-size:12px;color:#a5b4fc;flex-shrink:0}}
.score-num{{font-weight:700;color:#818cf8;font-size:15px;min-width:2ch;text-align:right}}
@keyframes pop{{0%{{transform:scale(1)}}50%{{transform:scale(1.35)}}100%{{transform:scale(1)}}}}
.score-pop{{animation:pop .3s ease}}
#main{{display:flex;flex:1;overflow:hidden;min-height:0}}
#video-col{{flex:0 0 60%;display:flex;flex-direction:column;background:#000;position:relative;min-width:0}}
video{{width:100%;height:100%;object-fit:contain;display:block}}
#quiz-markers{{position:absolute;bottom:0;left:0;right:0;height:24px;pointer-events:none}}
.q-marker{{position:absolute;width:3px;height:10px;background:#f59e0b;border-radius:2px;bottom:7px;transform:translateX(-50%);opacity:.75}}
#panel-col{{flex:0 0 40%;display:flex;flex-direction:column;overflow:hidden;border-left:1px solid rgba(255,255,255,.06);background:#13131c;min-width:0}}
#section-header{{padding:14px 18px 10px;border-bottom:1px solid rgba(255,255,255,.06);flex-shrink:0}}
.s-label{{font-size:10px;text-transform:uppercase;letter-spacing:.9px;color:rgba(255,255,255,.3);margin-bottom:3px}}
.s-title{{font-size:15px;font-weight:600;color:#e2e2e8;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
#panel-body{{flex:1;overflow-y:auto;padding:14px 18px;transition:opacity .18s ease}}
#panel-body.fading{{opacity:0}}
#panel-body::-webkit-scrollbar{{width:3px}}
#panel-body::-webkit-scrollbar-thumb{{background:rgba(255,255,255,.1);border-radius:2px}}
.summary-text{{font-size:13px;line-height:1.65;color:rgba(255,255,255,.68);margin-bottom:14px}}
.facts-heading{{font-size:10px;text-transform:uppercase;letter-spacing:.8px;color:rgba(255,255,255,.28);margin-bottom:7px}}
.fact-item{{display:flex;gap:8px;align-items:flex-start;padding:8px 10px;border-radius:8px;background:rgba(255,255,255,.04);margin-bottom:5px;cursor:pointer;transition:background .15s}}
.fact-item:hover{{background:rgba(255,255,255,.07)}}
.fact-bullet{{color:#6366f1;font-size:11px;margin-top:3px;flex-shrink:0}}
.fact-text{{font-size:13px;color:rgba(255,255,255,.72);line-height:1.5}}
.fact-copied{{color:#34d399;font-size:11px}}
.dd-toggle{{display:flex;align-items:center;gap:5px;cursor:pointer;font-size:12px;color:rgba(255,255,255,.38);margin:11px 0 7px;user-select:none;transition:color .15s}}
.dd-toggle:hover{{color:rgba(255,255,255,.6)}}
.dd-text{{font-size:13px;line-height:1.6;color:rgba(255,255,255,.5);padding:9px 12px;border-left:2px solid rgba(99,102,241,.4);background:rgba(99,102,241,.06);border-radius:0 6px 6px 0;margin-bottom:10px}}
.links-section{{margin-top:12px}}
.link-item{{display:flex;align-items:center;gap:6px;padding:7px 10px;border-radius:8px;background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.2);margin-bottom:5px;text-decoration:none;color:#a5b4fc;font-size:13px;transition:background .15s;word-break:break-word}}
.link-item:hover{{background:rgba(99,102,241,.15)}}
.link-icon{{font-size:10px;flex-shrink:0}}
.empty-panel{{text-align:center;padding:36px 18px;color:rgba(255,255,255,.28);font-size:13px;line-height:1.6}}
#quiz-modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.88);z-index:100;align-items:center;justify-content:center;padding:16px}}
#quiz-modal.active{{display:flex}}
.quiz-card{{background:#1e1e2e;border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:24px;max-width:520px;width:100%;box-shadow:0 24px 64px rgba(0,0,0,.6);max-height:90dvh;overflow-y:auto}}
.quiz-card::-webkit-scrollbar{{width:3px}}
.quiz-card::-webkit-scrollbar-thumb{{background:rgba(255,255,255,.1)}}
.quiz-top{{display:flex;align-items:center;gap:8px;margin-bottom:14px}}
.quiz-badge{{display:inline-flex;align-items:center;gap:5px;background:rgba(99,102,241,.15);border:1px solid rgba(99,102,241,.3);border-radius:20px;padding:3px 11px;font-size:11px;color:#a5b4fc}}
.quiz-diff{{font-size:10px;padding:2px 7px;border-radius:10px;font-weight:600}}
.diff-easy{{background:rgba(52,211,153,.15);color:#34d399}}
.diff-medium{{background:rgba(251,191,36,.15);color:#fbbf24}}
.diff-hard{{background:rgba(239,68,68,.15);color:#f87171}}
.quiz-q{{font-size:16px;font-weight:600;color:#e2e2e8;line-height:1.45;margin-bottom:18px}}
.quiz-options{{display:flex;flex-direction:column;gap:7px;margin-bottom:14px}}
.quiz-opt{{padding:11px 15px;border-radius:10px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.04);color:rgba(255,255,255,.78);font-size:13px;cursor:pointer;text-align:left;transition:all .15s;line-height:1.4}}
.quiz-opt:hover:not(:disabled){{background:rgba(99,102,241,.15);border-color:rgba(99,102,241,.4);color:#e2e2e8}}
.quiz-opt.correct{{background:rgba(52,211,153,.15);border-color:#34d399;color:#34d399}}
.quiz-opt.wrong{{background:rgba(239,68,68,.1);border-color:rgba(239,68,68,.45);color:#f87171}}
.quiz-opt:disabled{{cursor:default}}
.hint-toggle{{font-size:12px;color:rgba(255,255,255,.3);cursor:pointer;margin-bottom:10px;transition:color .15s}}
.hint-toggle:hover{{color:rgba(255,255,255,.5)}}
.hint-text{{font-size:12px;color:rgba(251,191,36,.8);background:rgba(251,191,36,.07);padding:8px 10px;border-radius:6px;margin-bottom:10px;line-height:1.5}}
.quiz-feedback{{padding:11px 13px;border-radius:10px;margin-bottom:14px}}
.quiz-feedback.correct-fb{{background:rgba(52,211,153,.1);border:1px solid rgba(52,211,153,.3)}}
.quiz-feedback.wrong-fb{{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2)}}
.fb-title{{font-size:13px;font-weight:600;margin-bottom:4px}}
.correct-fb .fb-title{{color:#34d399}}
.wrong-fb .fb-title{{color:#f87171}}
.fb-explain{{font-size:13px;line-height:1.55;color:rgba(255,255,255,.62)}}
.fb-fact{{font-size:12px;color:rgba(255,255,255,.38);margin-top:6px;font-style:italic;line-height:1.5}}
.quiz-actions{{display:flex;gap:8px}}
.btn-continue{{flex:1;padding:10px;border-radius:10px;background:#6366f1;border:none;color:#fff;font-size:13px;font-weight:600;cursor:pointer;transition:background .15s}}
.btn-continue:hover{{background:#5254e8}}
.btn-skip{{padding:10px 15px;border-radius:10px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);color:rgba(255,255,255,.45);font-size:13px;cursor:pointer;transition:background .15s}}
.btn-skip:hover{{background:rgba(255,255,255,.1);color:rgba(255,255,255,.65)}}
.kbd-hint{{font-size:11px;color:rgba(255,255,255,.22);padding:10px 18px;border-top:1px solid rgba(255,255,255,.05);flex-shrink:0;text-align:center}}
@media(max-width:768px){{
  #main{{flex-direction:column}}
  #video-col{{flex:0 0 40dvh}}
  #panel-col{{flex:1;border-left:none;border-top:1px solid rgba(255,255,255,.06)}}
}}
</style>
</head>
<body>
<header>
  <div class="hdr-title">🎬 {_esc(title)}</div>
  <div class="score-badge">Score&nbsp;<span class="score-num" id="score-display">0</span></div>
</header>
<div id="main">
  <div id="video-col">
    <video id="vid" controls src="/video/{job_id}">Your browser does not support HTML5 video.</video>
    <div id="quiz-markers"></div>
  </div>
  <div id="panel-col">
    <div id="section-header">
      <div class="s-label">Now Watching</div>
      <div class="s-title" id="s-title">—</div>
    </div>
    <div id="panel-body">
      <div class="empty-panel">Press play to start the interactive learning experience.<br><br>Quiz questions will appear at key moments.</div>
    </div>
  </div>
</div>
<div class="kbd-hint">Space = pause/play &nbsp;·&nbsp; ← → = seek 10s</div>
<div id="quiz-modal">
  <div class="quiz-card">
    <div class="quiz-top">
      <div class="quiz-badge">📝 Quiz Question</div>
      <span class="quiz-diff" id="q-diff"></span>
    </div>
    <div class="quiz-q" id="q-text"></div>
    <div class="quiz-options" id="q-opts"></div>
    <div class="hint-toggle" id="hint-btn" onclick="toggleHint()" style="display:none">💡 Show hint</div>
    <div class="hint-text" id="hint-text" style="display:none"></div>
    <div class="quiz-feedback" id="q-feedback" style="display:none"></div>
    <div class="quiz-actions">
      <button class="btn-skip" id="btn-skip" onclick="skipQuiz()">Skip</button>
      <button class="btn-continue" id="btn-cont" onclick="continueVideo()" style="display:none">Continue watching →</button>
    </div>
  </div>
</div>
<script>
const SD = {script_json};
const vid = document.getElementById('vid');
const panelBody = document.getElementById('panel-body');
const sTitleEl = document.getElementById('s-title');
const quizModal = document.getElementById('quiz-modal');
const scoreEl = document.getElementById('score-display');
let curSecIdx = -1, score = 0;
let pendingQuizTs = new Set(SD.quiz_points.map(q => +q.timestamp.toFixed(2)));

vid.addEventListener('loadedmetadata', () => {{
  const dur = vid.duration;
  const markersEl = document.getElementById('quiz-markers');
  markersEl.innerHTML = '';
  SD.quiz_points.forEach(qp => {{
    const m = document.createElement('div');
    m.className = 'q-marker';
    m.style.left = (qp.timestamp / dur * 100) + '%';
    m.title = 'Quiz at ' + fmt(qp.timestamp);
    markersEl.appendChild(m);
  }});
}});

vid.addEventListener('timeupdate', () => {{
  const t = vid.currentTime;
  let newIdx = SD.sections.findIndex(s => t >= s.start && t < s.end);
  if (newIdx === -1) newIdx = SD.sections.length - 1;
  if (newIdx !== curSecIdx && newIdx >= 0) {{
    curSecIdx = newIdx;
    updatePanel(SD.sections[newIdx]);
  }}
  for (const qp of SD.quiz_points) {{
    const ts = +qp.timestamp.toFixed(2);
    if (pendingQuizTs.has(ts) && t >= qp.timestamp) {{
      pendingQuizTs.delete(ts);
      vid.pause();
      showQuiz(qp);
      break;
    }}
  }}
}});

function updatePanel(s) {{
  panelBody.classList.add('fading');
  sTitleEl.textContent = s.title || '';
  setTimeout(() => {{
    panelBody.innerHTML = renderSection(s);
    panelBody.classList.remove('fading');
    panelBody.scrollTop = 0;
  }}, 170);
}}

function renderSection(s) {{
  let h = '';
  if (s.summary) h += `<p class="summary-text">${{esc(s.summary)}}</p>`;
  if (s.key_facts && s.key_facts.length) {{
    h += '<div class="facts-heading">Key Facts</div>';
    s.key_facts.forEach(f => {{
      h += `<div class="fact-item" onclick="copyFact(this,'${{esc(f).replace(/'/g,"\\\\'")}}')" title="Click to copy">
        <span class="fact-bullet">◆</span>
        <span class="fact-text">${{esc(f)}}</span>
      </div>`;
    }});
  }}
  if (s.deep_dive) {{
    h += `<div class="dd-toggle" onclick="toggleDD(this)"><span>▶</span> Deep dive</div>
      <div class="dd-text" style="display:none">${{esc(s.deep_dive)}}</div>`;
  }}
  if (s.links && s.links.length) {{
    h += '<div class="links-section">';
    s.links.forEach(l => {{
      h += `<a class="link-item" href="${{esc(l.url)}}" target="_blank" rel="noopener">
        <span class="link-icon">↗</span>${{esc(l.text)}}
      </a>`;
    }});
    h += '</div>';
  }}
  return h || '<p class="summary-text">Watch this section to learn more.</p>';
}}

function toggleDD(toggle) {{
  const next = toggle.nextElementSibling;
  const icon = toggle.querySelector('span');
  const open = next.style.display === 'none';
  next.style.display = open ? 'block' : 'none';
  icon.textContent = open ? '▼' : '▶';
}}

function copyFact(el, text) {{
  navigator.clipboard.writeText(text).then(() => {{
    const span = el.querySelector('.fact-text');
    const orig = span.innerHTML;
    span.innerHTML = '<span class="fact-copied">✓ Copied!</span>';
    setTimeout(() => span.innerHTML = orig, 1600);
  }}).catch(() => {{}});
}}

let activeQuiz = null, hintShown = false;
function showQuiz(qp) {{
  activeQuiz = qp;
  hintShown = false;
  const diff = qp.difficulty || 'medium';
  const diffEl = document.getElementById('q-diff');
  diffEl.textContent = diff;
  diffEl.className = 'quiz-diff diff-' + diff;
  document.getElementById('q-text').textContent = qp.question;
  const hintBtn = document.getElementById('hint-btn');
  const hintText = document.getElementById('hint-text');
  hintText.style.display = 'none';
  hintText.textContent = qp.hint || '';
  hintBtn.style.display = qp.hint ? '' : 'none';
  hintBtn.textContent = '💡 Show hint';
  document.getElementById('q-feedback').style.display = 'none';
  document.getElementById('btn-cont').style.display = 'none';
  document.getElementById('btn-skip').style.display = '';
  const optsEl = document.getElementById('q-opts');
  optsEl.innerHTML = '';
  qp.options.forEach((opt, i) => {{
    const btn = document.createElement('button');
    btn.className = 'quiz-opt';
    btn.textContent = String.fromCharCode(65 + i) + '. ' + opt;
    btn.onclick = () => answerQuiz(i);
    optsEl.appendChild(btn);
  }});
  quizModal.classList.add('active');
}}

function answerQuiz(idx) {{
  const qp = activeQuiz;
  const correct = idx === qp.correct_index;
  score += correct ? 10 : 5;
  scoreEl.textContent = score;
  scoreEl.closest('.score-badge').classList.remove('score-pop');
  void scoreEl.closest('.score-badge').offsetWidth;
  scoreEl.closest('.score-badge').classList.add('score-pop');
  document.querySelectorAll('.quiz-opt').forEach((btn, i) => {{
    btn.disabled = true;
    if (i === qp.correct_index) btn.classList.add('correct');
    else if (i === idx && !correct) btn.classList.add('wrong');
  }});
  const fb = document.getElementById('q-feedback');
  fb.style.display = '';
  fb.className = 'quiz-feedback ' + (correct ? 'correct-fb' : 'wrong-fb');
  fb.innerHTML = `<div class="fb-title">${{correct ? '✓ Correct! +10 points' : '✗ Not quite — +5 for trying'}}</div>
    <div class="fb-explain">${{esc(qp.explanation)}}</div>
    ${{qp.related_fact ? `<div class="fb-fact">💡 ${{esc(qp.related_fact)}}</div>` : ''}}`;
  document.getElementById('btn-skip').style.display = 'none';
  document.getElementById('btn-cont').style.display = '';
}}

function toggleHint() {{
  hintShown = !hintShown;
  document.getElementById('hint-text').style.display = hintShown ? '' : 'none';
  document.getElementById('hint-btn').textContent = hintShown ? '💡 Hide hint' : '💡 Show hint';
}}

function skipQuiz() {{ quizModal.classList.remove('active'); vid.play(); }}
function continueVideo() {{ quizModal.classList.remove('active'); vid.play(); }}

document.addEventListener('keydown', e => {{
  if (quizModal.classList.contains('active')) return;
  if (e.code === 'Space' && document.activeElement === document.body) {{
    e.preventDefault();
    vid.paused ? vid.play() : vid.pause();
  }} else if (e.code === 'ArrowRight') {{
    vid.currentTime = Math.min(vid.duration || 0, vid.currentTime + 10);
  }} else if (e.code === 'ArrowLeft') {{
    vid.currentTime = Math.max(0, vid.currentTime - 10);
  }}
}});

function fmt(s) {{ return Math.floor(s/60)+':'+(Math.floor(s%60)+'').padStart(2,'0'); }}
function esc(str) {{
  if (!str) return '';
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}}
</script>
</body>
</html>"""


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
