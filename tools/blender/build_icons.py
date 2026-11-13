# Vẽ lại biểu tượng nút cảm ứng bằng mô hình 3D trong Blender (render Cycles, nền trong suốt)
# Chạy: python3 tools/blender/build_icons.py <thư mục ra>
import bpy, math, os, sys
from mathutils import Vector
OUT = sys.argv[-1] if len(sys.argv) > 1 and not sys.argv[-1].endswith('.py') else '/tmp/icons'
os.makedirs(OUT, exist_ok=True)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene; s.render.engine = 'CYCLES'; s.cycles.samples = 48; s.cycles.use_denoising = True
    s.render.film_transparent = True; s.render.resolution_x = s.render.resolution_y = 160
    s.view_settings.view_transform = 'Standard'; s.view_settings.look = 'Medium High Contrast'
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2.5; cam.location = (0, -6, 0.35); cam.rotation_euler = (math.radians(86), 0, 0)
    for nm, loc, e, sz, col in (('key', (-3, -4, 4), 900, 3, (1, .95, .85)), ('rim', (3, 3, 2), 500, 2, (.8, .9, 1)), ('fill', (2, -5, -1), 200, 4, (1, 1, 1))):
        L = bpy.data.lights.new(nm, 'AREA'); L.energy = e; L.size = sz; L.color = col
        o = bpy.data.objects.new(nm, L); s.collection.objects.link(o); o.location = loc
        o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    w = bpy.data.worlds.new('w'); s.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[1].default_value = 0.35
    return s

def mat(name, col, metal=0.0, rough=0.45, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = 2.0
    return m
def link(o, m):
    o.data.materials.append(m)
    for p in getattr(o.data, 'polygons', []): p.use_smooth = True
    return o
def bevel(o, w=0.03, seg=3):
    md = o.modifiers.new('b', 'BEVEL'); md.width = w; md.segments = seg; return o
def cyl(r, d, loc=(0, 0, 0), rot=(0, 0, 0), v=40, r2=None):
    if r2 is None: bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=v, location=loc, rotation=rot)
    else: bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r2, depth=d, vertices=v, location=loc, rotation=rot)
    return bpy.context.object
