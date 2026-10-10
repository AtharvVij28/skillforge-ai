/**
 * Learning catalog for the authenticated home experience (frontend MVP).
 * Isolated from competency demo data so it can later be replaced by APIs.
 */

export type LearningSubject = {
  id: string
  name: string
  description: string
  icon: string
}

export const LEARNING_SUBJECTS: LearningSubject[] = [
  {
    id: 'python',
    name: 'Python',
    description: 'Core programming for data and automation workflows.',
    icon: 'PY',
  },
  {
    id: 'statistics',
    name: 'Statistics',
    description: 'Survey methods, estimation, and statistical reasoning.',
    icon: 'ST',
  },
  {
    id: 'machine-learning',
    name: 'Machine Learning',
    description: 'Foundations of supervised and unsupervised learning.',
    icon: 'ML',
  },
  {
    id: 'artificial-intelligence',
    name: 'Artificial Intelligence',
    description: 'Responsible AI concepts for public-sector analytics.',
    icon: 'AI',
  },
  {
    id: 'data-science',
    name: 'Data Science',
    description: 'End-to-end analysis from data prep to insight.',
    icon: 'DS',
  },
  {
    id: 'sql-databases',
    name: 'SQL & Databases',
    description: 'Querying and managing statistical datasets.',
    icon: 'SQL',
  },
  {
    id: 'data-visualization',
    name: 'Data Visualization',
    description: 'Clear charts and briefing-ready visual communication.',
    icon: 'DV',
  },
  {
    id: 'computer-networks',
    name: 'Computer Networks',
    description: 'Network fundamentals for digital public systems.',
    icon: 'CN',
  },
  {
    id: 'operating-systems',
    name: 'Operating Systems',
    description: 'OS concepts for secure and reliable computing.',
    icon: 'OS',
  },
  {
    id: 'web-development',
    name: 'Web Development',
    description: 'Building accessible web applications and portals.',
    icon: 'WEB',
  },
  {
    id: 'cloud-computing',
    name: 'Cloud Computing',
    description: 'Cloud platforms for scalable data workloads.',
    icon: 'CL',
  },
  {
    id: 'cybersecurity',
    name: 'Cybersecurity',
    description: 'Security awareness for data and digital services.',
    icon: 'SEC',
  },
  {
    id: 'algorithms-data-structures',
    name: 'Algorithms & Data Structures',
    description: 'Problem-solving patterns for efficient computation.',
    icon: 'ADS',
  },
]

export type SubjectProgress = {
  subjectId: string
  progressPercent: number
  currentChapter: number
  totalChapters: number
  lastActivity: string
  courseTitle: string
}

/** Seed progress when a learner first selects subjects (frontend MVP only). */
export function createInitialProgress(subjectIds: string[]): SubjectProgress[] {
  const seeds: Record<string, Omit<SubjectProgress, 'subjectId'>> = {
    python: {
      progressPercent: 72,
      currentChapter: 4,
      totalChapters: 8,
      lastActivity: 'Functions & Modules',
      courseTitle: 'Python Fundamentals',
    },
    statistics: {
      progressPercent: 48,
      currentChapter: 3,
      totalChapters: 7,
      lastActivity: 'Sampling Distributions',
      courseTitle: 'Applied Statistics',
    },
    'machine-learning': {
      progressPercent: 31,
      currentChapter: 2,
      totalChapters: 9,
      lastActivity: 'Supervised Learning Basics',
      courseTitle: 'ML Foundations',
    },
    'sql-databases': {
      progressPercent: 64,
      currentChapter: 5,
      totalChapters: 8,
      lastActivity: 'Joins & Aggregations',
      courseTitle: 'SQL for Data Analysis',
    },
    'data-visualization': {
      progressPercent: 40,
      currentChapter: 2,
      totalChapters: 6,
      lastActivity: 'Chart Literacy',
      courseTitle: 'Visual Communication',
    },
    'data-science': {
      progressPercent: 22,
      currentChapter: 1,
      totalChapters: 8,
      lastActivity: 'Data Wrangling Intro',
      courseTitle: 'Data Science Pathway',
    },
    'artificial-intelligence': {
      progressPercent: 18,
      currentChapter: 1,
      totalChapters: 7,
      lastActivity: 'AI Landscape Overview',
      courseTitle: 'Responsible AI Essentials',
    },
    cybersecurity: {
      progressPercent: 27,
      currentChapter: 2,
      totalChapters: 6,
      lastActivity: 'Threat Awareness',
      courseTitle: 'Cybersecurity Basics',
    },
    'cloud-computing': {
      progressPercent: 15,
      currentChapter: 1,
      totalChapters: 6,
      lastActivity: 'Cloud Concepts',
      courseTitle: 'Cloud Foundations',
    },
    'web-development': {
      progressPercent: 35,
      currentChapter: 2,
      totalChapters: 8,
      lastActivity: 'HTML & Accessibility',
      courseTitle: 'Web Development Starter',
    },
    'computer-networks': {
      progressPercent: 20,
      currentChapter: 1,
      totalChapters: 6,
      lastActivity: 'Network Layers',
      courseTitle: 'Networks Primer',
    },
    'operating-systems': {
      progressPercent: 12,
      currentChapter: 1,
      totalChapters: 6,
      lastActivity: 'Process Basics',
      courseTitle: 'OS Fundamentals',
    },
    'algorithms-data-structures': {
      progressPercent: 25,
      currentChapter: 2,
      totalChapters: 8,
      lastActivity: 'Arrays & Complexity',
      courseTitle: 'Algorithms Essentials',
    },
  }

  return subjectIds.map((subjectId) => {
    const seed = seeds[subjectId]
    if (seed) {
      return { subjectId, ...seed }
    }
    return {
      subjectId,
      progressPercent: 0,
      currentChapter: 1,
      totalChapters: 6,
      lastActivity: 'Ready to begin',
      courseTitle: 'Getting Started',
    }
  })
}

export function getSubjectById(id: string): LearningSubject | undefined {
  return LEARNING_SUBJECTS.find((subject) => subject.id === id)
}

export const SUBJECT_TO_COMPETENCY_CODE: Record<string, string> = {
  python: 'PYTHON',
  statistics: 'STATISTICS',
  'machine-learning': 'MACHINE_LEARNING',
  'artificial-intelligence': 'ARTIFICIAL_INTELLIGENCE',
  'data-science': 'DATA_SCIENCE',
  'sql-databases': 'SQL_DATABASES',
  'data-visualization': 'DATA_VISUALIZATION',
  'computer-networks': 'COMPUTER_NETWORKS',
  'operating-systems': 'OPERATING_SYSTEMS',
  'web-development': 'WEB_DEVELOPMENT',
  'cloud-computing': 'CLOUD_COMPUTING',
  cybersecurity: 'CYBERSECURITY',
  'algorithms-data-structures': 'ALGORITHMS',
}

export function competencyCodesForSubjects(subjectIds: string[]): string[] {
  return [...new Set(subjectIds.map((id) => SUBJECT_TO_COMPETENCY_CODE[id]).filter(Boolean))]
}

export function getRecommendationForSubjects(subjectIds: string[]): {
  title: string
  reason: string
  subjectId: string
} {
  const preferred =
    subjectIds.find((id) => id === 'sql-databases') ||
    subjectIds.find((id) => id === 'data-visualization') ||
    subjectIds[0]

  const subject = getSubjectById(preferred)
  return {
    subjectId: preferred,
    title: subject ? `${subject.name} pathway` : 'Next learning module',
    reason: 'Based on your selected subjects and current progress.',
  }
}
