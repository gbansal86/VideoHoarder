# Architecture Notes

- Content equality is centralized through `file_safety.files_equal`; collision names use `unique_conflict_path`.
- URL classification is centralized in `youtube_url.is_youtube_url` and shared by cookie fallback policy.
- `config.default.json` is the packaging schema authority; package generation never depends on live config creation.
- Native UI keeps Audio Only as a workflow, not a video-quality default.
