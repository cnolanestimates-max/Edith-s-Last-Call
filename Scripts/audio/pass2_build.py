"""Audio pass 2 (2026-11-25): harder stings, punchier one-shots, a richer rolling house score.

Nothing here touches SourceArt/Audio.  Every new file is written to SourceArt/AudioPass2/new/<same name>.wav so the
old and new can be compared; `pass2_apply.py` copies the approved ones over the originals.

  <numpy python> pass2_build.py                 build everything
  <numpy python> pass2_build.py stings wheel    build groups (stings, wheel, gun, doors, thumps, steps, creaks, electric, foley, beds)
  <numpy python> pass2_build.py sting_hit       build single sounds

Why: measured on 2026-11-25, most stings, thumps, steps and the house score had 80 to 99 % of their energy under
200 Hz, which Cheyenne's laptop speakers do not play at all.  Each recipe keeps the low end for real speakers and adds
harmonics and recorded mid-range layers so the same weight is heard on small ones, then sets a known loudness.

Left alone on purpose (her rules): Edith's screams (the 2.75 s attack scream), whispers, moans, all breathing, voices,
crickets and crows, the music box, record, television, clock, flashlight shake and smack, the scare lead-ins.
"""
import os, sys
import numpy as np
import pass2_lib as L
import pass2_sources as S

OLD = S.ROOT + "/SourceArt/Audio"
NEW = S.ROOT + "/SourceArt/AudioPass2/new"
RECIPES = {}
GROUPS = {}


def recipe(group, ch=1):
    def deco(fn):
        RECIPES[fn.__name__] = (fn, ch)
        GROUPS.setdefault(group, []).append(fn.__name__)
        return fn
    return deco


def old(name, start=0.0, dur=None):
    return L.load(f"{OLD}/{name}.wav", start, dur)


def src(key, start=0.0, dur=None):
    return L.load(S.path(key), start, dur)


def trim(x, thresh=-34.0, lead=0.002):
    e = np.abs(x).max(axis=1)
    i = np.flatnonzero(e > e.max() * L.lin(thresh))
    return x[max(i[0] - L.secs(lead), 0):] if len(i) else x


def hit(key, i, tail=0.0, **kw):
    """The i-th separate hit in a library recording."""
    x = src(key, 0, 95)
    ev = L.events(x, kw.get("thresh", -26), kw.get("gap", 0.25), 0.04)
    return L.grab(x, ev, i, tail)


def loudest(x, dur):
    n = L.secs(dur)
    c = np.concatenate(([0.0], np.cumsum((x ** 2).sum(axis=1))))
    i = int(np.argmax(c[n:] - c[:-n]))
    return x[i:i + n]


def onsets(x, thresh=-22.0, gap=0.09):
    return [a for a, b, p in L.events(x, thresh, gap, 0.01, pre=0.0)]


def periodic(fn, x, pre=4.0):
    """Run a filter chain on a loop so that the seam stays seamless."""
    n = L.secs(pre)
    y = fn(np.concatenate([x[-n:], x, x[:n]]))
    return y[n:n + len(x)]


def tile_to(loop, k, n):
    """A seamless loop repeated k times and fitted to exactly n samples (a sample or two of stretch at most)."""
    y = np.tile(loop, (k, 1))
    return y if len(y) == n else L.signal.resample(y, n, axis=0)


def weight(x, target, harm=1.6, punch=2.0, top=900.0, keep=0.85, hpf=32.0, sat=2.0, roomwet=None, fc=170.0, gap=4.5):
    """The standard treatment for anything heavy: sub kept, harmonics added above it, attack lifted, level set."""
    x = L.hp(x, hpf, 2)
    if harm:
        x = L.bass_harm(x, fc, harm, top, keep)
    if punch:
        x = L.transient(x, punch)
    if sat:
        x = L.saturate(x, sat, 0.5)
    if roomwet is not None:
        x = L.room(x, roomwet)
    return L.to_loud(L.balance(x, gap), target)


def polish(x, target, punch=2.0, air=0.0, hpf=60.0, roomwet=None, comp=False):
    """The standard treatment for small foley: clean the bottom, sharpen the attack, set the level."""
    x = L.hp(x, hpf, 2)
    if comp:
        x = L.compress(x, L.peak(x) - 14, 3.0, 0.004, 0.09)
    if punch:
        x = L.transient(x, punch)
    if air:
        x = L.exciter(x, 3000, air)
    if roomwet is not None:
        x = L.room(x, roomwet)
    return L.to_loud(x, target)


def same_len(x, name, fout=0.05):
    n = len(old(name))
    x = x[:n] if len(x) >= n else L.pad(x, 0, (n - len(x)) / L.SR)
    return L.fade(x, 0.0, fout)


