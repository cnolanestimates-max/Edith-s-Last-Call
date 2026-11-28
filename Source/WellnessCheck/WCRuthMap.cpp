#include "WCRuthMap.h"
#include "WCDirector.h"
#include "WCWorld.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/Texture2D.h"
#include "EngineUtils.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"

namespace
{
	const FName PieceFlags[] = {
		TEXT("ruth_map_foyer"), TEXT("ruth_map_music"), TEXT("ruth_map_service"), TEXT("ruth_map_front_up"),
		TEXT("ruth_map_rear_up"), TEXT("ruth_map_attic"), TEXT("ruth_map_cellar")
	};
	const FName RevealFlags[] = {
		NAME_None, TEXT("ruth_metronome_open"), TEXT("ruth_washboard_open"), TEXT("ruth_linen_open"),
		TEXT("ruth_tins_open"), TEXT("ruth_case_open"), TEXT("ruth_preserves_open")
	};
	const TCHAR* PuzzleTargets[] = {
		TEXT("ruth_foyer_envelope"), TEXT("ruth_metronome"), TEXT("ruth_washboard"), TEXT("ruth_linen"),
		TEXT("ruth_tin_moon"), TEXT("ruth_attic_case"), TEXT("ruth_shark_tin")
	};
	const TCHAR* PuzzlePrompts[] = {
		TEXT("Take the first piece of Ruth's map"), TEXT("Set the metronome to the wave"), TEXT("Lift the washboard"), TEXT("Pull the ribbon on the checked pillowcase"),
		TEXT("Press the moon tin"), TEXT("Lift the loose lining in Danny's case"), TEXT("Turn the tin with the scratched shark")
	};
	const FVector PuzzlePositions[] = {
		{326,180,143}, {1041,-932,96}, {2358,811,102}, {2820,504,438},
		{2632,-515,434}, {900,-380,741}, {610,-514,-264}
	};
	const FVector ScrapPositions[] = {
		{326,180,143}, {1023,-926,79}, {2344,789,79}, {2802,498,429},
		{2658,-497,429}, {879,-390,748}, {585,-507,-269}
	};
	const FVector StashPositions[] = {
		{211,-350,55}, {0,0,0}, {2695,-550,429}, {922,-381,748}
	};
	const FName KeepsakeFlags[] = { TEXT("ruth_glass_found"), NAME_None, TEXT("ruth_compass_found"), TEXT("ruth_photo_found") };
	const TCHAR* TinTargets[] = { TEXT("ruth_tin_moon"), TEXT("ruth_tin_wave"), TEXT("ruth_tin_star") };

	FName TargetEvent(const TCHAR* Target) { return FName(*(FString(TEXT("use:")) + Target)); }
	FName ScrapTarget(int32 Index) { return FName(*FString::Printf(TEXT("ruth_scrap_%d"), Index + 1)); }
	FName StashTarget(int32 Index) { return FName(*FString::Printf(TEXT("ruth_stash_%d"), Index)); }

	void Visible(AWCInteractable* A, bool bVisible)
	{
		if (!A) return;
		A->bEnabled = bVisible;
		A->SetActorHiddenInGame(!bVisible);
		A->SetActorEnableCollision(bVisible);
	}

