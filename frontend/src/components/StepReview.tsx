import { CSSProperties, useEffect, useRef, useState } from 'react'
import type {
  Checkpoint, CheckpointAlternative, Config, Importance, LearningScript, LearningSection,
  OverlayPosition, OverlayRole, OverlayTemplate, QuizPoint, Style, UploadResult,
} from '../types'

interface Props {
  upload: UploadResult
  config: Config
  checkpoints: Checkpoint[]
  summary: string
  sourceUrls: Record<string, string>
  learningScript: LearningScript
  onComplete: (checkpoints: Checkpoint[], learningScript: LearningScript) => void
  onBack: () => void
}

// ─── Style presets ────────────────────────────────────────────────────────────

const STYLE_PRESETS: Record<Style, { bg: string; text: string; sub: string; bold: boolean; sizeEm: number }> = {
  clean:     { bg: 'rgba(10,10,10,0.65)',  text: '#ffffff', sub: 'rgba(255,255,255,0.78)', bold: true,  sizeEm: 1.00 },
  cinematic: { bg: 'rgba(0,0,0,0.41)',     text: '#f0e8d2', sub: 'rgba(240,232,210,0.78)', bold: false, sizeEm: 0.78 },
  bold:      { bg: 'rgba(0,0,0,0.84)',     text: '#fff500', sub: 'rgba(255,245,0,0.78)',   bold: true,  sizeEm: 1.24 },
  minimal:   { bg: 'rgba(0,0,0,0.23)',     text: '#ffffff', sub: 'rgba(255,255,255,0.78)', bold: false, sizeEm: 0.67 },
}

const POSITION_CSS: Record<OverlayPosition, CSSProperties> = {
  top_left:      { top: '8px',    left:  '8px' },
  top_center:    { top: '8px',    left:  '50%', transform: 'translateX(-50%)' },
  top_right:     { top: '8px',    right: '8px' },
  bottom_left:   { bottom: '8px', left:  '8px' },
  bottom_center: { bottom: '8px', left:  '50%', transform: 'translateX(-50%)' },
  bottom_right:  { bottom: '8px', right: '8px' },
  center:        { top:  '50%',   left:  '50%', transform: 'translate(-50%,-50%)' },
}

const POSITION_LABELS: Record<OverlayPosition, string> = {
  top_left: 'Top Left', top_center: 'Top Center', top_right: 'Top Right',
  bottom_left: 'Bottom Left', bottom_center: 'Bottom Center', bottom_right: 'Bottom Right',
  center: 'Center',
}

const GRID_POSITIONS: { pos: OverlayPosition; arrow: string; row: number; col: number }[] = [
  { pos: 'top_left',      arrow: '↖', row: 0, col: 0 },
  { pos: 'top_center',    arrow: '↑', row: 0, col: 1 },
  { pos: 'top_right',     arrow: '↗', row: 0, col: 2 },
  { pos: 'center',        arrow: '·', row: 1, col: 1 },
  { pos: 'bottom_left',   arrow: '↙', row: 2, col: 0 },
  { pos: 'bottom_center', arrow: '↓', row: 2, col: 1 },
  { pos: 'bottom_right',  arrow: '↘', row: 2, col: 2 },
]

const IMPORTANCE_STYLES: Record<Importance, { label: string; cls: string }> = {
  must:   { label: 'Must',   cls: 'bg-red-500/20 text-red-400 border-red-500/30' },
  should: { label: 'Should', cls: 'bg-amber-500/20 text-amber-400 border-amber-500/30' },
  could:  { label: 'Could',  cls: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  would:  { label: 'Would',  cls: 'bg-white/8 text-white/35 border-white/10' },
}

const ROLE_META: Record<OverlayRole, { label: string; cls: string }> = {
  label:      { label: 'Label',   cls: 'bg-blue-500/15 text-blue-400' },
  fact:       { label: 'Fact',    cls: 'bg-purple-500/15 text-purple-400' },
  chapter:    { label: 'Chapter', cls: 'bg-indigo-500/20 text-indigo-400' },
  annotation: { label: 'Note',    cls: 'bg-amber-500/15 text-amber-400' },
  cta:        { label: 'CTA',     cls: 'bg-green-500/15 text-green-400' },
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function useDebounce<T>(value: T, ms: number): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), ms)
    return () => clearTimeout(t)
  }, [value, ms])
  return debounced
}

