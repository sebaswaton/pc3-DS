import React, { useState } from 'react'
import HomePage from './pages/HomePage.js'
import InitiativePage from './pages/InitiativePage.js'

export default function App() {
  const [page, setPage] = useState('home')
  const [selectedId, setSelectedId] = useState(null)

  function navigate(target, id = null) {
    setPage(target)
    setSelectedId(id)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1 onClick={() => navigate('home')}>Voz del Ciudadano</h1>
        <p>Plataforma de Iniciativas Legislativas Ciudadanas</p>
      </header>
      <main className="app-main">
        {page === 'home' && <HomePage navigate={navigate} />}
        {page === 'initiative' && (
          <InitiativePage initiativeId={selectedId} navigate={navigate} />
        )}
      </main>
    </div>
  )
}