# =================================================================================================== stings (2D, music)
@recipe("stings", 2)
def sting_hit():
    """The jump-scare hit under her scream.  Was a soft low thud (mid band -21 dB and falling)."""
    sm = trim(src("smash"))
    nb = L.fade(L.bell(L.hp(trim(src("noisebox_36", 0, 4.2)), 70), 1200, 3, 0.8), 0.0, 1.4)
    bm = L.decay(L.bass_harm(trim(src("boom_011", 0, 4.2)), 170, 1.7, 900, 0.8), 2.0)
    dj = trim(src("drop_jump"))
    sq = L.fade(L.cut(L.pitch(src("ice_squeal"), 0.62), 0.05, 2.5), 0.01, 1.5)
    ck = hit("stick_impact", 0, 0.08)
    x = L.mix([(sm, 0, 0), (nb, 0, -2), (bm, 0, -5), (dj, 0, -6), (sq, 0.01, -15), (L.to_peak(ck, -3), 0, -5)])
    x = L.saturate(L.transient(L.hp(x, 32), 3.0), 4.0, 0.5)
    x = L.reverb(x, 1.6, -15, 0.012, 160, 5000, seed=5)
    x = L.fade(x[:L.secs(3.3)], 0.0, 0.9)
    return L.to_loud(L.balance(x, 2.5, mono=False), -8.0, -1.0, mono=False)


@recipe("stings", 2)
def sting_low():
    """Five seconds of low dread.  Was 99 % under 200 Hz: silent on a laptop."""
    ds = L.bass_harm(trim(src("drop_slow"))[:L.secs(5.2)], 170, 2.0, 900, 0.7)
    br = L.lp(trim(src("braam_32", 0, 6))[:L.secs(5.2)], 1500)
    ms = L.bass_harm(L.pitch(trim(src("metal_scrape_low")), 1.5), 190, 1.2, 1000, 0.8)
    bm = L.decay(L.bass_harm(trim(src("boom_075", 0, 4)), 170, 1.6, 900, 0.8), 1.6)
    x = L.mix([(ds, 0, 0), (br, 0, 6), (ms, 0.2, -5), (bm, 0, -7)])
    x = L.reverb(L.saturate(L.hp(x, 32), 3.0, 0.4), 1.8, -16, 0.02, 150, 4000, seed=8)
    x = L.fade(x[:L.secs(5.0)], 0.02, 1.1)
    return L.to_loud(L.balance(x, 4.0, mono=False), -12.0, -1.5, mono=False)


@recipe("stings", 2)
def sting_rise():
    """A rise that breaks at 2.1 s (the old one peaked there too), then falls away."""
    T = 2.1
    up1 = L.rev(L.bass_harm(trim(src("boom_214", 0, 4))[:L.secs(T)], 170, 1.6, 900, 0.8))
    up2 = L.rev(trim(src("noisebox_10", 0, 4))[:L.secs(T)])
    bow = L.bass_harm(src("bowed_screech", 0.2, T), 170, 2.0, 900, 0.7)
    scr = L.fade(src("psycho", 28.0, T), T * 0.98, 0.0, 2.5)
    for v in (up1, up2, bow):
        v *= (np.linspace(0, 1, len(v)) ** 1.3)[:, None]
    sm = trim(src("smash"))
    dm = L.fade(trim(src("drop_med"))[:L.secs(1.9)], 0.0, 1.0)
    nb = L.fade(L.hp(trim(src("noisebox_36", 0, 3)), 70)[:L.secs(1.9)], 0.0, 1.2)
    x = L.mix([(up1, 0, -3), (up2, 0, -5), (bow, 0, -1), (scr, 0, -9), (sm, T, -3), (dm, T, -4), (nb, T, -6)])
    x = L.reverb(L.saturate(L.hp(x, 32), 3.0, 0.4), 1.3, -15, 0.012, 160, 5000, seed=9)
    x = L.fade(x[:L.secs(4.0)], 0.05, 1.0)
    return L.to_loud(L.balance(x, 3.0, mono=False), -9.0, -1.0, mono=False)


@recipe("stings", 2)
def sting_soft():
    """The quiet one for a first sight of her: a bowed-metal swell cresting at 2 s.  Was 94 % sub-bass."""
    bow = L.bass_harm(src("bowed_screech", 0.2, 4.2), 170, 2.4, 950, 0.6)
    air = L.fade(src("drone_tension", 10.5, 4.2), 1.8, 1.8)
    sq = L.fade(L.cut(L.pitch(src("ice_squeal"), 0.5), 0.1, 3.4), 1.5, 1.6)
    x = L.mix([(bow, 0, 0), (air, 0, -3), (sq, 0.4, -22)])
    x = L.reverb(L.hp(x, 32), 1.5, -14, 0.02, 160, 4500, seed=4)
    x = L.fade(x[:L.secs(4.0)], 0.3, 1.2)
    return L.to_loud(L.balance(x, 2.5, mono=False), -12.0, -2.0, mono=False)


