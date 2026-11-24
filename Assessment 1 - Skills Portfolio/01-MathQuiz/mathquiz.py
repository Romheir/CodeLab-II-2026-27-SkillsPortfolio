import tkinter as tk # standard gui library
import random # random numbers, operators, and floating items
import time # tracks live quiz timer
import math # powers smooth sine-wave color throbbing

THEMES = { # pitch black and pitch white palettes
    "dark": {
        "bg": "#000000", "card": "#111111", "border": "#262626", "fg": "#FFFFFF",
        "muted": "#A3A3A3", "btn": "#1F1F1F", "btn_hover": "#333333",
        "entry_bg": "#000000", "good": "#22C55E", "bad": "#EF4444", "bar_bg": "#262626"
    },
    "light": {
        "bg": "#FFFFFF", "card": "#F5F5F5", "border": "#D4D4D4", "fg": "#000000",
        "muted": "#525252", "btn": "#E5E5E5", "btn_hover": "#D4D4D4",
        "entry_bg": "#FFFFFF", "good": "#16A34A", "bad": "#DC2626", "bar_bg": "#E5E5E5"
    }
}

DIFF_META = { # geometry dash inspired colors and labels per difficulty
    1: {"name": "1. Easy", "desc": "Single-Digit (1–9)", "color": "#22C55E"},
    2: {"name": "2. Moderate", "desc": "Double-Digit (10–99)", "color": "#EAB308"},
    3: {"name": "3. Advanced", "desc": "4-Digit (1000–9999)", "color": "#EF4444"},
    4: {"name": "4. DEMON", "desc": "5-Digit (10000–99999)", "color": "#A855F7"}
}

THROB_RGB = { # (light_rgb, dark_rgb) pairs for throbbing equations by tier
    1: ((134, 239, 172), (20, 83, 45)),   # light green -> dark green
    2: ((254, 240, 138), (133, 77, 14)),  # light yellow -> dark yellow
    3: ((252, 165, 165), (127, 29, 29)),  # light red -> dark red
    4: ((216, 180, 254), (88, 28, 135))   # light purple -> dark purple
}

FLOATING_POOL = { # variables and equations grouped by difficulty tier
    1: ["+", "−", "x", "y", "2+3", "9−4", "5+7", "8−2", "1+6", "a+b", "="],
    2: ["×", "÷", "%", "45+19", "82−37", "2x=14", "a²+b²", "64−28", "3y+9", "72+15"],
    3: ["√", "π", "Δ", "∑", "1042−891", "3x²−5", "√144", "4812+2190