import { useEffect, useRef, useState } from 'react'
import type { Config, UploadResult } from '../types'

interface Question {
  id: string
  question: string
  options: string[]
}

interface Props {
  upload: UploadResult
  config: Config
  onComplete: (config: Config) => void
  onBack: () => void
}

export default function StepClarify({ upload, config, onComplete, onBack }: Props) {
  const [phase, setPhase] = useState<'loading' | 'questions' | 'submitting' | 'failed'>('loading')
  const [statusMsg, setStatusMsg] = useState('Transcribing audio...')
  const [progress, setProgress] = useState(0)
  const [questions, setQuestions] = useState<Question[]>([])
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [errorMsg, setErrorMsg] = useState('')
  const started = useRef(false)

  useEffect(() => {
    if (started.current) return
    started.current = true

    async function run() {
      try {
        const res = await fetch(`http://localhost:8000/pre-analyze/${upload.job_id}`, {
          method: 'POST',
        })
        if (!res.ok) throw new Error(`Server error: ${res.status}`)
      } catch (e) {
        setErrorMsg(e instanceof Error ? e.message : 'Failed to start analysis')
        setPhase('failed')
        return
      }

      const es = new EventSource(`http://localhost:8000/pre-analyze-events/${upload.job_id}`)
      es.onmessage = (event) => {
        if (event.data === '[DONE]') { es.close(); return }
        try {
          const data = JSON.parse(event.data)
          setStatusMsg(data.message || '')
          setProgress(data.progress || 0)

          if (data.status === 'ready') {
            es.close()
            const qs: Question[] = (data.questions || []).map((q: Question) => ({
              id: q.id,
              question: q.question,
              options: Array.isArray(q.options) ? q.options : [],
            }))
            setQuestions(qs)
            const init: Record<string, string> = {}
            for (const q of qs) init[q.id] = ''
            setAnswers(init)
            setPhase('questions')
          } else if (data.status === 'failed') {
            es.close()
            setErrorMsg(data.message || 'Analysis failed')
            setPhase('failed')
          }
        } catch (e) { console.error('SSE parse error (clarify):', e) }
      }
      es.onerror = () => {
        es.close()
        setErrorMsg('Lost connection to server')
        setPhase('failed')
      }
    }

    run()
  }, [upload.job_id])

  async function handleContinue() {
    const answered = questions
      .filter(q => answers[q.id]?.trim())
      .map(q => ({ question: q.question, answer: answers[q.id].trim() }))

    if (answered.length > 0) {
      setPhase('submitting')
      try {
        const r = await fetch(`http://localhost:8000/understand-answers/${upload.job_id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ answers: answered }),
        })
        if (!r.ok) console.error('understand-answers failed:', r.status)
      } catch (e) {
        // non-fatal — proceed with unrefined video_info
        console.error('understand-answers error:', e)
      }
    }

    onComplete(config)
  }

  function handleSkip() {
    onComplete(config)
  }

  // ── Loading ──
  if (phase === 'loading') {
    return (
      <div className="text-center">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/15 flex items-center justify-center mx-auto mb-8">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Understanding your video</h2>
        <p className="text-white/50 text-sm mb-8">Transcribing, watching frames, and building a complete picture.</p>
        <div className="max-w-sm mx-auto mb-4">
          <div className="flex justify-between text-xs text-white/40 mb-2">
            <span>{statusMsg}</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div className="h-full bg-indigo-500 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
          </div>
        </div>
        <button onClick={handleSkip} className="text-xs text-white/30 hover:text-white/55 transition-colors mt-4">
          Skip — generate overlays with what the AI understood
        </button>
      </div>
    )
  }

  // ── Submitting ──
  if (phase === 'submitting') {
    return (
      <div className="text-center">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/15 flex items-center justify-center mx-auto mb-8">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Updating understanding...</h2>
        <p className="text-white/50 text-sm">Incorporating your answers.</p>
      </div>
    )
  }

  // ── Failed ──
  if (phase === 'failed') {
    return (
      <div className="text-center">
        <div className="w-16 h-16 rounded-2xl bg-amber-500/15 flex items-center justify-center text-3xl mx-auto mb-6">⚠️</div>
        <h2 className="text-xl font-bold text-white mb-2">Couldn't analyse the video</h2>
        <p className="text-white/50 text-sm mb-6 max-w-sm mx-auto">{errorMsg || 'Analysis failed.'}</p>
        <div className="flex gap-3 justify-center">
          <button onClick={onBack} className="px-5 py-2.5 rounded-xl bg-white/8 hover:bg-white/12 text-white/60 text-sm transition-colors">
            Back
          </button>
          <button onClick={handleSkip} className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors">
            Continue anyway →
          </button>
        </div>
      </div>
    )
  }

  // ── Questions ──
  const hasAnswers = questions.some(q => answers[q.id]?.trim())

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-1">A few quick questions</h2>
        <p className="text-white/50 text-sm">
          Help the AI understand your intent — it already knows the content.
        </p>
      </div>

      {questions.length === 0 ? (
        <div className="p-4 rounded-xl bg-emerald-500/8 border border-emerald-500/20 mb-6">
          <p className="text-sm text-emerald-400">The AI understood your video clearly — no questions needed.</p>
        </div>
      ) : (
        <div className="space-y-5 mb-8">
          {questions.map((q) => (
            <div key={q.id}>
              <p className="text-sm font-medium text-white/85 mb-2.5">{q.question}</p>
              <div className="flex flex-wrap gap-2">
                {q.options.map((opt) => {
                  const selected = answers[q.id] === opt
                  return (
                    <button
                      key={opt}
                      onClick={() => setAnswers(prev => ({ ...prev, [q.id]: selected ? '' : opt }))}
                      className={`px-3.5 py-1.5 rounded-full text-sm border transition-all ${
                        selected
                          ? 'border-indigo-500 bg-indigo-500/20 text-white'
                          : 'border-white/15 bg-white/4 text-white/55 hover:border-white/30 hover:text-white/80'
                      }`}
                    >
                      {opt}
                    </button>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-3">
        <button onClick={onBack} className="px-5 py-3 rounded-xl bg-white/8 hover:bg-white/12 text-white/60 text-sm font-medium transition-colors">
          Back
        </button>
        <button onClick={handleContinue}
          className="flex-1 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition-colors">
          {hasAnswers ? 'Analyse with my answers →' : 'Analyse →'}
        </button>
      </div>

      {questions.length > 0 && (
        <button onClick={handleSkip} className="w-full mt-3 text-xs text-white/25 hover:text-white/45 transition-colors">
          Skip — generate overlays without answers
        </button>
      )}
    </div>
  )
}
