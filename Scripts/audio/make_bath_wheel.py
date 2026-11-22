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

# The unloaded bearing rasps once per revolution. Give it a narrow metallic
# squeal with a little dirt under it, rather than broadband wind.
t=np.arange(int(.39*sr))/sr
noise=norm(band(rng.normal(size=len(t)),610,3200))
phase=2*np.pi*np.cumsum(840+95*np.sin(2*np.pi*3.2*t)+27*np.sin(2*np.pi*13*t))/sr
squeal=.64*np.sin(phase)+.21*np.sin(2.09*phase)+.19*noise
envelope=np.clip(t/.028,0,1)*np.clip((t[-1]-t)/.11,0,1)*(.83+.17*np.cos(2*np.pi*17*t))
write('wheel_axle_rub',squeal*envelope*np.exp(-t*2),.48)

wood=norm(band(source('step_wood_02.wav',.60),52,1650))
rail=norm(band(source('chair_scrape.wav',.60),160,1950))
metal=norm(band(source('trash_crash.wav',.85),140,6200))
t=np.arange(len(metal))/sr
wall=np.zeros_like(metal)

def hit(out, clip, offset, amount):
    start=round(offset*sr)
    count=min(len(clip),len(out)-start)
    out[start:start+count]+=amount*clip[:count]

# A compressed tyre strikes the baseboard before the tubing and hardware clatter.
hit(wall,wood*np.exp(-t[:len(wood)]*9),0,.85)
hit(wall,metal*np.exp(-t*12),.028,.72)
hit(wall,rail*np.exp(-t[:len(rail)]*14),.13,.30)
write('wheel_baseboard',wall,.88)

# The side of the frame lands as a heavier two-part impact: metal, then
# a separate slap of wood and the loose footrest ringing against the tube.
fall=.87*metal*np.exp(-t*6)
hit(fall,wood*np.exp(-t[:len(wood)]*10),.024,.78)
hit(fall,metal*np.exp(-t*16),.105,.36)
hit(fall,rail*np.exp(-t[:len(rail)]*22),.22,.28)
write('wheel_sidefall',fall,.90)
