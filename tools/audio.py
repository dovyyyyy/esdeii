"""Navigation sound packs and original background music for the esdeii themes.

Everything is synthesised here from scratch (no samples):
  chime - soft square-ish chimes (handheld feel)
  click - short clicky taps and bright bell dings (living-room console menu feel)
  pop   - bubbly pops and marimba tones (tablet console feel)
  menu  - one consistent family of soft glassy clicks and airy swooshes, all in
          the same key and the same small room (living-room console menu feel)
Music: three original loops, rendered to OGG with ffmpeg.
"""
import os, subprocess, wave
import numpy as np
from scipy import signal

SR = 44100
RNG = np.random.default_rng(7)


# ---------------------------------------------------------------- building blocks
def env_ad(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


def sine(freq, dur, phase=0.0):
    n = int(SR * dur)
    f = np.interp(np.arange(n), np.linspace(0, n, len(freq)), freq) if np.ndim(freq) else np.full(n, freq)
    return np.sin(2 * np.pi * np.cumsum(f) / SR + phase)


def noise(dur):
    return RNG.standard_normal(int(SR * dur))


def bandpass(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], btype="band")
    return signal.lfilter(b, a, x)


def lowpass(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), btype="low")
    return signal.lfilter(b, a, x)


def highpass(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), btype="high")
    return signal.lfilter(b, a, x)


def pad_to(x, n):
    return np.concatenate([x, np.zeros(max(0, n - len(x)))])[:n]


def mixdown(parts, total=None):
    n = total or max(off + len(p) for off, p in parts)
    out = np.zeros(n)
    for off, p in parts:
        e = min(n, off + len(p))
        out[off:e] += p[:e - off]
    return out


def bell(freq, dur, vol=0.3, decay=0.25):
    """FM bell / ding."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    mod = np.sin(2 * np.pi * freq * 3.5 * t) * 2.2 * np.exp(-t / (decay * 0.5))
    car = np.sin(2 * np.pi * freq * t + mod)
    return car * env_ad(n, 0.002, decay) * vol


def save_wav(path, s, stereo=False):
    s = np.clip(s, -1, 1)
    data = (s * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2 if stereo else 1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def fade(s, fin=0.003, fout=0.01):
    a, b = int(SR * fin), int(SR * fout)
    s = s.copy()
    if a:
        s[:a] *= np.linspace(0, 1, a)
    if b:
        s[-b:] *= np.linspace(1, 0, b)
    return s


# ---------------------------------------------------------------- sound packs
def pack_chime():
    def tone(freqs, dur, vol, decay):
        n = int(SR * dur)
        ph = 2 * np.pi * np.cumsum(np.interp(np.arange(n), np.linspace(0, n, len(freqs)), freqs)) / SR
        s = (np.sin(ph) + 0.25 * np.sin(3 * ph) + 0.08 * np.sin(5 * ph)) / 1.33
        return s * env_ad(n, 0.004, decay) * vol
    cat = np.concatenate
    return {
        "scroll": tone([1760], 0.035, 0.22, 0.010),
        "systembrowse": tone([1318, 1568], 0.06, 0.25, 0.018),
        "quicksysselect": cat([tone([1175], 0.05, 0.25, 0.015), tone([1568], 0.07, 0.25, 0.02)]),
        "select": cat([tone([1047], 0.06, 0.3, 0.02), tone([1568], 0.12, 0.3, 0.04)]),
        "back": cat([tone([988], 0.06, 0.28, 0.02), tone([659], 0.11, 0.28, 0.035)]),
        "favorite": cat([bell(1568, 0.06, 0.2, 0.03), bell(2093, 0.06, 0.2, 0.03), bell(2637, 0.2, 0.2, 0.06)]),
        "launch": cat([tone([f], 0.09, 0.28, 0.04) for f in (784, 988, 1175)] + [tone([1568], 0.32, 0.3, 0.12)]),
    }


def click(vol=0.5, pitch=2600, body=900, dur=0.03):
    """Short plasticky tap: filtered noise transient + tiny pitched body."""
    n = int(SR * dur)
    nz = bandpass(noise(dur), pitch * 0.6, min(pitch * 2.2, 18000)) * env_ad(n, 0.0005, 0.0025) * 1.4
    tk = sine(body, dur) * env_ad(n, 0.0008, 0.006) * 0.7
    return fade((nz + tk) * vol, 0.0005, 0.004)


def room(x, length=0.22, wet=0.18):
    """Small bright room so taps feel round instead of dry."""
    n = int(SR * length)
    ir = RNG.standard_normal(n) * np.exp(-np.arange(n) / (SR * length / 6))
    ir = lowpass(ir, 7000)
    ir /= np.sqrt(np.sum(ir ** 2))
    dry = np.concatenate([x, np.zeros(n)])
    y = pad_to(signal.fftconvolve(x, ir), len(dry))
    out = dry * (1 - wet) + y * wet * 0.5
    tail = int(SR * 0.02)
    out[-tail:] *= np.linspace(1, 0, tail)
    return out


def tick(f0=2300, f1=1700, dur=0.022, vol=0.5):
    """Crisp tick: a tiny pitched blip that drops in pitch, plus a soft transient."""
    n = int(SR * dur)
    body = sine(np.array([f0, f1]), dur) * env_ad(n, 0.0004, dur / 5)
    tr = lowpass(noise(dur), 9000) * env_ad(n, 0.0002, 0.0012) * 0.35
    return fade((body + tr) * vol, 0.0003, 0.004)


def tok(f0=1050, f1=780, dur=0.045, vol=0.55):
    """Wooden 'tok': rounder, lower blip with a woody overtone."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = np.interp(np.arange(n), [0, n * 0.3, n], [f0, f1, f1])
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.35 * np.sin(2.76 * ph) * np.exp(-t / 0.006)
    tr = bandpass(noise(dur), 1500, 5000) * env_ad(n, 0.0002, 0.0015) * 0.4
    return fade((s * env_ad(n, 0.0006, dur / 4) + tr) * vol, 0.0003, 0.006)


