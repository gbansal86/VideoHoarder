# Architecture Notes — Phase 02

1. **Single duplicate decision boundary.** Library/deletion history and current queue identity are merged by the canonical backend check. Native UI may still provide early UX confirmation, but server-side job start remains authoritative.
2. **Video metrics are not job metrics.** Dashboard Completed Today is computed from canonical video rows plus physical media verification.
3. **Maintenance refresh is independent of the managed download queue.** Diagnostics/figure refresh must still work while downloads are paused.
4. **Refresh coalescing is lossless.** A refresh already in progress sets a pending flag; completion records only the in-flight target and schedules another read if newer state arrived.
5. **Queue page owns full session visibility.** Compact Dashboard keeps legacy snapshot behavior; dedicated Queue requests an unlimited session snapshot.
6. **Monolith discipline.** New decision logic was added to existing modular services. `app.py` changes are limited to compatibility/wiring, HTTP boundary checks, and the existing download persistence statement.
