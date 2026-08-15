"""Native PySide6 interface components for the VideoHoarder desktop app.

The download and library engine remains in :mod:`app.app`.  This module is the
desktop presentation layer: a focused command centre, a small set of guided
workflows, and settings that cover normal day-to-day use.  Long-tail tools are
still available through the embedded local application, but they no longer
dominate the primary interface.
"""

from __future__ import annotations

from datetime import datetime
import re
import time
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, QSize, Qt, QThreadPool, QTimer, Signal, Slot
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


NAV_ITEMS = (
    ("dashboard", "⌂", "Dashboard"),
    ("queue", "⇩", "Queue"),
    ("library", "▦", "Library"),
    ("oldimport", "⇪", "Import & Repair"),
    ("repairdata", "⟳", "Missing Data & AI"),
    ("chatgpt_processing", "◇", "ChatGPT Processing"),
    ("knowledge", "✦", "Knowledge & AI"),
    ("collections", "□", "Collections"),
    ("more", "•••", "More"),
)


def _clear_layout(layout: QVBoxLayout | QHBoxLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()


def _number(value: Any, default: int = 0) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return default


def _percent(value: Any) -> int:
    if isinstance(value, (int, float)):
        return max(0, min(100, int(value)))
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", str(value or ""))
    return max(0, min(100, int(float(match.group(1))))) if match else 0


def _compact_number(value: Any) -> str:
    number = _number(value)
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    if number >= 10_000:
        return f"{number / 1_000:.1f}K"
    return f"{number:,}"


def _job_progress(job: dict[str, Any], live: dict[str, Any]) -> int:
    total = _number(job.get("total"))
    processed = _number(job.get("processed"))
    if total:
        return max(0, min(100, round(processed * 100 / total)))
    if str(job.get("status") or "").upper() == "RUNNING":
        return _percent(live.get("current_percent"))
    if str(job.get("status") or "").upper() in {"SUCCESS", "WARN"}:
        return 100
    return 0


class WorkerSignals(QObject):
    completed = Signal(str, object)
    failed = Signal(str, str)


class FunctionTask(QRunnable):
    """Run a potentially slow read without blocking the desktop interface."""

    def __init__(self, key: str, function: Callable[[], Any]) -> None:
        super().__init__()
        self.key = key
        self.function = function
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            self.signals.completed.emit(self.key, self.function())
        except Exception as exc:  # pragma: no cover - defensive UI boundary
            self.signals.failed.emit(self.key, f"{type(exc).__name__}: {exc}")


class Sidebar(QFrame):
    page_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(248)
        self.buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 16)
        layout.setSpacing(6)

        brand = QWidget()
        brand_layout = QHBoxLayout(brand)
        brand_layout.setContentsMargins(10, 0, 4, 26)
        brand_layout.setSpacing(11)
        mark = QLabel("▷")
        mark.setObjectName("brandMark")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setFixedSize(34, 34)
        name = QLabel("VideoHoarder")
        name.setObjectName("brandName")
        brand_layout.addWidget(mark)
        brand_layout.addWidget(name, 1)
        layout.addWidget(brand)

        for key, icon, label in NAV_ITEMS:
            button = self._nav_button(key, icon, label)
            self.buttons[key] = button
            layout.addWidget(button)

        layout.addStretch(1)

        status = QFrame()
        status.setObjectName("sidebarStatus")
        status_layout = QHBoxLayout(status)
        status_layout.setContentsMargins(12, 10, 12, 10)
        dot = QLabel("●")
        dot.setObjectName("sidebarStatusDot")
        self.status_text = QLabel("Starting…")
        self.status_text.setObjectName("sidebarStatusText")
        status_layout.addWidget(dot)
        status_layout.addWidget(self.status_text, 1)
        layout.addWidget(status)

        settings = self._nav_button("settings", "⚙", "Settings")
        self.buttons["settings"] = settings
        layout.addWidget(settings)
        self.set_current("dashboard")

    def _nav_button(self, key: str, icon: str, label: str) -> QPushButton:
        # QPushButton interprets a single ampersand as a keyboard mnemonic.
        button = QPushButton(f"{icon}    {label.replace('&', '&&')}")
        button.setObjectName("navButton")
        button.setProperty("pageKey", key)
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedHeight(48)
        button.clicked.connect(lambda _checked=False, page=key: self.page_requested.emit(page))
        return button

    def set_current(self, key: str) -> None:
        for page, button in self.buttons.items():
            button.setChecked(page == key)

    def set_ready(self, ready: bool) -> None:
        self.status_text.setText("Local · Ready" if ready else "Starting…")
        for button in self.buttons.values():
            button.setEnabled(ready)


class MetricCard(QFrame):
    def __init__(self, icon: str, title: str, accent: str) -> None:
        super().__init__()
        self.setObjectName("metricCard")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 14, 14, 14)
        layout.setSpacing(14)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(50, 50)
        icon_label.setStyleSheet(
            f"background:{accent}; color:#cfe3ff; border-radius:14px; font-size:23px;"
        )
        text_box = QVBoxLayout()
        text_box.setSpacing(1)
        caption = QLabel(title)
        caption.setObjectName("metricTitle")
        self.value = QLabel("—")
        self.value.setObjectName("metricValue")
        self.detail = QLabel("")
        self.detail.setObjectName("metricDetail")
        text_box.addWidget(caption)
        text_box.addWidget(self.value)
        text_box.addWidget(self.detail)
        layout.addWidget(icon_label)
        layout.addLayout(text_box, 1)

    def set_data(self, value: str, detail: str = "", tone: str = "") -> None:
        self.value.setText(value)
        self.detail.setText(detail)
        colors = {"good": "#67d391", "warn": "#f3b63f", "bad": "#ff7b7b"}
        self.detail.setStyleSheet(f"color:{colors.get(tone, '#91a0b7')};")


