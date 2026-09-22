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

## Tag-driven GitHub Release

After the human acceptance checks are complete, create a tag that exactly matches the base application version. For example, `app/VERSION.txt = 33.2-GUI` requires tag `v33.2`.

Pushing that tag starts `.github/workflows/release.yml`. The release workflow:

1. reuses the validated Windows build workflow;
2. requires the full privacy/test/PyInstaller/frozen-self-test gates;
3. rejects a tag that does not match `app/VERSION.txt`;
4. downloads the validated Windows build artifact;
5. generates `SHA256SUMS.txt`; and
6. creates the GitHub Release with generated release notes.

Example after all release checks pass:

```powershell
git tag v33.2
git push origin v33.2
```

Do not move or recreate an already published release tag. Prepare a new version instead.
