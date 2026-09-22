# Code Changes

- Equal-size archive collisions are hash-compared; different content is preserved under unique conflict names.
- Phase-2 legacy ChatGPT storage migration uses content equality and unique legacy names.
- Lookalike hosts such as `wyoutube.com` no longer enter YouTube-specific/browser-cookie fallback paths.
- Reserved Windows names are normalized even when the stem has trailing spaces before an extension.
- Native Settings no longer offers `audio` as video quality; Audio Only remains a workflow.
- Code Parent config.example is generated from authoritative defaults, not live config.json.
