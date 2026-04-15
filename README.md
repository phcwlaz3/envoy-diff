# envoy-diff

> CLI tool to diff and validate environment variable configs across deployment stages

---

## Installation

```bash
pip install envoy-diff
```

Or install from source:

```bash
git clone https://github.com/yourname/envoy-diff.git && cd envoy-diff && pip install .
```

---

## Usage

Compare environment variable configs between two stages:

```bash
envoy-diff staging.env production.env
```

Validate that all required variables are present in a target config:

```bash
envoy-diff --validate staging.env production.env
```

Output missing or mismatched keys across files:

```bash
envoy-diff --format json staging.env production.env
```

**Example output:**

```
[MISSING]  DATABASE_URL        found in staging, not in production
[CHANGED]  LOG_LEVEL           staging=debug  production=info
[OK]       APP_PORT            matched in both
```

---

## Options

| Flag | Description |
|------|-------------|
| `--validate` | Exit with non-zero status if differences are found |
| `--format` | Output format: `text` (default) or `json` |
| `--ignore` | Comma-separated list of keys to ignore |

---

## License

MIT © 2024 [yourname](https://github.com/yourname)