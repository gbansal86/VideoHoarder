"""Dedicated native Queue page.

Dashboard keeps a compact queue overview, while this page is the authoritative
full queue view with all rows/columns, explicit refresh, pause reason, and job
controls.  Keeping it separate avoids the old Dashboard/Queue same-page UX.
"""
from __future__ import annotations

from typing import Any

from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from .native_ui import JobDetails, QueueTable


class NativeQueuePage(QWidget):
    status_message = Signal(str)
    open_folder_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.backend: Any | None = None
        self.jobs: list[dict[str, Any]] = []
        self.live: dict[str, Any] = {}
        self.queue_state: dict[str, Any] = {}
        self._selected_job: dict[str, Any] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 20)
        root.setSpacing(12)

        head = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Queue")
        title.setObjectName("pageTitle")
        subtitle = QLabel("All managed jobs. Scroll horizontally for every column and vertically for the full queue history in this session.")
        subtitle.setObjectName("pageSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        head.addLayout(title_box, 1)
        self.details_button = QPushButton("Job details")
        self.details_button.setObjectName("secondaryButton")
        self.details_button.setToolTip("Open the selected job details in a dedicated window.")
        self.details_button.clicked.connect(self._show_job_details)
        self.details_button.setEnabled(False)
        head.addWidget(self.details_button)
        self.refresh_button = QPushButton("Refresh queue")
        self.refresh_button.setObjectName("primaryButton")
        self.refresh_button.clicked.connect(self.refresh)
        head.addWidget(self.refresh_button)
        root.addLayout(head)

        self.pause_reason = QLabel("Queue status loading…")
        self.pause_reason.setObjectName("mutedLabel")
        self.pause_reason.setWordWrap(True)
        root.addWidget(self.pause_reason)

        body = QHBoxLayout()
        body.setSpacing(12)
        table_card = QFrame()
        table_card.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        self.table = QueueTable(row_limit=None)
        self.table.job_selected.connect(self._select_job)
        self.table.cellDoubleClicked.connect(lambda _row, _col: self._show_job_details())
        table_layout.addWidget(self.table)
        body.addWidget(table_card, 7)

        self.details = JobDetails()
        self.details.control_requested.connect(self._control_job)
        self.details.open_folder_requested.connect(self.open_folder_requested.emit)
        self.details.setMinimumWidth(350)
        self.details.setMaximumWidth(480)
        body.addWidget(self.details, 3)
        root.addLayout(body, 1)

        self.timer = QTimer(self)
        self.timer.setInterval(1200)
        self.timer.timeout.connect(self.refresh)

    def set_backend(self, backend: Any) -> None:
        self.backend = backend
        self.timer.start()
        self.refresh()

    def activate(self) -> None:
        self.refresh()
        self.table.setFocus()

    @Slot()
    def refresh(self) -> None:
        if not self.backend:
            return
        try:
            snapshot = self.backend.web_job_snapshot
            try:
                self.jobs = list(snapshot(limit=None) or [])
            except TypeError:
                self.jobs = list(snapshot() or [])
            self.live = dict(self.backend.snapshot() or {})
            self.queue_state = dict(self.backend.web_queue_state() or {})
        except Exception as exc:
            self.pause_reason.setText(f"Queue refresh failed: {type(exc).__name__}: {exc}")
            return

        running = int(self.queue_state.get("running") or 0)
        queued = int(self.queue_state.get("queued") or 0)
        if self.queue_state.get("paused"):
            self.pause_reason.setText(
                f"Queue is PAUSED · {queued} job(s) waiting. Select any job and click Resume queue in Job details."
            )
        elif queued and not running:
            self.pause_reason.setText(f"{queued} job(s) queued and waiting for the worker to start.")
        elif queued:
            self.pause_reason.setText(f"{running} running · {queued} waiting behind the active job.")
        elif running:
            self.pause_reason.setText(f"{running} job running · no queued jobs waiting.")
        else:
            self.pause_reason.setText("Queue is idle.")

        self.table.set_jobs(self.jobs, self.live, self.queue_state)
        selected_id = str(self._selected_job.get("job_id") or "")
        selected = next((job for job in self.jobs if str(job.get("job_id") or "") == selected_id), None)
        if selected is None and self.jobs:
            selected = self.jobs[0]
        self._select_job(selected or {})

    @Slot(object)
    def _select_job(self, job: object) -> None:
        self._selected_job = dict(job or {})
        self.details_button.setEnabled(bool(self._selected_job))
        self.details.set_job(
            self._selected_job,
            self.live,
            bool(self.queue_state.get("paused")),
            self.backend,
            self.jobs,
        )

    @Slot()
    def _show_job_details(self) -> None:
        if not self._selected_job:
            QMessageBox.information(self, "Job details", "Select a queue job first.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("VideoHoarder · Job details")
        dialog.resize(560, 720)
        layout = QVBoxLayout(dialog)
        details = JobDetails()
        details.control_requested.connect(self._control_job)
        details.open_folder_requested.connect(self.open_folder_requested.emit)
        details.set_job(
            self._selected_job, self.live, bool(self.queue_state.get("paused")),
            self.backend, self.jobs,
        )
        layout.addWidget(details)
        job_id=str(self._selected_job.get("job_id") or "")
        refresh_timer=QTimer(dialog)
        refresh_timer.setInterval(800)
        def refresh_dialog_details() -> None:
            if not self.backend or not job_id:
                return
            try:
                current=dict(self.backend.web_job_snapshot(job_id) or {})
                live=dict(self.backend.snapshot() or {})
                queue=dict(self.backend.web_queue_state() or {})
                jobs=list(self.backend.web_job_snapshot(limit=None) or [])
                if current:
                    details.set_job(current,live,bool(queue.get("paused")),self.backend,jobs)
            except Exception:
                pass
        refresh_timer.timeout.connect(refresh_dialog_details)
        refresh_timer.start()
        dialog.exec()

    @Slot(str, str)
    def _control_job(self, action: str, job_id: str) -> None:
        if not self.backend:
            return
        try:
            if action == "pause":
                ok, message = self.backend.web_pause_queue()
            elif action == "resume":
                ok, message = self.backend.web_resume_queue()
            elif action == "cancel":
                ok, message = self.backend.web_cancel_job(job_id)
            elif action == "retry":
                confirm_redownload = False
                if str(self._selected_job.get("status") or "").upper() == "SUCCESS":
                    answer = QMessageBox.question(
                        self,
                        "Download again?",
                        "This download already completed successfully. Download it again?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )
                    if answer != QMessageBox.StandardButton.Yes:
                        return
                    confirm_redownload = True
                ok, message, _new_job = self.backend.web_retry_job(job_id, confirm_redownload)
            elif action == "delete_failure":
                if not job_id:
                    return
                answer = QMessageBox.question(
                    self,
                    "Delete job failure entry",
                    "Delete/dismiss this job failure entry?\n\nThis does not delete downloaded videos or folders.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    return
                clearer = getattr(self.backend, "web_clear_current_failure", None)
                result = dict(clearer(f"job:{job_id}") if callable(clearer) else {})
                ok, message = bool(result.get("ok")), str(result.get("message") or "Failure entry deleted.")
            elif action == "stop":
                answer = QMessageBox.question(
                    self,
                    "Stop active work",
                    "Stop all running and queued VideoHoarder work?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    return
                result = self.backend.web_stop_everything()
                ok, message = bool(result.get("ok")), str(result.get("message") or "Stop requested")
            else:
                return
            self.status_message.emit(str(message))
            if not ok:
                QMessageBox.warning(self, "Queue control", str(message))
        except Exception as exc:
            QMessageBox.warning(self, "Queue control", f"{type(exc).__name__}: {exc}")
        self.refresh()
