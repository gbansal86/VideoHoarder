# Public GitHub release: source only

This source distribution is intended for **public cloning and contribution**. You do **not** need to provide an OpenAI key to build the application or use its local/manual workflows. The OpenAI transcript API option is disabled by default and can be enabled later, at the user's expense, using their own `OPENAI_API_KEY` process environment variable. **Never commit API keys to source, sample config, logs, issues, screenshots, or release artifacts.** ChatGPT subscriptions and OpenAI API billing/credits are separate.

## Before first public push

1. Extract the sanitized archive; publish **only the contents of its `Source/` directory**, not the parent ZIP, local VideoHoarder application root, or any `exchange/` folders.
2. Examine the source and license provenance of all files, third-party models/assets, screenshots, and sample transcript content. The source sanitizer is not a copyright/license review.
3. Run `python scripts/public_release_audit.py .` **before the tests** from a pristine or staged `Source/` tree, then run `python -m pytest -q`. Tests may generate temporary SQLite/cache files locally; if you run the audit again afterward, run it against a fresh sanitized staging tree. Resolve genuine findings; do not silence or bypass failures.
4. Confirm `app/config.default.json` and `app/config.example.json` have `openai_api_enabled=false`, `openai_store_responses=false`, `openai_allow_restricted_videos=false`, and no key value.
5. Run `git status --short` and `git ls-files` in the *destination repository* before committing. Do not add `exchange/`, media, generated reports, browser profiles, downloaded subtitles, session files, databases, or executable/build caches.
6. Inspect the **existing GitHub repository history separately**. This archive cannot sanitize previous commits or already-public exchange packages. If private data/credentials were pushed previously, remove the affected public content/history using an appropriate documented process and rotate any exposed credentials. A new clean commit does not erase old Git objects.
7. Run the Windows full test suite and create a Windows `.exe` only after Windows smoke/build tests pass. No Windows binary is included here.

## User API setup (optional)

- API support uses `app/openai_api_service.py`, the existing ChatGPT Processing UI, and the normal importer/review gate; it is **off** for every fresh installation.
- Users who want it can install the `openai` Python dependency and supply `OPENAI_API_KEY` in their own environment, enable the provider in Settings → Knowledge & AI, and explicitly submit selected eligible transcripts.
- The provider sends a transcript to an external service only upon an explicit processing action. Users should review privacy, cost, consent, copyright, and data-transfer implications. Restricted videos remain blocked by default.
- **Do not set up the maintainer's API key or billing account for public users.**

## Known boundaries

This release audit detects common secret formats, local-machine paths, and runtime file types in the *new package*. It is not a complete security/privacy audit and does not scan old GitHub history. `specs/evidence/` (historical real-video evidence) is omitted from the public source package; deterministic synthetic test fixtures are retained. The application's separate public GitHub exchange feature can publish transcripts/comments if the user explicitly chooses it: treat it as a separate public-data disclosure, and review its payload before use.
