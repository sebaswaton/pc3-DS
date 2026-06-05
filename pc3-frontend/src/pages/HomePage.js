import React, { useState, useEffect } from 'react'
import { listInitiatives, createInitiative, publishInitiative } from '../api/client.js'
import InitiativeCard from '../components/InitiativeCard.js'
import InitiativeForm from '../components/InitiativeForm.js'

export default function HomePage({ navigate, currentUser }) {
  const [initiatives, setInitiatives] = useState([])
  const [showForm, setShowForm]       = useState(false)
  const [notice, setNotice]           = useState('')

  useEffect(() => { load() }, [])

  async function load() {
    const inits = await listInitiatives()
    setInitiatives(inits)
  }

  async function handleCreate(title, content) {
    try {
      const initiative = await createInitiative(title, content, currentUser.id)
      await publishInitiative(initiative.id, currentUser.id)
      setShowForm(false)
      setNotice(`Iniciativa "${initiative.title}" publicada.`)
      load()
    } catch (err) {
      setNotice(err.message)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h2>Iniciativas</h2>
        {currentUser && (
          <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
            Nueva iniciativa
          </button>
        )}
      </div>

      {!currentUser && (
        <div className="info-banner">
          Inicia sesion para crear y firmar iniciativas.
        </div>
      )}

      {notice && (
        <div className="notice" onClick={() => setNotice('')}>{notice}</div>
      )}

      {showForm && currentUser && (
        <InitiativeForm
          authorId={currentUser.id}
          onSubmit={handleCreate}
          onCancel={() => setShowForm(false)}
        />
      )}

      {initiatives.length === 0 ? (
        <p className="empty-state">No hay iniciativas aun.</p>
      ) : (
        <div className="initiative-list">
          {initiatives.map((i) => (
            <InitiativeCard
              key={i.id}
              initiative={i}
              onSelect={(id) => navigate('initiative', id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
