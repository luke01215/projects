import { useState, useEffect } from 'react';
import { flashcards } from '../data/flashcards';
import { Flashcard, SpacedRepetitionData } from '../types';

const Flashcards = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState<string>('all');
  const [filteredCards, setFilteredCards] = useState<Flashcard[]>(flashcards);
  const [spacedRepData, setSpacedRepData] = useState<Record<string, SpacedRepetitionData>>({});

  const domains = ['all', ...new Set(flashcards.map(card => card.domain))];

  useEffect(() => {
    const filtered = selectedDomain === 'all' 
      ? flashcards 
      : flashcards.filter(card => card.domain === selectedDomain);
    setFilteredCards(filtered);
    setCurrentIndex(0);
    setIsFlipped(false);
  }, [selectedDomain]);

  useEffect(() => {
    const saved = localStorage.getItem('spacedRepetition');
    if (saved) {
      setSpacedRepData(JSON.parse(saved));
    }
  }, []);

  const saveProgress = () => {
    const progress = JSON.parse(localStorage.getItem('studyProgress') || '{}');
    progress.flashcardsReviewed = (progress.flashcardsReviewed || 0) + 1;
    progress.lastStudyDate = new Date().toISOString();
    localStorage.setItem('studyProgress', JSON.stringify(progress));
  };

  const handleResponse = (quality: 'hard' | 'medium' | 'easy') => {
    const card = filteredCards[currentIndex];
    const now = new Date();
    const currentData = spacedRepData[card.id] || {
      cardId: card.id,
      nextReviewDate: now.toISOString(),
      interval: 1,
      easeFactor: 2.5,
      reviewCount: 0
    };

    let newInterval = currentData.interval;
    let newEaseFactor = currentData.easeFactor;

    // Simplified SM-2 algorithm
    if (quality === 'easy') {
      newInterval = currentData.interval * newEaseFactor;
      newEaseFactor = Math.min(newEaseFactor + 0.15, 2.5);
    } else if (quality === 'medium') {
      newInterval = currentData.interval * 1.2;
    } else {
      newInterval = 1;
      newEaseFactor = Math.max(newEaseFactor - 0.2, 1.3);
    }

    const nextReview = new Date(now.getTime() + newInterval * 24 * 60 * 60 * 1000);

    const updatedData = {
      ...spacedRepData,
      [card.id]: {
        cardId: card.id,
        nextReviewDate: nextReview.toISOString(),
        interval: newInterval,
        easeFactor: newEaseFactor,
        reviewCount: currentData.reviewCount + 1
      }
    };

    setSpacedRepData(updatedData);
    localStorage.setItem('spacedRepetition', JSON.stringify(updatedData));
    saveProgress();
    nextCard();
  };

  const nextCard = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev + 1) % filteredCards.length);
  };

  const prevCard = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev - 1 + filteredCards.length) % filteredCards.length);
  };

  if (filteredCards.length === 0) {
    return <div className="text-center text-gray-600 dark:text-gray-400">No flashcards available</div>;
  }

  const currentCard = filteredCards[currentIndex];
  const cardData = spacedRepData[currentCard.id];

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

      <div className="text-center text-sm text-gray-600 dark:text-gray-400">
        Card {currentIndex + 1} of {filteredCards.length}
        {cardData && (
          <span className="ml-4">
            Reviewed {cardData.reviewCount} times | Next: {Math.round(cardData.interval)} days
          </span>
        )}
      </div>

      <div 
        className="relative h-96 cursor-pointer perspective-1000"
        onClick={() => setIsFlipped(!isFlipped)}
      >
        <div className={`relative w-full h-full transition-transform duration-500 transform-style-3d ${
          isFlipped ? 'rotate-y-180' : ''
        }`}>
          <div className="absolute w-full h-full backface-hidden">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-8 h-full flex flex-col justify-center items-center">
              <div className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 mb-4">
                {currentCard.domain}
              </div>
              <p className="text-xl font-medium text-gray-800 dark:text-gray-200 text-center">
                {currentCard.question}
              </p>
              <div className="mt-6 text-sm text-gray-500 dark:text-gray-400">
                Click to reveal answer
              </div>
            </div>
          </div>

          <div className="absolute w-full h-full backface-hidden rotate-y-180">
            <div className="bg-indigo-600 dark:bg-indigo-800 rounded-xl shadow-xl p-8 h-full flex flex-col justify-center">
              <p className="text-lg text-white text-center mb-6">
                {currentCard.answer}
              </p>
              <div className="flex flex-wrap gap-2 justify-center mt-4">
                {currentCard.tags.map(tag => (
                  <span key={tag} className="px-3 py-1 bg-white/20 rounded-full text-xs text-white">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {isFlipped && (
        <div className="flex justify-center gap-4">
          <button
            onClick={(e) => { e.stopPropagation(); handleResponse('hard'); }}
            className="px-6 py-3 bg-red-500 hover:bg-red-600 text-white rounded-lg font-semibold transition-colors"
          >
            Hard
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); handleResponse('medium'); }}
            className="px-6 py-3 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg font-semibold transition-colors"
          >
            Medium
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); handleResponse('easy'); }}
            className="px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg font-semibold transition-colors"
          >
            Easy
          </button>
        </div>
      )}

      <div className="flex justify-between">
        <button
          onClick={prevCard}
          className="px-6 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg font-semibold transition-colors"
        >
          ← Previous
        </button>
        <button
          onClick={nextCard}
          className="px-6 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg font-semibold transition-colors"
        >
          Next →
        </button>
      </div>

      <style>{`
        .perspective-1000 { perspective: 1000px; }
        .transform-style-3d { transform-style: preserve-3d; }
        .backface-hidden { backface-visibility: hidden; }
        .rotate-y-180 { transform: rotateY(180deg); }
      `}</style>
    </div>
  );
};

export default Flashcards;
