#include "WCGame.h"
#include "WCCharacter.h"
#include "WCDirector.h"
#include "WCWorld.h"
#include "CanvasItem.h"
#include "Components/CapsuleComponent.h"
#include "Engine/Canvas.h"
#include "Engine/Texture2D.h"

namespace
{
	using WCRuthMap::Floor;
	constexpr Floor Pages[] = {Floor::Ground,Floor::Upper,Floor::Attic,Floor::Cellar};
	const FLinearColor Pale(.79f,.67f,.48f,1.f);
	const FLinearColor Rust(.46f,.095f,.052f,1.f);
	const FLinearColor RoomTint(.27f,.37f,.17f,.25f);
	const FLinearColor RuthTabFill(.17f,.11f,.07f,.96f);

	WCRuthMap::FRoom PlayerRoom(AWCDirector* D)
	{
		const AWCCharacter* P = D->Player();
		return P ? WCRuthMap::RoomAt(P->GetActorLocation() -
			FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight())) : WCRuthMap::FRoom{};
	}
}

void AWCHUD::OpenRuthMap(AWCDirector* D)
{
	if (RuthPlates.IsEmpty()) RuthPlates.SetNum(WCRuthMap::PieceCount + 1);
	for (int32 I = 0; I <= WCRuthMap::PieceCount; ++I)
	{
		if (RuthPlates[I] || (I > 0 && !WCRuthMap::OwnsPiece(*D,I-1))) continue;
		const FString Plate = I == 0 ? TEXT("Header") : FString::Printf(TEXT("Scrap%d"), I);
		const FString Name = FString::Printf(TEXT("/Game/WC/RuthMap/T_RuthMap_%s.T_RuthMap_%s"), *Plate, *Plate);
		RuthPlates[I] = LoadObject<UTexture2D>(nullptr,*Name);
	}
	const auto Room = PlayerRoom(D);
	RuthFloor = Floor::Ground;
	if (Room.Piece != INDEX_NONE && WCRuthMap::HasFloor(*D,WCRuthMap::FloorForPiece(Room.Piece)))
		RuthFloor = WCRuthMap::FloorForPiece(Room.Piece);
	else
		for (Floor Page : Pages)
			if (WCRuthMap::HasFloor(*D,Page)) { RuthFloor = Page; break; }
	RuthStash = INDEX_NONE;
	RuthBack = Screen == EWCScreen::Pause ? EWCScreen::Pause : EWCScreen::None;
	D->Play2D(TEXT("paper"),.45f);
	Open(EWCScreen::RuthMap);
	SetPaused(true);
}

void AWCHUD::CloseRuthMap()
{
	Open(RuthBack);
	SetPaused(RuthBack == EWCScreen::Pause);
}

