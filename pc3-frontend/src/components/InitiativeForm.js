import React, { useState } from 'react'

export default function InitiativeForm({ authorId, onSubmit, onCancel }) {
  const [title, setTitle]     = useState('')
  const [content, setContent] = useState('')
  const [error, setError]     = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (!title || !content) {
      setError('Todos los campos son obligatorios')
      return
    }
    setError('')
    try {
      await onSubmit(title, content)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="form-container">
      <h3>Nueva Iniciativa</h3>
      <form onSubmit={handleSubmit}>
        <label>
          Titulo
          <input value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} />
        </label>
        <label>
          Articulado normativo
          <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={4} />
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
