import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './App.css'; // Reuse existing styles
import { translateKoreanToJapanese } from './translator';

function ArtistBoard() {
  const navigate = useNavigate();
  const [artists, setArtists] = useState([]);
  
  const [artistQuery, setArtistQuery] = useState('');
  const [artistResults, setArtistResults] = useState([]);
  
  const [isSearching, setIsSearching] = useState(false);
  const [isArtistJpMode, setIsArtistJpMode] = useState(false);

  useEffect(() => {
    fetchArtists();
  }, []);

  const fetchArtists = async () => {
    try {
      const res = await fetch('/api/artists');
      const data = await res.json();
      if (data.artists) {
        setArtists(data.artists);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleArtistSearch = async (e) => {
    e.preventDefault();
    if (!artistQuery.trim()) return;
    setIsSearching(true);
    try {
      let finalQuery = artistQuery;
      if (isArtistJpMode) {
        finalQuery = translateKoreanToJapanese(artistQuery);
        setArtistQuery(finalQuery);
      }
      const res = await fetch(`/api/spotify/search/artist?q=${encodeURIComponent(finalQuery)}`);
      const data = await res.json();
      if (data.artists && data.artists.items) {
        setArtistResults(data.artists.items);
      } else {
        setArtistResults([]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsSearching(false);
    }
  };

  const handleCreateArtistBoard = async (artist) => {
    if (!artist) return;
    try {
      const payload = {
        id: artist.id,
        name: artist.name,
        image_url: artist.images?.[0]?.url || ''
      };

      const res = await fetch('/api/artists', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        navigate(`/artists/${data.artist_id}`);
      } else {
        alert("게시판 생성에 실패했습니다.");
      }
    } catch (e) {
      console.error(e);
      alert("오류가 발생했습니다.");
    }
  };

  return (
    <main className="main-container light-mode">
      <div className="search-wrapper" style={{ width: '100%', maxWidth: '600px', margin: '0 auto', flex: 1, paddingBottom: '40px' }}>
        <Link to="/" className="home-btn" title="홈으로" style={{ position: 'absolute', left: '20px', top: '30px', color: 'var(--text-primary)' }}><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg></Link>
        <h1 className="logo-text" onClick={() => navigate('/')} style={{ cursor: 'pointer', marginTop: '10px' }}>Artists</h1>
        
        <div className="search-and-results-wrapper" style={{ marginBottom: '15px' }}>
          <form onSubmit={handleArtistSearch} className="search-form" style={{ marginTop: '10px' }}>
            <div className="search-input-container">
              <input 
                type="text" 
                className="search-input" 
                value={artistQuery}
                onChange={(e) => setArtistQuery(e.target.value)}
                placeholder="아티스트 이름을 검색하세요..."
              />
              <button 
                type="button" 
                className={`j-toggle-btn ${isArtistJpMode ? 'active' : ''}`} 
                onClick={() => setIsArtistJpMode(!isArtistJpMode)} 
                title="Toggle Japanese Input"
              >J</button>
              <button type="submit" className="search-button">검색</button>
            </div>
          </form>
          {isSearching && <div className="loading">검색 중...</div>}
          {artistResults.length > 0 && (
            <div className="results-dropdown" style={{ display: 'block', position: 'relative', marginTop: '10px' }}>
              {artistResults.map((artist) => (
                <div 
                  key={artist.id} 
                  className="result-item"
                  onClick={() => {
                    handleCreateArtistBoard(artist);
                  }}
                >
                  <img src={artist.images?.[0]?.url || '/favicon.svg'} alt="artist" className="result-item-cover" style={{ borderRadius: '50%', objectPosition: 'center 30%' }} />
                  <div className="result-item-info">
                    <div className="result-item-title">{artist.name}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="playlist-section">
          <h2 className="playlist-title">LIST</h2>
          {artists.length === 0 ? (
            <p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>아직 등록된 아티스트가 없습니다. 첫 아티스트 게시판을 만들어보세요!</p>
          ) : (
            <div className="playlist-grid">
              {artists.map(artist => (
                <div 
                  key={artist.id} 
                  className="playlist-item"
                  onClick={() => navigate(`/artists/${artist.id}`)}
                  style={{ 
                    position: 'relative', 
                    padding: '0',
                    height: '100px', 
                    overflow: 'hidden',
                    display: 'flex',
                    alignItems: 'center',
                    background: 'var(--bg-secondary)',
                    borderRadius: '12px',
                    border: '1px solid var(--border-color)',
                    cursor: 'pointer',
                    marginBottom: '15px'
                  }}
                >
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '35%',
                    height: '100%',
                    backgroundImage: `url(${artist.image_url || '/favicon.svg'})`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center 30%',
                    WebkitMaskImage: 'linear-gradient(to right, rgba(0,0,0,1) 30%, rgba(0,0,0,0) 100%)',
                    maskImage: 'linear-gradient(to right, rgba(0,0,0,1) 30%, rgba(0,0,0,0) 100%)',
                  }} />
                  
                  <div style={{ 
                    position: 'relative', 
                    zIndex: 1, 
                    marginLeft: '35%', 
                    paddingRight: '20px',
                    width: '100%',
                    textAlign: 'right'
                  }}>
                    <div style={{ 
                      fontSize: '1.6rem', 
                      fontWeight: '800', 
                      color: 'var(--text-primary)',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      letterSpacing: '-0.5px'
                    }}>
                      {artist.name}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      <footer style={{ marginTop: 'auto', padding: '40px 20px 20px', width: '100%', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
        <Link to="/about" style={{ textDecoration: 'none', color: 'inherit', fontWeight: 'bold' }}>코난수집함</Link>, conansjh20@gmail.com
      </footer>
    </main>
  );
}

export default ArtistBoard;
