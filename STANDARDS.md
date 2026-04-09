# Standards

All contributions to Cyber Port repositories must follow these standards.

---

## Language

All content must be in **English**: code, READMEs, comments, commit messages, documentation, and deploy scripts.

## Code Quality

- Python 3.11+ with type annotations on public functions
- `ruff` for linting, `mypy` for type checking
- `pytest` with minimum 70% coverage gate on all Python repositories
- Inline comments on CI/CD files explaining each step
- No placeholder text — only real, functional content

## Structure

Every repository must contain:
- `README.md` — Objective, Use cases, Structure, How to run, Contributing, Roadmap, License, Ethical disclaimer
- `LICENSE` — CC BY 4.0
- `SECURITY.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `ROADMAP.md`
- `.github/workflows/ci.yml`
- `tests/` with coverage gate

## Ethics

All content must be strictly **defensive**. No offensive tools, exploits, payloads, bypass techniques, or malicious automation of any kind. Every repository must include an ethical disclaimer.

## Governance

The 13-repo structure is permanent. New content goes inside existing repositories, never in new ones.