def bubble(f0=500, f1=1500, dur=0.035, vol=0.45):
    """Rising 'bloop' (a bubble popping upward)."""
    n = int(SR * dur)
    s = sine(np.array([f0, f1]), dur) * np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return fade(s * vol, 0.0005, 0.004)


def chime(freq, dur=0.5, vol=0.2, decay=0.16):
    """Soft glassy bell: FM bell with a sine underneath."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = bell(freq, dur, 1.0, decay) * 0.6 + np.sin(2 * np.pi * freq * t) * env_ad(n, 0.002, decay * 1.4) * 0.5
    return fade(s * vol, 0.001, dur * 0.35)


def airy(dur=0.25, vol=0.1, lo=1200, hi=7000):
    n = int(SR * dur)
    return bandpass(noise(dur), lo, hi) * np.sin(np.linspace(0, np.pi, n)) ** 2 * vol


def pack_click():
    sel = mixdown([(0, bubble(520, 1500, 0.035, 0.42)), (int(SR * 0.028), chime(1568, 0.5, 0.2, 0.13)),
                   (int(SR * 0.028), chime(2349, 0.5, 0.09, 0.10))])
    back = mixdown([(0, tok(900, 700, 0.04, 0.45)), (int(SR * 0.03), chime(1175, 0.35, 0.14, 0.08)),
                    (int(SR * 0.10), chime(880, 0.4, 0.13, 0.10))])
    launch = mixdown([(0, bubble(440, 1320, 0.04, 0.4)), (int(SR * 0.02), airy(0.45, 0.07, 2000, 9000))] +
                     [(int(SR * (0.05 + i * 0.065)), chime(f, 0.7, 0.16, 0.2))
                      for i, f in enumerate((1047, 1319, 1568, 2093, 2637))])
    fav = mixdown([(int(SR * i * 0.055), chime(f, 0.45, 0.14, 0.09)) for i, f in enumerate((2093, 2637, 3136))])
    short = ("scroll", "systembrowse", "quicksysselect")  # must stay short for fast scrolling
    return {k: (v if k in short else room(v)) for k, v in {
        "scroll": tick(2300, 1750, 0.022, 0.42),
        "systembrowse": mixdown([(0, tok(1050, 780, 0.045, 0.5)), (0, airy(0.08, 0.035, 2500, 8000))]),
        "quicksysselect": mixdown([(0, tok(980, 760, 0.04, 0.45)), (int(SR * 0.06), tok(1320, 1000, 0.04, 0.45))]),
        "select": sel,
        "back": back,
        "favorite": fav,
        "launch": launch,
    }.items()}


def pop(f0=900, f1=450, dur=0.06, vol=0.4):
    n = int(SR * dur)
    s = sine(np.array([f0, f1]), dur) * env_ad(n, 0.001, dur / 4)
    return fade(s * vol, 0.0008, 0.006)


def marimba(freq, dur=0.35, vol=0.3):
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 4 * t) * np.exp(-t / 0.01))
    return s * env_ad(n, 0.001, 0.08) * vol


def pack_pop():
    return {
        "scroll": pop(1100, 650, 0.045, 0.32),
        "systembrowse": pop(900, 520, 0.06, 0.36),
        "quicksysselect": mixdown([(0, pop(800, 500, 0.05, 0.3)), (int(SR * 0.05), pop(1200, 700, 0.05, 0.3))]),
        "select": mixdown([(0, pop(1000, 600, 0.04, 0.3)), (int(SR * 0.02), marimba(1047)), (int(SR * 0.09), marimba(1568))]),
        "back": mixdown([(0, marimba(880, 0.2)), (int(SR * 0.07), marimba(587, 0.3))]),
        "favorite": mixdown([(int(SR * i * 0.06), marimba(f, 0.3, 0.25)) for i, f in enumerate((1318, 1568, 2093))]),
        "launch": mixdown([(int(SR * i * 0.08), marimba(f, 0.45, 0.28)) for i, f in enumerate((784, 1047, 1318, 1568))]),
    }


# ---------------------------------------------------------------- "menu" pack
# Every sound is built from the same two ingredients - a soft glassy pluck and an
# airy swoosh - in one key (D major pentatonic) and one small room, then levelled
# so nothing jumps out. Moving the cursor always makes exactly the same click.
D5, A5, D6, E6, FS6, A6, B6, D7 = 587.33, 880.0, 1174.66, 1318.51, 1479.98, 1760.0, 1975.53, 2349.32


def glass(freq, dur=0.12, vol=1.0, decay=0.03):
    """Soft rounded pluck: a sine with gentle overtones and a tiny tactile tick."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * freq * t) + 0.16 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t / (decay * 0.5)) +
         0.05 * np.sin(2 * np.pi * freq * 3 * t) * np.exp(-t / (decay * 0.3)))
    s *= env_ad(n, 0.0015, decay)
    k = int(SR * 0.004)
    tickn = highpass(np.random.default_rng(int(freq)).standard_normal(k), 3000) * np.exp(-np.arange(k) / (SR * 0.0006))
    s[:k] += tickn * 0.25
    return fade(s * vol, 0.0004, min(dur * 0.3, 0.02))


