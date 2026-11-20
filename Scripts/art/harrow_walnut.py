"""Bake original straight-grain walnut and a bookmatched burr veneer for Edith's armoire."""
from pathlib import Path
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parents[2] / 'SourceArt/Textures/Harrow'
SIZE = 1024
v, u = np.mgrid[0:SIZE, 0:SIZE] / SIZE
rng = np.random.default_rng(1858)


def noise(width, height):
    source = Image.fromarray(rng.integers(0, 256, (height, width), dtype=np.uint8))
    return np.asarray(source.resize((SIZE, SIZE), Image.Resampling.BICUBIC)) / 255.0 - .5


def bake(name, burr):
    drift = noise(9, 3)
    phase = u + .035 * drift + .026 * np.sin(7*v + 3*u)
    if burr:
        phase += .16 * noise(5, 7) + .037 * noise(12, 16)
        for x, y, r in ((.23,.36,.19),(.77,.74,.27),(.48,.12,.16),(.89,.30,.12)):
            dx, dy = u-x, (v-y)*.83
            phase += .13 * np.exp(-(dx*dx + dy*dy)/(r*r))
    ring = .5 + .5*np.sin(phase*(136 if burr else 97) + 7*noise(6, 4))
    pores = np.maximum(0, noise(400, 73) + .14)
    grain = .42*ring**3 + .12*np.cos(phase*611 + 2*drift) + .80*pores
    figure = noise(18, 9)*.37 + noise(5, 4)*.46 - grain*.54
    colors = (158, 101, 60) if burr else (138, 80, 45)
    amplitude = (92, 75, 54)
    color = np.stack([base + a*figure for base, a in zip(colors, amplitude)], axis=-1)
    roughness = 100 + 33*grain + 27*noise(15, 19)
    dy, dx = np.gradient(pores*1.0 + grain*.7)
    normals = np.stack((-dx, dy, np.ones_like(dx)), axis=-1)
    normals /= np.linalg.norm(normals, axis=-1, keepdims=True)
    for suffix, array in (('', color), ('_R', roughness), ('_N', (normals*.5 + .5)*255)):
        if burr:
            half = array[:, :SIZE//2]
            array = np.concatenate((half, half[:, ::-1]), axis=1)
            if suffix == '_N':
                array[:, SIZE//2:, 0] = 255 - array[:, SIZE//2:, 0]
        Image.fromarray(np.uint8(np.clip(array, 0, 255))).save(OUT / f'T_Harrow{name}{suffix}.png')


if __name__ == '__main__':
    bake('Walnut', False)
    bake('Burr', True)
