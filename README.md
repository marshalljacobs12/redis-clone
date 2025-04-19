# 🔧 Redis Clone (Python)

A simplified Redis clone built from scratch in Python — featuring RESP parsing, an in-memory key-value store, Pub/Sub support, and configurable eviction policies (LRU/LFU). Designed as a distributed systems learning project.

---

## 🚀 Features Implemented

### ✅ Core Features
- **In-Memory Key-Value Store**
  - Supports `GET`, `SET`, `DEL`, `EXISTS`, `EXPIRE`, `TTL`
- **Data Structures**
  - Lists: `LPUSH`, `RPUSH`, `LPOP`, `RPOP`, `LRANGE`, `LLEN`
  - Sets: `SADD`, `SREM`, `SISMEMBER`, `SMEMBERS`
  - Hashes: `HSET`, `HGET`, `HDEL`, `HGETALL`
  - Sorted Sets: `ZADD`, `ZSCORE`, `ZRANGE`

### 📢 Pub/Sub
- Implements Redis-style publish/subscribe:
  - `SUBSCRIBE <channel>`
  - `UNSUBSCRIBE <channel>`
  - `PUBLISH <channel> <message>`
- Multiple subscribers per channel
- Real-time message delivery using asyncio

### 🧠 Eviction Policies
- Configurable via `config.py`
- Supports:
  - `noeviction`: reject writes if memory full
  - `allkeys-lru`: evict least recently used key
  - `allkeys-lfu`: evict least frequently used key
- Approximate memory tracking with `sys.getsizeof()`

---

## ⚙️ Project Structure

```
redis-clone/
├── server/                # TCP server and command router
├── datastore/             # Core data store modules (kv, list, hash, pubsub, eviction)
├── protocol/              # RESP parsing and serialization
├── persistence/           # AOF writer and compactor
├── tests/                 # Unit tests for core components
├── config.py              # Max memory & eviction policy settings
├── main.py                # Entry point
```

---

## 🧪 Example Usage

### 🔌 Start the Redis Clone server:
```bash
python main.py
```

### 🗣 Use `redis-cli` to interact:

```bash
# Basic set/get
redis-cli -p 6379
> SET hello world
> GET hello

# Pub/Sub test
> SUBSCRIBE news  # (in one terminal)
> PUBLISH news "hello subscribers"  # (from another)
```

---

## 🧰 Configuration

Edit `config.py` to tweak behavior:

```python
MAX_MEMORY_BYTES = 1024 * 1024  # 1 MB
EVICTION_POLICY = "allkeys-lru"  # or "allkeys-lfu", "noeviction"
```

---

## ✅ Tested With

- Python 3.10+
- `redis-cli` for client testing

---

## 📚 Still To-Do / Stretch Goals

- Master-replica replication
- Clustering (hash slot sharding)
- Client library with reconnect logic