	AWCUsable* Spot(AWCDirector& D, FName Id, const TCHAR* Prompt, const FVector& At, const FVector& Grab,
		UStaticMesh* Model = nullptr, UMaterialInterface* Surface = nullptr,
		const FVector& Scale = FVector::OneVector, float Yaw = 0.f)
	{
		const FTransform Pose(FRotator(0, Yaw, 0), At);
		AWCUsable* A = D.GetWorld()->SpawnActorDeferred<AWCUsable>(AWCUsable::StaticClass(), Pose, &D, nullptr, ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
		if (!A) return nullptr;
		A->WCId = Id;
		A->Prompt = Prompt;
		A->GrabExtent = Grab;
		A->Mesh->SetCollisionProfileName(TEXT("NoCollision"));
		if (Model)
		{
			A->Mesh->SetStaticMesh(Model);
			A->Mesh->SetRelativeScale3D(Scale);
			if (Surface) A->Mesh->SetMaterial(0, Surface);
		}
		A->FinishSpawning(Pose);
		return A;
	}

	void MoveProp(UWorld* World, const TCHAR* MeshName, const FVector& Near, const FVector& FoundOffset, bool bRevealed)
	{
		for (TActorIterator<AStaticMeshActor> It(World); It; ++It)
		{
			UStaticMeshComponent* Comp = It->GetStaticMeshComponent();
			if (!Comp || !Comp->GetStaticMesh() || Comp->GetStaticMesh()->GetFName() != MeshName ||
				FVector::DistSquared(It->GetActorLocation(), Near) > FMath::Square(35.0)) continue;
			// Keep the authored root transform for subsequent reloads.
			Comp->SetMobility(EComponentMobility::Movable);
			if (USceneComponent* Pivot = It->GetRootComponent(); Pivot != Comp)
				Comp->SetRelativeLocation(bRevealed ? FoundOffset : FVector::ZeroVector);
			else
				It->SetActorLocation(Near + (bRevealed ? FoundOffset : FVector::ZeroVector));
			return;
		}
	}
}

namespace WCRuthMap
{
	const FStash Stashes[4] = {
		{0, {714,-280}, TEXT("ruth_sea_glass"), TEXT("Ruth's sea glass"), TEXT("Look beside the piano bench on Treasure Island.")},
		{2, {2417,797}, TEXT("ammo_scullery"), TEXT("Spare cartridges"), TEXT("There is a box on the scullery wash bench.")},
		{4, {2855,-269}, TEXT("ruth_compass"), TEXT("Danny's compass"), TEXT("Check the dress-pattern table in the box room.")},
		{5, {1330,-325}, TEXT("ruth_photo"), TEXT("Ruth and Danny's photograph"), TEXT("Tucked into Danny's travel case in the Crow's Nest.")},
	};

	Floor FloorForPiece(int32 Piece)
	{
		static constexpr Floor Pages[] = { Floor::Ground, Floor::Ground, Floor::Ground, Floor::Upper, Floor::Upper, Floor::Attic, Floor::Cellar };
		return Pages[Piece];
	}

	const TCHAR* FloorName(Floor Page)
	{
		switch (Page)
		{
		case Floor::Ground: return TEXT("First floor");
		case Floor::Upper: return TEXT("Upstairs");
		case Floor::Attic: return TEXT("Crow's Nest");
		case Floor::Cellar: return TEXT("The Brig");
		}
		return TEXT("");
	}

	FVector2D PlanPoint(Floor Page, const FVector2D& World)
	{
		const bool bSmall = Page == Floor::Attic || Page == Floor::Cellar;
		const double X = bSmall ? 153. + World.X * .238 : 52. + World.X * .178;
		const double Y = Page == Floor::Ground ? 155. + World.Y * .141 : 152. + World.Y * .202;
		return {X / 690., Y / 306.};
	}

