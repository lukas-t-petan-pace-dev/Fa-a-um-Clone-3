from typing import Any, List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class MemoryEntry:
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ShortTermMemory:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._entries: List[MemoryEntry] = []

    def add(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        entry = MemoryEntry(
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self._entries.append(entry)
        if len(self._entries) > self.max_size:
            self._entries.pop(0)

    def get_context(self, limit: Optional[int] = None) -> str:
        entries = self._entries[-limit:] if limit else self._entries
        if not entries:
            return ""
        context_parts = []
        for entry in entries:
            content = entry.content if isinstance(entry.content, str) else str(entry.content)
            context_parts.append(f"[{entry.timestamp.strftime('%H:%M:%S')}] {content}")
        return "\n".join(context_parts)

    def get_recent(self, n: int = 5) -> List[MemoryEntry]:
        return self._entries[-n:]

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)


class LongTermMemory:
    def __init__(self):
        self._entries: List[MemoryEntry] = []

    def add(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        entry = MemoryEntry(
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self._entries.append(entry)

    def search(self, query: str) -> List[MemoryEntry]:
        results = []
        query_lower = query.lower()
        for entry in self._entries:
            content_str = str(entry.content).lower()
            if query_lower in content_str:
                results.append(entry)
        return results

    def get_all(self) -> List[MemoryEntry]:
        return self._entries.copy()

    def clear(self) -> None:
        self._entries.clear()


class Memory:
    def __init__(self, short_term_max_size: int = 100):
        self.short_term = ShortTermMemory(max_size=short_term_max_size)
        self.long_term = LongTermMemory()

    def add_interaction(self, role: str, content: Any) -> None:
        self.short_term.add(
            content=f"{role}: {content}",
            metadata={"role": role}
        )

    def add_to_long_term(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.long_term.add(content, metadata)

    def get_context(self, short_term_limit: Optional[int] = None) -> str:
        return self.short_term.get_context(limit=short_term_limit)

    def consolidate_to_long_term(self) -> None:
        for entry in self.short_term.get_recent(10):
            self.long_term.add(entry.content, entry.metadata)

    def clear(self) -> None:
        self.short_term.clear()
        self.long_term.clear()
