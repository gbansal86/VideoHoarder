"""Per-job cancellation and owned-resource tracking for managed queue work."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any

try:
    from .download_options import DownloadOptions
except ImportError:  # pragma: no cover - direct script compatibility
    from download_options import DownloadOptions


@dataclass(slots=True)
class JobContext:
    job_id: str
    options: DownloadOptions | None = None
    cancel_event: threading.Event = field(default_factory=threading.Event)
    cancel_reason: str = ""
    _processes: set[Any] = field(default_factory=set, repr=False)
    _drivers: set[Any] = field(default_factory=set, repr=False)
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def request_cancel(self, reason: str = "Cancelled by user", *, terminate: bool = True) -> None:
        self.cancel_reason = str(reason or "Cancelled by user")
        self.cancel_event.set()
        if terminate:
            self.terminate_owned_processes()
            self.close_owned_drivers()

    def cancelled(self) -> bool:
        return self.cancel_event.is_set()

    def register_process(self, process: Any) -> None:
        if process is None:
            return
        with self._lock:
            self._processes.add(process)

    def unregister_process(self, process: Any) -> None:
        if process is None:
            return
        with self._lock:
            self._processes.discard(process)

    def register_driver(self, driver: Any) -> None:
        if driver is None:
            return
        with self._lock:
            self._drivers.add(driver)

    def unregister_driver(self, driver: Any) -> None:
        if driver is None:
            return
        with self._lock:
            self._drivers.discard(driver)

    def owned_processes(self) -> list[Any]:
        with self._lock:
            return list(self._processes)

    def owned_drivers(self) -> list[Any]:
        with self._lock:
            return list(self._drivers)

    def terminate_owned_processes(self) -> None:
        for proc in self.owned_processes():
            try:
                if proc.poll() is None:
                    proc.terminate()
            except Exception:
                pass

    def close_owned_drivers(self) -> None:
        for driver in self.owned_drivers():
            try:
                threading.Thread(target=driver.quit, daemon=True).start()
            except Exception:
                pass
