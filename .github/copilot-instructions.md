# Copilot Instructions

## Stack

- **Frontend**: React 18 + Vite + shadcn/ui + Tailwind CSS + TypeScript
- **Backend**: FastAPI + Python 3.13 + Redis + PlatformIO
- **Firmware**: Arduino framework + ESPAsyncWebServer + WiFiManager + LittleFS
- **Docker**: Multi-stage (node → python/pio → nginx+python runtime)

## Conventions

### Python
- Use `from __future__ import annotations` at top of every file
- Type annotations on all functions (strict mypy)
- Async functions for all I/O (FastAPI, Redis, subprocess)
- structlog for logging (never `print()`)
- ruff for linting (line-length: 100)

### TypeScript/React
- Functional components only, hooks for state
- shadcn/ui components from `src/components/ui/`
- Tailwind for all styling (no inline styles)
- `cn()` utility for conditional class merging

### Git
- Branch: `feature/<description>` or `fix/<description>`
- Commits: conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
- PR: must pass CI (lint + tests + docker build)

### Adding a Board
1. `frontend/src/lib/boards.ts` — add `Board` entry
2. `backend/app/api/build.py` — add to `valid_boards` set
3. `backend/app/services/builder.py` — add to `BOARD_ENV_MAP` + `BOARD_CHIP_MAP`
4. `.github/workflows/firmware-test.yml` — add to matrix if new chip type
5. `docs/board-support.md` — update table

## PR Workflow

1. Open issue first for features/bugs
2. Fork → branch → implement → test → PR
3. Link issue in PR description (`Closes #N`)
4. One approval required to merge
