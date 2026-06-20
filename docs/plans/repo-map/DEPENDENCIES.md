# Dependency map

Status: **partially verified**

Verified on 2026-06-20 with `uv 0.11.9` and Python 3.12.

## Python environment

The repository is now a uv-managed Python project:

```sh
uv sync --all-extras --all-groups
```

Pinned project inputs:

- Python: `>=3.12,<3.13`
- HUD: `hud-python[modal]==0.6.4`
- Modal SDK: `modal==1.5.0`
- harden-v0 support deps: `harbor`, `litellm`, `pydantic`, `tenacity`,
  `PyYAML`, `python-dotenv`, `tqdm`
- dev deps: `pytest`, `ruff`

Observed install results:

- `hud-python==0.6.4`
- `modal==1.5.0`
- `harbor==0.15.0`
- `litellm==1.89.2`

The exact transitive set is in `uv.lock`.

## External source checkouts

harden-v0 is not a normal Python package at the verified revision: the upstream
has `requirements.txt` but no `pyproject.toml`. Terminal Wrench is a sparse
dataset source checkout. Both are fetched as pinned external source checkouts:

```sh
scripts/bootstrap_external_deps.sh
```

The script writes ignored checkouts under `.external/`.

| Dependency | Source | Revision | Local path | Verification |
|---|---|---:|---|---|
| harden-v0 | `https://github.com/few-sh/harden-v0.git` | `b9dd28c732e7e5435da4a2ac90ae92ac6ea65007` | `.external/harden-v0` | `env PYTHONPATH=.external/harden-v0 uv run python -m harden --help` exits 0 |
| Terminal Wrench | `https://github.com/few-sh/terminal-wrench.git` | `d8a29613235a0ef56a8b70b3142626a533da28c2` | `.external/terminal-wrench` sparse checkout | `tasks/mongodb-sales-aggregation-engine` exists |

## Authentication and system prerequisites

These are not installed by the repository:

- Root `.env`: copy `.env.example` to `.env` for local development. The real
  `.env` file is ignored and must not be committed.
- HUD API key: set with root `.env`, `HUD_API_KEY`, or a developer-local HUD
  configuration workflow that does not put secret values in shell history.
- Modal credentials: run `uv run python -m modal setup`.
- LLM provider key for harden-v0/LiteLLM, such as Anthropic or Gemini.
- Docker for harden-v0/Harbor task execution.
- Linux Docker Engine `>=20.10` if using harden-v0 `--pool-enabled`.

See `docs/plans/specs/07-environment.md` for the canonical variable list.

## Still blocked

Dependency setup does not create the missing product integration surfaces. Gate
1 still needs a real source trace, HUD adapter, Modal adapter, grader/verifier,
artifact store, and sandbox security controls.
