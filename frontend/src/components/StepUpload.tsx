import { useState, useRef, DragEvent, ChangeEvent } from 'react'
import type { UploadResult } from '../types'

interface Props {
  onComplete: (result: UploadResult) => void
}

export default function StepUpload({ onComplete }: Props) {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  async function handleFile(file: File) {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (!['mp4', 'mov', 'avi', 'mkv', 'webm'].includes(ext || '')) {
      setError('Please upload a video file (MP4, MOV, AVI, MKV, or WebM).')
      return
    }
    setError(null)
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Upload failed')
      }
      const result: UploadResult = await res.json()
      onComplete(result)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Upload failed. Make sure the backend is running.')
      setUploading(false)
    }
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  function onChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  return (
    <div className="text-center">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-3">Upload your video</h2>
        <p className="text-white/50 text-sm">MP4, MOV, AVI, MKV, or WebM · Any length</p>
      </div>

      <div
        className={`relative border-2 border-dashed rounded-2xl p-16 cursor-pointer transition-all
          ${dragging ? 'border-indigo-500 bg-indigo-500/10' : 'border-white/15 hover:border-white/30 bg-white/3'}
          ${uploading ? 'pointer-events-none opacity-70' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept="video/*"
          className="hidden"
          onChange={onChange}
        />
        {uploading ? (
          <div className="flex flex-col items-center gap-4">
            <div className="w-10 h-10 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-white/60 text-sm">Uploading...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white/8 flex items-center justify-center text-2xl">
              🎬
            </div>
            <div>
              <p className="text-white font-medium mb-1">Drop your video here</p>
              <p className="text-white/40 text-sm">or click to browse</p>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-3 rounded-xl bg-red-500/15 border border-red-500/30 text-red-400 text-sm">
          {error}
        </div>
      )}
    </div>
  )
}
