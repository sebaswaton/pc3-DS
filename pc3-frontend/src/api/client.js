// Pattern: Facade (lado cliente)
// Todos los componentes llaman a traves de este modulo.
// Abstrae el transporte HTTP y expone operaciones de negocio con nombre claro.

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

// Autenticacion (Adapter en backend: ReniecAdapter)
export const registerUser = (name, email) =>
  req('POST', '/auth/register', { name, email })

export const verifyUser = (userId) =>
  req('POST', `/auth/verify/${userId}`)

export const listUsers = () =>
  req('GET', '/auth/users')

// Iniciativas (Facade en backend: InitiativeFacade)
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

// Firmas (Decorator en backend: DuplicateCheck + MetadataEnrichment)
export const signInitiative = (initiativeId, userId) =>
  req('POST', `/initiatives/${initiativeId}/sign`, { user_id: userId })

// Comentarios (Composite en backend: CommentBranch / CommentLeaf)
export const getComments = (initiativeId) =>
  req('GET', `/initiatives/${initiativeId}/comments`)

export const addComment = (initiativeId, text, authorId, parentId = null) =>
  req('POST', `/initiatives/${initiativeId}/comments`, {
    text,
    author_id: authorId,
    parent_id: parentId,
  })
