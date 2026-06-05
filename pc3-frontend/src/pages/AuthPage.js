import React, { useState } from 'react'
import { registerUser, loginUser } from '../api/client.js'

export default function AuthPage({ onLogin }) {
  const [mode, setMode]         = useState('login')
  const [name, setName]         = useState('')
  const [email, setEmail]       = useState('')
  const [dni, setDni]           = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      if (mode === 'login') {
        const user = await loginUser(email, password)
        onLogin(user)
      } else {
        const user = await registerUser(name, email, dni, password)
        onLogin(user)
      }
    } catch (err) {
      setError(err.message)
    }
  }

  function toggle() {
    setMode(mode === 'login' ? 'register' : 'login')
    setError('')
    setName(''); setEmail(''); setDni(''); setPassword('')
  }

  return (
    <div className="page auth-page">
      <div className="form-container">
        <h2>{mode === 'login' ? 'Iniciar sesion' : 'Crear cuenta'}</h2>
        <form onSubmit={handleSubmit}>
          {mode === 'register' && (
            <label>
              Nombre completo
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </label>
          )}
          <label>
            Correo electronico
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          {mode === 'register' && (
            <label>
              DNI (8 digitos)
              <input
                value={dni}
                onChange={(e) => setDni(e.target.value)}
                maxLength={8}
                pattern="\d{8}"
                title="El DNI debe tener exactamente 8 digitos"
                required
              />
            </label>
          )}
          <label>
            Contrasena
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={6}
              required
            />
          </label>
          {error && <p className="error">{error}</p>}
          <div className="form-actions">
            <button type="submit" className="btn-primary">
              {mode === 'login' ? 'Ingresar' : 'Registrarse'}
            </button>
          </div>
        </form>
        <p className="auth-switch">
          {mode === 'login' ? 'No tienes cuenta?' : 'Ya tienes cuenta?'}{' '}
          <button className="btn-link" onClick={toggle}>
            {mode === 'login' ? 'Registrarse' : 'Iniciar sesion'}
          </button>
        </p>
      </div>
    </div>
  )
}
