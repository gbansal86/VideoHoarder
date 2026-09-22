"""Native unified Failure / Cleanup page for VideoHoarder.

The page uses one authoritative current-failure register containing both video
failures and failed queue jobs.  Every visible failure has a Delete action next
to it.  Deleting a failure dismisses/clears the failure record only; downloaded
media is never deleted here.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class NativeFailurePage(QWidget):
    status_message = Signal(str)
    failure_count_changed = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("nativeFailurePage")
        self.backend: Any | None = None
        self._all_rows: list[dict[str, Any]] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 20)
        root.setSpacing(12)

        title = QLabel("Failure / Cleanup")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "All current failed video entries and failed queue jobs. Delete clears only the failure entry/status; it never deletes downloaded media."
        )
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        controls = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search failure, video, job, channel, or reason…")
        self.search.textChanged.connect(self._render)
        refresh = QPushButton("Refresh")
        refresh.setObjectName("secondaryButton")
        refresh.clicked.connect(self.refresh)
        self.clear_all_confirm = QCheckBox("clear all")
        self.clear_all_confirm.setToolTip("Tick this before clearing all current failure entries.")
        self.clear_all_button = QPushButton("Clear all failures")
        self.clear_all_button.setObjectName("dangerButton")
        self.clear_all_button.setToolTip("Clears/dismisses all current failure records. It does not delete media.")
        self.clear_all_button.clicked.connect(self._clear_all_failures)
        controls.addWidget(self.search, 1)
        controls.addWidget(refresh)
        controls.addWidget(self.clear_all_confirm)
        controls.addWidget(self.clear_all_button)
        root.addLayout(controls)

        self.summary = QLabel("Loading failures…")
        self.summary.setObjectName("mutedLabel")
        root.addWidget(self.summary)

        # Put Delete immediately next to Failure so it never disappears off the
        # right edge when the reason column is wide.
        self.table = QTableWidget(0, 5)
        self.table.setObjectName("failureTable")
        self.table.setHorizontalHeaderLabels(("Failure", "Delete", "Type", "Channel", "Reason"))
        self.table.verticalHeader().hide()
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 310)
        self.table.setColumnWidth(1, 92)
        self.table.setColumnWidth(2, 110)
        self.table.setColumnWidth(3, 190)
        root.addWidget(self.table, 1)

    def set_backend(self, backend: Any) -> None:
        self.backend = backend
        self.refresh()

    def activate(self) -> None:
        if self.backend:
            self.refresh()

    @Slot()
    def refresh(self) -> None:
        if not self.backend:
            return
        try:
            loader = getattr(self.backend, "web_current_failure_rows", None)
            if callable(loader):
                self._all_rows = list(loader() or [])
            else:  # compatibility with older backends
                self._all_rows = list(self.backend.web_download_failure_rows() or [])
        except Exception as exc:
            self._all_rows = []
            QMessageBox.warning(self, "Could not load failures", f"{type(exc).__name__}: {exc}")
        self.failure_count_changed.emit(len(self._all_rows))
        self._render()

    def _render(self, _text: str = "") -> None:
        query = self.search.text().strip().lower()
        rows = [
            row for row in self._all_rows
            if not query or query in " ".join(
                str(row.get(key) or "")
                for key in (
                    "failure_key", "display_name", "video_id", "job_id", "clean_title", "original_title",
                    "label", "channel", "failure_kind", "failure_reason", "last_error", "reason", "message",
                )
            ).lower()
        ]
        self.table.setUpdatesEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(len(rows))
        for index, row in enumerate(rows):
            self.table.setRowHeight(index, 66)
            failure_key = str(row.get("failure_key") or "").strip()
            video_id = str(row.get("video_id") or "").strip()
            job_id = str(row.get("job_id") or "").strip()
            title = str(
                row.get("display_name") or row.get("clean_title") or row.get("original_title")
                or row.get("label") or video_id or job_id or "Unknown failure"
            )
            identifier = video_id or job_id
            failure = QTableWidgetItem(title + (f"\n{identifier}" if identifier and identifier not in title else ""))
            failure.setData(Qt.ItemDataRole.UserRole, failure_key)
            self.table.setItem(index, 0, failure)

            delete = QPushButton("Delete")
            delete.setObjectName("dangerButton")
            delete.setCursor(Qt.CursorShape.PointingHandCursor)
            delete.setEnabled(bool(failure_key))
            if failure_key:
                delete.clicked.connect(
                    lambda _checked=False, key=failure_key, name=title: self._delete_failure(key, name)
                )
            else:
                delete.setToolTip("This entry does not have a stable failure key.")
            self.table.setCellWidget(index, 1, delete)

            self.table.setItem(index, 2, QTableWidgetItem(str(row.get("failure_kind") or "Video")))
            self.table.setItem(index, 3, QTableWidgetItem(str(row.get("channel") or "")))
            reason = str(
                row.get("reason") or row.get("failure_reason") or row.get("last_error")
                or row.get("error_summary") or row.get("message") or "No reason captured"
            )
            reason_item = QTableWidgetItem(reason)
            reason_item.setToolTip(reason)
            self.table.setItem(index, 4, reason_item)
        self.table.setUpdatesEnabled(True)
        self.summary.setText(
            f"Current unresolved failures: {len(self._all_rows):,}"
            + (f" · showing {len(rows):,} matching search" if query else "")
        )

    def _delete_failure(self, failure_key: str, title: str) -> None:
        if not self.backend:
            return
        answer = QMessageBox.question(
            self,
            "Delete failure entry",
            f"Delete this current failure entry?\n\n{title}\n\n"
            "This clears/dismisses the failure record only. It does not delete the video or library folder.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            clearer = getattr(self.backend, "web_clear_current_failure", None)
            if callable(clearer):
                result = dict(clearer(failure_key) or {})
            elif failure_key.startswith("video:"):
                result = dict(self.backend.clear_selected_failure_entries([failure_key.split(":", 1)[1]]) or {})
            else:
                result = {"ok": False, "message": "This backend cannot delete this failure type."}
            if not result.get("ok"):
                QMessageBox.warning(self, "Could not delete failure", str(result.get("message") or "Unknown error"))
                return
            self.status_message.emit(str(result.get("message") or "Failure entry deleted."))
            self.refresh()
        except Exception as exc:
            QMessageBox.warning(self, "Could not delete failure", f"{type(exc).__name__}: {exc}")

    def _clear_all_failures(self) -> None:
        if not self.backend:
            return
        if not self.clear_all_confirm.isChecked():
            QMessageBox.information(
                self,
                "Confirm clear all",
                "Tick the 'clear all' checkbox first. This prevents accidental cleanup.",
            )
            return
        answer = QMessageBox.question(
            self,
            "Clear all current failures",
            "Clear/dismiss all current failure entries from Failure/Cleanup and Dashboard?\n\n"
            "This does not delete downloaded videos or folders.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            clearer = getattr(self.backend, "web_clear_all_current_failures", None)
            if not callable(clearer):
                QMessageBox.warning(self, "Not available", "This backend cannot clear all current failures.")
                return
            result = dict(clearer() or {})
            if not result.get("ok") and int(result.get("cleared") or 0) == 0:
                QMessageBox.warning(self, "Could not clear failures", str(result.get("message") or "Unknown error"))
            else:
                self.status_message.emit(str(result.get("message") or "Current failures cleared."))
            self.clear_all_confirm.setChecked(False)
            self.refresh()
        except Exception as exc:
            QMessageBox.warning(self, "Could not clear failures", f"{type(exc).__name__}: {exc}")
