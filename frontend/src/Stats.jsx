import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Stats.css';

function Stats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    document.title = "통계 - 코난수집함";
    fetch('/api/stats')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch stats');
        return res.json();
      })
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="stats-container">
      <div className="stats-header">
        <Link to="/" className="back-btn" title="홈으로 돌아가기"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight:'5px'}}><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>홈</Link>
        <h1 className="stats-title">수집함 통계</h1>
      </div>

      {loading ? (
        <div className="stats-loading">데이터를 불러오는 중입니다...</div>
      ) : error ? (
        <div className="stats-error">통계 데이터를 불러오지 못했습니다. ({error})</div>
      ) : (
        <div className="stats-content">
          <div className="visitor-cards">
            <div className="stat-card total-visitors">
              <div className="stat-icon">🌟</div>
              <div className="stat-info">
                <h3>누적 방문자</h3>
                <p className="stat-number">{stats.total_visitors.toLocaleString()}</p>
              </div>
            </div>
            
            <div className="stat-card today-visitors">
              <div className="stat-icon">🔥</div>
              <div className="stat-info">
                <h3>오늘 방문자</h3>
                <p className="stat-number">{stats.daily_visitors.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="top-songs-section">
            <h2>🎵 가장 많이 찾은 노래 TOP 20</h2>
            <div className="top-songs-list">
              {stats.top_songs && stats.top_songs.length > 0 ? (
                stats.top_songs.map((song, index) => (
                  <div 
                    key={song.id} 
                    className="top-song-item"
                    onClick={() => navigate(`/song/${song.id}`)}
                  >
                    <div className="song-rank">{index + 1}</div>
                    <img src={song.cover_url} alt="album cover" className="song-cover" />
                    <div className="song-details">
                      <div className="song-title">{song.title}</div>
                      <div className="song-artist">{song.artist}</div>
                    </div>
                    <div className="song-play-count">
                      <span className="play-icon">▶</span> {song.play_count.toLocaleString()}
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-songs">아직 조회된 노래가 없습니다.</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Stats;
