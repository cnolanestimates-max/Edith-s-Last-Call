#pragma once

#include "CoreMinimal.h"

class AWCDirector;

namespace WCRuthMap
{
	enum class Floor : uint8 { Ground, Upper, Attic, Cellar };
	inline constexpr int32 PieceCount = 7;

	struct FRoom
	{
		int32 Piece = INDEX_NONE;
		FBox2D Bounds{ForceInit};
		FBox2D Annex{ForceInit};
	};

	struct FStash
	{
		int32 Piece;
		FVector2D Mark;
		const TCHAR* Item;
		const TCHAR* Name;
		const TCHAR* Hint;
	};

	extern const FStash Stashes[4];
	Floor FloorForPiece(int32 Piece);
	const TCHAR* FloorName(Floor Page);
	FVector2D PlanPoint(Floor Page, const FVector2D& World);
	FRoom RoomAt(const FVector& Feet);
	bool OwnsPiece(const AWCDirector& Director, int32 Piece);
	int32 Count(const AWCDirector& Director);
	bool HasFloor(const AWCDirector& Director, Floor Page);
}
