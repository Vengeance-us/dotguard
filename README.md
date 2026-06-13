<p align="center">
  <img src="logo.png" alt="dotguard logo" width="140" />
</p>
<h1 align="center">dotguard</h1>
<p align="center">
  Validate your <code>.env</code> file against <code>.env.example</code> before you deploy.
</p>
<p align="center">
  <a href="https://pypi.org/project/dotguard/"><img alt="PyPI" src="https://img.shields.io/pypi/v/dotguard?color=000&labelColor=111&style=flat-square"></a>
  <a href="https://pypi.org/project/dotguard/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/dotguard?color=000&labelColor=111&style=flat-square"></a>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-000?labelColor=111&style=flat-square"></a>
</p>

---

## The problem

AI-assisted coding is fast. It's also quietly shipping placeholder credentials, empty secrets, and misconfigured environments to production every day.

Your `.env` file is the last line of defense — and most teams never validate it.

**dotguard does.**

---

## What it catches

| Check | Severity |
|---|---|
| Key in `.env.example` missing from `.env` | `ERROR` |
| Sensitive key with an empty value | `ERROR` |
| Sensitive key with a placeholder value (e.g. `your-key-here`) | `ERROR` |
| `.env` file tracked or staged in git | `ERROR` |
| Non-sensitive key with a placeholder value | `WARNING` |
| Key in `.env` not documented in `.env.example` | `WARNING` |
| Non-sensitive key with an empty value | `WARNING` |

---

## Install

```bash
pip install dotguard
```

---

## Usage

```bash
dotguard                   # Validate .env against .env.example
dotguard --strict          # Treat warnings as errors (recommended for CI)
dotguard --fail-on errors  # Exit 1 on errors only (default)
dotguard --fail-on warnings # Exit 1 on warnings only
dotguard --fail-on all     # Exit 1 on any issue
dotguard --no-extras       # Treat undocumented keys as errors
dotguard --no-git-check    # Skip git tracking check
dotguard --quiet           # Silent — exit code only
dotguard init              # Generate .env.example from your .env
dotguard init --force      # Overwrite an existing .env.example
```

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | All checks passed |
| `1` | One or more errors |
| `2` | File not found |

---

## CI integration

Drop dotguard into your pipeline to catch environment issues before they reach production.

### GitHub Actions (reusable workflow)

The easiest way to integrate dotGuard is via the reusable workflow. Add this to your own repo's workflow file:

```yaml
jobs:
  dotguard:
    uses: Vengeance-us/dotguard/.github/workflows/dotguard.yml@main
    with:
      fail_on: "errors"       # "errors" | "warnings" | "all" (default: "errors")
      env_file: ".env"        # path to your .env file (default: ".env")
      example_file: ".env.example"  # path to your .env.example (default: ".env.example")
      pr_comment: true        # post findings as a PR comment (default: false)
```

> If no `.env` file is found in the repository, dotGuard skips gracefully and the workflow passes.

### GitHub Actions (inline)

Prefer to inline it directly in your own workflow?

```yaml
- name: Validate environment
  run: |
    pip install dotguard
    dotguard --fail-on errors
```

### Pre-commit hook

```bash
# .git/hooks/pre-commit
dotguard --quiet || { echo "dotguard: fix .env errors before committing"; exit 1; }
```

---

## Getting started

If you don't have a `.env.example` yet, generate one from your existing `.env`:

```bash
dotguard init
```

This creates a `.env.example` with all your keys present but values scrubbed — safe to commit, ready to share with your team.

Then validate any time:

```bash
dotguard
```

---

## License

[MIT](LICENSE)

---

<p align="center">
  Built for developers who ship with confidence.
</p>
