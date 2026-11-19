"""Master the rear bin from two isolated takes in 344 Audio's metal impact recording."""
from pathlib import Path
import subprocess
import tempfile
import zipfile

AUDIO = Path(__file__).resolve().parents[2] / "SourceArt/Audio"
MEMBER = "344 Audio - Haunting Ambiences Vol. 3/METLImpt_Metal Bangs, Metal Hits, Banging On Doors_344 Audio_Haunting Ambiences Vol 3.wav"


def build():
    with tempfile.TemporaryDirectory() as tmp:
        source = next((AUDIO / "raw_lib").glob("METLImpt_Metal_Bangs*"), None)
        if not source:
            library = Path.home() / "OneDrive/Documents/ChatGPT/forklight-tts"
            with zipfile.ZipFile(library / "Sonniss.com-GDC2026-GameAudioBundle1of5.zip") as archive:
                source = Path(tmp) / "metal.wav"
                source.write_bytes(archive.read(MEMBER))
        filters = ("[0:a]aformat=sample_rates=48000:channel_layouts=mono,asetrate=43200,aresample=48000,"
                   "highpass=f=42,lowpass=f=5100,equalizer=f=160:t=q:w=1:g=3,afade=t=out:st=0.62:d=0.22[body];"
                   "[1:a]aformat=sample_rates=48000:channel_layouts=mono,highpass=f=400,lowpass=f=4200,"
                   "volume=.40,afade=t=out:st=0.28:d=0.17,adelay=245[lid];"
                   "[body][lid]amix=inputs=2:normalize=0,alimiter=limit=.78:level=0:latency=1")
        # Set gain against the measured PCM peak, keeping the impact's original dynamics.
        intermediate = Path(tmp) / "bin.wav"
        subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-ss","16.878","-t","0.79","-i",str(source),
                        "-ss","28.171","-t","0.48","-i",str(source),"-filter_complex",filters,
                        "-ar","48000","-ac","1",str(intermediate)],check=True)
        import array, wave
        with wave.open(str(intermediate)) as f:
            samples = array.array("h", f.readframes(f.getnframes()))
        gain = .73 * 32768 / max(map(abs, samples))
        subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-i",str(intermediate),"-af",f"volume={gain}",
                        "-c:a","pcm_s16le",str(AUDIO/"trash_crash.wav")],check=True)


if __name__ == "__main__":
    build()
