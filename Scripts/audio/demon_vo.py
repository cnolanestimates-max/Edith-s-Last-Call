"""Present-day Edith does not speak with one voice (Cheyenne: 'layer her voice on top of itself, darker, deeper, more
sinister, like three or four or ten voices talking at once').  Rebuilds VO/<id>.wav for every m_* line from the clean
takes in VO_dry (which are kept), except the memories (m_mem*) and her last 'thank you' (m_end): those stay human.

  python demon_vo.py            all her lines
  python demon_vo.py m_fin1     just these ids
No paid generation: ffmpeg only."""
import glob, os, subprocess, sys

ROOT = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Audio"
DRY, OUT = ROOT + "/VO_dry", ROOT + "/VO"
HUMAN = ("m_mem", "m_end")
# (pitch ratio, delay ms, gain): herself, two lower voices, something very deep under them, and a thin high one that is late
LAYERS = [(1.00, 0, 0.85), (0.80, 22, 0.80), (0.67, 41, 0.75), (0.50, 63, 0.55), (1.26, 78, 0.28), (0.90, 115, 0.35)]


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def atempo(f):
    """atempo only takes 0.5..2.0 per stage."""
    out = []
    while f > 2.0:
        out.append("atempo=2.0"); f /= 2.0
    while f < 0.5:
        out.append("atempo=0.5"); f /= 0.5
    out.append("atempo=%.5f" % f)
    return ",".join(out)


def demon(vid):
    src = f"{DRY}/{vid}.wav"
    if not os.path.exists(src):
        return False
    n = len(LAYERS)
    parts = [f"[0]aresample=48000,silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.05,asplit={n}" + "".join(f"[s{i}]" for i in range(n))]
    for i, (p, d, g) in enumerate(LAYERS):
        chain = f"[s{i}]"
        chain += f"asetrate=48000*{p:.3f},aresample=48000,{atempo(1.0 / p)}," if abs(p - 1.0) > 1e-3 else ""
        if p < 0.6:
            chain += "lowpass=f=1800,"
        if p > 1.1:
            chain += "highpass=f=900,"
        chain += f"adelay={d}:all=1,volume={g}[l{i}]"
        parts.append(chain)
    tail = "amix=inputs=%d:normalize=0,acompressor=threshold=-22dB:ratio=3:attack=8:release=160,asoftclip=type=tanh:threshold=0.9," % n
    whisper = vid.startswith(("m_ear", "m_whisper"))
    tail += "aecho=0.8:0.5:46|83:0.30|0.20," + ("aecho=0.9:0.45:210|370:0.16|0.10," if not whisper else "")
    if vid.startswith("m_phone"):
        tail += "highpass=f=320,lowpass=f=3300,"
    tail += "apad=pad_dur=0.25,loudnorm=I=-17:TP=-2.0:LRA=11"
    parts.append("".join(f"[l{i}]" for i in range(n)) + tail + "[o]")
    ff(["-i", src, "-filter_complex", ";".join(parts), "-map", "[o]", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", f"{OUT}/{vid}.wav"])
    return True


ids = sys.argv[1:] or sorted(os.path.basename(f)[:-4] for f in glob.glob(DRY + "/m_*.wav") if not os.path.basename(f).startswith("_"))
done = []
for vid in ids:
    if vid.startswith(HUMAN):
        continue
    if demon(vid):
        done.append(vid)
print("many-voiced:", len(done), ", ".join(done))
