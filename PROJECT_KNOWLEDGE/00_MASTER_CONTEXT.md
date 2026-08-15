# Master Context

VideoHoarder is a Windows-first local desktop application for collecting, organizing, enriching, reviewing, and searching video-library content. It combines a PySide6 desktop shell, an embedded/local HTTP workspace, SQLite persistence, command/job workflows, YouTube tooling, transcript/report generation, local Ollama integration, and manual ChatGPT package exchange.

Source reviewed: `C:\Users\gaurav.bansal\Documents\ChatGPT\VideoHoarder`.
Installed runtime reviewed: `D:\YT GUi\VideoHoarder.exe`.

The implementation is dominated by `app/app.py` (approximately 22,199 lines), with desktop shells in `app/gui.py` and `app/native_ui.py`. The code exposes many workflows but the checked source database contains zero rows in all ten application tables, so live-library behavior was not validated from this source copy.

Safety posture: ChatGPT exchange is manual; duplicate and clip results are reviewed/handoff records; destructive deletion exists elsewhere and must be explicitly invoked. A plaintext `D:\YT GUi\api_key.txt` exists and must never be included in reports or handoff packages.
