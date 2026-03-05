"""
Keymap definitions for the 3×3 macropad.

Physical key layout (viewed from above):
  ┌─────┬─────┬─────┐
  │  0  │  1  │  2  │  row 0
  ├─────┼─────┼─────┤
  │  3  │  4  │  5  │  row 1
  ├─────┼─────┼─────┤
  │  6  │  7  │  8  │  row 2
  └─────┴─────┴─────┘
   col0  col1  col2

  key_index = row * 3 + col

Each action is a dict:
    {"name": str, "codes": [int, ...]}
where codes are USB HID Usage IDs from the Keyboard/Keypad Usage Page (0x07).
"""


# ── USB HID key codes ────────────────────────────────────────────────────────
class KC:
    # Modifier keys (go into modifier byte of HID report)
    CTRL  = 0xE0   # Left Control
    SHIFT = 0xE1   # Left Shift
    ALT   = 0xE2   # Left Alt
    GUI   = 0xE3   # Left GUI (Win / Cmd)

    # Navigation cluster
    HOME  = 0x4A
    PG_UP = 0x4B
    END   = 0x4D
    PG_DN = 0x4E
    RIGHT = 0x4F
    LEFT  = 0x50
    DOWN  = 0x51
    UP    = 0x52

    # Common keys
    ENTER = 0x28
    ESC   = 0x29
    TAB   = 0x2B
    DEL   = 0x4C
    SPACE = 0x2C

    # Letters (USB HID offset: 'a' = 0x04)
    A = 0x04; B = 0x05; C = 0x06; D = 0x07
    E = 0x08; F = 0x09; G = 0x0A; H = 0x0B
    I = 0x0C; J = 0x0D; K = 0x0E; L = 0x0F
    M = 0x10; N = 0x11; O = 0x12; P = 0x13
    Q = 0x14; R = 0x15; S = 0x16; T = 0x17
    U = 0x18; V = 0x19; W = 0x1A; X = 0x1B
    Y = 0x1C; Z = 0x1D

    # Function keys
    F1  = 0x3A; F2  = 0x3B; F3  = 0x3C; F4  = 0x3D
    F5  = 0x3E; F6  = 0x3F; F7  = 0x40; F8  = 0x41
    F9  = 0x42; F10 = 0x43; F11 = 0x44; F12 = 0x45


def _k(name, *codes):
    """Build an action dict from a human-readable name and HID key codes."""
    return {"name": name, "codes": list(codes)}


# ── Layer 0 — Navigate (turquoise) ──────────────────────────────────────────
#
#   Home  │  Up   │ PgUp
#  ───────┼───────┼───────
#   Left  │ Enter │ Right
#  ───────┼───────┼───────
#   End   │ Down  │ PgDn
#
LAYER_NAVIGATE = [
    _k("Home",  KC.HOME),            # 0
    _k("Up",    KC.UP),              # 1
    _k("PgUp",  KC.PG_UP),           # 2
    _k("Left",  KC.LEFT),            # 3
    _k("Enter", KC.ENTER),           # 4
    _k("Right", KC.RIGHT),           # 5
    _k("End",   KC.END),             # 6
    _k("Down",  KC.DOWN),            # 7
    _k("PgDn",  KC.PG_DN),           # 8
]

# Encoder rotation in navigate layer
ENC_NAVIGATE = {
    "cw":  _k("NxtTab", KC.CTRL, KC.TAB),          # next browser/editor tab
    "ccw": _k("PrvTab", KC.CTRL, KC.SHIFT, KC.TAB), # previous tab
}


# ── Layer 1 — Edit (orange) ──────────────────────────────────────────────────
#
#   Undo  │  Cut   │ Redo
#  ───────┼────────┼───────
#   Copy  │ Paste  │ Find
#  ───────┼────────┼───────
#   Save  │SelAll  │ Close
#
LAYER_EDIT = [
    _k("Undo",   KC.CTRL, KC.Z),          # 0
    _k("Cut",    KC.CTRL, KC.X),          # 1
    _k("Redo",   KC.CTRL, KC.Y),          # 2
    _k("Copy",   KC.CTRL, KC.C),          # 3
    _k("Paste",  KC.CTRL, KC.V),          # 4
    _k("Find",   KC.CTRL, KC.F),          # 5
    _k("Save",   KC.CTRL, KC.S),          # 6
    _k("SelAll", KC.CTRL, KC.A),          # 7
    _k("Close",  KC.ALT,  KC.F4),         # 8
]

# Encoder rotation in edit layer
ENC_EDIT = {
    "cw":  _k("Redo", KC.CTRL, KC.Y),
    "ccw": _k("Undo", KC.CTRL, KC.Z),
}


# ── Aggregated exports ───────────────────────────────────────────────────────
LAYERS      = [LAYER_NAVIGATE, LAYER_EDIT]
LAYER_NAMES = ["Navigate", "Edit    "]   # padded to equal length for display
ENC_ACTIONS = [ENC_NAVIGATE, ENC_EDIT]