def swoosh(dur=0.25, f0=900.0, f1=6000.0, vol=1.0, q=2.2, peak=0.4, seed=1):
    """Airy whoosh: noise through a band-pass that glides from f0 to f1."""
    n = int(SR * dur)
    x = np.random.default_rng(seed).standard_normal(n)
    fc = f0 * (f1 / f0) ** (np.arange(n) / n)  # exponential glide
    y = np.zeros(n)
    low = band = 0.0
    damp = 1.0 / q
    for i in range(n):  # state-variable filter
        g = 2 * np.sin(np.pi * min(fc[i], SR / 6) / SR)
        high = x[i] - low - damp * band
        band += g * high
        low += g * band
        y[i] = band
    u = np.arange(n) / n
    shape = np.where(u < peak, np.sin(u / peak * np.pi / 2) ** 2, np.cos((u - peak) / (1 - peak) * np.pi / 2) ** 2)
    y = lowpass(y, 7500)  # soft and airy, never hissy
    return fade(y * shape * vol / (np.std(y) + 1e-9), 0.002, 0.01)


def level(x, rms_db, window=0.15, ceiling_db=-1.0):
    """Scale so the loudest `window` seconds sit at rms_db, then keep peaks under the ceiling."""
    k = max(1, int(SR * window))
    loud = np.sqrt(np.max(np.convolve(x ** 2, np.ones(k) / k, mode="valid"))) if len(x) > k else np.sqrt(np.mean(x ** 2))
    x = x * (10 ** (rms_db / 20) / (loud + 1e-12))
    pk = np.max(np.abs(x))
    lim = 10 ** (ceiling_db / 20)
    return x * (lim / pk) if pk > lim else x


