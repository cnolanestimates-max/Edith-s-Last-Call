"""Render Edith's stair treads from her existing footstep, wood contact and board resonance."""
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile


AUDIO = Path(__file__).resolve().parents[2] / "SourceArt/Audio"
RATE = 48000


def contact(name, speed):
    rate, wav = wavfile.read(AUDIO / (name + ".wav"))
    data = wav.astype(float) / 32768.
    if data.ndim == 2:
        data = data.mean(axis=1)
    onset = np.flatnonzero(np.abs(data) > .022)
    if onset.size:
        data = data[max(0, onset[0]-96):]
    return np.interp(np.arange(0,len(data),speed*rate/RATE),np.arange(len(data)),data)


for index, fundamental in enumerate((77., 70., 84.), 1):
    time = np.arange(round(.39*RATE)) / RATE
    # First the tread gives under her heel, then the short knock of the loose board.
    phase = 2*np.pi*(fundamental*time + .31*(1.-np.exp(-time/.025)))
    board = (1.-np.exp(-time/.005)) * np.exp(-time/.082) * (
        .56*np.sin(phase) + .27*np.sin(2.04*phase) + .11*np.sin(3.18*phase))
    step = contact(f"her_step_{index:02d}", .84)
    wood = contact(f"step_wood_{index+1:02d}", .82)
    board[:min(len(step),len(board))] += .97*step[:len(board)]
    offset = round(.014*RATE)
    length = min(len(wood),len(board)-offset)
    board[offset:offset+length] += .52*wood[:length]
    board = signal.sosfilt(signal.butter(2,45,fs=RATE,btype="highpass",output="sos"),board)
    board = np.tanh(1.7*board)
    board[-960:] *= np.linspace(1.,0.,960)
    board *= .86/np.max(np.abs(board))
    wavfile.write(AUDIO/f"shelf_stair_step_{index:02d}.wav",RATE,np.rint(board*32767).astype("<i2"))
