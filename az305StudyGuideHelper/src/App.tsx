import { useState } from 'react';
import Flashcards from './components/Flashcards';
import Quiz from './components/Quiz';
import CaseStudy from './components/CaseStudy';
import Progress from './components/Progress';
import Reference from './components/Reference';

type Tab = 'flashcards' | 'quiz' | 'casestudy' | 'progress' | 'reference';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('flashcards');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-indigo-900 dark:text-indigo-300 mb-2">
            AZ-305 Study Guide
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Azure Solutions Architect Expert Certification
          </p>
        </header>

        <nav className="flex flex-wrap justify-center gap-4 mb-8">
          {[
            { id: 'flashcards', label: '📚 Flashcards', icon: '📚' },
            { id: 'quiz', label: '✍️ Practice Quiz', icon: '✍️' },
            { id: 'casestudy', label: '💼 Case Studies', icon: '💼' },
            { id: 'progress', label: '📊 Progress', icon: '📊' },
            { id: 'reference', label: '📖 Reference', icon: '📖' }
          ].map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as Tab)}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === id
                  ? 'bg-indigo-600 text-white shadow-lg scale-105'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-indigo-50 dark:hover:bg-gray-700'
              }`}
            >
              {label}
            </button>
          ))}
        </nav>

        <main className="max-w-4xl mx-auto">
          {activeTab === 'flashcards' && <Flashcards />}
          {activeTab === 'quiz' && <Quiz />}
          {activeTab === 'casestudy' && <CaseStudy />}
          {activeTab === 'progress' && <Progress />}
          {activeTab === 'reference' && <Reference />}
        </main>
      </div>
    </div>
  );
}

export default App;
