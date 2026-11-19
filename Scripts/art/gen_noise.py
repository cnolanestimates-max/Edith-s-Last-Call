"""A tiling cloud-noise texture for the smoke material (no paid generation).  Writes SourceArt/Textures/misc/T_SmokeNoise.png."""
import os
import numpy as np
from PIL import Image

N = 256
rng = np.random.default_rng(7)
out = np.zeros((N, N))
fy = np.fft.fftfreq(N)[:, None]
fx = np.fft.fftfreq(N)[None, :]
f = np.sqrt(fx * fx + fy * fy)
f[0, 0] = 1.0
spec = np.fft.fft2(rng.standard_normal((N, N))) / (f ** 1.7)      # more energy in the big shapes: clouds, not grain
spec[0, 0] = 0
img = np.real(np.fft.ifft2(spec))
img = (img - img.min()) / (img.max() - img.min())
img = np.clip((img - 0.25) / 0.5, 0, 1) ** 1.2                    # stretch the contrast: clear holes and dense knots
d = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Textures/misc"
os.makedirs(d, exist_ok=True)
Image.fromarray((img * 255).astype(np.uint8), "L").save(d + "/T_SmokeNoise.png")
print("noise written", img.mean().round(3))
