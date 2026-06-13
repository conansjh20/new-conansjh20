import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import './JapaneseQuiz.css';

export default function JapaneseQuiz() {
  const [words, setWords] = useState([]);
  const [shuffledWords, setShuffledWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState('start'); // start, playing, gameover
  const [quizType, setQuizType] = useState('jp-to-kr'); 
  const [currentStage, setCurrentStage] = useState(1);
  const [options, setOptions] = useState([]);
  const [timeLeft, setTimeLeft] = useState(5000);

  const animationRef = useRef(null);
  const lastTickRef = useRef(null);

  useEffect(() => {
    fetch('/data/japanese_words_1.json?v=' + Date.now())
      .then(res => res.json())
      .then(data => {
        // Some words might have empty meaning, filter them out just in case
        const validWords = data.filter(w => w.meaning && w.word);
        setWords(validWords);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load words", err);
        setLoading(false);
      });
      
    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, []);

  useEffect(() => {
    if (mode === 'playing') {
      const tick = (now) => {
        if (!lastTickRef.current) lastTickRef.current = now;
        const delta = now - lastTickRef.current;
        lastTickRef.current = now;
        
        setTimeLeft(prev => {
          const newTime = prev - delta;
          if (newTime <= 0) {
            handleGameOver();
            return 0;
          }
          return newTime;
        });
        
        animationRef.current = requestAnimationFrame(tick);
      };
      animationRef.current = requestAnimationFrame(tick);
      
      return () => cancelAnimationFrame(animationRef.current);
    }
  }, [mode, currentStage]);

  const startGame = (type) => {
    setQuizType(type);
    const shuffled = [...words].sort(() => Math.random() - 0.5);
    setShuffledWords(shuffled);
    setCurrentStage(1);
    setMode('playing');
    generateQuestion(shuffled, 1);
  };

  const generateQuestion = (wordList, stage) => {
    const currentWord = wordList[stage - 1];
    
    // Pick 4 random distractors
    const distractors = [];
    while (distractors.length < 4) {
      const randIdx = Math.floor(Math.random() * wordList.length);
      const randWord = wordList[randIdx];
      if (randIdx !== (stage - 1) && !distractors.find(w => w.word === randWord.word)) {
        distractors.push(randWord);
      }
    }
    
    const allOptions = [currentWord, ...distractors].sort(() => Math.random() - 0.5);
    setOptions(allOptions);
    setTimeLeft(5000);
    lastTickRef.current = performance.now();
  };

  const handleGameOver = () => {
    setMode('gameover');
    if (animationRef.current) cancelAnimationFrame(animationRef.current);
  };

  const handleAnswer = (selectedWord) => {
    const correctWord = shuffledWords[currentStage - 1];
    if (selectedWord.word === correctWord.word) {
      // Correct!
      if (currentStage >= shuffledWords.length) {
        // You win!
        setMode('gameover'); // Can handle win state later
      } else {
        const nextStage = currentStage + 1;
        setCurrentStage(nextStage);
        generateQuestion(shuffledWords, nextStage);
      }
    } else {
      // Wrong!
      handleGameOver();
    }
  };

  if (loading) {
    return <div className="quiz-loading">단어 데이터를 불러오는 중...</div>;
  }

  return (
    <div className="quiz-container light-mode">
      <div className="quiz-inner">
        <header className="quiz-header">
          <Link to="/" className="quiz-back-link">← 메인으로</Link>
          <h1 className="quiz-title"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight:'10px', verticalAlign:'middle'}}><rect x="2" y="6" width="20" height="12" rx="2" ry="2"></rect><line x1="6" y1="12" x2="10" y2="12"></line><line x1="8" y1="10" x2="8" y2="14"></line><line x1="15" y1="13" x2="15.01" y2="13"></line><line x1="18" y1="11" x2="18.01" y2="11"></line></svg>일본어 퀴즈 (5초 서바이벌)</h1>
        </header>

        {mode === 'start' && (
          <div className="quiz-card quiz-start-card">
            <h2>퀴즈 모드를 선택하세요</h2>
            <p>1700여 개의 단어! 각 문제당 단 <strong>5초</strong>의 시간이 주어집니다.</p>
            <div className="quiz-mode-buttons">
              <button className="jq-btn primary" onClick={() => startGame('jp-to-kr')}>
                🇯🇵 일본어 보고 🇰🇷 뜻 맞추기
              </button>
              <button className="jq-btn primary" onClick={() => startGame('kr-to-jp')}>
                🇰🇷 뜻 보고 🇯🇵 일본어 맞추기
              </button>
            </div>
          </div>
        )}

        {mode === 'playing' && shuffledWords.length > 0 && (
          <div className="quiz-card quiz-play-card">
            <div className="quiz-stage-info">
              <span>Stage {currentStage} / {shuffledWords.length}</span>
              <span className="quiz-time-text">{(timeLeft / 1000).toFixed(1)}초</span>
            </div>
            
            <div className="timer-bar-bg">
              <div 
                className="timer-bar-fill" 
                style={{ 
                  width: `${(timeLeft / 5000) * 100}%`,
                  backgroundColor: timeLeft > 2500 ? '#4caf50' : timeLeft > 1000 ? '#ff9800' : '#f44336'
                }}
              ></div>
            </div>

            <div className="quiz-question">
              {quizType === 'jp-to-kr' ? (
                <>
                  <div className="question-main">{shuffledWords[currentStage - 1].word}</div>
                  <div className="question-sub">{shuffledWords[currentStage - 1].reading} ({shuffledWords[currentStage - 1].k_reading})</div>
                </>
              ) : (
                <div className="question-main">{shuffledWords[currentStage - 1].meaning}</div>
              )}
            </div>

            <div className="quiz-options">
              {options.map((opt, idx) => (
                <button 
                  key={idx} 
                  className="quiz-option-btn"
                  onClick={() => handleAnswer(opt)}
                >
                  {quizType === 'jp-to-kr' ? opt.meaning : `${opt.word} (${opt.reading} / ${opt.k_reading})`}
                </button>
              ))}
            </div>
          </div>
        )}

        {mode === 'gameover' && (
          <div className="quiz-card quiz-gameover-card">
            <h2>{currentStage > shuffledWords.length ? '🎉 모든 스테이지 클리어! 🎉' : '💀 Game Over'}</h2>
            <p className="final-score-text">
              최종 도달 스테이지: <span className="highlight-score">{currentStage}</span> / {shuffledWords.length}
            </p>
            
            {currentStage <= shuffledWords.length && (
              <div className="wrong-answer-info">
                <p>정답은 <strong>{quizType === 'jp-to-kr' ? shuffledWords[currentStage - 1].meaning : `${shuffledWords[currentStage - 1].word} (${shuffledWords[currentStage - 1].reading} / ${shuffledWords[currentStage - 1].k_reading})`}</strong> 였습니다.</p>
              </div>
            )}

            <button className="jq-btn restart-btn" onClick={() => setMode('start')}>
              다시 시작하기
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