class DownloadComposer(QFrame):
    download_requested = Signal(list, dict)

    PRESETS = (
        ("Full Library Capture", {"action": "full_download", "quality": "1080"}),
        ("Best Video", {"action": "media_only", "quality": "best"}),
        ("1080p Video", {"action": "media_only", "quality": "1080"}),
        ("720p Video", {"action": "media_only", "quality": "720"}),
        ("Audio Only", {"action": "media_only", "quality": "audio"}),
    )

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("composerCard")
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 17, 22, 17)
        root.setSpacing(12)

        title = QLabel("New download")
        title.setObjectName("sectionTitle")
        root.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(12)
        self.urls = QPlainTextEdit()
        self.urls.setObjectName("urlInput")
        self.urls.setPlaceholderText("Paste one or more video URLs…")
        self.urls.setFixedHeight(56)
        self.urls.setTabChangesFocus(True)
        self.preset = QComboBox()
        self.preset.setObjectName("presetCombo")
        self.preset.setMinimumWidth(230)
        self.preset.setFixedHeight(56)
        for label, data in self.PRESETS:
            self.preset.addItem(label, data)
        self.download = QPushButton("Download")
        self.download.setObjectName("primaryButton")
        self.download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download.setFixedSize(138, 56)
        self.download.clicked.connect(self._emit_download)
        row.addWidget(self.urls, 1)
        row.addWidget(self.preset)
        row.addWidget(self.download)
        root.addLayout(row)

        self.advanced_button = QPushButton("Advanced options  ▾")
        self.advanced_button.setObjectName("linkButton")
        self.advanced_button.setCheckable(True)
        self.advanced_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.advanced_button.toggled.connect(self._toggle_advanced)
        root.addWidget(self.advanced_button, 0, Qt.AlignmentFlag.AlignLeft)

        self.advanced = QFrame()
        self.advanced.setObjectName("advancedPanel")
        advanced_layout = QHBoxLayout(self.advanced)
        advanced_layout.setContentsMargins(12, 10, 12, 10)
        self.use_ollama = QCheckBox("Use local AI for enrichment")
        self.save_srt = QCheckBox("Save SRT subtitles")
        self.comments = QCheckBox("Capture comments")
        advanced_layout.addWidget(self.use_ollama)
        advanced_layout.addWidget(self.save_srt)
        advanced_layout.addWidget(self.comments)
        advanced_layout.addStretch()
        self.advanced.hide()
        root.addWidget(self.advanced)

    def _toggle_advanced(self, shown: bool) -> None:
        self.advanced.setVisible(shown)
        self.advanced_button.setText("Advanced options  ▴" if shown else "Advanced options  ▾")

    def _emit_download(self) -> None:
        text = self.urls.toPlainText().strip()
        urls = re.findall(r"https?://[^\s]+", text)
        if not urls and text:
            urls = [line.strip() for line in text.splitlines() if line.strip()]
        data = dict(self.preset.currentData() or {})
        data.update(
            {
                "use_ollama": self.use_ollama.isChecked(),
                "save_srt": self.save_srt.isChecked(),
                "download_comments": self.comments.isChecked(),
            }
        )
        self.download_requested.emit(urls, data)

    def set_busy(self, busy: bool) -> None:
        self.download.setEnabled(not busy)
        self.download.setText("Adding…" if busy else "Download")

    def clear_urls(self) -> None:
        self.urls.clear()


