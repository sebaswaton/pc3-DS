import React, { useState } from 'react'
import PatternBadge from './PatternBadge.js'
import { signInitiative } from '../api/client.js'

// Al llamar signInitiative, el backend aplica la cadena de Decoradores:
// DuplicateCheckDecorator -> MetadataEnrichmentDecorator -> BaseSignatureService

export default function SignButton({ initiative, userId, onSigned }) {
  const [loading, setLoading] = useState(false)
  const [msg, setMsg]         = useState('')

  async function handleSign() {
    if (!userId) { setMsg('Seleccione un ciudadano verificado'); return }
    setLoading(true)
    setMsg('')
    try {
      const result = await signInitiative(initiative.id, userId)
      setMsg(`Firma registrada. Total: ${result.signature_count.toLocaleString()}`)
      onSigned(result)
    } catch (err) {
      setMsg(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="sign-section">
      <div className="row-title">
        <h3>Firmar Iniciativa</h3>
        <PatternBadge pattern="Decorator" />
      </div>
      <p className="pattern-note">
        DuplicateCheckDecorator + MetadataEnrichmentDecorator envuelven la firma base.
      </p>
      <button
        className="btn-primary btn-wide"
        onClick={handleSign}
        disabled={initiative.status !== 'ACTIVA' || loading}
      >
        {loading ? 'Firmando...' : 'Firmar esta iniciativa'}
      </button>
      {msg && <p className="sign-msg">{msg}</p>}
    </div>
  )
}
