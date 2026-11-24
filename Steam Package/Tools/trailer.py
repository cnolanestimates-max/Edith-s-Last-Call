# Edith's Last Call: announcement trailer, cut from recorded gameplay frames, the game's own voice lines, music and effects.
# Every picture is a frame the game rendered (frame-by-frame captures at 30 fps); text cards and the end card are added.
import os, subprocess, sys
S = os.path.dirname(os.path.abspath(__file__))
SAV = r'C:\GameDev\Unreal\WellnessCheck\Saved'
AUD = r'C:\GameDev\Unreal\WellnessCheck\SourceArt\Audio'
W = os.path.join(S, 'trailer_work'); os.makedirs(W, exist_ok=True)
OUT = sys.argv[1]
FPS = 30
VF = 'scale=1920:1080:flags=lanczos:out_range=tv,setsar=1,format=yuv420p,setparams=range=tv'

def run(args):
    r = subprocess.run(['ffmpeg', '-y', '-v', 'error'] + args, capture_output=True, text=True)
    if r.returncode: print(r.stderr); raise SystemExit(1)

segs = []
def frames(name, folder, pattern, start, count, fade_in=0.0, fade_out=0.0):
    dur = count / FPS
    vf = VF
    if fade_in: vf += f',fade=t=in:st=0:d={fade_in}'
    if fade_out: vf += f',fade=t=out:st={dur - fade_out:.3f}:d={fade_out}'
    p = os.path.join(W, name + '.mp4')
    # the recorder sometimes skips a frame number, so take the frames by their order on disk, not by number
    import glob
    ext = pattern.rsplit('.', 1)[1]
    fs = sorted(glob.glob(os.path.join(SAV, folder, 'f_*.' + ext)))[start:start + count]
    lst = os.path.join(W, name + '.txt')
    with open(lst, 'w') as f:
        for x in fs: f.write(f"file '{x}'\nduration {1 / FPS:.6f}\n")
        f.write(f"file '{fs[-1]}'\n")
    run(['-f', 'concat', '-safe', '0', '-i', lst, '-frames:v', str(count), '-vf', vf, '-c:v', 'libx264', '-color_range', 'tv', '-crf', '17',
         '-preset', 'medium', '-r', str(FPS), p])
    segs.append((p, dur))

def still(name, png, dur, fade_in=0.6, fade_out=0.6):
    p = os.path.join(W, name + '.mp4')
    vf = VF + f',fade=t=in:st=0:d={fade_in},fade=t=out:st={dur - fade_out:.3f}:d={fade_out}'
    run(['-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.3f}', '-i', png, '-vf', vf, '-c:v', 'libx264', '-color_range', 'tv', '-crf', '17', '-r', str(FPS), p])
    segs.append((p, dur))

def black(name, dur):
    p = os.path.join(W, name + '.mp4')
    run(['-f', 'lavfi', '-i', f'color=c=black:s=1920x1080:r={FPS}:d={dur:.3f}', '-vf', VF, '-c:v', 'libx264', '-color_range', 'tv', '-crf', '17', p])
    segs.append((p, dur))

C = os.path.join(S, 'cards')
OPEN = 'steam_open/video/f_%05d.jpg'
# ---- picture --------------------------------------------------------------------------------------------------------
black('00_black', 3.5)                                                    # phone rings in the dark
still('01_date', os.path.join(C, 'c01_date.png'), 4.0)
frames('02_air', 'steam_open/video', 'f_%05d.jpg', 40, 150, fade_in=0.8)   # over the forest, following the cruiser
frames('03_drive', 'steam_open/video', 'f_%05d.jpg', 800, 195)             # the road in the headlights
frames('04_house', 'steam_open/video', 'f_%05d.jpg', 1420, 180)            # the house comes out of the trees
frames('05_house2', 'steam_open/video', 'f_%05d.jpg', 1600, 105, fade_out=0.5)
still('06_welfare', os.path.join(C, 'c02_welfare.png'), 3.0)
frames('07_hall', 'HallLightScareRec/Frames', 'f_%05d.png', 200, 135, fade_in=0.3)
frames('08_book', 'SettlersTake2/Frames', 'f_%05d.png', 60, 120)
frames('09_bath', 'BathChairFinal/Frames', 'f_%05d.png', 180, 113, fade_out=0.2)
black('10_black', 2.7)
still('11_waiting', os.path.join(C, 'c03_waiting.png'), 3.5)
frames('12_ceiling', 'Corner24Work/Final/frames', 'f_%05d.png', 465, 90)
frames('13_moon', 'Moon64/Frames', 'f_%05d.png', 240, 75)
frames('14_lunge', 'MoonFront/Frames', 'f_%05d.png', 240, 75)
black('15_black', 4.5)                                                    # "Stay." / supper's getting cold
still('16_end', os.path.join(C, 'c09_end.png'), 7.5, fade_in=0.15, fade_out=1.2)

