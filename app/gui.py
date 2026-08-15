"""Native PySide6 desktop shell for the VideoHoarder web application.

The mature application UI and backend remain in :mod:`app.app`.  This module
hosts that local-only UI in Qt WebEngine and adds the behavior users expect
from a Windows desktop application: no terminal, native menus/navigation,
safe external links, download dialogs, persistent window state and graceful
shutdown of long-running work.
"""

from __future__ import annotations

import io
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
import threading
import traceback
from typing import Any

from PySide6.QtCore import (
    QObject,
    QSettings,
    QStandardPaths,
    Qt,
    QThread,
    QTimer,
    QUrl,
    Signal,
    Slot,
)
from PySide6.QtGui import QAction, QCloseEvent, QDesktopServices, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QStyle,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView


APP_NAME = "VideoHoarder"
ORGANIZATION_NAME = "VideoHoarder"
GUI_VERSION = "33.0"
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
_SINGLE_INSTANCE_MUTEX = None

from .native_ui import CommandCenter, SettingsPage, Sidebar, WorkflowsPage, desktop_stylesheet


def application_root() -> Path:
    """Return the persistent portable app root in source and frozen builds."""
    if getattr(sys, "frozen", False):
        release_root = Path(sys.executable).resolve().parent
        portable_data = release_root / "Downloads"
        return portable_data if portable_data.is_dir() else release_root
    return Path(__file__).resolve().parent.parent


def bundled_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", application_root())).resolve()


def resource_path(relative: str) -> Path:
    bundled = bundled_root() / relative
    return bundled if bundled.exists() else application_root() / relative


class LogStream(io.TextIOBase):
    """Thread-safe rotating log target that is safe under pythonw.exe."""

    def __init__(self, path: Path, level: int) -> None:
        super().__init__()
        path.parent.mkdir(parents=True, exist_ok=True)
        logger_name = f"{APP_NAME}.{path.stem}.{level}"
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(level)
        self._logger.propagate = False
        if not self._logger.handlers:
            handler = RotatingFileHandler(
                path,
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            )
            handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
            self._logger.addHandler(handler)
        self._level = level
        self._lock = threading.RLock()

    @property
    def encoding(self) -> str:
        return "utf-8"

    def writable(self) -> bool:
        return True

    def write(self, value: str) -> int:
        text = str(value or "")
        if not text:
            return 0
        cleaned = text.replace("\r", "\n").strip("\n")
        if cleaned.strip():
            with self._lock:
                for line in cleaned.splitlines():
                    if line.strip():
                        self._logger.log(self._level, line.rstrip())
        return len(text)

    def flush(self) -> None:
        with self._lock:
            for handler in self._logger.handlers:
                handler.flush()


def install_file_logging() -> Path:
    log_path = application_root() / "logs" / "gui.log"
    sys.stdout = LogStream(log_path, logging.INFO)
    sys.stderr = LogStream(log_path, logging.ERROR)
    print(f"{APP_NAME} GUI {GUI_VERSION} starting")
    return log_path


class BackendWorker(QObject):
    ready = Signal(str, object, object)
    failed = Signal(str)

    @Slot()
    def start(self) -> None:
        try:
            from . import app as backend

            # The embedded dashboard is the progress UI; terminal-style status
            # lines would only create a noisy log file in a windowed build.
            backend.CFG["console_progress"] = False
            backend.ensure_project_layout()
            backend.migrate_legacy_root_files()
            backend.DOWNLOADS.mkdir(parents=True, exist_ok=True)
            server = backend.start_dashboard(open_browser=False)
            port = int(server.server_address[1])
            self.ready.emit(f"http://127.0.0.1:{port}", server, backend)
        except Exception:
            self.failed.emit(traceback.format_exc())


class SafeWebPage(QWebEnginePage):
    """Keep app navigation embedded and send public links to the browser."""

    popup_requested = Signal(QUrl)

    def __init__(self, profile: QWebEngineProfile, parent: QObject | None = None) -> None:
        super().__init__(profile, parent)
        self._popup_pages: list[QWebEnginePage] = []

    @staticmethod
    def _is_local(url: QUrl) -> bool:
        return url.scheme() in {"http", "https"} and url.host().lower() in LOCAL_HOSTS

    def acceptNavigationRequest(
        self,
        url: QUrl,
        navigation_type: QWebEnginePage.NavigationType,
        is_main_frame: bool,
    ) -> bool:
        if is_main_frame and url.isValid() and url.scheme() not in {"about", "data"}:
            if not self._is_local(url):
                QDesktopServices.openUrl(url)
                return False
        return super().acceptNavigationRequest(url, navigation_type, is_main_frame)

    def createWindow(self, window_type: QWebEnginePage.WebWindowType) -> QWebEnginePage:
        popup = QWebEnginePage(self.profile(), self)
        popup.urlChanged.connect(self.popup_requested.emit)
        popup.destroyed.connect(lambda: self._remove_popup(popup))
        self._popup_pages.append(popup)
        return popup

    def _remove_popup(self, popup: QWebEnginePage) -> None:
        if popup in self._popup_pages:
            self._popup_pages.remove(popup)

    def javaScriptConsoleMessage(
        self,
        level: QWebEnginePage.JavaScriptConsoleMessageLevel,
        message: str,
        line_number: int,
        source_id: str,
    ) -> None:
        if level != QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel:
            print(f"Web UI: {message} ({source_id}:{line_number})", file=sys.stderr)


class LoadingPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("loadingPanel")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 48, 48, 48)
        outer.addStretch(2)

        card = QFrame()
        card.setObjectName("loadingCard")
        card.setMaximumWidth(560)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(38, 34, 38, 34)
        layout.setSpacing(14)

        title = QLabel("VideoHoarder")
        title.setObjectName("loadingTitle")
        subtitle = QLabel("Starting your private video library…")
        subtitle.setObjectName("loadingSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message = QLabel("Preparing local services")
        self.message.setObjectName("loadingMessage")
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress = QProgressBar()
        progress.setRange(0, 0)
        progress.setTextVisible(False)
        progress.setFixedHeight(7)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addWidget(progress)
        layout.addWidget(self.message)

        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(card)
        row.addStretch()
        outer.addLayout(row)
        outer.addStretch(3)


class ErrorPanel(QWidget):
    retry_requested = Signal()
    open_log_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 48, 48, 48)
        outer.addStretch()
        title = QLabel("VideoHoarder could not start")
        title.setObjectName("errorTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details = QLabel()
        self.details.setWordWrap(True)
        self.details.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        retry = QPushButton("Try Again")
        retry.clicked.connect(self.retry_requested)
        logs = QPushButton("Open Log Folder")
        logs.clicked.connect(self.open_log_requested)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(retry)
        row.addWidget(logs)
        row.addStretch()
        outer.addWidget(title)
        outer.addWidget(self.details)
        outer.addLayout(row)
        outer.addStretch()

    def set_error(self, trace: str) -> None:
        last_line = next((line for line in reversed(trace.splitlines()) if line.strip()), trace)
        self.details.setText(f"{last_line}\n\nFull details were written to logs/gui.log.")


class LegacyMainWindow(QMainWindow):
    def __init__(self, log_path: Path) -> None:
        super().__init__()
        self.log_path = log_path
        self.backend: Any | None = None
        self.server: Any | None = None
        self.base_url = ""
        self.backend_thread: QThread | None = None
        self.backend_worker: BackendWorker | None = None
        self._closing = False

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1000, 680)
        icon = QIcon(str(resource_path("assets/app_icon.svg")))
        if not icon.isNull():
            self.setWindowIcon(icon)

        self.settings = QSettings(ORGANIZATION_NAME, APP_NAME)
        self.stack = QStackedWidget()
        self.loading_panel = LoadingPanel()
        self.error_panel = ErrorPanel()
        self.error_panel.retry_requested.connect(self.start_backend)
        self.error_panel.open_log_requested.connect(self.open_log_folder)
        self.stack.addWidget(self.loading_panel)
        self.stack.addWidget(self.error_panel)

        self.profile = self._create_profile()
        self.web_view = QWebEngineView()
        self.web_page = SafeWebPage(self.profile, self.web_view)
        self.web_page.popup_requested.connect(self.handle_popup)
        self.web_view.setPage(self.web_page)
        self._configure_web_view()
        self.stack.addWidget(self.web_view)
        self.setCentralWidget(self.stack)

        self._build_actions()
        self._build_toolbar()
        self._build_menus()
        self._apply_style()
        self._restore_window_state()
        QTimer.singleShot(0, self.start_backend)

    def _create_profile(self) -> QWebEngineProfile:
        storage = application_root() / "data" / "gui"
        cache = storage / "cache"
        storage.mkdir(parents=True, exist_ok=True)
        cache.mkdir(parents=True, exist_ok=True)
        profile = QWebEngineProfile(APP_NAME, self)
        profile.setPersistentStoragePath(str(storage))
        profile.setCachePath(str(cache))
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
        )
        profile.setHttpUserAgent(f"{profile.httpUserAgent()} {APP_NAME}/{GUI_VERSION}")
        profile.downloadRequested.connect(self.handle_download)
        return profile

    def _configure_web_view(self) -> None:
        page_settings = self.web_page.settings()
        page_settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        page_settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        page_settings.setAttribute(
            QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False
        )
        self.web_page.fullScreenRequested.connect(self.handle_fullscreen_request)
        self.web_view.loadStarted.connect(lambda: self.load_progress.setVisible(True))
        self.web_view.loadProgress.connect(self._set_load_progress)
        self.web_view.loadFinished.connect(self._load_finished)
        self.web_view.titleChanged.connect(self._update_title)
        self.web_view.urlChanged.connect(self._update_navigation_actions)

    def _build_actions(self) -> None:
        style = self.style()
        self.back_action = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack), "Back", self)
        self.back_action.setShortcut(QKeySequence.StandardKey.Back)
        self.back_action.triggered.connect(self.web_view.back)
        self.forward_action = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward), "Forward", self)
        self.forward_action.setShortcut(QKeySequence.StandardKey.Forward)
        self.forward_action.triggered.connect(self.web_view.forward)
        self.reload_action = QAction(style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "Reload", self)
        self.reload_action.setShortcut(QKeySequence.StandardKey.Refresh)
        self.reload_action.triggered.connect(self.web_view.reload)

        self.home_action = QAction("Dashboard", self)
        self.home_action.setShortcut("Alt+Home")
        self.home_action.triggered.connect(lambda: self.navigate("/app"))
        self.downloads_action = QAction("Downloads", self)
        self.downloads_action.triggered.connect(lambda: self.navigate("/app?tab=downloads"))
        self.library_action = QAction("Library", self)
        self.library_action.triggered.connect(lambda: self.navigate("/app?tab=library"))
        self.knowledge_action = QAction("Knowledge", self)
        self.knowledge_action.triggered.connect(lambda: self.navigate("/knowledge"))
        self.tools_action = QAction("Tools & Settings", self)
        self.tools_action.triggered.connect(lambda: self.navigate("/app?tab=tools"))
        self.help_action = QAction("Help", self)
        self.help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        self.help_action.triggered.connect(lambda: self.navigate("/help"))

        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.zoom_in_action.triggered.connect(lambda: self.set_zoom(self.web_view.zoomFactor() + 0.1))
        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.zoom_out_action.triggered.connect(lambda: self.set_zoom(self.web_view.zoomFactor() - 0.1))
        self.zoom_reset_action = QAction("Actual Size", self)
        self.zoom_reset_action.setShortcut("Ctrl+0")
        self.zoom_reset_action.triggered.connect(lambda: self.set_zoom(1.0))
        self.fullscreen_action = QAction("Full Screen", self)
        self.fullscreen_action.setShortcut("F11")
        self.fullscreen_action.setCheckable(True)
        self.fullscreen_action.triggered.connect(self.set_fullscreen)

        self.open_external_action = QAction("Open Current Page in Browser", self)
        self.open_external_action.triggered.connect(
            lambda: QDesktopServices.openUrl(self.web_view.url())
        )
        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.triggered.connect(self.close)

        self._server_actions = [
            self.home_action,
            self.downloads_action,
            self.library_action,
            self.knowledge_action,
            self.tools_action,
            self.help_action,
            self.open_external_action,
        ]
        for action in self._server_actions:
            action.setEnabled(False)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Navigation", self)
        toolbar.setObjectName("navigationToolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.addAction(self.back_action)
        toolbar.addAction(self.forward_action)
        toolbar.addAction(self.reload_action)
        toolbar.addSeparator()
        toolbar.addAction(self.home_action)
        toolbar.addAction(self.downloads_action)
        toolbar.addAction(self.library_action)
        toolbar.addAction(self.knowledge_action)
        toolbar.addAction(self.tools_action)
        toolbar.addAction(self.help_action)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        self.load_progress = QProgressBar()
        self.load_progress.setObjectName("loadProgress")
        self.load_progress.setFixedSize(90, 6)
        self.load_progress.setTextVisible(False)
        self.load_progress.setVisible(False)
        toolbar.addWidget(self.load_progress)
        self.connection_badge = QLabel("STARTING")
        self.connection_badge.setObjectName("connectionBadge")
        toolbar.addWidget(self.connection_badge)
        self.addToolBar(toolbar)

    def _build_menus(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.open_external_action)
        file_menu.addSeparator()
        file_menu.addAction("Open Library Folder", self.open_library_folder)
        file_menu.addAction("Open Downloads Folder", self.open_downloads_folder)
        file_menu.addAction("Open Log Folder", self.open_log_folder)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        navigate_menu = self.menuBar().addMenu("&Navigate")
        navigate_menu.addActions(
            [
                self.home_action,
                self.downloads_action,
                self.library_action,
                self.knowledge_action,
                self.tools_action,
                self.help_action,
            ]
        )

        view_menu = self.menuBar().addMenu("&View")
        view_menu.addActions(
            [
                self.back_action,
                self.forward_action,
                self.reload_action,
                self.zoom_in_action,
                self.zoom_out_action,
                self.zoom_reset_action,
                self.fullscreen_action,
            ]
        )

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(self.help_action)
        help_menu.addAction("About VideoHoarder", self.show_about)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow { background: #eef3f8; }
            QMenuBar { background: #ffffff; color: #172840; padding: 3px 6px; }
            QMenuBar::item:selected, QMenu::item:selected { background: #dcecff; }
            QMenu { background: #ffffff; color: #172840; border: 1px solid #c8d5e5; }
            QToolBar#navigationToolbar {
                background: #ffffff; border: 0; border-bottom: 1px solid #cfd9e6;
                padding: 5px 8px; spacing: 4px;
            }
            QToolButton { color: #18304d; padding: 6px 9px; border-radius: 6px; }
            QToolButton:hover { background: #e7f1ff; }
            QLabel#connectionBadge {
                color: #ffffff; background: #66788f; border-radius: 8px;
                font-size: 10px; font-weight: 700; padding: 4px 8px; margin-left: 8px;
            }
            QProgressBar#loadProgress { border: 0; background: #dde5ee; border-radius: 3px; }
            QProgressBar#loadProgress::chunk { background: #0a72e8; border-radius: 3px; }
            QWidget#loadingPanel { background: #edf3f9; }
            QFrame#loadingCard {
                background: #ffffff; border: 1px solid #d4dfeb; border-radius: 16px;
            }
            QLabel#loadingTitle { color: #102b4b; font-size: 34px; font-weight: 800; }
            QLabel#loadingSubtitle { color: #425c78; font-size: 16px; }
            QLabel#loadingMessage { color: #71849a; }
            QLabel#errorTitle { color: #a32222; font-size: 24px; font-weight: 750; }
            QPushButton {
                background: #0b6fdc; color: white; border: 0; border-radius: 7px;
                padding: 8px 14px; font-weight: 650;
            }
            QPushButton:hover { background: #095fbc; }
            """
        )

    def _restore_window_state(self) -> None:
        geometry = self.settings.value("window/geometry")
        state = self.settings.value("window/state")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1440, 900)
        if state:
            self.restoreState(state)
        zoom = float(self.settings.value("browser/zoom", 1.0))
        self.web_view.setZoomFactor(max(0.6, min(2.0, zoom)))

    @Slot()
    def start_backend(self) -> None:
        if self.backend_thread and self.backend_thread.isRunning():
            return
        self.stack.setCurrentWidget(self.loading_panel)
        self.connection_badge.setText("STARTING")
        for action in self._server_actions:
            action.setEnabled(False)
        thread = QThread(self)
        worker = BackendWorker()
        worker.moveToThread(thread)
        thread.started.connect(worker.start)
        worker.ready.connect(self.backend_ready)
        worker.failed.connect(self.backend_failed)
        worker.ready.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(self._backend_thread_finished)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.backend_thread = thread
        self.backend_worker = worker
        thread.start()

    @Slot()
    def _backend_thread_finished(self) -> None:
        self.backend_thread = None
        self.backend_worker = None

    @Slot(str, object, object)
    def backend_ready(self, base_url: str, server: Any, backend: Any) -> None:
        self.base_url = base_url.rstrip("/")
        self.server = server
        self.backend = backend
        self.connection_badge.setText("LOCAL · READY")
        self.connection_badge.setToolTip(
            f"Private local server\n{self.base_url}\nLibrary: {backend.BASE}"
        )
        for action in self._server_actions:
            action.setEnabled(True)
        self.stack.setCurrentWidget(self.web_view)
        self.navigate("/app")
        self.statusBar().showMessage(f"Library: {backend.BASE}", 8000)

    @Slot(str)
    def backend_failed(self, trace: str) -> None:
        print(trace, file=sys.stderr)
        self.connection_badge.setText("START FAILED")
        self.error_panel.set_error(trace)
        self.stack.setCurrentWidget(self.error_panel)

    def navigate(self, path: str) -> None:
        if not self.base_url:
            return
        path = path if path.startswith("/") else f"/{path}"
        self.web_view.setUrl(QUrl(f"{self.base_url}{path}"))

    @Slot(QUrl)
    def handle_popup(self, url: QUrl) -> None:
        if not url.isValid() or url.scheme() == "about":
            return
        if url.host().lower() in LOCAL_HOSTS:
            self.web_view.setUrl(url)
        else:
            QDesktopServices.openUrl(url)

    @Slot(object)
    def handle_download(self, download: Any) -> None:
        suggested = download.downloadFileName() or "download"
        default_dir = self.settings.value(
            "downloads/last_directory",
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation),
        )
        target, _ = QFileDialog.getSaveFileName(
            self,
            "Save Download",
            str(Path(str(default_dir)) / suggested),
        )
        if not target:
            download.cancel()
            return
        target_path = Path(target)
        self.settings.setValue("downloads/last_directory", str(target_path.parent))
        download.setDownloadDirectory(str(target_path.parent))
        download.setDownloadFileName(target_path.name)
        download.accept()
        self.statusBar().showMessage(f"Downloading {target_path.name}…")
        download.isFinishedChanged.connect(
            lambda: self.statusBar().showMessage(f"Saved: {target_path}", 8000)
        )

    @Slot(object)
    def handle_fullscreen_request(self, request: Any) -> None:
        request.accept()
        self.set_fullscreen(bool(request.toggleOn()))

    @Slot(bool)
    def set_fullscreen(self, enabled: bool) -> None:
        self.fullscreen_action.setChecked(enabled)
        self.menuBar().setVisible(not enabled)
        for toolbar in self.findChildren(QToolBar):
            toolbar.setVisible(not enabled)
        if enabled:
            self.showFullScreen()
        else:
            self.showNormal()

    def set_zoom(self, value: float) -> None:
        value = max(0.6, min(2.0, round(value, 1)))
        self.web_view.setZoomFactor(value)
        self.settings.setValue("browser/zoom", value)
        self.statusBar().showMessage(f"Zoom: {int(value * 100)}%", 2500)

    def _set_load_progress(self, value: int) -> None:
        self.load_progress.setValue(value)
        self.load_progress.setVisible(value < 100)

    def _load_finished(self, ok: bool) -> None:
        self.load_progress.setVisible(False)
        if ok:
            self.connection_badge.setText("LOCAL · READY")
        else:
            self.connection_badge.setText("PAGE ERROR")
            self.statusBar().showMessage("The page did not load. Use Reload to try again.", 8000)

    def _update_title(self, page_title: str) -> None:
        self.setWindowTitle(f"{page_title or APP_NAME} — {APP_NAME}")

    def _update_navigation_actions(self, _: QUrl) -> None:
        self.back_action.setEnabled(self.web_view.history().canGoBack())
        self.forward_action.setEnabled(self.web_view.history().canGoForward())

    def _open_path(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True) if not path.suffix else None
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))):
            QMessageBox.warning(self, APP_NAME, f"Windows could not open:\n{path}")

    def open_library_folder(self) -> None:
        self._open_path(Path(self.backend.BASE) if self.backend else application_root())

    def open_downloads_folder(self) -> None:
        target = Path(self.backend.DOWNLOADS) if self.backend else application_root() / "downloads"
        self._open_path(target)

    def open_log_folder(self) -> None:
        self._open_path(self.log_path.parent)

    def show_about(self) -> None:
        backend_version = getattr(self.backend, "APP_VERSION", GUI_VERSION)
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h2>{APP_NAME}</h2>"
            f"<p>Version {backend_version}</p>"
            "<p>A private, local-first video library manager with downloads, "
            "transcripts, reports, collections, search, and AI tools.</p>"
            "<p>The desktop interface is powered by PySide6. The application "
            "server listens only on your computer (127.0.0.1).</p>",
        )

    def _stop_server(self) -> None:
        if self.server is None:
            return
        server, self.server = self.server, None
        try:
            server.shutdown()
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
        try:
            server.server_close()
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._closing:
            event.accept()
            return
        if self.backend_thread and self.backend_thread.isRunning():
            QMessageBox.information(
                self,
                APP_NAME,
                "VideoHoarder is still starting. Please wait a moment, then close it again.",
            )
            event.ignore()
            return

        active = {"running": 0, "queued": 0}
        if self.backend:
            try:
                active = self.backend.web_queue_state()
            except Exception:
                print(traceback.format_exc(), file=sys.stderr)
        if int(active.get("running", 0)) or int(active.get("queued", 0)):
            answer = QMessageBox.question(
                self,
                "Work is still running",
                "Downloads or maintenance jobs are still active.\n\n"
                "Stop all work and exit VideoHoarder?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            try:
                self.backend.web_stop_everything()
            except Exception:
                print(traceback.format_exc(), file=sys.stderr)

        self._closing = True
        self.settings.setValue("window/geometry", self.saveGeometry())
        self.settings.setValue("window/state", self.saveState())
        self.settings.sync()
        self._stop_server()
        event.accept()


class MainWindow(QMainWindow):
    """Native command-centre shell with the mature local backend behind it."""

    LEGACY_ROUTES = {
        "library": ("Library", "/app?tab=library"),
        "oldimport": ("Old Library Import & Repair", "/oldimport"),
        "repairdata": ("Missing Data & AI", "/repairdata"),
        "chatgpt_processing": ("ChatGPT Processing", "/chatgpt-processing"),
        "knowledge": ("Knowledge & AI", "/knowledge"),
        "collections": ("Collections", "/app?tab=collections"),
    }

    def __init__(self, log_path: Path) -> None:
        super().__init__()
        self.log_path = log_path
        self.backend: Any | None = None
        self.server: Any | None = None
        self.base_url = ""
        self.backend_thread: QThread | None = None
        self.backend_worker: BackendWorker | None = None
        self._closing = False
        self._current_page = "dashboard"

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1120, 720)
        icon = QIcon(str(resource_path("assets/app_icon.svg")))
        if not icon.isNull():
            self.setWindowIcon(icon)
        self.settings = QSettings(ORGANIZATION_NAME, APP_NAME)

        self.profile = self._create_profile()
        self.web_view = QWebEngineView()
        self.web_page = SafeWebPage(self.profile, self.web_view)
        self.web_page.popup_requested.connect(self.handle_popup)
        self.web_view.setPage(self.web_page)

        self._build_actions()
        self.web_panel = self._build_web_panel()
        self._configure_web_view()

        self.sidebar = Sidebar()
        self.sidebar.set_ready(False)
        self.sidebar.page_requested.connect(self.show_page)
        self.loading_panel = LoadingPanel()
        self.error_panel = ErrorPanel()
        self.error_panel.retry_requested.connect(self.start_backend)
        self.error_panel.open_log_requested.connect(self.open_log_folder)
        self.command_center = CommandCenter()
        self.command_center.status_message.connect(self._show_status)
        self.command_center.open_folder_requested.connect(self.open_downloads_folder)
        self.workflows_page = WorkflowsPage()
        self.workflows_page.navigate_requested.connect(self.show_page)
        self.workflows_page.legacy_requested.connect(self.open_legacy)
        self.workflows_page.status_message.connect(self._show_status)
        self.settings_page = SettingsPage()
        self.settings_page.status_message.connect(self._show_status)
        self.settings_page.open_path_requested.connect(self.open_named_path)

        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")
        for widget in (
            self.loading_panel,
            self.error_panel,
            self.command_center,
            self.workflows_page,
            self.settings_page,
            self.web_panel,
        ):
            self.content_stack.addWidget(widget)

        shell = QWidget()
        shell.setObjectName("shellRoot")
        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        shell_layout.addWidget(self.sidebar)
        shell_layout.addWidget(self.content_stack, 1)
        self.setCentralWidget(shell)

        self.setStyleSheet(desktop_stylesheet())
        self.menuBar().hide()
        self.statusBar().hide()
        self._restore_window_state()
        self.content_stack.setCurrentWidget(self.loading_panel)
        QTimer.singleShot(0, self.start_backend)

    def _create_profile(self) -> QWebEngineProfile:
        storage = application_root() / "data" / "gui"
        cache = storage / "cache"
        storage.mkdir(parents=True, exist_ok=True)
        cache.mkdir(parents=True, exist_ok=True)
        profile = QWebEngineProfile(APP_NAME, self)
        profile.setPersistentStoragePath(str(storage))
        profile.setCachePath(str(cache))
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
        )
        profile.setHttpUserAgent(f"{profile.httpUserAgent()} {APP_NAME}/{GUI_VERSION}")
        profile.downloadRequested.connect(self.handle_download)
        return profile

    def _build_actions(self) -> None:
        style = self.style()
        self.back_action = QAction(
            style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack), "Back", self
        )
        self.back_action.setShortcut(QKeySequence.StandardKey.Back)
        self.back_action.triggered.connect(self.web_view.back)
        self.forward_action = QAction(
            style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward), "Forward", self
        )
        self.forward_action.setShortcut(QKeySequence.StandardKey.Forward)
        self.forward_action.triggered.connect(self.web_view.forward)
        self.reload_action = QAction(
            style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "Reload", self
        )
        self.reload_action.setShortcut(QKeySequence.StandardKey.Refresh)
        self.reload_action.triggered.connect(self.web_view.reload)
        self.fullscreen_action = QAction("Full Screen", self)
        self.fullscreen_action.setShortcut("F11")
        self.fullscreen_action.setCheckable(True)
        self.fullscreen_action.triggered.connect(self.set_fullscreen)
        self.dashboard_action = QAction("Dashboard", self)
        self.dashboard_action.setShortcut("Alt+Home")
        self.dashboard_action.triggered.connect(lambda: self.show_page("dashboard"))
        self.queue_action = QAction("Queue", self)
        self.queue_action.setShortcut("Ctrl+Shift+Q")
        self.queue_action.triggered.connect(lambda: self.show_page("queue"))
        self.more_action = QAction("Workflows", self)
        self.more_action.setShortcut("Ctrl+K")
        self.more_action.triggered.connect(lambda: self.show_page("more"))
        for action in (
            self.back_action,
            self.forward_action,
            self.reload_action,
            self.fullscreen_action,
            self.dashboard_action,
            self.queue_action,
            self.more_action,
        ):
            self.addAction(action)

    def _build_web_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("webPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("webHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 10, 16, 10)
        header_layout.setSpacing(8)
        for action in (self.back_action, self.forward_action, self.reload_action):
            button = QPushButton()
            button.setObjectName("secondaryButton")
            button.setIcon(action.icon())
            button.setToolTip(action.text())
            button.clicked.connect(action.trigger)
            button.setFixedSize(38, 34)
            header_layout.addWidget(button)
        self.web_title = QLabel("Library")
        self.web_title.setObjectName("webTitle")
        header_layout.addWidget(self.web_title)
        header_layout.addStretch()
        self.load_progress = QProgressBar()
        self.load_progress.setObjectName("loadProgress")
        self.load_progress.setTextVisible(False)
        self.load_progress.setFixedSize(100, 5)
        self.load_progress.hide()
        header_layout.addWidget(self.load_progress)
        self.connection_badge = QLabel("STARTING")
        self.connection_badge.setObjectName("connectionBadge")
        header_layout.addWidget(self.connection_badge)
        external = QPushButton("Open in browser")
        external.setObjectName("secondaryButton")
        external.clicked.connect(lambda: QDesktopServices.openUrl(self.web_view.url()))
        header_layout.addWidget(external)
        layout.addWidget(header)
        layout.addWidget(self.web_view, 1)
        return panel

    def _configure_web_view(self) -> None:
        page_settings = self.web_page.settings()
        page_settings.setAttribute(
            QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True
        )
        page_settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        page_settings.setAttribute(
            QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False
        )
        self.web_page.fullScreenRequested.connect(self.handle_fullscreen_request)
        self.web_view.loadStarted.connect(lambda: self.load_progress.setVisible(True))
        self.web_view.loadProgress.connect(self._set_load_progress)
        self.web_view.loadFinished.connect(self._load_finished)
        self.web_view.urlChanged.connect(self._update_navigation_actions)

    def _restore_window_state(self) -> None:
        geometry = self.settings.value("window/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1500, 900)
        zoom = float(self.settings.value("browser/zoom", 1.0))
        self.web_view.setZoomFactor(max(0.7, min(1.7, zoom)))

    @Slot()
    def start_backend(self) -> None:
        if self.backend_thread and self.backend_thread.isRunning():
            return
        self.content_stack.setCurrentWidget(self.loading_panel)
        self.sidebar.set_ready(False)
        self.connection_badge.setText("STARTING")
        thread = QThread(self)
        worker = BackendWorker()
        worker.moveToThread(thread)
        thread.started.connect(worker.start)
        worker.ready.connect(self.backend_ready)
        worker.failed.connect(self.backend_failed)
        worker.ready.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(self._backend_thread_finished)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.backend_thread = thread
        self.backend_worker = worker
        thread.start()

    @Slot()
    def _backend_thread_finished(self) -> None:
        self.backend_thread = None
        self.backend_worker = None

    @Slot(str, object, object)
    def backend_ready(self, base_url: str, server: Any, backend: Any) -> None:
        self.base_url = base_url.rstrip("/")
        self.server = server
        self.backend = backend
        self.connection_badge.setText("LOCAL · READY")
        self.connection_badge.setToolTip(
            f"Private local service\n{self.base_url}\nLibrary: {backend.BASE}"
        )
        self.sidebar.set_ready(True)
        self.command_center.set_backend(backend)
        self.workflows_page.set_backend(backend)
        self.settings_page.set_backend(backend)
        self.show_page("dashboard")
        self._show_status(f"Library ready · {backend.BASE}")

    @Slot(str)
    def backend_failed(self, trace: str) -> None:
        print(trace, file=sys.stderr)
        self.connection_badge.setText("START FAILED")
        self.error_panel.set_error(trace)
        self.content_stack.setCurrentWidget(self.error_panel)

    @Slot(str)
    def show_page(self, key: str) -> None:
        if not self.backend:
            return
        self._current_page = key
        self.sidebar.set_current(key)
        if key in {"dashboard", "queue"}:
            self.content_stack.setCurrentWidget(self.command_center)
            self.command_center.set_mode(key)
            return
        if key == "more":
            self.content_stack.setCurrentWidget(self.workflows_page)
            return
        if key == "settings":
            self.settings_page.refresh()
            self.content_stack.setCurrentWidget(self.settings_page)
            return
        title, route = self.LEGACY_ROUTES.get(key, ("VideoHoarder", "/app"))
        self.web_title.setText(title)
        self.content_stack.setCurrentWidget(self.web_panel)
        self.navigate(route)

    @Slot(str, str)
    def open_legacy(self, tab: str, command: str = "") -> None:
        labels = {
            "tools": "Advanced tools",
            "chatgpt": "ChatGPT processing",
            "intelligence": "Reports & export",
            "diagnostics": "Recovery center",
        }
        query = f"/app?tab={tab}"
        if command:
            query += f"&command={command}"
        self.web_title.setText(labels.get(tab, "VideoHoarder workflow"))
        self.content_stack.setCurrentWidget(self.web_panel)
        self.navigate(query)

    def navigate(self, path: str) -> None:
        if not self.base_url:
            return
        path = path if path.startswith("/") else f"/{path}"
        target = QUrl(f"{self.base_url}{path}")
        if self.web_view.url() == target:
            self.web_view.reload()
        else:
            self.web_view.setUrl(target)

    @Slot(QUrl)
    def handle_popup(self, url: QUrl) -> None:
        if not url.isValid() or url.scheme() == "about":
            return
        if url.host().lower() in LOCAL_HOSTS:
            self.content_stack.setCurrentWidget(self.web_panel)
            self.web_view.setUrl(url)
        else:
            QDesktopServices.openUrl(url)

    @Slot(object)
    def handle_download(self, download: Any) -> None:
        suggested = download.downloadFileName() or "download"
        default_dir = self.settings.value(
            "downloads/last_directory",
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation),
        )
        target, _ = QFileDialog.getSaveFileName(
            self, "Save Download", str(Path(str(default_dir)) / suggested)
        )
        if not target:
            download.cancel()
            return
        target_path = Path(target)
        self.settings.setValue("downloads/last_directory", str(target_path.parent))
        download.setDownloadDirectory(str(target_path.parent))
        download.setDownloadFileName(target_path.name)
        download.accept()
        self._show_status(f"Downloading {target_path.name}…")
        download.isFinishedChanged.connect(
            lambda: self._show_status(f"Saved: {target_path}")
        )

    @Slot(object)
    def handle_fullscreen_request(self, request: Any) -> None:
        request.accept()
        self.set_fullscreen(bool(request.toggleOn()))

    @Slot(bool)
    def set_fullscreen(self, enabled: bool) -> None:
        self.fullscreen_action.setChecked(enabled)
        if enabled:
            self.showFullScreen()
        else:
            self.showNormal()

    def _set_load_progress(self, value: int) -> None:
        self.load_progress.setValue(value)
        self.load_progress.setVisible(value < 100)

    def _load_finished(self, ok: bool) -> None:
        self.load_progress.hide()
        if not ok:
            self.connection_badge.setText("PAGE ERROR")
            self._show_status("This page did not load. Press Ctrl+R to try again.")
            return
        self.connection_badge.setText("LOCAL · READY")
        if self.web_view.url().path() == "/app":
            self.web_page.runJavaScript(self._legacy_theme_script())

    @staticmethod
    def _legacy_theme_script() -> str:
        """Make specialist legacy pages visually belong to the new shell."""

        return r"""
        (() => {
          if (document.getElementById('vlm-native-shell-theme')) return;
          const style = document.createElement('style');
          style.id = 'vlm-native-shell-theme';
          style.textContent = `
            :root{--bg:#0b1422!important;--panel:#111c2d!important;--text:#e8eef8!important;
              --muted:#91a0b7!important;--line:#2a394f!important;--blue:#277bf2!important;
              --shadow:none!important}
            html,body,.main{background:#0b1422!important;color:#e8eef8!important}
            .main{padding:18px!important}.header,.topnav{display:none!important}
            .card,.stat,.toolMini,.pathItem,.suggest,.flowStep,.fileitem,.coverBox{
              background:#111c2d!important;color:#e8eef8!important;border-color:#2a394f!important;box-shadow:none!important}
            input,textarea,select{background:#0e1928!important;color:#edf4ff!important;border-color:#43516a!important}
            th{background:#142136!important;color:#dfe7f2!important}td{color:#d9e2ef!important}
            .tablewrap{border-color:#2a394f!important}.muted,.explain{color:#91a0b7!important}
            .btn{background:#1c293d!important;color:#e8eef8!important;border-color:#354760!important}
            .btn.primary{background:#1768e8!important;color:#fff!important;border-color:#2c7af0!important}
            .btn.good{background:#153a2a!important;color:#77dea0!important;border-color:#2f6046!important}
            .btn.danger{background:#422128!important;color:#ff9aa7!important;border-color:#713541!important}
            pre{background:#07101d!important;border:1px solid #26364c!important}
          `;
          document.head.appendChild(style);
        })();
        """

    def _update_navigation_actions(self, _: QUrl) -> None:
        self.back_action.setEnabled(self.web_view.history().canGoBack())
        self.forward_action.setEnabled(self.web_view.history().canGoForward())

    def _show_status(self, message: str) -> None:
        text = str(message or "Ready")
        self.command_center.bottom_status.setText(text[:80])
        self.sidebar.status_text.setToolTip(text)

    def _open_path(self, path: Path) -> None:
        if not path.suffix:
            path.mkdir(parents=True, exist_ok=True)
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))):
            QMessageBox.warning(self, APP_NAME, f"Windows could not open:\n{path}")

    @Slot(str)
    def open_named_path(self, key: str) -> None:
        if not self.backend:
            return
        mapping = {
            "downloads": Path(self.backend.DOWNLOADS),
            "logs": Path(self.backend.LOGS),
            "config": Path(self.backend.CONFIG),
        }
        path = mapping.get(key)
        if path:
            self._open_path(path)

    def open_library_folder(self) -> None:
        self._open_path(Path(self.backend.BASE) if self.backend else application_root())

    def open_downloads_folder(self) -> None:
        target = Path(self.backend.DOWNLOADS) if self.backend else application_root() / "downloads"
        self._open_path(target)

    def open_log_folder(self) -> None:
        self._open_path(self.log_path.parent)

    def _stop_server(self) -> None:
        if self.server is None:
            return
        server, self.server = self.server, None
        try:
            server.shutdown()
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
        try:
            server.server_close()
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._closing:
            event.accept()
            return
        if self.backend_thread and self.backend_thread.isRunning():
            QMessageBox.information(
                self, APP_NAME, "VideoHoarder is still starting. Please wait a moment."
            )
            event.ignore()
            return
        active = {"running": 0, "queued": 0}
        if self.backend:
            try:
                active = self.backend.web_queue_state()
            except Exception:
                print(traceback.format_exc(), file=sys.stderr)
        if _number := int(active.get("running", 0) or 0) + int(active.get("queued", 0) or 0):
            answer = QMessageBox.question(
                self,
                "Work is still running",
                f"{_number} running or queued job(s) remain.\n\nStop all work and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            try:
                self.backend.web_stop_everything()
            except Exception:
                print(traceback.format_exc(), file=sys.stderr)
        self._closing = True
        self.settings.setValue("window/geometry", self.saveGeometry())
        self.settings.setValue("browser/zoom", self.web_view.zoomFactor())
        self.settings.sync()
        self._stop_server()
        event.accept()


def install_exception_hook(log_path: Path) -> None:
    def handle(exc_type: type[BaseException], exc: BaseException, tb: Any) -> None:
        details = "".join(traceback.format_exception(exc_type, exc, tb))
        print(details, file=sys.stderr)
        app = QApplication.instance()
        if app:
            QMessageBox.critical(
                None,
                f"{APP_NAME} Error",
                f"An unexpected error occurred:\n\n{exc}\n\n"
                f"Details were saved to:\n{log_path}",
            )

    sys.excepthook = handle


def set_windows_app_id() -> None:
    if os.name != "nt":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            f"VideoHoarder.Desktop.{GUI_VERSION}"
        )
    except Exception:
        pass

def acquire_single_instance() -> bool:
    """Prevent duplicate desktop backends and conflicting job queues on Windows."""
    global _SINGLE_INSTANCE_MUTEX
    if os.name != "nt":
        return True
    try:
        import ctypes
        _SINGLE_INSTANCE_MUTEX = ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\VideoHoarder.Desktop.SingleInstance")
        return ctypes.windll.kernel32.GetLastError() != 183
    except Exception:
        return True


def main() -> int:
    set_windows_app_id()
    if not acquire_single_instance():
        return 0
    log_path = install_file_logging()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setApplicationVersion(GUI_VERSION)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setQuitOnLastWindowClosed(True)
    icon = QIcon(str(resource_path("assets/app_icon.svg")))
    if not icon.isNull():
        app.setWindowIcon(icon)
    install_exception_hook(log_path)
    window = MainWindow(log_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
