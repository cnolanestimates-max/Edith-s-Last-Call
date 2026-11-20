"""Master the separate cries and whispers at the latch. Each is a single 12.5s take."""
from pathlib import Path
import subprocess

audio = Path(__file__).resolve().parents[2]/'SourceArt/Audio'

def master(inputs, filters, out):
    args = ['ffmpeg','-v','error','-y']
    for source in inputs:
        args.extend(['-i',str(audio/source)])
    subprocess.run(args+['-filter_complex',filters,'-map','[out]','-ac','1','-ar','48000',
                          '-c:a','pcm_s16le',str(audio/out)],check=True)

if __name__=='__main__':
    # Close, full-voiced grief from the first breath; increase presence as she loses control.
    master(['raw/edith_door_sobs.wav'], '[0:a]highpass=f=90,lowpass=f=6800,loudnorm=I=-16:TP=-2:LRA=7,'
           "volume='0.85+0.24*t/12.5':eval=frame,atrim=duration=12.5,afade=t=in:d=0.012,afade=t=out:st=12.485:d=0.015[out]",
           'door_weeping.wav')
    # A second throat just to the side of Edith: four overlapping utterances in the same space.
    master(['whisper_far_01.wav','VO/m_whisper1.wav','whisper_far_02.wav','VO/m_whisper2.wav','whisper_far_01.wav'],
           '[0:a]aresample=48000[a];[1:a]aresample=48000,adelay=3120:all=1[b];'
           '[2:a]aresample=48000,adelay=4750:all=1[c];[3:a]aresample=48000,adelay=8230:all=1[d];'
           '[4:a]aresample=48000,atempo=1.13,adelay=10500:all=1[e];'
           '[a][b][c][d][e]amix=inputs=5:normalize=0,highpass=f=340,lowpass=f=7500,'
           'loudnorm=I=-19:TP=-3:LRA=6,aresample=48000,apad=pad_dur=0.15,atrim=end_sample=600000,afade=t=out:st=12.485:d=0.015[out]',
           'door_whispering.wav')
