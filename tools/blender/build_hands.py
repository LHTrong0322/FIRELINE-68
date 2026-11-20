# Dựng tay góc nhìn thứ nhất (mid-poly): bàn tay nắm súng có đốt ngón, khớp gồ, cổ tay + ống tay áo thon dần có nếp gấp và gấu xắn.
# Chạy: python3 tools/blender/build_hands.py public/assets/models/hands_vm.glb
# Mọi toạ độ viết theo HỆ GAME (Three.js: +X phải, +Y lên = mu bàn tay, +Z = hướng ngón tay / từ khuỷu tới cổ tay),
# cuối cùng xoay sang hệ Blender để xuất GLB (+Y up) trả lại đúng hệ game.
#  - 'hand'  (vật liệu 'skin'):  gốc = giữa lòng bàn tay (khớp makeHand() cũ), cổ tay kéo lùi về -Z.
#  - 'sleeve'(vật liệu 'sleeve'): ống tay dài ĐƠN VỊ: z=0 ở khuỷu, z=1 ở cổ tay; game co giãn theo trục Z bằng chiều dài cẳng tay.
# AO đỉnh: bắn tia bán cầu (BVH) -> kẽ ngón, lòng bàn tay, nếp tay áo tối đi; lưu vào màu đỉnh (game nhân với vật liệu).
import bpy, bmesh, math, sys, os, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
OUT = sys.argv[-1] if sys.argv[-1].endswith('.glb') else '/tmp/hands_vm.glb'
bpy.ops.wm.read_factory_settings(use_empty=True); scn = bpy.context.scene
MATS = {n: bpy.data.materials.new(n) for n in ('skin', 'sleeve')}
random.seed(68)

def frame_along(pts):
    """Khung vận chuyển song song dọc đường đi -> (tangent, normal, binormal) mỗi điểm."""
    T = []
    for i in range(len(pts)):
        a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]; T.append((b - a).normalized())
    up = Vector((0, 1, 0)) if abs(T[0].y) < 0.9 else Vector((1, 0, 0))
    N = [(up - T[0] * up.dot(T[0])).normalized()]
    for i in range(1, len(pts)):
        n = N[-1] - T[i] * N[-1].dot(T[i]); N.append(n.normalized())
    return [(T[i], N[i], T[i].cross(N[i])) for i in range(len(pts))]

def sweep(bm, pts, radii, segs=8, cap_end=True, cap_start=False, rfun=None, flat=1.0):
    """Ống theo đường gấp khúc; flat<1 ép dẹt theo hướng normal (ngón tay hơi dẹt). Đầu cuối bo tròn."""
    fr = frame_along(pts); rings = []
    for i, (p, r) in enumerate(zip(pts, radii)):
        t, n, b = fr[i]; ring = []
        for k in range(segs):
            a = 2 * math.pi * k / segs; rr = r * (rfun(i, a) if rfun else 1.0)
            ring.append(bm.verts.new(p + n * (math.cos(a) * rr * flat) + b * (math.sin(a) * rr)))
        rings.append(ring)
    if cap_end:  # bán cầu đầu ngón
        t, n, b = fr[-1]; p = pts[-1]; r = radii[-1]
        for s in (0.55, 0.85):
            ring = [bm.verts.new(p + t * (r * math.sin(s * math.pi / 2) * 0.9) + (n * (math.cos(2 * math.pi * k / segs) * flat) + b * math.sin(2 * math.pi * k / segs)) * r * math.cos(s * math.pi / 2)) for k in range(segs)]
            rings.append(ring)
        tip = bm.verts.new(p + t * r * 0.9)
    for A, B in zip(rings, rings[1:]):
        for k in range(segs):
            j = (k + 1) % segs; bm.faces.new((A[k], A[j], B[j], B[k]))
    if cap_end:
        for k in range(segs): bm.faces.new((rings[-1][k], rings[-1][(k + 1) % segs], tip))
    if cap_start: bm.faces.new(list(reversed(rings[0])))
    return rings

def chain(start, d0, bend_axis, lens, bends, r0, r1, steps=3):
    """Ngón tay: các đốt nối nhau, mỗi khớp gập quanh bend_axis. Trả về điểm + bán kính (khớp gồ 6%)."""
    pts = [start.copy()]; rad = [r0 * 1.04]; d = d0.normalized(); p = start.copy(); total = sum(lens); acc = 0
    for li, (L, bnd) in enumerate(zip(lens, bends)):
        d = (Matrix.Rotation(bnd, 3, bend_axis) @ d).normalized()
        for s in range(1, steps + 1):
            p = p + d * (L / steps); acc += L / steps; pts.append(p.copy())
            r = r0 + (r1 - r0) * (acc / total)
            if s == steps and li < len(lens) - 1: r *= 1.07  # khớp ngón gồ lên
            elif s == steps // 2 + 1 and steps > 2: r *= 0.97  # giữa đốt thon nhẹ
            rad.append(r)
    return pts, rad

