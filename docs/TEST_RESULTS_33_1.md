# VideoHoarder 33.1-GUI — final validation evidence

Date: 2026-09-22

## Commands executed

```text
python -m pytest -q
```

Final result:

```text
341 passed, 22 skipped in 7.15s
```

A prior final verification run in the same source tree also returned `341 passed, 22 skipped`; the repeated pass is intentional evidence that the provider/packaging changes did not destabilize the suite.

Compile validation was also run with Python `compileall` against application, tests, scripts and build-support code.

## OpenAI-provider coverage

The new tests verify:

- provider readiness without exposing API-key values;
- one-video-per-call evidence isolation;
- `store=false` propagation;
- Structured Outputs request shape;
- JSON-object compatibility fallback;
- continue-after-one-video-error behavior;
- secret-free provider audit;
- private/unlisted/restricted-video blocking by default;
- explicit restricted-video opt-in;
- settings accept only the environment-variable name, not a stored OpenAI key;
- web/API orchestration imports results for review and does not auto-apply them.

The tests use a fake OpenAI SDK/client and perform no network request or paid model call.

## Platform boundary

One historical test asserted Windows `git.exe` path semantics on Linux. It is now explicitly Windows-only rather than changing production behavior. Windows remains the primary release platform.

## Not executed here

- Windows PyInstaller build and executable startup smoke test.
- A real OpenAI API call using a user's credential.

Both are deliberately excluded from this source-only validation environment.
