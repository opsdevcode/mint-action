# mint-action

First-party composite GitHub Action for Mint. It downloads an exact
`specmint` wheel from a GitHub Release, checks `SHA256SUMS`, installs it
on `ubuntu-latest` / Python 3.12, and runs `mint check` or `mint plan`.

Public preview. No `mint apply`. No live mutation. No Marketplace
listing. Pin an immutable commit SHA; there is no `latest` and no
`@main`.

## Default pins

| Input | Default |
| --- | --- |
| `language-tag` | `v0.7.0-alpha.2` |
| `language-wheel` | `specmint-0.7.0a2-py3-none-any.whl` |

Recorded wheel digest from that release:
`sha256:6407ded7475ccec10985735eb4992cad49cc4e84be98da93128cfa7aef0f4452`.

## Workflow

```yaml
name: Mint
on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  mint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: opsdevcode/mint-action@29918519e95b10eec7cbc3ffd253d7c5286599f6
        with:
          project: .
          command: check
```

Use `pull_request`, never `pull_request_target`. Keep the default
`contents: read`. To upload Code Scanning, add a follow-up step with
`security-events: write` on that job only and
`github/codeql-action/upload-sarif` pointing at `mint.sarif`.

`0.7.0a2` emits JSON diagnostics. This action maps that JSON to SARIF
2.1.0. After a language release that includes `--sarif-output`, the
action prefers the compiler-written file.

## Out of scope

- `mint apply`
- `pull_request_target`
- unpinned `latest` installs
- CLI telemetry
- Marketplace publication
