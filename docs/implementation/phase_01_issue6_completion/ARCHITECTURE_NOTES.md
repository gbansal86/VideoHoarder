# Architecture Notes

The user explicitly requested new features outside `app.py`. This phase adds three modules and reduces `app.py` from 28,894 to 28,876 lines. The native Queue page is separate from Dashboard but reuses the existing QueueTable/JobDetails presentation components to avoid duplicate queue rendering logic. Duplicate-download rules are pure-service logic usable by both native and web surfaces.
