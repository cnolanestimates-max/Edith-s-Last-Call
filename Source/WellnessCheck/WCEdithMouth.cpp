#include "WCEdithMouth.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Materials/MaterialInstanceDynamic.h"

void UWCEdithMouth::Fit(USkeletalMeshComponent* Body, FName Head, const FTransform& HeadRest, const FVector& Left, const FVector& Forward)
{
	USkeletalMesh* Rig = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/WC/Her/Mouth/SK_EdithMouth.SK_EdithMouth"));
	UMaterialInterface* Skin = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Her/Mouth/M_EdithFace.M_EdithFace"));
	if (!ensure(Rig && Skin && Body->GetMaterial(0))) return;
	const FReferenceSkeleton& Ref = Rig->GetRefSkeleton();
	ArchBones[0] = Ref.FindBoneIndex(TEXT("UpperArch"));
	ArchBones[1] = Ref.FindBoneIndex(TEXT("LowerArch"));
	if (!ensure(ArchBones[0] != INDEX_NONE && ArchBones[1] != INDEX_NONE)) return;
	for (int32 I = 0; I < JointCount; ++I)
	{
		const int32 Bone = Ref.FindBoneIndex(FName(*FString::Printf(TEXT("Tongue_%02d"), I)));
		if (!ensure(Bone != INDEX_NONE)) return;
		TongueBones[I] = Bone;
		RestSpine.Add(Ref.GetRefBonePose()[Bone].GetLocation());
	}
	Face = Body;
	RestSkin = Body->GetMaterial(0);
	OpenSkin = UMaterialInstanceDynamic::Create(Skin, this);
	SetSkinnedAssetAndUpdate(Rig);
	AttachToComponent(Body, FAttachmentTransformRules::KeepRelativeTransform, Head);
	// The mouth was fitted in centimetres along Edith's left, forward and up axes.
	const FTransform Frame(FRotationMatrix::MakeFromXY(Left, Forward).ToQuat(), Left * .30 + FVector(0, 0, 224.1));
	SetRelativeTransform(Frame * HeadRest.Inverse());
	SetCollisionEnabled(ECollisionEnabled::NoCollision);
	SetLightingChannels(true, true, false);
	SetBoundsScale(1.6f);
	SetVisibility(false);
	AddTickPrerequisiteComponent(Body);
}

void UWCEdithMouth::Close()
{
	if (!bOpen) return;
	SetVisibility(false);
	if (Face->GetMaterial(0) == OpenSkin) Face->SetMaterial(0, RestSkin);
	bOpen = false;
}

void UWCEdithMouth::Pose(float Jaw, float Extension, float Time)
{
	if (!OpenSkin) return;
	// Scene-specific skin overrides, including the writhing mirror reflection, own the entire face.
	if (Jaw <= .035f || (Face->GetMaterial(0) != RestSkin && Face->GetMaterial(0) != OpenSkin))
	{
		Close();
		return;
	}
	if (!bOpen)
	{
		Face->SetMaterial(0, OpenSkin);
		SetVisibility(true);
		bOpen = true;
	}

	const FTransform Frame = GetRelativeTransform() * Face->GetSocketTransform(GetAttachSocketName());
	const FVector Origin = Frame.GetLocation();
	OpenSkin->SetVectorParameterValue(TEXT("StudyOrigin"), FLinearColor(Origin.X, Origin.Y, Origin.Z, 1));
	auto SetAxis = [&](FName Name, const FVector& Axis)
	{
		FVector V = Frame.TransformVector(Axis);
		V /= FMath::Max(V.SizeSquared(), UE_SMALL_NUMBER);
		OpenSkin->SetVectorParameterValue(Name, FLinearColor(V.X, V.Y, V.Z, 1));
	};
	SetAxis(TEXT("StudyH"), FVector::ForwardVector);
	SetAxis(TEXT("StudyF"), FVector::RightVector);
	SetAxis(TEXT("StudyV"), FVector::UpVector);
	OpenSkin->SetScalarParameterValue(TEXT("JawOpen"), Jaw);

	// Each tooth is weighted at its socket; the points keep their length as the jaws close.
	const double Closed = 1. - Jaw;
	const auto& Ref = GetSkinnedAsset()->GetRefSkeleton().GetRefBonePose();
	for (int32 I = 0; I < 2; ++I)
	{
		const int32 Bone = ArchBones[I];
		FTransform Arch = Ref[Bone];
		FVector P = Arch.GetLocation();
		P.Z = FMath::Lerp(P.Z, 9.65, Closed);
		P.Y -= Closed * Closed * (5.7 + 2. * I);
		Arch.SetLocation(P);
		Arch.SetScale3D(FVector(1. - .38 * Closed, 1., 1.));
		BoneSpaceTransforms[Bone] = Arch;
	}

	constexpr int32 Last = JointCount - 1;
	const double Reach = FMath::Min(double(Extension), double(FMath::SmoothStep(.08f, .72f, Jaw)));
	FVector Centers[JointCount];
	double Radii[JointCount], Travel[JointCount];
	for (int32 I = 0; I <= Last; ++I)
	{
		const double U = double(I) / Last - (1. - Reach) * 1.11;
		Travel[I] = U;
		const double Q = FMath::Clamp(U, 0., 1.) * Last;
		const int32 K = FMath::Min(int32(Q), Last - 1);
		FVector P = FMath::Lerp(RestSpine[K], RestSpine[K + 1], Q - K);
		if (U < 0.)
		{
			P.Y -= 4. * (1. - FMath::Exp(6. * U));
			P.Z -= 1.1 * (1. - FMath::Exp(7. * U));
		}
		Radii[I] = FMath::Lerp(.10, 1., FMath::SmoothStep(-.16, .03, U));
		const double Free = FMath::SmoothStep(.24, .93, U);
		const double Phase = 8.15 * U - 3.05 * Time;
		P.X += Free * (6.9 * FMath::Sin(Phase) + 1.65 * FMath::Sin(Phase * 1.52 + .6));
		P.Y += Free * 2.7 * FMath::Sin(Phase + .85);
		P.Z += Free * (2.35 * FMath::Cos(Phase + .28) + 1.45 * FMath::Sin(.9 * Time));
		P.Z += Closed * (9.65 - P.Z) * (1. - FMath::Clamp(U, 0., 1.));
		Centers[I] = P;
	}
	for (int32 I = 0; I <= Last; ++I)
	{
		const int32 A = FMath::Max(I - 1, 0), B = FMath::Min(I + 1, Last);
		const FVector Old = (RestSpine[B] - RestSpine[A]).GetSafeNormal();
		const FVector Now = (Centers[B] - Centers[A]).GetSafeNormal(UE_SMALL_NUMBER, Old);
		const double Twist = .38 * FMath::SmoothStep(.25, .96, Travel[I]) * FMath::Sin(8.15 * Travel[I] - 3.05 * Time + 1.4);
		const int32 Bone = TongueBones[I];
		const FQuat Rotation = FQuat(Now, Twist) * FQuat::FindBetweenNormals(Old, Now) * Ref[Bone].GetRotation();
		BoneSpaceTransforms[Bone] = FTransform(Rotation, Centers[I], FVector(Radii[I]));
	}
	MarkRefreshTransformDirty();
}