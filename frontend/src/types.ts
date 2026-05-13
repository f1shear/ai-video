export type FontSize = 'small' | 'medium' | 'large'

export type VideoFormat = 'vertical' | 'horizontal' | 'square'
export type Style = 'clean' | 'cinematic' | 'bold' | 'minimal'

export type OverlayPosition =
  | 'top_left'
  | 'top_center'
  | 'top_right'
  | 'bottom_left'
  | 'bottom_center'
  | 'bottom_right'
  | 'center'

export type OverlayRole = 'label' | 'fact' | 'chapter' | 'annotation' | 'cta'
export type OverlayTemplate = 'corner_badge' | 'lower_third' | 'chyron' | 'cinematic_title' | 'pill'
export type Importance = 'must' | 'should' | 'could' | 'would'

export type Step = 'upload' | 'configure' | 'clarify' | 'process' | 'review' | 'export'

export interface UploadResult {
  job_id: string
  filename: string
  duration: number
}

export type ReasoningEffort = 'standard' | 'extended'

export interface Config {
  video_format: VideoFormat
  style: Style
  font_size: FontSize
  model: string
  reasoning_effort: ReasoningEffort
}

export interface CheckpointAlternative {
  text: string
  sub_text: string | null
  role: OverlayRole
  template: OverlayTemplate
  confidence: number
  rationale?: string | null
}

export interface Checkpoint {
  timestamp: number
  duration: number
  text: string
  sub_text: string | null
  position: OverlayPosition
  rationale?: string | null
  importance: Importance
  role: OverlayRole
  template: OverlayTemplate
  layer: string           // 'content' | 'subtitles' | 'chapters'
  source_url?: string | null
  confidence?: number
  alternatives?: CheckpointAlternative[]
}

export interface ProgressState {
  status: string
  message: string
  progress: number
}

export interface LearningSection {
  start: number
  end: number
  title: string
  summary: string
  summary_concise?: string
  summary_detailed?: string
  key_facts: string[]
  deep_dive: string
  links: { text: string; url: string }[]
}

export interface QuizPoint {
  timestamp: number
  question: string
  options: string[]
  correct_index: number
  explanation: string
  hint: string
  difficulty: 'easy' | 'medium' | 'hard'
  related_fact: string
  easier_version?: string
  harder_version?: string
}

export interface LearningScript {
  title: string
  sections: LearningSection[]
  quiz_points: QuizPoint[]
}

export interface TokenUsage {
  input_tokens: number
  output_tokens: number
  cost_usd: number
  models?: string[]
}