def pack_menu():
    at = lambda sec: int(SR * sec)
    sounds = {
        # cursor moves: the same short pluck every time, a touch brighter for games
        "scroll": glass(A6, 0.06, 1.0, 0.011),
        "systembrowse": mixdown([(0, glass(FS6, 0.09, 1.0, 0.016)), (0, swoosh(0.09, 2200, 5000, 0.12, seed=2))]),
        "quicksysselect": mixdown([(0, swoosh(0.18, 1400, 5000, 0.35, seed=3)), (at(0.06), glass(A6, 0.1, 0.9, 0.02))]),
        # open: click, a rising swoosh and a two-note ding
        "select": mixdown([(0, glass(D6, 0.4, 1.0, 0.07)), (at(0.045), glass(A6, 0.5, 0.85, 0.1)),
                           (0, swoosh(0.28, 700, 4500, 0.3, seed=4))]),
        # back: a falling swoosh and the same notes going down
        "back": mixdown([(0, swoosh(0.24, 4500, 700, 0.3, peak=0.3, seed=5)), (0, glass(A6, 0.3, 0.9, 0.05)),
                         (at(0.06), glass(D6, 0.4, 0.85, 0.08))]),
        "favorite": mixdown([(at(i * 0.05), glass(f, 0.4, 0.8, 0.06)) for i, f in enumerate((D6, FS6, A6, D7))]),
        # start a game: a long rising swoosh into a bright chord
        "launch": mixdown([(0, swoosh(0.6, 450, 6000, 0.45, peak=0.7, seed=6))] +
                          [(at(0.34 + i * 0.035), glass(f, 0.9, 0.7, 0.22)) for i, f in enumerate((D6, FS6, A6, D7))]),
    }
    targets = {"scroll": -23, "systembrowse": -22, "quicksysselect": -21, "select": -19, "back": -20,
               "favorite": -20, "launch": -19}
    out = {}
    for k, v in sounds.items():
        short = k in ("scroll", "systembrowse", "quicksysselect")  # must stay short for fast scrolling
        v = room(v, 0.07, 0.1) if short else room(v, 0.3, 0.16)
        out[k] = level(v, targets[k])
    return out


PACKS = {"chime": pack_chime, "click": pack_click, "pop": pack_pop, "menu": pack_menu}


def write_pack(name, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for k, s in PACKS[name]().items():
        save_wav(os.path.join(out_dir, k + ".wav"), np.concatenate([s, np.zeros(int(SR * 0.01))]))


# ---------------------------------------------------------------- music
NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}


def hz(name, octave):
    return 440.0 * 2 ** ((NOTE[name] + 12 * (octave + 1) - 69) / 12)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


