"""
Rotary encoder + push-button handler for MicroPython.

Detects rotation direction via quadrature decoding and distinguishes
short taps from long presses on the button.
"""

import machine
import time

_LONG_PRESS_MS = 700   # threshold in ms between short and long press


class RotaryEncoder:
    """Polling-based rotary encoder.  Call update() every loop iteration.

    Parameters
    ----------
    pin_a    : int   GPIO for encoder A phase.
    pin_b    : int   GPIO for encoder B phase.
    pin_btn  : int   GPIO for push-button (optional; None to disable).
    """

    def __init__(self, pin_a, pin_b, pin_btn=None):
        self._a = machine.Pin(pin_a, machine.Pin.IN, machine.Pin.PULL_UP)
        self._b = machine.Pin(pin_b, machine.Pin.IN, machine.Pin.PULL_UP)
        self._btn = (
            machine.Pin(pin_btn, machine.Pin.IN, machine.Pin.PULL_UP)
            if pin_btn is not None else None
        )
        self._last_a   = self._a.value()
        self._btn_down = False
        self._press_t  = 0

    # ── public ───────────────────────────────────────────────────────────────

    def update(self):
        """Poll the encoder once and return events.

        Returns
        -------
        delta       : int    +1 (CW), -1 (CCW), or 0.
        short_press : bool   True once on release after < 700 ms.
        long_press  : bool   True once on release after >= 700 ms.
        """
        delta              = self._read_delta()
        short_p, long_p    = self._read_btn()
        return delta, short_p, long_p

    # ── private ──────────────────────────────────────────────────────────────

    def _read_delta(self):
        a = self._a.value()
        if a == self._last_a:
            return 0
        delta       = 1 if (self._b.value() != a) else -1
        self._last_a = a
        return delta

    def _read_btn(self):
        if self._btn is None:
            return False, False
        pressed = not self._btn.value()   # active-low
        now     = time.ticks_ms()
        short_p = long_p = False

        if pressed and not self._btn_down:
            self._btn_down = True
            self._press_t  = now
        elif not pressed and self._btn_down:
            self._btn_down = False
            duration = time.ticks_diff(now, self._press_t)
            if duration < _LONG_PRESS_MS:
                short_p = True
            else:
                long_p = True

        return short_p, long_p
