import { useEffect, useRef, useState } from 'react'
import type { UploadResult, Config, Checkpoint, LearningScript, TokenUsage } from '../types'

interface Props {
  upload: UploadResult
  config: Config
  checkpoints: Checkpoint[]
  learningScript: LearningScript
  tokenUsage: TokenUsage
  onReset: () => void
}

function formatCost(usd: number): string {
  if (usd < 0.01) return `<$0.01`
  return `$${usd.toFixed(2)}`
}

function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}k`
  return String(n)
}

function modelLabel(id: string): string {
  const m = id.match(/claude-(\w+)-([\d]+)/)
  if (!m) return id
  const family = m[1].charAt(0).toUpperCase() + m[1].slice(1)
  const version = m[2]
  return `${family} ${version}`
}

export default function StepExport({ upload, config, checkpoints, learningScript, tokenUsage, onReset }: Props) {
  const [status, setStatus] = useState('idle')
  const [message, setMessage] = useState('Starting export...')
  const [progress, setProgress] = useState(0)
  const [failed, setFailed] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [done, setDone] = useState(false)
  const started = useRef(false)

  useEffect(() => {
    if (started.current) return
    started.current = true

    async function run() {
      try {
        const res = await fetch(`http://localhost:8000/export/${upload.job_id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ checkpoints, learning_script: learningScript }),
        })
        if (!res.ok) {
          const err = await res.json()
          throw new Error(err.detail || 'Failed to start export')
        }
      } catch (e: unknown) {
        setFailed(true)
        setErrorMessage(e instanceof Error ? e.message : 'Failed to start export.')
        return
      }

      const es = new EventSource(`http://localhost:8000/export-events/${upload.job_id}`)
      es.onmessage = (event) => {
        if (event.data === '[DONE]') {
          es.close()
          return
        }
        try {
          const data = JSON.parse(event.data)
          setStatus(data.status)
          setMessage(data.message)
          setProgress(data.progress)
          if (data.status === 'done') {
            es.close()
            setDone(true)
          } else if (data.status === 'failed') {
            es.close()
            setFailed(true)
            setErrorMessage(data.message || 'Export failed.')
          }
        } catch (e) {
          console.error('SSE parse error (export):', e)
        }
      }
      es.onerror = () => {
        es.close()
        setFailed(true)
        setErrorMessage('Lost connection to the server. Please try again.')
      }
    }

    run()
  }, [upload.job_id, checkpoints])

  function handleDownload() {
    const a = document.createElement('a')
    a.href = `http://localhost:8000/download/${upload.job_id}`
    a.download = 'checkpoint_overlay_result.mp4'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  function handleOpenPlayer() {
    window.open(`http://localhost:8000/player/${upload.job_id}`, '_blank', 'noopener,noreferrer')
  }

  if (failed) {
    return (
      <div className="text-center">
        <div className="w-16 h-16 rounded-2xl bg-red-500/15 flex items-center justify-center text-3xl mx-auto mb-6">❌</div>
        <h2 className="text-2xl font-bold text-white mb-3">Export failed</h2>
        <p className="text-white/50 text-sm mb-8 max-w-md mx-auto">{errorMessage}</p>
        <button
          onClick={onReset}
          className="px-8 py-3 rounded-xl bg-white/10 hover:bg-white/15 text-white text-sm font-medium transition-colors"
        >
          Start over
        </button>
      </div>
    )
  }

  if (done) {
    return (
      <div className="text-center">
        <div className="w-20 h-20 rounded-3xl bg-green-500/15 flex items-center justify-center text-4xl mx-auto mb-8">✅</div>
        <h2 className="text-3xl font-bold text-white mb-3">Your video is ready</h2>
        <p className="text-white/50 text-sm mb-10">
          {checkpoints.length} checkpoint overlay{checkpoints.length !== 1 ? 's' : ''} applied to{' '}
          <span className="text-white/70">{upload.filename}</span>
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={handleOpenPlayer}
            className="px-8 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition-colors flex items-center gap-2 justify-center"
          >
            <span>🎬</span>
            Open Interactive Player
          </button>
          <button
            onClick={handleDownload}
            className="px-8 py-3.5 rounded-xl bg-white/8 hover:bg-white/12 text-white/70 hover:text-white font-medium text-sm transition-colors flex items-center gap-2 justify-center"
          >
            <span>⬇</span>
            Download MP4
          </button>
          <button
            onClick={onReset}
            className="px-8 py-3.5 rounded-xl bg-white/6 hover:bg-white/10 text-white/50 hover:text-white/80 font-medium text-sm transition-colors"
          >
            Process another
          </button>
        </div>

        {tokenUsage.input_tokens > 0 && (
          <div className="mt-6 p-4 rounded-xl bg-white/4 border border-white/8 text-left flex items-center justify-between gap-4">
            <div>
              <p className="text-xs text-white/35 font-medium uppercase tracking-wider mb-1">
                AI usage this session
              </p>
              {tokenUsage.models && tokenUsage.models.length > 0 && (
                <p className="text-xs text-indigo-400/70 mb-1">
                  {tokenUsage.models.map(modelLabel).join(' · ')}
                </p>
              )}
              <p className="text-xs text-white/40">
                {formatTokens(tokenUsage.input_tokens)} in · {formatTokens(tokenUsage.output_tokens)} out
              </p>
            </div>
            <div className="text-right shrink-0">
              <p className="text-lg font-semibold text-white/70">{formatCost(tokenUsage.cost_usd)}</p>
              <p className="text-xs text-white/25">estimated</p>
            </div>
          </div>
        )}

        <div className="mt-4 p-4 rounded-xl bg-indigo-500/8 border border-indigo-500/20 text-left">
          <p className="text-xs text-indigo-300/60 font-medium uppercase tracking-wider mb-2">Interactive Player</p>
          <ul className="text-xs text-white/50 space-y-1">
            <li>• Side panel updates as the video plays — facts, summaries, links</li>
            <li>• Quiz questions pause the video at key moments</li>
            <li>• Click any fact card to copy it to clipboard</li>
          </ul>
        </div>
      </div>
    )
  }

  const statusLabels: Record<string, string> = {
    creating_overlays: 'Rendering overlay images...',
    exporting: 'Running FFmpeg export...',
  }
  const label = statusLabels[status] || message

  return (
    <div className="text-center">
      <div className="w-16 h-16 rounded-2xl bg-indigo-500/15 flex items-center justify-center mx-auto mb-8">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>

      <h2 className="text-2xl font-bold text-white mb-2">Exporting video</h2>
      <p className="text-white/50 text-sm mb-10">
        Applying {checkpoints.length} overlay{checkpoints.length !== 1 ? 's' : ''} and encoding the final MP4.
      </p>

      <div className="mb-4">
        <div className="flex justify-between text-xs text-white/40 mb-2">
          <span>{label}</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="flex justify-center gap-8 mt-8">
        {[
          { key: 'creating_overlays', label: 'Overlays' },
          { key: 'exporting', label: 'FFmpeg' },
          { key: 'done', label: 'Done' },
        ].map(({ key, label: stepLabel }) => {
          const order = ['creating_overlays', 'exporting', 'done']
          const cur = order.indexOf(status)
          const idx = order.indexOf(key)
          const isDone = cur > idx
          const isActive = cur === idx
          return (
            <div key={key} className="flex flex-col items-center gap-1.5">
              <div className={`w-2 h-2 rounded-full transition-all ${isDone ? 'bg-green-400' : isActive ? 'bg-indigo-400 animate-pulse' : 'bg-white/15'}`} />
              <span className={`text-xs ${isDone ? 'text-green-400' : isActive ? 'text-white/70' : 'text-white/25'}`}>{stepLabel}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
