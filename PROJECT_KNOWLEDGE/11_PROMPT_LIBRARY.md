# Prompt Library

Prompt definitions are embedded in `app/app.py` and package JSON generation rather than maintained as a clearly isolated prompt library. Schema and prompt version fields exist in ChatGPT request records.

Recommendation: inventory each prompt ID/version, purpose, inputs, expected schema, safety rules, backward compatibility, and tests before changing prompts.
