import { useState } from 'react'
import type { Config, FontSize, ReasoningEffort, Style, UploadResult, VideoFormat } from '../types'

interface Props {
  upload: UploadResult
  onComplete: (config: Config) => void
  onBack: () => void
}

function formatDuration(s: number) {
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return m > 0 ? `${m}m ${sec}s` : `${sec}s`
}

const FORMATS: { value: VideoFormat; icon: string; label: string; desc: string }[] = [
  { value: 'vertical',   icon: '📱', label: 'Vertical',    desc: '9:16 · TikTok, Reels, Shorts' },
  { value: 'horizontal', icon: '🖥️', label: 'Horizontal',  desc: '16:9 · YouTube, presentations' },
  { value: 'square',     icon: '⬛', label: 'Square',      desc: '1:1 · LinkedIn, Instagram' },
]

const STYLES: { value: Style; icon: string; label: string; desc: string }[] = [
  { value: 'clean',     icon: '✨', label: 'Clean',     desc: 'Simple labels, clear typography' },
  { value: 'cinematic', icon: '🎞️', label: 'Cinematic', desc: 'Restrained, elegant wording' },
  { value: 'bold',      icon: '⚡', label: 'Bold',      desc: 'Punchy text, strong energy' },
  { value: 'minimal',   icon: '○',  label: 'Minimal',   desc: 'Short labels only' },
]

const FONT_SIZES: { value: FontSize; label: string; preview: string; desc: string }[] = [
  { value: 'small',  label: 'Small',  preview: 'Aa', desc: 'Subtle, non-distracting' },
  { value: 'medium', label: 'Medium', preview: 'Aa', desc: 'Balanced — default' },
  { value: 'large',  label: 'Large',  preview: 'Aa', desc: 'High visibility' },
]

const MODELS: { value: string; label: string; sublabel: string; desc: string; supportsExtended: boolean }[] = [
  { value: 'claude-haiku-4-5-20251001', label: 'Haiku 4.5',  sublabel: 'Fast',     desc: 'Fastest · Lowest cost',        supportsExtended: false },
  { value: 'claude-sonnet-4-6',         label: 'Sonnet 4.6', sublabel: 'Balanced', desc: 'Best balance · Default',        supportsExtended: true  },
  { value: 'claude-opus-4-7',           label: 'Opus 4.7',   sublabel: 'Powerful', desc: 'Highest quality · Higher cost', supportsExtended: true  },
]

function SelectCard<T extends string>({ value, selected, onSelect, icon, label, desc }: {
  value: T; selected: boolean; onSelect: (v: T) => void
  icon: string; label: string; desc: string
}) {
  return (
    <button onClick={() => onSelect(value)}
      className={`p-4 rounded-xl border text-left transition-all w-full
        ${selected ? 'border-indigo-500 bg-indigo-500/15 text-white' : 'border-white/10 bg-white/3 text-white/70 hover:border-white/25 hover:bg-white/6'}`}>
      <div className="flex items-start gap-3">
        <span className="text-xl mt-0.5">{icon}</span>
        <div>
          <div className="font-medium text-sm">{label}</div>
          <div className="text-xs mt-0.5 opacity-60">{desc}</div>
        </div>
        {selected && <div className="ml-auto mt-0.5 w-4 h-4 rounded-full bg-indigo-500 flex items-center justify-center text-xs text-white flex-shrink-0">✓</div>}
      </div>
    </button>
  )
}

