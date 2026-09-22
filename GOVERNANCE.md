# Governance

VideoHoarder currently uses a maintainer-led model.

- Maintainers set release scope, architecture direction, compatibility policy, and security decisions.
- Contributors propose changes through issues/PRs and are encouraged to add regression tests.
- Significant changes to persistence, filesystem mutation, transcript evidence, provider boundaries, or package contracts require explicit design/testing notes.
- Working behavior is not removed solely to simplify code. Compatibility and migration paths are preferred.
- Repeated high-quality contributions may lead to broader review/maintenance permissions.

The long-term goal is to make maintenance less dependent on a single large orchestration file and easier for outside contributors to review safely.