lst = os.path.join(W, 'list.txt')
with open(lst, 'w') as f:
    for p, _ in segs: f.write(f"file '{p}'\n")
pic = os.path.join(W, 'picture.mp4')
run(['-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', pic])
T = {}; t = 0.0
for p, d in segs: T[os.path.basename(p)[:-4]] = t; t += d
total = t
print('picture', round(total, 2), 's')

# ---- sound ----------------------------------------------------------------------------------------------------------
# (file, start seconds, volume dB, optional trim seconds)
cues = [
    ('phone_ring.wav', 0.6, -4), ('phone_ring.wav', 2.6, -6),
    ('radio_static.wav', T['01_date'] + 0.5, -14),
    ('VO/r_arrive1.wav', T['02_air'] + 0.6, 0),
    ('VO/r_arrive2.wav', T['04_house'] + 0.4, 0),
    ('VO/d_arrive3.wav', T['05_house2'] + 1.4, 0),
    ('knock.wav', T['06_welfare'] + 0.4, -2),
    ('VO/d_phonecord.wav', T['07_hall'] + 0.3, 0),
    ('VO/r_trace.wav', T['08_book'] + 0.2, 0),
    ('sting_swell.wav', T['09_bath'] + 1.0, -6),
    ('thump_heavy.wav', T['12_ceiling'] + 0.2, -2),
    ('thump_heavy.wav', T['12_ceiling'] + 1.4, -4),
    ('sting_braam.wav', T['14_lunge'] + 0.9, 0),
    ('her_scream_01.wav', T['14_lunge'] + 1.3, -1),
    ('VO/m_ear1.wav', T['15_black'] + 0.6, 2),
    ('phone_ring.wav', T['15_black'] + 1.6, -8),
    ('VO/m_phone3.wav', T['15_black'] + 2.0, 1),
    ('sting_hit.wav', T['16_end'], -3),
]
inputs, filt, labels = [], [], []
for i, (f, st, db) in enumerate(cues):
    inputs += ['-i', os.path.join(AUD, f)]
    ms = int(st * 1000)
    filt.append(f'[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={db}dB,adelay={ms}|{ms}[a{i}]')
    labels.append(f'[a{i}]')
n = len(cues)
# music: the house score under the first half, the stalk drone from the second card, both cut dead on the lunge
mh, ms_ = n, n + 1
inputs += ['-i', os.path.join(AUD, 'music_house.wav'), '-i', os.path.join(AUD, 'music_stalk.wav')]
cut = T['15_black']
filt.append(f'[{mh}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{cut:.2f},afade=t=in:st=0:d=4,'
            f'afade=t=out:st={T["11_waiting"]:.2f}:d=2.5,volume=-9dB,adelay={int(T["01_date"]*1000)}|{int(T["01_date"]*1000)}[mh]')
sd = int(T['11_waiting'] * 1000)
filt.append(f'[{ms_}:a]aformat=sample_rates=48000:channel_layouts=stereo,afade=t=in:st=0:d=2,'
            f'atrim=0:{cut - T["11_waiting"]:.2f},afade=t=out:st={cut - T["11_waiting"] - 0.15:.2f}:d=0.15,volume=-4dB,adelay={sd}|{sd}[ms]')
labels += ['[mh]', '[ms]']
filt.append(''.join(labels) + f'amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{total:.2f},'
            f'loudnorm=I=-16:TP=-1.5:LRA=11[out]')
mix = os.path.join(W, 'mix.wav')
run(inputs + ['-filter_complex', ';'.join(filt), '-map', '[out]', '-ar', '48000', mix])
run(['-i', pic, '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest',
     '-movflags', '+faststart', OUT])
print('wrote', OUT, {k: round(v, 2) for k, v in T.items()})