function formatTime(s: number): string {
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

function parseTime(v: string): number {
  if (v.includes(':')) {
    const [m, s] = v.split(':').map(Number)
    return (m || 0) * 60 + (s || 0)
  }
  return parseFloat(v) || 0
}

// ─── OverlayBadge ─────────────────────────────────────────────────────────────

function OverlayBadge({ checkpoint, style }: { checkpoint: Checkpoint; style: Style }) {
  const s = STYLE_PRESETS[style]
  if (!checkpoint.text) return null

  if (checkpoint.role === 'chapter') {
    return (
      <div style={{ position: 'absolute', ...POSITION_CSS['center'], width: '90%', pointerEvents: 'none', textAlign: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.3)' }} />
          <div style={{ color: s.text, fontWeight: 600, fontSize: `${s.sizeEm * 0.85}rem`, backgroundColor: s.bg, padding: '4px 12px', borderRadius: '20px', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
            {checkpoint.text}
          </div>
          <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.3)' }} />
        </div>
        {checkpoint.sub_text && (
          <div style={{ color: s.sub, fontSize: `${s.sizeEm * 0.62}rem`, marginTop: '6px' }}>{checkpoint.sub_text}</div>
        )}
      </div>
    )
  }

  const posStyle = checkpoint.template === 'lower_third'
    ? { bottom: '12%', left: 0, right: 0, pointerEvents: 'none' as const }
    : { ...POSITION_CSS[checkpoint.position], pointerEvents: 'none' as const }

  return (
    <div style={{ position: 'absolute', ...posStyle }}>
      {checkpoint.template === 'lower_third' ? (
        <div style={{ background: `linear-gradient(to right, ${s.bg} 0%, transparent 100%)`, padding: '6px 16px', borderLeft: `4px solid ${s.text}` }}>
          <div style={{ color: s.text, fontWeight: 700, fontSize: `${s.sizeEm * 0.82}rem` }}>{checkpoint.text}</div>
          {checkpoint.sub_text && <div style={{ color: s.sub, fontSize: `${s.sizeEm * 0.62}rem`, marginTop: '2px' }}>{checkpoint.sub_text}</div>}
        </div>
      ) : (
        <div style={{ backgroundColor: s.bg, borderRadius: '4px', padding: '4px 8px', maxWidth: '85%', whiteSpace: 'nowrap' }}>
          <div style={{ color: s.text, fontWeight: s.bold ? 700 : 400, fontSize: `${s.sizeEm * 0.78}rem`, lineHeight: 1.2 }}>{checkpoint.text}</div>
          {checkpoint.sub_text && <div style={{ color: s.sub, fontSize: `${s.sizeEm * 0.62}rem`, marginTop: '2px', lineHeight: 1.2 }}>{checkpoint.sub_text}</div>}
        </div>
      )}
    </div>
  )
}

// ─── FramePreview ─────────────────────────────────────────────────────────────

function FramePreview({ jobId, checkpoint, style }: { jobId: string; checkpoint: Checkpoint; style: Style }) {
  const debouncedTs = useDebounce(checkpoint.timestamp, 350)
  const [src, setSrc] = useState('')
  const [loaded, setLoaded] = useState(false)
  const [errored, setErrored] = useState(false)
  const prevSrc = useRef('')

  useEffect(() => {
    const next = `http://localhost:8000/frame/${jobId}?t=${Math.max(0, debouncedTs).toFixed(2)}`
    if (next !== prevSrc.current) {
      prevSrc.current = next
      setLoaded(false)
      setErrored(false)
      setSrc(next)
    }
  }, [jobId, debouncedTs])

  return (
    <div className="relative w-full bg-black rounded-lg overflow-hidden" style={{ aspectRatio: '16/9' }}>
      {!loaded && !errored && <div className="absolute inset-0 flex items-center justify-center"><div className="w-5 h-5 border-2 border-white/20 border-t-white/60 rounded-full animate-spin" /></div>}
      {errored && <div className="absolute inset-0 flex items-center justify-center text-white/20 text-xs">no frame</div>}
      {src && <img src={src} alt="" className="w-full h-full object-contain" style={{ display: loaded ? 'block' : 'none' }} onLoad={() => setLoaded(true)} onError={() => { setLoaded(false); setErrored(true) }} />}
      {loaded && <OverlayBadge checkpoint={checkpoint} style={style} />}
    </div>
  )
}

// ─── PositionPicker ───────────────────────────────────────────────────────────

function PositionPicker({ value, onChange }: { value: OverlayPosition; onChange: (p: OverlayPosition) => void }) {
  return (
    <div className="inline-grid grid-cols-3 gap-1">
      {Array.from({ length: 9 }, (_, i) => {
        const row = Math.floor(i / 3), col = i % 3
        const match = GRID_POSITIONS.find(p => p.row === row && p.col === col)
        if (!match) return <div key={i} className="w-7 h-7" />
        const active = value === match.pos
        return (
          <button key={match.pos} title={POSITION_LABELS[match.pos]} onClick={() => onChange(match.pos)}
            className={`w-7 h-7 rounded text-sm font-mono flex items-center justify-center transition-colors ${active ? 'bg-indigo-500 text-white' : 'bg-white/8 hover:bg-white/15 text-white/50 hover:text-white/80'}`}>
            {match.arrow}
          </button>
        )
      })}
    </div>
  )
}

// ─── ConfidenceBadge ──────────────────────────────────────────────────────────

function ConfidenceBadge({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100)
  const cls = confidence >= 0.85
    ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25'
    : confidence >= 0.65
      ? 'bg-amber-500/15 text-amber-400 border-amber-500/25'
      : 'bg-red-500/15 text-red-400 border-red-500/25'
  return (
    <span className={`text-xs px-1.5 py-0.5 rounded border font-medium ${cls}`} title="AI confidence in this overlay's accuracy">
      {pct}%
    </span>
  )
}

// ─── CheckpointCard ───────────────────────────────────────────────────────────

function CheckpointCard({ cp, index, jobId, style, onUpdate, onRemove }: {
  cp: Checkpoint; index: number; jobId: string; style: Style
  onUpdate: (patch: Partial<Checkpoint>) => void; onRemove: () => void
}) {
  const [altsOpen, setAltsOpen] = useState(false)
  const isChapter = cp.role === 'chapter'
  const roleMeta = ROLE_META[cp.role]
  const importanceOrder: Importance[] = ['must', 'should', 'could', 'would']
  const templateOrder: OverlayTemplate[] = ['corner_badge', 'lower_third', 'chyron', 'cinematic_title', 'pill']
  const alternatives = cp.alternatives ?? []
  const confidence = cp.confidence ?? 0.8

  function swapWithAlternative(alt: CheckpointAlternative) {
    onUpdate({
      text: alt.text,
      sub_text: alt.sub_text,
      role: alt.role,
      template: alt.template,
      confidence: alt.confidence,
      rationale: alt.rationale ?? null,
      alternatives: [
        // put the current main back as an alternative
        { text: cp.text, sub_text: cp.sub_text, role: cp.role, template: cp.template, confidence: cp.confidence ?? 0.8, rationale: cp.rationale ?? null },
        ...alternatives.filter(a => a.text !== alt.text),
      ],
    })
    setAltsOpen(false)
  }

  return (
    <div className={`rounded-xl overflow-hidden border ${isChapter ? 'bg-indigo-500/5 border-indigo-500/20' : 'bg-white/5 border-white/8'}`}>
      <div className="flex">
        <div className="flex-1 p-4 min-w-0">
          <div className="flex items-center gap-2 mb-3 flex-wrap">
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-white/40">@</span>
              <input type="text" value={formatTime(cp.timestamp)} onChange={e => onUpdate({ timestamp: parseTime(e.target.value) })}
                className="w-14 rounded-lg px-2 py-1 text-xs text-center focus:outline-none focus:ring-1 focus:ring-indigo-500/60 bg-white/8 border border-white/12" title="Start time (M:SS)" />
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-white/40">for</span>
              <input type="number" min={1} max={30} step={0.5} value={cp.duration} onChange={e => onUpdate({ duration: parseFloat(e.target.value) || 4 })}
                className="w-14 rounded-lg px-2 py-1 text-xs text-center focus:outline-none focus:ring-1 focus:ring-indigo-500/60 bg-white/8 border border-white/12" title="Duration (s)" />
              <span className="text-xs text-white/40">s</span>
            </div>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${roleMeta.cls}`}>{roleMeta.label}</span>
            {(() => {
              const imp = cp.importance ?? 'should'
              const { label, cls } = IMPORTANCE_STYLES[imp]
              return (
                <button title="Click to change importance" onClick={() => onUpdate({ importance: importanceOrder[(importanceOrder.indexOf(imp) + 1) % importanceOrder.length] })}
                  className={`text-xs px-2 py-0.5 rounded-full border font-medium transition-colors ${cls}`}>{label}</button>
              )
            })()}
            {!isChapter && (
              <button title="Click to change template" onClick={() => onUpdate({ template: templateOrder[(templateOrder.indexOf(cp.template) + 1) % templateOrder.length] })}
                className="text-xs px-2 py-0.5 rounded-full border border-white/10 bg-white/6 text-white/35 hover:text-white/55 transition-colors">
                {cp.template.replace('_', ' ')}
              </button>
            )}
            <ConfidenceBadge confidence={confidence} />
            <div className="flex-1" />
            {cp.source_url && (
              <a href={cp.source_url} target="_blank" rel="noopener noreferrer" className="text-xs text-indigo-400/60 hover:text-indigo-400 transition-colors" title="Source">↗ wiki</a>
            )}
            <button onClick={onRemove} className="text-white/25 hover:text-red-400 transition-colors text-sm px-1" title="Remove">✕</button>
          </div>
          <div className="space-y-2 mb-3">
            <input type="text" value={cp.text} onChange={e => onUpdate({ text: e.target.value })} placeholder="Main label (max 6 words)"
              className="w-full rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500/60 bg-white/8 border border-white/12 placeholder-white/20" />
            <input type="text" value={cp.sub_text ?? ''} onChange={e => onUpdate({ sub_text: e.target.value || null })} placeholder="Optional sub-text / fact — leave blank to skip"
              className="w-full rounded-lg px-3 py-2 text-xs text-white/70 focus:outline-none focus:ring-1 focus:ring-indigo-500/60 bg-white/8 border border-white/12 placeholder-white/20" />
          </div>
          {!isChapter && cp.template !== 'chyron' && (
            <div className="flex items-center gap-3">
              <span className="text-xs text-white/40 shrink-0">Position</span>
              <PositionPicker value={cp.position} onChange={pos => onUpdate({ position: pos })} />
              <span className="text-xs text-white/30">{POSITION_LABELS[cp.position]}</span>
            </div>
          )}
          {cp.rationale && (
            <div className="mt-3 pt-3 border-t border-white/6 flex gap-2">
              <span className="text-xs text-indigo-400/60 shrink-0 mt-px">AI:</span>
              <p className="text-xs text-white/35 italic leading-relaxed">{cp.rationale}</p>
            </div>
          )}

          {/* Alternatives panel */}
          {alternatives.length > 0 && (
            <div className="mt-3 pt-3 border-t border-white/6">
              <button onClick={() => setAltsOpen(o => !o)}
                className="flex items-center gap-1.5 text-xs text-white/30 hover:text-white/50 transition-colors">
                <span>{altsOpen ? '▼' : '▶'}</span>
                <span>{alternatives.length} alternative{alternatives.length !== 1 ? 's' : ''}</span>
              </button>
              {altsOpen && (
                <div className="mt-2 space-y-2">
                  {alternatives.map((alt, ai) => (
                    <div key={ai} className="flex items-start gap-2 p-2.5 rounded-lg bg-white/4 border border-white/8">
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-white/75 font-medium truncate">{alt.text}</p>
                        {alt.sub_text && <p className="text-xs text-white/40 mt-0.5 truncate">{alt.sub_text}</p>}
                        <div className="flex items-center gap-1.5 mt-1">
                          <span className={`text-xs px-1.5 py-0.5 rounded ${ROLE_META[alt.role]?.cls ?? ''}`}>{alt.role}</span>
                          <ConfidenceBadge confidence={alt.confidence} />
                          {alt.rationale && <span className="text-xs text-white/25 truncate">{alt.rationale}</span>}
                        </div>
                      </div>
                      <button onClick={() => swapWithAlternative(alt)}
                        className="shrink-0 text-xs px-2 py-1 rounded-lg bg-indigo-500/15 hover:bg-indigo-500/25 text-indigo-400 transition-colors">
                        Use this
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
        <div className="w-56 shrink-0 p-3 flex items-start border-l border-white/6">
          <FramePreview jobId={jobId} checkpoint={cp} style={style} />
        </div>
      </div>
    </div>
  )
}

// ─── LayerSection ─────────────────────────────────────────────────────────────

function LayerSection({ title, count, enabled, onToggle, children, accent = false }: {
  title: string; count: number; enabled: boolean; onToggle: () => void; children: React.ReactNode; accent?: boolean
}) {
  return (
    <div className="mb-8">
      <div className="flex items-center gap-3 mb-3">
        <button onClick={onToggle} className={`w-10 h-5 rounded-full transition-colors relative shrink-0 ${enabled ? (accent ? 'bg-indigo-500' : 'bg-emerald-500') : 'bg-white/15'}`}>
          <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${enabled ? 'translate-x-5' : 'translate-x-0.5'}`} />
        </button>
        <h3 className={`text-sm font-semibold ${enabled ? 'text-white/90' : 'text-white/30'}`}>{title}</h3>
        <span className="text-xs text-white/30">{count} overlay{count !== 1 ? 's' : ''}</span>
      </div>
      <div className={`space-y-4 ${enabled ? '' : 'opacity-30 pointer-events-none'}`}>{children}</div>
    </div>
  )
}

// ─── RegenerateBar ────────────────────────────────────────────────────────────

function RegenerateBar({ label, loading, onRegenerate }: {
  label: string; loading: boolean; onRegenerate: (feedback: string) => void
}) {
  const [open, setOpen] = useState(false)
  const [feedback, setFeedback] = useState('')

  return (
    <div className="mb-6 rounded-xl border border-white/8 bg-white/3 overflow-hidden">
      <button onClick={() => setOpen(o => !o)} disabled={loading}
        className="w-full flex items-center justify-between px-4 py-3 text-sm text-white/50 hover:text-white/70 transition-colors disabled:opacity-50">
        <span className="flex items-center gap-2">
          {loading ? <span className="w-3.5 h-3.5 border border-indigo-400 border-t-transparent rounded-full animate-spin inline-block" /> : <span className="text-indigo-400">✦</span>}
          {loading ? 'Regenerating...' : label}
        </span>
        <span className="text-xs text-white/25">{open ? '▲' : '▼'}</span>
      </button>
      {open && !loading && (
        <div className="border-t border-white/8 p-4">
          <p className="text-xs text-white/40 mb-2">Optional: tell the AI what to improve</p>
          <textarea value={feedback} onChange={e => setFeedback(e.target.value)}
            placeholder='e.g. "focus more on historical context" or "make quiz questions harder"'
            rows={2}
            className="w-full rounded-lg px-3 py-2 text-sm bg-white/6 border border-white/12 text-white/80 placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-indigo-500/60 resize-none mb-3" />
          <button onClick={() => { onRegenerate(feedback); setOpen(false) }}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors">
            Regenerate now
          </button>
        </div>
      )}
    </div>
  )
}

// ─── SectionEditor ────────────────────────────────────────────────────────────

function SectionEditor({ section, index, onUpdate, onRemove }: {
  section: LearningSection; index: number
  onUpdate: (patch: Partial<LearningSection>) => void; onRemove: () => void
}) {
  const [ddOpen, setDdOpen] = useState(false)
  const [summaryDepth, setSummaryDepth] = useState<'default' | 'concise' | 'detailed'>('default')

  const hasDepthVariants = !!(section.summary_concise || section.summary_detailed)
  const displayedSummary =
    summaryDepth === 'concise' && section.summary_concise ? section.summary_concise
    : summaryDepth === 'detailed' && section.summary_detailed ? section.summary_detailed
    : section.summary

  return (
    <div className="rounded-xl border border-white/8 bg-white/3 overflow-hidden">
      <div className="p-4">
        {/* Header */}
        <div className="flex items-center gap-3 mb-3">
          <span className="text-xs text-indigo-400/70 bg-indigo-500/10 px-2 py-0.5 rounded-full font-medium shrink-0">
            {formatTime(section.start)} – {formatTime(section.end)}
          </span>
          <input type="text" value={section.title} onChange={e => onUpdate({ title: e.target.value })}
            placeholder="Section title"
            className="flex-1 rounded-lg px-3 py-1.5 text-sm font-semibold bg-white/6 border border-white/10 text-white focus:outline-none focus:ring-1 focus:ring-indigo-500/60 placeholder-white/20" />
          <button onClick={onRemove} className="text-white/25 hover:text-red-400 transition-colors px-1 shrink-0" title="Remove section">✕</button>
        </div>

        {/* Summary with depth toggle */}
        <div className="mb-3">
          {hasDepthVariants && (
            <div className="flex gap-1 mb-2">
              {(['concise', 'default', 'detailed'] as const).map(d => (
                <button key={d} onClick={() => setSummaryDepth(d)}
                  className={`text-xs px-2 py-0.5 rounded transition-colors ${summaryDepth === d ? 'bg-indigo-500/20 text-indigo-400' : 'text-white/30 hover:text-white/50'}`}>
                  {d === 'default' ? 'standard' : d}
                </button>
              ))}
            </div>
          )}
          <textarea value={displayedSummary}
            onChange={e => {
              if (summaryDepth === 'concise') onUpdate({ summary_concise: e.target.value })
              else if (summaryDepth === 'detailed') onUpdate({ summary_detailed: e.target.value })
              else onUpdate({ summary: e.target.value })
            }}
            placeholder="What happens in this section and why it matters..."
            rows={2}
            className="w-full rounded-lg px-3 py-2 text-sm bg-white/6 border border-white/10 text-white/80 placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-indigo-500/60 resize-none" />
        </div>

        {/* Key facts */}
        <p className="text-xs text-white/35 uppercase tracking-wider mb-2">Key Facts</p>
        <div className="space-y-1.5 mb-2">
          {section.key_facts.map((fact, fi) => (
            <div key={fi} className="flex items-center gap-2">
              <span className="text-indigo-400 text-xs shrink-0">◆</span>
              <input type="text" value={fact}
                onChange={e => onUpdate({ key_facts: section.key_facts.map((f, i) => i === fi ? e.target.value : f) })}
                className="flex-1 rounded-lg px-3 py-1.5 text-sm bg-white/6 border border-white/10 text-white/80 focus:outline-none focus:ring-1 focus:ring-indigo-500/60 placeholder-white/20"
                placeholder="Specific fact with a number, date, or name..." />
              <button onClick={() => onUpdate({ key_facts: section.key_facts.filter((_, i) => i !== fi) })}
                className="text-white/20 hover:text-red-400 transition-colors text-sm px-1 shrink-0">✕</button>
            </div>
          ))}
        </div>
        <button onClick={() => onUpdate({ key_facts: [...section.key_facts, ''] })}
          className="text-xs text-white/35 hover:text-white/55 transition-colors mb-3">+ Add fact</button>

        {/* Deep dive toggle */}
        <button onClick={() => setDdOpen(o => !o)}
          className="flex items-center gap-1.5 text-xs text-white/35 hover:text-white/55 transition-colors mb-2">
          <span>{ddOpen ? '▼' : '▶'}</span> Deep dive
        </button>
        {ddOpen && (
          <textarea value={section.deep_dive} onChange={e => onUpdate({ deep_dive: e.target.value })}
            placeholder="Extra context for curious viewers..."
            rows={2}
            className="w-full rounded-lg px-3 py-2 text-sm bg-white/6 border border-white/10 text-white/70 placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-indigo-500/60 resize-none mb-3" />
        )}

        {/* Links */}
        {section.links.length > 0 && (
          <div className="space-y-1.5 mb-2">
            {section.links.map((link, li) => (
              <div key={li} className="flex items-center gap-2">
                <span className="text-xs text-white/25 shrink-0">↗</span>
                <input type="text" value={link.text}
                  onChange={e => onUpdate({ links: section.links.map((l, i) => i === li ? { ...l, text: e.target.value } : l) })}
                  placeholder="Label" className="w-28 rounded-lg px-2 py-1.5 text-xs bg-white/6 border border-white/10 text-white/70 focus:outline-none focus:ring-1 focus:ring-indigo-500/60 placeholder-white/20" />
                <input type="text" value={link.url}
                  onChange={e => onUpdate({ links: section.links.map((l, i) => i === li ? { ...l, url: e.target.value } : l) })}
                  placeholder="https://..." className="flex-1 rounded-lg px-2 py-1.5 text-xs bg-white/6 border border-white/10 text-white/50 focus:outline-none focus:ring-1 focus:ring-indigo-500/60 placeholder-white/20" />
                <button onClick={() => onUpdate({ links: section.links.filter((_, i) => i !== li) })}
                  className="text-white/20 hover:text-red-400 transition-colors text-sm px-1 shrink-0">✕</button>
              </div>
            ))}
          </div>
        )}
        <button onClick={() => onUpdate({ links: [...section.links, { text: '', url: '' }] })}
          className="text-xs text-white/35 hover:text-white/55 transition-colors">+ Add reference link</button>
      </div>
    </div>
  )
}

// ─── QuizEditor ───────────────────────────────────────────────────────────────

function QuizCard({ qp, index, onUpdate, onRemove }: {
  qp: QuizPoint; index: number
  onUpdate: (patch: Partial<QuizPoint>) => void; onRemove: () => void
}) {
  const diffColors = { easy: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20', medium: 'text-amber-400 bg-amber-500/10 border-amber-500/20', hard: 'text-red-400 bg-red-500/10 border-red-500/20' }
  const diffs: QuizPoint['difficulty'][] = ['easy', 'medium', 'hard']
  const [variantMode, setVariantMode] = useState<'standard' | 'easier' | 'harder'>('standard')

  const hasVariants = !!(qp.easier_version || qp.harder_version)
  const displayedQuestion =
    variantMode === 'easier' && qp.easier_version ? qp.easier_version
    : variantMode === 'harder' && qp.harder_version ? qp.harder_version
    : qp.question

  return (
    <div className="rounded-xl border border-white/8 bg-white/3 overflow-hidden">
      <div className="p-4">
        {/* Header */}
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs text-white/40 bg-white/6 px-2 py-0.5 rounded-full">Q{index + 1}</span>
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-white/30">@</span>
            <input type="text" value={formatTime(qp.timestamp)} onChange={e => onUpdate({ timestamp: parseTime(e.target.value) })}
              className="w-14 rounded-lg px-2 py-1 text-xs text-center focus:outline-none focus:ring-1 focus:ring-indigo-500/60 bg-white/8 border border-white/12" title="When to pause (M:SS)" />
          </div>
          <button onClick={() => onUpdate({ difficulty: diffs[(diffs.indexOf(qp.difficulty) + 1) % diffs.length] })}
            className={`text-xs px-2 py-0.5 rounded-full border font-medium transition-colors ${diffColors[qp.difficulty]}`}>
            {qp.difficulty}
          </button>
          <div className="flex-1" />
          <button onClick={onRemove} className="text-white/25 hover:text-red-400 transition-colors px-1 text-sm">✕</button>
        </div>

        {/* Question with variant toggle */}
        <div className="mb-3">
          {hasVariants && (
            <div className="flex gap-1 mb-2">
              {(['easier', 'standard', 'harder'] as const).map(v => {
                const available = v === 'standard' || (v === 'easier' && qp.easier_version) || (v === 'harder' && qp.harder_version)
                return (
                  <button key={v} onClick={() => available && setVariantMode(v)} disabled={!available}
                    className={`text-xs px-2 py-0.5 rounded transition-colors
                      ${variantMode === v ? 'bg-indigo-500/20 text-indigo-400' : available ? 'text-white/30 hover:text-white/50' : 'text-white/15 cursor-not-allowed'}`}>
                    {v}
                  </button>
                )
              })}
            </div>
          )}
          <textarea value={displayedQuestion}
            onChange={e => {
              if (variantMode === 'easier') onUpdate({ easier_version: e.target.value })
              else if (variantMode === 'harder') onUpdate({ harder_version: e.target.value })
              else onUpdate({ question: e.target.value })
            }}
            placeholder="What question will pause the video here?"
            rows={2}
            className="w-full rounded-lg px-3 py-2 text-sm bg-white/6 border border-white/10 text-white/80 placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-indigo-500/60 resize-none" />
        </div>

        {/* Options */}
        <p className="text-xs text-white/35 uppercase tracking-wider mb-2">Options — click radio to mark correct</p>
        <div className="space-y-1.5 mb-3">
          {qp.options.map((opt, oi) => (
            <div key={oi} className="flex items-center gap-2">
              <button onClick={() => onUpdate({ correct_index: oi })}
                className={`w-5 h-5 rounded-full border-2 shrink-0 flex items-center justify-center transition-colors ${oi === qp.correct_index ? 'border-emerald-400 bg-emerald-400' : 'border-white/20 bg-transparent hover:border-white/40'}`}>
                {oi === qp.correct_index && <span className="w-2 h-2 rounded-full bg-white block" />}
              </button>
              <span className="text-xs text-white/30 shrink-0 w-4">{String.fromCharCode(65 + oi)}.</span>
              <input type="text" value={opt} onChange={e => onUpdate({ options: qp.options.map((o, i) => i === oi ? e.target.value : o) })}
                className={`flex-1 rounded-lg px-3 py-1.5 text-sm bg-white/6 border text-white/80 focus:outline-none focus:ring-1 focus:ring-indigo-500/60 ${oi === qp.correct_index ? 'border-emerald-500/30' : 'border-white/10'}`}
                placeholder={`Option ${String.fromCharCode(65 + oi)}`} />
            </div>
          ))}
        </div>

        {/* Explanation */}
        <textarea value={qp.explanation} onChange={e => onUpdate({ explanation: e.target.value })}
          placeholder="Why is this correct? What should viewers take away?"
          rows={2}
          className="w-full rounded-lg px-3 py-2 text-sm bg-white/6 border border-white/10 text-white/70 placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-indigo-500/60 resize-none mb-2" />

        {/* Hint */}
        <input type="text" value={qp.hint} onChange={e => onUpdate({ hint: e.target.value })}
          placeholder="Optional hint (shown if viewer asks)"
          className="w-full rounded-lg px-3 py-1.5 text-xs bg-white/6 border border-white/10 text-white/50 placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-indigo-500/60" />
      </div>
    </div>
  )
}

// ─── Main component ────────────────────────────────────────────────────────────

type TabId = 'overlays' | 'sidepanel' | 'quiz'

export default function StepReview({
  upload, config, checkpoints: initialCheckpoints,
  summary: initialSummary, sourceUrls: initialSourceUrls,
  learningScript: initialLearningScript,
  onComplete, onBack,
}: Props) {
  const [tab, setTab] = useState<TabId>('overlays')

  // Overlays state
  const [contentItems, setContentItems] = useState<Checkpoint[]>(
    initialCheckpoints.filter(c => c.layer !== 'chapters').map(cp => ({ ...cp }))
  )
  const [chapterItems, setChapterItems] = useState<Checkpoint[]>(
    initialCheckpoints.filter(c => c.layer === 'chapters').map(cp => ({ ...cp }))
  )
  const [contentEnabled, setContentEnabled] = useState(true)
  const [chaptersEnabled, setChaptersEnabled] = useState(true)
  const [summary, setSummary] = useState(initialSummary)
  const [sourceUrls, setSourceUrls] = useState(initialSourceUrls)

  // Learning script state
  const [learningScript, setLearningScript] = useState<LearningScript>(initialLearningScript)

  // Regenerate state
  const [regenLoading, setRegenLoading] = useState(false)
  const [regenError, setRegenError] = useState('')

  function updateContent(index: number, patch: Partial<Checkpoint>) {
    setContentItems(prev => prev.map((cp, i) => i === index ? { ...cp, ...patch } : cp))
  }
  function updateChapter(index: number, patch: Partial<Checkpoint>) {
    setChapterItems(prev => prev.map((cp, i) => i === index ? { ...cp, ...patch } : cp))
  }

  function updateSection(index: number, patch: Partial<LearningSection>) {
    setLearningScript(prev => ({
      ...prev,
      sections: prev.sections.map((s, i) => i === index ? { ...s, ...patch } : s),
    }))
  }
  function updateQuiz(index: number, patch: Partial<QuizPoint>) {
    setLearningScript(prev => ({
      ...prev,
      quiz_points: prev.quiz_points.map((q, i) => i === index ? { ...q, ...patch } : q),
    }))
  }

  function addCheckpoint() {
    const all = [...contentItems, ...chapterItems]
    const lastTs = all.length > 0 ? Math.max(...all.map(c => c.timestamp)) + 10 : 5
    setContentItems(prev => [...prev, {
      timestamp: Math.round(Math.min(lastTs, upload.duration - 5)),
      duration: 4, text: 'New checkpoint', sub_text: null,
      position: 'bottom_left' as OverlayPosition, rationale: null,
      importance: 'should' as const, role: 'label' as OverlayRole,
      template: 'corner_badge' as OverlayTemplate, layer: 'content', source_url: null,
    }])
  }

  function addQuizPoint() {
    const lastTs = learningScript.quiz_points.length > 0
      ? Math.max(...learningScript.quiz_points.map(q => q.timestamp)) + 60
      : 30
    setLearningScript(prev => ({
      ...prev,
      quiz_points: [...prev.quiz_points, {
        timestamp: Math.min(lastTs, upload.duration - 5),
        question: '', options: ['', '', '', ''], correct_index: 0,
        explanation: '', hint: '', difficulty: 'medium', related_fact: '',
      }],
    }))
  }

  async function handleRegenerateOverlays(feedback: string) {
    setRegenLoading(true)
    setRegenError('')
    try {
      const res = await fetch(`http://localhost:8000/regenerate/${upload.job_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback }),
      })
      if (!res.ok) {
        let msg = `Server error ${res.status}`
        try { const err = await res.json(); msg = err.detail || msg } catch { /* ignore */ }
        throw new Error(msg)
      }
      const data = await res.json()
      const all: Checkpoint[] = data.checkpoints as Checkpoint[]
      setContentItems(all.filter((c: Checkpoint) => c.layer !== 'chapters').map((cp: Checkpoint) => ({ ...cp })))
      setChapterItems(all.filter((c: Checkpoint) => c.layer === 'chapters').map((cp: Checkpoint) => ({ ...cp })))
      setSummary(data.summary || '')
      setSourceUrls(data.source_urls || {})
      setLearningScript(data.learning_script || { title: '', sections: [], quiz_points: [] })
    } catch (e) {
      setRegenError(e instanceof Error ? e.message : 'Regeneration failed')
    } finally {
      setRegenLoading(false)
    }
  }

  async function handleRegenerateLearning(feedback: string) {
    setRegenLoading(true)
    setRegenError('')
    try {
      const res = await fetch(`http://localhost:8000/regenerate-learning/${upload.job_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback }),
      })
      if (!res.ok) {
        let msg = `Server error ${res.status}`
        try { const err = await res.json(); msg = err.detail || msg } catch { /* ignore */ }
        throw new Error(msg)
      }
      const data = await res.json()
      setLearningScript(data.learning_script || { title: '', sections: [], quiz_points: [] })
    } catch (e) {
      setRegenError(e instanceof Error ? e.message : 'Learning regeneration failed')
    } finally {
      setRegenLoading(false)
    }
  }

  function handleComplete() {
    const all: Checkpoint[] = [
      ...(contentEnabled ? contentItems : []),
      ...(chaptersEnabled ? chapterItems : []),
    ]
    onComplete(all, learningScript)
  }

  const totalEnabled =
    (contentEnabled ? contentItems.length : 0) +
    (chaptersEnabled ? chapterItems.length : 0)

  const tabs: { id: TabId; label: string; count?: number }[] = [
    { id: 'overlays', label: 'Overlays', count: totalEnabled },
    { id: 'sidepanel', label: 'Side Panel', count: learningScript.sections.length },
    { id: 'quiz', label: 'Quiz', count: learningScript.quiz_points.length },
  ]

  return (
    <div>
      {/* Header */}
      <div className="mb-5">
        <h2 className="text-2xl font-bold text-white mb-1">Review & edit</h2>
        <p className="text-white/50 text-sm">
          AI generated {initialCheckpoints.length} overlay{initialCheckpoints.length !== 1 ? 's' : ''} and {initialLearningScript.quiz_points.length} quiz question{initialLearningScript.quiz_points.length !== 1 ? 's' : ''}.
          Edit anything, then generate.
        </p>
      </div>

      {/* AI summary */}
      {summary && (
        <div className="mb-5 p-4 rounded-xl bg-indigo-500/8 border border-indigo-500/20">
          <p className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-2">AI understood your video as</p>
          <textarea value={summary} onChange={e => setSummary(e.target.value)} rows={3}
            className="w-full bg-transparent text-sm text-white/75 leading-relaxed focus:outline-none resize-none" />
          {Object.keys(sourceUrls).length > 0 && (
            <div className="mt-2 flex flex-wrap gap-2 pt-2 border-t border-indigo-500/15">
              {Object.entries(sourceUrls).map(([place, url]) => (
                <a key={place} href={url} target="_blank" rel="noopener noreferrer"
                  className="text-xs text-indigo-400/60 hover:text-indigo-400 underline underline-offset-2 transition-colors">
                  {place} ↗
                </a>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab bar */}
      <div className="flex gap-1 mb-5 p-1 rounded-xl bg-white/5 border border-white/8">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-1.5
              ${tab === t.id ? 'bg-indigo-600 text-white' : 'text-white/45 hover:text-white/65'}`}>
            {t.label}
            {t.count !== undefined && (
              <span className={`text-xs px-1.5 py-0.5 rounded-full ${tab === t.id ? 'bg-white/20 text-white' : 'bg-white/8 text-white/35'}`}>
                {t.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Error banner */}
      {regenError && (
        <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400 flex items-center justify-between">
          {regenError}
          <button onClick={() => setRegenError('')} className="text-red-400/60 hover:text-red-400 ml-4">✕</button>
        </div>
      )}

      {/* ── Overlays tab ── */}
      {tab === 'overlays' && (
        <div className={regenLoading ? 'opacity-50 pointer-events-none' : ''}>
          <RegenerateBar label="Regenerate overlays with AI" loading={regenLoading} onRegenerate={handleRegenerateOverlays} />

          <LayerSection title="Content Overlays" count={contentItems.length} enabled={contentEnabled} onToggle={() => setContentEnabled(e => !e)}>
            {contentItems.length === 0
              ? <p className="text-center py-6 text-white/25 text-sm">No content overlays.</p>
              : contentItems.map((cp, i) => (
                <CheckpointCard key={i} cp={cp} index={i} jobId={upload.job_id} style={config.style}
                  onUpdate={patch => updateContent(i, patch)}
                  onRemove={() => setContentItems(prev => prev.filter((_, idx) => idx !== i))} />
              ))
            }
          </LayerSection>

          {chapterItems.length > 0 && (
            <LayerSection title="Chapter Markers" count={chapterItems.length} enabled={chaptersEnabled} onToggle={() => setChaptersEnabled(e => !e)} accent>
              {chapterItems.map((cp, i) => (
                <CheckpointCard key={i} cp={cp} index={i} jobId={upload.job_id} style={config.style}
                  onUpdate={patch => updateChapter(i, patch)}
                  onRemove={() => setChapterItems(prev => prev.filter((_, idx) => idx !== i))} />
              ))}
            </LayerSection>
          )}

          <button onClick={addCheckpoint}
            className="w-full py-2.5 rounded-xl border border-dashed border-white/15 hover:border-white/30 text-white/40 hover:text-white/60 text-sm transition-colors mb-8">
            + Add content overlay
          </button>
        </div>
      )}

      {/* ── Side Panel tab ── */}
      {tab === 'sidepanel' && (
        <div className={regenLoading ? 'opacity-50 pointer-events-none' : ''}>
          <RegenerateBar label="Regenerate side panel content with AI" loading={regenLoading} onRegenerate={handleRegenerateLearning} />

          {learningScript.title && (
            <div className="mb-4 flex items-center gap-3">
              <span className="text-xs text-white/35 uppercase tracking-wider shrink-0">Player title</span>
              <input type="text" value={learningScript.title}
                onChange={e => setLearningScript(prev => ({ ...prev, title: e.target.value }))}
                className="flex-1 rounded-lg px-3 py-2 text-sm bg-white/6 border border-white/10 text-white/80 focus:outline-none focus:ring-1 focus:ring-indigo-500/60" />
            </div>
          )}

          {learningScript.sections.length === 0 ? (
            <div className="text-center py-10 text-white/30 text-sm">
              <p className="mb-3">No sections yet.</p>
              <p className="text-xs text-white/20">Click "Regenerate" above to have the AI generate them,<br />or they were not available for this video.</p>
            </div>
          ) : (
            <div className="space-y-4 mb-6">
              {learningScript.sections.map((s, i) => (
                <SectionEditor key={i} section={s} index={i}
                  onUpdate={patch => updateSection(i, patch)}
                  onRemove={() => setLearningScript(prev => ({ ...prev, sections: prev.sections.filter((_, idx) => idx !== i) }))} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Quiz tab ── */}
      {tab === 'quiz' && (
        <div className={regenLoading ? 'opacity-50 pointer-events-none' : ''}>
          <RegenerateBar label="Regenerate quiz questions with AI" loading={regenLoading} onRegenerate={handleRegenerateLearning} />

          {learningScript.quiz_points.length === 0 ? (
            <div className="text-center py-10 text-white/30 text-sm">
              <p className="mb-3">No quiz questions yet.</p>
              <p className="text-xs text-white/20">Click "Regenerate" above or add one manually below.</p>
            </div>
          ) : (
            <div className="space-y-4 mb-4">
              {learningScript.quiz_points.map((qp, i) => (
                <QuizCard key={i} qp={qp} index={i}
                  onUpdate={patch => updateQuiz(i, patch)}
                  onRemove={() => setLearningScript(prev => ({ ...prev, quiz_points: prev.quiz_points.filter((_, idx) => idx !== i) }))} />
              ))}
            </div>
          )}

          <button onClick={addQuizPoint}
            className="w-full py-2.5 rounded-xl border border-dashed border-white/15 hover:border-white/30 text-white/40 hover:text-white/60 text-sm transition-colors mb-6">
            + Add quiz question
          </button>
        </div>
      )}

      {/* Actions — always visible */}
      <div className="flex gap-3 pt-2 border-t border-white/6 mt-2">
        <button onClick={onBack}
          className="px-5 py-3 rounded-xl bg-white/8 hover:bg-white/12 text-white/60 hover:text-white text-sm font-medium transition-colors">
          Re-analyse
        </button>
        <button onClick={handleComplete} disabled={totalEnabled === 0}
          className="flex-1 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold text-sm transition-colors">
          Generate video → ({totalEnabled} overlay{totalEnabled !== 1 ? 's' : ''})
        </button>
      </div>
    </div>
  )
}
