# Optional GPT-OSS-120B stage

This stage is intentionally separate from the deterministic native experiment. It asks the same model to choose a safe next continuation action from different representations. It measures whether the minimal representations remain useful when a stochastic reasoning model consumes them.

The API key is read only from `.env`; do not hard-code or commit it.
