"""Quiet rubber on boards, an intermittent bearing rub, and two separate contact sounds."""
from pathlib import Path
import subprocess
import sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

audio=Path(__file__).resolve().parents[2]/'SourceArt/Audio'
sr=48000
rng=np.random.default_rng(2718)

def band(x,lo,hi):
    return signal.sosfilt(signal.butter(3,(lo,hi),'bandpass',fs=sr,output='sos'),x)
def source(name,seconds):
    raw=subprocess.check_output(['ffmpeg','-loglevel','error','-i',str(audio/name),'-t',str(seconds),
                                 '-ac','1','-ar',str(sr),'-f','f32le','-'])
    v=np.frombuffer(raw,dtype='<f4')
    start=np.flatnonzero(np.abs(v)>.045*np.max(np.abs(v)))[0]
    return np.pad(v[start:],(0,start))
def norm(x): return x/max(np.max(np.abs(x)),1.e-8)
def write(name,x,peak):
    wavfile.write(audio/(name+'.wav'),sr,np.round(norm(x)*peak*32767).astype('<i2'))

def make_rolling_sounds():
    t=np.arange(4*sr)/sr
    noise=rng.normal(size=len(t))
    grain=norm(band(noise,75,435))*.50+norm(band(noise,720,1750))*.09
    rub=grain*(.80+.11*np.sin(2*np.pi*.75*t)+.08*np.cos(2*np.pi*1.25*t))
    for at in (.29,.97,1.49,2.08,3.11,3.71):
        i=int(at*sr);dt=t[:int(.068*sr)]
        rub[i:i+len(dt)]+=.22*np.exp(-dt*77)*np.sin(2*np.pi*104*dt)
    # Cross the first and last grains at the loop boundary.
    n=int(.065*sr); a=np.linspace(0,1,n)
    rub[-n:]=rub[-n:]*(1-a)+rub[:n]*a
    write('wheel_on_boards',rub[n:],.34)

    # The unloaded bearing rasps once per revolution. Give it a narrow metallic
    # squeal with a little dirt under it, rather than broadband wind.
    t=np.arange(int(.39*sr))/sr
    noise=norm(band(rng.normal(size=len(t)),610,3200))
    phase=2*np.pi*np.cumsum(840+95*np.sin(2*np.pi*3.2*t)+27*np.sin(2*np.pi*13*t))/sr
    squeal=.64*np.sin(phase)+.21*np.sin(2.09*phase)+.19*noise
    envelope=np.clip(t/.028,0,1)*np.clip((t[-1]-t)/.11,0,1)*(.83+.17*np.cos(2*np.pi*17*t))
    write('wheel_axle_rub',squeal*envelope*np.exp(-t*2),.48)

def make_impacts():
    time = np.arange(round(sr * 1.05)) / sr
    wood = source("step_wood_02.wav", .53)
    metal = source("trash_crash.wav", .85)
    rail = source("chair_scrape.wav", .53)


    def add(output, clip, seconds, gain, low, high, decay):
        start = round(seconds * sr)
        count = min(len(clip), len(output) - start)
        part = norm(band(clip[:count], low, high))
        output[start:start + count] += gain * part * np.exp(-time[:count] * decay)


    def body(frequency, decay):
        return np.sin(2 * np.pi * frequency * time) * np.exp(-decay * time) * np.minimum(time / .003, 1)


    wall = .64 * body(87, 15) + .19 * body(129, 23)
    add(wall, wood, .000, .94, 58, 2080, 10)
    add(wall, metal, .013, 1.15, 510, 8200, 15)
    add(wall, metal, .077, .63, 890, 6700, 20)
    add(wall, rail, .110, .19, 180, 2550, 10)

    fall = .78 * body(66, 12) + .22 * body(106, 18)
    add(fall, metal, .000, 1.05, 380, 7900, 11)
    add(fall, wood, .023, 1.13, 54, 1780, 6)
    add(fall, metal, .127, .62, 560, 5700, 16)
    add(fall, wood, .182, .38, 145, 3200, 17)
    add(fall, rail, .210, .32, 260, 2950, 11)
    add(fall, metal, .284, .32, 1450, 5900, 18)
    for name, wave in (("wheel_baseboard", wall), ("wheel_sidefall", fall)):
        wave *= np.minimum((time[-1] - time) / .095, 1)
        write(name, np.tanh(.93 * wave), .955)


if __name__ == "__main__":
    if "--impacts-only" not in sys.argv:
        make_rolling_sounds()
    make_impacts()
