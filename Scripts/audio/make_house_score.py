"""Build the continuous two-piece house score and the one-shot scare cue from Forklight's library."""
from pathlib import Path
import subprocess

LIBRARY = Path.home() / "OneDrive/Documents/ChatGPT/forklight-tts"
AUDIO = Path(__file__).resolve().parents[2] / "SourceArt/Audio"


def render(inputs, filters, output):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y"]
    for filename, start, duration in inputs:
        cmd += ["-ss", str(start), "-t", str(duration), "-i", str(LIBRARY / filename)]
    subprocess.run(cmd + ["-filter_complex", filters, "-map", "[out]", "-ar", "48000", "-ac", "2",
                          "-c:a", "pcm_s16le", str(AUDIO / output)], check=True)


if __name__ == "__main__":
    # Split the normalized beginning before joining. The last sample of the finished
    # loop runs straight into the first, at the same point in Apprehension.
    level = "loudnorm=I=-23.5:TP=-5:LRA=10,aresample=48000"
    render([("Apprehension - Kevin MacLeod.mp3", 7, 66),
            ("Darren Curtis - She's Watching Me MP3.mp3", 20, 110)],
           f"[0:a]{level},asplit=2[a][head];[1:a]{level}[b];"
           "[head]atrim=end=7,asetpts=PTS-STARTPTS[h];"
           "[a][b]acrossfade=d=7:c1=qsin:c2=qsin[first];"
           "[first][h]acrossfade=d=7:c1=qsin:c2=qsin,atrim=start=7,asetpts=PTS-STARTPTS[out]",
           "music_house.wav")
    # The passage heard in the audition. The scene controls how long its build lasts.
    render([("Bump in the Night - Kevin MacLeod.mp3", 25, 9)],
           "[0:a]loudnorm=I=-19:TP=-3.5:LRA=9,aresample=48000,"
           "afade=t=in:d=0.18,afade=t=out:st=8.5:d=0.5[out]",
           "scare_bump.wav")
