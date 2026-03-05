"""
Minimal SSD1306 OLED driver for MicroPython (I²C).

Works with any 128×32 or 128×64 SSD1306 display.
Uses the built-in framebuf module for all drawing primitives.

Usage
-----
    import machine
    from lib.ssd1306 import SSD1306_I2C

    i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400_000)
    display = SSD1306_I2C(128, 64, i2c)

    display.fill(0)
    display.text("Hello!", 0, 0, 1)
    display.show()
"""

import framebuf


class SSD1306_I2C:
    """SSD1306 OLED connected over I²C.

    Parameters
    ----------
    width  : int              Display width  in pixels (128 typical).
    height : int              Display height in pixels (32 or 64).
    i2c    : machine.I2C      Initialised I²C bus object.
    addr   : int              I²C address (default 0x3C).
    """

    def __init__(self, width, height, i2c, addr=0x3C):
        self.w     = width
        self.h     = height
        self._i    = i2c
        self._a    = addr
        self._pages = height // 8
        self._buf  = bytearray(self._pages * width)
        self.fb    = framebuf.FrameBuffer(self._buf, width, height, framebuf.MONO_VLSB)
        self._init_display()

    # ── framebuf pass-throughs ──────────────────────────────────────────────

    def fill(self, c=0):
        self.fb.fill(c)

    def pixel(self, x, y, c=1):
        self.fb.pixel(x, y, c)

    def text(self, s, x, y, c=1):
        self.fb.text(s, x, y, c)

    def rect(self, x, y, w, h, c=1):
        self.fb.rect(x, y, w, h, c)

    def fill_rect(self, x, y, w, h, c=1):
        self.fb.fill_rect(x, y, w, h, c)

    def hline(self, x, y, w, c=1):
        self.fb.hline(x, y, w, c)

    def vline(self, x, y, h, c=1):
        self.fb.vline(x, y, h, c)

    def line(self, x1, y1, x2, y2, c=1):
        self.fb.line(x1, y1, x2, y2, c)

    # ── display control ─────────────────────────────────────────────────────

    def show(self):
        """Push the framebuffer contents to the physical display."""
        self._cmd(0x21, 0x00, self.w - 1)      # set column address range
        self._cmd(0x22, 0x00, self._pages - 1)  # set page address range
        # prepend data control byte (0x40) to the framebuffer
        data    = bytearray(len(self._buf) + 1)
        data[0] = 0x40
        data[1:] = self._buf
        self._i.writeto(self._a, data)

    def clear(self):
        """Clear screen (fill black) and push immediately."""
        self.fill(0)
        self.show()

    # ── private ─────────────────────────────────────────────────────────────

    def _cmd(self, *args):
        """Send one or more command bytes to the controller."""
        for byte in args:
            self._i.writeto(self._a, bytes([0x00, byte]))

    def _init_display(self):
        for c in (
            0xAE,               # display off
            0xD5, 0x80,         # set display clock divide ratio
            0xA8, self.h - 1,   # set multiplex ratio
            0xD3, 0x00,         # set display offset
            0x40,               # set start line 0
            0x8D, 0x14,         # enable charge pump
            0x20, 0x00,         # set memory addressing mode: horizontal
            0xA1,               # set segment re-map (col 127 → SEG0)
            0xC8,               # set COM output scan direction: remapped
            0xDA, 0x12 if self.h == 64 else 0x02,   # set COM pins config
            0x81, 0xCF,         # set contrast
            0xD9, 0xF1,         # set pre-charge period
            0xDB, 0x40,         # set VCOMH deselect level
            0xA4,               # output follows RAM content
            0xA6,               # set normal display (not inverted)
            0xAF,               # display ON
        ):
            self._cmd(c)
