"""
3×3 Macropad — RP2040 Zero
──────────────────────────
Platform  : MicroPython v1.22+
            USB HID requires: import mip; mip.install("micropython-usb")

Pin map
-------
  GP0   SDA  ──┐  SSD1306 OLED, 128×64, I²C addr 0x3C
  GP1   SCL  ──┘
  GP3   COL0 ─┐
  GP4   COL1  ├─  3×3 key matrix (col2row)
  GP5   COL2 ─┘
  GP6   ROW0 ─┐
  GP7   ROW1  ├─  rows use internal pull-up; LOW = pressed
  GP8   ROW2 ─┘
  GP9   ENC A ─┐
  GP10  ENC B  ├─  rotary encoder
  GP11  ENC BTN┘
  GP12  NEOPIX ─   WS2812B strip, 9 LEDs

Encoder button
--------------
  Short tap  (< 700 ms) → switch layer  (Navigate ↔ Edit)
  Long press (≥ 700 ms) → toggle RGB LEDs on / off
"""

import machine
import time

from lib.keymatrix   import KeyMatrix
from lib.encoder     import RotaryEncoder
from lib.rgb_effects import RGBEffects
from lib.ssd1306     import SSD1306_I2C
from lib.keymap      import LAYERS, LAYER_NAMES, ENC_ACTIONS


# ── USB HID keyboard (optional — graceful fallback) ──────────────────────────
_kbd = None
try:
    import usb.device
    from usb.device.keyboard import KeyboardInterface
    _kbd_iface = KeyboardInterface()
    usb.device.get().init(_kbd_iface, builtin_driver=True)
    time.sleep_ms(500)   # let USB enumerate
    _kbd = _kbd_iface
    print("[HID] keyboard ready")
except Exception as e:
    print("[HID] not available:", e)
    print("      Install via:  import mip; mip.install('micropython-usb')")


# ── hardware init ─────────────────────────────────────────────────────────────
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400_000)

_display_ok = False
try:
    display     = SSD1306_I2C(128, 64, i2c)
    _display_ok = True
    print("[OLED] ready")
except Exception as e:
    print("[OLED] not found:", e)

matrix  = KeyMatrix(col_pins=[3, 4, 5], row_pins=[6, 7, 8])
encoder = RotaryEncoder(pin_a=9, pin_b=10, pin_btn=11)

_rgb_ok = False
try:
    rgb     = RGBEffects(pin=12, num_leds=9)
    _rgb_ok = True
    print("[RGB] ready")
except Exception as e:
    print("[RGB] init error:", e)


# ── state ─────────────────────────────────────────────────────────────────────
layer    = 0
last_key = "---"


# ── helpers ───────────────────────────────────────────────────────────────────
def send_key(action):
    """Press and immediately release the keys defined in *action*."""
    if _kbd is None or action is None:
        return
    codes = action.get("codes", [])
    if codes:
        _kbd.send_keys(codes)
        time.sleep_ms(15)
        _kbd.send_keys([])


def draw_display():
    if not _display_ok:
        return
    display.fill(0)
    # ── title bar (inverted) ─────────────────────────────────────────
    display.fill_rect(0, 0, 128, 12, 1)
    display.text("  MACROPAD  3x3  ", 2, 2, 0)
    # ── layer ────────────────────────────────────────────────────────
    display.text("Layer:", 2, 16, 1)
    display.text(LAYER_NAMES[layer], 56, 16, 1)
    # ── last key ─────────────────────────────────────────────────────
    display.text("Key:  ", 2, 28, 1)
    display.text(last_key[:9], 56, 28, 1)
    # ── separator ────────────────────────────────────────────────────
    display.hline(0, 42, 128, 1)
    # ── RGB status ───────────────────────────────────────────────────
    rgb_txt = "RGB: ON " if (_rgb_ok and rgb.enabled) else "RGB: OFF"
    display.text(rgb_txt, 2, 50, 1)
    display.show()


# ── startup ───────────────────────────────────────────────────────────────────
if _rgb_ok:
    rgb.startup()
draw_display()


# ── main loop ─────────────────────────────────────────────────────────────────
_tick_t  = time.ticks_ms()
_TICK_MS = 15   # RGB breathing cadence in ms

while True:
    # ── key matrix ──────────────────────────────────────────────────────────
    pressed, _ = matrix.scan()
    if pressed:
        idx      = pressed[0]               # process one key per iteration
        action   = LAYERS[layer][idx]
        last_key = action["name"]
        send_key(action)
        draw_display()

    # ── encoder ─────────────────────────────────────────────────────────────
    delta, short_p, long_p = encoder.update()

    if delta:
        enc_action = ENC_ACTIONS[layer]["cw" if delta > 0 else "ccw"]
        last_key   = enc_action["name"]
        send_key(enc_action)
        draw_display()

    if short_p:   # short tap → switch layer
        layer    = 1 - layer
        last_key = "---"
        if _rgb_ok:
            rgb.set_layer(layer)
        draw_display()

    if long_p:    # long press → toggle RGB
        if _rgb_ok:
            rgb.toggle()
        draw_display()

    # ── RGB breathing ────────────────────────────────────────────────────────
    now = time.ticks_ms()
    if time.ticks_diff(now, _tick_t) >= _TICK_MS:
        _tick_t = now
        if _rgb_ok:
            rgb.tick()

    time.sleep_ms(1)
