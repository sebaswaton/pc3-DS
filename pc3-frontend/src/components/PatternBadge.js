import React from 'react'

const COLORS = {
  Facade:    '#1e3a5f',
  Adapter:   '#7c3aed',
  Decorator: '#059669',
  Proxy:     '#dc2626',
  Composite: '#d97706',
}

export default function PatternBadge({ pattern }) {
  return (
    <span
      className="pattern-badge"
      style={{ backgroundColor: COLORS[pattern] || '#6b7280' }}
      title={`Patron estructural: ${pattern}`}
    >
      {pattern}
    </span>
  )
}
