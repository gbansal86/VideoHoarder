# VideoHoarder Recovery Checkpoints

Before every implementation pass:

1. Record the current source/build state in a dated checkpoint file.
2. Record what is implemented, pending, and being changed.
3. Run compile/tests after the change.
4. Update `VideoHoarder_Feature_Status_Current.md` and `VideoHoarder_Implementation_Changelog.md`.
5. Keep the checkpoint with the matching status documents so a failed build can be recovered or rolled back safely.

Checkpoints are documentation/state records only. They never contain API keys, cookies, private media, transcripts, or ChatGPT result contents.
