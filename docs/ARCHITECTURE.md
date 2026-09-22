# Architecture

VideoHoarder is being incrementally modularized rather than rewritten. The large legacy `app/app.py` remains the compatibility/orchestration layer while focused services own new logic.

## Major boundaries

```text
Native UI / embedded web views
          |
          v
managed jobs + thin app.py orchestration
          |
   +------+------------------+-------------------+
   |                         |                   |
   v                         v                   v
download/source        metadata/library     transcript/evidence
services                persistence          services
   |                         |                   |
   +-------------------------+-------------------+
                             |
                             v
                  Video Intelligence package
                             |
              +--------------+--------------+
              |                             |
              v                             v
        manual exchange             OpenAI API provider
                                            |
                                            v
                                  one VIDEO_ID per call
              |                             |
              +--------------+--------------+
                             v
                  deterministic importer
                             |
                             v
                       manual review
                             |
                             v
                    explicit apply tools
```

## Provider boundary

`app/openai_api_service.py` owns OpenAI-specific transport/request/response behavior. Provider code must not acquire transcripts, write library metadata, rename/move files, or apply semantic output.

The normal package contract is built first. This makes manual and API processing consume the same evidence/validation model and prevents a provider from becoming a second source of truth.

## Incremental modularization rule

When changing an existing feature:

1. identify the current authoritative implementation;
2. add/repair tests around behavior;
3. extract cohesive logic behind a small interface;
4. keep compatibility wrappers where needed;
5. remove duplicate/dead paths only after evidence shows callers migrated.

Avoid a big-bang rewrite of `app.py`; it would create unnecessary regression risk across persistence, files, jobs, and UI behavior.
