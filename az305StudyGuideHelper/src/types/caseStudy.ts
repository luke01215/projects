export interface CaseStudy {
  id: string;
  title: string;
  scenario: {
    company: string;
    industry: string;
    currentState: string[];
    requirements: string[];
    constraints: string[];
  };
  questions: CaseStudyQuestion[];
}

export interface CaseStudyQuestion {
  id: string;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
  topic: string;
}
