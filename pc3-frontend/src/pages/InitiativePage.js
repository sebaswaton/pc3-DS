import React, { useState, useEffect } from 'react'
import {
  getInitiative, getComments, addComment, sealInitiative,
} from '../api/client.js'
import { CommentTree } from '../patterns/CompositeComment.js'
import SignButton from '../components/SignButton.js'

export default function InitiativePage({ initiativeId, navigate, currentUser }) {
  const [initiative, setInitiative] = useState(null)
  const [comments, setComments]     = useState([])
  const [commentText, setComment]   = useState('')
  const [replyTo, setReplyTo]       = useState(null)
  const [msg, setMsg]               = useState('')

  useEffect(() => { loadAll() }, [initiativeId])

  async function loadAll() {
    const [init, cmts] = await Promise.all([
      getInitiative(initiativeId),
      getComments(initiativeId),
    ])
    setInitiative(init)
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
    if (!commentText) { setMsg('Escribe un comentario'); return }
    try {
      await addComment(initiativeId, commentText, currentUser.id, replyTo)
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
          <span>{initiative.signature_count.toLocaleString()} / 25,000 firmas</span>
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

        {currentUser ? (
          <>
            <SignButton initiative={initiative} userId={currentUser.id} onSigned={handleSigned} />

            {initiative.status === 'ACTIVA' && (
              <div className="section">
                <h3>Sellado manual</h3>
                <button className="btn-danger" onClick={handleSeal}>
                  Sellar y enviar al Congreso
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="info-banner">Inicia sesion para firmar esta iniciativa.</div>
        )}

        <div className="section">
          <h3>Comentarios</h3>

          {currentUser ? (
            <>
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
            </>
          ) : (
            <div className="info-banner">Inicia sesion para comentar.</div>
          )}

          {msg && <p className="error">{msg}</p>}
          <CommentTree comments={comments} onReply={currentUser ? setReplyTo : null} />
        </div>
      </div>
    </div>
  )
}
