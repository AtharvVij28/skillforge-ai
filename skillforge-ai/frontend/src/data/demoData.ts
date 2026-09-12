/**
 * HACKATHON ROUND 1 — FRONTEND DEMO DATA
 *
 * Isolated mock dataset for the judge-facing prototype.
 * This is NOT live iGOT Karmayogi or NSSTA data.
 * Future phases can replace this module with real API adapters.
 */

export const DEMO_NOTICE =
  'Demo data for SkillForge AI Round 1. Integration-ready for iGOT Karmayogi and NSSTA — not currently connected.'

export const learningLoop = ['Profile', 'Assess', 'Recommend', 'Learn', 'Assess again'] as const

export const demoUser = {
  id: 'demo-learner-atharv',
  greetingName: 'Atharv',
  fullName: 'Atharv Vij',
  designation: 'Statistical Analyst',
  department: 'Data & Analytics',
  experienceYears: 3,
  education: 'BCA / AI Specialization',
  role: 'Data & Statistical Analysis',
  targetRole: 'Senior Statistical Computing Officer',
  trainingCompleted: 8,
  profileCompletion: 92,
  email: 'atharv.vij@demo.skillforge',
  location: 'New Delhi',
} as const

export const demoKpis = {
  overallCompetency: 78,
  competenciesAssessed: 12,
  skillGaps: 4,
  learningProgress: 64,
} as const

export type CompetencyCategory = 'Statistical' | 'Technical' | 'Digital' | 'Governance' | 'Behavioural'

export type DemoCompetency = {
  id: string
  name: string
  category: CompetencyCategory
  currentPercent: number
  currentLevel: number
  targetLevel: number
  status: 'On track' | 'Developing' | 'Priority gap'
}

export const demoCompetencies: DemoCompetency[] = [
  {
    id: 'stat-analysis',
    name: 'Statistical Analysis',
    category: 'Statistical',
    currentPercent: 82,
    currentLevel: 4.1,
    targetLevel: 4.5,
    status: 'On track',
  },
  {
    id: 'python',
    name: 'Python',
    category: 'Technical',
    currentPercent: 68,
    currentLevel: 3.2,
    targetLevel: 4.5,
    status: 'Priority gap',
  },
  {
    id: 'sql',
    name: 'SQL',
    category: 'Technical',
    currentPercent: 71,
    currentLevel: 3.4,
    targetLevel: 4.0,
    status: 'Developing',
  },
  {
    id: 'viz',
    name: 'Data Visualization',
    category: 'Digital',
    currentPercent: 77,
    currentLevel: 3.8,
    targetLevel: 4.2,
    status: 'Developing',
  },
  {
    id: 'ml',
    name: 'Machine Learning',
    category: 'Technical',
    currentPercent: 64,
    currentLevel: 3.7,
    targetLevel: 4.0,
    status: 'Developing',
  },
  {
    id: 'gov',
    name: 'Digital Governance',
    category: 'Governance',
    currentPercent: 74,
    currentLevel: 3.7,
    targetLevel: 4.0,
    status: 'On track',
  },
  {
    id: 'survey',
    name: 'Survey Methodology',
    category: 'Statistical',
    currentPercent: 80,
    currentLevel: 4.0,
    targetLevel: 4.3,
    status: 'On track',
  },
  {
    id: 'privacy',
    name: 'Data Privacy',
    category: 'Governance',
    currentPercent: 76,
    currentLevel: 3.8,
    targetLevel: 4.0,
    status: 'On track',
  },
  {
    id: 'comms',
    name: 'Communication',
    category: 'Behavioural',
    currentPercent: 81,
    currentLevel: 4.0,
    targetLevel: 4.2,
    status: 'On track',
  },
]

export type Priority = 'High' | 'Medium' | 'Low'

export type DemoSkillGap = {
  id: string
  name: string
  current: number
  required: number
  gap: number
  priority: Priority
  explanation: string
}

export const demoSkillGaps: DemoSkillGap[] = [
  {
    id: 'gap-python',
    name: 'Advanced Python',
    current: 3.2,
    required: 4.5,
    gap: 1.3,
    priority: 'High',
    explanation:
      'Your role requires Python proficiency near 4.5. Current estimate is 3.2 based on profile and recent assessment performance in data manipulation.',
  },
  {
    id: 'gap-sql',
    name: 'SQL & Database Management',
    current: 3.4,
    required: 4.0,
    gap: 0.6,
    priority: 'Medium',
    explanation:
      'Official statistics workflows expect SQL at level 4.0. Recent practice shows gaps in joins and aggregation for large survey datasets.',
  },
  {
    id: 'gap-viz',
    name: 'Data Visualization',
    current: 3.8,
    required: 4.2,
    gap: 0.4,
    priority: 'Medium',
    explanation:
      'Target role includes briefing-ready visualisations. Current work is solid; remaining gap is in statistical communication graphics.',
  },
  {
    id: 'gap-ml',
    name: 'Machine Learning Fundamentals',
    current: 3.7,
    required: 4.0,
    gap: 0.3,
    priority: 'Low',
    explanation:
      'ML is a supporting competency for your target role. A short foundation module would close this modest gap.',
  },
]