CHORDS = {"maj7": [0, 4, 7, 11], "m7": [0, 3, 7, 10], "7": [0, 4, 7, 10], "m6": [0, 3, 7, 9], "6": [0, 4, 7, 9],
          "maj9": [0, 4, 7, 11, 14], "m9": [0, 3, 7, 10, 14], "": [0, 4, 7], "m": [0, 3, 7], "sus2": [0, 2, 7],
          "add9": [0, 4, 7, 14]}


def chord(root, kind):
    r = NOTE[root]
    return r, [r + i for i in CHORDS[kind]]


def epiano(freq, dur, vol=0.18):
    n = int(SR * dur)
    t = np.arange(n) / SR
    mod = np.sin(2 * np.pi * freq * t) * 1.6 * np.exp(-t / 0.35)
    s = np.sin(2 * np.pi * freq * t + mod) * (1 + 0.15 * np.sin(2 * np.pi * 5 * t))
    tine = np.sin(2 * np.pi * freq * 7 * t) * 0.08 * np.exp(-t / 0.03)
    return (s + tine) * env_ad(n, 0.004, 0.9) * vol


def piano(freq, dur, vol=0.18):
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * freq * h * t) * np.exp(-t * (1.2 + h * 0.9)) for h, a in
            ((1, 1.0), (2, 0.45), (3, 0.22), (4, 0.12), (5, 0.06)))
    return s * env_ad(n, 0.003, 1.6) * vol


def bass(freq, dur, vol=0.32):
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * freq * 2 * t)
    return s * env_ad(n, 0.006, dur * 0.7) * vol


def pad(freqs, dur, vol=0.05):
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            s += signal.sawtooth(2 * np.pi * f * 2 ** (det / 12) * t)
    s = lowpass(s, 1400)
    a = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.6)
    return s * a * vol / len(freqs)


def shaker(vol=0.05):
    d = 0.06
    return highpass(noise(d), 6000) * env_ad(int(SR * d), 0.002, 0.018) * vol


def rim(vol=0.12):
    d = 0.05
    return bandpass(noise(d), 1500, 4000) * env_ad(int(SR * d), 0.0005, 0.008) * vol + \
        sine(1800, d) * env_ad(int(SR * d), 0.0005, 0.01) * vol * 0.5


def kick(vol=0.35):
    d = 0.18
    return sine(np.array([140, 45]), d) * env_ad(int(SR * d), 0.001, 0.07) * vol


def square(freq, dur, vol=0.08, duty=0.25):
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = (signal.square(2 * np.pi * freq * t, duty=duty))
    return lowpass(s, 5000) * env_ad(n, 0.002, dur * 0.8) * vol


def triangle(freq, dur, vol=0.2):
    n = int(SR * dur)
    t = np.arange(n) / SR
    return signal.sawtooth(2 * np.pi * freq * t, 0.5) * env_ad(n, 0.002, dur) * vol


def chip_hat(vol=0.04):
    d = 0.03
    return highpass(noise(d), 8000) * env_ad(int(SR * d), 0.0005, 0.008) * vol


def reverb(x, wet=0.22, length=1.6):
    n = int(SR * length)
    ir = RNG.standard_normal(n) * np.exp(-np.arange(n) / (SR * length / 5))
    ir = lowpass(ir, 6000)
    ir /= np.sqrt(np.sum(ir ** 2))
    y = signal.fftconvolve(x, ir)[:len(x)]
    return x * (1 - wet) + y * wet * 0.6


class Song:
    def __init__(self, bpm, bars, beats=4):
        self.spb = 60 / bpm
        self.n = int(SR * self.spb * beats * bars) + SR * 3
        self.L = np.zeros(self.n)
        self.R = np.zeros(self.n)

    def at(self, beat):
        return int(beat * self.spb * SR)

    def add(self, beat, s, pan=0.0):
        o = self.at(beat)
        e = min(self.n, o + len(s))
        self.L[o:e] += s[:e - o] * (1 - max(0, pan))
        self.R[o:e] += s[:e - o] * (1 + min(0, pan))

    def render(self, wet=0.22, loop_beats=None):
        L, R = reverb(self.L, wet), reverb(self.R, wet)
        if loop_beats:  # fold the tail back onto the start so the loop is seamless
            cut = self.at(loop_beats)
            tail = len(L) - cut
            L[:tail] += L[cut:]
            R[:tail] += R[cut:]
            L, R = L[:cut], R[:cut]
        st = np.stack([L, R], 1)
        st /= np.max(np.abs(st)) / 0.89
        return st


