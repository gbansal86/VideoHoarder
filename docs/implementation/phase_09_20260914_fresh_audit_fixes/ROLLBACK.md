# Rollback

This handoff has no `.git`, so no fabricated commit/tag is recorded. Rollback is file-based:
1. Restore the previous Code Parent snapshot.
2. Do not roll back or overwrite user databases/media/config when restoring source.
3. If config recovery created `config.corrupt_*.json`, retain it for manual recovery.
4. Re-run the prior full test suite after source rollback.
