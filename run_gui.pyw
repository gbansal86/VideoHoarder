"""Double-click launcher for the VideoHoarder desktop application."""

from __future__ import annotations

import ctypes
from pathlib import Path
import sys
import traceback


def message_box(title: str, message: str, error: bool = False) -> None:
    flags = 0x10 if error else 0x40
    try:
        ctypes.windll.user32.MessageBoxW(None, message, title, flags)
    except Exception:
        pass


def release_self_test() -> int:
    """Non-interactive clean-room smoke used by the Windows release build."""
    import json
    import os
    from app import app as backend

    result = {
        "ok": False,
        "frozen": bool(getattr(sys, "frozen", False)),
        "executable": str(Path(sys.executable).resolve()),
        "code_root": str(backend.CODE_ROOT),
        "base": str(backend.BASE),
        "config": str(backend.CONFIG),
        "pyside_imported": True,  # app.gui imported successfully above
    }
    server = None
    try:
        backend.ensure_project_layout()
        source_neighbor = backend.CODE_ROOT / "Source"
        configured_build = str(backend.PATH_CONFIGURATION.get("build_environment") or "").strip()
        if configured_build:
            build_neighbor = Path(configured_build)
        else:
            build_neighbor = next(
                (
                    parent / ".videohoarder-tools" / "build-env"
                    for parent in (backend.CODE_ROOT, *backend.CODE_ROOT.parents)
                    if (parent / ".videohoarder-tools" / "build-env").is_dir()
                ),
                backend.CODE_ROOT / ".videohoarder-tools" / "build-env",
            )
        result.update({
            "source_neighbor_exists": source_neighbor.exists(),
            "build_venv_neighbor_exists": build_neighbor.exists(),
            "config_parent_writable": backend.CONFIG.parent.exists(),
        })

        # Packaged acceptance: prove the local backend becomes reachable and
        # the native Queue can see/control a submitted job in this frozen EXE.
        server = backend.start_dashboard(open_browser=False)
        port = int(server.server_address[1])
        ready, ready_error = backend.wait_for_http_ready(
            f"http://127.0.0.1:{port}/api/progress", timeout_seconds=4.0
        )
        result["backend_http_ready"] = bool(ready)
        if not ready:
            result["backend_http_error"] = str(ready_error or "")

        from PySide6.QtWidgets import QApplication
        from app.native_queue_page import NativeQueuePage

        qt_app = QApplication.instance() or QApplication([])
        backend.web_pause_queue()
        queue_job = backend.web_start_job("Release Queue Acceptance", backend.web_library_stats)
        page = NativeQueuePage()
        page.set_backend(backend)
        qt_app.processEvents()
        page.refresh()
        qt_app.processEvents()
        result["queue_job_id"] = str(queue_job)
        result["queue_visible"] = any(str(row.get("job_id") or "") == str(queue_job) for row in page.jobs)
        result["queue_row_count"] = int(page.table.rowCount())
        cancelled, cancel_message = backend.web_cancel_job(queue_job)
        result["queue_cancel_ok"] = bool(cancelled)
        result["queue_cancel_message"] = str(cancel_message or "")

        # Restart-recovery contract: an unfinished persisted job must return as
        # INTERRUPTED and retain enough task identity for explicit retry.
        recovery_id = "release-restart-recovery"
        with backend.WEB_JOB_LOCK:
            backend.WEB_JOBS[recovery_id] = {
                "job_id": recovery_id, "label": "Restart Recovery Acceptance",
                "status": "RUNNING", "created_at": 1.0, "message": "Working",
                "processed": 0, "total": 1, "transfer_percent": 42.0,
            }
            backend.WEB_JOB_TASKS[recovery_id] = (backend.web_library_stats, (), {})
        backend.web_persist_job_state(force=True)
        restored = backend.web_restore_persisted_jobs(force=True)
        recovered = backend.web_job_snapshot(recovery_id)
        result["restart_recovery_ok"] = (
            str(recovered.get("status") or "").upper() == "INTERRUPTED"
            and recovery_id in backend.WEB_JOB_TASKS
            and int(restored.get("interrupted") or 0) >= 1
        )
        result["recovered_status"] = str(recovered.get("status") or "")
        result["queue_acceptance_ok"] = bool(
            result["backend_http_ready"]
            and result["queue_visible"]
            and result["queue_cancel_ok"]
            and result["restart_recovery_ok"]
        )
        clean_environment_ok = result["frozen"] and not result["source_neighbor_exists"] and not result["build_venv_neighbor_exists"]
        result["ok"] = bool(clean_environment_ok and result["queue_acceptance_ok"])
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        try:
            if server is not None:
                server.shutdown(); server.server_close()
        except Exception:
            pass
    output = os.environ.get("VIDEOHOARDER_RELEASE_SELFTEST_OUTPUT", "")
    if output:
        Path(output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0 if result.get("ok") else 3


if "--release-self-test" in sys.argv:
    raise SystemExit(release_self_test())

try:
    from app.gui import main
except ModuleNotFoundError as exc:
    if (exc.name or "").startswith("PySide6"):
        root = Path(__file__).resolve().parent
        message_box(
            "VideoHoarder needs PySide6",
            "The desktop GUI dependencies are not installed yet.\n\n"
            "Run INSTALL_GUI.ps1 once, then double-click run_gui.pyw again.\n\n"
            f"Installer location:\n{root / 'INSTALL_GUI.ps1'}",
            error=True,
        )
        raise SystemExit(2)
    raise
except Exception as exc:
    message_box(
        "VideoHoarder could not start",
        f"{type(exc).__name__}: {exc}\n\n{traceback.format_exc()[-1800:]}",
        error=True,
    )
    raise SystemExit(1)

raise SystemExit(main())
