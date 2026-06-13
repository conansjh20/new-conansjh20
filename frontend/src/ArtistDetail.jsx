import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import './App.css';
import { translateKoreanToJapanese } from './translator';

const CommentForm = ({ isReply = false, onSubmit, onCancel }) => {
  const [nickname, setNickname] = useState('');
  const [password, setPassword] = useState('');
  const [content, setContent] = useState('');
  
  const [trackQuery, setTrackQuery] = useState('');
  const [trackResults, setTrackResults] = useState([]);
  const [selectedTrack, setSelectedTrack] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isTrackJpMode, setIsTrackJpMode] = useState(false);

  const handleTrackSearch = async (e) => {
    e.preventDefault();
    if (!trackQuery.trim()) return;
    setIsSearching(true);
    try {
      let finalQuery = trackQuery;
      if (isTrackJpMode) {
        finalQuery = translateKoreanToJapanese(trackQuery);
        setTrackQuery(finalQuery);
      }
      const res = await fetch(`/api/spotify/search?q=${encodeURIComponent(finalQuery)}`);
      const data = await res.json();
      if (data.tracks && data.tracks.items) {
        setTrackResults(data.tracks.items);
      } else {
        setTrackResults([]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!nickname || !password || !content || !selectedTrack) {
      alert("닉네임, 비밀번호, 내용, 첨부할 노래를 모두 입력해주세요.");
      return;
    }
    onSubmit({ nickname, password, content, selectedTrack });
  };

  return (
    <div style={{ marginBottom: isReply ? '10px' : '30px', marginTop: isReply ? '10px' : '0', animation: 'fadeIn 0.2s ease-in-out' }}>
      <form onSubmit={handleSubmit} style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
        <div style={{ display: 'flex', gap: '8px', marginBottom: '10px' }}>
          <input type="text" placeholder="닉네임" value={nickname} onChange={e => setNickname(e.target.value)} required style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid var(--border-color)', fontSize: '0.9rem' }} />
          <input type="password" placeholder="비밀번호" value={password} onChange={e => setPassword(e.target.value)} required style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid var(--border-color)', fontSize: '0.9rem' }} />
        </div>
        
        <textarea 
          placeholder="내용을 입력하세요..." 
          value={content} 
          onChange={e => setContent(e.target.value)} 
          required 
          style={{ width: '100%', height: '60px', padding: '8px', borderRadius: '4px', border: '1px solid var(--border-color)', marginBottom: '10px', boxSizing: 'border-box', resize: 'vertical', fontSize: '0.9rem' }} 
        />

        <div style={{ marginBottom: '10px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '0.8rem' }}>🎵 노래 첨부 (필수)</label>
          {!selectedTrack ? (
            <>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input 
                  type="text" 
                  placeholder="검색..." 
                  value={trackQuery}
                  onChange={e => setTrackQuery(e.target.value)}
                  style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid var(--border-color)', fontSize: '0.9rem' }}
                />
                <button 
                  type="button" 
                  className={`j-toggle-btn ${isTrackJpMode ? 'active' : ''}`} 
                  onClick={() => setIsTrackJpMode(!isTrackJpMode)} 
                  title="Toggle Japanese Input"
                >J</button>
                <button type="button" onClick={handleTrackSearch} style={{ padding: '0 15px', borderRadius: '4px', background: 'var(--text-secondary)', color: '#fff', border: 'none', cursor: 'pointer', fontSize: '0.9rem' }}>검색</button>
              </div>
              {isSearching && <div style={{ marginTop: '5px', fontSize: '0.8rem' }}>검색 중...</div>}
              {trackResults.length > 0 && (
                <div className="results-dropdown" style={{ display: 'block', position: 'relative', marginTop: '5px', maxHeight: '150px', overflowY: 'auto' }}>
                  {trackResults.map((track) => (
                    <div 
                      key={track.id} 
                      className="result-item"
                      onClick={() => {
                        setSelectedTrack(track);
                        setTrackResults([]);
                        setTrackQuery('');
                      }}
                      style={{ padding: '6px' }}
                    >
                      <img src={track.album?.images?.[0]?.url} alt="album" className="result-item-cover" style={{ width: '30px', height: '30px' }} />
                      <div className="result-item-info">
                        <div className="result-item-title" style={{ fontSize: '0.85rem' }}>{track.name}</div>
                        <div className="result-item-artist" style={{ fontSize: '0.75rem' }}>{track.artists.map(a => a.name).join(', ')}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(0,0,0,0.05)', padding: '6px', borderRadius: '6px' }}>
              <img src={selectedTrack.album?.images?.[0]?.url} alt="track" style={{ width: '40px', height: '40px', borderRadius: '4px', objectFit: 'cover' }} />
              <div style={{ marginLeft: '8px', flex: 1 }}>
                <div style={{ fontWeight: 'bold', fontSize: '0.85rem' }}>{selectedTrack.name}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{selectedTrack.artists.map(a => a.name).join(', ')}</div>
              </div>
              <button type="button" onClick={() => setSelectedTrack(null)} style={{ background: 'none', border: 'none', fontSize: '16px', cursor: 'pointer', padding: '5px' }} title="노래 다시 선택">❌</button>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
          {isReply && (
            <button type="button" onClick={onCancel} style={{ padding: '8px 15px', borderRadius: '4px', background: 'transparent', color: 'var(--text-secondary)', border: '1px solid var(--text-secondary)', cursor: 'pointer', fontSize: '0.9rem', fontWeight: 'bold' }}>취소</button>
          )}
          <button type="submit" disabled={!selectedTrack} style={{ padding: '8px 15px', borderRadius: '4px', background: selectedTrack ? 'var(--accent-color, #1db954)' : 'var(--text-secondary)', color: '#fff', border: 'none', cursor: selectedTrack ? 'pointer' : 'not-allowed', fontWeight: 'bold', fontSize: '0.9rem' }}>
            등록
          </button>
        </div>
      </form>
    </div>
  );
};

const CommentItem = ({ comment, depth = 0, replyTo, onSetReplyTo, onEdit, onDelete, onSubmitReply, childrenMap }) => {
  const children = childrenMap[comment.id] || [];
  
  return (
    <div style={{ 
      marginLeft: depth > 0 ? '15px' : '0',
      paddingLeft: depth > 0 ? '10px' : '0',
      borderLeft: depth > 0 ? '2px solid var(--border-color)' : 'none',
      marginTop: '8px'
    }}>
      <div style={{
        padding: '10px', 
        background: 'var(--bg-secondary)', 
        borderRadius: '6px',
        boxShadow: depth === 0 ? '0 1px 3px rgba(0,0,0,0.05)' : 'none'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
          <strong style={{ color: 'var(--text-primary)', fontSize: '0.9rem' }}>{depth > 0 ? '↳ ' : ''}{comment.nickname}</strong>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            {new Date(comment.created_at).toLocaleString()}
            <button onClick={() => { onSetReplyTo(comment.id); window.scrollTo({ top: 0, behavior: 'smooth' }); }} style={{ marginLeft: '8px', background: 'none', border: 'none', color: 'var(--accent-color, #1db954)', cursor: 'pointer', padding: 0 }}>답글</button>
            <button onClick={() => onEdit(comment.id, comment.content)} style={{ marginLeft: '8px', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: 0 }}>수정</button>
            <button onClick={() => onDelete(comment.id)} style={{ marginLeft: '8px', background: 'none', border: 'none', color: '#ff4d4f', cursor: 'pointer', padding: 0 }}>삭제</button>
          </span>
        </div>
        <p style={{ margin: '0 0 10px 0', lineHeight: '1.4', fontSize: '0.9rem', wordBreak: 'break-word', whiteSpace: 'pre-wrap' }}>{comment.content}</p>
        
        <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(0,0,0,0.05)', padding: '6px', borderRadius: '6px' }}>
          <Link to={`/song/${comment.track_id}`} title="재생 페이지로 이동" style={{ flexShrink: 0 }}>
            <img src={comment.track_image || '/favicon.svg'} alt="track" style={{ width: '40px', height: '40px', borderRadius: '4px', objectFit: 'cover', display: 'block' }} />
          </Link>
          <div style={{ marginLeft: '8px', flex: 1, overflow: 'hidden', minWidth: 0 }}>
            <Link to={`/song/${comment.track_id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
              <div style={{ fontWeight: 'bold', fontSize: '0.85rem', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>{comment.track_name}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>{comment.track_artist}</div>
            </Link>
          </div>
        </div>
      </div>
      
      {replyTo === comment.id && (
        <CommentForm 
          isReply={true} 
          onSubmit={(data) => onSubmitReply(comment.id, data)} 
          onCancel={() => onSetReplyTo(null)} 
        />
      )}

      {children.map(child => (
        <CommentItem 
          key={child.id} 
          comment={child} 
          depth={depth + 1} 
          replyTo={replyTo}
          onSetReplyTo={onSetReplyTo}
          onEdit={onEdit}
          onDelete={onDelete}
          onSubmitReply={onSubmitReply}
          childrenMap={childrenMap}
        />
      ))}
    </div>
  );
};

function ArtistDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [artist, setArtist] = useState(null);
  const [comments, setComments] = useState([]);

  // Reply state
  const [replyTo, setReplyTo] = useState(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchArtist();
    fetchComments();
  }, [id]);

  const fetchArtist = async () => {
    try {
      const res = await fetch(`/api/artists/${id}`);
      if (res.ok) {
        const data = await res.json();
        setArtist(data);
      } else {
        navigate('/artists');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchComments = async () => {
    try {
      const res = await fetch(`/api/artists/${id}/comments`);
      const data = await res.json();
      if (data.comments) {
        setComments(data.comments);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSubmitComment = async (parentId, data) => {
    try {
      const payload = {
        nickname: data.nickname,
        password: data.password,
        content: data.content,
        parent_id: parentId,
        track_id: data.selectedTrack.id,
        track_name: data.selectedTrack.name,
        track_artist: data.selectedTrack.artists.map(a => a.name).join(', '),
        track_image: data.selectedTrack.album?.images?.[0]?.url || ''
      };

      const res = await fetch(`/api/artists/${id}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const resData = await res.json();
      if (resData.success) {
        setReplyTo(null);
        setShowForm(false);
        fetchComments();
      } else {
        alert("댓글 작성에 실패했습니다.");
      }
    } catch (e) {
      console.error(e);
      alert("오류가 발생했습니다.");
    }
  };

  const handleDeleteComment = async (commentId) => {
    const pwd = prompt("삭제하려면 비밀번호를 입력하세요:");
    if (!pwd) return;

    try {
      const res = await fetch(`/api/artists/comments/${commentId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pwd })
      });
      const data = await res.json();
      if (data.success) {
        fetchComments();
      } else {
        alert(data.error || "비밀번호가 틀렸거나 삭제할 수 없습니다.");
      }
    } catch (e) {
      console.error(e);
      alert("오류가 발생했습니다.");
    }
  };

  const handleEditComment = async (commentId, oldContent) => {
    const pwd = prompt("수정하려면 비밀번호를 입력하세요:");
    if (!pwd) return;
    
    const newContent = prompt("새로운 내용을 입력하세요:", oldContent);
    if (!newContent || newContent === oldContent) return;

    try {
      const res = await fetch(`/api/artists/comments/${commentId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pwd, content: newContent })
      });
      const data = await res.json();
      if (data.success) {
        fetchComments();
      } else {
        alert(data.error || "비밀번호가 틀렸거나 수정할 수 없습니다.");
      }
    } catch (e) {
      console.error(e);
      alert("오류가 발생했습니다.");
    }
  };

  if (!artist) return <div className="loading">로딩 중...</div>;

  // Build comment tree
  const childrenMap = {};
  comments.forEach(c => {
    if (c.parent_id) {
      if (!childrenMap[c.parent_id]) childrenMap[c.parent_id] = [];
      childrenMap[c.parent_id].push(c);
    }
  });
  const rootComments = comments.filter(c => !c.parent_id);

  return (
    <main className="main-container light-mode">
      <div className="search-wrapper" style={{ width: '100%', maxWidth: '600px', margin: '0 auto', flex: 1, paddingBottom: '40px' }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px', marginTop: '10px', gap: '12px' }}>
          <Link to="/artists" style={{ color: 'var(--text-primary)', display: 'flex' }} title="목록으로"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg></Link>
          <h1 style={{ 
            margin: '0', 
            fontSize: '2rem', 
            fontWeight: '800', 
            color: 'var(--text-primary)',
            letterSpacing: '-0.5px',
            wordBreak: 'keep-all',
            lineHeight: '1.2'
          }}>
            {artist.name}
          </h1>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '20px', width: '100%' }}>
          <img 
            src={artist.image_url || '/favicon.svg'} 
            alt={artist.name}
            style={{
              maxWidth: '100%',
              maxHeight: '300px',
              borderRadius: '16px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
              objectFit: 'contain'
            }} 
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '15px' }}>
          <button 
            onClick={() => { setShowForm(!showForm); setReplyTo(null); }} 
            style={{ 
              padding: '8px 16px', 
              borderRadius: '20px', 
              background: showForm && !replyTo ? 'transparent' : 'var(--text-primary)', 
              color: showForm && !replyTo ? 'var(--text-secondary)' : 'var(--bg-primary)', 
              border: `1px solid ${showForm && !replyTo ? 'var(--text-secondary)' : 'var(--text-primary)'}`, 
              cursor: 'pointer', 
              fontWeight: '600', 
              fontSize: '0.95rem', 
              display: 'flex', 
              alignItems: 'center', 
              gap: '6px',
              transition: 'all 0.2s ease'
            }}
          >
            {showForm && !replyTo ? (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M18 6L6 18M6 6l12 12"/></svg>
                작성 취소
              </>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M12 5v14M5 12h14"/></svg>
                새 글 작성
              </>
            )}
          </button>
        </div>

        {showForm && !replyTo && (
          <CommentForm 
            isReply={false}
            onSubmit={(data) => handleSubmitComment(null, data)}
            onCancel={() => setShowForm(false)}
          />
        )}

        <div>
          {rootComments.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '40px 0', fontSize: '0.9rem' }}>아직 등록된 게시글이 없습니다. 첫 글의 주인공이 되어보세요!</p>
          ) : (
            rootComments.map(comment => (
              <CommentItem 
                key={comment.id} 
                comment={comment} 
                depth={0} 
                replyTo={replyTo}
                onSetReplyTo={(cid) => { setReplyTo(cid); setShowForm(false); }}
                onEdit={handleEditComment}
                onDelete={handleDeleteComment}
                onSubmitReply={handleSubmitComment}
                childrenMap={childrenMap}
              />
            ))
          )}
        </div>
      </div>
      <footer style={{ marginTop: 'auto', padding: '40px 20px 20px', width: '100%', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
        <Link to="/about" style={{ textDecoration: 'none', color: 'inherit', fontWeight: 'bold' }}>코난수집함</Link>, conansjh20@gmail.com
      </footer>
    </main>
  );
}

export default ArtistDetail;
