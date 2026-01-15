from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Optional, Dict


class JsonCache:
    """
    Thread-safe JSON cache with corruption recovery.
    Uses atomic writes (write to temp file, then rename) to prevent corruption.
    """
    
    def __init__(self, path: str = ".cache_places.json") -> None:
        self.path = Path(path)
        self._data: Dict[str, Any] = {}
        self._load()
    
    def _load(self) -> None:
        """Load cache from disk with corruption recovery."""
        if not self.path.exists():
            self._data = {}
            return
        
        try:
            content = self.path.read_text(encoding="utf-8")
            self._data = json.loads(content)
        except json.JSONDecodeError:
            # Cache file is corrupted - try to recover
            try:
                # Backup corrupted file
                backup_path = self.path.with_suffix(".json.backup")
                self.path.rename(backup_path)
                print(f"Cache corrupted. Backed up to {backup_path}")
            except Exception:
                pass
            self._data = {}
        except Exception as e:
            # Other errors (permissions, etc.)
            print(f"Warning: Could not load cache: {e}")
            self._data = {}
    
    def get(self, key: str) -> Optional[dict]:
        """Retrieve cached entry by key (case-insensitive)."""
        normalized_key = key.lower().strip()
        return self._data.get(normalized_key)
    
    def set(self, key: str, value: dict) -> None:
        """
        Store entry in cache with atomic write.
        Uses temp file + rename pattern to ensure atomicity.
        """
        normalized_key = key.lower().strip()
        self._data[normalized_key] = value
        self._write_atomic()
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._data = {}
        self._write_atomic()
    
    def _write_atomic(self) -> None:
        """Write cache to disk atomically using temp file + rename."""
        try:
            # Create temp file in same directory to ensure same filesystem
            temp_fd, temp_path = tempfile.mkstemp(
                dir=self.path.parent,
                prefix=".cache_places_tmp_",
                suffix=".json"
            )
            
            try:
                with open(temp_fd, 'w', encoding='utf-8') as f:
                    json.dump(self._data, f, ensure_ascii=False, indent=2)
                
                # Atomic rename (on same filesystem)
                Path(temp_path).replace(self.path)
            except Exception as e:
                # Clean up temp file on error
                try:
                    Path(temp_path).unlink()
                except Exception:
                    pass
                raise e
        
        except Exception as e:
            # Non-fatal: log but don't crash
            print(f"Warning: Cache write failed: {e}")
    
    def get_stats(self) -> dict:
        """Get cache statistics for debugging."""
        return {
            "path": str(self.path),
            "entries": len(self._data),
            "exists": self.path.exists(),
            "keys_sample": list(self._data.keys())[:10]
        }
