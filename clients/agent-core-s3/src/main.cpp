/**
 * Agent R.O.B.E.R.T. — CoreS3 Edge Device
 * 
 * Minimal boilerplate that initializes the M5Stack CoreS3 hardware
 * and displays a greeting on screen. This serves as the starting
 * point for all CoreS3 development.
 */

#include <M5Unified.h>

void setup() {
    // 1. Initialize hardware (display, power, touch, audio)
    auto cfg = M5.config();
    M5.begin(cfg);

    // 2. Set up logging via USB-CDC
    M5.Log.setLogLevel(m5::log_target_serial, ESP_LOG_INFO);
    M5_LOGI("Agent R.O.B.E.R.T. CoreS3 — System Initialized");

    // 3. Display greeting
    M5.Display.setTextSize(2);
    M5.Display.setTextColor(TFT_WHITE, TFT_BLACK);
    M5.Display.fillScreen(TFT_BLACK);
    M5.Display.setCursor(20, 40);
    M5.Display.println("Agent R.O.B.E.R.T.");
    M5.Display.setCursor(20, 80);
    M5.Display.setTextSize(1);
    M5.Display.println("CoreS3 Edge Device");
    M5.Display.setCursor(20, 120);
    M5.Display.println("Status: Online");

    M5_LOGI("Display ready");
}

void loop() {
    // CRITICAL: Must call M5.update() every frame
    // This updates touch state, button state, and power management
    M5.update();

    // Touch detection example
    if (M5.Touch.getCount() > 0) {
        auto touch = M5.Touch.getDetail(0);
        if (touch.wasPressed()) {
            M5_LOGI("Touch at (%d, %d)", touch.x, touch.y);
        }
    }

    delay(10); // Small delay to prevent watchdog issues
}