@recipe("stings", 2)
def sting_braam():
    o = old("sting_braam")
    b2 = L.fade(trim(src("braam_67", 0, 4))[:L.secs(2.85)], 0.3, 0.4)
    x = L.mix([(L.bass_harm(o, 170, 1.4, 900, 0.85), 0, 0), (b2, 0.25, 2)])
    return L.to_loud(L.balance(same_len(x, "sting_braam", 0.2), 3.5, mono=False), -10.0, -1.0, mono=False)


@recipe("stings", 2)
def sting_swell():
    x = L.bell(L.bass_harm(old("sting_swell"), 170, 1.3, 900, 0.85), 900, 2, 0.8)
    return L.to_loud(L.balance(x, 2.5, mono=False), -11.0, -1.5, mono=False)


# =================================================================================================== the wheelchair in the bath
@recipe("wheel")
def wheel_on_boards():
    """Rolling.  Was filtered noise; now a real wooden roll, a dragged runner, board seams and the old rumble under it.
    The game loops it while the chair moves and plays it at 0.9 to 1.3 speed, so it is built to loop without a seam."""
    n0 = len(old("wheel_on_boards")); xf = 0.3
    n = n0 + L.secs(xf)
    rum = L.bass_harm(old("wheel_on_boards"), 200, 1.5, 900, 0.9)
    rum = np.concatenate([rum, rum])[:n]                                    # the old file is itself a loop
    roll = L.pitch(trim(src("shaker_roll")), 0.6)
    roll = np.concatenate([roll, L.rev(roll)])[:n]
    drag = L.hp(L.cut(src("sleigh"), 0.3, n / L.SR + 0.2), 200)[:n]
    layers = [(rum, 0, -4), (L.lp(roll, 6000), 0, -2), (drag, 0, 3)]
    seam = [S.path(f"ken:impactWood_light_00{i}") for i in (0, 2, 4, 1, 3, 0)]
    for i, t in enumerate((0.52, 1.05, 1.63, 2.19, 2.84, 3.41)):
        c = L.bass_harm(trim(L.load(seam[i])), 170, 1.5, 800, 0.8)
        layers.append((L.to_peak(c, -11 - 2 * (i % 2)), t, 0))
        layers.append((L.to_peak(c, -18), t + 0.085, 0))                   # the second wheel crosses the same seam
    x = L.mix(layers)[:n]
    x = L.compress(L.hp(x, 45), -20, 2.5, 0.01, 0.15)
    return L.to_loud(L.loop_xfade(x, xf), -15.0)


@recipe("wheel")
def wheel_axle_rub():
    """One squeak per turn of the wheel.  Was a synthesized 840 Hz tone; now a real seat squeak with a dry metal edge."""
    n = len(old("wheel_axle_rub"))
    sq = loudest(src("creaky_seat", 2.0, 1.6), 0.36)
    ic = loudest(L.pitch(src("ice_squeal"), 1.25), 0.30)
    x = L.mix([(L.to_peak(L.fade(sq, 0.02, 0.1), -3), 0, 0), (L.to_peak(L.fade(ic, 0.03, 0.12), -3), 0.03, -9)])
    x = L.fade(L.hp(x, 300)[:n], 0.01, 0.09)
    return L.to_loud(L.pad(x, 0, max(n - len(x), 0) / L.SR), -15.0)


@recipe("wheel")
def wheel_baseboard():
    """The chair runs into the baseboard: wood on wood, the frame rattling after it."""
    o = L.bass_harm(old("wheel_baseboard"), 170, 2.0, 900, 0.85)
    ck = hit("stick_impact", 3, 0.12)
    wd = trim(L.load(S.path("ken:impactWood_heavy_002")))
    rat = L.fade(L.hp(src("shield_spin", 1.0, 0.45), 500), 0.01, 0.3)
    x = L.mix([(o, 0, 0), (L.to_peak(ck, -2), 0, 0), (L.to_peak(wd, -4), 0.004, 0), (L.to_peak(rat, -12), 0.06, 0)])
    x = L.room(L.transient(L.hp(x, 35), 4.0), -14, 0.3)
    return L.to_loud(L.balance(L.fade(x[:L.secs(1.25)], 0, 0.25), 3.5), -11.5)


@recipe("wheel")
def wheel_sidefall():
    """The chair goes over: frame hits the floor, a pipe rings, a wheel spins down."""
    o = L.bass_harm(old("wheel_sidefall"), 170, 2.0, 900, 0.85)
    wd = L.bass_harm(trim(src("wood_hit_dark", 2.2, 1.2)), 170, 1.6, 900, 0.8)
    mt = trim(L.load(S.path("ken:impactMetal_heavy_001")))
    pp = L.pitch(trim(src("pipe_concrete")), 0.6)
    spin = L.fade(L.hp(src("shield_spin", 31.9, 1.4), 350), 0.02, 0.5)
    x = L.mix([(o, 0, 0), (L.to_peak(wd, -3), 0, 0), (L.to_peak(mt, -6), 0.01, 0), (L.to_peak(pp, -11), 0.02, 0),
               (L.to_peak(spin, -10), 0.14, 0)])
    x = L.room(L.transient(L.hp(x, 35), 4.0), -13, 0.35)
    return L.to_loud(L.balance(L.fade(x[:L.secs(1.6)], 0, 0.4), 3.5), -10.0)


