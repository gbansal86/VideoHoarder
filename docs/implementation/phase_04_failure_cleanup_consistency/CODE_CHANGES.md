# Code Changes

## Post-validation correction — frozen prompt + handoff build scripts
- Modified `VideoHoarder.spec` to bundle `app/prompts/VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md`.
- Modified `scripts/create_code_parent_package.py` to preserve `BUILD_DEV_LAUNCHER.ps1`, `BUILD_DEV_LAUNCHER.bat`, and `CREATE_CODE_PARENT_PACKAGE.bat`.
- Extended release/package contract tests so these omissions fail automatically in future.
