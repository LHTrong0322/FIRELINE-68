"""Dựng người lính có xương bằng Blender (chạy: python3 tools/blender/build_soldier.py out.glb)."""
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix
OUT = sys.argv[-1] if sys.argv[-1].endswith('.glb') else '/tmp/soldier.glb'
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

# ---- khung khớp (mét, Blender Z-up, nhân vật nhìn về -Y). (x,y,z, rx, ry)
J = {
 'pelvis':(0,0,0.96, .155,.11), 'spine':(0,0.005,1.12, .145,.105), 'chest':(0,0.0,1.30, .175,.115), 'chestT':(0,0.01,1.42, .165,.105),
 'neck':(0,0.015,1.52, .055,.055), 'head':(0,0.0,1.63, .095,.105), 'headT':(0,0.005,1.73, .08,.09),
}
for s,sx in (('L',1),('R',-1)):
  J.update({
   'hip'+s:(sx*0.095,0,0.93, .105,.108), 'knee'+s:(sx*0.105,-0.012,0.51, .074,.076), 'ankle'+s:(sx*0.105,0.01,0.085, .05,.054), 'toe'+s:(sx*0.11,-0.15,0.035, .047,.032),
   'shoulder'+s:(sx*0.195,0.0,1.43, .07,.068), 'elbow'+s:(sx*0.45,0.0,1.43, .056,.054), 'wrist'+s:(sx*0.7,0.0,1.43, .036,.03), 'hand'+s:(sx*0.79,0.0,1.43, .042,.016),
  })
E = [('pelvis','spine'),('spine','chest'),('chest','chestT'),('chestT','neck'),('neck','head'),('head','headT')]
for s in 'LR':
  E += [('pelvis','hip'+s),('hip'+s,'knee'+s),('knee'+s,'ankle'+s),('ankle'+s,'toe'+s),
        ('chestT','shoulder'+s),('shoulder'+s,'elbow'+s),('elbow'+s,'wrist'+s),('wrist'+s,'hand'+s)]
names=list(J.keys()); idx={n:i for i,n in enumerate(names)}
me=bpy.data.meshes.new('Body'); me.from_pydata([J[n][:3] for n in names],[(idx[a],idx[b]) for a,b in E],[]); me.update()
ob=bpy.data.objects.new('Soldier',me); scn.collection.objects.link(ob); bpy.context.view_layer.objects.active=ob; ob.select_set(True)
sk=ob.modifiers.new('Skin','SKIN'); sk.branch_smoothing=0.6; sk.use_smooth_shade=True
for n,i in idx.items():
  sv=me.skin_vertices[0].data[i]; sv.radius=(J[n][3],J[n][4])
me.skin_vertices[0].data[idx['pelvis']].use_root=True
sub=ob.modifiers.new('Sub','SUBSURF'); sub.levels=2; sub.render_levels=2
bpy.ops.object.skin_armature_create(modifier='Skin')
arm=[o for o in scn.objects if o.type=='ARMATURE'][0]
print('armature', arm.name, 'bones', len(arm.data.bones))
for b in arm.data.bones: print(' ', b.name, tuple(round(v,2) for v in b.head_local), tuple(round(v,2) for v in b.tail_local), b.parent.name if b.parent else None)
print('mods', [m.type for m in ob.modifiers], 'vgroups', len(ob.vertex_groups))

# ---- đặt tên xương theo khớp ở đuôi xương
tailname = {'spine':'spine','chest':'spine2','chestT':'chest','neck':'neck','head':'head','headT':'headTop'}
for s in 'LR': tailname.update({'hip'+s:'pelvis'+s,'knee'+s:'thigh'+s,'ankle'+s:'shin'+s,'toe'+s:'foot'+s,'shoulder'+s:'clav'+s,'elbow'+s:'upperArm'+s,'wrist'+s:'forearm'+s,'hand'+s:'hand'+s})
for b in list(arm.data.bones):
  t=b.tail_local; best=None; bd=9
  for n,(x,y,z,_,_) in J.items():
    d=(Vector((x,y,z))-t).length
    if d<bd: bd=d; best=n
  b.name = 'root' if best=='pelvis' else tailname[best]
