# Plan: Local API keys + OAuth2 PKCE login (HI_RES_LOSSLESS)

> Resumable plan. Update the Progress checklist as steps complete.

## Progress
- [x] Phase 0: Scaffold `AGENTS.md` + repo `plans/` folder
- [x] `apiKey.py`: remove gist fetch, add PKCE client + `authMethod`
- [x] `model.py`: extend `LoginKey` for PKCE
- [x] `tidal.py`: add PKCE endpoints + fix `refreshAccessToken`
- [x] `pkce.py`: browser open, loopback server, scheme registration
- [x] `events.py`: `loginByPkce` + `loginByWebAuto` dispatcher
- [x] `__init__.py`: startup scheme register, `--auth-callback`, route login
- [x] `settings.py` + `lang/english.py`: port setting + AUTH strings
      (menu unchanged — the existing Login item auto-selects PKCE via the dispatcher)
- [x] Extra fixes: `setup.py` reads VERSION without importing the package;
      `__init__.py` puts the package dir on `sys.path` so flat imports work from any cwd
      (was a pre-existing bug: installed `tidal-dl` only ran from the `tidal_dl/` dir).
- [x] Automated verify: import w/o network, PKCE URL build, loopback round-trip,
      wrong-state rejection, Linux `tidal://` registration, real handler via installed binary
- [x] Live verify (real TIDAL account): full PKCE browser login OK (user 206790073, BR);
      HI_RES_LOSSLESS granted by playback endpoint; downloaded track 537242474 =
      48kHz/24-bit FLAC. Key token-exchange fix: must send `client_unique_key` (matching
      the authorize request) or TIDAL returns `invalid_client` / sub_status 1005
      ("issued to another client"). Handler `.desktop` must be `Terminal=false`.
      Shared-file fallback (`~/.tidal-dl.authcode`) added alongside the loopback port.

## How to run (dev)
Deps live only in the gcloud-bundled Python 3.14. Run the source from the package dir:
```
cd TIDALDL-PY/tidal_dl
/usr/lib/google-cloud-sdk/platform/bundledpythonunix/bin/python3 __init__.py
```
Or reinstall so the global `tidal-dl` uses this source:
```
cd TIDALDL-PY
/usr/lib/google-cloud-sdk/platform/bundledpythonunix/bin/python3 -m pip install --user --force-reinstall --no-deps --no-build-isolation .
```
In the menu: `7` -> key index `5` (TIDAL Desktop PKCE) to log in; `5` -> quality `4` (Max).

## Context
`tidal-dl` (in `TIDALDL-PY/tidal_dl/`) currently:
- Downloads its Tidal client-id/secret table from a **public GitHub gist** at import time
  (`apiKey.py:101-108`), overwriting the embedded `__KEYS_JSON__`.
- Authenticates **only via the OAuth2 device flow** (`getDeviceCode` + poll in `loginByWeb`),
  using `auth.tidal.com/v1/oauth2/device_authorization` and `/token` with HTTP-basic
  `(clientId, clientSecret)`.
- The bundled valid clients (index 1 `7m7Ap0JC9j1cOM3n`, index 4 `zU4XHVVkc2tDPo4t`) do
  **not** unlock the newest `HI_RES_LOSSLESS` quality.

Goal: stop pulling client keys from the public gist and keep them local; add the user's own
client (`3a5dzbD1VqdaUmqG`, the TIDAL desktop app) which unlocks `HI_RES_LOSSLESS`. That
client only supports **OAuth2 authorization-code + PKCE** (redirect `tidal://login/auth`),
not device flow — so add a PKCE login that works like `gcloud auth login`: auto-open the
browser (fallback to printing the URL), wait up to 5 minutes, auto-capture the code. Because
the redirect is a custom `tidal://` scheme, register that scheme with the OS
(Windows/Linux/macOS/Android-termux) at startup so the browser redirect is delivered back to
the running CLI; a loopback HTTP server receives the forwarded code, with manual paste as the
final fallback. Device flow is kept for the existing keys.

