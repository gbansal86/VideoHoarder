# Architecture Notes

- `media_only_service.py` owns non-empty media validation and VTT→SRT materialization helpers.
- `job_persistence_service.py` owns JSON-safe durable queue snapshots and restart transformation to `INTERRUPTED`.
- Queue persistence is throttled for progress writes and forced for state transitions.
- Task retry descriptors are not persisted when nested mapping keys look sensitive (`password`, `secret`, `token`, `cookie`, `authorization`, `api_key`).
- Native Library uses `FunctionTask`/`QThreadPool`; stale async responses are rejected by a serial number.
- MainWindow attaches Queue first and isolates each page's `set_backend()` boundary.
- Frozen self-test uses an isolated library root and now exercises the local server + native Queue contract.