# =================================================================================================== the pistol
@recipe("gun")
def gun_shot():
    """Was a thin click (energy centred at 5.6 kHz, no body).  Now a crack, a real blast under it and the room answering."""
    o = old("gun_shot")                                  # its loudest click came 0.18 s late, after two small ones
    i = int(np.argmax(np.abs(o).max(axis=1)))
    crack = L.fade(L.hp(o[max(i - L.secs(0.002), 0):i + L.secs(0.11)], 300), 0.0, 0.06)
    blast = L.pitch(hit("fireworks_near", 3, 0.5, thresh=-18), 1.3)
    thud = L.bass_harm(hit("punch_body", 0, 0.1), 170, 1.5, 900, 0.9)
    snap = hit("stick_impact", 6, 0.05)
    x = L.mix([(L.to_peak(crack, -2), 0, 0), (L.to_peak(blast, -1), 0, 0), (L.to_peak(thud, -4), 0, 0), (L.to_peak(snap, -6), 0, 0)])
    x = L.transient(L.hp(x, 40), 4.0)
    x = L.reverb(x, 0.9, -11, 0.008, 200, 5500, seed=12, early=((0.011, 0.5), (0.019, 0.4), (0.031, 0.3), (0.047, 0.22)))
    x = L.clip_soft(L.to_peak(x, 2.0), 0.0, -0.8)
    return L.to_loud(L.fade(x[:L.secs(1.8)], 0, 0.6), -9.5)


@recipe("gun")
def gun_empty():
    x = L.mix([(old("gun_empty"), 0, 0), (L.to_peak(L.lp(trim(src("latch_thunk")), 5000), -6), 0, 0)])
    return same_len(polish(x, -19.0, 4.0), "gun_empty")


@recipe("gun")
def gun_reload():
    return polish(old("gun_reload"), -19.0, 4.0, 0.2, 120)


@recipe("gun")
def bullet_impact_01():
    return weight(old("bullet_impact_01"), -14.0, 1.2, 3.0)


# =================================================================================================== doors
@recipe("doors")
def door_open_01():
    return same_len(weight(old("door_open_01"), -17.0, 0.7, 2.0, hpf=50, roomwet=-17), "door_open_01")


@recipe("doors")
def door_close_01():
    """Was a faint click.  Now the click, a latch and the door meeting its frame."""
    o = old("door_close_01")
    t = onsets(o, -12)[0]
    wd = L.bass_harm(trim(L.load(S.path("ken:impactWood_medium_001"))), 170, 1.2, 900, 0.9)
    cs = trim(src("case_closed"))
    x = L.mix([(o, 0, 0), (L.to_peak(wd, -5), t, 0), (L.to_peak(cs, -8), t + 0.012, 0)])
    return same_len(L.to_loud(L.room(L.transient(L.hp(x, 45), 3.0), -16), -16.5), "door_close_01")


@recipe("doors")
def door_locked_01():
    """A locked knob tried twice.  Was barely audible (-27 LUFS)."""
    o = old("door_locked_01")
    r1 = hit("suitcase_lock", 1, 0.05, gap=0.2)
    r2 = hit("suitcase_lock", 6, 0.05, gap=0.2)
    wd = L.bass_harm(trim(L.load(S.path("ken:impactWood_light_002"))), 170, 1.0, 900, 0.9)
    ts = onsets(o, -14, 0.15)[:2] or [0.05]
    lay = [(o, 0, 3)]
    for i, t in enumerate(ts):
        lay += [(L.to_peak((r1, r2)[i % 2], -5), t, 0), (L.to_peak(wd, -9), t + 0.01, 0)]
    x = L.mix(lay)
    return same_len(L.to_loud(L.room(L.transient(L.hp(x, 60), 3.0), -17), -16.5), "door_locked_01")


@recipe("doors")
def door_unlock():
    o = old("door_unlock")
    t = (onsets(o, -12) or [0.05])[0]
    key = hit("antique_lock", 3, 0.05, gap=0.2)
    th = trim(src("latch_thunk"))
    x = L.mix([(o, 0, 0), (L.to_peak(key, -7), t, 0), (L.to_peak(th, -6), t + 0.02, 0)])
    return same_len(L.to_loud(L.room(L.transient(L.hp(x, 60), 3.0), -17), -17.0), "door_unlock")


