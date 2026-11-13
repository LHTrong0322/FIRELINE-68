# Dựng khối bao cát cho 1 ô lưới (3m x 3m, cao ~1.1m) gồm nhiều bao riêng lẻ — xuất GLB
import bpy, bmesh, math, random, sys, os
from mathutils import Vector, Matrix
OUT = sys.argv[-1] if sys.argv[-1].endswith('.glb') else '/tmp/sandbags.glb'
random.seed(7); bpy.ops.wm.read_factory_settings(use_empty=True); scn = bpy.context.scene
# một bao cát: khối lập phương làm tròn, phồng giữa, thót hai đầu
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True)
for v in bm.verts:
    x, y, z = v.co
    r = 1 - 0.18 * (abs(x) * 2) ** 3          # thót đầu bao
    v.co = Vector((x * 0.58, y * 0.34 * r, z * 0.15 * (1.15 - 0.5 * (x * 2) ** 2)))
bag = bpy.data.meshes.new('bag'); bm.to_mesh(bag); bm.free()
obj = bpy.data.objects.new('bag', bag); scn.collection.objects.link(obj)
pass
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.cube_project(cube_size=0.6); bpy.ops.object.mode_set(mode='OBJECT')
bagme = obj.data
# xếp bao: vòng ngoài 3 lớp so le + lớp mặt trên
out = bmesh.new(); H = 0.15; S = 1.5
def place(x, y, z, rot):
    m = Matrix.Translation((x, y, z)) @ Matrix.Rotation(rot + random.uniform(-0.06, 0.06), 4, 'Z') @ Matrix.Rotation(random.uniform(-0.04, 0.04), 4, 'X')
    tmp = bmesh.new(); tmp.from_mesh(bagme); bmesh.ops.transform(tmp, matrix=m, verts=tmp.verts)
    sc = random.uniform(0.92, 1.05); bmesh.ops.scale(tmp, vec=(1, 1, sc), verts=tmp.verts, space=Matrix.Translation((-x, -y, -z)))
    me = bpy.data.meshes.new('t'); tmp.to_mesh(me); tmp.free(); out.from_mesh(me); bpy.data.meshes.remove(me)
for layer in range(4):
    z = 0.08 + layer * 0.26; off = 0.3 if layer % 2 else 0.0
    for side in range(4):
        for k in range(5):
            t = -S + 0.3 + off + k * 0.58
            if t > S - 0.25: continue
            inset = S - 0.36
            if side == 0: place(t, -inset, z, 0)
            if side == 1: place(t, inset, z, 0)
            if side == 2: place(-inset, t, z, math.pi / 2)
            if side == 3: place(inset, t, z, math.pi / 2)
for i in range(4):
    for j in range(3):
        place(-0.85 + j * 0.6 + (0.3 if i % 2 else 0), -0.9 + i * 0.6, 0.96, 0)
final = bpy.data.meshes.new('sandbags'); out.to_mesh(final); out.free()
for p in final.polygons: p.use_smooth = True
fo = bpy.data.objects.new('sandbags', final); scn.collection.objects.link(fo); bpy.data.objects.remove(obj)
fo.data.materials.append(bpy.data.materials.new('bag'))
for o in scn.objects: o.select_set(o == fo)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_yup=True, export_normals=True, export_texcoords=True, export_materials='EXPORT')
print('exported', OUT, os.path.getsize(OUT), len(final.vertices))
