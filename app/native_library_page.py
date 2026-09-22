"""Native Library browser for the VideoHoarder desktop shell.

This keeps everyday Library browsing out of the legacy web page and out of the
monolithic app.py.  It provides thumbnail/title rows, click-to-play, live date
sorting, and server-side pagination with a user-selectable page size.
"""

from __future__ import annotations

import math
import os
from typing import Any

from PySide6.QtCore import Qt, QUrl, Signal, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from .native_ui import FunctionTask
from .lru_cache import LRUCache

from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
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


class NativeLibraryPage(QWidget):
    """Fast native Library page backed by ``web_library_page``."""

    open_video_requested = Signal(str)
    status_message = Signal(str)

    PAGE_SIZES = (25, 50, 100, 200, 500)
    FILTERS = (
        ("Last 7 days", "latest"),
        ("All library videos", "all"),
        ("Downloaded", "downloaded"),
        ("Favorites", "favorites"),
        ("Unwatched", "unwatched"),
        ("Failures", "failed"),
    )
    SORTS = (
        ("Newest downloaded first", "downloaded_desc"),
        ("Oldest downloaded first", "downloaded_asc"),
        ("Video A-Z", "title"),
        ("Channel A-Z", "channel"),
        ("Category A-Z", "category"),
    )

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("nativeLibraryPage")
        self.backend: Any | None = None
        self._rows: list[dict[str, Any]] = []
        self._page = 1
        self._total = 0
        self._thumbnail_cache: LRUCache[str, QPixmap] = LRUCache(max_items=256)
        self._thumbnail_manager = QNetworkAccessManager(self)
        self._refresh_serial = 0
        self._refresh_busy = False

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 20)
        root.setSpacing(12)

        title = QLabel("Library")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Browse downloaded videos, sort by real download date, and click a video to play it.")
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        controls = QFrame()
        controls.setObjectName("libraryControls")
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(10)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search title, video ID, channel, category…")
        self.search.returnPressed.connect(self.refresh)
        controls_layout.addWidget(self.search, 1)

        self.filter = QComboBox()
        for label, key in self.FILTERS:
            self.filter.addItem(label, key)
        self.filter.currentIndexChanged.connect(self._control_changed)
        controls_layout.addWidget(self.filter)

        self.sort = QComboBox()
        for label, key in self.SORTS:
            self.sort.addItem(label, key)
        self.sort.currentIndexChanged.connect(self._control_changed)
        controls_layout.addWidget(self.sort)

        self.page_size = QComboBox()
        for size in self.PAGE_SIZES:
            self.page_size.addItem(f"{size} per page", size)
        self.page_size.setCurrentIndex(self.PAGE_SIZES.index(100))
        self.page_size.currentIndexChanged.connect(self._page_size_changed)
        controls_layout.addWidget(self.page_size)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("secondaryButton")
        self.refresh_button.clicked.connect(self.refresh)
        controls_layout.addWidget(self.refresh_button)
        root.addWidget(controls)

        self.summary = QLabel("Loading library…")
        self.summary.setObjectName("mutedLabel")
        root.addWidget(self.summary)

        self.table = QTableWidget(0, 4)
        self.table.setObjectName("libraryTable")
        self.table.setHorizontalHeaderLabels(("Video", "Channel", "Category", "Downloaded"))
        self.table.verticalHeader().hide()
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(2, 210)
        self.table.setColumnWidth(3, 170)
        self.table.cellDoubleClicked.connect(self._double_clicked)
        root.addWidget(self.table, 1)

        pager = QHBoxLayout()
        pager.setSpacing(8)
        self.previous = QPushButton("← Previous")
        self.previous.setObjectName("secondaryButton")
        self.previous.clicked.connect(self._previous_page)
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setObjectName("mutedLabel")
        self.next = QPushButton("Next →")
        self.next.setObjectName("secondaryButton")
        self.next.clicked.connect(self._next_page)
        pager.addStretch()
        pager.addWidget(self.previous)
        pager.addWidget(self.page_label)
        pager.addWidget(self.next)
        root.addLayout(pager)

    def set_backend(self, backend: Any) -> None:
        self.backend = backend
        self.refresh()

    def activate(self) -> None:
        """Refresh when the user re-opens Library so new downloads appear immediately."""
        if self.backend:
            self.refresh()

    def _control_changed(self, _index: int = 0) -> None:
        self._page = 1
        self.refresh()

    def _page_size_changed(self, _index: int = 0) -> None:
        self._page = 1
        self.refresh()

    @Slot()
    def refresh(self) -> None:
        if not self.backend:
            return
        self._refresh_serial += 1
        serial = self._refresh_serial
        query = self.search.text().strip()
        filter_key = str(self.filter.currentData() or "all")
        sort_key = str(self.sort.currentData() or "downloaded_desc")
        page = self._page
        page_size = self._page_size()
        backend = self.backend
        self._refresh_busy = True
        self.refresh_button.setEnabled(False)
        self.summary.setText("Loading library…")
        task = FunctionTask(
            f"library_page:{serial}",
            lambda: backend.web_library_page(query, filter_key, page, page_size, sort_key) or {},
        )
        task.signals.completed.connect(self._refresh_completed)
        task.signals.failed.connect(self._refresh_failed)
        from PySide6.QtCore import QThreadPool
        QThreadPool.globalInstance().start(task)

    @Slot(str, object)
    def _refresh_completed(self, key: str, value: object) -> None:
        try:
            serial = int(str(key).split(":", 1)[1])
        except (ValueError, IndexError):
            return
        if serial != self._refresh_serial:
            return
        payload = dict(value or {})
        self._rows = list(payload.get("items") or [])
        self._total = int(payload.get("total") or 0)
        self._page = max(1, int(payload.get("page") or self._page))
        self._refresh_busy = False
        self.refresh_button.setEnabled(True)
        self._render_page()

    @Slot(str, str)
    def _refresh_failed(self, key: str, message: str) -> None:
        try:
            serial = int(str(key).split(":", 1)[1])
        except (ValueError, IndexError):
            return
        if serial != self._refresh_serial:
            return
        self._refresh_busy = False
        self.refresh_button.setEnabled(True)
        self._rows = []
        self._total = 0
        self._render_page()
        self.status_message.emit(f"Library refresh failed: {message}")

    def _page_size(self) -> int:
        try:
            return max(1, int(self.page_size.currentData() or 100))
        except Exception:
            return 100

    def _max_page(self) -> int:
        return max(1, math.ceil(self._total / self._page_size()))

    def _render_page(self) -> None:
        page_size = self._page_size()
        max_page = self._max_page()
        self._page = max(1, min(self._page, max_page))
        start = (self._page - 1) * page_size
        rows = self._rows

        self.table.setUpdatesEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            self.table.setRowHeight(row_index, 92)
            video_id = str(row.get("video_id") or "")
            marker = QTableWidgetItem("")
            marker.setData(Qt.ItemDataRole.UserRole, video_id)
            self.table.setItem(row_index, 0, marker)
            self.table.setCellWidget(row_index, 0, self._video_widget(row))
            self.table.setItem(row_index, 1, QTableWidgetItem(str(row.get("channel") or "")))
            category = str(row.get("category") or "Other")
            subcategory = str(row.get("subcategory") or "General")
            self.table.setItem(row_index, 2, QTableWidgetItem(f"{category} / {subcategory}"))
            self.table.setItem(row_index, 3, QTableWidgetItem(str(row.get("downloaded_at") or "—")))
        self.table.setUpdatesEnabled(True)

        total = self._total
        shown_start = start + 1 if rows else 0
        shown_end = start + len(rows)
        self.summary.setText(
            f"{total:,} videos match · showing {shown_start:,}-{shown_end:,} · "
            f"{page_size} per page"
        )
        self.page_label.setText(f"Page {self._page} of {max_page}")
        self.previous.setEnabled(self._page > 1)
        self.next.setEnabled(self._page < max_page)

    def _video_widget(self, row: dict[str, Any]) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        thumbnail = QLabel()
        thumbnail.setFixedSize(120, 68)
        thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumbnail.setText("▣")
        thumbnail.setStyleSheet(
            "border:1px solid #314159;border-radius:6px;color:#6f829c;background:#0d1726;"
        )
        self._load_thumbnail(thumbnail, row)
        layout.addWidget(thumbnail, 0)

        text = QWidget()
        text_layout = QVBoxLayout(text)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        title = QPushButton(str(row.get("title") or row.get("video_id") or "Video"))
        title.setObjectName("videoLinkButton")
        title.setCursor(Qt.CursorShape.PointingHandCursor)
        title.setToolTip("Play this downloaded video")
        title.clicked.connect(lambda _checked=False, item=dict(row): self._open_video(item))
        identifier = QLabel(str(row.get("video_id") or ""))
        identifier.setObjectName("mutedLabel")
        text_layout.addWidget(title)
        text_layout.addWidget(identifier)
        layout.addWidget(text, 1)
        return widget

    def _load_thumbnail(self, label: QLabel, row: dict[str, Any]) -> None:
        source = str(row.get("thumbnail_url") or "").strip()
        if not source:
            video_id = str(row.get("video_id") or "").strip()
            if video_id:
                source = f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
        if not source:
            return
        try:
            local = os.path.expandvars(os.path.expanduser(source))
            if os.path.isfile(local):
                pixmap = QPixmap(local)
                if not pixmap.isNull():
                    self._apply_thumbnail(label, pixmap)
                return
        except Exception:
            pass
        cached = self._thumbnail_cache.get(source)
        if cached is not None:
            self._apply_thumbnail(label, cached)
            return
        if not source.lower().startswith(("http://", "https://")):
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

    @staticmethod
    def _apply_thumbnail(label: QLabel, pixmap: QPixmap) -> None:
        if pixmap.isNull():
            return
        label.setPixmap(
            pixmap.scaled(
                120,
                68,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        label.setText("")

    def _open_video(self, row: dict[str, Any]) -> None:
        video_id = str(row.get("video_id") or "").strip()
        if not video_id:
            return
        if not bool(row.get("has_media")):
            QMessageBox.information(self, "Video unavailable", "This Library row does not currently have a local media file.")
            return
        self.open_video_requested.emit(video_id)
        self.status_message.emit(f"Opening video · {row.get('title') or video_id}")

    @Slot(int, int)
    def _double_clicked(self, row_index: int, _column: int) -> None:
        item = self.table.item(row_index, 0)
        video_id = str(item.data(Qt.ItemDataRole.UserRole) or "") if item else ""
        row = next((x for x in self._rows if str(x.get("video_id") or "") == video_id), None)
        if row:
            self._open_video(row)

    def _previous_page(self) -> None:
        if self._page > 1:
            self._page -= 1
            self.refresh()

    def _next_page(self) -> None:
        if self._page < self._max_page():
            self._page += 1
            self.refresh()
