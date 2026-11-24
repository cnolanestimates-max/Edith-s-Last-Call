#include "WCFamilyPhotos.h"
#include "WCWorld.h"

#include "Components/DecalComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/Texture2D.h"
#include "EngineUtils.h"
#include "Materials/MaterialInstanceDynamic.h"

namespace
{
struct FPrintSurface
{
	FVector Center;
	double Width;
	double Height;
	FVector Right = FVector::XAxisVector;
	FVector Up = FVector::ZAxisVector;
};

// Local dimensions of the actual paper inside each kit frame, in cm.
const TMap<FName, FPrintSurface> Surfaces = {
	{TEXT("SM_Portrait_Large"), {{0,-2.95,60},72,102}},
	{TEXT("SM_Portrait_Small"), {{0,-2.42,30},33,48}},
	{TEXT("SM_Portrait_Oval"), {{0,1.94,37.5},41,61}},
	{TEXT("SM_Portrait_Slashed"), {{0,-2.42,47.5},58,83}},
	{TEXT("SM_Portrait_Glowing_Eyes"), {{0,-2.42,40},48,68}},
	{TEXT("SM_Portrait_Easel"), {{0,19.33,104.76},48,68,FVector::XAxisVector,{0,-0.17365,0.98481}}},
	{TEXT("SM_Picture_Frame_Broken_Glass"), {{0,-16.55,24.28},32,42,FVector::XAxisVector,{0,-0.25882,0.96593}}},
	{TEXT("SM_Picture_Frame_Fallen"), {{0,0,1.76},32,42,{0.96593,-0.25882,0},{-0.25866,-0.96534,0.0349}}}
};

// The curated wall pictures tell the family's story along the route through the house.
// These are the existing frame origins. Loose frames get a stable selection from the clean album.
struct FPlacement { FVector Origin; const TCHAR* Print; bool bClaws = false; double WallOffsetY = 0; };
const FPlacement WallAlbum[] = {
	{{1400,181,130},TEXT("Porch")}, {{600,181,150},TEXT("Anniversary")}, {{1250,-181,140},TEXT("Scratched")},
	{{250,-731,165},TEXT("Christmas"),true,31}, {{470,-731,175},TEXT("Baking")}, {{783,-420,150},TEXT("Walter")},
	{{783,-300,160},TEXT("Siblings")}, {{783,250,130},TEXT("Christmas")},
	{{600,181,480},TEXT("Porch")}, {{1300,-181,490},TEXT("VowsDefaced")},
	{{2000,-181,130},TEXT("Baking")}, {{2360,181,150},TEXT("Walter")}, {{2250,-181,160},TEXT("Anniversary")},
	{{2200,-581,185},TEXT("Walter"),false,22}, {{1990,-581,170},TEXT("Anniversary")}, {{1634,-260,170},TEXT("Siblings")},
	{{2200,181,480},TEXT("Christmas")}, {{2000,-181,490},TEXT("EdithGarden")},
	{{2400,-181,490},TEXT("Porch"),true}, {{1682,-350,464},TEXT("Daniel")}, {{1000,420,700},TEXT("Attic")}
};
const TCHAR* CleanAlbum[] = {TEXT("Porch"),TEXT("Baking"),TEXT("Siblings"),TEXT("Christmas"),TEXT("Walter"),TEXT("Anniversary"),TEXT("Daniel")};

FLinearColor AxisParameter(const FVector& Axis, const FVector& Center, double Offset)
{
	return FLinearColor(Axis.X, Axis.Y, Axis.Z, Offset - FVector::DotProduct(Axis, Center));
}

void MountPrint(UStaticMeshComponent* Frame, const FPrintSurface& S, UTexture2D* Print,
	UMaterialInterface* Paper, UMaterialInterface* Hidden, UMaterialInterface* Glass, bool bParentsCrop, float WearSeed)
{
	const int32 PaperIndex = Frame->GetMaterialIndex(TEXT("M_Portrait"));
	UMaterialInstanceDynamic* MID = Frame->CreateDynamicMaterialInstance(PaperIndex, Paper);
	if (!MID) return;
	// All original scans are 4:5. Crop to the moulding while retaining the faces' proportions.
	const double PrintWidth = FMath::Max(S.Width, S.Height * .8) / (bParentsCrop ? .53 : 1.);
	const float CenterU = bParentsCrop ? .49f : .5f;
	const float CenterV = bParentsCrop ? .30f : .5f;
	MID->SetVectorParameterValue(TEXT("PhotoU"), AxisParameter(S.Right / PrintWidth, S.Center, CenterU));
	MID->SetVectorParameterValue(TEXT("PhotoV"), AxisParameter(-S.Up / (PrintWidth / .8), S.Center, CenterV));
	const bool bOval = Frame->GetStaticMesh()->GetFName() == TEXT("SM_Portrait_Oval");
	MID->SetVectorParameterValue(TEXT("PaperShape"), FLinearColor(PrintWidth / S.Width, PrintWidth / (.8 * S.Height), bOval ? 1.f : 0.f));
	MID->SetVectorParameterValue(TEXT("PaperWeather"), FLinearColor(CenterU, CenterV, WearSeed));
	MID->SetTextureParameterValue(TEXT("Photograph"), Print);
	// The kit builds a mannequin face above the canvas out of several separate mesh sections.
	for (const TCHAR* Slot : {TEXT("M_PortraitFace"),TEXT("M_PortraitDark"),TEXT("M_Soot"),TEXT("M_EyeGlow")})
	{
		const int32 Index = Frame->GetMaterialIndex(FName(Slot));
		if (Index != INDEX_NONE) Frame->SetMaterial(Index, Hidden);
	}
	const int32 GlassIndex = Frame->GetMaterialIndex(TEXT("M_Glass"));
	if (GlassIndex != INDEX_NONE) Frame->SetMaterial(GlassIndex, Glass);
}

void ScoreFrame(UStaticMeshComponent* Frame, UMaterialInterface* Scratches)
{
	if (!Scratches) return;
	UDecalComponent* Marks = NewObject<UDecalComponent>(Frame->GetOwner());
	Marks->SetupAttachment(Frame);
	Marks->SetRelativeLocationAndRotation(FVector(15,1,66), FRotator(0,-90,0));
	// Shallow projection reaches the print and raised moulding, ending before the house wall.
	Marks->DecalSize = FVector(5.8,57,62);
	Marks->SetFadeScreenSize(.001f);
	Marks->SetSortOrder(12);
	Marks->SetDecalMaterial(Scratches);
	Marks->RegisterComponent();
}
}