class QueueTable(QTableWidget):
    job_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__(0, 5)
        self.setObjectName("queueTable")
        self.setHorizontalHeaderLabels(("Name", "Progress", "Status", "Speed", "ETA"))
        self.verticalHeader().hide()
        self.setShowGrid(False)
        self.setAlternatingRowColors(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(1, 190)
        self.setColumnWidth(2, 132)
        self.setColumnWidth(3, 95)
        self.setColumnWidth(4, 85)
        self.setMinimumHeight(330)
        self._jobs: list[dict[str, Any]] = []
        self.empty_state = QLabel(
            "Queue is clear\n\nPaste one or more links above to start a managed download.",
            self.viewport(),
        )
        self.empty_state.setObjectName("emptyQueue")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.itemSelectionChanged.connect(self._selection_changed)

    def set_jobs(self, jobs: list[dict[str, Any]], live: dict[str, Any]) -> None:
        selected_id = self.selected_job_id()
        visible = sorted(
            jobs,
            key=lambda item: (
                str(item.get("status") or "") not in {"RUNNING", "QUEUED"},
                -float(item.get("created_at") or 0),
            ),
        )[:12]
        self.setUpdatesEnabled(False)
        self.clearContents()
        self.setRowCount(len(visible))
        self._jobs = visible
        self.empty_state.setVisible(not visible)
        status_colors = {
            "RUNNING": QColor("#61a5ff"),
            "QUEUED": QColor("#a9b5c6"),
            "SUCCESS": QColor("#67d391"),
            "WARN": QColor("#f3b63f"),
            "FAILED": QColor("#ff7373"),
            "CANCELLED": QColor("#a9b5c6"),
        }

        for row, job in enumerate(visible):
            self.setRowHeight(row, 72)
            job_id = str(job.get("job_id") or "")
            label = str(job.get("label") or "Background job")
            message = str(job.get("message") or "")
            name_item = QTableWidgetItem(f"  {label}\n  {message[:70]}")
            name_item.setData(Qt.ItemDataRole.UserRole, job_id)
            name_item.setToolTip(message)
            self.setItem(row, 0, name_item)

            progress_value = _job_progress(job, live)
            progress_widget = QWidget()
            progress_layout = QHBoxLayout(progress_widget)
            progress_layout.setContentsMargins(8, 17, 10, 17)
            progress_layout.setSpacing(8)
            bar = QProgressBar()
            bar.setObjectName("rowProgress")
            bar.setRange(0, 100)
            bar.setValue(progress_value)
            bar.setTextVisible(False)
            percent = QLabel(f"{progress_value}%")
            percent.setObjectName("queuePercent")
            percent.setFixedWidth(38)
            progress_layout.addWidget(bar, 1)
            progress_layout.addWidget(percent)
            self.setCellWidget(row, 1, progress_widget)

            status = str(job.get("status") or "QUEUED").upper()
            status_item = QTableWidgetItem(f"●  {status.title()}")
            status_item.setForeground(status_colors.get(status, QColor("#a9b5c6")))
            self.setItem(row, 2, status_item)
            running = status == "RUNNING"
            self.setItem(row, 3, QTableWidgetItem(str(live.get("current_speed") or "—") if running else "—"))
            self.setItem(row, 4, QTableWidgetItem(str(live.get("current_eta") or "—") if running else "—"))

            if job_id == selected_id:
                self.selectRow(row)

        self.setUpdatesEnabled(True)
        if visible and self.currentRow() < 0:
            self.selectRow(0)

    def resizeEvent(self, event: Any) -> None:
        super().resizeEvent(event)
        self.empty_state.setGeometry(self.viewport().rect())

    def selected_job_id(self) -> str:
        row = self.currentRow()
        item = self.item(row, 0) if row >= 0 else None
        return str(item.data(Qt.ItemDataRole.UserRole) or "") if item else ""

    def _selection_changed(self) -> None:
        row = self.currentRow()
        if 0 <= row < len(self._jobs):
            self.job_selected.emit(self._jobs[row])


class JobDetails(QFrame):
    control_requested = Signal(str, str)
    open_folder_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("detailsCard")
        self._job: dict[str, Any] = {}
        self._queue_paused = False
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 17, 20, 18)
        root.setSpacing(12)

        title = QLabel("Job details")
        title.setObjectName("sectionTitle")
        root.addWidget(title)

        preview = QFrame()
        preview.setObjectName("jobPreview")
        preview_layout = QVBoxLayout(preview)
        preview_layout.setContentsMargins(18, 18, 18, 18)
        icon = QLabel("▷")
        icon.setObjectName("jobPreviewIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addStretch()
        preview_layout.addWidget(icon)
        preview_layout.addStretch()
        root.addWidget(preview)

        self.name = QLabel("Select a job")
        self.name.setObjectName("detailsName")
        self.name.setWordWrap(True)
        root.addWidget(self.name)

        self.detail_layout = QVBoxLayout()
        self.detail_layout.setSpacing(8)
        root.addLayout(self.detail_layout)
        root.addStretch(1)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        self.pause = QPushButton("Ⅱ  Pause queue")
        self.pause.setObjectName("primaryButton")
        self.pause.clicked.connect(self._pause_clicked)
        self.secondary = QPushButton("Cancel")
        self.secondary.setObjectName("secondaryButton")
        self.secondary.clicked.connect(self._secondary_clicked)
        buttons.addWidget(self.pause, 1)
        buttons.addWidget(self.secondary, 1)
        root.addLayout(buttons)

        self.open_folder = QPushButton("□  Open downloads folder")
        self.open_folder.setObjectName("secondaryButton")
        self.open_folder.clicked.connect(self.open_folder_requested.emit)
        root.addWidget(self.open_folder)
        self.set_job({}, {}, False, None)

    def _detail(self, label: str, value: str, icon: str) -> QWidget:
        widget = QWidget()
        row = QHBoxLayout(widget)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(9)
        glyph = QLabel(icon)
        glyph.setObjectName("detailIcon")
        glyph.setFixedWidth(19)
        caption = QLabel(label)
        caption.setObjectName("detailLabel")
        caption.setFixedWidth(74)
        text = QLabel(value or "—")
        text.setObjectName("detailValue")
        text.setWordWrap(True)
        row.addWidget(glyph)
        row.addWidget(caption)
        row.addWidget(text, 1)
        return widget

    def set_job(
        self,
        job: dict[str, Any],
        live: dict[str, Any],
        queue_paused: bool,
        backend: Any | None,
    ) -> None:
        self._job = dict(job or {})
        self._queue_paused = queue_paused
        _clear_layout(self.detail_layout)
        if not self._job:
            self.name.setText("No queue item selected")
            self.detail_layout.addWidget(self._detail("Status", "Ready for a new download", "●"))
            self.pause.setEnabled(False)
            self.secondary.hide()
            return

        label = str(self._job.get("label") or "Background job")
        status = str(self._job.get("status") or "QUEUED").upper()
        progress = _job_progress(self._job, live)
        destination = str(getattr(backend, "DOWNLOADS", "Downloads")) if backend else "Downloads"
        self.name.setText(label)
        self.detail_layout.addWidget(self._detail("Destination", destination, "□"))
        self.detail_layout.addWidget(self._detail("Status", status.title(), "●"))
        self.detail_layout.addWidget(self._detail("Progress", f"{progress}%", "▤"))
        self.detail_layout.addWidget(
            self._detail("Message", str(self._job.get("message") or "—"), "i")
        )
        self.detail_layout.addWidget(
            self._detail("Job ID", str(self._job.get("job_id") or "—"), "#")
        )
        self.pause.setEnabled(True)
        self.pause.setText("▶  Resume queue" if queue_paused else "Ⅱ  Pause queue")
        self.secondary.show()
        if status in {"FAILED", "WARN", "CANCELLED", "SUCCESS"}:
            self.secondary.setText("↻  Retry")
            self.secondary.setProperty("controlAction", "retry")
        elif status == "QUEUED":
            self.secondary.setText("×  Cancel")
            self.secondary.setProperty("controlAction", "cancel")
        else:
            self.secondary.setText("Stop all")
            self.secondary.setProperty("controlAction", "stop")

    def _pause_clicked(self) -> None:
        self.control_requested.emit("resume" if self._queue_paused else "pause", "")

    def _secondary_clicked(self) -> None:
        action = str(self.secondary.property("controlAction") or "")
        self.control_requested.emit(action, str(self._job.get("job_id") or ""))


class CommandCenter(QWidget):
    status_message = Signal(str)
    open_folder_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("commandCenter")
        self.backend: Any | None = None
        self.jobs: list[dict[str, Any]] = []
        self.live: dict[str, Any] = {}
        self.queue_state: dict[str, Any] = {}
        self.library_stats: dict[str, Any] = {}
        self._selected_job: dict[str, Any] = {}
        self._stats_running = False
        self._pool = QThreadPool.globalInstance()

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 14)
        root.setSpacing(14)

        self.composer = DownloadComposer()
        self.composer.download_requested.connect(self._start_download)
        root.addWidget(self.composer)

        metrics = QHBoxLayout()
        metrics.setSpacing(12)
        self.active_metric = MetricCard("⌁", "Active jobs", "#123f7f")
        self.today_metric = MetricCard("✓", "Completed today", "#1e5136")
        self.library_metric = MetricCard("▤", "Library", "#183e78")
        self.attention_metric = MetricCard("△", "Needs attention", "#604819")
        for card in (
            self.active_metric,
            self.today_metric,
            self.library_metric,
            self.attention_metric,
        ):
            metrics.addWidget(card, 1)
        root.addLayout(metrics)

        body = QHBoxLayout()
        body.setSpacing(12)
        queue_card = QFrame()
        queue_card.setObjectName("tableCard")
        queue_layout = QVBoxLayout(queue_card)
        queue_layout.setContentsMargins(0, 0, 0, 0)
        queue_layout.setSpacing(0)
        queue_header = QHBoxLayout()
        queue_header.setContentsMargins(18, 14, 14, 8)
        queue_title = QLabel("Active queue")
        queue_title.setObjectName("sectionTitle")
        self.queue_hint = QLabel("Waiting for local service…")
        self.queue_hint.setObjectName("mutedLabel")
        queue_header.addWidget(queue_title)
        queue_header.addStretch()
        queue_header.addWidget(self.queue_hint)
        queue_layout.addLayout(queue_header)
        self.table = QueueTable()
        self.table.job_selected.connect(self._select_job)
        queue_layout.addWidget(self.table, 1)
        body.addWidget(queue_card, 7)

        self.details = JobDetails()
        self.details.control_requested.connect(self._control_job)
        self.details.open_folder_requested.connect(self.open_folder_requested.emit)
        self.details.setMinimumWidth(310)
        self.details.setMaximumWidth(410)
        body.addWidget(self.details, 3)
        root.addLayout(body, 1)

        bottom = QFrame()
        bottom.setObjectName("queueStrip")
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(18, 9, 18, 9)
        self.bottom_count = QLabel("0 active  ·  0 queued")
        self.bottom_count.setObjectName("queueStripText")
        self.bottom_progress = QProgressBar()
        self.bottom_progress.setObjectName("globalProgress")
        self.bottom_progress.setTextVisible(False)
        self.bottom_progress.setRange(0, 100)
        self.bottom_status = QLabel("Ready")
        self.bottom_status.setObjectName("mutedLabel")
        bottom_layout.addWidget(self.bottom_count)
        bottom_layout.addWidget(self.bottom_progress, 1)
        bottom_layout.addWidget(self.bottom_status)
        root.addWidget(bottom)

        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(1200)
        self.poll_timer.timeout.connect(self.refresh_fast)
        self.stats_timer = QTimer(self)
        self.stats_timer.setInterval(45_000)
        self.stats_timer.timeout.connect(self.refresh_stats)

    def set_backend(self, backend: Any) -> None:
        self.backend = backend
        self.poll_timer.start()
        self.stats_timer.start()
        self.refresh_fast()
        self.refresh_stats()

    def set_mode(self, mode: str) -> None:
        if mode == "queue":
            self.table.setFocus(Qt.FocusReason.OtherFocusReason)
        else:
            self.composer.urls.setFocus(Qt.FocusReason.OtherFocusReason)

    def refresh_fast(self) -> None:
        if not self.backend:
            return
        try:
            self.jobs = list(self.backend.web_job_snapshot() or [])
            self.live = dict(self.backend.snapshot() or {})
            self.queue_state = dict(self.backend.web_queue_state() or {})
        except Exception as exc:
            self.bottom_status.setText(f"Refresh failed: {exc}")
            return

        active = _number(self.queue_state.get("running"))
        queued = _number(self.queue_state.get("queued"))
        failed = _number(self.queue_state.get("failed"))
        completed_today = 0
        today = datetime.now().date()
        for job in self.jobs:
            if str(job.get("status") or "").upper() != "SUCCESS":
                continue
            stamp = job.get("finished_at")
            try:
                if stamp and datetime.fromtimestamp(float(stamp)).date() == today:
                    completed_today += 1
            except (TypeError, ValueError, OSError):
                pass

        self.active_metric.set_data(str(active), f"{queued} waiting")
        self.today_metric.set_data(str(completed_today), "Finished successfully", "good")
        library_total = self.library_stats.get("total")
        self.library_metric.set_data(
            _compact_number(library_total) if library_total is not None else "—",
            str(self.library_stats.get("source") or "Loading library…"),
        )
        total_attention = max(failed, _number(self.library_stats.get("failed")))
        self.attention_metric.set_data(
            str(total_attention),
            "Review failures" if total_attention else "No known failures",
            "warn" if total_attention else "good",
        )
        self.queue_hint.setText(
            "Queue paused" if self.queue_state.get("paused") else f"{active} running · {queued} waiting"
        )
        self.table.set_jobs(self.jobs, self.live)
        selected_id = str(self._selected_job.get("job_id") or "")
        selected = next((job for job in self.jobs if str(job.get("job_id") or "") == selected_id), None)
        if selected is None and self.jobs:
            selected = self.jobs[0]
        self._select_job(selected or {})

        global_progress = 0
        total = _number(self.live.get("total"))
        if total:
            global_progress = max(0, min(100, round(_number(self.live.get("processed")) * 100 / total)))
        elif active:
            global_progress = _percent(self.live.get("current_percent"))
        self.bottom_progress.setValue(global_progress)
        self.bottom_count.setText(f"{active} active  ·  {queued} queued")
        status_text = str(
            self.live.get("current_status")
            or self.live.get("message")
            or ("Queue paused" if self.queue_state.get("paused") else "Ready")
        )
        self.bottom_status.setText(status_text[:64])

    def refresh_stats(self) -> None:
        if not self.backend or self._stats_running:
            return
        self._stats_running = True
        task = FunctionTask("library_stats", self.backend.web_library_stats)
        task.signals.completed.connect(self._background_completed)
        task.signals.failed.connect(self._background_failed)
        self._pool.start(task)

    @Slot(str, object)
    def _background_completed(self, key: str, value: object) -> None:
        if key == "library_stats":
            self._stats_running = False
            self.library_stats = dict(value or {})
            self.refresh_fast()

    @Slot(str, str)
    def _background_failed(self, key: str, message: str) -> None:
        if key == "library_stats":
            self._stats_running = False
            self.library_metric.set_data("—", message, "bad")

    @Slot(list, dict)
    def _start_download(self, urls: list[str], preset: dict[str, Any]) -> None:
        if not self.backend:
            return
        if not urls:
            QMessageBox.information(self, "Add a download", "Paste at least one video URL first.")
            self.composer.urls.setFocus()
            return
        self.composer.set_busy(True)
        try:
            action = str(preset.get("action") or "full_download")
            quality = str(preset.get("quality") or "1080")
            if action == "full_download":
                job_id = self.backend.web_start_job(
                    "Full Library Download",
                    self.backend.web_full_download,
                    urls,
                    quality,
                    bool(preset.get("use_ollama")),
                    bool(preset.get("save_srt")),
                    False,
                    bool(preset.get("download_comments")),
                )
            else:
                job_id = self.backend.web_start_job(
                    f"{quality.upper()} Media Download",
                    self.backend.web_media_only_download,
                    urls,
                    quality,
                    "Entertainment",
                    True,
                    "source",
                )
            self.composer.clear_urls()
            self.status_message.emit(f"Added {len(urls)} URL(s) to the queue · {job_id}")
            QTimer.singleShot(80, self.refresh_fast)
        except Exception as exc:
            QMessageBox.critical(self, "Could not add download", f"{type(exc).__name__}: {exc}")
        finally:
            self.composer.set_busy(False)

    @Slot(object)
    def _select_job(self, job: object) -> None:
        self._selected_job = dict(job or {})
        self.details.set_job(
            self._selected_job,
            self.live,
            bool(self.queue_state.get("paused")),
            self.backend,
        )

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
                ok, message, _new_job = self.backend.web_retry_job(job_id)
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
        self.refresh_fast()


