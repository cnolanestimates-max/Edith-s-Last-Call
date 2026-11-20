"""Original game Foley: a pair of detuned piano keys and a draining enamel bath."""
from array import array
from pathlib import Path
import math, random, wave
out=Path(__file__).resolve().parents[2]/'SourceArt/Audio'
rate=44100
def write(name,samples):
    with wave.open(str(out/(name+'.wav')),'wb') as f:
        f.setparams((1,2,rate,0,'NONE','not compressed'))
        f.writeframes(array('h',(round(max(-1,min(1,v))*30000) for v in samples)).tobytes())
def piano(t,f):
    if t<0:return 0.
    return min(1,t*260)*sum(math.exp(-t*(1.4+.35*n))*math.sin(2*math.pi*f*n*(1+n*n*.00015)*t)/(n**1.5) for n in range(1,9))
write('piano_answer',(.48*piano(i/rate,277.18)+.23*piano(i/rate-.96,146.83)+.14*piano(i/rate-1.06,155.56) for i in range(rate*5)))
rng=random.Random(1942)
bubbles=[(rng.uniform(.05,2.7),rng.uniform(68,300),rng.uniform(.04,.15)) for _ in range(105)]
samples=[0.]*(rate*3)
for start,pitch,dur in bubbles:
    at=int(start*rate)
    for j in range(int(dur*rate)):
        t=j/rate;u=t/dur
        samples[at+j]+=.12*math.sin(math.pi*u)*math.exp(-3*u)*math.sin(2*math.pi*pitch*t*(1+.6*u))
write('bath_drain',samples)
