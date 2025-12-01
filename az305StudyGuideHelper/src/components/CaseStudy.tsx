import { useState } from 'react';
import { caseStudies } from '../data/caseStudies';

const CaseStudy = () => {
  const [selectedCaseStudy, setSelectedCaseStudy] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [showResults, setShowResults] = useState(false);
  const [showScenario, setShowScenario] = useState(true);

  const caseStudy = caseStudies[selectedCaseStudy];
  const question = caseStudy.questions[currentQuestion];

  const handleSelectCaseStudy = (index: number) => {
    setSelectedCaseStudy(index);
    setCurrentQuestion(0);
    setSelectedAnswer(null);
    setShowExplanation(false);
    setAnswers({});
    setShowResults(false);
    setShowScenario(false);
  };

  const handleAnswer = (answerIndex: number) => {
    if (selectedAnswer !== null) return;
    
    setSelectedAnswer(answerIndex);
    setShowExplanation(true);
    setAnswers({ ...answers, [question.id]: answerIndex });
  };

  const nextQuestion = () => {
    if (currentQuestion < caseStudy.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
      setShowExplanation(false);
    } else {
      setShowResults(true);
    }
  };

  const calculateScore = () => {
    let correct = 0;
    caseStudy.questions.forEach(q => {
      if (answers[q.id] === q.correctAnswer) {
        correct++;
      }
    });
    return { correct, total: caseStudy.questions.length };
  };

  if (showResults) {
    const { correct, total } = calculateScore();
    const percentage = Math.round((correct / total) * 100);

    return (
      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4">
            {caseStudy.title} - Results
          </h2>
          
          <div className="text-center mb-8">
            <div className={`text-6xl font-bold mb-4 ${
              percentage >= 80 ? 'text-green-500' : percentage >= 60 ? 'text-yellow-500' : 'text-red-500'
            }`}>
              {percentage}%
            </div>
            <p className="text-xl text-gray-600 dark:text-gray-400">
              {correct} out of {total} questions correct
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
              {percentage >= 80 ? 'Excellent! You understand this scenario well.' :
               percentage >= 60 ? 'Good job! Review the explanations to improve.' :
               'Review the scenario and explanations carefully.'}
            </p>
          </div>

          <div className="space-y-4 mb-8">
            <h3 className="font-semibold text-gray-800 dark:text-gray-200">Question Review:</h3>
            {caseStudy.questions.map((q, idx) => {
              const userAnswer = answers[q.id];
              const isCorrect = userAnswer === q.correctAnswer;
              return (
                <div key={q.id} className={`p-4 rounded-lg border-2 ${
                  isCorrect ? 'border-green-500 bg-green-50 dark:bg-green-900/20' : 'border-red-500 bg-red-50 dark:bg-red-900/20'
                }`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-gray-800 dark:text-gray-200">
                        Q{idx + 1}: {q.topic}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {q.question}
                      </p>
                    </div>
                    <span className={`ml-4 text-xl ${isCorrect ? 'text-green-600' : 'text-red-600'}`}>
                      {isCorrect ? '✓' : '✗'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex gap-4">
            <button
              onClick={() => handleSelectCaseStudy(selectedCaseStudy)}
              className="flex-1 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition-colors"
            >
              Retry This Case Study
            </button>
            <button
              onClick={() => setShowScenario(true)}
              className="flex-1 px-6 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg font-semibold transition-colors"
            >
              Back to Case Studies
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (showScenario) {
    return (
      <div className="space-y-6">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-2">
            Case Study Practice
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Read the scenario carefully, then answer questions about the architecture
          </p>
        </div>

        <div className="grid gap-4">
          {caseStudies.map((cs, idx) => (
            <button
              key={cs.id}
              onClick={() => handleSelectCaseStudy(idx)}
              className="text-left bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-all hover:scale-[1.02]"
            >
              <h3 className="text-xl font-bold text-indigo-600 dark:text-indigo-400 mb-2">
                {cs.title}
              </h3>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                {cs.scenario.company} • {cs.scenario.industry}
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500 dark:text-gray-500">
                  {cs.questions.length} questions
                </span>
                <span className="text-indigo-600 dark:text-indigo-400">→</span>
              </div>
            </button>
          ))}
        </div>

        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
          <h3 className="font-semibold text-yellow-800 dark:text-yellow-300 mb-2">
            💡 Case Study Tips
          </h3>
          <ul className="text-sm text-yellow-700 dark:text-yellow-400 space-y-1">
            <li>• Read the entire scenario before answering questions</li>
            <li>• Pay attention to requirements vs constraints</li>
            <li>• Consider cost, security, scalability, and compliance together</li>
            <li>• In the real exam, you cannot go back to case study questions</li>
            <li>• Take notes on key requirements while reading</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-indigo-600 dark:bg-indigo-800 rounded-xl shadow-xl p-6 text-white">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">{caseStudy.title}</h2>
          <button
            onClick={() => setShowScenario(true)}
            className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm transition-colors"
          >
            ← Back to List
          </button>
        </div>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold mb-2">📋 Current State</h3>
            <ul className="text-sm space-y-1 opacity-90">
              {caseStudy.scenario.currentState.map((item, idx) => (
                <li key={idx}>• {item}</li>
              ))}
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-2">🎯 Requirements</h3>
            <ul className="text-sm space-y-1 opacity-90">
              {caseStudy.scenario.requirements.map((item, idx) => (
                <li key={idx}>• {item}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-4">
          <h3 className="font-semibold mb-2">⚠️ Constraints</h3>
          <ul className="text-sm space-y-1 opacity-90">
            {caseStudy.scenario.constraints.map((item, idx) => (
              <li key={idx}>• {item}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <div className="text-sm font-semibold text-indigo-600 dark:text-indigo-400 mb-1">
              Question {currentQuestion + 1} of {caseStudy.questions.length}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-500">
              Topic: {question.topic}
            </div>
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Progress: {Object.keys(answers).length}/{caseStudy.questions.length} answered
          </div>
        </div>

        <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-6">
          {question.question}
        </h3>

        <div className="space-y-3 mb-6">
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
                <div className="flex items-start">
                  <span className="mr-3 font-semibold flex-shrink-0">
                    {String.fromCharCode(65 + index)}.
                  </span>
                  <span className="flex-1">{option}</span>
                  {selectedAnswer !== null && index === question.correctAnswer && (
                    <span className="ml-auto text-green-600 dark:text-green-400 flex-shrink-0">✓</span>
                  )}
                  {selectedAnswer === index && index !== question.correctAnswer && (
                    <span className="ml-auto text-red-600 dark:text-red-400 flex-shrink-0">✗</span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {showExplanation && (
          <div className="mb-6 p-6 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
            <div className="font-semibold text-indigo-900 dark:text-indigo-300 mb-2">
              {selectedAnswer === question.correctAnswer ? '✓ Correct!' : '✗ Incorrect'}
            </div>
            <p className="text-gray-700 dark:text-gray-300">
              {question.explanation}
            </p>
          </div>
        )}

        {selectedAnswer !== null && (
          <button
            onClick={nextQuestion}
            className="w-full px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition-colors"
          >
            {currentQuestion < caseStudy.questions.length - 1 ? 'Next Question →' : 'See Results'}
          </button>
        )}
      </div>

      <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 text-sm text-gray-600 dark:text-gray-400">
        <strong>Note:</strong> In the actual AZ-305 exam, you cannot go back to previous questions within a case study once you move forward. Practice answering carefully before proceeding.
      </div>
    </div>
  );
};

export default CaseStudy;
