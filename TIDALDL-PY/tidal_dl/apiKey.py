#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  apiKey.py
@Date    :  2021/11/30
@Author  :  Yaronzz
@Version :  3.0
@Contact :  yaronhuang@foxmail.com
@Desc    :
"""
import json
import os

# API keys are embedded and local. They are intentionally NOT fetched from any
# remote repository/gist at runtime. Each key declares an `authMethod`:
#   - "device": OAuth2 device-authorization flow (getDeviceCode + poll)
#   - "pkce":   OAuth2 authorization-code flow with PKCE (browser + callback)
# PKCE clients are public and use no clientSecret; they declare `scope` and
# `redirectUri` used to build the authorize URL.
__KEYS_JSON__ = '''
{
    "version": "1.0.2",
    "keys": [
        {
            "platform": "Fire TV",
            "formats": "Normal/High/HiFi(No Master)",
            "clientId": "OmDtrzFgyVVL6uW56OnFA2COiabqm",
            "clientSecret": "zxen1r3pO0hgtOC7j6twMo9UAqngGrmRiWpV7QC1zJ8=",
            "authMethod": "device",
            "valid": "False",
            "from": "Fokka-Engineering (https://github.com/Fokka-Engineering/libopenTIDAL/blob/655528e26e4f3ee2c426c06ea5b8440cf27abc4a/README.md#example)"
        },
        {
            "platform": "Fire TV",
            "formats": "Master-Only(Else Error)",
            "clientId": "7m7Ap0JC9j1cOM3n",
            "clientSecret": "vRAdA108tlvkJpTsGZS8rGZ7xTlbJ0qaZ2K9saEzsgY=",
            "authMethod": "device",
            "valid": "True",
            "from": "Dniel97 (https://github.com/Dniel97/RedSea/blob/4ba02b88cee33aeb735725cb854be6c66ff372d4/config/settings.example.py#L68)"
        },
        {
            "platform": "Android TV",
            "formats": "Normal/High/HiFi(No Master)",
            "clientId": "Pzd0ExNVHkyZLiYN",
            "clientSecret": "W7X6UvBaho+XOi1MUeCX6ewv2zTdSOV3Y7qC3p3675I=",
            "authMethod": "device",
            "valid": "False",
            "from": ""
        },
        {
            "platform": "TV",
            "formats": "Normal/High/HiFi/Master",
            "clientId": "8SEZWa4J1NVC5U5Y",
            "clientSecret": "owUYDkxddz+9FpvGX24DlxECNtFEMBxipU0lBfrbq60=",
            "authMethod": "device",
            "valid": "False",
            "from": "morguldir (https://github.com/morguldir/python-tidal/commit/50f1afcd2079efb2b4cf694ef5a7d67fdf619d09)"
        },
        {
            "platform": "Android Auto",
            "formats": "Normal/High/HiFi/Master",
            "clientId": "zU4XHVVkc2tDPo4t",
            "clientSecret": "VJKhDFqJPqvsPVNBV6ukXTJmwlvbttP7wlMlrc72se4=",
            "authMethod": "device",
            "valid": "True",
            "from": "1nikolas (https://github.com/yaronzz/Tidal-Media-Downloader/pull/840)"
        },
        {
            "platform": "Tidal client (PKCE)",
            "formats": "Normal/High/HiFi/Master/Max(HI_RES_LOSSLESS)",
            "clientId": "3a5dzbD1VqdaUmqG",
            "clientSecret": "",
            "authMethod": "pkce",
            "scope": "r_usr w_usr",
            "redirectUri": "tidal://login/auth",
            "valid": "True",
            "from": "emrise"
        }
    ]
}
'''
__API_KEYS__ = json.loads(__KEYS_JSON__)

# Optional remote key list. When a URL is configured, the embedded table above is
# refreshed from it at startup so keys can be rotated WITHOUT republishing to PyPI
# (the client ids are public, not secret). Any failure keeps the embedded keys, so
# the tool still works offline / if the URL is down.
# Configure via the TIDAL_KEYS_URL env var, or hard-code a raw gist URL here.
# The URL must return the same JSON shape: {"version": "...", "keys": [ ... ]}.
# This "no-hash" gist raw URL always serves the latest revision, so keys can be
# rotated by editing the gist — no new release needed. TIDAL_KEYS_URL overrides it.
__KEYS_URL__ = 'https://gist.githubusercontent.com/Emrise-r/10b7bff98778b465d8e44437290f5a21/raw/tidal-keys.json'

__ERROR_KEY__ = {
    'platform': 'None',
    'formats': '',
    'clientId': '',
    'clientSecret': '',
    'authMethod': 'device',
    'valid': 'False',
}


def getNum():
    return len(__API_KEYS__['keys'])


def getItem(index: int):
    if index < 0 or index >= len(__API_KEYS__['keys']):
        return __ERROR_KEY__
    return __API_KEYS__['keys'][index]


def isItemValid(index: int):
    item = getItem(index)
    return item['valid'] == 'True'


def getItems():
    return __API_KEYS__['keys']


def getLimitIndexs():
    array = []
    for i in range(len(__API_KEYS__['keys'])):
        array.append(str(i))
    return array


def getVersion():
    return __API_KEYS__['version']


def getAuthMethod(index: int):
    item = getItem(index)
    return item.get('authMethod', 'device')


# ---------------------------------------------------------------------------
# Secrets from the environment / a .env file (keep credentials out of the repo)
# ---------------------------------------------------------------------------
def _load_dotenv():
    """
    Populate os.environ from a .env file (without overriding vars already set).
    Search order: $TIDAL_ENV_FILE, ~/.tidal-dl.env, ./.env. Lightweight parser,
    no external dependency. Lines are KEY=VALUE; '#' comments and blanks ignored;
    surrounding quotes on the value are stripped.
    """
    home = os.environ.get('HOME') or os.path.expanduser('~')
    candidates = [
        os.environ.get('TIDAL_ENV_FILE'),
        os.path.join(home, '.tidal-dl.env'),
        os.path.join(os.getcwd(), '.env'),
    ]
    for path in candidates:
        if not path or not os.path.isfile(path):
            continue
        try:
            with open(path, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    k, v = line.split('=', 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v
        except Exception:
            pass


def _apply_env_overrides():
    """
    Two ways to supply credentials via the environment:
      1. Override the secret of an embedded key by its clientId:
           TIDAL_SECRET_<clientId>=...
      2. Define a fully custom client (added as the last selectable key):
           TIDAL_CLIENT_ID=...            (required to enable)
           TIDAL_CLIENT_SECRET=...        (blank for public PKCE clients)
           TIDAL_AUTH_METHOD=pkce|device  (default: pkce)
           TIDAL_SCOPE=r_usr w_usr        (default)
           TIDAL_REDIRECT_URI=tidal://login/auth (default)
           TIDAL_CLIENT_NAME=...          (display label, optional)
    """
    for key in __API_KEYS__['keys']:
        env_secret = os.environ.get('TIDAL_SECRET_' + str(key.get('clientId', '')))
        if env_secret:
            key['clientSecret'] = env_secret

    cid = os.environ.get('TIDAL_CLIENT_ID')
    if cid:
        __API_KEYS__['keys'].append({
            'platform': os.environ.get('TIDAL_CLIENT_NAME', 'Custom (env)'),
            'formats': 'Normal/High/HiFi/Master/Max(HI_RES_LOSSLESS)',
            'clientId': cid,
            'clientSecret': os.environ.get('TIDAL_CLIENT_SECRET', ''),
            'authMethod': os.environ.get('TIDAL_AUTH_METHOD', 'pkce'),
            'scope': os.environ.get('TIDAL_SCOPE', 'r_usr w_usr'),
            'redirectUri': os.environ.get('TIDAL_REDIRECT_URI', 'tidal://login/auth'),
            'valid': 'True',
            'from': 'environment / .env',
        })


def _load_remote_keys():
    """
    Refresh the key table from TIDAL_KEYS_URL (or __KEYS_URL__) if set. Lets keys
    be rotated remotely without a new release. Never fatal: on any error (no URL,
    network failure, bad JSON, empty list) the embedded keys are kept as-is.
    """
    url = os.environ.get('TIDAL_KEYS_URL') or __KEYS_URL__
    if not url:
        return
    try:
        import requests
        data = requests.get(url, timeout=6).json()
        if isinstance(data, dict) and isinstance(data.get('keys'), list) and data['keys']:
            __API_KEYS__['version'] = data.get('version', __API_KEYS__.get('version'))
            __API_KEYS__['keys'] = data['keys']
    except Exception:
        pass  # keep embedded keys


_load_dotenv()          # so TIDAL_KEYS_URL can come from a .env file too
_load_remote_keys()     # remote refresh (optional, falls back to embedded)
_apply_env_overrides()  # env secret/custom-client overrides win on top
