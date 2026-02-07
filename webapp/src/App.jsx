import { useState, useEffect } from 'react'
import './App.css'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'

function App() {
  // Views: 'login' | 'dashboard' | 'processing' | 'success' | 'error'
  const [view, setView] = useState('login')
  const [token, setToken] = useState('')
  const [user, setUser] = useState(null)

  // Status State for Button Feedback
  const [status, setStatus] = useState('')

  // Notification State
  const [notification, setNotification] = useState(null)

  // Token Visibility State
  const [showToken, setShowToken] = useState(false)

  // Data State
  const [genres, setGenres] = useState([])
  const [selectedGenres, setSelectedGenres] = useState(['pop', 'dance'])
  const [playlistName, setPlaylistName] = useState('My Discovery Mix')
  const [description, setDescription] = useState('Created by SPOTplaylistBird')
  const [trackCount, setTrackCount] = useState(500)

  const [resultLinks, setResultLinks] = useState([])
  const [loadingGenres, setLoadingGenres] = useState(false)

  // Progress State
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    let interval
    if (view === 'processing') {
      setProgress(0)
      interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 95) return prev // Stall at 95% until done
          // Slow down as we get higher
          const inc = prev < 50 ? 5 : prev < 80 ? 2 : 1
          return prev + inc
        })
      }, 800)
    } else {
      setProgress(0)
    }
    return () => clearInterval(interval)
  }, [view])

  // Error State
  const [errorData, setErrorData] = useState(null)

  // PERSISTENCE: Check for saved token on load
  useEffect(() => {
    const savedToken = localStorage.getItem('spotify_token')
    if (savedToken) {
      setToken(savedToken)
      validateToken(savedToken)
    }
  }, [])

  const validateToken = async (t) => {
    try {
      const res = await axios.post('http://localhost:8000/authenticate', { token: t })
      if (res.data.status === 'success') {
        setUser(res.data)
        if (res.data.cleaned_token) {
          setToken(res.data.cleaned_token)
          localStorage.setItem('spotify_token', res.data.cleaned_token)
        }
        setView('dashboard')
        fetchGenres()
        showNotification(`Welcome back, ${res.data.display_name || 'User'}!`, "success")
      } else {
        // Token expired or invalid
        localStorage.removeItem('spotify_token')
      }
    } catch (e) {
      localStorage.removeItem('spotify_token')
    }
  }

  const handleLogout = () => {
    setToken('')
    setUser(null)
    setView('login')
    localStorage.removeItem('spotify_token')
    showNotification("Logged out successfully.", "info")
  }

  const fetchGenres = async () => {
    setLoadingGenres(true)
    try {
      const res = await axios.get('http://localhost:8000/genres')
      if (res.data.genres && res.data.genres.length > 0) {
        setGenres(res.data.genres)
      } else {
        showNotification("No genres loaded from server.", "warning")
      }
    } catch (e) {
      console.error(e)
      showNotification("Failed to load genres.", "error")
    } finally {
      setLoadingGenres(false)
    }
  }

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type })
    setTimeout(() => setNotification(null), 4000)
  }

  const handleLogin = async () => {
    if (!token) return showNotification("Please paste your token first!", "error");
    setStatus('Connecting...')
    try {
      const res = await axios.post('http://localhost:8000/authenticate', { token })

      if (res.data.status === 'success') {
        setUser(res.data)
        const validToken = res.data.cleaned_token || token
        setToken(validToken)
        localStorage.setItem('spotify_token', validToken) // Save for persistence
        setView('dashboard')
        fetchGenres()
        showNotification(`Bem-vindo, ${res.data.display_name || 'Spotify User'}!`, "success")
      }
      else if (res.data.status === 'rate_limit') {
        setErrorData(res.data)
        setView('error')
        showNotification(res.data.message, "error")
      }
      else if (res.data.status === 'auth_error') {
        showNotification(res.data.message, "error")
        setStatus('Try Again')
      }
      else if (res.data.status === 'forbidden') {
        showNotification(res.data.message, "warning")
      }
      else {
        // Generic Error
        showNotification(res.data.message || "Falha no login.", "error")
        setStatus('Error')
      }
    } catch (e) {
      console.error(e); // Log error for debugging
      showNotification("Error: " + e.message, "error")
      setStatus('Failed')
    } finally {
      // Only clear if we didn't already transition to dashboard
      // Or if there was an error, wait a bit for feedback
      if (view !== 'dashboard') {
        setTimeout(() => setStatus(''), 2000)
      } else {
        setStatus('')
      }
    }
  }



  const toggleGenre = (g) => {
    if (selectedGenres.includes(g)) {
      setSelectedGenres(selectedGenres.filter(i => i !== g))
    } else {
      setSelectedGenres([...selectedGenres, g])
    }
  }

  const handleCreate = async () => {
    setView('processing')
    try {
      const payload = {
        token,
        genres: selectedGenres,
        playlist_name: playlistName,
        description: description,
        track_count: parseInt(trackCount)
      }
      const res = await axios.post('http://localhost:8000/execute', payload)

      if (res.data.status === 'success') {
        setResultLinks(res.data.links)
        setView('success')
        showNotification("Playlists created successfully!", "success")
      } else if (res.data.status === 'rate_limit') {
        setErrorData(res.data)
        setView('error')
      } else {
        showNotification("Error: " + res.data.message, "error")
        setView('dashboard')
      }
    } catch (e) {
      showNotification("Critical Error: " + e.message, "error")
      setView('dashboard')
    }
  }

  return (
    <div className="app-container">
      {/* Background Engine */}
      <div className="bg-layer" />
      <div className="bg-overlay" />

      {/* Notification Toast */}
      <AnimatePresence>
        {notification && (
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            className={`notification-toast ${notification.type}`}
          >
            {notification.message}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 4 BUBBLES - CHAOTIC & INDIVIDUAL MOVEMENTS */}

      {/* 1. TOP LEFT - Wandering (11s) */}
      <motion.div
        className="bubble"
        style={{ width: 60, height: 60, top: '15%', left: '10%' }}
        animate={{ y: [0, -30, 10, -10, 0], x: [0, 20, -10, 10, 0] }}
        transition={{ duration: 11, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* 2. TOP RIGHT - Floating (13s) */}
      <motion.div
        className="bubble"
        style={{ width: 180, height: 180, top: '5%', right: '8%' }}
        animate={{ y: [0, 40, -10, 20, 0], x: [0, -30, 10, -20, 0] }}
        transition={{ duration: 13, repeat: Infinity, delay: 0, ease: "easeInOut" }}
      />

      {/* 3. BOTTOM LEFT - Drifting (17s) */}
      <motion.div
        className="bubble"
        style={{ width: 220, height: 220, bottom: '8%', left: '5%' }}
        animate={{ y: [0, -50, 20, -30, 0], x: [0, 40, -20, 30, 0] }}
        transition={{ duration: 17, repeat: Infinity, delay: 0, ease: "easeInOut" }}
      />

      {/* 4. BOTTOM RIGHT - Bobbing (19s) */}
      <motion.div
        className="bubble"
        style={{ width: 100, height: 100, bottom: '20%', right: '15%' }}
        animate={{ y: [0, 30, -30, 20, 0], x: [0, -20, 20, -10, 0] }}
        transition={{ duration: 19, repeat: Infinity, delay: 0, ease: "easeInOut" }}
      />

      <AnimatePresence>

        {view === 'login' && (
          <motion.div
            key="login"
            className="glass-card"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, x: -100 }}
          >
            {/* LOGO ADDED HERE */}
            <div className="logo-wrapper">
              <img src="/logo.png" className="app-logo" alt="Spot Playlist Bird" />
            </div>


            <p style={{ color: 'rgba(255,255,255,0.8)', textAlign: 'center', marginBottom: 20 }}>
              Paste your access token to begin.
            </p>

            <div className="input-capsule" style={{ position: 'relative' }}>
              <input
                type={showToken ? "text" : "password"}
                placeholder="Paste User Token Here"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                style={{ paddingRight: 40 }}
              />
              <button
                onClick={() => setShowToken(!showToken)}
                title={showToken ? "Hide Token" : "Show Token"}
                style={{
                  position: 'absolute',
                  right: 10,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  opacity: 0.7,
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                {showToken ? (
                  // Eye Slash (Hide)
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                  </svg>
                ) : (
                  // Eye (Show)
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                )}
              </button>
            </div>

            <button
              className="shiny-button"
              onClick={handleLogin}
              disabled={!!status}
              style={{ opacity: status ? 0.7 : 1, cursor: status ? 'not-allowed' : 'pointer' }}
            >
              {status || 'Connect to Spotify'}
            </button>
            <a href="https://developer.spotify.com/console/post-playlists/" target="_blank" style={{ color: 'white', marginTop: 15, fontSize: 12, opacity: 0.7 }}>Get Token Here</a>
          </motion.div>
        )}

        {view === 'dashboard' && (
          <motion.div
            key="dashboard"
            className="glass-card"
            style={{ maxWidth: 800 }}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, scale: 0.9 }}
          >


            {/* Logout Button - Absolute Corner Position */}
            <button
              onClick={handleLogout}
              className="logout-btn"
              onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
              onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
            >
              Log Out <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
            </button>

            <h1 style={{ marginBottom: 20 }}>Studio Control</h1>

            <div style={{ width: '100%', marginBottom: 10 }}>
              <label style={{ color: '#ccc', fontSize: 12, marginLeft: 15, marginBottom: 5, display: 'block', textTransform: 'uppercase', letterSpacing: 1 }}>Playlist Settings</label>

              <div className="form-row">
                <div className="input-capsule" style={{ flex: 2, position: 'relative' }}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ position: 'absolute', left: 20, top: '50%', transform: 'translateY(-50%)', opacity: 0.9 }}>
                    <path d="M12 20h9"></path>
                    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                  </svg>
                  <input
                    type="text"
                    placeholder="Playlist Name (Ex: Summer Vibes)"
                    value={playlistName}
                    onChange={e => setPlaylistName(e.target.value)}
                    style={{ paddingLeft: 50 }}
                  />
                </div>
                <div className="input-capsule" style={{ flex: 1, position: 'relative' }}>
                  <span style={{ position: 'absolute', top: -20, left: 10, fontSize: 10, color: 'rgba(255,255,255,0.6)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Track Quantity</span>
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ position: 'absolute', left: 20, top: '50%', transform: 'translateY(-50%)', opacity: 0.9 }}>
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                  <input
                    type="number"
                    placeholder="500"
                    value={trackCount}
                    onChange={e => setTrackCount(e.target.value)}
                    style={{ paddingLeft: 50 }}
                  />
                </div>
              </div>

              <div className="input-capsule" style={{ position: 'relative' }}>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ position: 'absolute', left: 20, top: '50%', transform: 'translateY(-50%)', opacity: 0.9 }}>
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                <input
                  type="text"
                  placeholder="Description (Optional)"
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  style={{ paddingLeft: 50 }}
                />
              </div>
            </div>

            <div style={{ width: '100%', height: 1, background: 'rgba(255,255,255,0.2)', margin: '10px 0' }}></div>

            <div style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                <label style={{ color: '#ccc', fontSize: 12, marginLeft: 15, textTransform: 'uppercase', letterSpacing: 1 }}>Select Genres ({selectedGenres.length})</label>
                <button onClick={() => setSelectedGenres([])} style={{ background: 'none', border: 'none', color: '#ff4444', cursor: 'pointer', fontSize: 12 }}>Clear All</button>
              </div>

              <div style={{
                display: 'flex', flexWrap: 'wrap', gap: 8,
                maxHeight: 180, overflowY: 'auto',
                padding: 15, background: 'rgba(0,0,0,0.2)', borderRadius: 20,
                border: '1px solid rgba(255,255,255,0.1)',
                minHeight: 100, alignItems: 'center', justifyContent: loadingGenres || genres.length === 0 ? 'center' : 'flex-start'
              }}>
                {loadingGenres ? (
                  <div style={{ color: 'white', opacity: 0.7 }}>Loading Genres...</div>
                ) : genres.length === 0 ? (
                  <div style={{ textAlign: 'center' }}>
                    <p style={{ color: 'white', opacity: 0.5, fontSize: 13 }}>Failed to load genres.</p>
                    <button onClick={fetchGenres} style={{ marginTop: 5, padding: '5px 10px', borderRadius: 10, border: 'none', background: 'rgba(255,255,255,0.2)', color: 'white', cursor: 'pointer' }}>Retry</button>
                  </div>
                ) : (
                  genres.map(g => (
                    <button
                      key={g}
                      onClick={() => toggleGenre(g)}
                      className={`genre-btn ${selectedGenres.includes(g) ? 'selected' : ''}`}
                    >
                      {g}
                    </button>
                  ))
                )}
              </div>
            </div>

            <button className="shiny-button" onClick={handleCreate}>
              Launch Generator
            </button>
          </motion.div>
        )}

        {view === 'processing' && (
          <motion.div
            key="processing"
            className="glass-card"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{
              background: 'rgba(255, 255, 255, 0.1)', // More transparent
              backdropFilter: 'blur(15px)',
              maxWidth: 600,
              textAlign: 'center'
            }}
          >
            <h1 style={{ marginBottom: 10, fontSize: '1.5rem', textTransform: 'uppercase', letterSpacing: 2 }}>Creating Magic...</h1>

            {/* PROGRESS PERCENTAGE */}
            <div style={{ fontSize: '4rem', fontWeight: 'bold', color: 'white', marginBottom: 20 }}>
              {progress}%
            </div>

            {/* PROGRESS BAR CONTAINER */}
            <div style={{
              width: '100%',
              height: 8,
              background: 'rgba(255,255,255,0.1)',
              borderRadius: 10,
              overflow: 'hidden',
              marginBottom: 20
            }}>
              {/* PROGRESS FILL */}
              <motion.div
                style={{
                  height: '100%',
                  background: '#1DB954',
                  boxShadow: '0 0 10px #1DB954'
                }}
                animate={{ width: `${progress}%` }}
                transition={{ ease: 'linear' }}
              />
            </div>

            <p style={{ color: 'rgba(255,255,255,0.8)', fontSize: 12, letterSpacing: 1 }}>SEARCHING TRACKS AND FILLING PLAYLISTS.</p>
          </motion.div>
        )}

        {view === 'success' && (
          <motion.div
            key="success"
            className="glass-card"
            initial={{ opacity: 0, scale: 1.2 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <h1 style={{ fontSize: '3rem' }}>Success!</h1>
            <p style={{ color: 'white' }}>Your playlists have been created.</p>

            <div style={{ marginTop: 20, display: 'flex', flexDirection: 'column', gap: 10 }}>
              {resultLinks.map((link, i) => (
                <a
                  key={i}
                  href={link.url}
                  target="_blank"
                  style={{
                    padding: 15, background: 'rgba(255,255,255,0.2)',
                    color: 'white', textDecoration: 'none', borderRadius: 15,
                    display: 'block', textAlign: 'center', fontWeight: 'bold'
                  }}
                >
                  Open "{link.name}" on Spotify
                </a>
              ))}
            </div>

            <button className="shiny-button" onClick={() => setView('dashboard')}>
              Create Another
            </button>
          </motion.div>
        )}

        {view === 'error' && (
          <motion.div
            key="error"
            className="glass-card"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            style={{ borderTop: '2px solid #ff4444' }}
          >
            <h1 style={{ fontSize: '2rem', color: '#ff6b6b' }}>Access Paused</h1>

            <p style={{ color: 'white', fontSize: '1.1rem', margin: '20px 0' }}>
              {errorData?.message || "An unknown error occurred."}
            </p>

            {errorData?.retry_after && (
              <div style={{
                background: 'rgba(0,0,0,0.3)', padding: 20, borderRadius: 20,
                textAlign: 'center', margin: '20px 0', width: '100%'
              }}>
                <span style={{ color: '#aaa', fontSize: 14 }}>ESTIMATED WAIT TIME</span>
                <div style={{ fontSize: 40, fontWeight: 'bold', color: 'white' }}>
                  {errorData.retry_after}s
                </div>
              </div>
            )}

            <button className="shiny-button" onClick={() => setView('login')}>
              Update Token
            </button>

            <button
              className="shiny-button"
              onClick={() => setView('dashboard')}
              style={{ marginTop: 10, background: 'rgba(255,255,255,0.1)', color: 'white' }}
            >
              Try Again
            </button>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  )
}

export default App
