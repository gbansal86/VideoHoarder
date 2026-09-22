# Synthetic local-video example

This directory contains **fully synthetic** subtitle/metadata examples for learning and contributor testing. It contains no private media, downloaded video, API output, or real platform identifier.

## Try the local import workflow safely

1. Copy or create a short video you are authorized to use.
2. Rename that file to `demo_video.mp4`.
3. Copy `demo_video.srt` from this directory beside the video.
4. Optionally keep `demo_video.metadata.json` nearby for your own inspection; it is illustrative documentation and is not required by the importer.
5. Open **Import Local Videos**.
6. Add the folder containing `demo_video.mp4`.
7. Choose **Scan / Preview**.
8. Use **Leave in place** for the safest first test.
9. Import the video and confirm that the adjacent subtitle is associated with the local record.

Do not commit the actual `demo_video.mp4` you used for testing.

## What this demonstrates

- local-video import does not require a YouTube ID;
- adjacent subtitle evidence can be associated locally;
- importing a file does not automatically call OpenAI or another cloud provider;
- the media can remain in its original location.

For the full behavior contract, see [docs/LOCAL_VIDEO_IMPORT.md](../../docs/LOCAL_VIDEO_IMPORT.md).
