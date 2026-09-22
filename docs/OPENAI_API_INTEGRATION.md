# Optional OpenAI API integration

VideoHoarder supports two semantic-processing paths:

1. **Manual exchange** — create a self-contained package, process it manually, then import returned JSON.
2. **OpenAI Responses API** — explicitly submit an existing/new Video Intelligence package from the ChatGPT Processing page.

The API path is optional. Core download/library/transcript functionality does not depend on it.

## Data flow

```text
canonical transcript + allowed metadata
              |
              v
      CHATGPT_PACKAGE.json
              |
       one VIDEO_ID only
              |
              v
     OpenAI Responses API
              |
              v
 OPENAI_API_RESULT_<package>.json
              |
              v
existing VideoHoarder importer/validator
              |
              v
       manual review queue
              |
        explicit apply only
```

## Evidence boundary

The normal package builder is allow-list driven. It permits identity/operational metadata, source chapters/tags, transcript provenance, deterministic transcript-health context, and canonical transcript evidence. It forbids descriptions, viewer comments, raw formats/caption inventories, counts, local filesystem details, credentials, cookies, and other unrelated fields.

The API provider sends **one complete video package at a time**, in package order. It does not send the other videos in that package in the same model call.

## API key

The key itself is never part of `config.json` or a VideoHoarder report. The setting `openai_api_key_env` stores only the name of an environment variable. Default:

```text
OPENAI_API_KEY
```

Example for the current PowerShell process:

```powershell
$env:OPENAI_API_KEY = "your-key-here"
```

Do not commit a key, paste it into an issue, place it in ChatGPT packages, or add it to screenshots/logs.

## Configuration

Defaults are in `app/config.default.json`:

```json
{
  "openai_api_enabled": false,
  "openai_model": "gpt-5.6",
  "openai_reasoning_effort": "high",
  "openai_timeout_seconds": 900,
  "openai_max_retries": 2,
  "openai_max_output_tokens": 32000,
  "openai_api_key_env": "OPENAI_API_KEY",
  "openai_store_responses": false,
  "openai_structured_outputs": true,
  "openai_allow_restricted_videos": false
}
```

The model is configurable because availability and recommended models can change over time.

## Restricted/private videos

If package metadata marks a video private, unlisted, members-only, subscriber-only, premium-only, login-required, or authentication-required, the provider skips it by default. `openai_allow_restricted_videos` must be explicitly enabled before such a video can be sent. Only enable it when you have authorization and understand that evidence leaves the local machine.

## Structured output and validation

VideoHoarder passes the package's formal result schema to the Responses API as Structured Outputs when enabled. Some historical schemas may contain JSON-Schema features a provider rejects. In that case the provider retries that video once in JSON-object mode.

This fallback does **not** bypass VideoHoarder validation. The returned result still goes through the same importer used by the manual workflow, including package ID, expected VIDEO_ID, schema version, evidence references/segment IDs, feature coverage, timestamps, placeholders, package integrity, and review-state checks.

## Files written beside a processed package

- `OPENAI_API_RESULT_<package_id>.json` — merged package-level result.
- `OPENAI_API_RUN.json` — sanitized provider audit: model, response IDs, timings, token usage, failures, and privacy settings.

Neither file contains the API key.

## Failure behavior

- Videos are processed sequentially.
- A failed video is recorded and later videos continue.
- A partial merged result can still be imported; missing VIDEO_IDs become reprocessing/review items.
- If every video fails, the app stops before import and points the maintainer to the provider audit.
- No result is automatically applied to library files/metadata.

## Maintainer design rule

Keep provider code in `app/openai_api_service.py`. Do not move API transport, credentials, or provider-specific request construction back into `app.py`. `app.py` should remain orchestration/compatibility glue while the repository is incrementally modularized.

## OpenAI references

- Responses API create/reference: https://developers.openai.com/api/reference/python/resources/responses/methods/create
- Structured Outputs: https://developers.openai.com/api/docs/guides/structured-outputs
- GPT-5.6 Sol model: https://developers.openai.com/api/docs/models/gpt-5.6-sol

VideoHoarder intentionally keeps the model configurable because model availability, pricing, and recommended settings can change independently of the application release.

## Imported local videos

A local `platform=local` record does not need a YouTube ID or URL. It enters the existing transcript package flow **only after usable local transcript evidence is present**. Importing files does not start OpenAI/ASR or download YouTube captions; the API remains disabled by default and requires explicit submission. Review locally recorded/private transcript evidence before any cloud submission. See [LOCAL_VIDEO_IMPORT.md](LOCAL_VIDEO_IMPORT.md).
