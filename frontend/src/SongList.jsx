import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './SongList.css';
import './App.css'; // For lyrics styling

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

export default function SongList() {
  const [songs, setSongs] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [selectedSong, setSelectedSong] = useState(null);
  const [editingSongId, setEditingSongId] = useState(null);
  const [editForm, setEditForm] = useState({ title: '', artist: '' });

  useEffect(() => {
    fetchSongs(page);
  }, [page]);

  const fetchSongs = async (p) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/songlist?page=${p}`);
      if (res.ok) {
        const data = await res.json();
        setSongs(data.songs);
        setTotalPages(data.total_pages);
      }
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleSongClick = (song) => {
    if (editingSongId) return; // Prevent expanding while editing
    if (selectedSong && selectedSong.id === song.id) {
      setSelectedSong(null); // Toggle off
    } else {
      setSelectedSong(song);
    }
  };

  const handleEditClick = (e, song) => {
    e.stopPropagation();
    setEditingSongId(song.id);
    setEditForm({ 
      title: song.title || '', 
      artist: song.artist || '',
      lyrics: song.lyrics ? JSON.parse(JSON.stringify(song.lyrics)) : ''
    });
  };

  const handleCancelEdit = (e) => {
    e.stopPropagation();
    setEditingSongId(null);
  };

  const handleSaveEdit = async (e, id) => {
    e.stopPropagation();
    try {
      const res = await fetch(`/api/songlist/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editForm),
      });
      if (res.ok) {
        setSongs(songs.map(s => s.id === id ? { ...s, ...editForm } : s));
        setEditingSongId(null);
        if (selectedSong?.id === id) {
          setSelectedSong({ ...selectedSong, ...editForm });
        }
      } else {
        alert('수정에 실패했습니다.');
      }
    } catch (err) {
      console.error(err);
      alert('오류가 발생했습니다.');
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (window.confirm('정말로 삭제하시겠습니까?')) {
      try {
        const res = await fetch(`/api/songlist/${id}`, { method: 'DELETE' });
        if (res.ok) {
          setSongs(songs.filter(s => s.id !== id));
          if (selectedSong?.id === id) {
            setSelectedSong(null);
          }
        } else {
          alert('삭제에 실패했습니다.');
        }
      } catch (err) {
        console.error(err);
        alert('오류가 발생했습니다.');
      }
    }
  };

  return (
    <div className="songlist-container light-mode">
      <header className="songlist-header">
        <Link to="/" className="back-link">← 처음으로 (검색하기)</Link>
        <h1>저장된 가사 목록</h1>
      </header>
      
      {totalPages > 1 && (
        <div className="pagination">
          <button 
            disabled={page === 1} 
            onClick={() => setPage(p => p - 1)}
          >
            이전
          </button>
          <span>{page} / {totalPages}</span>
          <button 
            disabled={page === totalPages} 
            onClick={() => setPage(p => p + 1)}
          >
            다음
          </button>
        </div>
      )}

      {loading ? (
        <div className="loading">불러오는 중...</div>
      ) : (
        <div className="song-grid">
          {songs.length === 0 ? (
            <div className="no-songs">저장된 가사가 없습니다. 곡을 검색해서 가사를 저장해 보세요!</div>
          ) : (
            songs.map(song => (
              <div key={song.id} className="song-item">
                <div 
                  className={`song-card ${selectedSong?.id === song.id ? 'selected' : ''}`}
                  onClick={() => handleSongClick(song)}
                >
                  <img src={song.cover_url || '/favicon.svg'} alt="cover" className="song-cover" />
                  <div className="song-info">
                    {editingSongId === song.id ? (
                      <div className="edit-mode-container" onClick={e => e.stopPropagation()}>
                        <div className="song-id-display">ID: {song.id} (편집 불가)</div>
                        <input 
                          type="text" 
                          value={editForm.title} 
                          onChange={e => setEditForm({...editForm, title: e.target.value})}
                          placeholder="곡명"
                          className="edit-input"
                        />
                        <input 
                          type="text" 
                          value={editForm.artist} 
                          onChange={e => setEditForm({...editForm, artist: e.target.value})}
                          placeholder="가수"
                          className="edit-input"
                        />
                        <div className="edit-actions">
                          <button className="save-btn" onClick={(e) => handleSaveEdit(e, song.id)}>저장</button>
                          <button className="cancel-btn" onClick={handleCancelEdit}>취소</button>
                        </div>
                        <div className="edit-lyrics-section">
                          <div className="edit-lyrics-title">가사 편집</div>
                          {typeof editForm.lyrics === 'string' ? (
                            <textarea 
                              value={editForm.lyrics}
                              onChange={e => setEditForm({...editForm, lyrics: e.target.value})}
                              className="edit-textarea"
                              rows={5}
                            />
                          ) : (
                            <div className="edit-lyrics-list">
                              {editForm.lyrics?.map((line, idx) => (
                                <div key={idx} className="edit-lyric-line">
                                  <input 
                                    type="text" 
                                    value={line.original || ''} 
                                    onChange={e => {
                                      const newLyrics = [...editForm.lyrics];
                                      newLyrics[idx].original = e.target.value;
                                      setEditForm({...editForm, lyrics: newLyrics});
                                    }}
                                    placeholder="원문"
                                    className="edit-lyric-input"
                                  />
                                  <input 
                                    type="text" 
                                    value={line.pronunciation || ''} 
                                    onChange={e => {
                                      const newLyrics = [...editForm.lyrics];
                                      newLyrics[idx].pronunciation = e.target.value;
                                      setEditForm({...editForm, lyrics: newLyrics});
                                    }}
                                    placeholder="발음"
                                    className="edit-lyric-input"
                                  />
                                  <input 
                                    type="text" 
                                    value={line.translation || ''} 
                                    onChange={e => {
                                      const newLyrics = [...editForm.lyrics];
                                      newLyrics[idx].translation = e.target.value;
                                      setEditForm({...editForm, lyrics: newLyrics});
                                    }}
                                    placeholder="해석"
                                    className="edit-lyric-input"
                                  />
                                  <button 
                                    className="delete-line-btn" 
                                    onClick={() => {
                                      const newLyrics = editForm.lyrics.filter((_, i) => i !== idx);
                                      setEditForm({...editForm, lyrics: newLyrics});
                                    }}
                                  >✕</button>
                                </div>
                              ))}
                              <button 
                                className="add-line-btn" 
                                onClick={() => {
                                  setEditForm({...editForm, lyrics: [...(editForm.lyrics || []), {original: '', pronunciation: '', translation: ''}]});
                                }}
                              >+ 줄 추가</button>
                            </div>
                          )}
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="song-title">{song.title || '알 수 없는 곡명'}</div>
                        <div className="song-artist">{song.artist || '알 수 없는 가수'}</div>
                        <div className="song-likes" style={{ fontSize: '0.85rem', color: '#ff4d4d', marginTop: '4px' }}>
                          ❤️ {song.likes || 0}
                        </div>
                        <div className="song-id-display">ID: {song.id}</div>
                      </>
                    )}
                  </div>
                  {editingSongId !== song.id && (
                    <div className="song-card-actions">
                      <button className="edit-btn" onClick={(e) => handleEditClick(e, song)}>편집</button>
                      <button className="delete-btn" onClick={(e) => handleDelete(e, song.id)}>삭제</button>
                    </div>
                  )}
                </div>
                
                {selectedSong?.id === song.id && (() => {
                  let dynamicStyles = {};
                  if (song.theme_colors && song.theme_colors.dominant) {
                    const [r, g, b] = song.theme_colors.dominant;
                    const palette = song.theme_colors.palette || [];
                    
                    const getRelativeLuminance = (r, g, b) => {
                      const [rs, gs, bs] = [r, g, b].map(c => {
                        c = c / 255;
                        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
                      });
                      return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
                    };
                    
                    const bgLuminance = getRelativeLuminance(r, g, b);
                    
                    let bestTextColor = [r, g, b];
                    let bestContrast = 0;
                    for (const c of palette) {
                      const lum = getRelativeLuminance(c[0], c[1], c[2]);
                      const contrast = (Math.max(bgLuminance, lum) + 0.05) / (Math.min(bgLuminance, lum) + 0.05);
                      if (contrast > bestContrast) {
                        bestContrast = contrast;
                        bestTextColor = c;
                      }
                    }


                    dynamicStyles = {
                      '--bg-primary': `rgb(${r}, ${g}, ${b})`,
                      '--bg-secondary': `rgba(${bestTextColor[0]}, ${bestTextColor[1]}, ${bestTextColor[2]}, 0.1)`,
                      '--text-primary': `rgb(${bestTextColor[0]}, ${bestTextColor[1]}, ${bestTextColor[2]})`,
                      '--text-secondary': `rgba(${bestTextColor[0]}, ${bestTextColor[1]}, ${bestTextColor[2]}, 0.8)`,
                      '--border-color': `rgba(${bestTextColor[0]}, ${bestTextColor[1]}, ${bestTextColor[2]}, 0.3)`,
                      '--shadow-color': bgLuminance < 0.5 ? 'rgba(0,0,0,0.6)' : 'rgba(0,0,0,0.15)'
                    };
                  }
                  return (
                    <div className="expanded-song-details" style={dynamicStyles}>
                    <div className="song-metadata-grid">
                       <div className="meta-item">
                           <span className="meta-label">재생 횟수</span>
                           <span className="meta-value">{song.play_count || 0}회</span>
                       </div>
                       <div className="meta-item">
                           <span className="meta-label">저장 일시</span>
                           <span className="meta-value">{song.created_at ? new Date(song.created_at).toLocaleString() : '-'}</span>
                       </div>
                       <div className="meta-item">
                           <span className="meta-label">번역된 제목</span>
                           <span className="meta-value">{song.translated_title_info?.translation || '-'}</span>
                       </div>
                       <div className="meta-item">
                           <span className="meta-label">번역된 앨범명</span>
                           <span className="meta-value">{song.translated_album_info?.translation || '-'}</span>
                       </div>
                       <div className="meta-item">
                           <span className="meta-label">유튜브 연결</span>
                           <span className="meta-value">
                               {song.youtube_video_id ? (
                                   <a href={`https://youtu.be/${song.youtube_video_id}`} target="_blank" rel="noopener noreferrer">
                                       {song.youtube_video_id} 🔗
                                   </a>
                               ) : '-'}
                           </span>
                       </div>
                       <div className="meta-item">
                           <span className="meta-label">테마 색상</span>
                           <span className="meta-value">
                               {song.theme_colors ? (
                                   <span className="color-swatch-container">
                                       <span className="color-swatch" style={{backgroundColor: `rgb(${song.theme_colors.dominant.join(',')})`}} title="Dominant"></span>
                                       {song.theme_colors.palette?.map((c, i) => (
                                           <span key={i} className="color-swatch" style={{backgroundColor: `rgb(${c.join(',')})`}} title={`Palette ${i+1}`}></span>
                                       ))}
                                   </span>
                               ) : '-'}
                           </span>
                       </div>
                    </div>
                    
                    <h3 className="lyrics-heading">가사 데이터</h3>
                    <div className="lyrics-container list-lyrics" style={{ borderTop: 'none', padding: '0' }}>
                      {typeof song.lyrics === 'string' ? (
                        <div className="lyrics-string-container">
                          <pre className="lyrics-text">{song.lyrics}</pre>
                        </div>
                      ) : (
                        song.lyrics?.map((line, idx) => (
                          <div key={idx} className="lyrics-line">
                            <div className="lyrics-original">{line.original}</div>
                            {line.pronunciation && line.pronunciation !== line.original && (
                              <div className="lyrics-pronunciation">{renderPhonetic(line.pronunciation)}</div>
                            )}
                            {line.translation && (
                              <div className="lyrics-translation">{line.translation}</div>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )})()}
              </div>
            ))
          )}
        </div>
      )}
      
      {totalPages > 1 && (
        <div className="pagination">
          <button 
            disabled={page === 1} 
            onClick={() => setPage(p => p - 1)}
          >
            이전
          </button>
          <span>{page} / {totalPages}</span>
          <button 
            disabled={page === totalPages} 
            onClick={() => setPage(p => p + 1)}
          >
            다음
          </button>
        </div>
      )}
    </div>
  );
}
