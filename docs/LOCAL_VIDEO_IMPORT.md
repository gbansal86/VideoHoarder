# Import videos already on a hard drive

VideoHoarder v33.2 adds a **separate Import Local Videos** workflow. It does not depend on YouTube accounts, URLs, or an OpenAI API key. Do not use the older **Old Library Import & Repair** workflow for unrelated local videos: that workflow is intended for existing VideoHoarder/YouTube-based folder structures.

## Step-by-step on Windows

1. Open VideoHoarder and select **Import Local Videos** in the left sidebar. In the embedded dashboard, visit `/import-local`, or follow the link from **Old Library Import & Repair**.
2. Paste the absolute path to a folder, an individual video, or multiple paths (one complete path per line). Spaces are supported. Example paths: `D:\Videos` and `E:\Courses\Lesson 1.mp4` (replace with your own paths).
3. Click **Scan / Preview**. This enumerates supported videos without changing their source files. Large collections should be scanned in smaller folders if the 10,000-file safety cap is reached.
4. Select one storage mode: **Leave in place** (default; only SQLite registration), **Copy** (creates an independent managed copy), or **Move** (requires a separate confirmation and relocates the original video). The importer never overwrites an existing managed destination.
5. Click **Import Selected Videos** and review the job's result. Re-importing the same source path skips its existing record rather than creating duplicate rows.
6. Open **Library** and search by filename/title. Imported videos receive stable `local_...` IDs and `platform=local`. Playback uses VideoHoarder's existing local `/media/<id>` video endpoint.

Supported input extensions: `.mp4`, `.mkv`, `.webm`, `.mov`, `.m4v`, `.avi`, `.wmv`, `.flv`, `.mpg`, `.mpeg`, `.ts`, `.mts`, `.m2ts`, `.3gp`, and `.ogv`. Files with no content and filesystem symlinks are skipped. Metadata duration/dimensions are discovered if FFprobe is on the PATH; it is not mandatory.

## Subtitles, transcripts, and AI

The importer detects a sibling `.srt` or `.vtt` using the same video filename stem, including `.en.srt/.en.vtt`, and recognizes adjacent `.transcript.txt`/`.transcript_timestamped.txt`/`.timestamped.txt` files. Existing caption or transcript text is converted or copied to the app's **local transcript cache**, while the source subtitle/transcript file is left unchanged. It does **not** send any video, transcript, metadata, or API request to external services when importing.

To use ChatGPT Processing, select the imported local video's `local_...` ID and create an intelligence package **only after** suitable transcript evidence is present and passes the existing transcript-health gate. Optional OpenAI Responses API submission is a separate explicit action that requires a user's own key and enabled setting. VideoHoarder will not fetch captions from YouTube for `platform=local` entries. **Automatic speech-to-text for videos without a sidecar is not part of this importer yet**; add/prepare a transcript separately before requesting transcript intelligence.

Note: processing a locally recorded/private video using an external AI provider is a privacy-sensitive choice. Review the allowed package evidence before explicitly sending it.

## Important safety/compatibility limits

- **Reference mode never edits or renames the source video.** If you delete the original file or disconnect the drive, VideoHoarder marks the record unavailable instead of purging your other local videos.
- The local ID is derived from the *original absolute source path*. It is stable across repeat imports of that path; changing the original path may require re-registering the video. Copy/move modes retain the original ID for the managed copy.
- Copy/move operate on **video files only**, not on an entire source folder. Existing sidecars remain where they were, with their paths recorded in SQLite and derived transcript text stored inside VideoHoarder's app data.
- A moved video cannot always be returned to its original drive if that drive becomes unavailable or a system failure occurs; **leave in place** or **copy** is safer for irreplaceable files.
- Some existing YouTube-only repair, metadata refresh, and download actions are not appropriate for `platform=local` records. Do not run YouTube recovery commands on arbitrary local imports.
- The desktop `.exe` must be built/tested on Windows. This source release has automated Linux-safe contract tests; real drive permissions, physical drives, and FFprobe extraction should also be checked on Windows before creating a binary release.
