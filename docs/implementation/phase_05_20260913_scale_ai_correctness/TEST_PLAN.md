# Phase 05 Test Plan

1. Page a synthetic 12,050-video SQLite library beyond the historical 10,000 cap and verify authoritative total/max page.
2. Load >999 search-score candidates through the SQLite TEMP relation and verify no parameter-limit truncation.
3. Verify the native Library calls `web_library_page`, stores a server total, and fetches each page on navigation.
4. Seed a legacy source-hash-matching embedding vector from the wrong backend and prove it is rebuilt.
5. Verify embedding identity changes by backend/model/dimension and semantic similarity accepts only matching identities.
6. Correct evidence text while keeping the same chunk ID and prove Local AI does not return the old cached answer.
7. Verify generation-setting changes alter answer-cache identity.
8. Run the complete cumulative pytest suite, audit implementation markers, then run the complete suite a second time before Phase 06.
