"""
NeoPixel (WS2812B) RGB effects for MicroPython.

Effects
-------
startup()          One-shot startup sweep (blocking, ~1 s).
set_layer(n)       Switch breathing colour to match the active layer.
tick()             Advance breathing animation by one step (~15 ms cadence).
toggle()           Turn all LEDs on or off.

Colours
-------
Layer 0 → turquoise  (0, 80, 70)
Layer 1 → orange     (90, 35, 0)
"""

import machine
import neopixel
import math
import time


class RGBEffects:
    TURQUOISE = (0, 80, 70)
    ORANGE    = (90, 35, 0)
    BLACK     = (0, 0, 0)

    _PERIOD = 180   # steps per full breathing cycle

    def __init__(self, pin, num_leds):
        """
        Parameters
        ----------
        pin      : int   GPIO number for the NeoPixel data line.
        num_leds : int   Number of LEDs in the strip.
        """
        self._np      = neopixel.NeoPixel(machine.Pin(pin), num_leds)
        self._n       = num_leds
        self._enabled = True
        self._color   = self.TURQUOISE
        self._step    = 0

    # ── public ───────────────────────────────────────────────────────────────

    def startup(self):
        """Blocking startup animation: sweep on then sweep off."""
        for i in range(self._n):
            self._np[i] = self.TURQUOISE
            self._np.write()
            time.sleep_ms(60)
        time.sleep_ms(250)
        for i in range(self._n - 1, -1, -1):
            self._np[i] = self.BLACK
            self._np.write()
            time.sleep_ms(40)

    def set_layer(self, layer):
        """Switch breathing colour for *layer* (0 = turquoise, 1 = orange)."""
        self._color = self.TURQUOISE if layer == 0 else self.ORANGE
        self._step  = 0   # restart breathing cycle cleanly

    def toggle(self):
        """Toggle all LEDs on / off."""
        self._enabled = not self._enabled
        if not self._enabled:
            self._fill(self.BLACK)

    @property
    def enabled(self):
        return self._enabled

    def tick(self):
        """Advance breathing animation one step.  Call every ~15 ms."""
        if not self._enabled:
            return
        self._step = (self._step + 1) % self._PERIOD
        t      = self._step / self._PERIOD
        bright = (math.sin(t * 2 * math.pi - math.pi / 2) + 1.0) / 2.0
        bright = bright ** 1.5                     # gentle gamma curve
        r = int(self._color[0] * bright)
        g = int(self._color[1] * bright)
        b = int(self._color[2] * bright)
        self._fill((r, g, b))

    # ── private ──────────────────────────────────────────────────────────────

    def _fill(self, color):
        for i in range(self._n):
            self._np[i] = color
        self._np.write()
