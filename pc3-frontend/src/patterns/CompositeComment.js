import React from 'react'

function CommentNode({ comment, depth, onReply }) {
  const isLeaf = !comment.can_reply || depth >= 3
  const indent = depth * 18

  return (
    <div className="comment-node" style={{ marginLeft: indent }}>
      <div className="comment-header">
        <span className="comment-author">{comment.author_id.slice(0, 8)}</span>
        <span className="comment-meta">nivel {comment.level}</span>
        {!isLeaf && (
          <button className="btn-link" onClick={() => onReply(comment.id)}>
            responder
          </button>
        )}
      </div>
      <p className="comment-text">{comment.text}</p>
      {comment.children && comment.children.length > 0 && (
        <div className="comment-children">
          {comment.children.map((child) => (
            <CommentNode key={child.id} comment={child} depth={depth + 1} onReply={onReply} />
          ))}
        </div>
      )}
    </div>
  )
}

export function CommentTree({ comments, onReply }) {
  if (!comments || comments.length === 0) {
    return <p className="empty-state">Sin comentarios aun.</p>
  }
  return (
    <div className="comment-tree">
      {comments.map((c) => (
        <CommentNode key={c.id} comment={c} depth={0} onReply={onReply} />
      ))}
    </div>
  )
}
