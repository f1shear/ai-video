import { useState } from 'react'
import type { Step, UploadResult, Config, Checkpoint, LearningScript, TokenUsage } from './types'
import StepUpload from './components/StepUpload'
import StepConfigure from './components/StepConfigure'
import StepClarify from './components/StepClarify'
import StepProcess from './components/StepProcess'
import StepReview from './components/StepReview'
import StepExport from './components/StepExport'

const STEPS: Step[] = ['upload', 'configure', 'clarify', 'process', 'review', 'export']
const STEP_LABELS: Record<Step, string> = {
  upload: 'Upload',
  configure: 'Configure',
  clarify: 'Clarify',
  process: 'Analyse',
  review: 'Review',
  export: 'Export',
}

export default function App() {
  const [step, setStep] = useState<Step>('upload')
  const [upload, setUpload] = useState<UploadResult | null>(null)
  const [config, setConfig] = useState<Config | null>(null)
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([])
  const [videoSummary, setVideoSummary] = useState('')
  const [sourceUrls, setSourceUrls] = useState<Record<string, string>>({})
  const [learningScript, setLearningScript] = useState<LearningScript>({ title: '', sections: [], quiz_points: [] })
  const [tokenUsage, setTokenUsage] = useState<TokenUsage>({ input_tokens: 0, output_tokens: 0, cost_usd: 0 })

  const stepIndex = STEPS.indexOf(step)

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-white/10 px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-white tracking-tight">Overlay</h1>
            <p className="text-xs text-white/40 mt-0.5">Find the moments. Add the labels.</p>
          </div>
          <div className="flex items-center gap-2">
            {STEPS.map((s, i) => (
              <div key={s} className="flex items-center gap-2">
                <div className={`flex items-center gap-1.5 ${i === stepIndex ? 'text-white' : i < stepIndex ? 'text-green-400' : 'text-white/25'}`}>
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-medium border
                    ${i === stepIndex ? 'bg-indigo-500 border-indigo-500 text-white' :
                      i < stepIndex ? 'bg-green-500/20 border-green-500/50 text-green-400' :
                      'bg-transparent border-white/20 text-white/30'}`}>
                    {i < stepIndex ? '✓' : i + 1}
                  </div>
                  <span className="text-xs font-medium hidden sm:block">{STEP_LABELS[s]}</span>
                </div>
                {i < STEPS.length - 1 && (
                  <div className={`w-6 h-px ${i < stepIndex ? 'bg-green-500/40' : 'bg-white/10'}`} />
                )}
              </div>
            ))}
          </div>
        </div>
      </header>

      <main className="flex-1 flex items-start justify-center px-6 py-12">
        <div className={`w-full ${step === 'review' ? 'max-w-5xl' : step === 'clarify' ? 'max-w-xl' : 'max-w-2xl'}`}>
          {step === 'upload' && (
            <StepUpload
              onComplete={(result) => {
                setUpload(result)
                setStep('configure')
              }}
            />
          )}
          {step === 'configure' && upload && (
            <StepConfigure
              upload={upload}
              onComplete={(cfg) => {
                setConfig(cfg)
                setStep('clarify')
              }}
              onBack={() => setStep('upload')}
            />
          )}
          {step === 'clarify' && upload && config && (
            <StepClarify
              upload={upload}
              config={config}
              onComplete={(cfg) => {
                setConfig(cfg)
                setStep('process')
              }}
              onBack={() => setStep('configure')}
            />
          )}
          {step === 'process' && upload && config && (
            <StepProcess
              upload={upload}
              config={config}
              onComplete={(cps, summary, urls, ls, tu) => {
                setCheckpoints(cps)
                setVideoSummary(summary)
                setSourceUrls(urls)
                setLearningScript(ls)
                setTokenUsage(tu)
                setStep('review')
              }}
              onFail={() => setStep('upload')}
            />
          )}
          {step === 'review' && upload && config && (
            <StepReview
              upload={upload}
              config={config}
              checkpoints={checkpoints}
              summary={videoSummary}
              sourceUrls={sourceUrls}
              learningScript={learningScript}
              onComplete={(edited, ls) => {
                setCheckpoints(edited)
                setLearningScript(ls)
                setStep('export')
              }}
              onBack={() => setStep('process')}
            />
          )}
          {step === 'export' && upload && config && (
            <StepExport
              upload={upload}
              config={config}
              checkpoints={checkpoints}
              learningScript={learningScript}
              tokenUsage={tokenUsage}
              onReset={() => {
                setUpload(null)
                setConfig(null)
                setCheckpoints([])
                setVideoSummary('')
                setSourceUrls({})
                setLearningScript({ title: '', sections: [], quiz_points: [] })
                setTokenUsage({ input_tokens: 0, output_tokens: 0, cost_usd: 0 })
                setStep('upload')
              }}
            />
          )}
        </div>
      </main>
    </div>
  )
}