class WorkflowCard(QFrame):
    requested = Signal(str)

    def __init__(self, key: str, icon: str, title: str, description: str, button: str) -> None:
        super().__init__()
        self.key = key
        self.setObjectName("workflowCard")
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(9)
        head = QHBoxLayout()
        glyph = QLabel(icon)
        glyph.setObjectName("workflowIcon")
        glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        glyph.setFixedSize(42, 42)
        name = QLabel(title)
        name.setObjectName("workflowTitle")
        head.addWidget(glyph)
        head.addWidget(name, 1)
        root.addLayout(head)
        text = QLabel(description)
        text.setObjectName("mutedLabel")
        text.setWordWrap(True)
        root.addWidget(text)
        root.addStretch()
        action = QPushButton(button)
        action.setObjectName("secondaryButton")
        action.setCursor(Qt.CursorShape.PointingHandCursor)
        action.clicked.connect(lambda: self.requested.emit(self.key))
        root.addWidget(action)


class WorkflowsPage(QWidget):
    navigate_requested = Signal(str)
    legacy_requested = Signal(str, str)
    status_message = Signal(str)

    WORKFLOWS = (
        ("new_download", "⇩", "New download", "Paste links, choose a preset, and add them to the managed queue.", "Open downloader"),
        ("resume", "↻", "Resume downloads", "Audit incomplete items and safely continue only the work still needed.", "Run Smart Resume"),
        ("health", "♡", "Library health", "Back up metadata, check paths and dependencies, and apply safe repairs.", "Run health workflow"),
        ("knowledge", "✦", "Refresh knowledge", "Rebuild search indexes, knowledge pages, semantic data, and AI evidence.", "Refresh knowledge"),
        ("chatgpt", "◇", "ChatGPT processing", "Create packages, import reviewed results, validate, preview, and apply updates.", "Open workspace"),
        ("reports", "▤", "Reports & export", "Repair reports and export the current library catalog for other tools.", "Open reports"),
        ("recovery", "△", "Recovery center", "Use guided recovery only when the database or physical library needs repair.", "Open recovery"),
        ("setup", "⚙", "Setup assistant", "Check portable dependencies and configure less-common integrations.", "Open setup"),
    )

    def __init__(self) -> None:
        super().__init__()
        self.backend: Any | None = None
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 20)
        root.setSpacing(14)
        title = QLabel("Workflows")
        title.setObjectName("pageTitle")
        subtitle = QLabel("The 53 individual actions are grouped into eight jobs you can understand and finish.")
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        grid = QGridLayout()
        grid.setSpacing(12)
        for index, values in enumerate(self.WORKFLOWS):
            card = WorkflowCard(*values)
            card.requested.connect(self._run_workflow)
            grid.addWidget(card, index // 4, index % 4)
        root.addLayout(grid, 1)

        footer = QHBoxLayout()
        note = QLabel("Rare and diagnostic commands are still available when you need them.")
        note.setObjectName("mutedLabel")
        advanced = QPushButton("Open all advanced tools")
        advanced.setObjectName("linkButton")
        advanced.clicked.connect(lambda: self.legacy_requested.emit("tools", ""))
        footer.addWidget(note)
        footer.addStretch()
        footer.addWidget(advanced)
        root.addLayout(footer)

    def set_backend(self, backend: Any) -> None:
        self.backend = backend

    @Slot(str)
    def _run_workflow(self, key: str) -> None:
        if key == "new_download":
            self.navigate_requested.emit("dashboard")
            return
        routes = {
            "chatgpt": ("chatgpt", ""),
            "reports": ("intelligence", "export_csv"),
            "recovery": ("diagnostics", ""),
            "setup": ("tools", "portable_dependencies"),
        }
        if key in routes:
            self.legacy_requested.emit(*routes[key])
            return
        actions = {
            "resume": (
                "Smart Resume — Audit, Repair & Sync",
                "smart_resume_audit_repair_sync",
                [False],
            ),
            "health": (
                "Full System Health Check, Backup & Safe Repair",
                "full_system_health_backup_safe_repair",
                [],
            ),
            "knowledge": (
                "Knowledge & AI — Build, Verify, Ask & Find",
                "knowledge_ai_build_verify_refresh",
                [],
            ),
        }
        if not self.backend or key not in actions:
            return
        label, function_name, args = actions[key]
        answer = QMessageBox.question(
            self,
            label,
            f"Add “{label}” to the managed queue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            function = getattr(self.backend, function_name)
            job_id = self.backend.web_start_job(label, function, *args)
            self.status_message.emit(f"Queued: {label} · {job_id}")
            self.navigate_requested.emit("queue")
        except Exception as exc:
            QMessageBox.critical(self, "Could not start workflow", f"{type(exc).__name__}: {exc}")


class SettingsPage(QWidget):
    status_message = Signal(str)
    open_path_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.backend: Any | None = None
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 22, 24, 20)
        outer.setSpacing(14)
        title = QLabel("Settings")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Everyday options stay here. Advanced configuration remains available as a file.")
        subtitle.setObjectName("pageSubtitle")
        outer.addWidget(title)
        outer.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setObjectName("settingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        grid = QGridLayout(content)
        grid.setContentsMargins(0, 2, 8, 8)
        grid.setSpacing(12)

        general = self._section("Downloads", "Normal defaults for new jobs.")
        form = general.layout()
        self.quality = QComboBox()
        self.quality.addItems(("1080", "720", "480", "360", "best", "audio"))
        self.workers = QSpinBox()
        self.workers.setRange(1, 32)
        self.workers.setSuffix(" workers")
        self.subtitles = QCheckBox("Download subtitles when available")
        self.srt = QCheckBox("Save SRT by default")
        form.addWidget(self._field("Default quality", self.quality))
        form.addWidget(self._field("Parallel work", self.workers))
        form.addWidget(self.subtitles)
        form.addWidget(self.srt)
        grid.addWidget(general, 0, 0)

        intelligence = self._section("Knowledge & AI", "Control optional enrichment without hiding basic downloads.")
        ai_layout = intelligence.layout()
        self.ai_enabled = QCheckBox("Enable local AI features")
        self.smart_resume = QCheckBox("Use Smart Resume by default")
        self.fast_mode = QCheckBox("Prefer fast, deterministic processing")
        self.model = QLineEdit()
        self.model.setPlaceholderText("Ollama model")
        ai_layout.addWidget(self.ai_enabled)
        ai_layout.addWidget(self.smart_resume)
        ai_layout.addWidget(self.fast_mode)
        ai_layout.addWidget(self._field("Local model", self.model))
        grid.addWidget(intelligence, 0, 1)

        privacy = self._section("Source access", "Cookies are off unless a download explicitly needs them.")
        privacy_layout = privacy.layout()
        self.cookies = QComboBox()
        self.cookies.addItems(("none", "browser", "file"))
        self.browser = QComboBox()
        self.browser.addItems(("firefox", "chrome", "edge"))
        privacy_layout.addWidget(self._field("Cookies mode", self.cookies))
        privacy_layout.addWidget(self._field("Browser", self.browser))
        grid.addWidget(privacy, 1, 0)

        storage = self._section("Storage & diagnostics", "Open folders without exposing a command prompt.")
        storage_layout = storage.layout()
        for label, key in (
            ("Open downloads folder", "downloads"),
            ("Open log folder", "logs"),
            ("Open advanced config.json", "config"),
        ):
            button = QPushButton(label)
            button.setObjectName("secondaryButton")
            button.clicked.connect(lambda _checked=False, path_key=key: self.open_path_requested.emit(path_key))
            storage_layout.addWidget(button)
        grid.addWidget(storage, 1, 1)
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

        buttons = QHBoxLayout()
        buttons.addStretch()
        reload_button = QPushButton("Reload")
        reload_button.setObjectName("secondaryButton")
        reload_button.clicked.connect(self.refresh)
        save = QPushButton("Save settings")
        save.setObjectName("primaryButton")
        save.clicked.connect(self.save)
        buttons.addWidget(reload_button)
        buttons.addWidget(save)
        outer.addLayout(buttons)

    def _section(self, title: str, description: str) -> QFrame:
        card = QFrame()
        card.setObjectName("settingsCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)
        heading = QLabel(title)
        heading.setObjectName("sectionTitle")
        text = QLabel(description)
        text.setObjectName("mutedLabel")
        text.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(text)
        return card

    def _field(self, label: str, widget: QWidget) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        caption = QLabel(label)
        caption.setObjectName("fieldLabel")
        layout.addWidget(caption)
        layout.addWidget(widget)
        return box

    def set_backend(self, backend: Any) -> None:
        self.backend = backend
        self.refresh()

    @Slot()
    def refresh(self) -> None:
        if not self.backend:
            return
        values = self.backend.web_config_view()
        self.quality.setCurrentText(str(values.get("download_quality") or "1080"))
        self.workers.setValue(_number(values.get("workers"), 4))
        self.subtitles.setChecked(bool(values.get("download_subtitles")))
        self.srt.setChecked(bool(values.get("save_srt_default")))
        self.ai_enabled.setChecked(bool(values.get("ai_enabled")))
        self.smart_resume.setChecked(bool(values.get("smart_resume")))
        self.fast_mode.setChecked(bool(values.get("fast_no_llm_mode")))
        self.model.setText(str(values.get("ollama_model") or ""))
        self.cookies.setCurrentText(str(values.get("cookies_mode") or "none"))
        self.browser.setCurrentText(str(values.get("browser_for_cookies") or "firefox"))

    @Slot()
    def save(self) -> None:
        if not self.backend:
            return
        values = {
            "download_quality": self.quality.currentText(),
            "workers": self.workers.value(),
            "download_subtitles": self.subtitles.isChecked(),
            "save_srt_default": self.srt.isChecked(),
            "ai_enabled": self.ai_enabled.isChecked(),
            "smart_resume": self.smart_resume.isChecked(),
            "fast_no_llm_mode": self.fast_mode.isChecked(),
            "ollama_model": self.model.text().strip(),
            "cookies_mode": self.cookies.currentText(),
            "browser_for_cookies": self.browser.currentText(),
        }
        try:
            result = self.backend.web_config_update(values)
            self.status_message.emit(str(result.get("message") or "Settings saved"))
        except Exception as exc:
            QMessageBox.critical(self, "Could not save settings", f"{type(exc).__name__}: {exc}")


def desktop_stylesheet() -> str:
    """Return the shared dark command-centre design system."""

    return r"""
    * { font-family: "Segoe UI Variable", "Segoe UI"; font-size: 13px; }
    QMainWindow, QWidget#shellRoot, QWidget#commandCenter { background: #09111f; color: #e8eef8; }
    QFrame#sidebar { background: #061225; border-right: 1px solid #192841; }
    QLabel#brandMark { background: #0c6cf2; color: white; border-radius: 10px; font-size: 24px; font-weight: 800; }
    QLabel#brandName { color: #ffffff; font-size: 20px; font-weight: 750; }
    QPushButton#navButton { text-align: left; color: #cbd5e4; border: 0; border-radius: 8px; padding: 0 15px; background: transparent; font-size: 14px; }
    QPushButton#navButton:hover { color: white; background: #12233a; }
    QPushButton#navButton:checked { color: white; background: #1768e8; font-weight: 650; }
    QPushButton#navButton:disabled { color: #607088; }
    QFrame#sidebarStatus { background: #0c192b; border: 1px solid #1e304a; border-radius: 9px; }
    QLabel#sidebarStatusDot { color: #50c878; font-size: 11px; }
    QLabel#sidebarStatusText { color: #91a0b7; font-size: 11px; }

    QFrame#composerCard, QFrame#metricCard, QFrame#tableCard, QFrame#detailsCard,
    QFrame#workflowCard, QFrame#settingsCard, QFrame#queueStrip {
        background: #111c2d; border: 1px solid #223149; border-radius: 11px;
    }
    QFrame#composerCard { background: #132033; }
    QLabel#sectionTitle { color: #f3f6fb; font-size: 16px; font-weight: 700; }
    QLabel#pageTitle { color: white; font-size: 28px; font-weight: 760; }
    QLabel#pageSubtitle, QLabel#mutedLabel { color: #91a0b7; }
    QLabel#metricTitle { color: #c1ccdc; font-size: 13px; }
    QLabel#metricValue { color: white; font-size: 22px; font-weight: 720; }
    QLabel#metricDetail { color: #91a0b7; font-size: 11px; }

    QPlainTextEdit#urlInput, QComboBox#presetCombo, QLineEdit, QComboBox, QSpinBox {
        background: #101a2a; color: #eef4ff; border: 1px solid #42516a; border-radius: 7px;
        padding: 9px 12px; selection-background-color: #1768e8;
    }
    QPlainTextEdit#urlInput:focus, QComboBox#presetCombo:focus, QLineEdit:focus,
    QComboBox:focus, QSpinBox:focus { border: 1px solid #3b82f6; }
    QComboBox::drop-down { border: 0; width: 28px; }
    QComboBox QAbstractItemView { background: #152238; color: #eff5ff; border: 1px solid #36465f; selection-background-color: #1768e8; }
    QFrame#advancedPanel { background: #0d1726; border: 1px solid #25354c; border-radius: 8px; }
    QCheckBox { color: #c6d1e1; spacing: 8px; }
    QCheckBox::indicator { width: 17px; height: 17px; }
    QCheckBox::indicator:unchecked { border: 1px solid #53627a; border-radius: 4px; background: #0d1726; }
    QCheckBox::indicator:checked { border: 1px solid #2f7df4; border-radius: 4px; background: #1768e8; }

    QPushButton#primaryButton { background: #1768e8; color: white; border: 1px solid #2c7af0; border-radius: 7px; padding: 10px 16px; font-weight: 680; }
    QPushButton#primaryButton:hover { background: #2377f0; }
    QPushButton#primaryButton:pressed { background: #1059c7; }
    QPushButton#primaryButton:disabled { background: #29415f; color: #8695aa; border-color: #324b6a; }
    QPushButton#secondaryButton { background: #1c293d; color: #e0e7f2; border: 1px solid #314159; border-radius: 7px; padding: 9px 13px; }
    QPushButton#secondaryButton:hover { background: #273750; border-color: #48607f; }
    QPushButton#linkButton { color: #4f96ff; background: transparent; border: 0; padding: 4px 1px; text-align: left; font-weight: 600; }
    QPushButton#linkButton:hover { color: #82b5ff; }

    QTableWidget#queueTable { background: transparent; alternate-background-color: transparent; border: 0; color: #e7edf6; outline: 0; }
    QTableWidget#queueTable::item { border-bottom: 1px solid #26354a; padding: 8px; }
    QTableWidget#queueTable::item:selected { background: #172d4b; border-top: 1px solid #2277ec; border-bottom: 1px solid #2277ec; }
    QLabel#emptyQueue { color: #708198; font-size: 14px; background: transparent; }
    QHeaderView::section { background: #111c2d; color: #bdc8d8; border: 0; border-bottom: 1px solid #2a394f; padding: 11px 8px; font-weight: 650; }
    QScrollBar:vertical { background: #0d1726; width: 10px; margin: 0; }
    QScrollBar::handle:vertical { background: #34445d; min-height: 26px; border-radius: 5px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QProgressBar#rowProgress, QProgressBar#globalProgress { background: #26364c; border: 0; border-radius: 4px; height: 8px; }
    QProgressBar#rowProgress::chunk, QProgressBar#globalProgress::chunk { background: #277bf2; border-radius: 4px; }
    QLabel#queuePercent { color: #cbd5e4; }

    QFrame#jobPreview { min-height: 135px; background: #0a2447; border: 1px solid #285182; border-radius: 9px; }
    QLabel#jobPreviewIcon { color: #5298ff; font-size: 52px; font-weight: 300; }
    QLabel#detailsName { color: white; font-size: 15px; font-weight: 700; }
    QLabel#detailIcon { color: #8ba0bc; }
    QLabel#detailLabel { color: #8c9bb0; font-size: 11px; }
    QLabel#detailValue { color: #dce5f2; font-size: 11px; }
    QLabel#queueStripText { color: #e4eaf4; font-weight: 650; }

    QLabel#workflowIcon { color: #8eb9ff; background: #153766; border-radius: 10px; font-size: 20px; }
    QLabel#workflowTitle { color: white; font-size: 15px; font-weight: 700; }
    QFrame#workflowCard:hover { border-color: #3a5d8f; background: #142238; }
    QLabel#fieldLabel { color: #aebbd0; font-size: 11px; font-weight: 650; }
    QScrollArea#settingsScroll { background: transparent; }
    QScrollArea#settingsScroll > QWidget > QWidget { background: #09111f; }

    QWidget#webPanel { background: #0b1422; }
    QFrame#webHeader { background: #111c2d; border-bottom: 1px solid #25344a; }
    QLabel#webTitle { color: white; font-size: 16px; font-weight: 700; }
    QLabel#connectionBadge { color: #6ed797; background: #163426; border: 1px solid #28563e; border-radius: 8px; padding: 5px 9px; font-size: 10px; font-weight: 700; }
    QProgressBar#loadProgress { border: 0; background: #26364c; border-radius: 3px; max-height: 5px; }
    QProgressBar#loadProgress::chunk { background: #277bf2; border-radius: 3px; }
    QWidget#loadingPanel { background: #09111f; }
    QFrame#loadingCard { background: #111c2d; border: 1px solid #26364c; border-radius: 14px; }
    QLabel#loadingTitle { color: white; font-size: 30px; font-weight: 750; }
    QLabel#loadingSubtitle { color: #bdc9da; font-size: 15px; }
    QLabel#loadingMessage { color: #7f90a8; }
    QLabel#errorTitle { color: #ff8181; font-size: 22px; font-weight: 720; }
    QToolTip { background: #17253a; color: white; border: 1px solid #3c4e68; }
    """
