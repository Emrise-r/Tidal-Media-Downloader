# AGENTS.md — Tidal-Media-Downloader

## Project
Python CLI `tidal-dl` that downloads Tidal media. Source lives in `TIDALDL-PY/tidal_dl/`.
Entry point: `tidal_dl:main` (console script `tidal-dl`). Python 3, deps in
`TIDALDL-PY/setup.py` / `requirements.txt` (aigpy, requests, pycryptodome, pydub,
prettytable, lxml).

## Layout (TIDALDL-PY/tidal_dl/)
- `__init__.py` — entry, getopt CLI, interactive menu
- `tidal.py` — `TidalAPI` client, OAuth, media/metadata HTTP
- `events.py` — login + download orchestration
- `settings.py` — `Settings`/`TokenSettings` (`~/.tidal-dl.json`, `~/.tidal-dl.token.json`)
- `apiKey.py` — bundled client-id/secret table + auth metadata
- `pkce.py` — OAuth2 PKCE helpers: browser open, loopback callback server, `tidal://` scheme registration
- `model.py`, `paths.py`, `printf.py`, `download.py`, `decryption.py`, `enums.py`, `lang/`

## Run / install
From `TIDALDL-PY/`: `pip install -r requirements.txt && python setup.py install`, then
`tidal-dl`. Imports are flat, so run with `tidal_dl/` on `sys.path`.

## Conventions
- Auth per client is selected by `apiKey` entry `authMethod` (`device` | `pkce`).
- Keys are embedded and local — never fetch credentials from remote repos/gists.
- Tokens are stored base64-obfuscated in `~/.tidal-dl.token.json`.

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
