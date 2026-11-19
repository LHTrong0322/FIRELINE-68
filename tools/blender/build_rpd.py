# Dựng trung liên RPD góc nhìn thứ nhất (mid-poly: vát cạnh + weighted normals, không cần bake normal map)
# Chạy: python3 tools/blender/build_rpd.py public/assets/models/rpd_vm.glb
# Hệ toạ độ Blender: +Y = hướng nòng (game: -Z), +Z = lên, +X = phải. Gốc = giữa hộp khoá nòng (khớp mô hình cũ).
# Vật liệu theo tên: 'dark' (thép nhuộm đen), 'metal' (thép mòn sáng), 'wood' (gỗ báng), 'drum' (hộp đạn thép xám mòn) -> game gán M.darkMetal / M.metal / M.gunWood.
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix
OUT = sys.argv[-1] if sys.argv[-1].endswith('.glb') else '/tmp/rpd_vm.glb'
bpy.ops.wm.read_factory_settings(use_empty=True); scn = bpy.context.scene
MATS = {n: bpy.data.materials.new(n) for n in ('dark', 'metal', 'wood', 'drum')}
parts = []

def obj_from_bm(bm, name, mat, bevel=0.0, segs=2):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); scn.collection.objects.link(o); me.materials.append(MATS[mat])
    for p in me.polygons: p.use_smooth = True
    if bevel > 0:
        m = o.modifiers.new('bv', 'BEVEL'); m.width = bevel; m.segments = segs; m.limit_method = 'ANGLE'; m.angle_limit = math.radians(35); m.harden_normals = False
    parts.append(o); return o

