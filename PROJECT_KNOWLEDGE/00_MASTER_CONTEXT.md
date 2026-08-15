# Master Context

Recorded: 2026-08-15

VideoHoarder is a Windows-first local desktop application for collecting, organizing, enriching, reviewing and searching a personal video library. It combines PySide6 native surfaces, an embedded loopback HTTP workspace, SQLite, filesystem artifacts, jobs, YouTube/transcript tooling, reports/indexes, local Ollama and manual ChatGPT exchange.

Source: `C:\Users\gaurav.bansal\Documents\ChatGPT\VideoHoarder`. Installed runtime: `D:\YT GUi\VideoHoarder.exe`. Git: private `https://github.com/gbansal86/VideoHoarder.git`, branch `main`.

`app/app.py` is approximately 25,052 physical lines and owns most backend/UI/integration behavior. `app/gui.py` and `app/native_ui.py` provide desktop shells. The audited SQLite database has zero rows in all ten application tables, so schema is verified but live-library behavior is generally UNKNOWN.

Safety: ChatGPT exchange is manual; imported data requires validation/review; duplicate and clip review do not make physical changes; separate destructive tools require explicit use. Plaintext `D:\YT GUi\api_key.txt` exists and must never enter Git, reports or handoffs.
