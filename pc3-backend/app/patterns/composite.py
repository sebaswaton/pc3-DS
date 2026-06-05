from abc import ABC, abstractmethod
from datetime import datetime, timezone
import uuid

MAX_DEPTH = 3


class CommentComponent(ABC):
    @abstractmethod
    def get_data(self) -> dict:
        pass

    @abstractmethod
    def level(self) -> int:
        pass


class CommentLeaf(CommentComponent):
    def __init__(self, text: str, author_id: str, parent_id: str | None, depth: int):
        self.id = str(uuid.uuid4())
        self.text = text
        self.author_id = author_id
        self.parent_id = parent_id
        self._depth = depth
        self.created_at = datetime.now(timezone.utc).isoformat()

    def level(self) -> int:
        return self._depth

    def get_data(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "author_id": self.author_id,
            "parent_id": self.parent_id,
            "level": self._depth,
            "created_at": self.created_at,
            "children": [],
            "can_reply": False,
        }


class CommentBranch(CommentComponent):
    def __init__(self, text: str, author_id: str, parent_id: str | None, depth: int):
        self.id = str(uuid.uuid4())
        self.text = text
        self.author_id = author_id
        self.parent_id = parent_id
        self._depth = depth
        self.created_at = datetime.now(timezone.utc).isoformat()
        self._children: list[CommentComponent] = []

    def level(self) -> int:
        return self._depth

    def add_child(self, comment: CommentComponent):
        if comment.level() > MAX_DEPTH:
            raise ValueError(f"Profundidad maxima de comentarios ({MAX_DEPTH}) alcanzada")
        self._children.append(comment)

    def get_data(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "author_id": self.author_id,
            "parent_id": self.parent_id,
            "level": self._depth,
            "created_at": self.created_at,
            "children": [c.get_data() for c in self._children],
            "can_reply": True,
        }


def build_comment(
    text: str,
    author_id: str,
    parent_id: str | None = None,
    depth: int = 1,
) -> CommentComponent:
    if depth > MAX_DEPTH:
        raise ValueError(f"Profundidad maxima de comentarios ({MAX_DEPTH}) alcanzada")
    if depth == MAX_DEPTH:
        return CommentLeaf(text, author_id, parent_id, depth)
    return CommentBranch(text, author_id, parent_id, depth)