# ---------------- BÀN TAY ----------------
bm = bmesh.new()
# lòng bàn tay: khối hộp chia nhỏ -> subdivision cho tròn trịa, mu tay hơi vồng, mép ngón út thon
pal = bmesh.new(); bmesh.ops.create_cube(pal, size=1.0)
bmesh.ops.subdivide_edges(pal, edges=[e for e in pal.edges if abs((e.verts[0].co-e.verts[1].co).z)>0.5], cuts=1, use_grid_fill=True)
for v in pal.verts:
    x, y, z = v.co  # x: ngang, y: dày, z: dọc
    w = 0.084 if z >= 0 else 0.07                 # rộng ở hàng khớp ngón, hẹp về cổ tay (sau subsurf co lại ~15%)
    th = 0.036 * (0.85 if x < 0 else 1.0)         # mép ngón út mỏng hơn mép ngón cái
    v.co = Vector((x * w, y * th + (0.004 if y > 0 else 0), z * 0.1))
pm = bpy.data.meshes.new('palm'); pal.to_mesh(pm); pal.free()
po = bpy.data.objects.new('palm', pm); scn.collection.objects.link(po)
sd = po.modifiers.new('sd', 'SUBSURF'); sd.levels = 3; sd.render_levels = 3
bpy.context.view_layer.objects.active = po; bpy.ops.object.modifier_apply(modifier='sd')
bm.from_mesh(po.data); bpy.data.objects.remove(po)

# 4 ngón (i=0 út ... i=3 trỏ; ngón cái ở +X). Tư thế nắm báng/ốp lót tay: gập mạnh.
X = Vector((1, 0, 0))
FING = [  # x, chiều dài 3 đốt, bán kính gốc/ngọn, độ gập 3 khớp, lệch z gốc
    (-0.027, (0.032, 0.020, 0.017), 0.0078, 0.0062, (1.00, 1.10, 0.55), -0.006),
    (-0.009, (0.041, 0.026, 0.019), 0.0088, 0.0068, (0.95, 1.12, 0.60), 0.000),
    (0.009, (0.045, 0.028, 0.020), 0.0092, 0.0070, (0.90, 1.12, 0.60), 0.002),
    (0.027, (0.042, 0.025, 0.019), 0.0090, 0.0068, (0.80, 1.05, 0.55), 0.000),
]
for fx, lens, r0, r1, bends, dz in FING:
    start = Vector((fx, -0.002, 0.036 + dz)); pts, rad = chain(start, Vector((0, 0.05, 1)), X, lens, bends, r0, r1, steps=3)
    sweep(bm, pts, rad, segs=8, flat=0.86, rfun=lambda i, a: 1.0 + (0.05 if (math.cos(a) > 0.6 and i in (3, 6)) else 0))  # gồ khớp phía mu
# ngón cái: mọc từ mép trong gần cổ tay, chĩa chéo xuống-trước, ôm vòng quanh báng
tpts, trad = chain(Vector((0.03, -0.008, -0.012)), Vector((0.35, -0.55, 0.75)), Vector((0, 0.25, 1)).normalized(), (0.036, 0.03, 0.024), (0.0, -0.55, -0.45), 0.0125, 0.0082, steps=3)
sweep(bm, tpts, trad, segs=8, flat=0.85)
# gò cơ ngón cái (mô cái) nối ngón cái với lòng bàn tay
sweep(bm, [Vector((0.02, -0.012, -0.03)), Vector((0.028, -0.012, -0.01)), Vector((0.032, -0.01, 0.006))], [0.013, 0.015, 0.012], segs=10, cap_end=True, cap_start=True)
# cổ tay: lùi về -Z vào trong ống tay áo
wp = [Vector((0, 0, z)) for z in (-0.02, -0.045, -0.07, -0.095)]
sweep(bm, wp, [0.031, 0.029, 0.03, 0.032], segs=12, cap_end=False, cap_start=True, flat=0.72)
hm = bpy.data.meshes.new('hand'); bm.to_mesh(hm); bm.free()
hand = bpy.data.objects.new('hand', hm); scn.collection.objects.link(hand); hm.materials.append(MATS['skin'])

