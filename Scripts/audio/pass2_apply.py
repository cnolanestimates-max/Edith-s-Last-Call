"""Audio pass 2: put approved sounds into the game.

  <numpy python> pass2_apply.py all                 every sound of the pass
  <numpy python> pass2_apply.py stings wheel gun    by group (stings, wheel, gun, doors, thumps, steps, creaks, electric, foley, beds)
  <numpy python> pass2_apply.py sting_hit --dry     single sounds; --dry only lists

Copies SourceArt/AudioPass2/new/<name>.wav over SourceArt/Audio/<name>.wav (the old files stay in git history) and adds
the names to SourceArt/AudioPass2/applied.json.  Then, with no UnrealEditor running:

  Scripts/tools/pass2_import.ps1        imports only those files and keeps each asset's loop flag and volume
"""
import json, os, shutil, sys
import pass2_build as B

LIST = B.S.ROOT + "/SourceArt/AudioPass2/applied.json"

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry" in sys.argv
    names = []
    for a in args:
        names += list(B.RECIPES) if a == "all" else B.GROUPS.get(a, [a])
    done = json.load(open(LIST)) if os.path.exists(LIST) else []
    for n in names:
        src = f"{B.NEW}/{n}.wav"
        if not os.path.exists(src):
            print(f"{n}: not built, skipped")
            continue
        print(("would copy " if dry else "copied ") + n)
        if not dry:
            shutil.copyfile(src, f"{B.OLD}/{n}.wav")
            if n not in done:
                done.append(n)
    if not dry:
        json.dump(sorted(done), open(LIST, "w"), indent=1)
        print(f"{len(done)} sounds listed in {LIST}")
