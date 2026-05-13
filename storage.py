# storage.py
import time
from typing import Optional, Dict

class VisitStorage:
    def __init__(self, ttl_seconds: int = 3600):
        self._storage: Dict[str, dict] = {}
        self._timestamps: Dict[str, float] = {}
        self._ttl = ttl_seconds
    
    def save(self, visit_id: str, utm_data: dict):
        self._storage[visit_id] = utm_data
        self._timestamps[visit_id] = time.time()
        self._cleanup()
    
    def get_and_delete(self, visit_id: str) -> Optional[dict]:
        self._cleanup()
        utm = self._storage.pop(visit_id, None)
        self._timestamps.pop(visit_id, None)
        return utm
    
    def _cleanup(self):
        now = time.time()
        expired = [k for k, t in self._timestamps.items() if now - t > self._ttl]
        for k in expired:
            self._storage.pop(k, None)
            self._timestamps.pop(k, None)
