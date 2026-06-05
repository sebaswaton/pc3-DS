import React, { useState, useEffect } from 'react'
import {
  listInitiatives, listUsers, registerUser, verifyUser,
  createInitiative, publishInitiative,
} from '../api/client.js'
import InitiativeCard from '../components/InitiativeCard.js'
import InitiativeForm from '../components/InitiativeForm.js'
import PatternBadge from '../components/PatternBadge.js'

export default function HomePage({ navigate }) {
  const [initiatives, setInitiatives] = useState([])
  const [users, setUsers]             = useState([])
  const [showForm, setShowForm]       = useState(false)
  const [showReg, setShowReg]         = useState(false)
  const [name, setName]               = useState('')
  const [email, setEmail]             = useState('')
  const [notice, setNotice]           = useState('')

  useEffect(() => { load() }, [])

  async function load() {
    const [inits, usrs] = await Promise.all([listInitiatives(), listUsers()])
    setInitiatives(inits)
    setUsers(usrs)
  }

  async function handleCreate(title, content, authorId) {
    const initiative = await createInitiative(title, content, authorId)
    await publishInitiative(initiative.id, authorId)
    setShowForm(false)
    setNotice(`Iniciativa "${initiative.title}" publicada.`)
    load()
  }

  async function handleRegister(e) {
    e.preventDefault()
    try {
      const user = await registerUser(name, email)
      await verifyUser(user.id)
      setNotice(`Usuario "${user.name}" registrado y verificado (via ReniecAdapter).`)
      setShowReg(false)
      setName(''); setEmail('')
      load()
    } catch (err) {
      setNotice(err.message)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h2>Iniciativas</h2>
        <div className="header-actions">
          <button className="btn-secondary" onClick={() => setShowReg(!showReg)}>
            Registrar ciudadano
          </button>
          <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
            Nueva iniciativa
          </button>
        </div>
      </div>

      {notice && (
        <div className="notice" onClick={() => setNotice('')}>{notice}</div>
      )}

      {showReg && (
        <div className="form-container">
          <div className="row-title">
            <h3>Registrar y verificar ciudadano</h3>
            <PatternBadge pattern="Adapter" />
          </div>
          <p className="pattern-note">
            ReniecAdapter adapta el servicio externo RENIEC a la interfaz interna IdentityVerifier.
          </p>
          <form onSubmit={handleRegister}>
            <label>Nombre<input value={name} onChange={(e) => setName(e.target.value)} /></label>
            <label>Email<input value={email} onChange={(e) => setEmail(e.target.value)} /></label>
            <button type="submit" className="btn-primary">Registrar y verificar</button>
          </form>
        </div>
      )}

      {showForm && (
        <InitiativeForm users={users} onSubmit={handleCreate} onCancel={() => setShowForm(false)} />
      )}

      {initiatives.length === 0 ? (
        <p className="empty-state">No hay iniciativas. Crea la primera.</p>
      ) : (
        <div className="initiative-list">
          {initiatives.map((i) => (
            <InitiativeCard key={i.id} initiative={i} onSelect={(id) => navigate('initiative', id)} />
          ))}
        </div>
      )}
    </div>
  )
}