def melody_line(scale_notes, bars, beats_per_bar, rhythm, seed, lo, hi):
    rng = np.random.default_rng(seed)
    idx = len(scale_notes) // 2
    notes = []
    for bar in range(bars):
        for pos, length in rhythm[bar % len(rhythm)]:
            idx = int(np.clip(idx + rng.choice([-2, -1, -1, 0, 1, 1, 2]), 0, len(scale_notes) - 1))
            m = scale_notes[idx]
            while m < lo:
                m += 12
            while m > hi:
                m -= 12
            notes.append((bar * beats_per_bar + pos, length, m))
    return notes


def song_plaza():
    """Mellow bossa stroll, 100 bpm."""
    s = Song(100, 32)
    prog = [("F", "maj7"), ("E", "m7"), ("D", "m9"), ("C", "m7"), ("A#", "maj7"), ("A#", "m6"), ("A", "m7"), ("G", "m7")]
    second = [None, ("A", "7"), None, ("F", "7"), None, None, ("D", "7"), ("C", "7")]
    scale = [m for m in range(48, 90) if (m - 5) % 12 in (0, 2, 4, 5, 7, 9, 11)]
    rhythm = [[(0, 1.5), (1.5, 1), (2.5, 1.5)], [(0.5, 0.5), (1, 1), (2, 2)], [(0, 1), (1, 0.5), (1.5, 1.5), (3, 1)],
              [(0, 3)], [(0, 0.5), (0.5, 1), (1.5, 1), (2.5, 1.5)], [(1, 1), (2, 2)], [(0, 1.5), (1.5, 2.5)], [(0, 4)]]
    mel = melody_line(scale, 32, 4, rhythm, 3, 69, 86)
    for bar in range(32):
        for half, ch in ((0, prog[bar % 8]), (2, second[bar % 8] or prog[bar % 8])):
            root, notes = chord(*ch)
            b0 = bar * 4 + half
            if half == 2 and second[bar % 8] is None:
                pass
            for hit, ln in ((0, 0.6), (1.5 if half == 0 else 0.5, 0.5)):
                if half == 2 and hit > 1:
                    continue
                for k, m in enumerate(notes):
                    s.add(b0 + hit, epiano(midi_hz(m + 60), ln * s.spb * 2.2, 0.07), pan=-0.3 + k * 0.2)
            bf = midi_hz(root + 36)
            s.add(b0, bass(bf, 1.4 * s.spb))
            s.add(b0 + 1.5, bass(bf * 1.5, 0.5 * s.spb, 0.26))
        for e in range(8):
            s.add(bar * 4 + e * 0.5, shaker(0.035 if e % 2 else 0.05), pan=0.4)
        for p in (0, 0.75, 1.75, 2.5, 3.5) if bar % 2 == 0 else (0, 1, 2, 2.75):
            s.add(bar * 4 + p, rim(0.06), pan=-0.2)
        s.add(bar * 4, kick(0.25))
        s.add(bar * 4 + 2.5, kick(0.18))
    if True:
        for beat, ln, m in mel:
            if beat >= 32:
                s.add(beat, bell(midi_hz(m), ln * s.spb + 0.4, 0.09, 0.35), pan=0.15)
                s.add(beat, epiano(midi_hz(m), ln * s.spb + 0.3, 0.05), pan=0.15)
    return s.render(0.2, loop_beats=128)


