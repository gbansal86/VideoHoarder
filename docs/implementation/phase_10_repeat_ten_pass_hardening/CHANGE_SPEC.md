# Phase 10 Change Specification — Repeat 10-Pass Hardening

Change size: MEDIUM follow-up hardening on the governed Phase-09 source.

## Requirements
- FIX-105: residual transcript/archive and Phase-2 legacy merges must never use equal size as duplicate proof.
- SEC-106: YouTube classification/cookie fallback must require an actual YouTube host, not lookalike domains.
- FIX-107: Windows reserved names remain escaped even with spaces before extensions.
- FIX-108: Native Settings must not advertise an unsupported audio value as a video-quality default and privacy text must match the safe default.
- FIX-109: OAuth/dependency guidance must be portable and must not promise unverified tool installation.
- GOV-110: a pristine Code Parent must regenerate a complete config.example schema without first creating config.json.
- DOC-111: governance/final validation must match this exact source state.

## Acceptance
Targeted regressions pass, complete pytest is green except platform-native skips, compileall passes, two generated Code Parent archives are byte-identical, and the extracted retained package reruns the complete suite.
