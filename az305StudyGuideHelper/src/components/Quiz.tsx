import { useState, useEffect } from 'react';
import { quizQuestions } from '../data/quizQuestions';
import { QuizQuestion } from '../types';

const Quiz = () => {
  const [selectedDomain, setSelectedDomain] = useState<string>('all');
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [quizCompleted, setQuizCompleted] = useState(false);

  const domains = ['all', ...new Set(quizQuestions.map(q => q.domain))];

  useEffect(() => {
    startQuiz();
  }, [selectedDomain]);

  const startQuiz = () => {
    const filtered = selectedDomain === 'all'
      ? quizQuestions
      : quizQuestions.filter(q => q.domain === selectedDomain);
    
    // Shuffle questions
    const shuffled = [...filtered].sort(() => Math.random() - 0.5);
    setQuestions(shuffled);
    setCurrentQuestion(0);
    setSelectedAnswer(null);
    setShowExplanation(false);
    setScore({ correct: 0, total: 0 });
    setQuizCompleted(false);
  };

  const handleAnswer = (answerIndex: number) => {
    if (selectedAnswer !== null) return;
    
    setSelectedAnswer(answerIndex);
    setShowExplanation(true);
    
    const isCorrect = answerIndex === questions[currentQuestion].correctAnswer;
    const newScore = {
      correct: score.correct + (isCorrect ? 1 : 0),
      total: score.total + 1
    };
    setScore(newScore);

    // Save progress
    const progress = JSON.parse(localStorage.getItem('studyProgress') || '{}');
    progress.quizzesTaken = (progress.quizzesTaken || 0) + 1;
    progress.correctAnswers = (progress.correctAnswers || 0) + (isCorrect ? 1 : 0);
    progress.totalQuestions = (progress.totalQuestions || 0) + 1;
    progress.lastStudyDate = new Date().toISOString();
    
    const domain = questions[currentQuestion].domain;
    if (!progress.domainScores) progress.domainScores = {};
    if (!progress.domainScores[domain]) progress.domainScores[domain] = { correct: 0, total: 0 };
    progress.domainScores[domain].correct += isCorrect ? 1 : 0;
    progress.domainScores[domain].total += 1;
    
    localStorage.setItem('studyProgress', JSON.stringify(progress));
  };

  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
      setShowExplanation(false);
    } else {
      setQuizCompleted(true);
    }
  };

  if (questions.length === 0) {
    return <div className="text-center text-gray-600 dark:text-gray-400">Loading quiz...</div>;
  }

  if (quizCompleted) {
    const percentage = Math.round((score.correct / score.total) * 100);
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-8 text-center">
        <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          Quiz Completed! 🎉
        </h2>
        <div className="text-6xl font-bold text-indigo-600 dark:text-indigo-400 mb-4">
          {percentage}%
        </div>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
          You got {score.correct} out of {score.total} questions correct
        </p>
        <div className="space-y-4">
          <button
            onClick={startQuiz}
            className="w-full px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition-colors"
          >
            Retake Quiz
          </button>
          <div className="flex gap-2">
            {domains.map(domain => (
              <button
                key={domain}
                onClick={() => { setSelectedDomain(domain); startQuiz(); }}
                className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg text-sm font-medium transition-colors"
              >
                {domain === 'all' ? 'All' : domain.split(',')[0]}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const question = questions[currentQuestion];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2 justify-center">
        {domains.map(domain => (
          <button
            key={domain}
            onClick={() => setSelectedDomain(domain)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              selectedDomain === domain
                ? 'bg-indigo-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-indigo-50 dark:hover:bg-gray-700'
            }`}
          >
            {domain === 'all' ? 'All Domains' : domain}
          </button>
        ))}
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-8">
        <div className="flex justify-between items-center mb-6">
          <div className="text-sm font-semibold text-indigo-600 dark:text-indigo-400">
            Question {currentQuestion + 1} of {questions.length}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Score: {score.correct}/{score.total}
          </div>
        </div>

        <div className="mb-6">
          <div className="text-xs text-gray-500 dark:text-gray-500 mb-2">
            {question.domain}
          </div>
          <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-6">
            {question.question}
          </h3>

          <div className="space-y-3">
            {question.options.map((option, index) => {
              let buttonClass = 'w-full text-left px-6 py-4 rounded-lg border-2 transition-all ';
              
              if (selectedAnswer === null) {
                buttonClass += 'border-gray-200 dark:border-gray-700 hover:border-indigo-400 dark:hover:border-indigo-600 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200';
              } else if (index === question.correctAnswer) {
                buttonClass += 'border-green-500 bg-green-50 dark:bg-green-900/20 text-gray-800 dark:text-gray-200';
              } else if (index === selectedAnswer) {
                buttonClass += 'border-red-500 bg-red-50 dark:bg-red-900/20 text-gray-800 dark:text-gray-200';
              } else {
                buttonClass += 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400';
              }

              return (
                <button
                  key={index}
                  onClick={() => handleAnswer(index)}
                  disabled={selectedAnswer !== null}
                  className={buttonClass}
                >
                  <div className="flex items-center">
                    <span className="mr-3 font-semibold">
                      {String.fromCharCode(65 + index)}.
                    </span>
                    <span>{option}</span>
                    {selectedAnswer !== null && index === question.correctAnswer && (
                      <span className="ml-auto text-green-600 dark:text-green-400">✓</span>
                    )}
                    {selectedAnswer === index && index !== question.correctAnswer && (
                      <span className="ml-auto text-red-600 dark:text-red-400">✗</span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {showExplanation && (
          <div className="mt-6 p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
            <div className="font-semibold text-indigo-900 dark:text-indigo-300 mb-2">
              Explanation:
            </div>
            <p className="text-gray-700 dark:text-gray-300">
              {question.explanation}
            </p>
          </div>
        )}

        {selectedAnswer !== null && (
          <button
            onClick={nextQuestion}
            className="mt-6 w-full px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition-colors"
          >
            {currentQuestion < questions.length - 1 ? 'Next Question →' : 'Finish Quiz'}
          </button>
        )}
      </div>
    </div>
  );
};

export default Quiz;
