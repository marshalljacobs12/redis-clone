# tests/test_eviction.py

import pytest
from datastore import BaseStore
from config import EVICTION_POLICY

def test_lru_eviction(monkeypatch):
    monkeypatch.setattr("config.MAX_MEMORY_BYTES", 500)  # ~500 bytes max
    monkeypatch.setattr("config.EVICTION_POLICY", "allkeys-lru")

    store = BaseStore()
    for i in range(20):
        store.set(f"key{i}", "x" * 30)  # ~30–40 bytes per key

    total_keys = sum(1 for k in store.store if store.exists(k))
    assert total_keys < 20, "Eviction should have occurred under LRU"

def test_lfu_eviction(monkeypatch):
    monkeypatch.setattr("config.MAX_MEMORY_BYTES", 500)
    monkeypatch.setattr("config.EVICTION_POLICY", "allkeys-lfu")

    store = BaseStore()

    # Step 1: Insert key0 early and warm up LFU
    store.set("key0", "x" * 40)
    for _ in range(50):
        store.get("key0")

    # Step 2: Fill memory with more keys
    for i in range(1, 20):  # skip key0
        store.set(f"key{i}", "x" * 40)

    # Step 3: Validate eviction
    assert store.exists("key0"), "key0 should remain due to high LFU score"
    evicted = [f"key{i}" for i in range(1, 10) if not store.exists(f"key{i}")]
    assert evicted, "Some lower LFU keys should have been evicted"
