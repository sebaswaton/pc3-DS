import React, { useState } from 'react'
import { signInitiative } from '../api/client.js'

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
      <h3>Firmar Iniciativa</h3>
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
