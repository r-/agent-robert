# 🚀 M5Stack CoreS3 — Project Onboarding

Welcome to the CoreS3 development environment.
This document is the **technical baseline** for all development within the `agent-core-s3` project using PlatformIO + Arduino.

---

## 🛠 1. Environment Requirements

| Requirement | Value |
|---|---|
| **IDE** | VS Code / Antigravity |
| **Build System** | PlatformIO (PIO) |
| **Platform** | `espressif32` |
| **Board** | `m5stack-cores3` |
| **Framework** | Arduino |
| **Primary Libraries** | M5Unified (hardware abstraction), M5GFX (display & touch) |

---

## 📐 2. Hardware Specifications

The CoreS3 is **not** a standard ESP32. You must respect these constraints:

### Core

| Component | Specification | Development Notes |
|---|---|---|
| MCU | ESP32-S3 (Dual-core Xtensa LX7 @ 240 MHz) | Supports native USB-CDC |
| RAM | 512 KB Internal SRAM + **8 MB PSRAM** | Use PSRAM for large buffers |
| Flash | 16 MB | Partitioned for OTA + SPIFFS/LittleFS |
| Storage | MicroSD card slot | SD CS on GPIO 4, FAT32 format |
| Power | AXP2101 PMU | `M5.begin()` required to power peripherals |

### Display & Input

| Component | Specification | Development Notes |
|---|---|---|
| Display | 2.0" IPS LCD, 320×240 (ILI9342C) | Use `M5.Display` (M5GFX) |
| Touch | FT6336U (Capacitive) | Multi-touch supported |

### Audio

| Component | Specification | Development Notes |
|---|---|---|
| Speaker | 1W via AW88298 (16-bit I2S amp) | Use `M5.Speaker` |
| Microphones | Dual, via ES7210 audio decoder | Use `M5.Mic` |

### Sensors & Peripherals

| Component | Specification |
|---|---|
| Camera | GC0308 (0.3 MP) |
| IMU | BMI270 (6-axis accelerometer + gyro) |
| Magnetometer | BMM150 |
| Proximity | LTR-553ALS-WA |
| RTC | BM8563 (timekeeping + sleep wake-up) |

### Grove Ports

| Port | Pins | Protocol |
|---|---|---|
| Port A | GPIO1, GPIO2 | I2C |
| Port B | GPIO8, GPIO9 | GPIO / UART |
| Port C | GPIO17, GPIO18 | GPIO / UART |

---

## 💻 3. Programming Standards

### A. The "M5 Boilerplate"

Always initialize the device at the start of `setup()`. This turns on the screen, speaker, and power management.

```cpp
#include <M5Unified.h>

void setup() {
    auto cfg = M5.config();
    M5.begin(cfg);

    // CoreS3 uses Native USB. Use M5.Log or USBSerial.
    M5.Log.setLogLevel(m5::log_target_serial, ESP_LOG_INFO);
    M5_LOGI("System Initialized");
}

void loop() {
    M5.update(); // CRITICAL: Updates touch/button states every frame
}
```

### B. Memory Management

With 8 MB of PSRAM available, **always** allocate large buffers (images, audio, maps) in PSRAM:

```cpp
uint8_t* buffer = (uint8_t*)heap_caps_malloc(size, MALLOC_CAP_SPIRAM);
if (!buffer) {
    M5_LOGE("PSRAM allocation failed!");
}
```

### C. Networking & Discovery

- **mDNS**: Use `ESPmDNS.h`. Devices should resolve to `<devicename>.local`.
- **Local APIs**: Never hardcode IPs. Use mDNS or configure the API Router URL via a config file on the SD card.
- **Agent Integration**: Connect to Agent R.O.B.E.R.T. via the API Router:

```cpp
#include <HTTPClient.h>

// POST to the router's /agent endpoint
HTTPClient http;
http.begin("http://api-router.local:8787/agent");
http.addHeader("Content-Type", "application/json");
http.addHeader("Authorization", "Bearer cores3-key-1");

String payload = "{\"message\":\"Hello from CoreS3\",\"session_key\":\"cores3\"}";
int code = http.POST(payload);

if (code == 200) {
    String response = http.getString();
    // Parse JSON and display on screen
}
http.end();
```

---

## 📁 4. Project Structure (PlatformIO)

```
/agent-core-s3/
├── platformio.ini          # Build configuration
├── ONBOARDING.md           # This file
├── README.md               # Project overview
├── src/
│   └── main.cpp            # Entry point
├── include/                # Header files
├── lib/                    # Custom local libraries
└── data/                   # SPIFFS/LittleFS files (optional)
```

---

## 🔍 5. Troubleshooting

| Problem | Solution |
|---|---|
| **Device not found** | Hold Reset to enter Download Mode (green LED solid). Use correct USB-C port. |
| **Black screen** | Ensure `M5.begin()` is called. AXP2101 must power the LCD rail. |
| **SD Card fail** | Format to FAT32. Try `SD.begin(GPIO_NUM_4, SPI, 25000000);` if auto-detect fails. |
| **PSRAM not working** | Ensure `board_build.arduino.memory_type = qio_opi` in `platformio.ini`. |
| **Serial not printing** | CoreS3 uses USB-CDC, not UART. Use `M5.Log` or `USBSerial`. |

---

## 📚 6. References

- [M5Stack CoreS3 Docs](https://docs.m5stack.com/en/core/CoreS3)
- [M5Unified GitHub](https://github.com/m5stack/M5Unified)
- [M5GFX GitHub](https://github.com/m5stack/M5GFX)
- [PlatformIO ESP32-S3](https://docs.platformio.org/en/latest/boards/espressif32/m5stack-cores3.html)

---

> **Next Step for AI Agent**: Read `platformio.ini`. If missing, generate one using the `m5stack-cores3` environment with M5Unified and M5GFX dependencies.