def box(name, mat, size, loc, rot=(0, 0, 0), bevel=0.004, taper=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        x, y, z = v.co
        if taper:  # taper=(sx_front, sz_front) thu nhỏ đầu +Y
            t = y + 0.5; x *= 1 + (taper[0] - 1) * t; z *= 1 + (taper[1] - 1) * t
        v.co = Vector((x * size[0], y * size[1], z * size[2]))
    M = Matrix.Translation(loc) @ Matrix.Rotation(rot[0], 4, 'X') @ Matrix.Rotation(rot[1], 4, 'Y') @ Matrix.Rotation(rot[2], 4, 'Z')
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return obj_from_bm(bm, name, mat, bevel)

def tube(name, mat, r1, r2, length, loc, axis='Y', segs=16, bevel=0.0015, rot=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r1, radius2=r2, depth=length)
    R = {'Y': Matrix.Rotation(-math.pi / 2, 4, 'X'), 'X': Matrix.Rotation(math.pi / 2, 4, 'Y'), 'Z': Matrix.Identity(4)}[axis]
    if rot: R = rot @ R
    bmesh.ops.transform(bm, matrix=Matrix.Translation(loc) @ R, verts=bm.verts)
    return obj_from_bm(bm, name, mat, bevel)

def lathe(name, mat, prof, loc, segs=20, axis='Y'):
    """prof: [(r, y)] quay quanh trục Y."""
    bm = bmesh.new(); rings = []
    for r, y in prof:
        if r <= 1e-6: rings.append([bm.verts.new((0, y, 0))]); continue
        rings.append([bm.verts.new((r * math.cos(a), y, r * math.sin(a))) for a in [i * 2 * math.pi / segs for i in range(segs)]])
    for a, b in zip(rings, rings[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            if len(a) == 1: bm.faces.new((a[0], b[j], b[i]))
            elif len(b) == 1: bm.faces.new((a[i], a[j], b[0]))
            else: bm.faces.new((a[i], a[j], b[j], b[i]))
    for ring in (rings[0], rings[-1]):
        if len(ring) > 1: bm.faces.new(ring)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    R = Matrix.Identity(4) if axis == 'Y' else Matrix.Rotation(math.pi / 2, 4, 'Z')
    bmesh.ops.transform(bm, matrix=Matrix.Translation(loc) @ R, verts=bm.verts)
    return obj_from_bm(bm, name, mat, 0)

def extrude_profile(name, mat, pts, width, loc, bevel=0.004, plane='YZ'):
    """Đa giác 2D (y,z) đùn theo X (độ dày width), dùng cho báng/tay cầm."""
    bm = bmesh.new()
    vs = [bm.verts.new((-width / 2, y, z)) for y, z in pts]
    f = bm.faces.new(vs)
    bmesh.ops.recalc_face_normals(bm, faces=[f])
    if f.normal.x > 0: f.normal_flip()
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    ext = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(width, 0, 0), verts=ext)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bmesh.ops.translate(bm, vec=loc, verts=bm.verts)
    return obj_from_bm(bm, name, mat, bevel, 2)

# ---------- hộp khoá nòng + nắp nạp đạn ----------
box('receiver', 'dark', (0.044, 0.30, 0.058), (0, -0.04, 0.0), bevel=0.005)
box('feedcover', 'dark', (0.048, 0.17, 0.022), (0, 0.0, 0.036), bevel=0.007)            # nắp hộp tiếp đạn (nhô cao)
box('feedcover_hinge', 'metal', (0.05, 0.014, 0.014), (0, -0.085, 0.036), bevel=0.003)
box('cover_latch', 'metal', (0.012, 0.018, 0.02), (0, 0.088, 0.04), bevel=0.003)
box('rear_body', 'dark', (0.04, 0.10, 0.05), (0, -0.20, -0.006), bevel=0.005)
# thước ngắm (tangent sight) trên nắp
box('rsight_base', 'dark', (0.03, 0.05, 0.012), (0, 0.105, 0.036), bevel=0.002)
box('rsight_leaf', 'metal', (0.026, 0.045, 0.004), (0, 0.11, 0.046), rot=(math.radians(4), 0, 0), bevel=0.0012)
box('rsight_notch_l', 'dark', (0.008, 0.006, 0.01), (-0.009, 0.09, 0.052), bevel=0.001)
box('rsight_notch_r', 'dark', (0.008, 0.006, 0.01), (0.009, 0.09, 0.052), bevel=0.001)
# tay kéo khoá nòng bên phải + rãnh
box('charge_slot', 'metal', (0.004, 0.12, 0.008), (0.0225, 0.0, -0.012), bevel=0.001)
tube('charge_handle', 'metal', 0.006, 0.007, 0.03, (0.04, 0.03, -0.012), axis='X', segs=10)
box('charge_knob', 'metal', (0.012, 0.014, 0.016), (0.055, 0.03, -0.012), bevel=0.004)
# cửa tiếp đạn bên trái (băng đạn đi vào từ hộp tròn)
box('feed_port', 'dark', (0.02, 0.05, 0.03), (-0.03, 0.0, 0.005), bevel=0.003)
# ốp đinh tán
for i, y in enumerate((-0.15, -0.08, 0.06)):
    for s in (-1, 1): tube(f'rivet{i}{s}', 'metal', 0.0035, 0.0035, 0.003, (s * 0.0225, y, -0.016), axis='X', segs=8, bevel=0)
# ---------- cò + vòng cò ----------
box('trigger_housing', 'dark', (0.03, 0.09, 0.022), (0, -0.07, -0.038), bevel=0.003)
box('guard_bottom', 'dark', (0.016, 0.07, 0.005), (0, -0.07, -0.078), bevel=0.0015)
box('guard_front', 'dark', (0.016, 0.005, 0.04), (0, -0.034, -0.058), bevel=0.0015)
box('trigger', 'metal', (0.006, 0.008, 0.026), (0, -0.06, -0.058), rot=(math.radians(-15), 0, 0), bevel=0.0015)
# ---------- báng gỗ liền tay cầm (kiểu bán súng lục) ----------
stock_prof = [(-0.25, 0.012), (-0.25, -0.03), (-0.17, -0.06), (-0.12, -0.075), (-0.12, -0.15), (-0.095, -0.155),
              (-0.075, -0.07), (-0.05, -0.035), (-0.045, 0.012)]  # (y, z) phần gần tay cầm
extrude_profile('stock_grip', 'wood', [(y, z) for y, z in stock_prof], 0.04, (0, 0, 0), bevel=0.008)
stock_rear = [(-0.25, 0.018), (-0.52, 0.0), (-0.53, -0.115), (-0.50, -0.125), (-0.25, -0.04)]
extrude_profile('stock_butt', 'wood', stock_rear, 0.044, (0, 0, 0), bevel=0.01)
box('buttplate', 'dark', (0.046, 0.008, 0.13), (0, -0.532, -0.058), rot=(math.radians(-5), 0, 0), bevel=0.003)
# ---------- ốp lót tay gỗ (ngắn) ----------
box('handguard', 'wood', (0.05, 0.17, 0.05), (0, 0.205, -0.004), bevel=0.012, taper=(0.86, 0.85))
for k in range(5): box(f'hg_groove{k}', 'wood', (0.052, 0.006, 0.006), (0, 0.15 + k * 0.025, -0.021), bevel=0.002)
box('hg_ring', 'metal', (0.054, 0.012, 0.054), (0, 0.297, -0.004), bevel=0.006)
# ---------- nòng dài + ống trích khí ----------
tube('barrel', 'dark', 0.0125, 0.011, 0.52, (0, 0.56, 0.014), segs=18)
tube('barrel_shroud', 'dark', 0.016, 0.016, 0.06, (0, 0.33, 0.014), segs=18)
tube('gas_tube', 'metal', 0.0075, 0.0075, 0.29, (0, 0.44, -0.016), segs=12)
box('gas_block', 'dark', (0.026, 0.035, 0.052), (0, 0.6, -0.002), bevel=0.005)
tube('gas_plug', 'metal', 0.006, 0.006, 0.012, (0.016, 0.6, -0.016), axis='X', segs=10)
# đầu ngắm có vành che + đầu nòng
box('fsight_base', 'dark', (0.026, 0.03, 0.022), (0, 0.79, 0.032), bevel=0.003)
lathe('fsight_hood', 'dark', [(0.012, -0.009), (0.012, 0.009), (0.0095, 0.009), (0.0095, -0.009)], (0, 0.79, 0.048), segs=14).rotation_euler = (0, 0, 0)
box('fsight_post', 'metal', (0.003, 0.004, 0.02), (0, 0.79, 0.04), bevel=0.0008)
lathe('muzzle', 'dark', [(0.0045, 0.82), (0.016, 0.82), (0.016, 0.80), (0.014, 0.78), (0.0045, 0.78)], (0, 0, 0.014), segs=16)
# ---------- chân chống gấp dọc nòng ----------
box('bipod_clamp', 'dark', (0.044, 0.024, 0.036), (0, 0.69, 0.002), bevel=0.004)
for s in (-1, 1):
    tube(f'bipod_leg{s}', 'dark', 0.005, 0.0045, 0.27, (s * 0.017, 0.555, -0.01), segs=8)
    box(f'bipod_foot{s}', 'dark', (0.01, 0.028, 0.012), (s * 0.017, 0.425, -0.016), bevel=0.002)
box('bipod_latch', 'metal', (0.046, 0.008, 0.01), (0, 0.45, -0.012), bevel=0.002)
# ---------- hộp đạn tròn 100 viên (vỏ dập 2 nửa có gân, nắp, quai) ----------
DR, DW = 0.082, 0.068
dc = (-0.002, 0.04, -0.11)
drum = lathe('drum', 'drum', [(0.0, -DW / 2), (DR - 0.012, -DW / 2), (DR, -DW / 2 + 0.008), (DR, DW / 2 - 0.008),
                              (DR - 0.012, DW / 2), (0.0, DW / 2)], (0, 0, 0), segs=36)
drum.rotation_euler = (0, 0, math.pi / 2); drum.location = dc
seam = lathe('drum_seam', 'metal', [(DR + 0.003, -0.004), (DR + 0.003, 0.004), (DR - 0.002, 0.004), (DR - 0.002, -0.004)], (0, 0, 0), segs=36)
seam.rotation_euler = (0, 0, math.pi / 2); seam.location = dc
for side in (-1, 1):  # gân dập tròn trên hai mặt
    rib = lathe(f'drum_rib{side}', 'drum', [(0.052, 0.0), (0.056, 0.0), (0.056, 0.003), (0.052, 0.003)], (0, 0, 0), segs=28)
    rib.rotation_euler = (0, 0, math.pi / 2); rib.location = (dc[0] + side * (DW / 2), dc[1], dc[2]); rib.scale = (1, side, 1)
    hub = tube(f'drum_hub{side}', 'metal', 0.016, 0.014, 0.006, (dc[0] + side * (DW / 2 + 0.002), dc[1], dc[2]), axis='X', segs=14)
box('drum_latch', 'metal', (0.07, 0.016, 0.01), (dc[0], dc[1] + DR - 0.004, dc[2] + 0.02), bevel=0.003)
box('drum_neck', 'dark', (0.03, 0.05, 0.05), (-0.018, 0.02, -0.04), bevel=0.004)          # cổ nối lên cửa tiếp đạn
box('drum_handle', 'metal', (0.008, 0.07, 0.006), (dc[0] - DW / 2 - 0.012, dc[1], dc[2] + 0.03), bevel=0.002)
for y in (-0.03, 0.03): box(f'drum_hpost{y}', 'metal', (0.012, 0.006, 0.02), (dc[0] - DW / 2 - 0.006, dc[1] + y, dc[2] + 0.022), bevel=0.0015)
# ---------- khoen dây đeo ----------
lathe('sling_ring', 'metal', [(0.008, -0.002), (0.011, -0.002), (0.011, 0.002), (0.008, 0.002)], (-0.024, -0.48, -0.06), segs=10, axis='X')

# ---------- áp modifier, weighted normals, UV, AO đỉnh, gộp theo vật liệu ----------
for o in parts:
    bpy.context.view_layer.objects.active = o
    for m in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
    o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4)
merged = []
groups = {mn: [o for o in parts if o.data.materials[0] == mat] for mn, mat in MATS.items()}
for mn, mat in MATS.items():
    objs = groups[mn]
    if not objs: continue
    for o in scn.objects: o.select_set(o in objs)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); o = bpy.context.view_layer.objects.active; o.name = 'rpd_' + mn
    # UV hộp ~ mật độ vân 0.3 m/ô
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(cube_size=0.35 if mn == 'wood' else 0.25); bpy.ops.object.mode_set(mode='OBJECT')
    # weighted normals: mặt lớn phẳng, cạnh vát cong mượt -> viền sáng kiểu súng FPS hiện đại
    o.data.shade_smooth()
    wn = o.modifiers.new('wn', 'WEIGHTED_NORMAL'); wn.keep_sharp = True; wn.weight = 100; wn.mode = 'FACE_AREA'
    bpy.ops.object.modifier_apply(modifier='wn')
    # AO hốc (cavity) vào màu đỉnh: đỉnh nằm trong khe/góc lõm tối đi, mặt phẳng & cạnh lồi giữ nguyên
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); cav = []
    for v in bm.verts:
        ds = [((e.other_vert(v).co - v.co).normalized()).dot(v.normal) for e in v.link_edges if (e.other_vert(v).co - v.co).length > 1e-6]
        c = sum(ds) / len(ds) if ds else 0.0
        cav.append(max(0.45, min(1.0, 1.0 - max(0.0, c) * 1.6)))
    bm.free()
    ca = o.data.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
    for i, c in enumerate(cav): ca.data[i].color = (c, c, c, 1)
    o.data.color_attributes.active_color = ca
    merged.append(o)
for o in scn.objects: o.select_set(o in merged)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_yup=True, export_normals=True,
                          export_texcoords=True, export_materials='EXPORT', export_vertex_color='ACTIVE', export_all_vertex_colors=False)
print('exported', OUT, os.path.getsize(OUT), {o.name: (len(o.data.vertices), sum(len(p.vertices) - 2 for p in o.data.polygons)) for o in merged})