@recipe("doors")
def door_slam():
    """A slam that shakes the wall: the old slam, a dark heavy wooden hit, a plank, the latch jumping."""
    o = old("door_slam")
    t = (onsets(o, -10) or [0.02])[0]
    wd = L.bass_harm(trim(src("wood_hit_dark", 20.8, 1.3)), 170, 1.6, 900, 0.85)
    pl = trim(L.load(S.path("ken:impactWood_heavy_000")))
    la = hit("suitcase_open", 1, 0.05, gap=0.2)
    x = L.mix([(L.bass_harm(o, 170, 1.3, 900, 0.9), 0, 0), (L.to_peak(wd, -2), t, 0), (L.to_peak(pl, -5), t + 0.003, 0),
               (L.to_peak(la, -13), t + 0.03, 0)])
    x = L.room(L.transient(L.hp(x, 35), 4.0), -13, 0.4)
    return same_len(L.to_loud(L.balance(x, 3.5), -10.5), "door_slam", 0.2)


@recipe("doors")
def door_creak_long():
    x = L.bell(L.bass_harm(L.hp(old("door_creak_long"), 80), 190, 1.1, 1000, 0.6), 1200, 4, 0.8)
    x = L.compress(L.exciter(x, 2500, 0.25), L.peak(x) - 14, 2.5, 0.01, 0.15)
    return L.to_loud(x, -14.0)


def _far(x, target, f=1100.0, t60=0.8):
    x = L.reverb(L.through_wall(x, f), t60, -8, 0.02, 150, 1800, seed=21)
    return L.to_loud(x, target)


@recipe("doors")
def door_far_01():
    return same_len(_far(door_close_01(), -19.0), "door_far_01", 0.3)


@recipe("doors")
def door_far_02():
    return same_len(_far(door_creak_long(), -18.0), "door_far_02", 0.3)


@recipe("doors")
def door_far_03():
    return same_len(_far(door_slam(), -15.0, 900), "door_far_03", 0.3)


@recipe("doors")
def trunk_open():
    return weight(old("trunk_open"), -17.0, 0.8, 2.0, hpf=50)


@recipe("doors")
def car_door():
    o = old("car_door")
    ts = onsets(o, -12, 0.2)
    lay = [(o, 0, 0)]
    for t in ts[:2]:
        lay.append((L.to_peak(L.bass_harm(hit("punch_body", 2, 0.08), 170, 1.5, 900, 0.9), -7), t, 0))
    return same_len(L.to_loud(L.transient(L.hp(L.mix(lay), 40), 3.0), -15.0), "car_door")


# =================================================================================================== knocks, thumps, falls
@recipe("thumps")
def knock():
    o = old("knock")
    wd = L.bass_harm(trim(L.load(S.path("ken:impactWood_medium_003"))), 170, 1.2, 900, 0.9)
    lay = [(L.bass_harm(o, 170, 0.8, 900, 0.9), 0, 0)]
    for t in onsets(o, -16, 0.1)[:6]:
        lay.append((L.to_peak(wd, -9), t, 0))
    return same_len(L.to_loud(L.room(L.transient(L.hp(L.mix(lay), 45), 3.0), -17), -13.0), "knock")


def _w(name, target, harm=1.8, punch=2.0, **kw):
    def fn():
        return same_len(weight(old(name), target, harm, punch, **kw), name)
    fn.__name__ = name
    return fn


for _n, _t, _h, _p in (
        ("knock_far_01", -13.0, 1.8, 2.0), ("knock_far_02", -14.5, 1.2, 2.0),
        ("thump_far_01", -12.0, 2.0, 2.0), ("thump_far_02", -13.0, 2.0, 2.0), ("thump_heavy", -10.5, 2.0, 3.0),
        ("bang_far_01", -17.0, 1.8, 1.0), ("wood_hit_far_01", -14.0, 2.0, 2.0),
        ("steps_above_01", -18.0, 2.4, 2.0), ("steps_above_02", -18.0, 2.4, 2.0), ("steps_above_03", -18.0, 2.4, 2.0),
        ("ceiling_thump_01", -17.0, 1.5, 0.0), ("ceiling_thump_02", -17.0, 1.5, 0.0), ("ceiling_thump_03", -17.0, 2.0, 0.0),
        ("ceiling_boot_step_01", -16.0, 2.2, 0.0), ("ceiling_boot_step_02", -18.0, 2.0, 0.0), ("ceiling_boot_step_03", -16.0, 2.2, 0.0),
        ("ceiling_boot_step_04", -16.0, 2.0, 0.0), ("ceiling_boot_step_05", -16.0, 2.2, 0.0), ("ceiling_boot_step_06", -17.0, 2.0, 0.0),
        ("shelf_stair_step_01", -14.0, 2.0, 0.0), ("shelf_stair_step_02", -14.0, 2.0, 0.0), ("shelf_stair_step_03", -14.0, 2.0, 0.0),
        ("her_step_01", -18.5, 1.8, 1.0), ("her_step_02", -18.0, 1.8, 1.0), ("her_step_03", -18.5, 1.8, 1.0), ("her_step_04", -18.0, 1.8, 1.0),
        ("frame_fall", -12.5, 1.3, 3.0)):
    recipe("thumps")(_w(_n, _t, _h, _p))


