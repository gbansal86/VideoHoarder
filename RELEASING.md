# Releasing VideoHoarder

A release should be reproducible from a clean public source commit.

## Checklist

1. Update `app/VERSION.txt`, `APP_VERSION`, native GUI version, Windows version metadata, changelog, and build archive names.
2. Confirm no runtime databases, logs, downloads, browser profiles, API keys, cookies, `.env` files, or generated package/result data are staged.
3. Run:

   ```powershell
   python -m compileall -q app tests build_support
   python -m pytest -q
   ```

4. Build on Windows:

   ```powershell
   .\BUILD_WINDOWS.ps1
   ```

5. Start the packaged app and verify dashboard/native UI startup plus one non-destructive workflow.
6. Record SHA-256 for the release archive/executable.
7. Review `SECURITY.md`, dependency alerts, and provider/privacy changes.
8. Tag the clean commit and publish release notes from `CHANGELOG.md`.

## API-provider release rule

Never perform a live provider test with a maintainer's real key in CI. Mock/fake clients cover automated tests. If a live smoke test is performed privately, use a dedicated low-privilege development key, a synthetic transcript fixture, and do not publish the request/response if it contains sensitive data.