The mapping `AudioQuality.Max -> "HI_RES_LOSSLESS"` already exists (`tidal.py:362-363`).

## Decisions (confirmed)
- Keys: keep embedded `__KEYS_JSON__`, delete gist fetch, add user's client. No external file.
- Callback: loopback HTTP auto-capture + manual-paste fallback.
- Scheme: register `tidal://` -> `tidal-dl` at startup if not present.
- Device flow: keep both; flow chosen by the selected key's `authMethod`.

## Changes

### 1. `apiKey.py`
- Delete gist block (~lines 101-108) and the `import requests` used only for it.
- Add `authMethod` to every entry (existing -> `"device"`).
- Append PKCE entry: clientId `3a5dzbD1VqdaUmqG`, clientSecret `""`, `authMethod:"pkce"`,
  `scope:"r_usr w_usr"`, `redirectUri:"tidal://login/auth"`, `valid:"True"`.
- Add `getAuthMethod(index)`; update `__ERROR_KEY__`.

### 2. `model.py`
Add `LoginKey` fields: `codeVerifier`, `state`, `redirectUri`, `clientUniqueKey`, `authUrl`.

### 3. `tidal.py`
- `getPkceLoginUrl()`: PKCE verifier/challenge (S256), state, client_unique_key; build
  `https://login.tidal.com/authorize?...` (client_id, redirect_uri, response_type=code,
  code_challenge, code_challenge_method=S256, scope, appMode=DESKTOP, lang=en,
  restrictSignup=true, client_unique_key, state).
- `getTokenByCode(code)`: POST `auth.tidal.com/v1/oauth2/token`, grant_type=authorization_code,
  code, code_verifier, redirect_uri, client_id, no basic auth.
- Fix `refreshAccessToken`: only send basic auth when clientSecret is non-empty; else client_id
  in body with `auth=None`.

### 4. `pkce.py` (new)
- `open_browser(url)->bool` (webbrowser; termux-open-url fallback).
- `CallbackServer` on 127.0.0.1:`SETTINGS.authCallbackPort` (default 8989), daemon thread,
  validates state, `wait(timeout=300)->code`; writes `~/.tidal-dl.authcb.json` {port,state}.
- `deliver_callback(url)`: parse code/state, forward to running server via localhost.
- `register_scheme()`: idempotent per-OS `tidal://` registration (Windows winreg, Linux
  .desktop+xdg-mime, macOS .app+lsregister, termux no-op); marker file `~/.tidal-dl.scheme`.
- `parse_code(url)->(code,state)`.

### 5. `events.py`
- `loginByPkce()`: gcloud-style (build url, start server, open browser + print url, wait 300s,
  manual-paste fallback, `getTokenByCode`, save TOKEN). Reuse `__displayTime__`.
- `loginByWebAuto()` dispatcher by `apiKey.getAuthMethod(SETTINGS.apiKeyIndex)`.

### 6. `__init__.py`
- Call `pkce.register_scheme()` once at startup (marker-guarded).
- Add `--auth-callback <url>` getopt -> `pkce.deliver_callback` then return.
- Route menu login through `loginByWebAuto()`.

### 7. `settings.py`
Add `authCallbackPort = 8989`.

### 8. `printf.py` / `lang/english.py`
Menu label(s); add `AUTH_PKCE_*` / `AUTH_MANUAL_PASTE` strings.

## Verification
1. `python -c "import apiKey"` from `tidal_dl/` — no github HTTP; `getItems()` includes PKCE entry.
2. Launch `tidal-dl`; Linux `xdg-mime query default x-scheme-handler/tidal` -> `tidal-dl.desktop`;
   re-launch does no duplicate work.
3. PKCE happy path: select PKCE key, Login -> browser -> `tidal://` redirect -> loopback captures
   code -> token saved; subsequent `loginByConfig` works.
4. Manual fallback: block browser; paste redirected URL completes login within 5 min.
5. HI_RES_LOSSLESS: set quality Max; download HiRes track; `getStreamUrl` requests
   `HI_RES_LOSSLESS` and returns a stream.
6. Device flow still works for a device key (e.g. index 4).
