import React, { useState } from 'react'
import HomePage from './pages/HomePage.js'
import InitiativePage from './pages/InitiativePage.js'
import AuthPage from './pages/AuthPage.js'

export default function App() {
  const [page, setPage]           = useState('home')
  const [selectedId, setSelectedId] = useState(null)
  const [currentUser, setCurrentUser] = useState(null)

  function navigate(target, id = null) {
    setPage(target)
    setSelectedId(id)
  }

  function handleLogin(user) {
    setCurrentUser(user)
    navigate('home')
  }

  function handleLogout() {
    setCurrentUser(null)
    navigate('home')
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1 onClick={() => navigate('home')}>Voz del Ciudadano</h1>
        <div className="header-right">
          {currentUser ? (
            <div className="user-info">
              <span className="user-name">{currentUser.name}</span>
              {currentUser.verified && (
                <span className="verified-badge">Verificado</span>
              )}
              <button className="btn-link" onClick={handleLogout}>Salir</button>
            </div>
          ) : (
            <button className="btn-secondary" onClick={() => navigate('auth')}>
              Iniciar sesion
            </button>
          )}
        </div>
      </header>
      <main className="app-main">
        {page === 'home' && (
          <HomePage navigate={navigate} currentUser={currentUser} />
        )}
        {page === 'initiative' && (
          <InitiativePage
            initiativeId={selectedId}
            navigate={navigate}
            currentUser={currentUser}
          />
        )}
        {page === 'auth' && <AuthPage onLogin={handleLogin} />}
      </main>
    </div>
  )
}
