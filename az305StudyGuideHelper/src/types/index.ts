export interface Flashcard {
  id: string;
  domain: string;
  question: string;
  answer: string;
  difficulty: 'easy' | 'medium' | 'hard';
  tags: string[];
}

export interface QuizQuestion {
  id: string;
  domain: string;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
  difficulty: 'easy' | 'medium' | 'hard';
}

export interface StudyProgress {
  flashcardsReviewed: number;
  quizzesTaken: number;
  correctAnswers: number;
  totalQuestions: number;
  lastStudyDate: string;
  domainScores: Record<string, { correct: number; total: number }>;
}

export interface SpacedRepetitionData {
  cardId: string;
  nextReviewDate: string;
  interval: number;
  easeFactor: number;
  reviewCount: number;
}
