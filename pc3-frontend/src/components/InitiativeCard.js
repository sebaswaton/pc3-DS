import React from 'react'

const STATUS_LABEL = {
  BORRADOR:         'Borrador',
  ACTIVA:           'Activa',
  LISTA_PARA_ENVIO: 'Lista para envio',
  ENVIADA:          'Enviada',
  EXPIRADA:         'Expirada',
}

export default function InitiativeCard({ initiative, onSelect }) {
  const progress = Math.min((initiative.signature_count / 25000) * 100, 100)
  const statusClass = `status-${initiative.status.toLowerCase().replace(/_/g, '-')}`

  return (
    <div className="initiative-card" onClick={() => onSelect(initiative.id)}>
      <div className="card-top">
        <h3>{initiative.title}</h3>
        <span className={`status-badge ${statusClass}`}>
          {STATUS_LABEL[initiative.status] || initiative.status}
        </span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>
      <div className="card-bottom">
        <span>{initiative.signature_count.toLocaleString()} / 25,000 firmas</span>
        {initiative.deadline && (
          <span>Vence: {new Date(initiative.deadline).toLocaleDateString('es')}</span>
        )}
      </div>
    </div>
  )
}