	FRoom RoomAt(const FVector& P)
	{
		const auto Room = [](int32 Piece, double X0, double Y0, double X1, double Y1)
		{
			return FRoom{Piece, FBox2D(FVector2D(X0,Y0), FVector2D(X1,Y1)), FBox2D(ForceInit)};
		};
		const double X = P.X, Y = P.Y;
		if (FMath::Abs(P.Z + 350.) < 75. && X >= 0. && X < 1600.)
		{
			if (Y >= -600. && Y < -200. && X < 800.) return Room(6,0,-600,800,-200);
			if (FMath::Abs(Y) < 200.) return Room(6,0,-200,1600,200);
		}
		if (FMath::Abs(P.Z - 700.) < 75. && X >= 0. && X < 1600. && FMath::Abs(Y) < 600.)
			return Room(5,0,-600,1600,600);
		const bool bUpper = FMath::Abs(P.Z - 350.) < 75.;
		if ((!bUpper && FMath::Abs(P.Z) >= 75.) || X < 0. || X >= (bUpper ? 3420. : 2800.)) return {};
		if (bUpper)
		{
			const int32 Piece = X < 1600. ? 3 : 4;
			if (FMath::Abs(Y) < 200.) return X < 1600. ? Room(3,0,-200,1600,200) : Room(4,1600,-200,3420,200);
			if (FMath::Abs(Y) >= 600.) return {};
			static constexpr double Cuts[] = {0,800,1600,2400,3020,3420};
			for (int32 I = 1; I < UE_ARRAY_COUNT(Cuts); ++I)
				if (X < Cuts[I]) return Room(Piece,Cuts[I-1],Y < 0. ? -600. : 200.,Cuts[I],Y < 0. ? -200. : 600.);
		}
		if (Y < (X < 800. ? -750. : -600.) && Y > -1015. && X > 550. && X < 1205.)
		{
			FRoom Music = Room(0,800,-1015,1205,-600);
			Music.Annex = FBox2D(FVector2D(550,-1015), FVector2D(800,-750));
			return Music;
		}
		if (X > 1690. && X < 2510. && Y > 600. && Y < 892.) return Room(2,1690,600,2510,892);
		if (Y >= 600. || Y < (X < 800. ? -750. : -600.)) return {};
		if (FMath::Abs(Y) < 200.)
		{
			if (X < 400.) return Room(0,0,-200,400,200);
			if (X < 800.) return Room(0,400,-200,800,200);
			if (X < 1600.) return Room(1,800,-200,1600,200);
			return Room(2,1600,-200,2800,200);
		}
		if (X < 800.) return Y < 0. ? Room(0,0,-750,800,-200) : Room(0,0,200,800,600);
		if (X < 1600.) return Y < 0. ? Room(1,800,-600,1600,-200) : Room(1,800,200,1600,600);
		if (Y < 0.) return X < 2400. ? Room(2,1600,-600,2400,-200) : Room(2,2400,-600,2800,-200);
		return X < 2000. ? Room(2,1600,200,2000,600) : Room(2,2000,200,2800,600);
	}

	bool OwnsPiece(const AWCDirector& Director, int32 Piece)
	{
		return Piece >= 0 && Piece < PieceCount && Director.Has(PieceFlags[Piece]);
	}

	int32 Count(const AWCDirector& Director)
	{
		int32 Total = 0;
		for (int32 I = 0; I < PieceCount; ++I) Total += OwnsPiece(Director,I);
		return Total;
	}

