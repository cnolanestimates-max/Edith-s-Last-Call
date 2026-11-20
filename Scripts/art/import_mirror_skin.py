"""Author the bathroom reflection's displacement on a copy of Edith's fitted skin."""
import unreal as u

assets = u.EditorAssetLibrary
edit = u.MaterialEditingLibrary
source = "/Game/WC/Her/M_Her"
target = "/Game/WC/Her/M_HerMirror"

# The rest mesh is 270 cm tall. Work in that space so the relief follows her
# seated pose and expression. Neighbouring tracks overlap at the cell boundaries.
relief = """
float mask = smoothstep(12.0, 19.0, P.y)
    * smoothstep(222.0, 229.5, P.z) * (1 - smoothstep(257.0, 264.0, P.z))
    * (1 - smoothstep(12.0, 17.0, abs(P.x)));
mask *= smoothstep(3.8, 5.8, length(P.xz - float2(6,246.6)));
mask *= smoothstep(0.4, 1.6, length((P.xz - float2(.3,234.0)) * float2(.40,1)));
if (mask < .001) return 0;
float2 p = P.xz - float2(0,244);
float2 spacing = float2(5.2,5.7);
float2 cell = floor(p / spacing);
float peak = 0, total = 0;
[unroll] for (int y = -1; y <= 1; ++y) {
    [unroll] for (int x = -1; x <= 1; ++x) {
        float2 id = cell + float2(x,y);
        float3 hash = frac(float3(id.xyx) * float3(.1031,.1030,.0973));
        hash += dot(hash,hash.yzx + 33.33);
        float3 r = frac((hash.xxy + hash.yzz) * hash.zyx);
        float phase = r.z * 6.28318 + T * (.92 + .83*r.y);
        float angle = r.x * 6.28318 + .56*sin(phase*.71 + r.y*5);
        float2 along = float2(cos(angle),sin(angle));
        float2 across = float2(-along.y,along.x);
        float2 center = (id + .5 + .23*(r.xy-.5))*spacing
            + along*(2.0*sin(phase)) + across*(.88*cos(phase*.83));
        float2 delta = p - center;
        float u = dot(delta,along);
        float v = dot(delta,across) - 1.18*sin(.52*u - 1.75*phase)
            - .46*sin(.8*u + .74*phase);
        float lengthCm = 3.8 + 1.35*r.z;
        float girth = (.95 + .39*r.x) * (1 + .14*cos(.95*u - 2.6*phase));
        float envelope = 1 - smoothstep(.46,1,abs(u)/lengthCm);
        float ridge = envelope * exp2(-1.55*v*v/(girth*girth)) * (.88 + .12*sin(phase+.48*u));
        peak = max(peak,ridge);
        total += ridge;
    }
}
return mask * (3.9*peak + .62*min(total-peak,1.4));
"""

def custom(mat, label, code, pins, output, x, y):
    expr = edit.create_material_expression(mat, u.MaterialExpressionCustom, x, y)
    expr.set_editor_property("description", label)
    expr.set_editor_property("code", code)
    expr.set_editor_property("output_type", output)
    inputs = []
    for name, _, _ in pins:
        pin = u.CustomInput()
        pin.set_editor_property("input_name", name)
        inputs.append(pin)
    expr.set_editor_property("inputs", inputs)
    for name, upstream, channel in pins:
        assert edit.connect_material_expressions(upstream, channel, expr, name), name
    return expr

def build():
    prop = u.MaterialProperty
    if assets.does_asset_exist(target):
        mat = assets.load_asset(target)
        offset = edit.get_material_property_input_node(mat, prop.MP_WORLD_POSITION_OFFSET)
        height = next(e for e in edit.get_inputs_for_material_expression(mat, offset)
                      if isinstance(e, u.MaterialExpressionCustom))
        height.set_editor_property("code", relief)
    else:
        mat = assets.duplicate_asset(source, target)
        if not mat:
            raise RuntimeError("Could not duplicate Edith's skin")
        node = lambda cls, x, y: edit.create_material_expression(mat, cls, x, y)
        wire = edit.connect_material_expressions
        scalar = u.CustomMaterialOutputType.CMOT_FLOAT1
        vector = u.CustomMaterialOutputType.CMOT_FLOAT3
        rest = node(u.MaterialExpressionPreSkinnedPosition, -1900, 840)
        time = node(u.MaterialExpressionTime, -1900, 970)
        height = custom(mat, "Burrowing under the skin", relief,
                        [("P", rest, ""), ("T", time, "")], scalar, -1610, 860)
        vertex_normal = node(u.MaterialExpressionVertexNormalWS, -1560, 1100)
        offset = node(u.MaterialExpressionMultiply, -1230, 860)
        assert wire(height, "", offset, "A") and wire(vertex_normal, "", offset, "B")
        assert edit.connect_material_property(offset, "", prop.MP_WORLD_POSITION_OFFSET)

        # Carry the displaced vertices' height into the pixel shader. Reorient
        # the fitted pore normal as the crests turn through the actual sidelight.
        interp = node(u.MaterialExpressionVertexInterpolator, -1260, 1060)
        assert wire(height, "", interp, "")
        pos = node(u.MaterialExpressionWorldPosition, -1270, 1240)
        pos.set_editor_property("world_position_shader_offset", u.WorldPositionIncludedOffsets.WPT_EXCLUDE_ALL_SHADER_OFFSETS)
        grad = custom(mat, "Surface slope in world space", """
float3 x = ddx(W), y = ddy(W);
float3 n = cross(x,y);
float denom = max(dot(n,n),1.e-12);
return (cross(y,n)*ddx(H) + cross(n,x)*ddy(H))/denom;
""", [("W",pos,""),("H",interp,"")], vector, -970, 1140)
        tangent = node(u.MaterialExpressionTransform, -700, 1120)
        tangent.set_editor_property("transform_source_type", u.MaterialVectorCoordTransformSource.TRANSFORMSOURCE_WORLD)
        tangent.set_editor_property("transform_type", u.MaterialVectorCoordTransform.TRANSFORM_TANGENT)
        assert wire(grad, "", tangent, "")
        skin = edit.get_material_property_input_node(mat, prop.MP_NORMAL)
        channel = edit.get_material_property_input_node_output_name(mat, prop.MP_NORMAL)
        normal = custom(mat, "Light across the stretched skin",
                        "return normalize(float3(Skin.xy - .92*Slope.xy, Skin.z));",
                        [("Skin",skin,channel),("Slope",tangent,"")], vector, -400, 1030)
        assert edit.connect_material_property(normal, "", prop.MP_NORMAL)
    edit.recompile_material(mat)
    assert assets.save_loaded_asset(mat, False)
    u.log("WCMIRRORSKIN saved " + target)

if __name__ == "__main__":
    build()