# ---------------- ỐNG TAY ÁO ----------------
bm = bmesh.new(); SEG = 18; NZ = 26; Z_END = 0.86
folds = [(random.uniform(0.15, 0.75), random.uniform(0, 6.28), random.uniform(0.04, 0.07)) for _ in range(5)]
rings = []
for iz in range(NZ + 1):
    z = Z_END * iz / NZ; ring = []
    for k in range(SEG):
        a = 2 * math.pi * k / SEG
        r = 0.049 + (0.039 - 0.049) * (z / Z_END)
        for fz, fa, amp in folds:  # nếp gấp vải: gờ chạy chéo quanh ống, mạnh ở mặt trong khuỷu
            r *= 1 + amp * math.exp(-((z - fz - 0.05 * math.sin(a + fa)) / 0.035) ** 2) * (0.6 + 0.4 * math.cos(a - fa))
        if z > Z_END - 0.09:  # gấu tay áo xắn: phồng tròn
            u = (z - (Z_END - 0.09)) / 0.09; r *= 1 + 0.16 * math.sin(u * math.pi) ** 0.7
        ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a) * 0.9, z)))
    rings.append(ring)
# mép gấu cuộn vào trong (tránh nhìn thấy lỗ hở)
inner = [bm.verts.new((v.co.x * 0.86, v.co.y * 0.86, Z_END - 0.02)) for v in rings[-1]]
rings.append(inner)
for A, B in zip(rings, rings[1:]):
    for k in range(SEG):
        j = (k + 1) % SEG; bm.faces.new((A[k], A[j], B[j], B[k]))
bm.faces.new(list(reversed(rings[0])))
sm = bpy.data.meshes.new('sleeve'); bm.to_mesh(sm); bm.free()
sleeve = bpy.data.objects.new('sleeve', sm); scn.collection.objects.link(sleeve); sm.materials.append(MATS['sleeve'])

# ---------------- UV, AO đỉnh, chuẩn hướng, xuất ----------------
def vertex_ao(o, dist, n_rays=24, floor=0.42, zscale=1.0):
    me = o.data; bm = bmesh.new(); bm.from_mesh(me); bm.normal_update()
    vs = [v.co.copy() for v in bm.verts]
    if zscale != 1.0:  # tay áo trong game dài ~0.3 m: tính AO trên hình đã kéo đúng tỉ lệ
        for v in bm.verts: v.co.z *= zscale
        bm.normal_update()
    tree = BVHTree.FromBMesh(bm); ao = []
    dirs = []
    for i in range(n_rays):  # bán cầu Fibonacci
        zc = (i + 0.5) / n_rays; r = math.sqrt(1 - zc * zc); ph = i * 2.39996
        dirs.append(Vector((r * math.cos(ph), r * math.sin(ph), zc)))
    for v in bm.verts:
        n = v.normal; t = n.orthogonal().normalized(); b = n.cross(t); occ = 0.0
        for d in dirs:
            w = (t * d.x + b * d.y + n * d.z).normalized()
            hit = tree.ray_cast(v.co + n * 0.0006, w, dist)
            if hit[0] is not None: occ += (1 - hit[3] / dist) * d.z
        ao.append(max(floor, 1 - 1.9 * occ / sum(d.z for d in dirs)))
    bm.free()
    ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
    for i, c in enumerate(ao): ca.data[i].color = (c, c, c, 1)
    me.color_attributes.active_color = ca

for o in (hand, sleeve):
    for p in o.data.polygons: p.use_smooth = True
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    if o is hand: bpy.ops.uv.cube_project(cube_size=0.25)
    bpy.ops.object.mode_set(mode='OBJECT'); o.select_set(False)
# UV ống tay: trụ (u quanh ống, v dọc), vân vải ~0.25 m mỗi ô khi cẳng tay dài 0.3 m
uvl = sleeve.data.uv_layers.new(name='UV'); sv = sleeve.data.vertices
for poly in sleeve.data.polygons:
    for li in poly.loop_indices:
        co = sv[sleeve.data.loops[li].vertex_index].co
        a = math.atan2(co.y, co.x) / (2 * math.pi) + 0.5
        uvl.data[li].uv = (a * 0.55, co.z * 1.2)
    us = [uvl.data[li].uv[0] for li in poly.loop_indices]  # sửa đường nối u
    if max(us) - min(us) > 0.3:
        for li in poly.loop_indices:
            if uvl.data[li].uv[0] < 0.2: uvl.data[li].uv = (uvl.data[li].uv[0] + 0.55, uvl.data[li].uv[1])
vertex_ao(hand, 0.03)
vertex_ao(sleeve, 0.05, floor=0.55, zscale=0.32)
# hệ game -> hệ Blender (xuất +Y up sẽ đổi ngược lại): Bx=gx, By=-gz, Bz=gy
G2B = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
for o in (hand, sleeve): o.data.transform(G2B); o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_yup=True, export_normals=True,
                          export_texcoords=True, export_materials='EXPORT', export_vertex_color='ACTIVE', export_all_vertex_colors=False)
print('exported', OUT, os.path.getsize(OUT), {o.name: (len(o.data.vertices), sum(len(p.vertices) - 2 for p in o.data.polygons)) for o in (hand, sleeve)})
