# Edith's Last Call: announcement trailer, second cut (2026-11-24, after Cheyenne's notes).
# Built the way short indie horror trailers on Steam are (Visage, MADiSON, The Mortuary Assistant): the dispatch setup, then
# slow floating shots through the house, its rooms and props, a quickening run of short shots, one glimpse of her at most,
# black, a whisper, the title.  No scares.  Every picture is a frame the game rendered from today's build (the floating camera
# is -WCFloat in WCAuto.cpp, shot list in float_shots.py); the opening is the in-game drive.  Usage: trailer2.py <out.mp4>
import os, subprocess, sys, glob
S = os.path.dirname(os.path.abspath(__file__))
SAV = r'C:\GameDev\Unreal\WellnessCheck\Saved'
AUD = r'C:\GameDev\Unreal\WellnessCheck\SourceArt\Audio'
W = os.path.join(S, 'trailer2_work'); os.makedirs(W, exist_ok=True)
OUT = sys.argv[1]
FPS = 30
VF = 'scale=1920:1080:flags=lanczos:out_range=tv,setsar=1,format=yuv420p,setparams=range=tv'
# the house is lit for play (five feet of flashlight); for a store page lift the shadows a little so the rooms read
LIFT = 'eq=gamma=1.28:contrast=1.06:saturation=0.92,'

def run(args):
    r = subprocess.run(['ffmpeg', '-y', '-v', 'error'] + args, capture_output=True, text=True)
    if r.returncode: print(r.stderr); raise SystemExit(1)

segs = []
def frames(name, folder, start, count, fade_in=0.0, fade_out=0.0, lift=True, ext='png', zoom=0.0):
    dur = count / FPS
    vf = (LIFT if lift else '')
    if zoom:                                   # a slow push for a still-ish shot
        vf += f"scale=2304:1296,crop=1920*(1-{zoom}*t/{dur}):1080*(1-{zoom}*t/{dur}):(iw-ow)/2:(ih-oh)/2,"
    vf += VF
    if fade_in: vf += f',fade=t=in:st=0:d={fade_in}'
    if fade_out: vf += f',fade=t=out:st={dur - fade_out:.3f}:d={fade_out}'
    p = os.path.join(W, name + '.mp4')
    fs = sorted(glob.glob(os.path.join(SAV, folder, 'f_*.' + ext)))[start:start + count]   # by order: the recorder skips numbers
    lst = os.path.join(W, name + '.txt')
    with open(lst, 'w') as f:
        for x in fs: f.write(f"file '{x}'\nduration {1 / FPS:.6f}\n")
        f.write(f"file '{fs[-1]}'\n")
    run(['-f', 'concat', '-safe', '0', '-i', lst, '-frames:v', str(count), '-vf', vf, '-c:v', 'libx264', '-color_range', 'tv', '-crf', '17',
         '-preset', 'medium', '-r', str(FPS), p])
    segs.append((p, dur))

def still(name, img, dur, fade_in=0.6, fade_out=0.6, push=0.0):
    p = os.path.join(W, name + '.mp4')
    vf = ''
    if push: vf = f"scale=w='2*trunc(960*(1+{push}*t/{dur}))':h='2*trunc(540*(1+{push}*t/{dur}))':eval=frame,crop=1920:1080,"
    vf += VF + f',fade=t=in:st=0:d={fade_in},fade=t=out:st={dur - fade_out:.3f}:d={fade_out}'
    run(['-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.3f}', '-i', img, '-vf', vf, '-c:v', 'libx264', '-color_range', 'tv', '-crf', '17', '-r', str(FPS), p])
    segs.append((p, dur))

def black(name, dur):
    p = os.path.join(W, name + '.mp4')
    run(['-f', 'lavfi', '-i', f'color=c=black:s=1920x1080:r={FPS}:d={dur:.3f}', '-vf', VF, '-c:v', 'libx264', '-color_range', 'tv', '-crf', '17', p])
    segs.append((p, dur))

