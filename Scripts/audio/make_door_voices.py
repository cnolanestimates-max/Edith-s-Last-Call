"""Master Ruth's door from the owner's GDC recordings. Keep the original library intact."""
import argparse
import io
from pathlib import Path
import subprocess
import zipfile

import numpy as np
from scipy import signal
from scipy.io import wavfile

AUDIO = Path(__file__).resolve().parents[2] / 'SourceArt/Audio'
LIBRARY = Path.home() / 'OneDrive/Documents/ChatGPT/forklight-tts'
RATE = 48000
LENGTH = 12.5
TAKES = (
    (2, 'Epic Stock Media - AAA Game Character British Female Detective/'
        'VOXCry_British Detective Crying Vocal Female Low Energy Weep_ESM_AAAGCBFD.wav'),
    (5, 'SoundBits - Vox Hominis - Human Effort Voices/VOXCry_Crying Female 04 05_SNDBTS_VH.wav'),
)


def decode(data, filters='anull'):
    result = subprocess.run(['ffmpeg','-v','error','-i','pipe:0','-af',filters,'-ac','1',
                             '-ar',str(RATE),'-f','f32le','pipe:1'], input=data, capture_output=True,check=True)
    return np.frombuffer(result.stdout,dtype='<f4').copy()


def recording(library, take):
    volume, filename = take
    with zipfile.ZipFile(library / f'Sonniss.com-GDC2026-GameAudioBundle{volume}of5.zip') as archive:
        return decode(archive.read(filename),'highpass=f=85,lowpass=f=12000')


def pitch(stem, ratio):
    data = io.BytesIO()
    wavfile.write(data,RATE,stem.astype(np.float32))
    shifted = decode(data.getvalue(),f'rubberband=pitch={ratio}:pitchq=quality')
    return np.pad(shifted,(0,max(0,len(stem)-len(shifted))))[:len(stem)]


def band(stem, low, high):
    return signal.sosfilt(signal.butter(3,(low,high),'bandpass',fs=RATE,output='sos'),stem)


def rms(stem):
    return np.sqrt(np.mean(np.square(stem)))


def place(track, excerpt, start, gain=1.0):
    offset = round(start*RATE)
    source = excerpt[:len(track)-offset].copy()
    fade = min(len(source)//2,round(.029*RATE))
    if fade:
        ramp = np.linspace(0,1,fade)
        source[:fade] *= ramp
        source[-fade:] *= ramp[::-1]
    track[offset:offset+len(source)] += source*gain


def delay(stem, seconds):
    n = round(seconds*RATE)
    return np.pad(stem,(n,0))[:len(stem)]


def save(name, stem, peak):
    stem = stem.copy()
    stem *= peak / max(np.max(np.abs(stem)),1e-8)
    wavfile.write(AUDIO/(name+'.wav'),RATE,np.int16(np.rint(32767*stem)))


def weeping(library, t):
    weep, sob = (recording(library,take) for take in TAKES)
    # Alternate complete breaths with shorter catches. Both performers are genuinely crying.
    sob *= rms(weep) / rms(sob)
    dry = np.zeros_like(t)
    place(dry,weep,0)
    place(dry,sob[round(1.30*RATE):],2.39,.84)
    place(dry,weep[round(.83*RATE):],5.12,1.06)
    place(dry,sob,6.72,.97)
    place(dry,weep,10.65,1.08)
    # The first 2.4 seconds are the natural performance. Lower doubles, uneven
    # throat flutter and saturation gradually take it over without masking the syllable rhythm.
    change = np.clip((t-2.4)/(LENGTH-2.4),0,1)
    low = pitch(dry,.69)
    deep = pitch(dry,.48)
    growl = band(np.tanh(4.3*(low + .55*deep)),85,3400)
    flutter = 1 - .28*change*(1+np.sin(2*np.pi*(15*t+.31*t*t)))
    torn = (.53*growl*flutter + .83*low + .30*delay(deep,.063))
    body = (1-.58*change)*dry + (change**1.18)*torn
    performance = body + change*.12*delay(body,.089)
    return np.tanh(1.45*performance)


def whispers(t):
    # Breath gestures shaped into sibilants and murmured vowels. No dialogue samples.
    air = decode((AUDIO/'her_breath.wav').read_bytes(),'highpass=f=180,lowpass=f=8500')
    rng = np.random.default_rng(1941)
    track = np.zeros_like(t)
    for i,start in enumerate((.10,1.13,2.32,3.66,4.50,5.44,6.51,7.39,8.34,9.04,9.89,10.65,11.37,11.94)):
        length = rng.uniform(.72,1.34)
        count = round(length*RATE)
        j = rng.integers(0,len(air)-count)
        phrase = air[j:j+count].copy()
        if i%3==1:
            phrase = phrase[::-1].copy()
        phrase = phrase / max(rms(phrase),.002)
        u = np.linspace(0,1,count)
        hiss = band(phrase,2500,7400)
        vowel = band(phrase,650+(i%3)*120,2080)
        lips = np.sin(np.pi*u)**.65 * (.52+.48*np.sin((u*1.8+i*.33)*np.pi)**2)
        utterance = (.65*hiss + vowel*(.5+.5*np.sin(u*np.pi)))*lips
        # Each mouth movement carries at the door, including the first one.
        utterance = np.tanh(.43*utterance/max(rms(utterance),.003))
        place(track,utterance,start)
    rise = .25 + .75*(t/LENGTH)**1.25
    return (track + .18*delay(track,.061))*rise


def scream():
    original = decode((AUDIO/'her_scream_02.wav').read_bytes(),'highpass=f=135,lowpass=f=4300')
    voice = original[round(.47*RATE):round(2.31*RATE)].copy()
    voice[:round(.025*RATE)] *= np.linspace(0,1,round(.025*RATE))
    end = round(.27*RATE)
    voice[-end:] *= np.linspace(1,0,end)
    room = np.pad(voice,(0,round(.27*RATE)))
    return room + .28*delay(room,.078) + .14*delay(room,.173)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library',type=Path,default=LIBRARY)
    args = parser.parse_args()
    times = np.arange(round(RATE*LENGTH))/RATE
    save('door_weeping',weeping(args.library,times),.85)
    save('door_whispering',whispers(times),.61)
    save('door_room_scream',scream(),.88)
