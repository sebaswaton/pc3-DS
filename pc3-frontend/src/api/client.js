const BASE = 'http://localhost:8000/api'

async function req(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } }
  if (body) opts.body = JSON.stringify(body)
  const res = await fetch(`${BASE}${path}`, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Error de servidor' }))
    throw new Error(err.detail || 'Error desconocido')
  }
  return res.json()
}

export const registerUser = (name, email, dni, password) =>
  req('POST', '/auth/register', { name, email, dni, password })

export const loginUser = (email, password) =>
  req('POST', '/auth/login', { email, password })

export const listUsers = () =>
  req('GET', '/auth/users')

export const listInitiatives = () =>
  req('GET', '/initiatives')

export const getInitiative = (id) =>
  req('GET', `/initiatives/${id}`)

export const createInitiative = (title, content, authorId) =>
  req('POST', '/initiatives', { title, content, author_id: authorId })

export const publishInitiative = (id, authorId) =>
  req('POST', `/initiatives/${id}/publish`, { author_id: authorId })

export const sealInitiative = (id) =>
  req('POST', `/initiatives/${id}/seal`)

export const signInitiative = (initiativeId, userId) =>
  req('POST', `/initiatives/${initiativeId}/sign`, { user_id: userId })

export const getComments = (initiativeId) =>
  req('GET', `/initiatives/${initiativeId}/comments`)

export const addComment = (initiativeId, text, authorId, parentId = null) =>
  req('POST', `/initiatives/${initiativeId}/comments`, {
    text,
    author_id: authorId,
    parent_id: parentId,
  })
