"""Native PySide6 interface components for the VideoHoarder desktop app.

The download and library engine remains in :mod:`app.app`.  This module is the
desktop presentation layer: a focused command centre, a small set of guided
workflows, and settings that cover normal day-to-day use.  Long-tail tools are
still available through the embedded local application, but they no longer
dominate the primary interface.
"""

from __future__ import annotations

from datetime import datetime
import os
import re
import time
from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, QSize, Qt, QThreadPool, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QColor, QFont, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
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



from .download_queue_service import (
    display_name as queue_display_name,
    initial_job_metadata,
    job_type as queue_job_type,
    latest_batch_summary,
    queue_wait_message,
    overall_progress_percent,
)
from .download_options import DownloadOptions
from .download_guard_service import confirmation_message, queue_duplicate_matches
from .lru_cache import LRUCache

NAV_ITEMS = (
    ("dashboard", "⌂", "Dashboard"),
    ("downloads", "⇩", "Downloads"),
    ("queue", "⇩", "Queue"),
    ("library", "▦", "Library"),
    ("oldimport", "⇪", "Import & Repair"),
    ("localimport", "▣", "Import Local Videos"),
    ("repairdata", "⟳", "Missing Data & AI"),
    ("chatgpt_processing", "◇", "ChatGPT Processing"),
    ("knowledge", "✦", "Knowledge & AI"),
    ("subscriptions", "◉", "Subscriptions"),
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
    return overall_progress_percent(job, live)


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
    clicked = Signal()

    def __init__(self, icon: str, title: str, accent: str) -> None:
        super().__init__()
        self.setObjectName("metricCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
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

    def mouseReleaseEvent(self, event: Any) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class DownloadComposer(QFrame):
    download_requested = Signal(list, dict)

    # PRESETS is retained for compatibility with existing tests/integrations.
    # The visible UI now separates workflow from quality so users no longer
    # need to infer workflow from a mixed preset list.
    PRESETS = (
        ("Full Library Capture", {"action": "full_download", "quality": "1080"}),
        ("Best Video", {"action": "media_only", "quality": "best"}),
        ("1080p Video", {"action": "media_only", "quality": "1080"}),
        ("720p Video", {"action": "media_only", "quality": "720"}),
        ("Audio Only", {"action": "media_only", "quality": "audio"}),
    )
    WORKFLOWS = (
        ("Full Library", "full_download"),
        ("Media Only", "media_only"),
        ("Audio Only", "audio_only"),
    )
    QUALITIES = (
        ("Best available", "best"),
        ("1080p", "1080"),
        ("720p", "720"),
        ("480p", "480"),
        ("360p", "360"),
    )

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("composerCard")
        self._applying_defaults = False
        self._quality_overridden = False
        self._srt_overridden = False
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 17, 22, 17)
        root.setSpacing(12)

        title = QLabel("New download")
        title.setObjectName("sectionTitle")
        root.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(10)
        self.urls = QPlainTextEdit()
        self.urls.setObjectName("urlInput")
        self.urls.setPlaceholderText("Paste one or more video URLs…")
        self.urls.setFixedHeight(56)
        self.urls.setTabChangesFocus(True)

        self.workflow = QComboBox()
        self.workflow.setObjectName("workflowCombo")
        self.workflow.setMinimumWidth(170)
        self.workflow.setFixedHeight(56)
        self.workflow.setToolTip("Choose what VideoHoarder should create")
        for label, key in self.WORKFLOWS:
            self.workflow.addItem(label, key)
        self.workflow.currentIndexChanged.connect(self._workflow_changed)

        self.quality = QComboBox()
        self.quality.setObjectName("qualityCombo")
        self.quality.setMinimumWidth(155)
        self.quality.setFixedHeight(56)
        self.quality.setToolTip("Video quality is independent from the download workflow")
        for label, value in self.QUALITIES:
            self.quality.addItem(label, value)
        # Preserve the previous normal default.
        self.quality.setCurrentIndex(next((i for i in range(self.quality.count()) if self.quality.itemData(i) == "1080"), 0))
        self.quality.currentIndexChanged.connect(self._quality_changed_by_user)

        self.download = QPushButton("Download")
        self.download.setObjectName("primaryButton")
        self.download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download.setFixedSize(138, 56)
        self.download.clicked.connect(self._emit_download)
        row.addWidget(self.urls, 1)
        row.addWidget(self.workflow)
        row.addWidget(self.quality)
        row.addWidget(self.download)
        root.addLayout(row)

        helper = QHBoxLayout()
        helper.setSpacing(10)
        workflow_label = QLabel("Workflow: Full Library / Media Only / Audio Only")
        workflow_label.setObjectName("mutedLabel")
        quality_label = QLabel("Quality is selected separately")
        quality_label.setObjectName("mutedLabel")
        helper.addWidget(workflow_label)
        helper.addStretch()
        helper.addWidget(quality_label)
        root.addLayout(helper)

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
        self.save_srt.toggled.connect(self._srt_changed_by_user)
        self.download_subtitles = QCheckBox("Download subtitles/transcript when available")
        self.smart_resume = QCheckBox("Smart Resume (skip already-complete videos)")
        self.comments = QCheckBox("Capture comments")
        self.resolve_embedded = QCheckBox("Resolve embedded video URL")
        self.resolve_embedded.setToolTip("Find Dailymotion/YouTube/Vimeo links hidden behind iframe/player pages before downloading.")
        advanced_layout.addWidget(self.use_ollama)
        advanced_layout.addWidget(self.save_srt)
        advanced_layout.addWidget(self.download_subtitles)
        advanced_layout.addWidget(self.smart_resume)
        advanced_layout.addWidget(self.comments)
        advanced_layout.addWidget(self.resolve_embedded)
        advanced_layout.addStretch()
        self.advanced.hide()
        root.addWidget(self.advanced)
        self._workflow_changed()

    def _quality_changed_by_user(self, _index: int = 0) -> None:
        if not self._applying_defaults:
            self._quality_overridden = True

    def _srt_changed_by_user(self, _checked: bool = False) -> None:
        if not self._applying_defaults:
            self._srt_overridden = True

    def apply_settings_defaults(self, values: dict[str, Any] | None, *, force: bool = False) -> None:
        """Apply saved defaults only to controls the user has not deliberately overridden."""
        values = dict(values or {})
        self._applying_defaults = True
        try:
            if force or not self._quality_overridden:
                wanted = str(values.get("download_quality") or "1080")
                index = next((i for i in range(self.quality.count()) if str(self.quality.itemData(i)) == wanted), -1)
                if index >= 0:
                    self.quality.setCurrentIndex(index)
            defaults = DownloadOptions.from_settings(values)
            if force or not self._srt_overridden:
                self.save_srt.setChecked(defaults.save_srt)
            self.download_subtitles.setChecked(defaults.vtt)
            self.smart_resume.setChecked(defaults.smart_resume)
            self.use_ollama.setChecked(defaults.use_ollama)
        finally:
            self._applying_defaults = False
        if force:
            self._quality_overridden = False
            self._srt_overridden = False

    def _workflow_changed(self, _index: int = 0) -> None:
        audio_only = str(self.workflow.currentData() or "") == "audio_only"
        self.quality.setEnabled(not audio_only)
        self.quality.setToolTip(
            "Audio Only uses the best available audio stream."
            if audio_only
            else "Choose video quality independently from the workflow."
        )

    def _toggle_advanced(self, shown: bool) -> None:
        self.advanced.setVisible(shown)
        self.advanced_button.setText("Advanced options  ▴" if shown else "Advanced options  ▾")

    def show_all_options(self) -> None:
        """Expose advanced options when opened from More → New download."""
        self.advanced_button.setChecked(True)
        self.urls.setFocus(Qt.FocusReason.OtherFocusReason)
        self.urls.ensureCursorVisible()

    def _emit_download(self) -> None:
        text = self.urls.toPlainText().strip()
        urls = re.findall(r"https?://[^\s]+", text)
        if not urls and text:
            urls = [line.strip() for line in text.splitlines() if line.strip()]

        workflow = str(self.workflow.currentData() or "full_download")
        if workflow == "audio_only":
            action = "media_only"
            quality = "audio"
        else:
            action = workflow
            quality = str(self.quality.currentData() or "1080")
        data = {
            "action": action,
            "quality": quality,
            "workflow": workflow,
            "use_ollama": self.use_ollama.isChecked(),
            "save_srt": self.save_srt.isChecked(),
            "vtt": self.download_subtitles.isChecked(),
            "smart_resume": self.smart_resume.isChecked(),
            "download_comments": self.comments.isChecked(),
            "resolve_embedded": self.resolve_embedded.isChecked(),
        }
        self.download_requested.emit(urls, data)

    def set_busy(self, busy: bool) -> None:
        self.download.setEnabled(not busy)
        self.download.setText("Adding…" if busy else "Download")

    def clear_urls(self) -> None:
        self.urls.clear()


class QueueTable(QTableWidget):
    job_selected = Signal(object)

    def __init__(self, row_limit: int | None = 12) -> None:
        super().__init__(0, 6)
        self.row_limit = row_limit
        self.setObjectName("queueTable")
        self.setHorizontalHeaderLabels(("Name", "Type", "Progress", "Status", "Speed", "ETA"))
        self.verticalHeader().hide()
        self.setShowGrid(False)
        self.setAlternatingRowColors(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        # Keep Name visible even when the Job details panel narrows the table.
        # Previously the stretch section could collapse to ~0px, making Type
        # appear to be the first column and hiding the filename/thumbnail.
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        for column in range(1, 6):
            self.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(0, 340)
        self.setColumnWidth(1, 130)
        self.setColumnWidth(2, 165)
        self.setColumnWidth(3, 110)
        self.setColumnWidth(4, 85)
        self.setColumnWidth(5, 75)
        self.setMinimumHeight(330)
        self._jobs: list[dict[str, Any]] = []
        self._thumbnail_cache: LRUCache[str, QPixmap] = LRUCache(max_items=256)
        self._thumbnail_manager = QNetworkAccessManager(self)
        self.empty_state = QLabel(
            "Queue is clear\n\nPaste one or more links above to start a managed download.",
            self.viewport(),
        )
        self.empty_state.setObjectName("emptyQueue")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.itemSelectionChanged.connect(self._selection_changed)

    def _apply_thumbnail(self, label: QLabel, pixmap: QPixmap) -> None:
        if pixmap.isNull():
            return
        label.setPixmap(
            pixmap.scaled(
                48,
                48,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        label.setText("")

    def _load_thumbnail(self, label: QLabel, job: dict[str, Any]) -> None:
        source = str(job.get("thumbnail_path") or job.get("thumbnail_url") or "").strip()
        label.setFixedSize(48, 48)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setText("▣")
        label.setStyleSheet("border:1px solid #314159;border-radius:6px;color:#6f829c;background:#0d1726;")
        if not source:
            return
        try:
            local = os.path.expandvars(os.path.expanduser(source))
            if os.path.isfile(local):
                pixmap = QPixmap(local)
                if not pixmap.isNull():
                    self._thumbnail_cache.put(source, pixmap)
                    self._apply_thumbnail(label, pixmap)
                return
        except Exception:
            pass
        if not source.lower().startswith(("http://", "https://")):
            return
        cached = self._thumbnail_cache.get(source)
        if cached is not None:
            self._apply_thumbnail(label, cached)
            return
        label.setProperty("thumbnailSource", source)
        reply = self._thumbnail_manager.get(QNetworkRequest(QUrl(source)))

        def finished() -> None:
            try:
                data = bytes(reply.readAll())
                pixmap = QPixmap()
                if data and pixmap.loadFromData(data):
                    self._thumbnail_cache.put(source, pixmap)
                    if str(label.property("thumbnailSource") or "") == source:
                        self._apply_thumbnail(label, pixmap)
            except RuntimeError:
                pass
            finally:
                reply.deleteLater()

        reply.finished.connect(finished)

    def _name_widget(self, job: dict[str, Any]) -> QWidget:
        box = QWidget()
        layout = QHBoxLayout(box)
        layout.setContentsMargins(8, 7, 8, 7)
        layout.setSpacing(10)
        thumbnail = QLabel()
        self._load_thumbnail(thumbnail, job)
        title = QLabel(queue_display_name(job))
        title.setWordWrap(True)
        title.setToolTip(str(job.get("source_url") or queue_display_name(job)))
        title.setStyleSheet("font-weight:600;color:#e7edf6;background:transparent;")
        layout.addWidget(thumbnail, 0)
        layout.addWidget(title, 1)
        return box

    def set_jobs(self, jobs: list[dict[str, Any]], live: dict[str, Any], queue_state: dict[str, Any] | None = None) -> None:
        selected_id = self.selected_job_id()
        visible = sorted(
            jobs,
            key=lambda item: (
                str(item.get("status") or "") not in {"RUNNING", "QUEUED"},
                -float(item.get("created_at") or 0),
            ),
        )
        if self.row_limit is not None:
            visible = visible[: max(0, int(self.row_limit))]
        queue_state = dict(queue_state or {})
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
            status = str(job.get("status") or "QUEUED").upper()

            name_item = QTableWidgetItem("")
            name_item.setData(Qt.ItemDataRole.UserRole, job_id)
            name_item.setToolTip(str(job.get("source_url") or ""))
            self.setItem(row, 0, name_item)
            self.setCellWidget(row, 0, self._name_widget(job))
            self.setItem(row, 1, QTableWidgetItem(queue_job_type(job)))

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
            self.setCellWidget(row, 2, progress_widget)

            status_label = status.title()
            if status == "QUEUED" and queue_state.get("paused"):
                status_label = "Queued · paused"
            status_item = QTableWidgetItem(f"●  {status_label}")
            status_item.setForeground(status_colors.get(status, QColor("#a9b5c6")))
            if status == "QUEUED":
                status_item.setToolTip(
                    "Waiting because the queue is paused. Click Resume queue."
                    if queue_state.get("paused")
                    else "Waiting for the earlier queued/running job to finish."
                )
            self.setItem(row, 3, status_item)
            running = status == "RUNNING"
            self.setItem(row, 4, QTableWidgetItem(str(job.get("current_speed") or live.get("current_speed") or "—") if running else "—"))
            self.setItem(row, 5, QTableWidgetItem(str(job.get("current_eta") or live.get("current_eta") or "—") if running else "—"))

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
        self.child_table: QTableWidget | None = None
        self.child_log: QPlainTextEdit | None = None
        self._selected_child_id = ""
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 17, 20, 18)
        root.setSpacing(12)

        title = QLabel("Job details")
        title.setObjectName("sectionTitle")
        root.addWidget(title)

        self.name = QLabel("Select a job")
        self.name.setObjectName("detailsName")
        self.name.setWordWrap(True)
        root.addWidget(self.name)

        self.detail_layout = QVBoxLayout()
        self.detail_layout.setSpacing(8)
        root.addLayout(self.detail_layout)
        root.addStretch(1)

        # Full-width stacked controls remain readable on narrower layouts.
        self.pause = QPushButton("Ⅱ  Pause queue")
        self.pause.setObjectName("primaryButton")
        self.pause.clicked.connect(self._pause_clicked)
        self.secondary = QPushButton("Cancel")
        self.secondary.setObjectName("secondaryButton")
        self.secondary.clicked.connect(self._secondary_clicked)
        self.stop_all = QPushButton("■  Stop all jobs")
        self.stop_all.setObjectName("dangerButton")
        self.stop_all.setToolTip("Stops every running and queued VideoHoarder job.")
        self.stop_all.clicked.connect(self._stop_all_clicked)
        root.addWidget(self.pause)
        root.addWidget(self.secondary)
        root.addWidget(self.stop_all)

        self.delete_failure = QPushButton("Delete failure entry")
        self.delete_failure.setObjectName("dangerButton")
        self.delete_failure.setToolTip("Dismisses the selected failed/cancelled job entry. It does not delete media.")
        self.delete_failure.clicked.connect(self._delete_failure_clicked)
        root.addWidget(self.delete_failure)

        self.open_folder = QPushButton("□  Open downloads folder")
        self.open_folder.setObjectName("secondaryButton")
        self.open_folder.clicked.connect(self.open_folder_requested.emit)
        root.addWidget(self.open_folder)
        self.open_saved = QPushButton("□  Open saved location")
        self.open_saved.setObjectName("secondaryButton")
        self.open_saved.clicked.connect(self._open_saved_clicked)
        root.addWidget(self.open_saved)
        self.open_log = QPushButton("⚠  Open failed job log")
        self.open_log.setObjectName("secondaryButton")
        self.open_log.clicked.connect(self._open_log_clicked)
        root.addWidget(self.open_log)
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
        queue_jobs: list[dict[str, Any]] | None = None,
    ) -> None:
        self._job = dict(job or {})
        self._queue_paused = queue_paused
        self._saved_path = ""
        _clear_layout(self.detail_layout)
        if not self._job:
            self.name.setText("No queue item selected")
            self.detail_layout.addWidget(self._detail("Status", "Ready for a new download", "●"))
            self.pause.setEnabled(False)
            self.secondary.hide()
            self.stop_all.hide()
            self.delete_failure.hide()
            self.open_saved.hide()
            self.open_log.hide()
            return

        label = str(self._job.get("label") or "Background job")
        status = str(self._job.get("status") or "QUEUED").upper()
        progress = _job_progress(self._job, live)
        destination = str(getattr(backend, "DOWNLOADS", "Downloads")) if backend else "Downloads"
        self.name.setText(label)
        self.detail_layout.addWidget(self._detail("Destination", destination, "□"))
        self.detail_layout.addWidget(self._detail("Status", status.title(), "●"))
        self.detail_layout.addWidget(self._detail("Progress", f"{progress}%", "▤"))
        stage = str(self._job.get("stage") or "—")
        batch_total = _number(self._job.get("batch_total") if self._job.get("batch_total") not in (None, "") else self._job.get("total"))
        batch_done = _number(self._job.get("batch_processed") if self._job.get("batch_processed") not in (None, "") else self._job.get("processed"))
        transfer = _percent(self._job.get("transfer_percent") if self._job.get("transfer_percent") not in (None, "") else live.get("current_percent"))
        self.detail_layout.addWidget(self._detail("Stage", stage, "›"))
        if batch_total:
            self.detail_layout.addWidget(self._detail("Batch", f"{min(batch_done, batch_total)}/{batch_total}", "#"))
        if status in {"RUNNING", "CANCELLING"}:
            self.detail_layout.addWidget(self._detail("Current transfer", f"{transfer}%", "⇩"))
        message_text = str(self._job.get("message") or "—")
        if status == "QUEUED":
            all_jobs = list(queue_jobs or [])
            state = {
                "paused": bool(queue_paused),
                "running": sum(str(row.get("status") or "").upper() == "RUNNING" for row in all_jobs),
                "queued": sum(str(row.get("status") or "").upper() == "QUEUED" for row in all_jobs),
            }
            message_text = queue_wait_message(self._job, all_jobs, state)
        self.detail_layout.addWidget(self._detail("Message", message_text, "i"))
        children=[dict(row) for row in (self._job.get("active_videos") or []) if isinstance(row,dict)]
        if children:
            child_label=QLabel(f"Videos ({len(children)})")
            child_label.setObjectName("detailLabel")
            self.detail_layout.addWidget(child_label)
            table=QTableWidget(len(children),5)
            table.setObjectName("childVideoTable")
            table.setHorizontalHeaderLabels(["Video","Status","Progress","Speed","ETA"])
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setAlternatingRowColors(True)
            table.verticalHeader().setVisible(False)
            table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
            for column in range(1,5):
                table.horizontalHeader().setSectionResizeMode(column,QHeaderView.ResizeMode.ResizeToContents)
            table.setMinimumHeight(118)
            table.setMaximumHeight(min(260,58+34*len(children)))
            for row_index,child in enumerate(children):
                values=(
                    str(child.get("title") or child.get("video_id") or "Video"),
                    str(child.get("status") or child.get("stage") or "Queued").title(),
                    f"{_percent(child.get('percent'))}%",
                    str(child.get("speed") or "—"),
                    str(child.get("eta") or "—"),
                )
                for column,value in enumerate(values):
                    table.setItem(row_index,column,QTableWidgetItem(value))
            self.child_table=table
            self.detail_layout.addWidget(table)
            chooser=QComboBox()
            chooser.setObjectName("childLogFilter")
            chooser.addItem("All video events","")
            for child in children:
                child_id=str(child.get("video_id") or "")
                chooser.addItem(str(child.get("title") or child_id or "Video"),child_id)
            selected_index=max(0,chooser.findData(self._selected_child_id))
            chooser.setCurrentIndex(selected_index)
            log_view=QPlainTextEdit()
            log_view.setObjectName("childVideoLog")
            log_view.setReadOnly(True)
            log_view.setPlaceholderText("Per-video log events will appear here while downloads run.")
            log_view.setMaximumHeight(150)
            self.child_log=log_view
            def update_child_log(index: int) -> None:
                child_id=str(chooser.itemData(index) or "")
                self._selected_child_id=child_id
                reader=getattr(backend,"web_job_video_log",None) if backend else None
                lines=reader(str(self._job.get("job_id") or ""),child_id,200) if callable(reader) else []
                log_view.setPlainText("\n".join(str(line) for line in (lines or [])))
                bar=log_view.verticalScrollBar();bar.setValue(bar.maximum())
            chooser.currentIndexChanged.connect(update_child_log)
            def select_child_row(row: int, _column: int) -> None:
                child_id=str(children[row].get("video_id") or "") if 0 <= row < len(children) else ""
                index=chooser.findData(child_id)
                if index >= 0:chooser.setCurrentIndex(index)
            table.cellClicked.connect(select_child_row)
            self.detail_layout.addWidget(chooser)
            child_controls=QWidget()
            child_control_row=QHBoxLayout(child_controls)
            child_control_row.setContentsMargins(0,0,0,0)
            child_pause=QPushButton("Ⅱ  Pause video")
            child_retry=QPushButton("↻  Resume / retry")
            child_cancel=QPushButton("×  Cancel video")
            child_pause.setObjectName("secondaryButton")
            child_retry.setObjectName("secondaryButton")
            child_cancel.setObjectName("dangerButton")
            def request_child(action: str) -> None:
                child_id=str(chooser.currentData() or "")
                if child_id:self.control_requested.emit(action,f"{self._job.get('job_id') or ''}::{child_id}")
            child_pause.clicked.connect(lambda:request_child("pause_child"))
            child_retry.clicked.connect(lambda:request_child("retry_child"))
            child_cancel.clicked.connect(lambda:request_child("cancel_child"))
            child_control_row.addWidget(child_pause)
            child_control_row.addWidget(child_retry)
            child_control_row.addWidget(child_cancel)
            def update_child_controls(index: int) -> None:
                child_id=str(chooser.itemData(index) or "")
                child=next((row for row in children if str(row.get("video_id") or "")==child_id),{})
                child_status=str(child.get("status") or "").upper()
                child_pause.setEnabled(bool(child_id) and child_status in {"QUEUED","RUNNING"})
                child_cancel.setEnabled(bool(child_id) and child_status in {"QUEUED","RUNNING","PAUSING"})
                child_retry.setEnabled(bool(child_id) and child_status in {"PAUSED","CANCELLED","FAILED","INTERRUPTED"})
            chooser.currentIndexChanged.connect(update_child_controls)
            self.detail_layout.addWidget(child_controls)
            self.detail_layout.addWidget(log_view)
            update_child_log(selected_index)
            update_child_controls(selected_index)
        else:
            self.child_table=None
            self.child_log=None
        error_text = str(self._job.get("error_summary") or self._job.get("error") or "")
        if error_text:
            self.detail_layout.addWidget(self._detail("Error", error_text[-1200:], "!"))
        log_path = str(self._job.get("log_path") or "")
        if log_path:
            self.detail_layout.addWidget(self._detail("Log file", log_path, "↗"))
        self.detail_layout.addWidget(
            self._detail("Job ID", str(self._job.get("job_id") or "—"), "#")
        )
        self.pause.setEnabled(True)
        self.pause.setText("▶  Resume queue" if queue_paused else "Ⅱ  Pause queue")
        self.secondary.show()
        if status == "SUCCESS":
            self.secondary.setText("↻  Download again")
            self.secondary.setProperty("controlAction", "retry")
        elif status == "INTERRUPTED":
            self.secondary.setText("↻  Resume / retry")
            self.secondary.setProperty("controlAction", "retry")
        elif status in {"FAILED", "WARN", "CANCELLED"}:
            self.secondary.setText("↻  Retry")
            self.secondary.setProperty("controlAction", "retry")
        elif status == "QUEUED":
            self.secondary.setText("×  Cancel")
            self.secondary.setProperty("controlAction", "cancel")
        else:
            self.secondary.setText("×  Cancel this job")
            self.secondary.setProperty("controlAction", "cancel")
        active_any = any(str(row.get("status") or "").upper() in {"RUNNING", "CANCELLING", "QUEUED"} for row in (queue_jobs or [self._job]))
        self.stop_all.setVisible(active_any)
        self.delete_failure.setVisible(status in {"FAILED", "WARN", "CANCELLED"})
        saved_candidates = [
            self._job.get("local_folder"),
            self._job.get("output_path"),
            self._job.get("download_folder"),
            self._job.get("destination"),
            self._job.get("local_video"),
        ]
        for candidate in saved_candidates:
            if not candidate:
                continue
            path = Path(str(candidate))
            if path.exists():
                self._saved_path = str(path if path.is_dir() else path.parent)
                break
        self.open_saved.setVisible(True)
        self.open_saved.setToolTip(self._saved_path or "No per-job saved path was captured; opens the main downloads folder.")
        self.open_log.setVisible(bool(log_path))

    def _open_log_clicked(self) -> None:
        path = str(self._job.get("log_path") or "")
        if path:
            try:
                os.startfile(path)
            except OSError:
                pass

    def _pause_clicked(self) -> None:
        self.control_requested.emit("resume" if self._queue_paused else "pause", "")

    def _secondary_clicked(self) -> None:
        action = str(self.secondary.property("controlAction") or "")
        self.control_requested.emit(action, str(self._job.get("job_id") or ""))

    def _stop_all_clicked(self) -> None:
        self.control_requested.emit("stop", "")

    def _delete_failure_clicked(self) -> None:
        self.control_requested.emit("delete_failure", str(self._job.get("job_id") or ""))

    def _open_saved_clicked(self) -> None:
        if self._saved_path:
            try:
                os.startfile(self._saved_path)
                return
            except OSError:
                pass
        self.open_folder_requested.emit()


class CommandCenter(QWidget):
    status_message = Signal(str)
    open_folder_requested = Signal()
    navigate_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("commandCenter")
        self.backend: Any | None = None
        self.jobs: list[dict[str, Any]] = []
        self.failed_jobs: list[dict[str, Any]] = []
        self.live: dict[str, Any] = {}
        self.queue_state: dict[str, Any] = {}
        self.library_stats: dict[str, Any] = {}
        self.current_failure_count = 0
        self._selected_job: dict[str, Any] = {}
        self._stats_running = False
        self._stats_pending = False
        self._stats_refresh_target = 0.0
        self._stats_inflight_target = 0.0
        self._stats_refreshed_through = 0.0
        self._figures_running = False
        self._pool = QThreadPool.globalInstance()
        # QRunnable is not a QObject, so Python may collect a locally scoped
        # task (and its signal object) while Qt is still running it.  Retain
        # tasks until their terminal signal is delivered.
        self._background_tasks: set[FunctionTask] = set()

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
        self.active_metric.clicked.connect(lambda: self.navigate_requested.emit("queue"))
        self.today_metric.clicked.connect(lambda: self.navigate_requested.emit("queue"))
        self.library_metric.clicked.connect(lambda: self.navigate_requested.emit("library"))
        self.attention_metric.clicked.connect(self._show_attention)
        for card in (
            self.active_metric,
            self.today_metric,
            self.library_metric,
            self.attention_metric,
        ):
            metrics.addWidget(card, 1)
        root.addLayout(metrics)

        dashboard_tools = QHBoxLayout()
        self.refresh_all_button = QPushButton("Refresh all figures")
        self.refresh_all_button.setObjectName("primaryButton")
        self.refresh_all_button.setToolTip("Queues a database/library report rebuild and refreshes Dashboard counts.")
        self.refresh_all_button.clicked.connect(self._refresh_all_figures)
        dashboard_tools.addWidget(self.refresh_all_button)
        dashboard_tools.addStretch()
        self.clear_failures_confirm = QCheckBox("clear all failures")
        self.clear_failures_confirm.setToolTip("Tick this before clearing all current failure entries.")
        self.clear_failures_button = QPushButton("Clear all failures")
        self.clear_failures_button.setObjectName("dangerButton")
        self.clear_failures_button.setToolTip("Clears/dismisses current failure records only. It does not delete media.")
        self.clear_failures_button.clicked.connect(self._clear_all_failures)
        dashboard_tools.addWidget(self.clear_failures_confirm)
        dashboard_tools.addWidget(self.clear_failures_button)
        root.addLayout(dashboard_tools)

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
        self.refresh_queue_button = QPushButton("Refresh queue")
        self.refresh_queue_button.setObjectName("secondaryButton")
        self.refresh_queue_button.setToolTip("Refresh queue rows and status now; does not rebuild the library.")
        self.refresh_queue_button.clicked.connect(self.refresh_fast)
        queue_header.addWidget(self.refresh_queue_button)
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
        self.failure_timer = QTimer(self)
        self.failure_timer.setInterval(5_000)
        self.failure_timer.timeout.connect(self.refresh_failure_count)

    def set_backend(self, backend: Any) -> None:
        self.backend = backend
        self.apply_settings_defaults(backend.web_config_view(), force=True)
        self.poll_timer.start()
        self.stats_timer.start()
        self.failure_timer.start()
        self.refresh_failure_count()
        self.refresh_fast()
        self.refresh_stats()

    def apply_settings_defaults(self, values: dict[str, Any] | None, *, force: bool = False) -> None:
        self.composer.apply_settings_defaults(values, force=force)

    def set_mode(self, mode: str) -> None:
        if mode == "queue":
            self.table.setFocus(Qt.FocusReason.OtherFocusReason)
        else:
            self.composer.urls.setFocus(Qt.FocusReason.OtherFocusReason)

    def focus_downloader(self) -> None:
        # More → New download should visibly open the complete downloader, not
        # merely switch to Dashboard and leave advanced options collapsed.
        self.composer.show_all_options()
        self.status_message.emit("Downloader ready · choose workflow and quality, then paste URL(s)")

    def set_failure_count(self, count: int) -> None:
        self.current_failure_count = max(0, int(count or 0))
        self.attention_metric.set_data(
            str(self.current_failure_count),
            "Review failures" if self.current_failure_count else "No known failures",
            "warn" if self.current_failure_count else "good",
        )

    def refresh_failure_count(self) -> None:
        if not self.backend:
            return
        try:
            loader = getattr(self.backend, "web_current_failure_rows", None)
            rows = loader() if callable(loader) else self.backend.web_download_failure_rows()
            self.set_failure_count(len(rows or []))
        except Exception:
            # Keep the last verified count instead of replacing it with stale
            # historical job totals or an arbitrary fallback.
            pass

    def refresh_fast(self) -> None:
        if not self.backend:
            return
        try:
            self.jobs = list(self.backend.web_job_snapshot() or [])
            self.failed_jobs = []
            self.live = dict(self.backend.snapshot() or {})
            self.queue_state = dict(self.backend.web_queue_state() or {})
        except Exception as exc:
            self.bottom_status.setText(f"Refresh failed: {exc}")
            return

        active = _number(self.queue_state.get("running"))
        queued = _number(self.queue_state.get("queued"))
        failed = _number(self.queue_state.get("failed"))
        completed_today = _number(self.library_stats.get("downloaded_today"))

        self.active_metric.set_data(str(active), f"{queued} waiting")
        self.today_metric.set_data(str(completed_today), "Downloaded today", "good")
        library_total = self.library_stats.get("available_downloaded_videos")
        self.library_metric.set_data(
            _compact_number(library_total) if library_total is not None else "—",
            f"{_compact_number(self.library_stats.get('database_rows'))} DB rows"
            if self.library_stats.get("database_rows") is not None
            else str(self.library_stats.get("source") or "Loading library…"),
        )
        # Needs attention represents current unresolved video failures only.
        # Historical failed job logs stay reviewable but must not re-inflate the
        # count after a user cleans a resolved failure.
        total_attention = int(self.current_failure_count)
        self.attention_metric.set_data(
            str(total_attention),
            "Review failures" if total_attention else "No known failures",
            "warn" if total_attention else "good",
        )
        terminal_finished = max(
            [float(job.get("finished_at") or 0) for job in self.jobs if str(job.get("status") or "").upper() in {"SUCCESS", "WARN", "FAILED", "CANCELLED"}]
            or [0.0]
        )
        if terminal_finished > self._stats_refreshed_through:
            self._stats_refresh_target = max(self._stats_refresh_target, terminal_finished)
            QTimer.singleShot(0, self.refresh_stats)
        batch = latest_batch_summary(self.jobs)
        if self.queue_state.get("paused"):
            queue_hint = "Queue paused"
        elif _number(batch.get("total")) > 1:
            queue_hint = f"{batch.get('done',0)} done · {batch.get('left',0)} left · {batch.get('running',0)} running"
        else:
            queue_hint = f"{active} running · {queued} waiting"
        self.queue_hint.setText(queue_hint)
        self.table.set_jobs(self.jobs, self.live, self.queue_state)
        selected_id = str(self._selected_job.get("job_id") or "")
        selected = next((job for job in self.jobs if str(job.get("job_id") or "") == selected_id), None)
        if selected is None and self.jobs:
            selected = self.jobs[0]
        self._select_job(selected or {})

        running_job = next(
            (job for job in self.jobs if str(job.get("status") or "").upper() in {"RUNNING", "CANCELLING"}),
            None,
        )
        global_progress = overall_progress_percent(running_job or {}, self.live) if active else 0
        self.bottom_progress.setValue(global_progress)
        self.bottom_count.setText(f"{active} active  ·  {queued} queued")
        status_text = str(
            self.live.get("current_status")
            or self.live.get("message")
            or ("Queue paused" if self.queue_state.get("paused") else "Ready")
        )
        self.bottom_status.setText(status_text[:64])

    def refresh_stats(self) -> None:
        if not self.backend:
            return
        if self._stats_running:
            self._stats_pending = True
            return
        self._stats_running = True
        self._stats_pending = False
        self._stats_inflight_target = self._stats_refresh_target
        task = FunctionTask("library_stats", self.backend.web_library_stats)
        self._background_tasks.add(task)
        task.signals.completed.connect(
            lambda key, value, running_task=task: self._finish_background_task(
                running_task, key, value=value
            )
        )
        task.signals.failed.connect(
            lambda key, message, running_task=task: self._finish_background_task(
                running_task, key, message=message
            )
        )
        self._pool.start(task)

    def _finish_background_task(
        self,
        task: FunctionTask,
        key: str,
        *,
        value: object | None = None,
        message: str | None = None,
    ) -> None:
        self._background_tasks.discard(task)
        if message is None:
            self._background_completed(key, value)
        else:
            self._background_failed(key, message)

    @Slot(str, object)
    def _background_completed(self, key: str, value: object) -> None:
        if key == "library_stats":
            self._stats_running = False
            self.library_stats = dict(value or {})
            self._stats_refreshed_through = max(self._stats_refreshed_through, self._stats_inflight_target)
            if self._stats_pending:
                QTimer.singleShot(0, self.refresh_stats)
            self.refresh_fast()
        elif key == "dashboard_figures":
            self._figures_running = False
            payload = dict(value or {})
            self.library_stats = dict(payload.get("stats") or self.library_stats)
            self.set_failure_count(int(payload.get("failure_count") or 0))
            self._stats_refreshed_through = max(self._stats_refreshed_through, self._stats_refresh_target)
            self.status_message.emit("Dashboard figures refreshed from current database and physical library.")
            self.refresh_fast()

    @Slot(str, str)
    def _background_failed(self, key: str, message: str) -> None:
        if key == "library_stats":
            self._stats_running = False
            self.library_metric.set_data("—", message, "bad")
            if self._stats_pending:
                QTimer.singleShot(0, self.refresh_stats)
        elif key == "dashboard_figures":
            self._figures_running = False
            QMessageBox.warning(self, "Could not refresh figures", message)

    @Slot(list, dict)
    def _start_download(self, urls: list[str], preset: dict[str, Any]) -> None:
        if not self.backend:
            return
        if not urls:
            QMessageBox.information(self, "Add a download", "Paste at least one video URL first.")
            self.composer.urls.setFocus()
            return
        duplicate_items: list[dict[str, Any]] = []
        try:
            checker = getattr(self.backend, "redownload_history_check", None)
            if callable(checker):
                duplicate_items.extend(list((checker(urls) or {}).get("items") or []))
            duplicate_items.extend(queue_duplicate_matches(urls, list(self.backend.web_job_snapshot() or [])))
        except Exception:
            pass
        # Duplicates pasted in the same request also require confirmation.
        identity_counts: dict[str, int] = {}
        identity_samples: dict[str, tuple[str, dict[str, Any]]] = {}
        for raw in urls:
            meta = initial_job_metadata(raw, "Input")
            ident = str(meta.get("video_id") or raw).strip()
            identity_counts[ident] = identity_counts.get(ident, 0) + 1
            identity_samples[ident] = (str(raw), meta)
        for ident, count in identity_counts.items():
            if count > 1:
                raw, meta = identity_samples[ident]
                duplicate_items.append({
                    "video_id": str(meta.get("video_id") or ""),
                    "url": raw,
                    "status": "ALREADY_IN_QUEUE",
                    "title": str(meta.get("display_name") or "Duplicate pasted URL"),
                })
        if duplicate_items:
            unique: dict[tuple[str, str, str], dict[str, Any]] = {}
            for item in duplicate_items:
                sig = (str(item.get("video_id") or ""), str(item.get("url") or ""), str(item.get("status") or ""))
                unique[sig] = item
            answer = QMessageBox.question(
                self,
                "Download again?",
                confirmation_message(list(unique.values())),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        self.composer.set_busy(True)
        try:
            writer=getattr(self.backend,"web_write_urls",None)
            if callable(writer):
                writer(urls)
            action = str(preset.get("action") or "full_download")
            quality = str(preset.get("quality") or "1080")
            workflow = str(preset.get("workflow") or ("audio_only" if quality == "audio" else action))
            resolve_embedded = bool(preset.get("resolve_embedded"))
            batch_id = f"download-{time.time_ns()}"
            job_ids: list[str] = []
            total = len(urls)
            for index, one_url in enumerate(urls, 1):
                suffix = f" {index}/{total}" if total > 1 else ""
                if action == "full_download":
                    type_name = "Full Library + Resolver" if resolve_embedded else "Full Library"
                    label = f"Full Library Download{suffix}"
                elif workflow == "audio_only" or quality == "audio":
                    type_name = "Audio Only + Resolver" if resolve_embedded else "Audio Only"
                    label = f"Audio Only Download{suffix}"
                else:
                    type_name = "Media Only + Resolver" if resolve_embedded else "Media Only"
                    label = f"{quality.upper()} Media Download{suffix}"
                job_id = self.backend.web_start_job(
                    label,
                    self.backend.web_download_workflow,
                    [one_url],
                    action,
                    resolve_embedded,
                    quality,
                    bool(preset.get("use_ollama")),
                    bool(preset.get("save_srt")),
                    False,
                    bool(preset.get("download_comments")),
                    "Entertainment",
                    bool(preset.get("vtt", True)),
                    "source",
                    bool(preset.get("smart_resume", True)),
                )
                self.backend.web_job_update(
                    job_id,
                    **initial_job_metadata(
                        one_url, type_name, batch_id=batch_id,
                        batch_index=index, batch_total=total
                    ),
                )
                job_ids.append(str(job_id))
            self.composer.clear_urls()
            self.status_message.emit(
                f"Added {len(urls)} URL(s) to the queue · "
                f"{', '.join(job_ids[:3])}{'…' if len(job_ids)>3 else ''}"
            )
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
            self.jobs,
        )

    def _show_attention(self) -> None:
        # Always open the authoritative Failure / Cleanup page. Selecting an old
        # queue row made the metric appear broken and mixed history with current
        # unresolved failures.
        self.navigate_requested.emit("failures")

    def _clear_all_failures(self) -> None:
        if not self.backend:
            return
        if not self.clear_failures_confirm.isChecked():
            QMessageBox.information(
                self,
                "Confirm clear all",
                "Tick the 'clear all failures' checkbox first. This prevents accidental cleanup.",
            )
            return
        answer = QMessageBox.question(
            self,
            "Clear all current failures",
            "Clear/dismiss all current failure entries from Dashboard and Failure/Cleanup?\n\n"
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
            self.clear_failures_confirm.setChecked(False)
            self.refresh_failure_count()
            self.refresh_fast()
        except Exception as exc:
            QMessageBox.warning(self, "Could not clear failures", f"{type(exc).__name__}: {exc}")

    def _refresh_all_figures(self) -> None:
        """Queue the physical-library/database reconciliation as a visible managed job."""
        if not self.backend:
            return
        try:
            function = getattr(self.backend, "refresh_dashboard_figures", None)
            starter = getattr(self.backend, "web_start_job", None)
            if not callable(function) or not callable(starter):
                self.status_message.emit("Dashboard refresh is unavailable.")
                return
            job_id = starter("Refresh all figures", function, True)
            self.status_message.emit(f"Refresh all figures queued · Job ID {job_id}")
            self.refresh_fast()
        except Exception as exc:
            QMessageBox.warning(self, "Could not refresh figures", f"{type(exc).__name__}: {exc}")

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
            elif action in {"pause_child", "cancel_child", "retry_child"}:
                parent_job_id, separator, video_id = str(job_id).partition("::")
                if not separator or not parent_job_id or not video_id:
                    ok, message = False, "Missing parent job or video ID."
                elif action == "pause_child":
                    ok, message = self.backend.web_pause_child_job(parent_job_id, video_id)
                elif action == "cancel_child":
                    ok, message = self.backend.web_cancel_child_job(parent_job_id, video_id)
                else:
                    ok, message, _new_job = self.backend.web_retry_child_job(parent_job_id, video_id)
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
                self.refresh_failure_count()
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
        ("new_download", "⇩", "New download", "Open the full Downloads tab with Full Library and Media Only options.", "Open downloader"),
        ("resume", "↻", "Resume downloads", "Audit incomplete items and safely continue only the work still needed.", "Run Smart Resume"),
        ("failures", "!", "Failure / Cleanup", "Review failed jobs, clear selected failures, reconcile stale errors, and cleanup safely.", "Open failures"),
        ("health", "♡", "Library health", "Back up metadata, check paths and dependencies, and apply safe repairs.", "Run health workflow"),
        ("knowledge", "✦", "Refresh knowledge", "Rebuild search indexes, knowledge pages, semantic data, and AI evidence.", "Refresh knowledge"),
        ("subscriptions", "◉", "YouTube subscriptions", "Collect subscribed channels, review suggested categories, and choose which channels to scan.", "Open subscriptions"),
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
            self.navigate_requested.emit("downloads")
            return
        if key == "failures":
            self.navigate_requested.emit("failures")
            return
        routes = {
            "chatgpt": ("chatgpt", ""),
            "subscriptions": ("subscriptions", ""),
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
    settings_saved = Signal(object)
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
        self.quality.addItems(("1080", "720", "480", "360", "best"))
        self.workers = QSpinBox()
        self.workers.setRange(1, 5)
        self.workers.setSuffix(" videos")
        self.subtitles = QCheckBox("Download subtitles when available")
        self.srt = QCheckBox("Save SRT by default")
        form.addWidget(self._field("Default quality", self.quality))
        form.addWidget(self._field("Simultaneous downloads", self.workers))
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
        self.openai_enabled = QCheckBox("Enable OpenAI API transcript intelligence")
        self.openai_model = QLineEdit()
        self.openai_model.setPlaceholderText("gpt-5.6")
        self.openai_effort = QComboBox()
        self.openai_effort.addItems(("none", "low", "medium", "high", "xhigh", "max"))
        self.openai_key_env = QLineEdit()
        self.openai_key_env.setPlaceholderText("OPENAI_API_KEY")
        self.openai_allow_restricted = QCheckBox("Allow private/unlisted/restricted videos to be sent to the API")
        self.openai_allow_restricted.setToolTip("Off by default. Enable only when you are authorized to send that content to an external API.")
        self.openai_status = QLabel("OpenAI API key is read from an environment variable; the key itself is never saved in VideoHoarder.")
        self.openai_status.setObjectName("mutedLabel")
        self.openai_status.setWordWrap(True)
        ai_layout.addWidget(self.ai_enabled)
        ai_layout.addWidget(self.smart_resume)
        ai_layout.addWidget(self.fast_mode)
        ai_layout.addWidget(self._field("Local model", self.model))
        ai_layout.addSpacing(8)
        ai_layout.addWidget(self.openai_enabled)
        ai_layout.addWidget(self._field("OpenAI model", self.openai_model))
        ai_layout.addWidget(self._field("Reasoning effort", self.openai_effort))
        ai_layout.addWidget(self._field("API-key environment variable", self.openai_key_env))
        ai_layout.addWidget(self.openai_allow_restricted)
        ai_layout.addWidget(self.openai_status)
        grid.addWidget(intelligence, 0, 1)

        privacy = self._section("Source access", "Browser-cookie access is off by default. Enable it only when YouTube access or a 403/login-restricted retry requires it.")
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
        self.workers.setValue(_number(values.get("parallel_videos"), 2))
        self.subtitles.setChecked(bool(values.get("download_subtitles")))
        self.srt.setChecked(bool(values.get("save_srt_default")))
        self.ai_enabled.setChecked(bool(values.get("ai_enabled")))
        self.smart_resume.setChecked(bool(values.get("smart_resume")))
        self.fast_mode.setChecked(bool(values.get("fast_no_llm_mode")))
        self.model.setText(str(values.get("ollama_model") or ""))
        self.openai_enabled.setChecked(bool(values.get("openai_api_enabled")))
        self.openai_model.setText(str(values.get("openai_model") or "gpt-5.6"))
        self.openai_effort.setCurrentText(str(values.get("openai_reasoning_effort") or "high"))
        self.openai_key_env.setText(str(values.get("openai_api_key_env") or "OPENAI_API_KEY"))
        self.openai_allow_restricted.setChecked(bool(values.get("openai_allow_restricted_videos")))
        try:
            api_status=self.backend.chatgpt_openai_api_status()
            self.openai_status.setText(("Ready" if api_status.get("ready") else "Not ready") + " - " + str(api_status.get("message") or "") + " Key value is never stored by VideoHoarder.")
        except Exception:
            self.openai_status.setText("OpenAI API status unavailable. The API key value is never stored by VideoHoarder.")
        self.cookies.setCurrentText(str(values.get("cookies_mode") or "none"))
        self.browser.setCurrentText(str(values.get("browser_for_cookies") or "firefox"))

    @Slot()
    def save(self) -> None:
        if not self.backend:
            return
        values = {
            "download_quality": self.quality.currentText(),
            "parallel_videos": self.workers.value(),
            "download_subtitles": self.subtitles.isChecked(),
            "save_srt_default": self.srt.isChecked(),
            "ai_enabled": self.ai_enabled.isChecked(),
            "smart_resume": self.smart_resume.isChecked(),
            "fast_no_llm_mode": self.fast_mode.isChecked(),
            "ollama_model": self.model.text().strip(),
            "openai_api_enabled": self.openai_enabled.isChecked(),
            "openai_model": self.openai_model.text().strip() or "gpt-5.6",
            "openai_reasoning_effort": self.openai_effort.currentText(),
            "openai_api_key_env": self.openai_key_env.text().strip() or "OPENAI_API_KEY",
            "openai_allow_restricted_videos": self.openai_allow_restricted.isChecked(),
            "cookies_mode": self.cookies.currentText(),
            "browser_for_cookies": self.browser.currentText(),
        }
        try:
            result = self.backend.web_config_update(values)
            message = str(result.get("message") or "Settings saved")
            self.status_message.emit(message)
            if result.get("ok"):
                saved = dict(result.get("settings") or values)
                self.settings_saved.emit(saved)
            else:
                QMessageBox.warning(self, "Settings not saved", message + ("\n" + "\n".join(result.get("errors") or []) if result.get("errors") else ""))
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
    QLabel#globalNotice { background: #0c192b; color: #dce8f8; border-top: 1px solid #243650; padding: 7px 14px; font-size: 12px; }

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
    QPushButton#dangerButton { background: #3b1f28; color: #ffb4bf; border: 1px solid #74404c; border-radius: 7px; padding: 8px 12px; font-weight: 650; }
    QPushButton#dangerButton:hover { background: #542634; border-color: #a64e60; color: white; }
    QPushButton#videoLinkButton { color: #e7edf6; background: transparent; border: 0; padding: 0; text-align: left; font-weight: 700; }
    QPushButton#videoLinkButton:hover { color: #6aa8ff; text-decoration: underline; }
    QPushButton#linkButton { color: #4f96ff; background: transparent; border: 0; padding: 4px 1px; text-align: left; font-weight: 600; }
    QPushButton#linkButton:hover { color: #82b5ff; }

    QTableWidget#queueTable, QTableWidget#libraryTable, QTableWidget#failureTable { background: #111c2d; alternate-background-color: #111c2d; border: 1px solid #223149; border-radius: 9px; color: #e7edf6; outline: 0; }
    QTableWidget#queueTable::item, QTableWidget#libraryTable::item, QTableWidget#failureTable::item { border-bottom: 1px solid #26354a; padding: 8px; }
    QTableWidget#queueTable::item:selected { background: #172d4b; border-top: 1px solid #2277ec; border-bottom: 1px solid #2277ec; }
    QLabel#emptyQueue { color: #708198; font-size: 14px; background: transparent; }
    QHeaderView::section { background: #111c2d; color: #bdc8d8; border: 0; border-bottom: 1px solid #2a394f; padding: 11px 8px; font-weight: 650; }
    QScrollBar:vertical { background: #0d1726; width: 10px; margin: 0; }
    QScrollBar::handle:vertical { background: #34445d; min-height: 26px; border-radius: 5px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QScrollBar:horizontal { background: #0d1726; height: 11px; margin: 0; }
    QScrollBar::handle:horizontal { background: #34445d; min-width: 30px; border-radius: 5px; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
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
