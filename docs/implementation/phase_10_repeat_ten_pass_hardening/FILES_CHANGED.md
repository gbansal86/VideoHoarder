# Files Changed

| File | Change | Requirement |
|---|---|---|
| app/app.py | residual safe merges; portable OAuth/dependency help; canonical URL classifier delegation | FIX-105, SEC-106, FIX-109 |
| app/youtube_url.py | exact `www.` prefix handling + canonical host predicate | SEC-106 |
| app/download_access.py | reuse canonical YouTube host predicate | SEC-106 |
| app/file_safety.py | reserved device-name variants with pre-extension spaces | FIX-107 |
| app/native_ui.py | video-quality choices/privacy wording | FIX-108 |
| scripts/create_code_parent_package.py | pristine full-schema config.example + validation | GOV-110 |
| tests/test_repeat_ten_pass_cycle.py | regression coverage | FIX-105..GOV-110 |
| docs/implementation/* | governance/final evidence | DOC-111 |
