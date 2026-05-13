import { useEffect, useRef, useState } from 'react'
import type { UploadResult, Config, Checkpoint, LearningScript, TokenUsage } from '../types'
// Config is sent as-is to /process; backend reads video_info from job store

interface Props {
  upload: UploadResult
  config: Config
  onComplete: (checkpoints: Checkpoint[], summary: string, sourceUrls: Record<string, string>, learningScript: LearningScript, tokenUsage: TokenUsage) => void
  onFail: () => void
}

export default function StepProcess({ upload, config, onComplete, onFail }: Props) {
  const [status, setStatus] = useState('queued')
  const [message, setMessage] = useState('Starting...')
  const [progress, setProgress] = useState(0)
  const [failed, setFailed] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const started = useRef(false)

  useEffect(() => {
    if (started.current) return
    started.current = true

    async function run() {
      try {
        const res = await fetch(`http://localhost:8000/process/${upload.job_id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(config),
        })
        if (!res.ok) {
          const err = await res.json()
          throw new Error(err.detail || 'Failed to start processing')
        }
      } catch (e: unknown) {
        setFailed(true)
        setErrorMessage(e instanceof Error ? e.message : 'Failed to start processing.')
        return
      }

      const es = new EventSource(`http://localhost:8000/events/${upload.job_id}`)
      es.onmessage = async (event) => {
        if (event.data === '[DONE]') {
          es.close()
          return
        }
        try {
          const data = JSON.parse(event.data)
          setStatus(data.status)
          setMessage(data.message)
          setProgress(data.progress)

          if (data.status === 'checkpoints_ready') {
            es.close()
            // Fetch the generated checkpoints + learning script then hand off to review step
            try {
              const r = await fetch(`http://localhost:8000/checkpoints/${upload.job_id}`)
              if (!r.ok) throw new Error('Failed to fetch checkpoints')
              const body = await r.json()
              onComplete(
                body.checkpoints as Checkpoint[],
                (body.summary as string) || '',
                (body.source_urls as Record<string, string>) || {},
                (body.learning_script as LearningScript) || { title: '', sections: [], quiz_points: [] },
                (body.token_usage as TokenUsage) || { input_tokens: 0, output_tokens: 0, cost_usd: 0 },
              )
            } catch (e: unknown) {
              setFailed(true)
              setErrorMessage(e instanceof Error ? e.message : 'Failed to load checkpoints.')
            }
          } else if (data.status === 'failed') {
            es.close()
            setFailed(true)
            setErrorMessage(data.message || 'Processing failed.')
          }
        } catch (e) {
          console.error('SSE parse error (process):', e)
        }
      }
      es.onerror = () => {
        es.close()
        setFailed(true)
        setErrorMessage('Lost connection to the server. Please try again.')
      }
    }

    run()
  }, [upload.job_id, config, onComplete])

  if (failed) {
    return (
      <div className="text-center">
        <div className="w-16 h-16 rounded-2xl bg-red-500/15 flex items-center justify-center text-3xl mx-auto mb-6">❌</div>
        <h2 className="text-2xl font-bold text-white mb-3">Processing failed</h2>
        <p className="text-white/50 text-sm mb-8 max-w-md mx-auto">{errorMessage}</p>
        <button
          onClick={onFail}
          className="px-8 py-3 rounded-xl bg-white/10 hover:bg-white/15 text-white text-sm font-medium transition-colors"
        >
          Try again
        </button>
      </div>
    )
  }

  const statusLabels: Record<string, string> = {
    queued: 'Getting ready...',
    transcribing: 'Transcribing audio...',
    finding_checkpoints: 'Analysing video with AI...',
    generating_learning: 'Generating learning content...',
    checkpoints_ready: 'Ready!',
  }
  const label = statusLabels[status] || message

  return (
    <div className="text-center">
      <div className="w-16 h-16 rounded-2xl bg-indigo-500/15 flex items-center justify-center mx-auto mb-8">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>

      <h2 className="text-2xl font-bold text-white mb-2">Analysing your video</h2>
      <p className="text-white/50 text-sm mb-10">
        Finding key moments, generating overlays and learning content.
      </p>

      <div className="mb-4">
        <div className="flex justify-between text-xs text-white/40 mb-2">
          <span>{message}</span>
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
          { key: 'transcribing', label: 'Transcribe' },
          { key: 'finding_checkpoints', label: 'AI Analysis' },
          { key: 'generating_learning', label: 'Learning' },
          { key: 'checkpoints_ready', label: 'Ready' },
        ].map(({ key, label: stepLabel }) => {
          const order = ['transcribing', 'finding_checkpoints', 'generating_learning', 'checkpoints_ready']
          const cur = order.indexOf(status)
          const idx = order.indexOf(key)
          const done = cur > idx
          const active = cur === idx
          return (
            <div key={key} className="flex flex-col items-center gap-1.5">
              <div className={`w-2 h-2 rounded-full transition-all ${done ? 'bg-green-400' : active ? 'bg-indigo-400 animate-pulse' : 'bg-white/15'}`} />
              <span className={`text-xs ${done ? 'text-green-400' : active ? 'text-white/70' : 'text-white/25'}`}>{stepLabel}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
