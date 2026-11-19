"""Ground-level yard ambience, made from wind and stationary insect bands only."""
from pathlib import Path
import subprocess
AUDIO = Path(__file__).resolve().parents[2] / "SourceArt/Audio"


def build():
    for name, level, insects in (("amb_yard", -31, .72), ("amb_dawn", -35, .16)):
        # Three independently modulated narrow noise bands. No animal or field recordings.
        args = []
        filters = []
        for i, (freq, width, rate, depth, gain) in enumerate((
                (290, 420, .13, .22, 1.0), (3270, 480, 48, .46, .36 * insects),
                (4210, 360, 31, .82, .43 * insects), (3790, 340, 37, .66, .33 * insects))):
            args += ["-f", "lavfi", "-i", f"anoisesrc=color=pink:duration=45:sample_rate=48000:seed={31+i}"]
            filters.append(f"[{i}:a]bandpass=f={freq}:width_type=h:w={width},tremolo=f={rate}:d={depth},"
                           f"tremolo=f={.103+i*.021}:d=0.33,volume={gain}[n{i}]")
        filters.append("[n0][n1][n2][n3]amix=inputs=4:normalize=0,asplit=3[x][y][z]")
        filters.extend(["[x]atrim=1:44,asetpts=PTS-STARTPTS[body]", "[y]atrim=44:45,asetpts=PTS-STARTPTS[tail]",
                        "[z]atrim=0:1,asetpts=PTS-STARTPTS[head]", "[tail][head]acrossfade=d=1:c1=qsin:c2=qsin[seam]",
                        f"[body][seam]concat=n=2:v=0:a=1,loudnorm=I={level}:TP=-8:LRA=5"])
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *args, "-filter_complex", ";".join(filters),
                        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(AUDIO / (name + ".wav"))], check=True)


if __name__ == "__main__":
    build()
