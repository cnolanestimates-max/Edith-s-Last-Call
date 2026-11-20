"""Quiet rubber on boards, an intermittent bearing rub, and two separate contact sounds."""
from pathlib import Path
import subprocess
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

t=np.arange(int(.43*sr))/sr
noise=band(rng.normal(size=len(t)),620,2900)
phase=2*np.pi*np.cumsum(690+45*np.sin(2*np.pi*2.6*t)+14*np.sin(2*np.pi*7*t))/sr
rub=(.76*norm(noise)+.24*np.sin(phase))*(np.sin(np.pi*t/t[-1])**2)*np.exp(-t*4)
write('wheel_axle_rub',rub,.25)

wood=norm(band(source('step_wood_02.wav',.60),52,1650))
rail=norm(band(source('chair_scrape.wav',.60),160,1950))
t=np.arange(len(wood))/sr
wall=wood*np.exp(-t*6)+.18*np.resize(rail,len(t))*np.exp(-t*11)
write('wheel_baseboard',wall,.62)

# The game's recorded bin metal, shortened and damped to the weight of a tubular chair frame.
metal=norm(band(source('trash_crash.wav',.85),185,3500))
t=np.arange(len(metal))/sr
fall=.55*metal*np.exp(-t*6)+.60*np.pad(wood,(0,len(t)-len(wood)))*np.exp(-t*8)
echo=int(.112*sr)
fall[echo:]+=.20*metal[:-echo]*np.exp(-t[:-echo]*18)
write('wheel_sidefall',fall,.72)
