
# Departure Board Emulator

[![Build](https://github.com/lrzo01/DepartureLineupEmulator/actions/workflows/ci.yml/badge.svg)](https://github.com/lrzo01/DepartureLineupEmulator/actions/workflows/ci.yml)
[![Lint](https://github.com/lrzo01/DepartureLineupEmulator/actions/workflows/lint.yml/badge.svg)](https://github.com/lrzo01/DepartureLineupEmulator/actions/workflows/lint.yml)


This project aims to recreate departure lineup boards which are specifically found around major stations, powered by live data from the [Worldline TIGER API](https://tiger-api-portal.worldline.global).

These specifically have been focused on intermediate stations on the ECML (Newcastle, Berwick, York etc) which are now removed in favour of more modern displays.

## Preview

<img width="1680" height="1014" alt="image" src="https://github.com/user-attachments/assets/b66ba79a-1a32-44d6-9080-1c6a9df4e90f" />

## Running the project
Binaries for Windows, Linux and MacOS are available on the Releases page, no installation of Python is required.

## Running from Source

### Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
git clone https://github.com/lrzo01/DepartureLineupEmulator
cd departure-lineup-emulator

uv sync

uv run departure-board-emulator
```

### Environment

Copy `.env.example` to `.env` and fill in an API key. You can use inspect element to find this on the Worldline TIGER site.

```bash
cp .env.example .env
```

```env
WORLDLINE_TIGER_API_KEY=your_key_here
```



## Building from source

The release CI uses [PyInstaller](https://pyinstaller.org). To build locally:

```bash
uv pip install pyinstaller

uv run pyinstaller \
  --noconsole \
  --noconfirm \
  --name=departure-board-emulator \
  --add-data="config.toml:." \
  --add-data=".env:." \
  --add-data="fonts:fonts" \
  run.py
```

Output will be in `dist/`