print('renamed', sorted(b.name for b in arm.data.bones))
# ---- áp dụng da + làm mượt (giữ armature)
bpy.context.view_layer.objects.active=ob
while ob.modifiers[1].type!='SUBSURF': bpy.ops.object.modifier_move_up(modifier='Sub')
bpy.ops.object.modifier_apply(modifier='Skin'); bpy.ops.object.modifier_apply(modifier='Sub')
me=ob.data; print('verts', len(me.vertices), 'polys', len(me.polygons))
# ---- vùng vật liệu
for nm in ('skin','shirt','pants','boots'):
  m=bpy.data.materials.new(nm); ob.data.materials.append(m)
for p in me.polygons:
  c=p.center
  if c.z>1.545 or abs(c.x)>0.715: p.material_index=0
  elif c.z<0.135: p.material_index=3
  elif c.z<1.02 and abs(c.x)<0.24: p.material_index=2
  else: p.material_index=1
  p.use_smooth=True
# ---- UV
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.01); bpy.ops.object.mode_set(mode='OBJECT')
# ---- xương IK (không biến dạng) gắn vào ngực
bpy.context.view_layer.objects.active=arm; arm.select_set(True); bpy.ops.object.mode_set(mode='EDIT')
eb=arm.data.edit_bones
def addb(name, head, parent):
  b=eb.new(name); b.head=Vector(head); b.tail=Vector(head)+Vector((0,0,0.06)); b.parent=eb[parent]; b.use_deform=False; return b
addb('ikR',(-0.07,-0.26,1.28),'chest'); addb('ikL',(-0.02,-0.41,1.31),'chest')
addb('poleR',(-0.5,0.15,1.0),'chest'); addb('poleL',(0.45,-0.25,0.95),'chest')
bpy.ops.object.mode_set(mode='POSE')
pb=arm.pose.bones
for s,t,p in (('R','ikR','poleR'),('L','ikL','poleL')):
  c=pb['forearm'+s].constraints.new('IK'); c.target=arm; c.subtarget=t; c.chain_count=2  # không dùng pole: solver tự gập khuỷu ra ngoài, đạt mục tiêu chính xác hơn
for b in pb: b.rotation_mode='XYZ'
# ---- xác định chiều quay để chân bước về phía trước (-Y)
def foot_y(ang):
  pb['thighL'].rotation_euler=(ang,0,0); bpy.context.view_layer.update(); return (arm.matrix_world @ pb['shinL'].tail).y
S = 1 if foot_y(0.4) < foot_y(0) else -1
pb['thighL'].rotation_euler=(0,0,0)
print('leg sign', S)
REST={'ikR':Vector((-0.08,-0.17,1.21)),'ikL':Vector((-0.01,-0.42,1.26))}
def set_ik(name, world):  # đặt xương IK tới vị trí (toạ độ rest) bằng location tương đối
  b=arm.data.bones[name]; delta=Vector(world)-b.head_local
  pb[name].location = b.matrix_local.to_3x3().inverted() @ delta
def key_all(f):
  for b in pb:
    b.keyframe_insert('rotation_euler', frame=f); b.keyframe_insert('location', frame=f)
def reset():
  for b in pb: b.rotation_euler=(0,0,0); b.location=(0,0,0)
def legs(t, amp, knee):
  ph=math.sin(t); pb['thighL'].rotation_euler=(S*amp*ph,0,0); pb['thighR'].rotation_euler=(-S*amp*ph,0,0)
  pb['shinL'].rotation_euler=(-S*knee*max(0,math.sin(t+1.3)),0,0); pb['shinR'].rotation_euler=(-S*knee*max(0,-math.sin(t+1.3)),0,0)
actions={}
def make(name, frames, fn):
  act=bpy.data.actions.new(name); arm.animation_data_create(); arm.animation_data.action=act
  for f in range(frames+1): reset(); fn(f/frames); key_all(f+1)
  actions[name]=act; return act