@recipe("thumps")
def body_fall():
    o = old("body_fall")
    t = (onsets(o, -10) or [0.02])[0]
    th = L.bass_harm(hit("punch_body", 1, 0.1), 170, 1.6, 900, 0.9)
    x = L.mix([(L.bass_harm(o, 170, 1.3, 900, 0.9), 0, 0), (L.to_peak(th, -3), t, 0)])
    return same_len(L.to_loud(L.balance(L.room(L.transient(L.hp(x, 35), 3.0), -15), 4.0), -13.0), "body_fall")


# =================================================================================================== footsteps
def _step_wood(i, boot, target=-21.5, p=1.0, hollow=0.0):
    o = L.bass_harm(L.hp(old(f"step_wood_0{i}"), 55), 170, 2.0, 800, 0.85)
    b = hit("boots_wood", boot, 0.16, thresh=-24, gap=0.2)
    b = L.pitch(L.hp(b, 120), p)
    x = L.mix([(L.to_peak(o, -3), 0, 0), (L.to_peak(L.fade(b, 0, 0.12), -9), 0.003, 0)])
    if hollow:
        x = L.bell(x, 300, hollow, 1.0)
    x = L.room(L.transient(x, 2.0), -19, 0.22)
    return L.to_loud(L.fade(x[:L.secs(0.34)], 0, 0.1), target)


for _i, _b, _p in ((1, 0, 1.0), (2, 2, 0.96), (3, 3, 1.04), (4, 0, 0.93), (5, 2, 1.08)):
    def _f(i=_i, b=_b, p=_p):
        return _step_wood(i, b, -23.0, p)
    _f.__name__ = f"step_wood_0{_i}"
    recipe("steps")(_f)


@recipe("steps")
def step_stairs_01():
    return _step_wood(2, 0, -22.5, 0.9, 3.0)


@recipe("steps")
def step_stairs_02():
    return _step_wood(4, 3, -22.5, 0.86, 3.0)


for _i in (1, 2, 3, 4):
    def _f(i=_i):
        x = L.bass_harm(L.hp(old(f"step_stone_0{i}"), 60), 170, 1.2, 900, 0.9)
        x = L.room(L.pad(L.transient(x, 2.0), 0, 0.12), -12, 0.28, seed=30 + i)
        return L.to_loud(L.fade(x[:L.secs(0.3)], 0, 0.12), -22.5)
    _f.__name__ = f"step_stone_0{_i}"
    recipe("steps")(_f)

for _i in (1, 2, 3, 4):
    def _f(i=_i):
        o = old(f"step_gravel_0{i}")
        cr = L.pitch(trim(L.load(S.path(f"ken:footstep_snow_00{i}"))), 1.18)
        tw = hit("twigs", (1, 4, 8, 2)[i - 1], 0.05, thresh=-22, gap=0.3)
        x = L.mix([(L.to_peak(o, -4), 0, 0), (L.to_peak(L.hp(cr, 300), -5), 0.004, 0), (L.to_peak(L.hp(tw, 1500), -15), 0.01, 0)])
        x = L.exciter(L.transient(L.hp(x, 110), 2.0), 3000, 0.2)
        return same_len(L.to_loud(x, -22.5), f"step_gravel_0{i}")
    _f.__name__ = f"step_gravel_0{_i}"
    recipe("steps")(_f)


# =================================================================================================== creaks, groans, scrapes
for _n, _t, _h in (("creak_01", -17.0, 1.3), ("creak_02", -17.5, 0.0), ("creak_03", -16.0, 1.3), ("creak_04", -17.5, 0.0),
                   ("house_groan_01", -15.0, 2.2), ("house_groan_02", -15.0, 1.4),
                   ("drag_floor", -13.0, 1.6), ("shelf_scrape", -14.0, 1.3)):
    def _f(n=_n, t=_t, h=_h):
        x = L.hp(old(n), 45)
        if h:
            x = L.bass_harm(x, 180, h, 1000, 0.7)
        x = L.compress(x, L.peak(x) - 14, 2.5, 0.008, 0.14)
        return same_len(L.to_loud(L.room(x, -19, 0.3), t), n)
    _f.__name__ = _n
    recipe("creaks")(_f)

for _n, _t in (("chair_scrape", -17.0), ("chair_creak_01", -18.0), ("scratch_wall_01", -21.0), ("scratch_wall_02", -21.0),
               ("scratch_wall_03", -20.5), ("scratch_wall_04", -20.0), ("bath_drain", -21.0)):
    def _f(n=_n, t=_t):
        x = L.hp(old(n), 60)
        x = L.bass_harm(x, 180, 1.0, 1000, 0.8) if L.low_share(x) > 40 else x
        x = L.compress(x, L.peak(x) - 16, 3.0, 0.005, 0.12)
        return same_len(L.to_loud(x, t), n)
    _f.__name__ = _n
    recipe("creaks")(_f)

