<br>
    <a href="https://github.com/yaronzz/Tidal-Media-Downloader-PRO">[GUI-REPOSITORY]</a>
<br>

![Tidal-Media-Downloader](https://socialify.git.ci/yaronzz/Tidal-Media-Downloader/image?description=1&font=Rokkitt&forks=1&issues=1&language=1&name=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Dark)


<div align="center">
  <h1>Tidal-Media-Downloader</h1>
  <a href="https://github.com/yaronzz/Tidal-Media-Downloader/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/yaronzz/Tidal-Media-Downloader.svg?style=flat-square" alt="">
  </a>
  <a href="https://github.com/yaronzz/Tidal-Media-Downloader/releases">
    <img src="https://img.shields.io/github/v/release/yaronzz/Tidal-Media-Downloader.svg?style=flat-square" alt="">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/github/issues/yaronzz/Tidal-Media-Downloader.svg?style=flat-square" alt="">
  </a>
  <a href="https://github.com/yaronzz/Tidal-Media-Downloader">
    <img src="https://img.shields.io/github/downloads/yaronzz/Tidal-Media-Downloader/total?label=tidal-gui%20download" alt="">
  </a>
  <a href="https://pypi.org/project/tidal-dl/">
    <img src="https://img.shields.io/pypi/dm/tidal-dl?label=tidal-dl%20download" alt="">
  </a>
  <a href="https://github.com/yaronzz/Tidal-Media-Downloader/actions/workflows/build.yml">
    <img src="https://github.com/yaronzz/Tidal-Media-Downloader/actions/workflows/build.yml/badge.svg" alt="">
  </a>
</div>
<p align="center">
  «Tidal-Media-Downloader» is an application that lets you download videos and tracks from Tidal. It supports two version: tidal-dl and tidal-gui. (This repository only contains tidal-dl, and the release isn't the newest gui version.)
    <br>
        <a href="https://github.com/yaronzz/Tidal-Media-Downloader-PRO/releases">Download</a> |
        <a href="https://doc.yaronzz.com/post/tidal_dl_installation/">Documentation</a> |
        <a href="https://doc.yaronzz.com/post/tidal_dl_installation_chn/">中文文档</a> |
    <br>
</p>

## 📺 Installation 

```shell
pip3 install tidal-dl --upgrade
```

| USE                                                   | FUNCTION                   |
| ----------------------------------------------------- | -------------------------- |
| tidal-dl                                              | Show interactive interface |
| tidal-dl -h                                           | Show help-message          |
| tidal-dl -l "https://tidal.com/browse/track/70973230" | Download link              |
| tidal-dl -g                                           | Show simple-gui            |

If you are using windows system, you can use [tidal-pro](https://github.com/yaronzz/Tidal-Media-Downloader-PRO)

## 🛠️ Build from source (PKCE / HI_RES_LOSSLESS fork)

> The PyPI package above is the original **device-flow** build. This fork
> (`feature/oauth2-pkce-flow`) adds an **OAuth2 PKCE login** (API key index `5`,
> _TIDAL Desktop (PKCE)_) that unlocks **HI_RES_LOSSLESS**. It is not on PyPI —
> install it from source.

**Prerequisites**

- Python **3.10 – 3.14** (verified on all five: install, import, and CLI run), `pip`, `git`
- Optional: **ffmpeg** on `PATH` (used by `pydub` for some audio conversions)

**Install (all platforms)**

```shell
git clone https://github.com/Emrise-r/Tidal-Media-Downloader.git
cd Tidal-Media-Downloader/TIDALDL-PY
git checkout feature/oauth2-pkce-flow
pip install .
tidal-dl
```

The console script installs to your user scripts dir (e.g. on Windows
`%APPDATA%\Python\Python3xx\Scripts`); make sure it's on `PATH`. If `pip` can't
overwrite `tidal-dl.exe`, close any running `tidal-dl` first (the exe is locked
while running).

**First-time login (PKCE)**

1. Run `tidal-dl`, choose `7` (Select APIKey) → `5` (_TIDAL Desktop (PKCE)_).
2. A browser opens — sign in and authorize. The `tidal://` redirect is captured
   automatically: on first run the CLI registers a per-OS URL-scheme handler
   (`pkce_windows` / `pkce_linux` / `pkce_macos`) so the code is delivered back
   to the waiting session — no copy-paste needed.
3. Choose `5` (Settings-Quality) → `4` (Max = HI_RES_LOSSLESS).

If auto-capture ever fails, paste the `tidal://login/auth?code=…&state=…` URL
(visible in the browser's DevTools console / address bar) into the waiting
terminal — it's the built-in fallback.

### Per-OS notes

- **Windows — install the *classic* desktop TIDAL, not the Store app.** The
  Microsoft Store (MSIX) TIDAL — package `WiMPMusic` — claims the `tidal://`
  scheme at the app-manifest level, which **outranks this CLI's handler and
  steals the login redirect**. Use winget and verify the source is the plain
  `.exe` installer from `download.tidal.com`:

  ```powershell
  winget show TIDALMusicAS.TIDAL     # Installer Type: exe  (download.tidal.com)
  winget install --id TIDALMusicAS.TIDAL -e
  ```

  If you already have the Store version, remove it first so this CLI's handler
  wins, then install the classic one:

  ```powershell
  Get-AppxPackage WiMPMusic* | Remove-AppxPackage
  ```

- **Linux / macOS** — no competing packaged app, so the handler registers and
  auto-capture works out of the box (manual paste remains the fallback).

### Nightly Builds

|Download nightly builds from continuous integration: 	| [![Build Status][Build]][Actions] 
|-------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|

[Actions]: https://github.com/yaronzz/Tidal-Media-Downloader/actions
[Build]: https://github.com/yaronzz/Tidal-Media-Downloader/workflows/Tidal%20Media%20Downloader/badge.svg

## 🤖 Features
- Download album \ track \ video \ playlist \ artist-albums

- Add metadata to songs

- Selectable video resolution and track quality

## 💽 User Interface

<img src="https://i.loli.net/2020/08/19/gqW6zHI1SrKlomC.png" alt="image" style="zoom: 50%;" />

![image-20220708105823257](https://s2.loli.net/2022/07/08/vV6HsxugwoDyGr8.png)

![image-20200806013705425](https://i.loli.net/2020/08/06/sPLowIlCGyOdpVN.png)

## Settings - Possible Tags

### Album

| Tag               | Example value                        |
| ----------------- | ------------------------------------ |
| {ArtistName}      | The Beatles                          |
| {AlbumArtistName} | The Beatles                          |
| {Flag}            | M/A/E  (Master/Dolby Atmos/Explicit) |
| {AlbumID}         | 55163243                             |
| {AlbumYear}       | 1963                                 |
| {AlbumTitle}      | Please Please Me (Remastered)        |
| {AudioQuality}    | LOSSLESS                             |
| {DurationSeconds} | 1919                                 |
| {Duration}        | 31:59                                |
| {NumberOfTracks}  | 14                                   |
| {NumberOfVideos}  | 0                                    |
| {NumberOfVolumes} | 1                                    |
| {ReleaseDate}     | 1963-03-22                           |
| {RecordType}      | ALBUM                                |
| {None}            |                                      |

### Track

| Tag               | Example Value                              |
| ----------------- | ------------------------------------------ |
| {TrackNumber}     | 01                                         |
| {ArtistName}      | The Beatles                                |
| {ArtistsName}     | The Beatles                                |
| {TrackTitle}      | I Saw Her Standing There (Remastered 2009) |
| {ExplicitFlag}    | (*Explicit*)                               |
| {AlbumYear}       | 1963                                       |
| {AlbumTitle}      | Please Please Me (Remastered)              |
| {AudioQuality}    | LOSSLESS                                   |
| {DurationSeconds} | 173                                        |
| {Duration}        | 02:53                                      |
| {TrackID}         | 55163244                                   |

### Video

| Tag               | Example Value                              |
| ----------------- | ------------------------------------------ |
| {VideoNumber}     | 00                                         |
| {ArtistName}      | DMX                                        |
| {ArtistsName}     | DMX, Westside Gunn                         |
| {VideoTitle}      | Hood Blues                                 |
| {ExplicitFlag}    | (*Explicit*)                               |
| {VideoYear}       | 2021                                       |
| {TrackID}         | 188932980                                  |

## ☕ Support

If you really like my projects and want to support me, you can buy me a coffee and star this project. 

<a href="https://www.buymeacoffee.com/yaronzz" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/arial-orange.png" alt="Buy Me A Coffee" style="height: 51px !important;width: 217px !important;" ></a>

## 🎂 Contributors
This project exists thanks to all the people who contribute. 

<a href="https://github.com/yaronzz/Tidal-Media-Downloader/graphs/contributors"><img src="https://contributors-img.web.app/image?repo=yaronzz/Tidal-Media-Downloader" /></a>

## 🎨 Libraries and reference

- [aigpy](https://github.com/yaronzz/AIGPY)
- [python-tidal](https://github.com/tamland/python-tidal)
- [redsea](https://github.com/redsudo/RedSea)
- [tidal-wiki](https://github.com/Fokka-Engineering/TIDAL/wiki)

## 📜 Disclaimer
- Private use only.
- Need a Tidal-HIFI subscription. 
- You should not use this method to distribute or pirate music.
- It may be illegal to use this in your country, so be informed.

## Developing

Editable install so code changes are picked up without reinstalling:

```shell
cd TIDALDL-PY
pip uninstall -y tidal-dl
pip install -e .
```

`requirements.txt` additionally lists the optional GUI deps (`PyQt5`,
`qt-material`); they are only needed for `tidal-dl -g`.
