import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import SongList from './SongList.jsx'
import JapaneseQuiz from './JapaneseQuiz.jsx'
import About from './About.jsx'
import Stats from './Stats.jsx'
import ArtistBoard from './ArtistBoard.jsx'
import ArtistDetail from './ArtistDetail.jsx'

if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  document.title = '[로컬] 코난수집함';
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/song/:id" element={<App />} />
        <Route path="/songlist" element={<SongList />} />
        <Route path="/japanese-quiz" element={<JapaneseQuiz />} />
        <Route path="/about" element={<About />} />
        <Route path="/stats" element={<Stats />} />
        <Route path="/artists" element={<ArtistBoard />} />
        <Route path="/artists/:id" element={<ArtistDetail />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