for _n, _t, _h in (("wind_gust_01", -19.5, 1.6), ("wind_gust_02", -20.5, 1.6), ("wind_gust_03", -19.5, 2.6)):
    def _f(n=_n, t=_t, h=_h):
        x = L.bass_harm(L.hp(old(n), 40), 190, h, 1100, 0.7)
        return same_len(L.to_loud(x, t), n, 0.5)
    _f.__name__ = _n
    recipe("creaks")(_f)


# =================================================================================================== electric
@recipe("electric")
def bulb_die():
    """A light going out.  Was a 80 Hz hum nobody could hear on small speakers: now a short arc, a fizz and the thump."""
    o = L.bass_harm(L.hp(old("bulb_die"), 30), 160, 2.6, 900, 0.9)
    arc = L.decay(L.fade(trim(src("arc"))[:L.secs(0.38)], 0.0, 0.2), 0.3)
    fz = L.fade(L.hp(src("buzz", 0.4, 0.7), 400), 0.01, 0.6, 2.0)
    gl = L.pitch(trim(L.load(S.path("ken:impactGlass_light_001"))), 1.5)
    x = L.mix([(L.to_peak(o, -5), 0, 0), (L.to_peak(arc, -8), 0, 0), (L.to_peak(fz, -16), 0.03, 0), (L.to_peak(gl, -18), 0.02, 0)])
    return same_len(L.to_loud(L.room(L.hp(x, 35), -18, 0.3), -19.0), "bulb_die", 0.3)


@recipe("electric")
def bulb_pop():
    o = old("bulb_pop")
    gl = trim(L.load(S.path("ken:impactGlass_light_003")))
    th = L.bass_harm(trim(L.load(S.path("ken:impactSoft_medium_001"))), 170, 1.2, 900, 0.9)
    x = L.mix([(o, 0, 0), (L.to_peak(gl, -9), 0.004, 0), (L.to_peak(th, -8), 0, 0)])
    return same_len(L.to_loud(L.transient(L.hp(x, 60), 3.0), -16.0), "bulb_pop")


@recipe("electric")
def bulb_buzz():
    return L.to_loud(L.hp(old("bulb_buzz"), 150), -23.5)


@recipe("electric")
def switch_click():
    x = L.mix([(old("switch_click"), 0, 0), (L.to_peak(L.lp(trim(src("latch_thunk")), 3500), -10), 0.0, 0)])
    return same_len(polish(x, -21.0, 3.0, 0.0, 120, -20), "switch_click", 0.03)


@recipe("electric")
def flashlight_click():
    return polish(old("flashlight_click"), -20.0, 2.0, 0.0, 150)


# =================================================================================================== small foley
@recipe("foley")
def pickup():
    return polish(old("pickup"), -20.0, 2.0, 0.0, 100)


@recipe("foley")
def paper():
    return polish(old("paper"), -19.0, 1.0, 0.15, 150)


@recipe("foley")
def phone_pickup():
    o = old("phone_pickup")
    t = (onsets(o, -12) or [0.05])[0]
    hs = hit("phone_handset", 1, 0.08, gap=0.3)
    x = L.mix([(o, 0, 0), (L.to_peak(hs, -4), t, 0)])
    return same_len(polish(x, -18.0, 3.0, 0.0, 90, -18), "phone_pickup")


@recipe("foley")
def phone_ring():
    """Her dead landline.  Had 60 % of its energy under 200 Hz and a dull bell: cleaned, brightened, brought forward."""
    x = L.hp(old("phone_ring"), 380, 4)
    x = L.bell(L.bell(x, 2300, 4, 1.0), 900, 2, 1.0)
    x = L.compress(L.exciter(x, 3000, 0.3), L.peak(x) - 12, 3.0, 0.003, 0.08)
    return L.to_loud(L.room(x, -17, 0.35), -14.0)


