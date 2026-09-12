/**
 * Frontend learning-progress abstraction.
 * Persists selected subjects per authenticated user in localStorage.
 * Swap this module later for backend learning APIs without rewriting UI.
 */

import { createInitialProgress, type SubjectProgress } from '@/data/learningCatalog'

export type LearnerLearningState = {
  subjectIds: string[]
  progress: SubjectProgress[]
  onboardedAt: string
  updatedAt: string
}

function storageKey(userId: string): string {
  return `skillforge_subjects_${userId}`
}

function readRaw(userId: string): LearnerLearningState | null {
  try {
    const raw = localStorage.getItem(storageKey(userId))
    if (!raw) return null
    const parsed = JSON.parse(raw) as LearnerLearningState
    if (!parsed || !Array.isArray(parsed.subjectIds)) return null
    return parsed
  } catch {
    return null
  }
}

function writeRaw(userId: string, state: LearnerLearningState): void {
  localStorage.setItem(storageKey(userId), JSON.stringify(state))
}

export function hasLearningOnboarding(userId: string): boolean {
  const state = readRaw(userId)
  return Boolean(state && state.subjectIds.length > 0)
}

export function getLearningState(userId: string): LearnerLearningState | null {
  return readRaw(userId)
}

export function getSelectedSubjectIds(userId: string): string[] {
  return readRaw(userId)?.subjectIds ?? []
}

export function getSubjectProgress(userId: string): SubjectProgress[] {
  return readRaw(userId)?.progress ?? []
}

export function saveSubjectSelection(userId: string, subjectIds: string[]): LearnerLearningState {
  const uniqueIds = [...new Set(subjectIds)]
  if (uniqueIds.length === 0) {
    throw new Error('At least one subject is required')
  }

  const existing = readRaw(userId)
  const now = new Date().toISOString()
  const next: LearnerLearningState = {
    subjectIds: uniqueIds,
    progress: createInitialProgress(uniqueIds),
    onboardedAt: existing?.onboardedAt ?? now,
    updatedAt: now,
  }
  writeRaw(userId, next)
  return next
}

export function getContinueLearning(userId: string): SubjectProgress | null {
  const progress = getSubjectProgress(userId)
  if (progress.length === 0) return null
  return [...progress].sort((a, b) => b.progressPercent - a.progressPercent)[0] ?? null
}

export function clearLearningState(userId: string): void {
  localStorage.removeItem(storageKey(userId))
}
