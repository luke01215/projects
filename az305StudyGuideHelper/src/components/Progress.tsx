import { useState, useEffect } from 'react';
import { StudyProgress } from '../types';

const Progress = () => {
  const [progress, setProgress] = useState<StudyProgress>({
    flashcardsReviewed: 0,
    quizzesTaken: 0,
    correctAnswers: 0,
    totalQuestions: 0,
    lastStudyDate: '',
    domainScores: {}
  });

  useEffect(() => {
    const saved = localStorage.getItem('studyProgress');
    if (saved) {
      try {
        setProgress(JSON.parse(saved));
      } catch (error) {
        console.error('Failed to parse progress:', error);
      }
    }
  }, []);

  const resetProgress = () => {
    if (window.confirm('Are you sure you want to reset all progress? This cannot be undone.')) {
      localStorage.removeItem('studyProgress');
      localStorage.removeItem('spacedRepetition');
      setProgress({
        flashcardsReviewed: 0,
        quizzesTaken: 0,
        correctAnswers: 0,
        totalQuestions: 0,
        lastStudyDate: '',
        domainScores: {}
      });
    }
  };

  const overallAccuracy = progress.totalQuestions > 0
    ? Math.round((progress.correctAnswers / progress.totalQuestions) * 100)
    : 0;

  const lastStudy = progress.lastStudyDate
    ? new Date(progress.lastStudyDate).toLocaleDateString()
    : 'Never';

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-8">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-6">
          Study Progress
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
            <div className="text-3xl font-bold mb-2">{progress.flashcardsReviewed}</div>
            <div className="text-sm opacity-90">Flashcards Reviewed</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white">
            <div className="text-3xl font-bold mb-2">{progress.quizzesTaken}</div>
            <div className="text-sm opacity-90">Quizzes Taken</div>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
            <div className="text-3xl font-bold mb-2">{overallAccuracy}%</div>
            <div className="text-sm opacity-90">Overall Accuracy</div>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-6 text-white">
            <div className="text-3xl font-bold mb-2">{progress.totalQuestions}</div>
            <div className="text-sm opacity-90">Questions Answered</div>
          </div>
        </div>

        <div className="mb-6">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Last Study Session: <span className="font-semibold text-gray-800 dark:text-gray-200">{lastStudy}</span>
          </div>
        </div>

        {Object.keys(progress.domainScores).length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
              Performance by Domain
            </h3>
            <div className="space-y-4">
              {Object.entries(progress.domainScores).map(([domain, scores]) => {
                const accuracy = scores.total > 0
                  ? Math.round((scores.correct / scores.total) * 100)
                  : 0;
                
                return (
                  <div key={domain} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {domain}
                      </span>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {scores.correct}/{scores.total} ({accuracy}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                      <div
                        className={`h-2.5 rounded-full transition-all ${
                          accuracy >= 80
                            ? 'bg-green-500'
                            : accuracy >= 60
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${accuracy}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={resetProgress}
            className="px-6 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-semibold transition-colors"
          >
            Reset All Progress
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-8">
        <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          Study Tips
        </h3>
        <ul className="space-y-2 text-gray-600 dark:text-gray-400">
          <li className="flex items-start">
            <span className="mr-2">📅</span>
            <span>Study regularly - aim for at least 30 minutes per day</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">🔄</span>
            <span>Review flashcards marked as "Hard" more frequently</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">🎯</span>
            <span>Focus on domains where your accuracy is below 70%</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">📝</span>
            <span>Take practice quizzes to test your understanding</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">📖</span>
            <span>Use the Reference guide to deepen your knowledge</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default Progress;
