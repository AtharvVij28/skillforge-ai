import api from '@/services/api'

export type QuestionOption = { key: string; text: string }

export type AssessmentQuestion = {
  id: string
  stem: string
  options: QuestionOption[]
  competency_code: string
  competency_name: string
  points: number | string
  correct_option: string | null
  explanation: string | null
}

export type AssessmentDetail = {
  id: string
  title: string
  description: string | null
  question_count: number
  generation_method: string
  questions: AssessmentQuestion[]
}

export type AttemptResult = {
  attempt_id: string
  assessment_id: string
  status: string
  percentage: number | string | null
  feedback_summary: string | null
  next_action: string | null
  strengths: string[]
  weaknesses: string[]
  competency_breakdown: Array<{
    competency_name: string
    percent_correct: number | string
    previous_score: number | string | null
    updated_score: number | string
  }>
  questions: AssessmentQuestion[]
}

export async function generateAssessment(
  questionCount = 5,
  competencyCodes: string[] = [],
): Promise<AssessmentDetail> {
  const { data } = await api.post<AssessmentDetail>(
    '/api/assessments/generate',
    {
      question_count: questionCount,
      competency_codes: competencyCodes,
    },
    { timeout: 90000 },
  )
  return data
}

export async function startAssessment(assessmentId: string) {
  const { data } = await api.post<{
    attempt_id: string
    questions: AssessmentQuestion[]
  }>(`/api/assessments/${assessmentId}/start`)
  return data
}

export async function submitAttempt(
  attemptId: string,
  answers: Array<{ question_id: string; selected_option: string }>,
): Promise<AttemptResult> {
  const { data } = await api.post<AttemptResult>(`/api/assessments/attempts/${attemptId}/submit`, {
    answers,
  })
  return data
}