export type DemoLearningResource = {
  id: string
  title: string
  priority: Priority
  reason: string
  difficulty: string
  durationHours: number
  progress: number
  action: 'Continue Learning' | 'Start Learning' | 'View Course'
  providerLabel: string
  isDemo: true
}

export const demoLearningPath: DemoLearningResource[] = [
  {
    id: 'learn-python',
    title: 'Advanced Python for Statistical Computing',
    priority: 'High',
    reason: 'Closes your largest competency gap.',
    difficulty: 'Intermediate',
    durationHours: 6,
    progress: 32,
    action: 'Continue Learning',
    providerLabel: 'Demo learning resource · Integration-ready (iGOT / NSSTA)',
    isDemo: true,
  },
  {
    id: 'learn-sql',
    title: 'SQL for Statistical Data Management',
    priority: 'Medium',
    reason: 'Addresses role-required SQL proficiency for survey data pipelines.',
    difficulty: 'Intermediate',
    durationHours: 4,
    progress: 0,
    action: 'Start Learning',
    providerLabel: 'Demo learning resource · Integration-ready (iGOT / NSSTA)',
    isDemo: true,
  },
  {
    id: 'learn-viz',
    title: 'Data Visualization with Python',
    priority: 'Medium',
    reason: 'Supports briefing-quality charts for official statistical outputs.',
    difficulty: 'Beginner–Intermediate',
    durationHours: 5,
    progress: 12,
    action: 'View Course',
    providerLabel: 'Demo learning resource · Integration-ready (iGOT / NSSTA)',
    isDemo: true,
  },
]

export const demoTrainingHistory = [
  { title: 'Introduction to Official Statistics', year: '2024', provider: 'Demo · NSSTA-style' },
  { title: 'Survey Sampling Basics', year: '2024', provider: 'Demo · iGOT-style' },
  { title: 'Data Ethics in Public Sector', year: '2025', provider: 'Demo · Internal' },
  { title: 'SQL Fundamentals for Analysts', year: '2025', provider: 'Demo · iGOT-style' },
] as const

export type DemoQuestion = {
  id: string
  stem: string
  options: string[]
  correctIndex: number
  explanation: string
}

export const demoAssessment = {
  title: 'Python & Statistical Computing Assessment',
  competency: 'Python',
  totalQuestions: 10,
  questions: [
    {
      id: 'q1',
      stem: 'Which pandas method is most appropriate for combining two survey tables on a common household ID?',
      options: ['DataFrame.append()', 'DataFrame.merge()', 'DataFrame.explode()', 'DataFrame.stack()'],
      correctIndex: 1,
      explanation: 'merge() joins tables on keys such as household ID — the standard pattern for survey microdata.',
    },
    {
      id: 'q2',
      stem: 'What does a groupby().agg() pattern typically support in official statistics?',
      options: [
        'Fitting a neural network',
        'Rendering a map tile',
        'Domain-level summaries from unit records',
        'Encrypting a database',
      ],
      correctIndex: 2,
      explanation: 'Aggregation after grouping is how unit-level records become domain estimates.',
    },
    {
      id: 'q3',
      stem: 'Which structure best stores mixed survey metadata (labels, codes, missing-value flags)?',
      options: ['A single float array', 'A dictionary of Series / DataFrame attrs', 'A raw TCP socket', 'A CSS stylesheet'],
      correctIndex: 1,
      explanation: 'Metadata belongs alongside the data object so labels and missing-value codes stay aligned.',
    },
    {
      id: 'q4',
      stem: 'You need to recode “refused” and “don’t know” as missing before estimation. Which approach is sound?',
      options: [
        'Replace those codes with NaN using a documented mapping',
        'Delete every row containing text',
        'Multiply all values by zero',
        'Convert the file to a screenshot',
      ],
      correctIndex: 0,
      explanation: 'Explicit, documented recoding preserves transparency of official statistical processing.',
    },
    {
      id: 'q5',
      stem: 'Which library is commonly used with Python for statistical modelling of survey outcomes?',
      options: ['statsmodels', 'nginx', 'ffmpeg', 'webpack'],
      correctIndex: 0,
      explanation: 'statsmodels provides transparent statistical models suitable for analytical work.',
    },
    {
      id: 'q6',
      stem: 'A weighted mean of a survey variable should use:',
      options: [
        'Unweighted arithmetic mean only',
        'Design weights aligned to the sampling design',
        'Random integers',
        'The file size in megabytes',
      ],
      correctIndex: 1,
      explanation: 'Survey estimates must respect the sampling design through appropriate weights.',
    },
    {
      id: 'q7',
      stem: 'Which practice reduces leakage when splitting data for a competency assessment model?',
      options: [
        'Putting the same household in train and test',
        'Splitting at household or PSU level',
        'Sorting by the target then cutting',
        'Dropping all identifiers after modelling',
      ],
      correctIndex: 1,
      explanation: 'Unit-level clustering (household/PSU) should stay within one split.',
    },
    {
      id: 'q8',
      stem: 'NumPy vectorisation is preferred over Python loops primarily because it:',
      options: [
        'Makes charts purple',
        'Improves performance on large numeric arrays',
        'Replaces SQL entirely',
        'Removes the need for documentation',
      ],
      correctIndex: 1,
      explanation: 'Vectorised operations are faster and clearer for large official-statistics arrays.',
    },
    {
      id: 'q9',
      stem: 'Which output is most appropriate for an explainable competency score update?',
      options: [
        'A hidden embedding with no rationale',
        'Score change plus the assessment items that drove it',
        'A random walk',
        'Deleting the previous profile',
      ],
      correctIndex: 1,
      explanation: 'SkillForge AI requires human-readable reasons whenever scores change.',
    },
    {
      id: 'q10',
      stem: 'After closing a Python gap, the learning loop should next:',
      options: [
        'Freeze the profile forever',
        'Reassess and refresh recommendations',
        'Disable assessments',
        'Ignore role requirements',
      ],
      correctIndex: 1,
      explanation: 'The closed loop is Profile → Assess → Recommend → Learn → Assess again.',
    },
  ] satisfies DemoQuestion[],
}