	bool HasFloor(const AWCDirector& Director, Floor Page)
	{
		for (int32 I = 0; I < PieceCount; ++I)
			if (FloorForPiece(I) == Page && OwnsPiece(Director,I)) return true;
		return false;
	}
}

void AWCDirector::RuthMapBegin()
{
	if (RuthMapActors.Num()) { RefreshRuthMap(); return; }
	if (!Thing(TEXT("music_lesson"))) return;
	UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube"));
	UStaticMesh* Cylinder = LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	UStaticMesh* Envelope = LoadObject<UStaticMesh>(nullptr,TEXT("/Game/WC/Props/HouseDetails/SM_BathLetter.SM_BathLetter"));
	UMaterialInterface* Paper = LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WC/Materials/MI_PaperOld.MI_PaperOld"));
	UMaterialInterface* Brass = LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WC/Materials/MI_Brass.MI_Brass"));
	UMaterialInterface* Tin = LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WC/Materials/MI_Rust.MI_Rust"));
	const auto Add = [&](FName Id, const TCHAR* Prompt, FVector At, FVector Grab, UStaticMesh* Mesh = nullptr,
		UMaterialInterface* Mat = nullptr, FVector Scale = FVector::OneVector, float Yaw = 0.f)
	{
		RuthMapActors.Add(Id,Spot(*this,Id,Prompt,At,Grab,Mesh,Mat,Scale,Yaw));
	};
	for (int32 I = 0; I < WCRuthMap::PieceCount; ++I)
	{
		const bool bTin = I == 4 || I == 6;
		Add(PuzzleTargets[I],PuzzlePrompts[I],PuzzlePositions[I],
			I == 0 ? FVector(21,6,17) : I == 2 ? FVector(18,13,21) : FVector(10,9,9),
			I == 0 ? (Envelope ? Envelope : Cube) : bTin ? Cylinder : nullptr,
			I == 0 && !Envelope ? Paper : bTin ? Tin : nullptr,
			I == 0 ? (Envelope ? FVector(1.55,1.55,1.) : FVector(.32,.24,.01)) : bTin ? FVector(.14,.14,.10) : FVector::OneVector);
		Add(ScrapTarget(I),TEXT("Take Ruth's map scrap"),ScrapPositions[I],FVector(9,6,5),Cube,Paper,FVector(.13,.085,.006),-11.f + 7.f * I);
	}
	if (AWCInteractable* FirstScrap = RuthMapActors.FindRef(PuzzleTargets[0]).Get())
	{
		FirstScrap->Mesh->SetRelativeRotation(FRotationMatrix::MakeFromXZ(FVector::ForwardVector, -FVector::RightVector).Rotator());
		UTextRenderComponent* Title = NewObject<UTextRenderComponent>(FirstScrap);
		Title->SetupAttachment(FirstScrap->Root);
		Title->SetRelativeLocation(FVector(0,-1.4,-4));
		Title->SetRelativeRotation(FRotator(0,-90,0));
		Title->SetHorizontalAlignment(EHTA_Center);
		Title->SetVerticalAlignment(EVRTA_TextCenter);
		Title->SetWorldSize(3.f);
		Title->SetTextRenderColor(FColor(60,34,24));
		Title->SetText(FText::FromString(TEXT("RUTH'S MAP")));
		Title->RegisterComponent();
	}
	Add(TinTargets[1],TEXT("Press the wave tin"),FVector(2652,-511,434),FVector(8,7,9),Cylinder,Tin,FVector(.14,.14,.10));
	Add(TinTargets[2],TEXT("Press the star tin"),FVector(2672,-504,434),FVector(8,7,9),Cylinder,Tin,FVector(.14,.14,.10));
	static const TCHAR* Chalk[] = {TEXT(")"),TEXT("~"),TEXT("*")};
	for (int32 I = 0; I < UE_ARRAY_COUNT(TinTargets); ++I)
	{
		if (AWCInteractable* A = RuthMapActors.FindRef(TinTargets[I]).Get())
		{
			UTextRenderComponent* Mark = NewObject<UTextRenderComponent>(A);
			Mark->SetupAttachment(A->Mesh);
			Mark->SetAbsolute(false,false,true);
			Mark->SetRelativeLocation(FVector(0,0,52));
			Mark->SetRelativeRotation(FRotator(90,0,0));
			Mark->SetWorldSize(7.f);
			Mark->SetHorizontalAlignment(EHTA_Center);
			Mark->SetVerticalAlignment(EVRTA_TextCenter);
			Mark->SetTextRenderColor(FColor(208,198,171));
			Mark->SetText(FText::FromString(Chalk[I]));
			Mark->RegisterComponent();
		}
	}
	UStaticMesh* Glass = LoadObject<UStaticMesh>(nullptr,TEXT("/Game/HorrorHouseKit/Meshes/Clutter_Debris/SM_Glass_Shards_Small.SM_Glass_Shards_Small"));
	Add(StashTarget(0),TEXT("Take Ruth's sea glass"),StashPositions[0],FVector(8,8,6),Glass,nullptr,FVector(.24));
	Add(StashTarget(2),TEXT("Take Danny's brass compass"),StashPositions[2],FVector(8,8,6),Cylinder,Brass,FVector(.105,.105,.024));
	if (AWCInteractable* Compass = RuthMapActors.FindRef(StashTarget(2)).Get())
	{
		const auto CompassPart = [&](UStaticMesh* Mesh, UMaterialInterface* Mat, FVector At, FVector Scale, float Yaw)
		{
			UStaticMeshComponent* Part = NewObject<UStaticMeshComponent>(Compass);
			Part->SetupAttachment(Compass->Root);
			Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			Part->SetStaticMesh(Mesh);
			Part->SetMaterial(0,Mat);
			Part->SetRelativeTransform(FTransform(FRotator(0,Yaw,0),At,Scale));
			Part->RegisterComponent();
		};
		CompassPart(Cylinder,Paper,FVector(0,0,1.3),FVector(.085,.085,.007),0);
		CompassPart(Cube,Tin,FVector(0,0,1.9),FVector(.068,.011,.004),32);
	}
	UStaticMesh* Plane = LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Plane.Plane"));
	UMaterialInterface* PhotoPrint = LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WC/FamilyPhotos/M_FamilyPrint.M_FamilyPrint"));
	UTexture2D* Siblings = LoadObject<UTexture2D>(nullptr,TEXT("/Game/WC/FamilyPhotos/Siblings.Siblings"));
	if (PhotoPrint && Siblings)
	{
		UMaterialInstanceDynamic* Print = UMaterialInstanceDynamic::Create(PhotoPrint,this);
		Print->SetTextureParameterValue(TEXT("Photograph"),Siblings);
		PhotoPrint = Print;
	}
	Add(StashTarget(3),TEXT("Take the Harrow photograph"),StashPositions[3],FVector(10,7,5),
		Plane ? Plane : Cube,PhotoPrint ? PhotoPrint : Paper,FVector(.12,.085,.004),24.f);

	const auto Write = [&](const TCHAR* Id, const TCHAR* Addition)
	{
		if (AWCNote* Page = Cast<AWCNote>(Thing(Id))) Page->Body += Addition;
	};
	Write(TEXT("music_lesson"),TEXT("\n\nRuth's pencil on the back: The next scrap is in the tick-tock. Slide the weight up to the little moon."));
	Write(TEXT("linen_checkout"),TEXT("\n\nFound a ribbon in the checked pillowcase. Ruth must have sewn it in herself. I left it where it was."));
	Write(TEXT("boxroom_patterns"),TEXT("\n\nThree tins below, each with a chalk mark. A child's writing on the wrapper reads: My lock is moon, wave, star. Press them like that, Danny."));
	RefreshRuthMap();
}

void AWCDirector::RefreshRuthMap()
{
	if (RuthMapActors.IsEmpty()) return;
	const auto Get = [&](FName Id) -> AWCInteractable*
	{
		const TWeakObjectPtr<AWCInteractable>* Entry = RuthMapActors.Find(Id);
		return Entry ? Entry->Get() : nullptr;
	};
	for (int32 I = 0; I < WCRuthMap::PieceCount; ++I)
	{
		const bool bOwned = WCRuthMap::OwnsPiece(*this,I);
		const bool bOpen = I != 0 && Has(RevealFlags[I]);
		Visible(Get(PuzzleTargets[I]),!bOwned && !bOpen);
		Visible(Get(ScrapTarget(I)),!bOwned && bOpen);
	}
	const bool bTins = !Has(RevealFlags[4]) && !WCRuthMap::OwnsPiece(*this,4);
	for (int32 I = 0; I < UE_ARRAY_COUNT(TinTargets); ++I)
	{
		if (AWCInteractable* Tin = Get(TinTargets[I]))
		{
			Tin->SetActorHiddenInGame(false);
			Tin->bEnabled = bTins;
			Tin->SetActorEnableCollision(bTins);
			Tin->Mesh->SetRelativeLocation(FVector(0,0,!bTins || I < RuthTinStep ? -3.f : 0.f));
		}
	}
	if (AWCInteractable* Shark = Get(PuzzleTargets[6]); Shark && Has(RevealFlags[6]))
	{
		Shark->SetActorHiddenInGame(false);
		Shark->Mesh->SetRelativeLocation(FVector(18,-8,0));
	}
	if (RuthMetronomeStep == 0)
		if (AWCInteractable* Meter = Get(PuzzleTargets[1])) Meter->Prompt = PuzzlePrompts[1];
	for (const int32 I : {0,2,3})
	{
		const bool bTaken = Has(KeepsakeFlags[I]) || HasItem(WCRuthMap::Stashes[I].Item);
		if (bTaken) Items.Add(WCRuthMap::Stashes[I].Item);
		Visible(Get(StashTarget(I)),!bTaken && (I != 3 || Has(RevealFlags[5])));
	}
	MoveProp(GetWorld(),TEXT("SM_SculleryWashSet"),FVector(2357.7,825,78.5),FVector(10,12,0),Has(RevealFlags[2]));
	MoveProp(GetWorld(),TEXT("SM_LinenStackSet"),FVector(2821,518,429.4),FVector(8,9,0),Has(RevealFlags[3]));
}

bool AWCDirector::RuthMapEvent(FName EventId)
{
	if (EventId == TEXT("locked:sitting") && !Has(TEXT("ruth_tried_sitting"))) RememberAtCheckpoint(TEXT("ruth_tried_sitting"));
	if (EventId == TEXT("locked:up_ell") && !Has(TEXT("ruth_tried_rear"))) RememberAtCheckpoint(TEXT("ruth_tried_rear"));
	if (!EventId.ToString().StartsWith(TEXT("use:ruth_"))) return false;
	for (int32 I = 0; I < WCRuthMap::PieceCount; ++I)
	{
		if (EventId == TargetEvent(*ScrapTarget(I).ToString()) || (I == 0 && EventId == TargetEvent(PuzzleTargets[0])))
		{
			if (WCRuthMap::OwnsPiece(*this,I) || (I != 0 && !Has(RevealFlags[I]))) return true;
			const bool bFirst = WCRuthMap::Count(*this) == 0;
			RememberAtCheckpoint(PieceFlags[I]);
			Play2D(TEXT("paper"),.75f);
			ShowToast(FString::Printf(TEXT("Ruth's map  %d / %d scraps"),WCRuthMap::Count(*this),WCRuthMap::PieceCount));
			if (bFirst) ShowHint(TEXT("M: unfold Ruth's map"),7.f);
			RefreshRuthMap();
			return true;
		}
	}
	for (const int32 I : {0,2,3})
	{
		if (EventId != TargetEvent(*StashTarget(I).ToString())) continue;
		const auto& Treasure = WCRuthMap::Stashes[I];
		if (Has(KeepsakeFlags[I]) || (I == 3 && !Has(RevealFlags[5]))) return true;
		GiveItem(Treasure.Item,Treasure.Name);
		RememberAtCheckpoint(KeepsakeFlags[I]);
		RefreshRuthMap();
		return true;
	}

	int32 Reveal = INDEX_NONE;
	const bool bMetronome = EventId == TEXT("use:ruth_metronome");
	if (bMetronome)
	{
		if (Has(RevealFlags[1])) return true;
		static const TCHAR* Marks[] = {TEXT("wave"),TEXT("star"),TEXT("crescent")};
		PlayAt(TEXT("switch_click"),PuzzlePositions[1],.55f);
		if (++RuthMetronomeStep >= UE_ARRAY_COUNT(Marks)) Reveal = 1;
		else
		{
			Feedback(FString::Printf(TEXT("The weight clicks into the %s mark."),Marks[RuthMetronomeStep-1]));
			if (AWCInteractable* Meter = Thing(PuzzleTargets[1]))
				Meter->Prompt = FString::Printf(TEXT("Move the weight to the %s"),Marks[RuthMetronomeStep]);
			return true;
		}
	}
	for (int32 I : {2,3,5,6})
		if (EventId == TargetEvent(PuzzleTargets[I])) Reveal = I;

	for (int32 I = 0; I < UE_ARRAY_COUNT(TinTargets); ++I)
	{
		if (EventId != TargetEvent(TinTargets[I])) continue;
		if (Has(RevealFlags[4])) return true;
		PlayAt(TEXT("switch_click"),PuzzlePositions[4]+FVector(I*20,0,0),.5f);
		if (I == RuthTinStep)
		{
			if (++RuthTinStep == UE_ARRAY_COUNT(TinTargets)) Reveal = 4;
			else Feedback(TEXT("The tin stays pressed."));
		}
		else
		{
			RuthTinStep = 0;
			Feedback(TEXT("The tins spring back up."));
		}
		if (Reveal == INDEX_NONE) { RefreshRuthMap(); return true; }
		break;
	}
	if (Reveal == INDEX_NONE) return false;
	if (!Has(RevealFlags[Reveal]))
	{
		static const TCHAR* Lines[] = {
			TEXT(""), TEXT("The crescent notch releases the loose base."),
			TEXT("There is folded paper under the washboard."), TEXT("The checked pillowcase opens at the ribbon."),
			TEXT("The third tin clicks. A scrap slips from the little sleeve beneath them."),
			TEXT("A scrap and a photograph are inside the loose lining."), TEXT("There is a paper scrap underneath the tin.")
		};
		RememberAtCheckpoint(RevealFlags[Reveal]);
		PlayAt(TEXT("paper"),ScrapPositions[Reveal],.8f);
		Feedback(Lines[Reveal]);
		RefreshRuthMap();
	}
	return true;
}
