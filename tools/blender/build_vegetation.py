# Cây cối, đá cho bản đồ ngoài trời: lấy mô hình chụp thật Poly Haven (CC0: fern_02, shrub_03, rock_07),
# giảm đa giác cho điện thoại, và ghép dương xỉ thành tán cây cọ. Xuất 1 GLB gồm các mesh: fern, shrub, rock, palm.
# Chạy: python3 tools/blender/build_vegetation.py <thư mục poly haven> <out.glb>
import bpy, math, sys, os, random
from mathutils import Vector, Matrix
SRC = sys.argv[-2]; OUT = sys.argv[-1]; random.seed(3)
bpy.ops.wm.read_factory_settings(use_empty=True); scn = bpy.context.scene
def imp(name, ratio):
    before = set(scn.objects); bpy.ops.import_scene.gltf(filepath=f'{SRC}/{name}/{name}.gltf')
    ms = [o for o in scn.objects if o not in before and o.type == 'MESH']
    for o in scn.objects: o.select_set(False)
    for o in ms: o.select_set(True)
    bpy.context.view_layer.objects.active = ms[0]
    if len(ms) > 1: bpy.ops.object.join()
    o = bpy.context.object; o.parent = None; bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    m = o.modifiers.new('d', 'DECIMATE'); m.ratio = ratio; bpy.ops.object.modifier_apply(modifier='d')
    for e in [x for x in scn.objects if x.type == 'EMPTY']: bpy.data.objects.remove(e)
    o.name = name.split('_')[0]; print(name, 'tris', sum(len(p.vertices) - 2 for p in o.data.polygons)); return o
fern = imp('fern_02', 0.35); shrub = imp('shrub_03', 0.18); rock = imp('rock_07', 0.03)
for img in bpy.data.images:
    if img.size[0] > 512: img.scale(512, 512)
# cây cọ: thân cong + tán gồm nhiều lá dương xỉ phóng to
bpy.ops.curve.primitive_bezier_curve_add(); cu = bpy.context.object
sp = cu.data.splines[0]; pts = sp.bezier_points; pts[0].co = (0, 0, 0); pts[0].handle_left = (0, 0, -1); pts[0].handle_right = (0.2, 0, 2.5)
pts[1].co = (0.9, 0, 7.5); pts[1].handle_left = (0.4, 0, 5.5); pts[1].handle_right = (1.2, 0, 8.5)
cu.data.bevel_depth = 0.17; cu.data.bevel_resolution = 2; cu.data.resolution_u = 8; cu.data.use_fill_caps = True
bpy.ops.object.convert(target='MESH'); trunk = bpy.context.object
bm = bpy.data.materials.new('bark'); bm.use_nodes = True; b = bm.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (0.24, 0.18, 0.12, 1); b.inputs['Roughness'].default_value = 0.95
trunk.data.materials.append(bm)
for v in trunk.data.vertices:  # vân thân cọ: các vòng gờ
    r = Vector((v.co.x, v.co.y, 0)); 
    v.co += Vector((v.co.x - (0.9 * (v.co.z / 7.5) ** 2), v.co.y, 0)).normalized() * 0.03 * (1 if int(v.co.z * 3) % 2 else -1)
parts = [trunk]
leaf = fern.copy(); leaf.data = fern.data.copy(); scn.collection.objects.link(leaf)
bpy.context.view_layer.objects.active = leaf
for o in scn.objects: o.select_set(o == leaf)
m = leaf.modifiers.new('d', 'DECIMATE'); m.ratio = 0.3; bpy.ops.object.modifier_apply(modifier='d')
for i in range(7):
    c = leaf.copy(); c.data = leaf.data.copy(); scn.collection.objects.link(c)
    a = i / 7 * 2 * math.pi + random.uniform(-0.2, 0.2); s = random.uniform(3.2, 4.0)
    c.matrix_world = Matrix.Translation((0.9, 0, 7.4)) @ Matrix.Rotation(a, 4, 'Z') @ Matrix.Rotation(random.uniform(0.15, 0.5), 4, 'X') @ Matrix.Diagonal((s, s, s * 0.7, 1))
    parts.append(c)
for o in scn.objects: o.select_set(False)
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = trunk; bpy.ops.object.join(); palm = bpy.context.object; palm.name = 'palm'; bpy.data.objects.remove(leaf)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in scn.objects: o.location = (0, 0, 0)
for o in scn.objects: o.select_set(o.type == 'MESH')
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_yup=True, export_image_format='JPEG', export_jpeg_quality=80)
print('exported', OUT, os.path.getsize(OUT), [(o.name, len(o.data.vertices)) for o in scn.objects if o.type == 'MESH'])
