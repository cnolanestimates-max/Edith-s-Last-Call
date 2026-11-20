"""Mix the bookshelf cue from four CC0 VSCO 2 Community Edition solo violin takes.

Pass a directory containing the LLVln_ArcoVib WAVs from Strings/Solo Violin/Arco Vib,
and the destination WAV. The 5.6-second cue ends when Edith breaks eye contact.
"""
import argparse
from pathlib import Path
import subprocess


def render(samples, output):
    # Separate performances keep the small differences in bow pressure and vibrato.
    layers = [
        ("A6_f", 0.04, 1.000, 0,   1.00),
        ("A6_p", 0.12, 0.994, 85,  0.67),
        ("G6_f", 0.08, 1.130, 160, 0.46),
        ("E6_p", 0.10, 1.000, 245, 0.52),
    ]
    args = ["ffmpeg", "-v", "error", "-nostdin", "-y"]
    filters = []
    for index, (take, start, pitch, delay, gain) in enumerate(layers):
        args.extend(["-i", str(samples / f"LLVln_ArcoVib_{take}.wav")])
        filters.append(f"[{index}:a]atrim=start={start}:duration=5.7,asetpts=PTS-STARTPTS,"
                       f"aformat=channel_layouts=mono,aresample=48000,asetrate={round(48000*pitch)},"
                       f"aresample=48000,adelay={delay},volume={gain}[bow{index}]")
    filters.append("[bow0][bow1][bow2][bow3]amix=inputs=4:normalize=0,atrim=duration=5.6,"
                   "highpass=f=320,loudnorm=I=-20:TP=-3:LRA=7,aresample=48000,"
                   "afade=t=in:d=0.75,afade=t=out:st=5.12:d=0.48")
    subprocess.run(args + ["-filter_complex", ";".join(filters), "-ar", "48000", "-ac", "1",
                           "-c:a", "pcm_s16le", str(output)], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("samples", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.samples, args.output)