# =================================================================================================== loops: the house score and beds (stereo)
@recipe("beds", 2)
def music_house():
    """The main indoor score.  The approved 162 s piece stays as the core; around it now roll slow bowed-metal waves,
    an airy tension layer that breathes, and harmonics of the bass.  Everything repeats on the same 162 s so it loops."""
    core = old("music_house")
    n = len(core); T = n / L.SR
    core = periodic(lambda v: L.bass_harm(v, 160, 1.2, 800, 1.0), core)
    out = core.copy()
    # six waves, one every 27 s, each a different pitch and side
    unit = T / 6
    for i, (p, pan, g) in enumerate(((1.0, -0.4, -3), (0.75, 0.5, -2), (1.26, 0.2, -5), (0.84, -0.6, -2), (1.12, 0.6, -4), (0.67, -0.1, -1))):
        w = L.pitch(src("bowed_screech", 0.2, 19.0), p)
        w = L.bass_harm(w, 170, 2.6, 950, 0.4)
        w = L.fade(w[:L.secs(min(len(w) / L.SR, 22.0))], 2.5, 9.0)
        w = L.reverb(w, 3.0, -9, 0.03, 150, 3500, seed=40 + i)
        w = w * np.array([[1 - max(pan, 0) * 0.7, 1 + min(pan, 0) * 0.7]])
        a = L.secs(unit * i + 6.0)
        idx = (a + np.arange(len(w))) % n
        np.add.at(out, idx, w * L.lin(g + L.integrated(core) - L.integrated(w)))
    # air: 54 s of the tension drone, folded into a loop, three times round, breathing on a 40.5 s cycle
    air = L.loop_xfade(L.lp(src("drone_tension", 4.0, T / 3 + 6.0), 3200), 6.0)
    air = tile_to(air, 3, n)
    t = np.arange(n) / L.SR
    breath = L.lin(3.5 * np.sin(2 * np.pi * t / (T / 4)) + 2.0 * np.sin(2 * np.pi * t / (T / 7) + 1.0))
    out += air * breath[:, None] * L.lin(-9 + L.integrated(core) - L.integrated(air))
    # a slow floor under it: 27 s of dark room, six times round
    fl = L.loop_xfade(L.bass_harm(src("dark_industrial", 1.0, unit + 4.0), 150, 1.6, 700, 0.8), 4.0)
    fl = tile_to(fl, 6, n)
    swell = L.lin(3.0 * np.sin(2 * np.pi * t / (T / 5) + 2.0))
    out += fl * swell[:, None] * L.lin(-11 + L.integrated(core) - L.integrated(fl))
    out = periodic(lambda v: L.compress(L.balance(v, 6.0, mono=False), -22, 1.6, 0.05, 0.6), out)
    out *= L.lin(-21.0 - L.integrated(out))
    return L.limit(out, -3.5)


@recipe("beds", 2)
def music_stalk():
    """The hunt.  99.8 % of it sat under 200 Hz.  The same loop is now doubled one, two and three octaves up (each
    copy is the loop played 2, 4 and 8 times faster, so they still meet at the seam), which a laptop can play."""
    o = old("music_stalk")
    n = len(o)
    x = periodic(lambda v: L.bass_harm(v, 150, 0.8, 750, 1.0), o, 2.0)
    X = np.fft.rfft(o, axis=0)
    for k, g in ((2, -5.0), (4, -9.0), (8, -15.0)):
        Y = np.zeros_like(X)
        m = (len(X) - 1) // k
        Y[:m * k + 1:k] = X[:m + 1]                    # the loop k times over in the same length: exactly periodic
        x = x + np.fft.irfft(Y, n, axis=0) * L.lin(g)
    x *= L.lin(-21.5 - L.integrated(x))
    return L.limit(x, -3.0)


@recipe("beds", 2)
def music_drone():
    o = old("music_drone")
    x = periodic(lambda v: L.bass_harm(v, 160, 1.0, 800, 1.0), o)
    x *= L.lin(-22.5 - L.integrated(x))
    return L.limit(x, -4.0)


@recipe("beds", 2)
def amb_cellar():
    o = old("amb_cellar")
    x = periodic(lambda v: L.bass_harm(v, 160, 1.4, 800, 1.0), o)
    x *= L.lin(-29.0 - L.integrated(x))
    return L.limit(x, -8.0)


# =================================================================================================== run
def build(names):
    rows = []
    for nm in names:
        fn, ch = RECIPES[nm]
        try:
            x = fn()
        except Exception as exc:
            import traceback
            print(f"{nm}: FAILED {exc}\n{traceback.format_exc()}")
            continue
        L.write(f"{NEW}/{nm}.wav", x, ch)
        o = old(nm) if os.path.exists(f"{OLD}/{nm}.wav") else None
        m = ch == 1
        row = (nm, len(x) / L.SR, L.peak(x), L.loud(x, m), L.loud_small(x, m))
        if o is not None:
            row += (len(o) / L.SR, L.peak(o), L.loud(o, m), L.loud_small(o, m))
        rows.append(row)
        if o is not None:
            print(f"{nm:22s} {row[5]:6.2f}s pk {row[6]:5.1f} full {row[7]:6.1f} laptop {row[8]:6.1f}   ->   {row[1]:6.2f}s pk {row[2]:5.1f} full {row[3]:6.1f} laptop {row[4]:6.1f}   (full {row[3] - row[7]:+.1f}, laptop {row[4] - row[8]:+.1f} dB)", flush=True)
        else:
            print(f"{nm:22s} new: {row[1]:.2f}s pk {row[2]:.1f} full {row[3]:.1f} laptop {row[4]:.1f}", flush=True)
    return rows


if __name__ == "__main__":
    want = sys.argv[1:] or list(GROUPS)
    names = []
    for w in want:
        names += GROUPS.get(w, [w])
    build(names)
