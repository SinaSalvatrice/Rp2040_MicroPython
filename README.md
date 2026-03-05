# RP2040 Zero — 3×3 Macropad

Minimal, hackable macropad firmware for the **RP2040 Zero** running **MicroPython**.  
Two layers, rotary encoder, 9-LED NeoPixel strip with breathing effects, and a 128×64 OLED.

---

## Hardware you need

| Component | Detail |
|---|---|
| Controller | RP2040 Zero |
| Key switches | 3×3 matrix (9 switches) |
| Rotary encoder | EC11 or compatible (with push button) |
| LED strip | WS2812B × 9 (NeoPixel) |
| Display | SSD1306 OLED, 128×64, I²C |
| Diodes | 1N4148 × 9 (one per switch, for col2row anti-ghosting) |

---

## Wiring

| GPIO | Role | Notes |
|---|---|---|
| GP0 | SDA | OLED I²C data |
| GP1 | SCL | OLED I²C clock |
| GP3 | COL 0 | Matrix column — OUTPUT |
| GP4 | COL 1 | Matrix column — OUTPUT |
| GP5 | COL 2 | Matrix column — OUTPUT |
| GP6 | ROW 0 | Matrix row — INPUT, pull-up |
| GP7 | ROW 1 | Matrix row — INPUT, pull-up |
| GP8 | ROW 2 | Matrix row — INPUT, pull-up |
| GP9 | ENC A | Encoder phase A |
| GP10 | ENC B | Encoder phase B |
| GP11 | ENC BTN | Encoder push button |
| GP12 | NEOPIXEL | WS2812B data line |

**Matrix wiring (col2row):**  
Each column pin connects to one side of a row of switches.  
The other side of each switch connects (through a diode, cathode toward the row pin) to a row pin.  
Diode direction: `COL → |> → ROW`

---

## Key layout

```
┌────────┬────────┬────────┐
│   0    │   1    │   2    │  ← row 0
├────────┼────────┼────────┤
│   3    │   4    │   5    │  ← row 1
├────────┼────────┼────────┤
│   6    │   7    │   8    │  ← row 2
└────────┴────────┴────────┘
 col 0    col 1    col 2
```

---

## Layers

Switch layers with a **short tap** on the encoder button.

### Layer 0 — Navigate  (LEDs breathe turquoise)

| Position | Key | Sends |
|---|---|---|
| 0 (top-left) | Home | `Home` |
| 1 (top-mid) | Up | `↑` |
| 2 (top-right) | PgUp | `Page Up` |
| 3 (mid-left) | Left | `←` |
| 4 (center) | Enter | `Enter` |
| 5 (mid-right) | Right | `→` |
| 6 (bot-left) | End | `End` |
| 7 (bot-mid) | Down | `↓` |
| 8 (bot-right) | PgDn | `Page Down` |
| Encoder CW | NxtTab | `Ctrl + Tab` |
| Encoder CCW | PrvTab | `Ctrl + Shift + Tab` |

### Layer 1 — Edit  (LEDs breathe orange)

| Position | Key | Sends |
|---|---|---|
| 0 | Undo | `Ctrl + Z` |
| 1 | Cut | `Ctrl + X` |
| 2 | Redo | `Ctrl + Y` |
| 3 | Copy | `Ctrl + C` |
| 4 | Paste | `Ctrl + V` |
| 5 | Find | `Ctrl + F` |
| 6 | Save | `Ctrl + S` |
| 7 | SelAll | `Ctrl + A` |
| 8 | Close | `Alt + F4` |
| Encoder CW | Redo | `Ctrl + Y` |
| Encoder CCW | Undo | `Ctrl + Z` |

---

## Encoder button

| Press | Action |
|---|---|
| Short tap (< 700 ms) | Switch layer (Navigate ↔ Edit) |
| Long press (≥ 700 ms) | Toggle RGB LEDs on / off |

---

## RGB LEDs

| Event | Behaviour |
|---|---|
| Boot | One-shot sweep: LEDs light up one by one in turquoise, then fade out |
| Layer 0 active | Slow turquoise breathing |
| Layer 1 active | Slow orange breathing |
| Long-press encoder btn | Toggle LEDs on / off |

---

## Display

The OLED shows:
- **Layer** name (Navigate / Edit)
- **Last key** pressed
- **RGB** on/off status

---

## Setup

### 1. Flash MicroPython

Download the latest RP2040 `.uf2` from  
<https://micropython.org/download/rp2-pico/>

Hold **BOOT**, plug USB, release BOOT — the RP2040 mounts as a drive.  
Drag the `.uf2` onto it. It reboots into MicroPython.

### 2. Install the USB HID library

Open a serial REPL (Thonny, `mpremote`, PuTTY — anything at 115200 baud) and run:

```python
import mip
mip.install("micropython-usb")
```

> **No internet on the board?**  Download the `micropython-usb` wheel from  
> <https://github.com/micropython/micropython-lib> and copy it with `mpremote` or Thonny.

### 3. Copy the project files

Copy the following to the **root** of the RP2040 filesystem:

```
code.py
lib/
  keymatrix.py
  encoder.py
  rgb_effects.py
  ssd1306.py
  keymap.py
```

With `mpremote`:
```bash
mpremote cp code.py :code.py
mpremote cp -r lib :lib
```

With Thonny: use **File → Save as…** and pick *MicroPython device*.

### 4. Reset

Press the RESET button (or power-cycle). The macropad starts immediately.

---

## Customising the keymap

Edit **`lib/keymap.py`**:

- `LAYER_NAVIGATE` — list of 9 action dicts for Layer 0.
- `LAYER_EDIT`     — list of 9 action dicts for Layer 1.
- `ENC_NAVIGATE` / `ENC_EDIT` — dicts with `"cw"` and `"ccw"` actions.

Each action is built with the helper `_k(name, *keycodes)`:

```python
_k("MyKey", KC.CTRL, KC.ALT, KC.DEL)
```

All keycodes are in the `KC` class (USB HID Usage IDs, Keyboard/Keypad page 0x07).  
Add your own by looking up the value in the  
[USB HID Usage Tables](https://usb.org/sites/default/files/hut1_4.pdf) (table 10).

---

## Library reference

| File | What it does |
|---|---|
| `lib/keymatrix.py` | col2row matrix scanner with debounce |
| `lib/encoder.py` | Quadrature rotary encoder + short/long button detection |
| `lib/rgb_effects.py` | NeoPixel startup sweep and sinusoidal layer breathing |
| `lib/ssd1306.py` | Framebuf-based SSD1306 I²C OLED driver |
| `lib/keymap.py` | HID keycodes (`KC`), layer definitions, encoder actions |

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| No keypresses sent | Install `micropython-usb` (step 2 above) |
| OLED blank | Check GP0/GP1 wiring; verify I²C address (try `0x3D` if `0x3C` fails) |
| LEDs don't light | Check GP12 → DIN on the strip; verify 5 V power |
| Wrong key fires | Check column/row wiring matches `col_pins`/`row_pins` in `code.py` |
| Encoder skips steps | Increase `debounce_ms` in `KeyMatrix` or slow down the polling loop |