def song_lounge():
    """Calm piano lounge, 72 bpm."""
    s = Song(72, 24)
    prog = [("D", "maj9"), ("B", "m9"), ("G", "maj7"), ("A", "6"), ("F#", "m7"), ("B", "m7"), ("E", "m9"), ("A", "sus2")]
    scale = [m for m in range(50, 92) if (m - 2) % 12 in (0, 2, 4, 6, 7, 9, 11)]
    rhythm = [[(0, 2), (2, 2)], [(1, 1), (2, 2)], [(0, 3)], [(0.5, 1.5), (2, 2)]]
    mel = melody_line(scale, 24, 4, rhythm, 11, 74, 88)
    for bar in range(24):
        root, notes = chord(*prog[bar % 8])
        s.add(bar * 4, pad([midi_hz(m + 48) for m in notes[:4]], 4 * s.spb + 0.5, 0.05))
        s.add(bar * 4, bass(midi_hz(root + 36), 3.6 * s.spb, 0.22))
        arp = [notes[i % len(notes)] + 60 for i in (0, 1, 2, 3, 2, 1, 2, 3)]
        for i, m in enumerate(arp):
            s.add(bar * 4 + i * 0.5, piano(midi_hz(m), 1.4, 0.09), pan=-0.35 + 0.1 * (i % 4))
    for beat, ln, m in mel:
        if beat >= 16:
            s.add(beat, bell(midi_hz(m), ln * s.spb + 1.0, 0.07, 0.6), pan=0.25)
    return s.render(0.3, loop_beats=96)


def song_pocket():
    """Cheerful chiptune, 126 bpm."""
    s = Song(126, 32)
    prog = [("C", ""), ("A", "m"), ("F", ""), ("G", ""), ("C", ""), ("E", "m"), ("F", ""), ("G", "")]
    scale = [m for m in range(60, 96) if m % 12 in (0, 2, 4, 7, 9)]
    rhythm = [[(0, 0.5), (0.5, 0.5), (1, 1), (2, 0.5), (2.5, 0.5), (3, 1)], [(0, 1.5), (1.5, 0.5), (2, 2)],
              [(0, 0.5), (0.5, 0.5), (1, 0.5), (1.5, 0.5), (2, 1), (3, 1)], [(0, 2), (2, 1), (3, 1)]]
    mel = melody_line(scale, 32, 4, rhythm, 21, 72, 91)
    for bar in range(32):
        root, notes = chord(*prog[bar % 8])
        for i in range(16):
            m = notes[i % 3] + 72 + (12 if (i // 3) % 2 else 0)
            s.add(bar * 4 + i * 0.25, square(midi_hz(m), 0.11, 0.03, 0.125), pan=-0.3)
        for i, p in enumerate((0, 1, 2, 3)):
            s.add(bar * 4 + p, triangle(midi_hz(root + 36 + (7 if i % 2 else 0)), 0.9 * s.spb, 0.2))
        for i in range(8):
            s.add(bar * 4 + i * 0.5, chip_hat(0.05 if i % 2 else 0.03), pan=0.3)
        s.add(bar * 4, kick(0.3))
        s.add(bar * 4 + 2, kick(0.3))
    for beat, ln, m in mel:
        if beat >= 16:
            s.add(beat, square(midi_hz(m), ln * s.spb * 0.9, 0.06, 0.5), pan=0.2)
    return s.render(0.12, loop_beats=128)


SONGS = {"Plaza Stroll": song_plaza, "Channel Lounge": song_lounge, "Pocket Breeze": song_pocket}


def write_music(out_dir, tmp_dir):
    os.makedirs(out_dir, exist_ok=True)
    for i, (title, fn) in enumerate(SONGS.items(), 1):
        wav = os.path.join(tmp_dir, f"{i:02d}.wav")
        st = fn()
        st = np.concatenate([st, st])  # two passes of the loop (~2-3 min)
        save_wav(wav, st.reshape(-1), stereo=True)
        ogg = os.path.join(out_dir, f"{i:02d} - {title}.ogg")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "4",
                        "-metadata", f"title={title}", "-metadata", "artist=esdeii", ogg], check=True)
        print("music:", title)
