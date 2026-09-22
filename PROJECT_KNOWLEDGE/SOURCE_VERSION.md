# Source Version

Recorded: 2026-08-15

Working-source update: 2026-09-22 (Codex-for-OSS/OpenAI API + repository hardening milestone; extracted source without accessible `.git` metadata)

Current local Git baseline: `b6b8123e7ee0e330e3edefc5d32d46fbb94b406e`

Independent child-control implementation commit: `20faa9135415485e8f13770178120b6fa8178de9`

Five-video acceptance and scheduler-parity commit: `c736b39ea30f0c93d59d68e14138915aff4f6bee`

Optional report-validation correction: `62db6dd7d6a6fbc9291131f78d679dbbef76abdb`

- Application version: `33.2-GUI`
- Repository: `https://github.com/gbansal86/VideoHoarder.git`
- Branch: `main`
- Initial source commit: `643c1f2e4ea4e6e090e8e06286b33c588cc67bdc`
- Living knowledge completion commit: `5c66fe1b67206a50e80082dc0a039cecfa11df3d`
- Full knowledge reconciliation commit: `f8e209bf65bc4f56e3c9618180cf40dfbcd68928`
- Independent-validation input baseline: `f74650adbfc04b26386835cab05fd71109611e2b`
- `app/app.py` SHA-256: `C7C9CDBD1C675338EDB9363AF36E4B29D3BEFB22D2858AB3041FDA0464A9B2EE`
- `app/gui.py` SHA-256: `A48169D098DE70B0E1D1606718C01312FBB80CDCB179B54BE9011541A6753491`
- `app/native_ui.py` SHA-256: `9D607CAC3E9B629FC6F88624CC2AD921E4E65F4C94EC1D2BCBABDCF039D22915`
- `requirements.txt` SHA-256: `3361D7A03D436A537A759CEE0E2E27EF215CDE3582099483E3D1A67A3A6AF63D`
- Local/installed EXE SHA-256: `698B33DA474BE36F49B495DEB74D474A66066E4EF516C4853099EBAC1E3107CC`
- EXE size: 218,124,389 bytes

Current working-source fingerprints after the concurrency milestone:

- `app/app.py` SHA-256: `C7C9CDBD1C675338EDB9363AF36E4B29D3BEFB22D2858AB3041FDA0464A9B2EE`
- `app/native_ui.py` SHA-256: `9D607CAC3E9B629FC6F88624CC2AD921E4E65F4C94EC1D2BCBABDCF039D22915`
- `app/native_queue_page.py` SHA-256: `E8EA68C3EA3A88DD5ED0E8EF64D745FFB4452F9A800455BDDDB1CDAB6019E2E5`
- The application version remains `33.0-GUI`; no binary was built for this source-only milestone.

Current working-source fingerprints after independent child-job controls (2026-09-20):

- `app/app.py` SHA-256: `C7C9CDBD1C675338EDB9363AF36E4B29D3BEFB22D2858AB3041FDA0464A9B2EE`
- `app/native_ui.py` SHA-256: `9D607CAC3E9B629FC6F88624CC2AD921E4E65F4C94EC1D2BCBABDCF039D22915`
- `app/job_persistence_service.py` SHA-256: `2283757BBE0D59960E1B61B47EFCBB241C63E43D4A3CA172C985A4FC4FD39B77`
- The application version remains `33.0-GUI`; no binary was built.

Post five-video acceptance/final child-path fingerprint (2026-09-20):

- `app/app.py` SHA-256: `C7C9CDBD1C675338EDB9363AF36E4B29D3BEFB22D2858AB3041FDA0464A9B2EE`
- The application version remains `33.0-GUI`; no binary was built.

The EXE hash proves the installed and local distribution copies are identical. It does not independently prove that the current source tree exactly produced that historical binary.


## 2026-09-22 API/OSS source milestone

- Added optional OpenAI Responses API provider in `app/openai_api_service.py`.
- Added one-video-per-call isolation, restricted-video privacy gate, secret-free audit, Structured Outputs + JSON fallback, and existing-importer review integration.
- Added native/web provider controls without storing API-key values.
- Added OpenAI provider unit/integration tests.
- Added OSS repository files, CI, CodeQL, Dependabot and public API/security documentation.
- Removed runtime SQLite database from the source package.
- Version bumped to `33.1-GUI`; no executable was built in this source review environment.

Final 33.1 source validation: **341 passed, 22 skipped, 0 failed**. No Windows binary was built in this review environment.

Final 33.1 key fingerprints:

- `app/app.py` SHA-256: `C7C9CDBD1C675338EDB9363AF36E4B29D3BEFB22D2858AB3041FDA0464A9B2EE`
- `app/native_ui.py` SHA-256: `9D607CAC3E9B629FC6F88624CC2AD921E4E65F4C94EC1D2BCBABDCF039D22915`
- `app/openai_api_service.py` SHA-256: `8EEEE358631ED33611DBC0AFFFACAF9E592D0363710B5D8B7A52EF1E0EB823A5`
- `app/settings_service.py` SHA-256: `992A057FBE6414A5EABE606C30E326EC5098121329CFBDEFFA4A6EC3C3468AD7`
- `scripts/create_code_parent_package.py` SHA-256: `0589FA21D9D559E74B7F19F27F453C8E74346594D6C1D4C22018B9A748181D8D`
- `requirements.txt` SHA-256: `3361D7A03D436A537A759CEE0E2E27EF215CDE3582099483E3D1A67A3A6AF63D`



## 2026-09-22 v33.2 local-video/publication milestone

- Added the dedicated Import Local Videos workflow, stable local IDs, reference/copy/confirmed-move modes, adjacent subtitle/transcript association, and local playback integration.
- Added beginner quick-start documentation and annotated SVG walkthroughs for installation, local import, transcript intelligence, and public-repository safety.
- Current source version: `33.2-GUI`.
- Final source validation before GitHub publication: **354 passed, 22 skipped, 0 failed**.
- No v33.2 Windows binary was built in this Linux review environment; publish source first and build the binary on Windows.
