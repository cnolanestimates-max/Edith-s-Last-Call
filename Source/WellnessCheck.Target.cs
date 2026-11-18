using UnrealBuildTool;
using System.Collections.Generic;

public class WellnessCheckTarget : TargetRules
{
    public WellnessCheckTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("WellnessCheck");
    }
}

