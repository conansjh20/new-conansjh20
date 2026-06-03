import { useState, useEffect, useRef } from 'react'

import './App.css'
import { translateKoreanToJapanese } from './translator'
import YouTube from 'react-youtube'
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom'

const renderPhonetic = (text) => {
  if (!text) return null;
  const parts = text.split(/(\*.)/g);
  return parts.map((part, i) => {
    if (part.startsWith('*')) {
      return <u key={i}>{part.slice(1)}</u>;
    }
    return <span key={i}>{part}</span>;
  });
};

const isEnglishLyric = (text) => {
  if (!text) return false;
  const hasCJK = /[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\u1100-\u11ff]/.test(text);
  const hasEnglish = /[a-zA-Z]/.test(text);
  return !hasCJK && hasEnglish;
};

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [selectedTrack, setSelectedTrack] = useState(null)
  const [isSearching, setIsSearching] = useState(false)
  const [isJapaneseMode, setIsJapaneseMode] = useState(false)
  const [youtubeVideoId, setYoutubeVideoId] = useState(null)
  const [youtubeVideoIds, setYoutubeVideoIds] = useState([])
  const [trackInfo, setTrackInfo] = useState(null)
  const [playlistTracks, setPlaylistTracks] = useState([])
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0)
  const [lyrics, setLyrics] = useState(null)
  const [dynamicTheme, setDynamicTheme] = useState(null)
  const [isManualInputOpen, setIsManualInputOpen] = useState(false)
  const [manualLyrics, setManualLyrics] = useState('')
  const [likesCount, setLikesCount] = useState(0)
  const [isLiked, setIsLiked] = useState(false)
  const [showHeartAnim, setShowHeartAnim] = useState(false)
  const searchWrapperRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (searchWrapperRef.current && !searchWrapperRef.current.contains(event.target)) {
        setResults([]);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    
    // Fetch latest playlist tracks
    fetch('/api/spotify/playlist/0CihGi2a3T0o1Ztpp6zOtF/latest')
      .then(res => res.json())
      .then(data => {
        if (data.tracks) {
          setPlaylistTracks(data.tracks);
        }
      })
      .catch(err => console.error("Playlist fetch failed", err));
      
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const [recentSearches, setRecentSearches] = useState(() => {
    try {
      const saved = localStorage.getItem('recentSearches');
      return saved ? JSON.parse(saved) : [];
    } catch (e) {
      return [];
    }
  });
  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    
    let finalQuery = query;
    if (isJapaneseMode) {
      finalQuery = translateKoreanToJapanese(query);
      setQuery(finalQuery); // Update input field to show translated text
    }
    
    if (!finalQuery.trim()) return;
    
    setIsSearching(true);
    try {
      const res = await fetch(`/api/spotify/search?q=${encodeURIComponent(finalQuery)}`);
      const data = await res.json();
      if (data.tracks && data.tracks.items) {
        setResults(data.tracks.items);
      } else {
        setResults([]);
      }
    } catch (error) {
      console.error("Search failed", error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSelectTrack = async (track) => {
    setSelectedTrack(track);
    setResults([]);
    setYoutubeVideoId(null);
    setYoutubeVideoIds([]);
    setCurrentVideoIndex(0);
    setIsManualInputOpen(false);
    setManualLyrics('');
    setLyrics("Loading lyrics...");
    setTrackInfo(null);
    setLikesCount(0);
    setIsLiked(false);
    
    fetch(`/api/song/${track.id}/likes`)
      .then(res => res.json())
      .then(data => {
        setLikesCount(data.likes || 0);
        const today = new Date().toISOString().split('T')[0];
        const likedData = JSON.parse(localStorage.getItem('liked_songs') || '{}');
        if (likedData[track.id] === today) {
          setIsLiked(true);
        } else {
          setIsLiked(false);
        }
      })
      .catch(err => console.error("Likes fetch failed", err));
      
    
    // Fetch Translation for Title and Album
    try {
      const infoRes = await fetch('/api/translate/info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: track.name,
          album: track.album?.name || ''
        })
      });
      if (infoRes.ok) {
        const infoData = await infoRes.json();
        setTrackInfo(infoData);
      }
    } catch (e) {
      console.error("Track info fetch failed", e);
    }
    
    const artist = track.artists[0]?.name || '';

    const newRecent = {
      id: track.id,
      title: track.name,
      artist: artist,
      track: track
    };
    
    setRecentSearches(prev => {
      const filtered = prev.filter(item => item.id !== newRecent.id);
      const updated = [newRecent, ...filtered].slice(0, 5);
      localStorage.setItem('recentSearches', JSON.stringify(updated));
      return updated;
    });

    // Fetch dynamic color from backend
    try {
      const imgUrl = track.album?.images[0]?.url;
      if (imgUrl) {
        fetch(`/api/color?url=${encodeURIComponent(imgUrl)}`)
          .then(res => res.json())
          .then(colorData => {
            if (colorData.dominant) {
              const [r, g, b] = colorData.dominant;
              const palette = colorData.palette || [];
              const c2 = palette.length > 1 ? palette[1] : [r, g, b];
              const c3 = palette.length > 2 ? palette[2] : [r, g, b];
              const c4 = palette.length > 3 ? palette[3] : c2;
              
              const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
              const isDark = luminance < 0.5;
              
              const getRelativeLuminance = (r, g, b) => {
                const [rs, gs, bs] = [r, g, b].map(c => {
                  c = c / 255;
                  return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
                });
                return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
              };

              const L1 = getRelativeLuminance(r, g, b);
              const L2 = getRelativeLuminance(c4[0], c4[1], c4[2]);
              
              const lighter = Math.max(L1, L2);
              const darker = Math.min(L1, L2);
              const contrastRatio = (lighter + 0.05) / (darker + 0.05);
              
              const finalBtnTextColor = contrastRatio < 3.0 ? (isDark ? '#ffffff' : '#121212') : `rgb(${c4[0]}, ${c4[1]}, ${c4[2]})`;
              
              setDynamicTheme({
                '--bg-primary': `rgb(${r}, ${g}, ${b})`,
                '--bg-secondary': isDark ? `rgba(255, 255, 255, 0.15)` : `rgba(0, 0, 0, 0.08)`,
                '--bg-hover': isDark ? `rgba(255, 255, 255, 0.25)` : `rgba(0, 0, 0, 0.15)`,
                '--text-primary': isDark ? '#ffffff' : '#121212',
                '--text-secondary': isDark ? 'rgba(255, 255, 255, 0.75)' : 'rgba(0, 0, 0, 0.75)',
                '--border-color': isDark ? `rgba(255, 255, 255, 0.2)` : `rgba(0, 0, 0, 0.2)`,
                '--accent-gradient': `linear-gradient(135deg, rgb(${c2[0]}, ${c2[1]}, ${c2[2]}) 0%, rgb(${c3[0]}, ${c3[1]}, ${c3[2]}) 100%)`,
                '--shadow-color': isDark ? 'rgba(0,0,0,0.6)' : 'rgba(0,0,0,0.15)',
                '--btn-text-color': finalBtnTextColor
              });
            }
          })
          .catch(err => console.error("Color fetch failed", err));
      }
    } catch (e) {
      console.error(e);
    }

    try {
      const q = encodeURIComponent(`${artist} ${track.name}`);
      const res = await fetch(`/api/youtube/search?q=${q}`);
      const data = await res.json();
      if (data.videoIds && data.videoIds.length > 0) {
        setYoutubeVideoIds(data.videoIds);
        setYoutubeVideoId(data.videoIds[0]);
      } else if (data.videoId) {
        setYoutubeVideoId(data.videoId);
        setYoutubeVideoIds([data.videoId]);
      }
    } catch (err) {
      console.error("Youtube search failed", err);
    }
    
    try {
      setLyrics("가사를 불러오는 중입니다...");
      const dbRes = await fetch(`/api/lyrics/${track.id}`);
      if (dbRes.ok) {
        const dbData = await dbRes.json();
        setLyrics(dbData);
        return; // Exit early, no need for LRCLIB!
      }
    } catch (err) {
      console.error("DB fetch failed", err);
    }

    try {
      const targetDuration = Math.round(track.duration_ms / 1000);
      const searchQuery = encodeURIComponent(`${artist} ${track.name}`);
      const url = `https://lrclib.net/api/search?q=${searchQuery}`;
      const res = await fetch(url);
      
      if (res.ok) {
        const data = await res.json();
        
        if (data && data.length > 0) {
          const isJapanese = (text) => /[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]/.test(text || '');
          
          // Sort by duration match
          const sortedData = data.sort((a, b) => Math.abs(a.duration - targetDuration) - Math.abs(b.duration - targetDuration));
          
          // 1. Closest duration AND Japanese text
          let selectedItem = sortedData.find(item => Math.abs(item.duration - targetDuration) <= 5 && isJapanese(item.syncedLyrics || item.plainLyrics));
          
          // 2. Any duration AND Japanese text
          if (!selectedItem) {
              selectedItem = sortedData.find(item => isJapanese(item.syncedLyrics || item.plainLyrics));
          }
          
          // 3. Closest duration with synced lyrics
          if (!selectedItem) {
              selectedItem = sortedData.find(item => Math.abs(item.duration - targetDuration) <= 5 && item.syncedLyrics);
          }
          
          // 4. Just the closest one
          if (!selectedItem) {
              selectedItem = sortedData[0];
          }

          const rawLyrics = selectedItem.syncedLyrics || selectedItem.plainLyrics || "";
          
          if (rawLyrics) {
            setLyrics("가사를 처리하고 번역하는 중입니다. (약 3~5초 소요)...");
            const processRes = await fetch('/api/lyrics/process', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ 
                lyrics: rawLyrics, 
                track_id: track.id,
                title: track.name,
                artist: artist,
                cover_url: track.album?.images?.[0]?.url || ''
              })
            });
            
            if (processRes.ok) {
              const processed = await processRes.json();
              setLyrics(processed);
            } else {
              setLyrics("가사 처리 중 오류가 발생했습니다.");
            }
          } else {
            setLyrics("가사를 찾을 수 없습니다 (Not found).");
          }
        } else {
          setLyrics("가사를 찾을 수 없습니다 (Not found).");
        }
      } else {
        setLyrics("가사를 찾을 수 없습니다 (Not found).");
      }
    } catch (err) {
      console.error("Lyrics fetch failed", err);
      setLyrics("가사를 불러오는 중 오류가 발생했습니다.");
    }
  };

  const handleArtistClick = async (artistId) => {
    if (!artistId) return;
    setIsSearching(true);
    try {
      const res = await fetch(`/api/spotify/artist/${artistId}/top-tracks`);
      const data = await res.json();
      if (data.tracks) {
        setResults(data.tracks.slice(0, 10));
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        setResults([]);
      }
    } catch (error) {
      console.error("Failed to fetch artist top tracks", error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleYoutubeError = (event) => {
    // If any error occurs (101, 150, 100, 2, 5, etc.), try the next video in the list
    if (youtubeVideoIds && currentVideoIndex < youtubeVideoIds.length - 1) {
      console.log(`Video ID ${youtubeVideoId} cannot be played (error ${event.data}), trying next one...`);
      const nextIndex = currentVideoIndex + 1;
      setCurrentVideoIndex(nextIndex);
      setYoutubeVideoId(youtubeVideoIds[nextIndex]);
    }
  };

  const handleManualLyricsSubmit = async () => {
    if (!manualLyrics.trim() || !selectedTrack) return;
    setIsManualInputOpen(false);
    setLyrics("가사를 처리하고 번역하는 중입니다. (약 3~5초 소요)...");
    try {
      const processRes = await fetch('/api/lyrics/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          lyrics: manualLyrics, 
          track_id: selectedTrack.id,
          title: selectedTrack.name,
          artist: selectedTrack.artists[0]?.name || '',
          cover_url: selectedTrack.album?.images?.[0]?.url || ''
        })
      });
      
      if (processRes.ok) {
        const processed = await processRes.json();
        setLyrics(processed);
      } else {
        setLyrics("가사 처리 중 오류가 발생했습니다.");
      }
    } catch (err) {
      console.error(err);
      setLyrics("가사 처리 중 오류가 발생했습니다.");
    }
  };

  const handleLike = async () => {
    if (!selectedTrack || isLiked) return;
    
    const today = new Date().toISOString().split('T')[0];
    const likedData = JSON.parse(localStorage.getItem('liked_songs') || '{}');
    
    if (likedData[selectedTrack.id] === today) {
      return; 
    }
    
    setShowHeartAnim(true);
    setTimeout(() => setShowHeartAnim(false), 1000);
    
    try {
      const res = await fetch(`/api/song/${selectedTrack.id}/like`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: selectedTrack.name,
          artist: selectedTrack.artists[0]?.name || '',
          cover_url: selectedTrack.album?.images?.[0]?.url || ''
        })
      });
      if (res.ok) {
        const data = await res.json();
        setLikesCount(data.likes);
        setIsLiked(true);
        likedData[selectedTrack.id] = today;
        localStorage.setItem('liked_songs', JSON.stringify(likedData));
      }
    } catch (e) {
      console.error("Like failed", e);
    }
  };

  return (
    <main 
      className={`main-container light-mode ${selectedTrack ? 'has-selection' : ''}`}
      style={dynamicTheme || {}}
    >
      <div className="search-wrapper">
        <h1 className="logo-text" onClick={() => window.location.href = '/'} style={{ cursor: 'pointer' }}>코난수집함</h1>
        
        <div className="search-and-results-wrapper" ref={searchWrapperRef}>
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-input-container">
              <svg className="search-icon" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"></path></svg>
              <input 
                type="text" 
                className="search-input" 
                value={query}
                onChange={handleQueryChange}
                placeholder={isJapaneseMode ? "한국어 발음으로 검색 (예: 사요나라)" : "Search for a song..."}
              />
              <button 
                type="button"
                className={`j-toggle-btn ${isJapaneseMode ? 'active' : ''}`}
                onClick={() => setIsJapaneseMode(!isJapaneseMode)}
                title="Toggle Japanese Input"
              >
                J
              </button>
              <button type="submit" className="search-button">Search</button>
            </div>
          </form>

          {recentSearches.length > 0 && (
            <div className="recent-searches">
              <div className="recent-searches-list">
                {recentSearches.map(item => (
                  <button 
                    key={item.id} 
                    className="recent-search-btn"
                    onClick={() => handleSelectTrack(item.track)}
                  >
                    {item.artist} - {item.title}
                  </button>
                ))}
              </div>
            </div>
          )}

          {isSearching && <div className="loading">Searching...</div>}
          
          {results.length > 0 && (
            <div className="results-dropdown">
              {results.map((track) => (
                <div 
                  key={track.id} 
                  className="result-item"
                  onClick={() => handleSelectTrack(track)}
                >
                  <img src={track.album.images[0]?.url} alt="album" className="result-item-cover" />
                  <div className="result-item-info">
                    <div className="result-item-title">{track.name}</div>
                    <div className="result-item-artist">{track.artists.map(a => a.name).join(', ')}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {(!selectedTrack && results.length === 0 && !isSearching) && playlistTracks.length > 0 && (
            <div className="playlist-section">
              <h2 className="playlist-title">PLAYLIST</h2>
              <div className="playlist-grid">
                {playlistTracks.map(track => (
                  <div 
                    key={track.id} 
                    className="playlist-item"
                    onClick={() => handleSelectTrack(track)}
                  >
                    <img src={track.album?.images[0]?.url} alt="album" className="playlist-cover" />
                    <div className="playlist-info">
                      <div className="playlist-track-name">{track.name}</div>
                      <div className="playlist-artist-name">{track.artists.map(a => a.name).join(', ')}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {selectedTrack && (
          <div className="selected-track-card">
            <div className="selected-track-info">
              <img 
                src={selectedTrack.album.images[0]?.url} 
                alt="Album Cover" 
                className="album-cover" 
              />
              <div className="track-details">
                <div className="track-title-wrapper">
                  <h2 className="track-title" style={{ margin: 0 }}>{selectedTrack.name}</h2>
                  <button 
                    className={`like-btn ${isLiked ? 'liked' : ''}`} 
                    onClick={handleLike}
                    disabled={isLiked}
                    title={isLiked ? "오늘 이미 좋아요를 누르셨습니다." : "좋아요"}
                  >
                    ❤️
                    {showHeartAnim && <div className="floating-heart">❤️</div>}
                  </button>
                </div>
                {trackInfo && trackInfo.title && trackInfo.title.translation && trackInfo.title.translation !== selectedTrack.name && !isEnglishLyric(selectedTrack.name) && (
                  <p className="track-meta-title" style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', marginTop: '4px', marginBottom: '8px', lineHeight: '1.2' }}>
                    {trackInfo.title.pronunciation && trackInfo.title.pronunciation !== selectedTrack.name ? <span style={{opacity: 0.8, marginRight: '4px'}}>({trackInfo.title.pronunciation})</span> : null}
                    <span style={{fontWeight: '500'}}>{trackInfo.title.translation}</span>
                  </p>
                )}
                <p className="track-artist">
                  {selectedTrack.artists.map((a, i) => (
                    <span key={a.id}>
                      <span 
                        onClick={() => handleArtistClick(a.id)}
                        style={{ cursor: 'pointer', textDecoration: 'none', color: 'var(--btn-text-color)' }}
                        title={`${a.name} 대표곡 검색`}
                      >
                        {a.name}
                      </span>
                      {i < selectedTrack.artists.length - 1 ? ', ' : ''}
                    </span>
                  ))}
                </p>
                <p className="track-album">Album: {selectedTrack.album.name}</p>
                {trackInfo && trackInfo.album && trackInfo.album.translation && trackInfo.album.translation !== selectedTrack.album.name && !isEnglishLyric(selectedTrack.album.name) && (
                  <p className="track-meta-album" style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px', marginBottom: '4px', lineHeight: '1.2' }}>
                    {trackInfo.album.pronunciation && trackInfo.album.pronunciation !== selectedTrack.album.name ? <span style={{opacity: 0.8, marginRight: '4px'}}>({trackInfo.album.pronunciation})</span> : null}
                    {trackInfo.album.translation}
                  </p>
                )}
                <p className="track-year">Released: {selectedTrack.album.release_date?.split('-')[0]}</p>
              </div>
            </div>
            {youtubeVideoId && (
              <div className="youtube-wrapper">
                <div className="youtube-container">
                  <YouTube 
                    videoId={youtubeVideoId}
                    opts={{ width: '100%', height: '100%', playerVars: { autoplay: 1 } }}
                    onError={handleYoutubeError}
                    className="youtube-iframe-wrapper"
                    iframeClassName="youtube-iframe"
                  />
                </div>
                {youtubeVideoIds && youtubeVideoIds.length > 1 && (
                  <button 
                    className="next-video-btn" 
                    onClick={() => {
                      const nextIndex = (currentVideoIndex + 1) % youtubeVideoIds.length;
                      setCurrentVideoIndex(nextIndex);
                      setYoutubeVideoId(youtubeVideoIds[nextIndex]);
                    }}
                  >
                    다른 영상 재생 ({currentVideoIndex + 1}/{youtubeVideoIds.length})
                  </button>
                )}
              </div>
            )}
            
            {lyrics && (
              <div className="lyrics-container">
                {typeof lyrics === 'string' ? (
                  <div className="lyrics-string-container">
                    <pre className="lyrics-text">{lyrics}</pre>
                    {(lyrics.includes("찾을 수 없습니다") || lyrics.includes("오류가 발생")) && (
                      <div className="manual-lyrics-wrapper">
                        {!isManualInputOpen ? (
                          <button 
                            className="manual-lyrics-btn" 
                            onClick={() => setIsManualInputOpen(true)}
                          >
                            가사 직접 입력하기
                          </button>
                        ) : (
                          <div className="manual-lyrics-input-area">
                            <textarea 
                              className="manual-lyrics-textarea"
                              placeholder="여기에 가사를 붙여넣으세요..."
                              value={manualLyrics}
                              onChange={(e) => setManualLyrics(e.target.value)}
                            />
                            <div className="manual-lyrics-actions">
                              <button className="manual-submit-btn" onClick={handleManualLyricsSubmit}>확인</button>
                              <button className="manual-cancel-btn" onClick={() => setIsManualInputOpen(false)}>취소</button>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  lyrics.map((line, idx) => (
                    <div key={idx} className="lyrics-line">
                      <div className="lyrics-original">{line.original}</div>
                      {line.pronunciation && line.pronunciation !== line.original && !isEnglishLyric(line.original) && (
                        <div className="lyrics-pronunciation">{renderPhonetic(line.pronunciation)}</div>
                      )}
                      {line.translation && (
                        <div className="lyrics-translation">{line.translation}</div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  )
}

export default App