export default function StepConfigure({ upload, onComplete, onBack }: Props) {
  const [videoFormat, setVideoFormat]         = useState<VideoFormat>('horizontal')
  const [style, setStyle]                     = useState<Style>('clean')
  const [fontSize, setFontSize]               = useState<FontSize>('medium')
  const [model, setModel]                     = useState<string>('claude-sonnet-4-6')
  const [reasoningEffort, setReasoningEffort] = useState<ReasoningEffort>('standard')

  const selectedModel = MODELS.find(m => m.value === model)!

  function handleContinue() {
    onComplete({
      video_format: videoFormat,
      style,
      font_size: fontSize,
      model,
      reasoning_effort: reasoningEffort,
    })
  }

  return (
    <div>
      <div className="mb-8 p-4 rounded-xl bg-white/5 border border-white/10 flex items-center gap-3">
        <span className="text-2xl">🎬</span>
        <div className="flex-1 min-w-0">
          <div className="font-medium text-sm text-white truncate">{upload.filename}</div>
          <div className="text-xs text-white/40 mt-0.5">{formatDuration(upload.duration)}</div>
        </div>
        <button onClick={onBack} className="text-xs text-white/30 hover:text-white/60 transition-colors">Change</button>
      </div>

      <h2 className="text-2xl font-bold text-white mb-6">Configure your video</h2>

      <section className="mb-8">
        <h3 className="text-sm font-medium text-white/60 uppercase tracking-wider mb-3">Target format</h3>
        <div className="grid grid-cols-3 gap-2">
          {FORMATS.map(f => <SelectCard key={f.value} {...f} selected={videoFormat === f.value} onSelect={setVideoFormat} />)}
        </div>
      </section>

      <section className="mb-8">
        <h3 className="text-sm font-medium text-white/60 uppercase tracking-wider mb-3">Overlay style</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {STYLES.map(s => <SelectCard key={s.value} {...s} selected={style === s.value} onSelect={setStyle} />)}
        </div>
      </section>

      <section className="mb-8">
        <h3 className="text-sm font-medium text-white/60 uppercase tracking-wider mb-3">Overlay text size</h3>
        <div className="grid grid-cols-3 gap-2">
          {FONT_SIZES.map(f => (
            <button key={f.value} onClick={() => setFontSize(f.value)}
              className={`p-4 rounded-xl border text-center transition-all
                ${fontSize === f.value ? 'border-indigo-500 bg-indigo-500/15 text-white' : 'border-white/10 bg-white/3 text-white/70 hover:border-white/25 hover:bg-white/6'}`}>
              <div className={`font-bold mb-1 ${f.value === 'small' ? 'text-base' : f.value === 'medium' ? 'text-xl' : 'text-3xl'}`}>{f.preview}</div>
              <div className="font-medium text-sm">{f.label}</div>
              <div className="text-xs mt-0.5 opacity-60">{f.desc}</div>
              {fontSize === f.value && <div className="mt-1.5 w-4 h-4 rounded-full bg-indigo-500 flex items-center justify-center text-xs text-white mx-auto">✓</div>}
            </button>
          ))}
        </div>
      </section>

      <section className="mb-8">
        <h3 className="text-sm font-medium text-white/60 uppercase tracking-wider mb-3">AI model</h3>
        <div className="grid grid-cols-3 gap-2">
          {MODELS.map(m => (
            <button key={m.value} onClick={() => {
              setModel(m.value)
              if (!m.supportsExtended) setReasoningEffort('standard')
            }}
              className={`p-4 rounded-xl border text-left transition-all
                ${model === m.value ? 'border-indigo-500 bg-indigo-500/15 text-white' : 'border-white/10 bg-white/3 text-white/70 hover:border-white/25 hover:bg-white/6'}`}>
              <div className="text-xs font-semibold text-white/40 mb-0.5">{m.sublabel}</div>
              <div className="font-semibold text-sm">{m.label}</div>
              <div className="text-xs mt-1 opacity-60 leading-snug">{m.desc}</div>
              {model === m.value && <div className="mt-2 w-4 h-4 rounded-full bg-indigo-500 flex items-center justify-center text-xs text-white">✓</div>}
            </button>
          ))}
        </div>
      </section>

      <section className="mb-8">
        <h3 className="text-sm font-medium text-white/60 uppercase tracking-wider mb-3">Reasoning effort</h3>
        <div className="grid grid-cols-2 gap-2">
          {([
            { value: 'standard' as ReasoningEffort, label: 'Standard', desc: 'Fast, efficient inference' },
            { value: 'extended' as ReasoningEffort, label: 'Extended', desc: 'Deeper analysis, better accuracy' },
          ]).map(r => {
            const disabled = r.value === 'extended' && !selectedModel.supportsExtended
            return (
              <button key={r.value} onClick={() => !disabled && setReasoningEffort(r.value)}
                disabled={disabled}
                className={`p-4 rounded-xl border text-left transition-all
                  ${disabled ? 'opacity-35 cursor-not-allowed border-white/8 bg-white/2' :
                    reasoningEffort === r.value ? 'border-indigo-500 bg-indigo-500/15 text-white' :
                    'border-white/10 bg-white/3 text-white/70 hover:border-white/25 hover:bg-white/6'}`}>
                <div className="font-medium text-sm">{r.label}</div>
                <div className="text-xs mt-0.5 opacity-60">
                  {disabled ? 'Not available for Haiku' : r.desc}
                </div>
                {reasoningEffort === r.value && !disabled && (
                  <div className="mt-2 w-4 h-4 rounded-full bg-indigo-500 flex items-center justify-center text-xs text-white">✓</div>
                )}
              </button>
            )
          })}
        </div>
      </section>

      <button onClick={handleContinue}
        className="w-full py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition-colors">
        Continue →
      </button>
    </div>
  )
}