export const demoInsights = {
  headline:
    'Your profile indicates strong statistical foundations but a developing level of programming proficiency.',
  items: [
    'Advanced Python is currently your largest competency gap.',
    'Completing the recommended Python pathway could move your profile approximately 18% closer to the target role competency requirements.',
    'Statistical Analysis remains your strongest area and should be maintained through applied project work.',
  ],
  whyThisRecommendation: [
    'Target role (Senior Statistical Computing Officer) requires Python near proficiency 4.5.',
    'Current estimated Python level is 3.2 from profile signals and assessment items.',
    'Recent assessment performance showed weaknesses in data manipulation patterns.',
    'Prior learning covered SQL fundamentals but not advanced Python for statistical computing.',
  ],
}

export const demoAdmin = {
  kpis: {
    totalLearners: 1284,
    averageCompetency: 72,
    criticalSkillGaps: 186,
    assessmentsCompleted: 4820,
  },
  competencyDistribution: [
    { name: 'Statistical', value: 81 },
    { name: 'Technical', value: 68 },
    { name: 'Digital', value: 74 },
    { name: 'Governance', value: 70 },
    { name: 'Behavioural', value: 77 },
  ],
  topSkillGaps: [
    { name: 'Python', learners: 412 },
    { name: 'Cloud Computing', learners: 288 },
    { name: 'GIS', learners: 241 },
    { name: 'SQL', learners: 196 },
    { name: 'Machine Learning', learners: 174 },
  ],
  engagement: [
    { month: 'Apr', hours: 820 },
    { month: 'May', hours: 910 },
    { month: 'Jun', hours: 1040 },
    { month: 'Jul', hours: 990 },
    { month: 'Aug', hours: 1180 },
    { month: 'Sep', hours: 1260 },
  ],
  departments: [
    { name: 'Data & Analytics', learners: 340, competency: 76 },
    { name: 'Survey Operations', learners: 290, competency: 71 },
    { name: 'National Accounts', learners: 210, competency: 74 },
    { name: 'IT & DPI', learners: 180, competency: 69 },
    { name: 'Training Wing', learners: 264, competency: 73 },
  ],
  learners: [
    { name: 'Atharv Vij', department: 'Data & Analytics', competency: 78, gaps: 4 },
    { name: 'Meera Iyer', department: 'Survey Operations', competency: 81, gaps: 2 },
    { name: 'Rohan Das', department: 'National Accounts', competency: 69, gaps: 5 },
    { name: 'Priya Nair', department: 'IT & DPI', competency: 74, gaps: 3 },
    { name: 'Kabir Sen', department: 'Training Wing', competency: 72, gaps: 4 },
  ],
}

export const frameworkCategories = [
  {
    name: 'Statistical',
    items: ['Statistical Methods', 'Survey Methodology', 'Data Analysis', 'Statistical Modelling'],
  },
  {
    name: 'Technical',
    items: ['Python', 'SQL', 'Machine Learning', 'Big Data', 'GIS', 'Cloud Computing'],
  },
  {
    name: 'Digital',
    items: ['Data Visualization', 'Digital Workflows', 'Open Data Practices'],
  },
  {
    name: 'Governance',
    items: ['Data Governance', 'Cybersecurity Awareness', 'Data Privacy', 'Digital Public Infrastructure'],
  },
  {
    name: 'Behavioural',
    items: ['Leadership', 'Communication', 'Project Management', 'Decision Making'],
  },
] as const
