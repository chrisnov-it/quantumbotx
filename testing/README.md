# Testing Folder Policy

`testing/` is intended for public-safe regression checks, demos, and diagnostics
that do not contain broker credentials, account IDs, private server names, or
local recovery scripts.

Use `testing_private/` for local-only scripts, broker/account diagnostics, and
anything tied to a specific trading account. That folder is ignored by Git.

Before adding new files here, avoid committing:

- API keys, passwords, tokens, account numbers, or broker server names.
- Logs or screenshots from real accounts.
- One-off scripts that mutate local bot state or place orders.
