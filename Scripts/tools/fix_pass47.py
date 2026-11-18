"""Finishes pass 46:
 - the hand under the bed uses her real reach (wrist 92 cm forward, 30 cm to her left in the Under clip) and she is a quarter
   larger for that moment, so the arm is long and the hand is big; the box goes with the hand and stops where a crouched
   player can still reach it;
 - Ruth's music box and the under-bed point are placed from the bed's real bounds;
 - her_step_01..04: a wet slap over a heavy low thud (library + our own wood steps, no paid generation);
 - Sneer and Brow shape keys on her face."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
P = "C:/GameDev/Unreal/WellnessCheck/"
R = P + "Source/WellnessCheck/"
L = P + "Scripts/level/"

edit(R + "WCEntity.h", [
    ('''	void Talk(float Seconds) { TalkLeft = FMath::Max(TalkLeft, Seconds); }''', '''	void Talk(float Seconds) { TalkLeft = FMath::Max(TalkLeft, Seconds); }
	FVector BoneWorld(FName Bone) const;'''),
])
s = io.open(R + "WCEntity.cpp", encoding="utf-8").read()
if "AWCEntity::BoneWorld" not in s:
    s = s.rstrip() + '''

FVector AWCEntity::BoneWorld(FName Bone) const
{
	return Body && Body->GetBoneIndex(Bone) != INDEX_NONE ? Body->GetBoneLocation(Bone) : GetActorLocation();
}
'''
    io.open(R + "WCEntity.cpp", "w", encoding="utf-8", newline="\n").write(s)

p = R + "WCStory.cpp"
s = io.open(p, encoding="utf-8").read()
a = s.index("// ---------------------------------------------------------------------------------------------- S7 the hand under the bed")
b = s.index("// ---------------------------------------------------------------------------------------------- S5 the attic")
s = s[:a] + '''// ---------------------------------------------------------------------------------------------- S7 the hand under the bed
// Slow.  He comes into Ruth's room and sees the music box on the floor; the view is held on it; her arm comes out from under the
// bed, closes on the box and draws it back under.  She is never seen.  Then he has to get down and take it back.
void AWCDirector::ScareUnderBed()
{
	if (Has(TEXT("underbed_done"))) return;
	Set(TEXT("underbed_done"));
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S7_hand"), PlaySeconds);
	for (TObjectIterator<UAudioComponent> It; It; ++It) if (It->GetWorld() == GetWorld() && It->Sound && It->Sound->GetName().Contains(TEXT("musicbox"))) It->FadeOut(2.5f, 0.f);
	AWCEntity* H = Her();
	AWCCharacter* P = Player();
	AWCInteractable* Box = Thing(TEXT("pick_keep_ruth"));
	if (!H || !P || !Box) return;
	bBusy = true;
	P->SetInputLocked(true);
	if (!P->IsFlashlightOn()) P->SetFlashlight(true);
	const FVector BoxFrom = Box->GetActorLocation();
	const FVector Under = Pos(TEXT("Her_Under"));
	const FVector Dir = (BoxFrom - Under).GetSafeNormal2D();
	const FVector Left(Dir.Y, -Dir.X, 0.f);
	const float K = 1.25f;                                       // for this she is a quarter larger: a long arm, a big hand
	// in the Under clip her left wrist lies 92 cm ahead of her and 30 cm to her left; the fingers go on past it
	FVector AtBox = BoxFrom - Dir * (92.f * K + 17.f) - Left * (30.f * K);
	AtBox.Z = Under.Z;
	const FVector Hidden = AtBox - Dir * 175.f;
	LookAtPoint = BoxFrom + FVector(0, 0, 6);
	LookAtUntil = Clock + 9.8;
	Box->bEnabled = false;
	H->Appear(Hidden, Dir.Rotation().Yaw, TEXT("Under"), true, 0.5f);
	H->SetActorScale3D(FVector(K));
	H->SetGlow(0.f);
	Tension = 0.8f;
	SetLoop(TEXT("amb"), TEXT("amb_house"), 0.1f, 1.5f);
	After(1.6f, [this, AtBox, BoxFrom, Dir]()
	{
		AWCEntity* E = Her();
		if (!E) return;
		FVector At = AtBox;
		const FVector Wrist = E->BoneWorld(TEXT("LeftHand")) - E->GetActorLocation();
		const float Fwd = FVector::DotProduct(Wrist, Dir);
		if (Fwd > 60.f && Fwd < 190.f) { At = BoxFrom - FVector(Wrist.X, Wrist.Y, 0.f) - Dir * 17.f; At.Z = AtBox.Z; }
		UE_LOG(LogWCStory, Display, TEXT("WC: S7 wrist offset fwd %.0f side %.0f"), Fwd, FVector::DotProduct(Wrist, FVector(Dir.Y, -Dir.X, 0.f)));
		E->Slide(At, 3.4f);
		PlayAt(TEXT("scratch_wall"), BoxFrom, 0.8f, 0.7f, 1500.f);
		Play2D(TEXT("sting_low"), 0.6f, EWCSnd::Music);
	});
	After(5.3f, [this, Box, BoxFrom, Hidden, Dir]()
	{
		// the fingers close; the box goes with them
		AWCEntity* E = Her();
		if (!E) return;
		PlayAt(TEXT("pickup"), BoxFrom, 0.9f, 0.7f, 1200.f);
		PlayAt(TEXT("drag_floor"), BoxFrom, 0.5f, 1.3f, 1200.f);
		const FVector HerAt = E->GetActorLocation();
		E->Slide(Hidden, 3.2f);
		for (int32 i = 1; i <= 66; ++i) After(i * 0.05f, [this, Box, BoxFrom, HerAt, Dir]()
		{
			AWCEntity* E2 = Her();
			if (!E2 || !IsValid(Box)) return;
			const float Back = FMath::Clamp(FVector::DotProduct(HerAt - E2->GetActorLocation(), Dir), 0.f, 100.f);
			Box->SetActorLocation(BoxFrom - Dir * Back);
		});
	});
	After(9.6f, [this, Box]()
	{
		if (AWCEntity* E = Her()) { E->Vanish(); E->SetActorScale3D(FVector(1.f)); }
		if (IsValid(Box)) Box->bEnabled = true;
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		bBusy = false;
		LookAtUntil = 0.0;
		Rest(140.f);
		ApplyWorldState();
		Think(TEXT("...It took it. It's under the bed."));
		ShowHint(TEXT("C: crouch"), 6.f);
		Checkpoint(TEXT("hand"));
	});
}

''' + s[b:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

# ---------------------------------------------------------------- level: the box sits just off the bed's open side
edit(L + "build_house.py", [
    ('''place(ow("Bed_02g", "Bed_Hospital_Sheet"), 640, -470, UZ, 180 + OW_YAW, KD, tags=["RuthBed"], name="RuthBed")''',
     '''_rb = place(ow("Bed_02g", "Bed_Hospital_Sheet"), 640, -470, UZ, 180 + OW_YAW, KD, tags=["RuthBed"], name="RuthBed")
_rbo, _rbe = _rb.get_actor_bounds(False)
RB_X, RB_EDGE = (_rbo.x, _rbo.y + _rbe.y) if 20 < _rbe.y < 160 else (640.0, -400.0)
log(f"RuthBed centre ({_rbo.x:.0f},{_rbo.y:.0f}) half ({_rbe.x:.0f},{_rbe.y:.0f},{_rbe.z:.0f}) open edge y={RB_EDGE:.0f}")'''),
    ('''pickup("pick_keep_ruth", "keep_ruth", "Ruth's music box", "Music_Box_Closed", 600, -338, UZ + 1, 30, grab=(16, 16, 12))
point("MusicBoxPoint", 600, -338, UZ + 20)''', '''pickup("pick_keep_ruth", "keep_ruth", "Ruth's music box", "Music_Box_Closed", RB_X, RB_EDGE + 52, UZ + 1, 30, grab=(16, 16, 12))
point("MusicBoxPoint", RB_X, RB_EDGE + 52, UZ + 20)'''),
    ('''point("Her_Under", 600, -480, UZ, 90)''', '''point("Her_Under", RB_X, RB_EDGE - 60, UZ, 90)'''),
])

# ---------------------------------------------------------------- her feet
edit(P + "Scripts/audio/lib_sfx.py", [
    ('''# footsteps overhead: several of our own wood steps in a row, heard through the ceiling''',
     '''# her feet: a wet slap (library) over a heavy low thud (our own wood step, slowed).  name: (slap pitch, wood step, slap delay ms)
HER_STEPS = {"her_step_01": (0.72, 1, 0), "her_step_02": (0.62, 3, 14), "her_step_03": (0.80, 2, 0), "her_step_04": (0.67, 5, 22)}
SLAP = (2, "WOODImpt_Hit Blood Spill Splat Wood Impact Light Hit Squelch Small Thump 03")
# footsteps overhead: several of our own wood steps in a row, heard through the ceiling'''),
    ('''    for name, (order, gap) in STEPS_ABOVE.items():''', '''    for name, (pitch, wood, delay) in HER_STEPS.items():
        dst = f"{OUT}/{name}.wav"
        if os.path.exists(dst) and not force:
            continue
        try:
            slap, origin = raw_copy(*SLAP)
            ff(["-i", slap, "-i", f"{OUT}/step_wood_0{wood}.wav", "-filter_complex",
                f"[0]aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,asetrate=48000*{pitch},aresample=48000,lowpass=f=5200,adelay={delay}:all=1,volume=0.9[w];"
                f"[1]asetrate=48000*0.55,aresample=48000,lowpass=f=650,volume=2.0[t];"
                f"[w][t]amix=inputs=2:normalize=0,apad=pad_dur=0.15,areverse,afade=t=in:d=0.12,areverse,alimiter=limit=0.9,volume=1.3[o]",
                "-map", "[o]", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", dst])
            credits.append(f"- {name}: {origin} + our own step_wood_0{wood}")
            print("  ", name, round(dur(dst), 2), "s")
            ok += 1
        except Exception as exc:
            print("  FAILED", name, str(exc)[:300])
    for name, (order, gap) in STEPS_ABOVE.items():'''),
])

# ---------------------------------------------------------------- her face
edit(P + "Scripts/her/build_her.py", [
    ('''print("HER scream: jaw verts", n_jaw, "gap verts", n_gap)''', '''print("HER scream: jaw verts", n_jaw, "gap verts", n_gap)
# SNEER: the upper lip on her left side lifts off the mouth.  BROW: the brow comes down over the eye.
sk_sneer = mesh.shape_key_add(name="Sneer", from_mix=False)
sk_brow = mesh.shape_key_add(name="Brow", from_mix=False)
EYE_Z = float(ecen[2])
n_sneer = n_brow = 0
for i, p in enumerate(co):
    x, y, z = float(p[0]), float(p[1]), float(p[2])
    if y > -14.0:
        continue
    front = 1.0 - sstep(-19.0, -14.0, y)
    u = z - LIP_Z
    sx_ = x - MOUTH_X
    if 0.75 <= u <= 5.2 and sx_ > -1.0:
        w_ = sstep(-1.0, 2.0, sx_) * (1.0 - sstep(5.0, 9.5, sx_)) * (1.0 - sstep(2.4, 5.2, u)) * front
        if w_ > 0.02:
            sk_sneer.data[i].co = inv_ @ Vector((x + 0.5 * w_, y - 0.9 * w_, z + 2.4 * w_))
            n_sneer += 1
    bz = z - (EYE_Z + 1.6)
    if 0.0 <= bz <= 8.0 and abs(x) < 11.0:
        w_ = sstep(0.0, 1.2, bz) * (1.0 - sstep(3.5, 8.0, bz)) * (1.0 - sstep(7.0, 11.0, abs(x))) * front
        if w_ > 0.02:
            sk_brow.data[i].co = inv_ @ Vector((x * (1.0 - 0.08 * w_), y - 1.1 * w_, z - 1.9 * w_))
            n_brow += 1
print("HER face: sneer verts", n_sneer, "brow verts", n_brow)'''),
    ('''    sk_scream.value = 0.0
    raise SystemExit(0)''', '''    sk_scream.value = 0.0
    for _nm, _keys in (("sneer_1", (sk_sneer,)), ("brow_1", (sk_brow,)), ("all_1", (sk_sneer, sk_brow))):
        for _k in _keys:
            _k.value = 1.0
        sk_scream.value = 0.3 if _nm == "all_1" else 0.0
        _cam.location = _tgt + Vector((0.15, -1, 0.0)).normalized() * 150
        _cam.rotation_euler = (_tgt - _cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "preview", _nm + ".png")
        bpy.ops.render.render(write_still=True)
        for _k in _keys:
            _k.value = 0.0
    sk_scream.value = 0.0
    raise SystemExit(0)'''),
])
print("ok")