AIM_R=(-0.07,-0.26,1.28); AIM_L=(-0.02,-0.41,1.31)
make('aim', 2, lambda u:(set_ik('ikR',AIM_R), set_ik('ikL',AIM_L), legs(0,0,0.08), pb['spine'].__setattr__('rotation_euler',(S*0.04,0,0))))
make('walk', 24, lambda u:(set_ik('ikR',AIM_R), set_ik('ikL',AIM_L), legs(u*2*math.pi,0.42,0.75)))
make('run', 16, lambda u:(set_ik('ikR',(-0.07,-0.23,1.25)), set_ik('ikL',(-0.01,-0.38,1.28)), legs(u*2*math.pi,0.75,1.3), pb['spine'].__setattr__('rotation_euler',(S*0.18,0,0))))
FREE_R=(-0.22,-0.02,0.92); FREE_L=(0.22,-0.02,0.92)
make('idle', 2, lambda u:(set_ik('ikR',FREE_R), set_ik('ikL',FREE_L)))
make('walkFree', 24, lambda u:(set_ik('ikR',(-0.22,-0.06*math.sin(u*6.28),0.93)), set_ik('ikL',(0.22,0.06*math.sin(u*6.28),0.93)), legs(u*2*math.pi,0.4,0.7)))
def captive(u):
  set_ik('ikR',(-0.05,0.17,1.02)); set_ik('ikL',(0.05,0.17,1.02))
  pb['thighL'].rotation_euler=(0,0,0); pb['thighR'].rotation_euler=(0,0,0)
  pb['shinL'].rotation_euler=(-S*1.55,0,0); pb['shinR'].rotation_euler=(-S*1.55,0,0)
  pb['neck'].rotation_euler=(S*0.35,0,0)
make('captive', 2, captive)
def death(u):
  k=min(1,u*1.6); set_ik('ikR',(-0.3,0.1,0.75)); set_ik('ikL',(0.3,0.1,0.75)); legs(0,0,0)
  pb['shinL'].rotation_euler=(-S*0.9*k,0,0); pb['shinR'].rotation_euler=(-S*0.6*k,0,0); pb['thighL'].rotation_euler=(S*0.5*k,0,0); pb['thighR'].rotation_euler=(S*0.2*k,0,0)
  pb['spine'].rotation_euler=(-S*0.25*k,0,0); pb['neck'].rotation_euler=(-S*0.4*k,0,0)
make('death', 20, death)
for a in actions.values(): a.use_fake_user=True
arm.animation_data.action=actions['aim']
bpy.ops.object.mode_set(mode='OBJECT')
# ---- xuất GLB
for o in scn.objects: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS', export_force_sampling=True,
  export_def_bones=False, export_skins=True, export_morph=False, export_apply=False, export_yup=True, export_texcoords=True, export_normals=True, export_materials='EXPORT')
import os; print('exported', OUT, os.path.getsize(OUT))
# ---- ảnh xem trước (workbench) nếu có biến môi trường PREVIEW
import os
if os.environ.get('PREVIEW'):
  cols={'skin':(0.75,0.55,0.4,1),'shirt':(0.33,0.38,0.22,1),'pants':(0.3,0.34,0.2,1),'boots':(0.08,0.07,0.06,1)}
  for m in ob.data.materials: m.diffuse_color=cols[m.name]
  cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); scn.collection.objects.link(cam); scn.camera=cam
  cam.location=(1.6,-2.6,1.4); cam.rotation_euler=(math.radians(82),0,math.radians(32))
  scn.render.engine='BLENDER_WORKBENCH'; scn.display.shading.color_type='MATERIAL'; scn.display.shading.light='STUDIO'
  scn.render.resolution_x=480; scn.render.resolution_y=640
  for nm,fr in (('aim',1),('walk',7),('run',5),('captive',1),('death',20)):
    arm.animation_data.action=actions[nm]; scn.frame_set(fr); scn.render.filepath=f'/tmp/prev_{nm}.png'; bpy.ops.render.render(write_still=True)
  print('previews done')
