"""Small bounded LRU cache used by native UI image surfaces."""
from __future__ import annotations

from collections import OrderedDict
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class LRUCache(Generic[K, V]):
    def __init__(self, max_items: int = 256) -> None:
        self.max_items = max(1, int(max_items))
        self._items: OrderedDict[K, V] = OrderedDict()

    def get(self, key: K, default: V | None = None):
        try:
            value = self._items.pop(key)
        except KeyError:
            return default
        self._items[key] = value
        return value

    def put(self, key: K, value: V) -> None:
        if key in self._items:
            self._items.pop(key, None)
        self._items[key] = value
        while len(self._items) > self.max_items:
            self._items.popitem(last=False)

    def __len__(self) -> int:
        return len(self._items)