void AWCHUD::DrawRuthMap(AWCDirector* D)
{
	const float W = Canvas->SizeX, H = Canvas->SizeY;
	Box(0,0,W,H,FLinearColor(.027f,.019f,.013f,.97f));
	TArray<Floor,TInlineAllocator<4>> Available;
	for (Floor Page : Pages)
		if (WCRuthMap::HasFloor(*D,Page)) Available.Add(Page);
	if (Available.IsEmpty()) return;
	if (!Available.Contains(RuthFloor)) RuthFloor = Available[0];

	const float Width = FMath::Min(W*.90f,(H-Px(185.f))/.615f);
	const float Left = (W - Width)*.5f;
	const float Top = Px(33.f);
	const float HeadH = Width*124.f/736.f;
	const float ChartY = Top + HeadH + Px(7.f);
	const float ChartH = Width*327.f/736.f;
	const float Footer = ChartY + ChartH;
	const auto ScreenPoint = [&](const FVector2D& World)
	{
		return FVector2D(Left,ChartY) + WCRuthMap::PlanPoint(RuthFloor,World)*FVector2D(Width,ChartH);
	};
	const auto Plate = [&](int32 Index, float Y, float Height)
	{
		if (!RuthPlates.IsValidIndex(Index) || !RuthPlates[Index] || !RuthPlates[Index]->GetResource()) return;
		FCanvasTileItem Tile(FVector2D(Left,Y),RuthPlates[Index]->GetResource(),FVector2D(Width,Height),FLinearColor::White);
		Tile.BlendMode = SE_BLEND_Translucent;
		Canvas->DrawItem(Tile);
	};
	const auto Line = [&](FVector2D A, FVector2D B, const FLinearColor& Color, float Thick)
	{
		FCanvasLineItem Item(A,B);
		Item.SetColor(Color);
		Item.LineThickness = Thick;
		Canvas->DrawItem(Item);
	};

	APlayerController* PC = GetOwningPlayerController();
	float MX = 0, MY = 0;
	const bool bMouse = CanvasMouse(MX,MY);
	const bool bClick = bMouse && PC->WasInputKeyJustPressed(EKeys::LeftMouseButton);
	const auto Hit = [&](float X,float Y,float SX,float SY)
	{
		return bMouse && MX >= X && MX <= X+SX && MY >= Y && MY <= Y+SY;
	};
	const int32 Step = (PC->WasInputKeyJustPressed(EKeys::Right) || PC->WasInputKeyJustPressed(EKeys::Gamepad_RightShoulder)) ? 1 :
		(PC->WasInputKeyJustPressed(EKeys::Left) || PC->WasInputKeyJustPressed(EKeys::Gamepad_LeftShoulder)) ? -1 : 0;
	if (Step != 0)
	{
		const int32 Next = (Available.IndexOfByKey(RuthFloor) + Step + Available.Num()) % Available.Num();
		RuthFloor = Available[Next];
		RuthStash = INDEX_NONE;
	}
	const float TabW = FMath::Min(Px(188.f),(Width-Px(25.f))/Available.Num());
	const float TabX = W*.5f-Available.Num()*TabW*.5f;
	const float TabY = Footer + Px(4.f);
	for (int32 I = 0; I < Available.Num(); ++I)
	{
		const float X = TabX+I*TabW;
		if (bClick && Hit(X,TabY,TabW,Px(36.f))) { RuthFloor = Available[I]; RuthStash = INDEX_NONE; }
		const bool bActive = RuthFloor == Available[I];
		Box(X,TabY,TabW-Px(5.f),Px(36.f),bActive ? Pale : RuthTabFill);
		Text(WCRuthMap::FloorName(Available[I]),X+(TabW-Px(5.f))*.5f,TabY+Px(6.f),Px(22.f),
			bActive ? RuthTabFill : Pale,1,false,false);
	}

	Plate(0,Top,HeadH);
	for (int32 I = 0; I < WCRuthMap::PieceCount; ++I)
		if (WCRuthMap::FloorForPiece(I) == RuthFloor && WCRuthMap::OwnsPiece(*D,I))
			Plate(I+1,ChartY,ChartH);

	const auto Room = PlayerRoom(D);
	if (Room.Piece != INDEX_NONE && WCRuthMap::FloorForPiece(Room.Piece) == RuthFloor && WCRuthMap::OwnsPiece(*D,Room.Piece))
	{
		for (const FBox2D* Bounds : {&Room.Bounds,&Room.Annex})
		{
			if (!Bounds->bIsValid) continue;
			const FVector2D A = ScreenPoint(Bounds->Min + FVector2D(9,9));
			const FVector2D B = ScreenPoint(Bounds->Max - FVector2D(9,9));
			Box(A.X,A.Y,B.X-A.X,B.Y-A.Y,RoomTint);
		}
	}

	for (int32 I = 0; I < UE_ARRAY_COUNT(WCRuthMap::Stashes); ++I)
	{
		const auto& Stash = WCRuthMap::Stashes[I];
		if (WCRuthMap::FloorForPiece(Stash.Piece) != RuthFloor || !WCRuthMap::OwnsPiece(*D,Stash.Piece) || D->HasItem(Stash.Item)) continue;
		const FVector2D At = ScreenPoint(Stash.Mark);
		const float R = Px(8.f);
		const bool bOnStar = Hit(At.X-R*2,At.Y-R*2,R*4,R*4);
		if (bClick && bOnStar) RuthStash = RuthStash == I ? INDEX_NONE : I;
		const FVector2D Shape[] = {{0,-R},{R*.36, -R*.35},{R,0},{R*.36,R*.35},{0,R},{-R*.36,R*.35},{-R,0},{-R*.36,-R*.35}};
		for (int32 J = 0; J < UE_ARRAY_COUNT(Shape); ++J)
			Line(At+Shape[J],At+Shape[(J+1)%UE_ARRAY_COUNT(Shape)],Rust,Px(RuthStash == I || bOnStar ? 3.5f : 2.3f));
	}
	const auto MarkLocked = [&](Floor Page, int32 Piece, const TCHAR* Flag, const TCHAR* DoorId, FVector2D Position)
	{
		if (RuthFloor != Page || !WCRuthMap::OwnsPiece(*D,Piece) || !D->Has(Flag)) return;
		const AWCDoor* Door = D->Door(DoorId);
		if (!Door || !Door->bLocked) return;
		const FVector2D At = ScreenPoint(Position);
		const float R = Px(6.f);
		Line(At-FVector2D(R,R),At+FVector2D(R,R),Rust,Px(2.2f));
		Line(At+FVector2D(-R,R),At+FVector2D(R,-R),Rust,Px(2.2f));
	};
	MarkLocked(Floor::Ground,1,TEXT("ruth_tried_sitting"),TEXT("sitting"),{1400,-217});
	MarkLocked(Floor::Upper,3,TEXT("ruth_tried_rear"),TEXT("up_ell"),{1590,-11});

	const FString Detail = RuthStash != INDEX_NONE
		? FString::Printf(TEXT("%s   %s"),WCRuthMap::Stashes[RuthStash].Name,WCRuthMap::Stashes[RuthStash].Hint)
		: FString::Printf(TEXT("%d of %d scraps   |   Green marks your room   |   Diamonds mark treasure   |   Red X marks a tried lock"),
			WCRuthMap::Count(*D),WCRuthMap::PieceCount);
	Wrapped(Detail,Left,TabY+Px(45.f),Width,Px(21.f),Pale,1,false);
	Text(TEXT("[M] or [Esc]  Fold map     [Left / Right]  Turn page"),W*.5f,H-Px(32.f),Px(20.f),Pale,1,false,false);
}
