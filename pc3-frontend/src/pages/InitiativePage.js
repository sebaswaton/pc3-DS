import React, { useState, useEffect } from 'react'
import {
  getInitiative, listUsers, getComments, addComment, sealInitiative,
} from '../api/client.js'
import { CommentTree } from '../patterns/CompositeComment.js'
import SignButton from '../components/SignButton.js'
import PatternBadge from '../components/PatternBadge.js'

export default function InitiativePage({ initiativeId, navigate }) {
  const [initiative, setInitiative] = useState(null)
  const [users, setUsers]           = useState([])
  const [comments, setComments]     = useState([])
  const [userId, setUserId]         = useState('')
  const [commentText, setComment]   = useState('')
  const [replyTo, setReplyTo]       = useState(null)
  const [msg, setMsg]               = useState('')

  useEffect(() => { loadAll() }, [initiativeId])

  async function loadAll() {
    const [init, usrs, cmts] = await Promise.all([
      getInitiative(initiativeId),
      listUsers(),
      getComments(initiativeId),
    ])
    setInitiative(init)
    setUsers(usrs)
    setComments(cmts.comments || [])
  }

  async function handleSigned(result) {
    setInitiative((prev) => ({
      ...prev,
      signature_count: result.signature_count,
      status: result.initiative_status,
    }))
  }

  async function handleComment(e) {
    e.preventDefault()
    if (!commentText || !userId) { setMsg('Seleccione usuario e ingrese texto'); return }
    try {
      await addComment(initiativeId, commentText, userId, replyTo)
      setComment(''); setReplyTo(null); setMsg('')
      const updated = await getComments(initiativeId)
      setComments(updated.comments || [])
    } catch (err) {
      setMsg(err.message)
    }
  }

  async function handleSeal() {
    try {
      await sealInitiative(initiativeId)
      const updated = await getInitiative(initiativeId)
      setInitiative(updated)
      setMsg('Expediente sellado y enviado al Congreso.')
    } catch (err) {
      setMsg(err.message)
    }
  }

  if (!initiative) return <p className="loading">Cargando...</p>

  const progress = Math.min((initiative.signature_count / 25000) * 100, 100)

  return (
    <div className="page">
      <button className="btn-link" onClick={() => navigate('home')}>Volver</button>

      <div className="detail-card">
        <h2>{initiative.title}</h2>
        <div className="detail-meta">
          <span className={`status-badge status-${initiative.status.toLowerCase().replace(/_/g, '-')}`}>
            {initiative.status}
          </span>
          {initiative.radicacion && (
            <span className="radicacion">Radicacion: {initiative.radicacion}</span>
          )}
        </div>

        <div className="section">
          <div className="row-title">
            <span>{initiative.signature_count.toLocaleString()} / 25,000 firmas</span>
            <PatternBadge pattern="Proxy" />
          </div>
          <p className="pattern-note">
            CryptographicSealProxy congela el expediente al alcanzar 25,000 firmas y bloquea escrituras posteriores.
          </p>
          <div className="progress-bar large">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>

        <div className="section">
          <h3>Articulado normativo</h3>
          <p className="content-text">{initiative.content}</p>
        </div>

        {initiative.seal_hash && (
          <div className="seal-box">
            <strong>Sello criptografico SHA-512</strong>
            <code className="hash">{initiative.seal_hash.slice(0, 80)}...</code>
            <span className="seal-date">Sellado: {new Date(initiative.sealed_at).toLocaleString('es')}</span>
          </div>
        )}

        <div className="section">
          <label>
            Ciudadano activo
            <select value={userId} onChange={(e) => setUserId(e.target.value)}>
              <option value="">Seleccionar...</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.name} {u.verified ? '(verificado)' : '(no verificado)'}
                </option>
              ))}
            </select>
          </label>
        </div>

        <SignButton initiative={initiative} userId={userId} onSigned={handleSigned} />

        {initiative.status === 'ACTIVA' && (
          <div className="section">
            <div className="row-title">
              <h3>Sellado manual</h3>
              <PatternBadge pattern="Proxy" />
            </div>
            <button className="btn-danger" onClick={handleSeal}>
              Sellar y enviar al Congreso
            </button>
          </div>
        )}

        <div className="section">
          <div className="row-title">
            <h3>Comentarios</h3>
            <PatternBadge pattern="Composite" />
          </div>
          <p className="pattern-note">
            Arbol parte-todo: CommentBranch (puede responder) / CommentLeaf (nivel maximo, sin respuesta).
          </p>

          {replyTo && (
            <div className="reply-bar">
              Respondiendo a {replyTo.slice(0, 8)}...
              <button className="btn-link" onClick={() => setReplyTo(null)}>cancelar</button>
            </div>
          )}

          <form onSubmit={handleComment} className="comment-form">
            <textarea
              value={commentText}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Escribe un comentario..."
              rows={3}
              maxLength={2000}
            />
            <button type="submit" className="btn-primary">
              {replyTo ? 'Responder' : 'Comentar'}
            </button>
          </form>

          {msg && <p className="error">{msg}</p>}
          <CommentTree comments={comments} onReply={setReplyTo} />
        </div>
      </div>
    </div>
  )
}