C = os.path.join(S, 'cards')
F = 'trailer2/video/'
OPEN = 'steam_open/video'
# ---- picture --------------------------------------------------------------------------------------------------------
black('00_black', 3.0)                                                         # the phone rings in the dark
still('01_date', os.path.join(C, 'c01_date.png'), 3.5)
frames('02_air', OPEN, 330, 150, fade_in=0.8, lift=False, ext='jpg')            # over the forest, following the cruiser
frames('03_drive', OPEN, 840, 195, lift=False, ext='jpg')                       # the road in the headlights
frames('04_drive2', OPEN, 1290, 150, lift=False, ext='jpg')                     # the house through the trees
frames('05_house', OPEN, 1500, 299, fade_out=0.8, lift=False, ext='jpg')
black('06_knock', 2.2)
frames('07_hall', F + 'hall_push', 0, 165, fade_in=0.4)
frames('08_dining', F + 'dining_table', 20, 180)
frames('09_kitchen', F + 'kitchen', 130, 90)
frames('10_drawings', F + 'sitting_drawings', 40, 150)
frames('11_kids', F + 'kids_room', 30, 120)
frames('12_altar', F + 'prayer_altar', 30, 120)
frames('13_attic', F + 'attic', 30, 120)
frames('14_cellar', F + 'cellar_jars', 10, 180)
# quickening
frames('15_sick', F + 'sickroom', 100, 45)
frames('16_den', F + 'den', 120, 36)
frames('17_master', F + 'master', 140, 30)
frames('18_jars', F + 'cellar', 235, 24)
frames('19_piano', F + 'piano', 150, 18)
still('20_glimpse', os.path.join(S, 'glimpse.jpg'), 0.6, fade_in=0.0, fade_out=0.15, push=0.04)
black('21_black', 5.0)                                                         # "Nobody comes..."
still('22_end', os.path.join(C, 'c09_end.png'), 6.5, fade_in=0.15, fade_out=1.2)
black('23_after', 3.0)                                                         # the phone, once more: "You came."

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
cues = [
    ('phone_ring.wav', 0.4, -4), ('phone_ring.wav', 2.2, -6),
    ('radio_static.wav', T['01_date'] + 0.4, -14),
    ('VO/d_arrive1.wav', T['01_date'] + 1.6, 0),
    ('VO/r_arrive1.wav', T['02_air'] + 4.8, 0),
    ('VO/r_arrive2.wav', T['05_house'] + 0.2, 0),
    ('VO/d_arrive3.wav', T['05_house'] + 7.2, 0),
    ('knock.wav', T['06_knock'] + 0.5, -2),
    ('door_creak_long.wav', T['07_hall'] - 0.2, -8),
    ('VO/d_foyer.wav', T['07_hall'] + 0.8, 0, 4.4),
    ('VO/d_table.wav', T['08_dining'] + 0.8, 0),
    ('creak_02.wav', T['09_kitchen'] + 1.0, -10),
    ('VO/d_sitting.wav', T['10_drawings'] + 0.3, 0),
    ('whisper_far_01.wav', T['11_kids'] + 0.8, -10),
    ('VO/r_trace.wav', T['12_altar'] + 0.2, 0),
    ('VO/d_trace.wav', T['14_cellar'] + 2.2, 0),
    ('thump_heavy.wav', T['15_sick'] + 0.1, -4),
    ('bulb_buzz.wav', T['16_den'], -10),
    ('thump_heavy.wav', T['17_master'] + 0.1, -2),
    ('door_slam.wav', T['18_jars'] + 0.1, -6),
    ('bulb_pop.wav', T['19_piano'] + 0.2, -6),
    ('sting_hit.wav', T['20_glimpse'], -2),
    ('VO/m_phone2.wav', T['21_black'] + 0.9, 2),
    ('sting_hit.wav', T['22_end'], -6),
    ('phone_ring.wav', T['23_after'] + 0.3, -8),
    ('VO/m_phone1.wav', T['23_after'] + 1.4, 2),
]
inputs, filt, labels = [], [], []
for i, c in enumerate(cues):
    f, st, db = c[:3]
    inputs += ['-i', os.path.join(AUD, f)]
    ms = int(st * 1000)
    tr = f'atrim=0:{c[3]},afade=t=out:st={c[3] - 0.15}:d=0.15,' if len(c) > 3 else ''
    filt.append(f'[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,{tr}volume={db}dB,adelay={ms}|{ms}[a{i}]')
    labels.append(f'[a{i}]')
n = len(cues)
# the house score from the date card to the quickening, the stalk drone under the quickening, both cut dead on the glimpse
mh, ms_ = n, n + 1
inputs += ['-i', os.path.join(AUD, 'music_house.wav'), '-i', os.path.join(AUD, 'music_stalk.wav')]
cut = T['21_black']
st0 = T['01_date']; q = T['14_cellar'] + 2.0
filt.append(f'[{mh}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{cut - st0:.2f},afade=t=in:st=0:d=4,'
            f'afade=t=out:st={q - st0:.2f}:d=3,volume=-10dB,adelay={int(st0*1000)}|{int(st0*1000)}[mh]')
sd = int(q * 1000)
filt.append(f'[{ms_}:a]aformat=sample_rates=48000:channel_layouts=stereo,afade=t=in:st=0:d=1.5,'
            f'atrim=0:{cut - q:.2f},afade=t=out:st={cut - q - 0.1:.2f}:d=0.1,volume=-5dB,adelay={sd}|{sd}[ms]')
labels += ['[mh]', '[ms]']
filt.append(''.join(labels) + f'amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{total:.2f},'
            f'loudnorm=I=-16:TP=-1.5:LRA=11[out]')
mix = os.path.join(W, 'mix.wav')
run(inputs + ['-filter_complex', ';'.join(filt), '-map', '[out]', '-ar', '48000', mix])
run(['-i', pic, '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest',
     '-movflags', '+faststart', OUT])
print('wrote', OUT, {k: round(v, 2) for k, v in T.items()})