void UWCFamilyPhotos::OnWorldBeginPlay(UWorld& World)
{
	Super::OnWorldBeginPlay(World);
	if (!World.GetMapName().EndsWith(TEXT("House"))) return;
	const FString Folder = TEXT("/Game/WC/FamilyPhotos/");
	auto Material = [&Folder](const TCHAR* Name) { return LoadObject<UMaterialInterface>(nullptr, *(Folder + Name)); };
	UMaterialInterface* Paper = Material(TEXT("M_FamilyPrint"));
	UMaterialInterface* Hidden = Material(TEXT("M_HidePortraitRelief"));
	UMaterialInterface* Glass = Material(TEXT("M_PhotoGlass"));
	UMaterialInterface* Wood = Material(TEXT("MI_FrameWood"));
	UMaterialInterface* Brass = Material(TEXT("MI_FrameBrass"));
	UMaterialInterface* Scratches = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Decals/MD_scratches"));
	if (!Paper || !Hidden || !Glass) return;
	TMap<FName, UTexture2D*> Prints;
	int32 Count = 0, Clawed = 0;
	for (TActorIterator<AStaticMeshActor> It(&World); It; ++It)
	{
		UStaticMeshComponent* Frame = It->GetStaticMeshComponent();
		const UStaticMesh* Mesh = Frame->GetStaticMesh();
		const FPrintSurface* Surface = Mesh ? Surfaces.Find(Mesh->GetFName()) : nullptr;
		if (!Surface) continue;
		const FVector P = It->GetActorLocation();
		const FIntVector Cell(FMath::RoundToInt(P.X), FMath::RoundToInt(P.Y), FMath::RoundToInt(P.Z));
		FName Name(CleanAlbum[GetTypeHash(Cell) % UE_ARRAY_COUNT(CleanAlbum)]);
		bool bClaws = false;
		FVector Offset = FVector::ZeroVector;
		if (Mesh->GetName().StartsWith(TEXT("SM_Portrait_")))
		{
			for (const FPlacement& Placement : WallAlbum)
			{
				if (FVector::DistSquared(P, Placement.Origin) < FMath::Square(35.0))
				{
					Name = FName(Placement.Print);
					bClaws = Placement.bClaws;
					// The peeling plaster and the chimney breast project in front of their base walls.
					Offset.Y = Placement.WallOffsetY;
					break;
				}
			}
		}
		else if (Mesh->GetName().StartsWith(TEXT("SM_Picture_Frame_")))
		{
			// Floor-level kit props were placed at the subfloor. Sit them on the visible finish.
			if (FMath::IsNearlyZero(P.Z, .1)) Offset.Z = 8;
			else if (FMath::IsNearlyEqual(P.Z, 350., .1) || FMath::IsNearlyEqual(P.Z, 700., .1)) Offset.Z = 2;
		}
		if (!Offset.IsZero())
		{
			const EComponentMobility::Type OriginalMobility = Frame->Mobility;
			Frame->SetMobility(EComponentMobility::Movable);
			Frame->AddWorldOffset(Offset, false, nullptr, ETeleportType::TeleportPhysics);
			Frame->SetMobility(OriginalMobility);
		}
		// Both states of the falling photograph show the same parents, with only his eyes struck out.
		const bool bFallingClue = It->ActorHasTag(TEXT("Hide_framefall")) || It->ActorHasTag(TEXT("Show_framefall"));
		if (bFallingClue) Name = TEXT("Scratched");
		UTexture2D*& Photo = Prints.FindOrAdd(Name);
		if (!Photo) Photo = LoadObject<UTexture2D>(nullptr, *(Folder + Name.ToString()));
		if (!Photo) continue;
		// Both poses of the falling clue share a stain pattern. Other prints weather independently.
		const float WearSeed = bFallingClue ? .42f : (GetTypeHash(Cell) % 1021) / 1021.f;
		MountPrint(Frame, *Surface, Photo, Paper, Hidden, Glass, bFallingClue, WearSeed);
		for (const FName Slot : {FName(TEXT("M_WoodBlack")), FName(TEXT("M_WoodLight")), FName(TEXT("M_Gold"))})
		{
			const int32 Index = Frame->GetMaterialIndex(Slot);
			UMaterialInterface* Finish = Slot == TEXT("M_Gold") ? Brass : Wood;
			if (Index != INDEX_NONE && Finish) Frame->SetMaterial(Index, Finish);
		}
		if (bClaws) { ScoreFrame(Frame, Scratches); ++Clawed; }
		++Count;
	}
	for (TActorIterator<AWCLook> It(&World); It; ++It)
	{
		if (It->WCId == TEXT("look_hall_portrait")) It->Text = TEXT("Little white cuts right across the eyes. Every pair but hers.");
		else if (It->WCId == TEXT("look_mantel_photos")) It->Text = TEXT("Christmas morning. The cuts run off the photograph and into the frame.");
		else if (It->WCId == TEXT("look_den_portrait")) It->Text = TEXT("Walter Harrow. His eyes are cut like the rest. Whoever took this got him to smile.");
		else if (It->WCId == TEXT("look_attic_easel")) It->Text = TEXT("I saw this picture downstairs. There were four of them. The gray one is sitting on top of the print, in thick house paint.");
	}
	UE_LOG(LogTemp, Display, TEXT("Harrow album: %d frames, %d different prints, %d claw-marked frames"), Count, Prints.Num(), Clawed);
}
