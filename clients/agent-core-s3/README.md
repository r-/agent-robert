# Agent CoreS3

The **edge device** component of the Agent R.O.B.E.R.T. ecosystem, running on an [M5Stack CoreS3](https://docs.m5stack.com/en/core/CoreS3).

## Role in the System

```
┌─────────────┐     HTTP/JSON     ┌─────────────┐     in-process     ┌─────────────┐
│  CoreS3     │ ───────────────▶  │  API Router  │ ───────────────▶  │  Agent       │
│  (This)     │ ◀───────────────  │  :8787       │ ◀───────────────  │  R.O.B.E.R.T │
└─────────────┘                   └─────────────┘                   └─────────────┘
   Edge Device                      Web Gateway                      AI Brain
```

The CoreS3 acts as a **physical interface** — it can:
- Display information on its 320×240 touch screen
- Record audio via dual microphones
- Send queries to Agent R.O.B.E.R.T. via the API Router
- Control Home Assistant devices (via Robert's HA tools)

## Getting Started

1. Install [PlatformIO](https://platformio.org/install) in VS Code
2. Open this folder as a PlatformIO project
3. Read [ONBOARDING.md](ONBOARDING.md) for hardware specs and coding standards
4. Build: `pio run`
5. Upload: `pio run --target upload`

## Prerequisites

- M5Stack CoreS3 hardware
- USB-C cable
- API Router running on the local network (`http://api-router.local:8787`)
