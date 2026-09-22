# Test Plan

1. Reproduce equal-size/different-content collisions in both transcript archive functions and Phase-2 migration.
2. Reject YouTube lookalike hosts while retaining real watch/live/short/youtu.be hosts.
3. Check reserved Windows-name variants.
4. Check Native Settings source contract and portable OAuth help.
5. Regenerate config.example from a source root with no config.json.
6. Run complete pytest + compileall.
7. Generate Code Parent twice; compare bytes and content; extract retained ZIP and rerun complete pytest.
