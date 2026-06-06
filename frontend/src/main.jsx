import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import SongList from './SongList.jsx'
import JapaneseQuiz from './JapaneseQuiz.jsx'
import About from './About.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/song/:id" element={<App />} />
        <Route path="/songlist" element={<SongList />} />
        <Route path="/japanese-quiz" element={<JapaneseQuiz />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
