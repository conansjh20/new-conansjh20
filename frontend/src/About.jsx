import { Link } from 'react-router-dom';
import './index.css';

export default function About() {
  const techStack = [
    { name: 'Python', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg', link: 'https://www.python.org/' },
    { name: 'React', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/react/react-original.svg', link: 'https://react.dev/' },
    { name: 'YouTube API', icon: 'https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg', link: 'https://developers.google.com/youtube' },
    { name: 'Spotify API', icon: 'https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg', link: 'https://developer.spotify.com/' },
    { name: 'Gemini', icon: 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg', link: 'https://gemini.google.com/' },
    { name: 'Flask', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/flask/flask-original.svg', link: 'https://flask.palletsprojects.com/' },
    { name: 'MySQL', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/mysql/mysql-original.svg', link: 'https://www.mysql.com/' },
    { name: 'PythonAnywhere', icon: 'https://www.pythonanywhere.com/static/anywhere/images/PA-logo-snake-only.svg', link: 'https://www.pythonanywhere.com/' },
    { name: 'Vite', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/vitejs/vitejs-original.svg', link: 'https://vitejs.dev/' },
    { name: 'LRCLIB', icon: '/images/lrclib.png', link: 'https://lrclib.net/' }
  ];

  return (
    <div className="main-container light-mode" style={{ justifyContent: 'center', paddingTop: 0, minHeight: '100vh', overflow: 'hidden' }}>
      <div style={{ maxWidth: '900px', width: '100%', padding: '20px', textAlign: 'center' }}>
        <h1 style={{ marginBottom: '30px', color: 'var(--text-primary)', fontSize: '2.5rem' }}>코난수집함 소개</h1>
        
        <p style={{ 
          color: 'var(--text-secondary)', 
          marginBottom: '20px', 
          fontSize: '1.2rem', 
          lineHeight: '1.8',
          fontWeight: '500'
        }}>
          컴퓨터와 코딩, J-POP이 좋아 만든 홈페이지 입니다.<br/>
          <a href="https://github.com/conansjh20/new-conansjh20" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-primary)', textDecoration: 'none', fontWeight: 'bold' }}>
            GitHub: conansjh20/new-conansjh20
          </a>
        </p>

        <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'center' }}>
          <div style={{ 
            position: 'relative',
            width: '380px', 
            height: '380px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '10px 0'
          }}>
            {techStack.map((tech, idx) => {
              // Sunflower/Fermat's spiral pattern to naturally scatter them inside a circle
              const c = 60; // 60 is the sweet spot for 56px icons: very dense but guaranteed no overlap
              const angle = idx * 2.39996; // Golden angle (137.5 degrees in radians)
              const r = c * Math.sqrt(idx + 0.5); // Add 0.5 to avoid dead center overlap
              
              const translateX = Math.cos(angle) * r;
              const translateY = Math.sin(angle) * r;
              
              const Wrapper = tech.link === '#' ? 'div' : 'a';
              const wrapperProps = tech.link === '#' ? {} : {
                href: tech.link,
                target: "_blank",
                rel: "noopener noreferrer"
              };
              
              return (
                <Wrapper 
                  key={idx} 
                  {...wrapperProps}
                  style={{ 
                    position: 'absolute',
                    display: 'block',
                    height: '56px',
                    transform: `translate(${translateX}px, ${translateY}px)`,
                    transition: 'transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), filter 0.3s',
                    zIndex: '1'
                  }}
                  title={tech.name}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = `translate(${translateX}px, ${translateY}px) scale(1.25)`;
                    e.currentTarget.style.zIndex = '10';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = `translate(${translateX}px, ${translateY}px)`;
                    e.currentTarget.style.zIndex = '1';
                  }}
                >
                  <img 
                    src={tech.icon} 
                    alt={tech.name} 
                    style={{ 
                      height: '100%', 
                      width: 'auto',
                      objectFit: 'contain',
                      filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.15))',
                      borderRadius: tech.name === 'LRCLIB' ? '12px' : '0'
                    }}
                    onError={(e) => {
                      // If original color image fails, fallback to simpleicons
                      const fallbackKey = tech.name.toLowerCase().replace(' api', '');
                      e.target.src = `https://cdn.simpleicons.org/${fallbackKey}/888888`;
                    }}
                  />
                </Wrapper>
              );
            })}

            {/* Optional background circle hint if wanted, but left transparent */}
          </div>
        </div>

        <Link 
          to="/" 
          style={{ 
            display: 'inline-block',
            textDecoration: 'none', 
            color: '#fff', 
            background: '#808080', 
            padding: '12px 30px', 
            borderRadius: '30px', 
            fontWeight: 'bold',
            boxShadow: '0 4px 15px var(--shadow-color)',
            transition: 'transform 0.2s',
            marginTop: '10px'
          }}
          onMouseEnter={(e) => e.target.style.transform = 'translateY(-2px)'}
          onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
        >
          메인으로 돌아가기
        </Link>
      </div>
    </div>
  );
}