def box(sx, sy, sz, loc=(0, 0, 0), rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.scale = (sx, sy, sz); bpy.ops.object.transform_apply(scale=True); return o
def sph(r, loc=(0, 0, 0), sc=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=40, ring_count=20); o = bpy.context.object; o.scale = sc; return o
def tor(R, r, loc=(0, 0, 0), rot=(math.pi / 2, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot, major_segments=48, minor_segments=12); return bpy.context.object
def poly(pts, depth=0.18, loc=(0, 0, 0)):  # đa giác phẳng trong mặt XZ, đùn theo Y
    me = bpy.data.meshes.new('p'); o = bpy.data.objects.new('p', me); bpy.context.scene.collection.objects.link(o)
    vs = [(x, -depth / 2, z) for x, z in pts] + [(x, depth / 2, z) for x, z in pts]; n = len(pts)
    fs = [list(range(n))[::-1], list(range(n, 2 * n))] + [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    me.from_pydata(vs, [], fs); me.update(); o.location = loc; bevel(o, 0.025, 2); return o
def text(t, size=1.0, loc=(0, 0, 0), m=None):
    bpy.ops.object.text_add(location=loc, rotation=(math.pi / 2, 0, 0)); o = bpy.context.object; o.data.body = t; o.data.size = size
    o.data.extrude = 0.08; o.data.bevel_depth = 0.02; o.data.align_x = 'CENTER'; o.data.align_y = 'CENTER'; o.data.font = bpy.data.fonts.load('<builtin>') if False else o.data.font
    if m: o.data.materials.append(m)
    return o
def render(name):
    s = bpy.context.scene; s.render.filepath = os.path.join(OUT, name + '.png'); bpy.ops.render.render(write_still=True); print('icon', name)

BRASS = lambda: mat('brass', (0.95, 0.72, 0.32), 1.0, 0.28)
STEEL = lambda: mat('steel', (0.55, 0.57, 0.6), 1.0, 0.32)
IVORY = lambda: mat('ivory', (0.93, 0.9, 0.82), 0.0, 0.4)
OLIVE = lambda: mat('olive', (0.25, 0.3, 0.14), 0.0, 0.55)
RED = lambda: mat('red', (0.8, 0.06, 0.04), 0.0, 0.4)
GREEN = lambda: mat('green', (0.2, 0.85, 0.45), 0.0, 0.35)
DARK = lambda: mat('dark', (0.06, 0.06, 0.06), 0.3, 0.5)
WOOD = lambda: mat('wood', (0.45, 0.22, 0.08), 0.0, 0.5)

# BẮN: viên đạn đồng
reset(); b = BRASS()
link(bevel(cyl(0.3, 1.1, (0, 0, -0.35))), b); link(cyl(0.3, 0.75, (0, 0, 0.55), r2=0.02), mat('cu', (0.85, 0.42, 0.22), 1.0, 0.25)); link(bevel(cyl(0.33, 0.12, (0, 0, -0.93))), b)
bpy.ops.object.select_all(action='DESELECT')
ms=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active=ms[0]; bpy.ops.object.join(); bpy.context.object.rotation_euler[1]=math.radians(-35); bpy.context.object.location=(0,0,0.05)
render('fire')
# NHẢY: mũi tên lên đôi
reset(); m = IVORY()
for z in (-0.35, 0.3): link(poly([(-0.85, z - 0.25), (0, z + 0.55), (0.85, z - 0.25), (0.6, z - 0.48), (0, z + 0.08), (-0.6, z - 0.48)]), m)
render('jump')
# NGỒI: mũi tên xuống + vạch đất
reset(); m = IVORY()
link(poly([(-0.85, 0.5), (0, -0.3), (0.85, 0.5), (0.6, 0.73), (0, 0.17), (-0.6, 0.73)]), m); link(bevel(box(1.7, 0.18, 0.16, (0, 0, -0.75))), OLIVE())
render('crouch')
# NẰM / BÒ: người nằm sấp
reset(); m = IVORY()
link(sph(0.25, (-0.85, 0, -0.05)), m); link(bevel(box(1.1, 0.35, 0.32, (0.05, 0, -0.18)), 0.12, 4), m)
link(bevel(box(0.55, 0.28, 0.2, (-0.45, 0, 0.12), (0, math.radians(25), 0)), 0.08), m); link(bevel(box(0.8, 0.26, 0.2, (0.9, 0, -0.32), (0, math.radians(8), 0)), 0.08), m)
link(bevel(box(2.2, 0.2, 0.08, (0, 0, -0.58))), OLIVE())
render('prone')
# NẠP ĐẠN: băng đạn cong + chữ R
reset()
link(bevel(box(0.55, 0.4, 1.3, (-0.38, 0, -0.05), (0, math.radians(-12), 0)), 0.08), DARK())
for z in (0.5, 0.38): link(bevel(cyl(0.11, 0.42, (-0.3, 0, z + 0.12), (0, math.radians(78), 0))), BRASS())
link(text('R', 1.35, (0.42, -0.05, -0.08), IVORY()), None) if False else text('R', 1.35, (0.42, -0.05, -0.08), IVORY())
render('reload')
# NGẮM: ống ngắm + tâm ngắm
reset(); m = IVORY(); link(tor(0.8, 0.09), m)
for a in range(4):
    ang = a * math.pi / 2; link(bevel(box(0.5 if a % 2 == 0 else 0.1, 0.16, 0.1 if a % 2 == 0 else 0.5, (math.cos(ang) * 0.55, 0, math.sin(ang) * 0.55))), m)
link(sph(0.09), RED()); render('aim')
# ĐÈN PIN
reset(); s = STEEL()
o = link(bevel(cyl(0.22, 1.1, (-0.2, 0, -0.1), (0, math.radians(60), 0))), DARK()); link(cyl(0.34, 0.45, (0.4, 0, 0.25), (0, math.radians(60), 0), r2=0.22), s)
link(cyl(0.3, 0.05, (0.6, 0, 0.37), (0, math.radians(60), 0)), mat('lens', (1, .95, .7), 0, 0.1, emit=(1, .9, .6)))
for k in range(3):
    a = math.radians(40 + k * 22); link(bevel(box(0.5, 0.1, 0.08, (0.95 + 0.25 * math.cos(a), 0, 0.55 + 0.25 * math.sin(a) - 0.2), (0, -a, 0))), mat('ray', (1, .9, .5), 0, .4, emit=(1, .85, .4)))
render('light')
# LỰU ĐẠN
reset(); o = OLIVE(); link(sph(0.55, (0, 0, -0.15), (1, 1, 1.15)), o)
for z in (-0.45, -0.15, 0.15): link(tor(0.56 * math.cos(math.asin(min(.99, (z + 0.15) / 0.63))), 0.04, (0, 0, z), (0, 0, 0)), o)
link(bevel(cyl(0.18, 0.3, (0, 0, 0.62))), STEEL()); link(bevel(box(0.12, 0.14, 0.7, (0.26, 0, 0.35), (0, math.radians(-18), 0)), 0.04), STEEL()); link(tor(0.13, 0.03, (-0.28, 0, 0.72)), STEEL())
render('nade')
# BỘC PHÁ: khối thuốc nổ + kíp
reset(); w = mat('tnt', (0.42, 0.26, 0.12), 0, 0.7)
for x in (-0.5, 0, 0.5): link(bevel(box(0.46, 0.5, 1.0, (x, 0, -0.15)), 0.05), w)
link(bevel(box(1.55, 0.54, 0.14, (0, 0, -0.05)), 0.03), DARK()); link(bevel(box(0.3, 0.3, 0.25, (0, 0, 0.5)), 0.05), DARK()); link(sph(0.08, (0, -0.16, 0.55)), mat('led', (1, .1, .05), 0, .3, emit=(1, .1, .05)))
render('charge')
# CỨU THƯƠNG: hộp trắng chữ thập đỏ
reset(); link(bevel(box(1.6, 0.6, 1.2, (0, 0, -0.1)), 0.15, 4), IVORY()); r = RED()
link(bevel(box(0.3, 0.2, 0.85, (0, -0.32, -0.1)), 0.04), r); link(bevel(box(0.85, 0.16, 0.3, (0, -0.34, -0.1)), 0.04), r); link(bevel(box(0.7, 0.3, 0.12, (0, 0, 0.6)), 0.05), DARK())
render('heal')
# CỬA HÀNG (QUÂN NHU): xe đẩy chở hòm
reset(); s = STEEL()
link(poly([(-1.0, 0.45), (-0.75, 0.45), (-0.55, -0.35), (0.85, -0.35), (0.95, 0.2), (-0.62, 0.2), (-0.58, 0.05), (0.75, 0.05), (0.7, -0.2), (-0.66, -0.2)], 0.12), s)
link(bevel(box(0.5, 0.4, 0.4, (0.05, 0, 0.45)), 0.05), WOOD()); link(bevel(box(0.42, 0.4, 0.32, (0.55, 0, 0.41)), 0.05), OLIVE())
for x in (-0.35, 0.6): link(cyl(0.13, 0.12, (x, 0, -0.55), (math.pi / 2, 0, 0)), DARK())
render('shop')
# DÙNG / CỨU: bàn tay
reset(); m = mat('skin', (0.85, 0.62, 0.45), 0, 0.5)
link(bevel(box(0.8, 0.3, 0.75, (0, 0, -0.35)), 0.15, 4), m)
for i, (x, h) in enumerate(((-0.3, 0.62), (-0.1, 0.75), (0.1, 0.72), (0.3, 0.6))): link(bevel(box(0.17, 0.24, h, (x, 0, 0.05 + h / 2)), 0.08, 3), m)
link(bevel(box(0.5, 0.24, 0.17, (0.52, 0, -0.25), (0, math.radians(-40), 0)), 0.08, 3), m)
render('use')
# CHAT: bong bóng
reset(); m = IVORY(); link(bevel(box(1.7, 0.3, 1.1, (0, 0, 0.15)), 0.25, 5), m); link(poly([(-0.5, -0.4), (-0.8, -0.85), (-0.1, -0.4)], 0.3), m)
for x in (-0.45, 0, 0.45): link(sph(0.11, (x, -0.17, 0.15)), DARK())
render('chat')
# MENU / RỜI TRẬN: cửa + mũi tên
reset(); link(bevel(box(0.9, 0.2, 1.7, (0.35, 0, 0)), 0.04), WOOD()); link(sph(0.06, (0.05, -0.12, 0)), BRASS())
link(poly([(-1.05, 0), (-0.6, 0.42), (-0.6, 0.15), (-0.1, 0.15), (-0.1, -0.15), (-0.6, -0.15), (-0.6, -0.42)], 0.2, (0, -0.15, 0)), mat('or', (1, .7, .15), 0, .35))
render('exit')
print('done')
