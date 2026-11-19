"""Bake the frozen forest in its reference pose for UE's static Nanite renderer."""
import unreal


def forest_mesh_path(mesh_name):
    return "/Game/WC/Forest/SM_" + mesh_name


def bake_forest_meshes():
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    library = unreal.EditorAssetLibrary
    variants = {"Tree_Baltic_Pine_01": set("ABCD"), "Tree_Baltic_Pine_Sapling_01": set("ABC"),
                "Tree_Dead_Pine": set("ABCD"), "Plant_Bracken_Fern_01": set("ABC")}
    for data in registry.get_assets_by_path("/Game/Megaplant_Library", recursive=True):
        name = str(data.asset_name)
        species, _, variant = name.rpartition("_")
        if species not in variants or variant not in variants[species] or str(data.asset_class_path.asset_name) != "SkeletalMesh":
            continue
        path = forest_mesh_path(name)
        if library.does_asset_exist(path):
            continue
        source = data.get_asset()
        dynamic = unreal.DynamicMesh()
        _, result = unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(
            source, dynamic, unreal.GeometryScriptCopyMeshFromAssetOptions(), unreal.GeometryScriptMeshReadLOD())
        if result != unreal.GeometryScriptOutcomePins.SUCCESS or dynamic.get_triangle_count() == 0:
            raise RuntimeError(f"No reference mesh for {name}")
        options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
        options.enable_collision = False
        options.enable_nanite = True
        nanite = options.nanite_settings
        nanite.enabled = True
        nanite.shape_preservation = unreal.NaniteShapePreservation.PRESERVE_AREA
        options.nanite_settings = nanite
        mesh, outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dynamic, path, options)
        if outcome != unreal.GeometryScriptOutcomePins.SUCCESS or not mesh:
            raise RuntimeError(f"Could not bake {name}")
        mesh.set_editor_property("nanite_settings", nanite)
        mesh.set_editor_property("static_materials", [
            unreal.StaticMaterial(material_interface=s.material_interface, material_slot_name=s.material_slot_name)
            for s in source.materials])
        if not library.save_loaded_asset(mesh):
            raise RuntimeError(f"Could not save {path}")
        unreal.log_warning(f"WC_BAKED {name} {dynamic.get_triangle_count()} triangles, {len(mesh.static_materials)} material slots")


def configure_forest_mesh(component, mesh):
    component.set_collision_profile_name("NoCollision")
    component.set_editor_property("visible_in_ray_tracing", False)
    component.set_editor_property("affect_dynamic_indirect_lighting", False)
    component.set_editor_property("affect_distance_field_lighting", False)
    component.set_cull_distance(5200 if "Fern" in mesh.get_name() else 10000)


def upgrade_placed_forest():
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    baked = {}
    instances = []
    for actor in actors.get_all_level_actors():
        if not isinstance(actor, unreal.SkeletalMeshActor):
            continue
        source = actor.skeletal_mesh_component.skeletal_mesh_asset
        if source and source.get_path_name().startswith("/Game/Megaplant_Library/"):
            name = source.get_name()
            if name not in baked:
                baked[name] = unreal.load_asset(forest_mesh_path(name))
                if not baked[name]:
                    raise RuntimeError(f"Missing baked foliage for {name}")
            instances.append((actor, baked[name]))
    for old, mesh in instances:
        a = actors.spawn_actor_from_class(unreal.StaticMeshActor, old.get_actor_location(), old.get_actor_rotation())
        c = a.static_mesh_component
        c.set_static_mesh(mesh)
        a.set_actor_scale3d(old.get_actor_scale3d())
        a.set_folder_path(old.get_folder_path())
        configure_forest_mesh(c, mesh)
        c.set_cast_shadow(old.skeletal_mesh_component.cast_shadow)
        label = old.get_actor_label()
        if not actors.destroy_actor(old):
            raise RuntimeError(f"Could not replace {label}")
        a.set_actor_label(label)
    unreal.log_warning(f"WC_FOREST replaced {len(instances)} frozen plants using {len(baked)} shared meshes")


# This file also runs on its own in Unreal to restore the map's local Fab-derived assets.
bake_forest_meshes()
