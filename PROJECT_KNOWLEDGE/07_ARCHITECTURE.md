# Architecture

Windows PySide6 shell -> embedded local HTTP workspace -> monolithic Python application services -> SQLite and filesystem artifacts -> external tools/services (yt-dlp/ffmpeg-like dependencies, YouTube, transcript API, Ollama, browser/Selenium) -> manual ChatGPT exchange.

Primary architectural risk: UI markup, API routing, domain logic, persistence, filesystem mutation, subprocess orchestration, and external integrations share one module. Recommended direction is characterization-first extraction into database, artifact, package, download, transcript, report, HTTP, and job modules while preserving existing public behavior.
