"""1. Edith looked like crumpled paper up close (seen in the lit grab photo): the FBX carries no tangents, and the import was
   told to take them from the file, so her normal map was applied on garbage tangents.  Import her normals and let the engine
   build the tangents.
2. Forest drive: a stronger wash on the road, and enough glow in the cabin to see the dash and wheel as shapes.
3. Bot: when it cannot get somewhere, it says what it is walking into."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
P = "C:/GameDev/Unreal/WellnessCheck/"
edit(P + "Scripts/level/import_assets.py", [
    ('''        sd.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)
        sd.set_editor_property("import_morph_targets", True)''', '''        sd.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
        try:
            sd.set_editor_property("normal_generation_method", unreal.FBXNormalGenerationMethod.MIKK_T_SPACE)
        except Exception as exc:
            log(f"mikk: {exc}")
        sd.set_editor_property("import_morph_targets", True)'''),
])
edit(P + "Scripts/level/forest.py", [
    ('''cpart(light_spot("RoadWash", CRX + 230, CRY, 120, 0, -17, 5200,''', '''cpart(light_spot("RoadWash", CRX + 230, CRY, 120, 0, -17, 8500,'''),
    ('''cpart(light_point("DashGlow", CRX + 44, CRY - 37, -40 + 92, 0.035,''', '''cpart(light_point("DashGlow", CRX + 44, CRY - 37, -40 + 92, 0.16,'''),
    ('''cpart(light_point("CabinFill", CRX - 10, CRY - 10, -40 + 138, 0.10,''', '''cpart(light_point("CabinFill", CRX - 10, CRY - 10, -40 + 138, 0.55,'''),
])
edit(P + "Source/WellnessCheck/WCAuto.cpp", [
    ('''					UE_LOG(LogWCAuto, Error, TEXT("WCAUTO FAIL unreachable %s%s"), *S.Arg.ToString(), bForce ? TEXT(" -> teleported") : TEXT(""));''',
     '''					{
						FHitResult Hit;
						FCollisionQueryParams Q(SCENE_QUERY_STAT(WCAutoWall), false, P);
						const FVector From = Loc - FVector(0, 0, 30.f);
						const bool bHit = GetWorld()->SweepSingleByChannel(Hit, From, From + Dir * 90.f, FQuat::Identity, ECC_Pawn, FCollisionShape::MakeSphere(22.f), Q);
						UE_LOG(LogWCAuto, Error, TEXT("WCAUTO WHY %s: walking into %s (%s) %.0f cm ahead, at (%.0f,%.0f,%.0f) heading (%.2f,%.2f)"), *S.Arg.ToString(),
							bHit && Hit.GetActor() ? *Hit.GetActor()->GetActorNameOrLabel() : TEXT("nothing found"), bHit && Hit.GetComponent() ? *Hit.GetComponent()->GetName() : TEXT("-"), bHit ? Hit.Distance : -1.f, Loc.X, Loc.Y, Loc.Z, Dir.X, Dir.Y);
					}
					UE_LOG(LogWCAuto, Error, TEXT("WCAUTO FAIL unreachable %s%s"), *S.Arg.ToString(), bForce ? TEXT(" -> teleported") : TEXT(""));'''),
])
print("ok")
