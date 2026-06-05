import React, { useState } from 'react'
import PatternBadge from './PatternBadge.js'

export default function InitiativeForm({ users, onSubmit, onCancel }) {
  const [title, setTitle]     = useState('')
  const [content, setContent] = useState('')
  const [authorId, setAuthor] = useState('')
  const [error, setError]     = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (!title || !content || !authorId) {
      setError('Todos los campos son obligatorios')
      return
    }
    setError('')
    try {
      await onSubmit(title, content, authorId)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="form-container">
      <div className="row-title">
        <h3>Nueva Iniciativa</h3>
        <PatternBadge pattern="Facade" />
      </div>
      <p className="pattern-note">InitiativeFacade orquesta creacion, publicacion y reglas.</p>
      <form onSubmit={handleSubmit}>
        <label>
          Titulo
          <input value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} />
        </label>
        <label>
          Articulado normativo
          <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={4} />
        </label>
        <label>
          Colectivo autor
          <select value={authorId} onChange={(e) => setAuthor(e.target.value)}>
            <option value="">Seleccionar...</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>{u.name}</option>
            ))}
          </select>
        </label>
        {error && <p className="error">{error}</p>}
        <div className="form-actions">
          <button type="submit" className="btn-primary">Crear y publicar</button>
          <button type="button" className="btn-secondary" onClick={onCancel}>Cancelar</button>
        </div>
      </form>
    </div>
  )
}
