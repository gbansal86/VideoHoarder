# Performance

Status: NEEDS REVIEW.

Potential risks include repeated full-library scans, large monolithic imports/startup, filesystem hashing, large HTML generation, synchronous external calls, and browser-profile/build footprint. The manifest proposal correctly targets incremental checks, but no large-library benchmark was run.
