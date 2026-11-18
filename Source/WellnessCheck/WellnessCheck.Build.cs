using UnrealBuildTool;

public class WellnessCheck : ModuleRules
{
    public WellnessCheck(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput", "AudioMixer", "NavigationSystem"
        });
    }
}
