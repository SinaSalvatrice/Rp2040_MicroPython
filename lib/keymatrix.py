"""
col2row key matrix scanner for MicroPython.

Wiring
------
  Columns → OUTPUT pins, driven LOW one at a time to scan.
  Rows    → INPUT pins with PULL_UP; reads LOW when a key is pressed.

Key index layout (row-major, 0-based):
  ┌───┬───┬───┐
  │ 0 │ 1 │ 2 │  row 0
  ├───┼───┼───┤
  │ 3 │ 4 │ 5 │  row 1
  ├───┼───┼───┤
  │ 6 │ 7 │ 8 │  row 2
  └───┴───┴───┘
  col0 col1 col2

  key_index = row * ncols + col
"""

import machine
import time


class KeyMatrix:
    """Scan a col×row key matrix with simple debouncing.

    Parameters
    ----------
    col_pins : list[int]   GPIO numbers for columns (outputs).
    row_pins : list[int]   GPIO numbers for rows (inputs, pull-up).
    debounce_ms : int      Minimum stable time before a state change is accepted.
    """

    def __init__(self, col_pins, row_pins, debounce_ms=20):
        self.ncols = len(col_pins)
        self.nrows = len(row_pins)
        self._debounce_ms = debounce_ms

        self._cols = [machine.Pin(p, machine.Pin.OUT, value=1) for p in col_pins]
        self._rows = [machine.Pin(p, machine.Pin.IN, machine.Pin.PULL_UP) for p in row_pins]

        n = self.ncols * self.nrows
        self._stable = [False] * n   # last debounced state
        self._raw    = [False] * n   # last raw state
        self._since  = [0] * n       # ticks_ms when raw last changed

    # ── public ───────────────────────────────────────────────────────────────

    def scan(self):
        """Scan the matrix and return debounced events.

        Returns
        -------
        pressed  : list[int]   Key indices that just became pressed.
        released : list[int]   Key indices that just became released.
        """
        raw = self._read_raw()
        now = time.ticks_ms()
        pressed, released = [], []

        for i in range(self.ncols * self.nrows):
            if raw[i] != self._raw[i]:
                self._raw[i]   = raw[i]
                self._since[i] = now
            if (time.ticks_diff(now, self._since[i]) >= self._debounce_ms
                    and raw[i] != self._stable[i]):
                self._stable[i] = raw[i]
                (pressed if raw[i] else released).append(i)

        return pressed, released

    # ── private ──────────────────────────────────────────────────────────────

    def _read_raw(self):
        raw = [False] * (self.ncols * self.nrows)
        for c, col in enumerate(self._cols):
            col.value(0)
            time.sleep_us(10)   # settling time
            for r, row in enumerate(self._rows):
                raw[c + r * self.ncols] = not row.value()
            col.value(1)
        return raw
