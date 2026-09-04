# VideoHoarder ChatGPT Exchange

This repository is reserved for VideoHoarder package exchange.

## Workflow

1. VideoHoarder publishes planner or intelligence packages under `exchange/outgoing/`.
2. Each `CHATGPT_PACKAGE.json` is processed independently using the strongest reasoning mode available.
3. ChatGPT reads only the specifically requested package path.
4. Returned result JSON files are placed under `exchange/incoming/results/` for VideoHoarder validation.
5. Validation reports are stored under `exchange/validation/`.

Video media, authentication tokens, local databases, and application configuration must never be committed.

The repository state before conversion is preserved on branch `backup-before-chatgpt-exchange-20260903`.
