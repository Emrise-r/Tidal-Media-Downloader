# AGENTS.md — Tidal-Media-Downloader

## Project
Python CLI `tidal-dl` that downloads Tidal media. Source lives in `TIDALDL-PY/tidal_dl/`.
Entry point: `tidal_dl:main` (console script `tidal-dl`). Python 3.10–3.14. Runtime deps
in `TIDALDL-PY/setup.py` (aigpy, requests, pycryptodome, pydub, prettytable).
Published on PyPI as **`tidal-dl-max`** (the `tidal-dl` name is the upstream author's);
the installed command stays `tidal-dl`. This is a fork of yaronzz/Tidal-Media-Downloader.

## Layout (TIDALDL-PY/tidal_dl/)
- `__init__.py` — entry, getopt CLI, interactive menu
- `tidal.py` — `TidalAPI` client, OAuth, media/metadata HTTP
- `events.py` — login + download orchestration
- `settings.py` — `Settings`/`TokenSettings` (`~/.tidal-dl.json`, `~/.tidal-dl.token.json`)
- `apiKey.py` — client-id/secret table (embedded + optional remote gist refresh) + auth metadata
- `pkce.py` — OAuth2 PKCE helpers (browser open, loopback callback server) + `SchemeStrategy` base;
  per-OS `tidal://` registration lives in `pkce_windows.py` / `pkce_linux.py` / `pkce_macos.py`
- `model.py`, `paths.py`, `printf.py`, `download.py`, `decryption.py`, `enums.py`, `lang/`

## Run / install
Install from source: `cd TIDALDL-PY && pip install .` (or `pip install -e .` for dev), then
`tidal-dl`. Or from PyPI: `pip install tidal-dl-max`. Imports are flat; `__init__.py` inserts
`tidal_dl/` onto `sys.path` at runtime so the flat imports resolve when installed.
Build a release: `python -m build` in `TIDALDL-PY/`; publish with `twine upload dist/*`.
Bump `VERSION` in `printf.py` first (date format `YYYY.MM.DD.N`).

## Conventions
- Auth per client is selected by `apiKey` entry `authMethod` (`device` | `pkce`).
- Keys are embedded as a fallback; an **optional remote refresh** replaces them at startup
  from a raw gist (`apiKey.__KEYS_URL__`, overridable via the `TIDAL_KEYS_URL` env var) so keys
  can be rotated without a PyPI release. Any fetch failure keeps the embedded keys.
- `apiKeyIndex` is **positional** — keep the remote key order/count identical (append-only).
  The PKCE key (`Tidal client (PKCE)`, unlocks HI_RES_LOSSLESS) is **index 5**.
- Tokens are stored base64-obfuscated in `~/.tidal-dl.token.json` (portable across machines).

## Secrets (env / .env)
`apiKey.py` reads credentials from the environment so secrets stay out of the repo.
Loaded from `$TIDAL_ENV_FILE`, else `~/.tidal-dl.env`, else `./.env` (see `.env.example`);
existing env vars win over the file. `.env` / `*.env` / `.tidal-dl.env` are gitignored.
- Custom client (appended as the last selectable key): `TIDAL_CLIENT_ID` (required),
  `TIDAL_CLIENT_SECRET` (blank for public PKCE), `TIDAL_AUTH_METHOD` (pkce|device, default
  pkce), `TIDAL_SCOPE`, `TIDAL_REDIRECT_URI`, `TIDAL_CLIENT_NAME`.
- Override an embedded key's secret by clientId: `TIDAL_SECRET_<clientId>=...`.
- The PKCE desktop client (`3a5dzbD1VqdaUmqG`) is a public client — it has NO secret;
  only a `client_id` is needed and it is not sensitive.

## Plan flow
Implementation plans are kept in `plans/` (this repo) so any session can resume. Each plan
is a markdown file; update it as steps complete. Current work: `plans/pkce-hires-lossless-auth.md`.
