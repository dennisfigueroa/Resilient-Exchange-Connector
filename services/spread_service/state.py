"""
In-memory store for latest spreads.
Replace/extend with Redis or another store when needed.
"""
import threading
from typing import Dict, Optional, Any

_lock = threading.Lock()
_latest: Dict[str, Any] = {}


def update_spread(spread_msg: dict):
    """Store latest spread keyed by symbol."""
    symbol = spread_msg.get("symbol")
    if not symbol:
        return
    with _lock:
        _latest[symbol] = spread_msg


def get_spread(symbol: str) -> Optional[dict]:
    with _lock:
        return _latest.get(symbol)


def get_all() -> Dict[str, dict]:
    with _lock:
        return dict(_latest)
