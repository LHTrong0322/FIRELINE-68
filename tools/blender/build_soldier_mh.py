# Dựng lính FIRELINE '68 từ thân người MakeHuman (CC0) + xương "game_engine" (CC0) + quân phục may theo dáng người.
# Chạy:  python3 tools/blender/build_soldier_mh.py <out.glb>      (cần: pip install bpy)
# Biến môi trường: ETH=asian|caucasian|african (khuôn mặt), KIT=vn|us (quần áo/giày), PREVIEW=1 (ảnh xem trước /tmp/mh_*.png)
import bpy, bmesh, json, gzip, math, os, sys
from mathutils import Vector, Quaternion, Matrix

HERE = os.path.dirname(os.path.abspath(__file__)); MH = os.path.join(HERE, 'mh')
OUT = sys.argv[-1] if sys.argv[-1].endswith('.glb') else '/tmp/soldier_mh.glb'
ETH = os.environ.get('ETH', 'asian'); KIT = os.environ.get('KIT', 'vn')
bpy.ops.wm.read_factory_settings(use_empty=True); scn = bpy.context.scene

# ---------- đọc lưới gốc
V = []; UV = []; F = []; grp = None
for line in gzip.open(MH + '/base.obj.gz', 'rt'):
    if line.startswith('v '): V.append([float(t) for t in line.split()[1:4]])
    elif line.startswith('vt '): UV.append([float(t) for t in line.split()[1:3]])
    elif line.startswith('g '): grp = line.split()[1]
    elif line.startswith('f '):
        ps = [p.split('/') for p in line.split()[1:]]
        F.append(([int(p[0]) - 1 for p in ps], [int(p[1]) - 1 if len(p) > 1 and p[1] else 0 for p in ps], grp))

def target(name, w):
    for line in gzip.open(MH + f'/{name}.target.gz', 'rt'):
        t = line.split()
        if len(t) == 4 and not line.startswith('#'):
            i = int(t[0]); V[i][0] += w * float(t[1]); V[i][1] += w * float(t[2]); V[i][2] += w * float(t[3])
target('universal-male-young-maxmuscle-averageweight', 0.45)
target({'asian': 'asian-male-young', 'african': 'african-male-young'}.get(ETH, 'caucasian-male-young'), 1.0 if ETH == 'asian' else 0.85)
# ---------- "đại phẫu" khuôn mặt (v4.7): tinh chỉnh bằng các target chi tiết CC0 của MakeHuman (mpfb2)
SCULPT = {
  'asian': {'head/head-oval': 0.35, 'head/head-square': 0.3, 'chin/chin-prominent-incr': 0.5, 'chin/chin-width-decr': 0.1, 'chin/chin-height-incr': 0.12,
            'cheek/l-cheek-bones-incr': 0.35, 'cheek/r-cheek-bones-incr': 0.35, 'cheek/l-cheek-volume-decr': 0.25, 'cheek/r-cheek-volume-decr': 0.25,
            'nose/nose-width1-decr': 0.2, 'nose/nose-point-width-decr': 0.25, 'nose/nose-flaring-decr': 0.3, 'nose/nose-trans-forward': 0.15, 'nose/nose-scale-vert-incr': 0.12,
            'eyes/l-eye-scale-incr': 0.18, 'eyes/r-eye-scale-incr': 0.18, 'eyes/l-eye-corner1-up': 0.15, 'eyes/r-eye-corner1-up': 0.15,
            'eyebrows/eyebrows-trans-down': 0.25, 'eyebrows/eyebrows-angle-up': 0.2, 'mouth/mouth-lowerlip-volume-incr': 0.15, 'mouth/mouth-scale-horiz-decr': 0.08,
            'head/head-fat-decr': 0.3, 'head/head-age-incr': 0.35, 'forehead/forehead-scale-vert-decr': 0.35,
            'eyes/l-eye-height2-incr': 0.3, 'eyes/r-eye-height2-incr': 0.3},
  'caucasian': {'head/head-square': 0.4, 'chin/chin-prominent-incr': 0.4, 'chin/chin-width-incr': 0.2, 'cheek/l-cheek-bones-incr': 0.25, 'cheek/r-cheek-bones-incr': 0.25,
            'nose/nose-hump-incr': 0.2, 'eyebrows/eyebrows-trans-down': 0.3, 'head/head-fat-decr': 0.3, 'cheek/l-cheek-volume-decr': 0.3, 'cheek/r-cheek-volume-decr': 0.3},
}
for k, w in SCULPT.get(ETH, {}).items(): target('face/' + k, w)
# vùng ảnh hưởng của target -> mặt nạ để vẽ da (môi, lông mày, mí, quầng mắt, mũi, má, râu, tai)
def tmask(names):
    m = {}
    for n in names:
        for line in gzip.open(MH + f'/face/{n}.target.gz', 'rt'):
            t = line.split()
            if len(t) == 4 and not line.startswith('#'):
                i = int(t[0]); m[i] = m.get(i, 0) + math.sqrt(sum(float(x) ** 2 for x in t[1:]))
    mx = max(m.values()) if m else 1
    return {i: min(1.0, v / mx * 1.8) for i, v in m.items()}
MASKS = [tmask(['mouth/mouth-upperlip-volume-incr', 'mouth/mouth-lowerlip-volume-incr']),
         tmask(['eyebrows/eyebrows-trans-up']),
         tmask(['eyes/l-eye-height2-incr', 'eyes/r-eye-height2-incr', 'eyes/l-eye-eyefold-down', 'eyes/r-eye-eyefold-down']),
         tmask(['eyes/l-eye-bag-incr', 'eyes/r-eye-bag-incr']),
         tmask(['nose/nose-volume-incr']),
         tmask(['cheek/l-cheek-volume-incr', 'cheek/r-cheek-volume-incr']),
         tmask(['chin/chin-prominent-incr', 'chin/chin-width-incr', 'mouth/mouth-philtrum-volume-incr', 'mouth/mouth-laugh-lines-in'])]

def tb(v): return Vector((v[0] * 0.1, -v[2] * 0.1, v[1] * 0.1))
P = [tb(v) for v in V]
groups = {}
for vi, ti, g in F: groups.setdefault(g, set()).update(vi)
def centroid(g): s = groups[g]; return sum((P[i] for i in s), Vector()) / len(s)
ground = min(P[i].z for i in groups['body'])
for p in P: p.z -= ground

# ---------- xương (game_engine rig)
RIG = json.load(open(MH + '/rig.game_engine.json'))
W = json.load(gzip.open(MH + '/weights.game_engine.json.gz', 'rt'))['weights']
RN = {'Root': 'rootG', 'pelvis': 'root', 'spine_01': 'spine', 'spine_02': 'spine2', 'spine_03': 'chest', 'neck_01': 'neck', 'head': 'head',
      'clavicle_l': 'clavL', 'clavicle_r': 'clavR', 'upperarm_l': 'upperArmL', 'upperarm_r': 'upperArmR', 'lowerarm_l': 'forearmL', 'lowerarm_r': 'forearmR',
      'hand_l': 'handL', 'hand_r': 'handR', 'thigh_l': 'thighL', 'thigh_r': 'thighR', 'calf_l': 'shinL', 'calf_r': 'shinR', 'foot_l': 'footL', 'foot_r': 'footR', 'ball_l': 'ballL', 'ball_r': 'ballR'}
rn = lambda n: RN.get(n, n)
def jpos(spec):
    if spec['strategy'] == 'CUBE': return centroid(spec['cube_name'])
    return sum((P[i] for i in spec['vertex_indices']), Vector()) / len(spec['vertex_indices'])
ad = bpy.data.armatures.new('rig'); arm = bpy.data.objects.new('rig', ad); scn.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='EDIT'); eb = ad.edit_bones
for n, b in RIG.items():
    e = eb.new(rn(n)); e.head = jpos(b['head']); e.tail = jpos(b['tail'])
    if (e.tail - e.head).length < 1e-3: e.tail = e.head + Vector((0, 0, 0.05))
    e.roll = b.get('roll', 0)
for n, b in RIG.items():
    if b.get('parent'): eb[rn(n)].parent = eb[rn(b['parent'])]; eb[rn(n)].use_connect = bool(b.get('use_connect'))
# xương IK (không biến dạng) gắn vào ngực
SH = {s: eb['upperArm' + s].head.copy() for s in 'LR'}
def addb(name, head, parent):
    b = eb.new(name); b.head = Vector(head); b.tail = Vector(head) + Vector((0, 0, 0.05)); b.parent = eb[parent]; b.use_deform = False
OZ = SH['R'].z - 1.2934  # bám theo chiều cao vai (người cao/thấp)
def Z(v): return (v[0], v[1], v[2] + OZ)
AIM_R = Z((-0.075, -0.225, 1.16)); AIM_L = Z((0.0, -0.37, 1.19))
addb('ikR', AIM_R, 'chest'); addb('ikL', AIM_L, 'chest')
bpy.ops.object.mode_set(mode='OBJECT')
print('shoulders', SH, 'height', max(P[i].z for i in groups['body']))

# ---------- phân vùng da / áo / quần / giày theo xương có trọng số lớn nhất
dom = {}
for bn, lst in W.items():
    for vi, w in lst:
        if w > dom.get(vi, ('', 0))[1]: dom[vi] = (bn, w)
J = {k: centroid(k) for k in ('joint-l-hand', 'joint-r-hand', 'joint-neck', 'joint-l-eye', 'joint-r-eye', 'joint-l-ankle', 'joint-r-ankle', 'joint-head', 'joint-head-2', 'joint-spine-4')}
waist_z = J['joint-spine-4'].z - 0.015; eye_z = (J['joint-l-eye'].z + J['joint-r-eye'].z) / 2; eye_y = (J['joint-l-eye'].y + J['joint-r-eye'].y) / 2
SHIRT = {'spine_01', 'spine_02', 'spine_03', 'clavicle_l', 'clavicle_r', 'upperarm_l', 'upperarm_r', 'lowerarm_l', 'lowerarm_r'}
LEGS = {'thigh_l', 'thigh_r', 'calf_l', 'calf_r'}
boot_top = 0.26 if KIT == 'us' else 0.0
def region(i):
    b = dom.get(i, ('', 0))[0]; p = P[i]
    if b in ('lowerarm_l', 'lowerarm_r', 'hand_l', 'hand_r'):
        h = J['joint-l-hand'] if b.endswith('_l') else J['joint-r-hand']
        if (p - h).length < 0.035 or b.startswith('hand'): return 'skin'
        return 'sleeve'
    if b in SHIRT: return 'sleeve' if b.startswith('upperarm') else 'shirt'
    if b == 'neck_01': return 'shirt' if p.z < J['joint-neck'].z - 0.035 else 'skin'
    if b == 'pelvis': return 'shirt' if p.z > waist_z else 'pants'
    if b in LEGS:
        if KIT == 'us' and p.z < boot_top: return 'boots'
        if KIT != 'us' and p.z < 0.115: return 'skin'
        return 'legs' if b.startswith('calf') else 'pants'
    if b.startswith('foot') or b.startswith('ball'): return 'boots' if KIT == 'us' else 'skin'
    if b == 'head':
        top = p.z > eye_z + 0.062 or (p.y > eye_y + 0.075 and p.z > eye_z - 0.045)
        if abs(p.x) > 0.066 and p.z < eye_z + 0.03: top = False  # tai không phủ tóc
        return 'hair' if top else 'skin'
    return 'skin'
REG = {}
for i in groups['body']: REG[i] = region(i)

# ---------- dựng lưới: thân (da + tóc), mắt, quần áo (vỏ bọc lệch theo pháp tuyến)
def build(name, faces, offs=None):
    used = sorted({i for f in faces for i in f[0]}); remap = {v: k for k, v in enumerate(used)}
    me = bpy.data.meshes.new(name); ob = bpy.data.objects.new(name, me); scn.collection.objects.link(ob)
    bm = bmesh.new(); vs = [bm.verts.new(P[i]) for i in used]; bm.verts.ensure_lookup_table(); uvl = bm.loops.layers.uv.new('UVMap')
    for vi, ti, _m in faces:
        try: f = bm.faces.new([vs[remap[i]] for i in vi])
        except ValueError: continue
        f.material_index = _m; f.smooth = True
        for l, t in zip(f.loops, ti): l[uvl].uv = UV[t]
    bm.normal_update()
    if offs:
        nrm = [v.normal.copy() for v in bm.verts]
        for k, v in enumerate(bm.verts): v.co += nrm[k] * offs(used[k], v.co, nrm[k])
    bm.to_mesh(me); bm.free()
    vg = {}
    for bn, lst in W.items():
        for vi, w in lst:
            if vi in remap:
                g = vg.get(bn) or ob.vertex_groups.new(name=rn(bn)); vg[bn] = g; g.add([remap[vi]], w, 'REPLACE')
    return ob, remap

MATS = ['skin', 'hair', 'eye', 'shirt', 'pants', 'boots']
def mat(n):
    m = bpy.data.materials.get(n) or bpy.data.materials.new(n); return m
CLOTH = {'shirt': 3, 'sleeve': 3, 'pants': 4, 'legs': 4, 'boots': 5}
body_f = []; cloth_f = []; eye_f = []
for vi, ti, g in F:
    if g == 'body':
        rs = [REG[i] for i in vi]
        if all(r in CLOTH for r in rs):
            cloth_f.append((vi, ti, CLOTH[max(set(rs), key=rs.count)]))
            continue
        if any(r in CLOTH for r in rs): cloth_f.append((vi, ti, CLOTH[[r for r in rs if r in CLOTH][0]]))
        body_f.append((vi, ti, 1 if rs.count('hair') * 2 >= len(rs) else 0))
    elif g in ('helper-l-eye', 'helper-r-eye'): eye_f.append((vi, ti, 2))

# vỏ quần áo: độ phồng + nếp gấp
AX = {}
for n in ('upperarm_l', 'upperarm_r', 'lowerarm_l', 'lowerarm_r', 'thigh_l', 'thigh_r', 'calf_l', 'calf_r'):
    a, b = jpos(RIG[n]['head']), jpos(RIG[n]['tail']); AX[n] = (a, (b - a).normalized(), (b - a).length)
def cloth_off(i, co, n):
    r = REG.get(i, 'skin'); b = dom.get(i, ('', 0))[0]
    base = {'shirt': 0.013, 'sleeve': 0.021, 'pants': 0.017, 'legs': 0.024, 'boots': 0.009}.get(r, 0.006)
    if b in AX and r in ('sleeve', 'pants', 'legs'):
        a, d, L = AX[b]; t = (co - a).dot(d); rad = co - a - d * t
        ang = math.atan2(rad.x, rad.y + 1e-6)
        k = clamp01(t / L)
        fold = 0.0075 * math.sin(t * 48 + 2.4 * math.sin(ang * 2 + t * 7)) * (0.35 + 0.65 * math.sin(k * math.pi)) + 0.003 * math.sin(ang * 5 + t * 20)
        sag = 0.012 * (k if r in ('legs', 'sleeve') else 0)
        if r == 'legs' and co.z < 0.2: sag -= 0.02 * (0.2 - co.z) / 0.08  # ống quần túm ở cổ chân  # ống quần, tay áo rộng dần về cuối
        return base + fold + sag
    if r == 'shirt':  # nếp áo nhăn ở eo (sơ vin) và nách
        dz = co.z - waist_z
        return base + (0.009 * max(0, 1 - dz / 0.1) * (0.5 + 0.5 * math.sin(co.x * 80))) + 0.004 * math.sin(co.z * 55 + co.x * 22) * (0.5 + 0.5 * math.sin(co.x * 13))
    return base
def clamp01(x): return 0 if x < 0 else 1 if x > 1 else x

# ---------- vẽ ảnh da + tóc (2048) và pháp tuyến lỗ chân lông
import numpy as np
sys.path.insert(0, HERE); import skintex
TONE = {'asian': (214, 168, 132), 'caucasian': (226, 182, 156), 'african': (118, 80, 58)}[ETH]
LIP = {'asian': (168, 108, 98), 'caucasian': (186, 112, 104), 'african': (112, 64, 56)}[ETH]
HAIRC = (16, 13, 11) if ETH != 'caucasian' else (58, 42, 30)
bmax = max(P[i].z for i in groups['body'])
def vmask(i):
    r = REG.get(i, 'skin'); hz = 1.0 if r == 'hair' else 0.0
    beard = MASKS[6].get(i, 0) * (1 - MASKS[0].get(i, 0))
    ear = 1.0 if (dom.get(i, ('', 0))[0] == 'head' and abs(P[i].x) > 0.068 and P[i].z < eye_z + 0.02 and P[i].z > eye_z - 0.07) else 0.0
    return [MASKS[0].get(i, 0), MASKS[1].get(i, 0), MASKS[2].get(i, 0), MASKS[3].get(i, 0), MASKS[4].get(i, 0), MASKS[5].get(i, 0), beard, hz, ear]
tu, tp, tm = [], [], []
for vi, ti, _m in body_f:
    idx = [(0, 1, 2)] if len(vi) == 3 else [(0, 1, 2), (0, 2, 3)]
    for a, b, c in idx:
        tu.append([UV[ti[a]], UV[ti[b]], UV[ti[c]]]); tp.append([list(P[vi[a]]), list(P[vi[b]]), list(P[vi[c]])]); tm.append([vmask(vi[a]), vmask(vi[b]), vmask(vi[c])])
TEXSZ = int(os.environ.get('TEXSZ', '2048'))
rgb, nrm = skintex.bake(np.array(tu, float), np.array(tp, float), np.array(tm, float), TEXSZ, TONE, HAIRC, LIP, stubble=0.35 if ETH == 'asian' else 0.5, eye=(eye_y, eye_z))
import cv2
SKIN_IMG = f'/tmp/skin_{ETH}.jpg'; SKIN_NRM = f'/tmp/skin_{ETH}_n.jpg'
cv2.imwrite(SKIN_IMG, rgb[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 88]); cv2.imwrite(SKIN_NRM, cv2.resize(nrm, (TEXSZ // 2, TEXSZ // 2), interpolation=cv2.INTER_AREA)[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 90])
# mắt: ảnh mống mắt CC0 của MakeHuman, làm sẫm thành nâu đen kiểu Á Đông
eimg = cv2.imread(MH + '/brown_eye.png', cv2.IMREAD_COLOR).astype(np.float32)
sat = eimg.max(2, keepdims=True) - eimg.min(2, keepdims=True); irisz = (sat > 40).astype(np.float32)
if ETH != 'caucasian': eimg = eimg * (1 - irisz * 0.55)
else: g_ = eimg.mean(2, keepdims=True); eimg = eimg * (1 - irisz) + irisz * g_ * np.array([1.25, 1.0, 0.72])  # mắt xanh xám (BGR)
EYE_IMG = f'/tmp/eye_{ETH}.jpg'; cv2.imwrite(EYE_IMG, cv2.resize(eimg, (512, 512), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 88])
print('skin baked', SKIN_IMG)

body, _ = build('body', body_f)
hair_extra = None
cloth, _ = build('cloth', cloth_f, cloth_off)
eyes, _ = build('eyes', eye_f)
for o in (body, cloth, eyes):
    for n in MATS: o.data.materials.append(mat(n))
# mắt gắn vào đầu
for v in eyes.data.vertices:
    for g in list(v.groups): pass
# UV mắt: chiếu cầu quanh tâm mỗi nhãn cầu lên ảnh mống mắt (tâm nhãn cầu dưới-trái của ảnh: u=.283, v=.292)
me = eyes.data
_vl = [v.co.copy() for v in me.vertices if v.co.x > 0]; _vr = [v.co.copy() for v in me.vertices if v.co.x <= 0]
EC = {'L': sum(_vl, Vector()) / len(_vl), 'R': sum(_vr, Vector()) / len(_vr)}
ER = sum((c - EC['L']).length for c in _vl) / len(_vl)
print('eye centers', EC, 'radius', ER, 'ymin', min(c.y for c in _vl))
# thay lưới mắt phụ bằng nhãn cầu tròn đều (UV chuẩn) cùng tâm, bán kính
bm = bmesh.new()
for c in EC.values():
    r = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=14, radius=ER * 0.98)
    for v in r['verts']: v.co += c
bm.to_mesh(me); bm.free()
me.uv_layers.new(name='UVMap') if not me.uv_layers else None
for p_ in me.polygons: p_.material_index = 2; p_.use_smooth = True
uvl = me.uv_layers.active.data
for poly in me.polygons:
    for li in poly.loop_indices:
        co = me.vertices[me.loops[li].vertex_index].co; c = EC['L'] if (co - EC['L']).length < (co - EC['R']).length else EC['R']
        d = (co - c).normalized(); th = math.acos(max(-1, min(1, -d.y))); ph = math.atan2(d.z, d.x)
        r = th / math.radians(21) * 0.112; uvl[li].uv = (0.283 + r * math.cos(ph), 0.292 + r * math.sin(ph))
eyes.vertex_groups.clear(); g = eyes.vertex_groups.new(name='head'); g.add(list(range(len(eyes.data.vertices))), 1.0, 'REPLACE')
# tóc: đẩy lớp tóc nổi lên 4mm
bm = bmesh.new(); bm.from_mesh(body.data); bm.normal_update()
for f in bm.faces:
    if f.material_index == 1:
        for v in f.verts: v.tag = True
for v in bm.verts:
    if v.tag: v.co += v.normal * 0.0045
bm.to_mesh(body.data); bm.free()

# giảm số đỉnh (điện thoại): bảo toàn khuôn mặt
def decimate(o, ratio):
    bpy.context.view_layer.objects.active = o; m = o.modifiers.new('dec', 'DECIMATE'); m.ratio = ratio; m.use_collapse_triangulate = False
    bpy.ops.object.modifier_apply(modifier='dec')
decimate(cloth, 0.8); decimate(body, 0.55)
for o in (body, cloth, eyes):
    o.parent = arm; md = o.modifiers.new('arm', 'ARMATURE'); md.object = arm
print('verts body', len(body.data.vertices), 'cloth', len(cloth.data.vertices), 'eyes', len(eyes.data.vertices))

# ---------- tư thế & hoạt ảnh
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='POSE'); pb = arm.pose.bones
for s in 'LR':
    c = pb['forearm' + s].constraints.new('IK'); c.target = arm; c.subtarget = 'ik' + s; c.chain_count = 2
for b in pb: b.rotation_mode = 'QUATERNION'
def rot(name, axis, ang):  # quay quanh trục toạ độ thế giới (tư thế gốc)
    b = arm.data.bones[name]; la = (b.matrix_local.to_3x3().inverted() @ Vector(axis)).normalized()
    pb[name].rotation_quaternion = Quaternion(la, ang) @ pb[name].rotation_quaternion
def set_ik(name, world):
    b = arm.data.bones[name]; pb[name].location = b.matrix_local.to_3x3().inverted() @ (Vector(world) - b.head_local)
def reset():
    for b in pb: b.rotation_quaternion = (1, 0, 0, 0); b.location = (0, 0, 0)
def foot_y(a):
    reset(); rot('thighL', (1, 0, 0), a); bpy.context.view_layer.update(); return (arm.matrix_world @ pb['shinL'].tail).y
S = 1 if foot_y(0.4) < foot_y(0) else -1; reset()
def calf_ok():  # chiều gập gối để cẳng chân ra sau
    reset(); rot('shinL', (1, 0, 0), 0.8); bpy.context.view_layer.update(); return (arm.matrix_world @ pb['footL'].head).y > pb['shinL'].head.y
K = 1 if calf_ok() else -1; reset()
print('signs', S, K)
FING = [f'{n}_0{i}_{s}' for n in ('index', 'middle', 'ring', 'pinky') for i in (1, 2, 3) for s in 'lr']
def grip(amt):  # nắm tay quanh báng súng
    for f in FING:
        b = arm.data.bones[f]; ax = b.matrix_local.to_3x3().col[0]
        pb[f].rotation_quaternion = Quaternion(b.matrix_local.to_3x3().inverted() @ ax, amt * (1.1 if f.endswith('1_l') or f.endswith('1_r') else 0.9))
    for s in 'lr':
        b = arm.data.bones[f'thumb_02_{s}']; pb[f'thumb_02_{s}'].rotation_quaternion = Quaternion((1, 0, 0), amt * 0.5)
def legs(t, amp, knee, bob=0.0):
    ph = math.sin(t)
    rot('thighL', (1, 0, 0), S * amp * ph); rot('thighR', (1, 0, 0), -S * amp * ph)
    rot('shinL', (1, 0, 0), K * knee * max(0, math.sin(t + 1.3))); rot('shinR', (1, 0, 0), K * knee * max(0, -math.sin(t + 1.3)))
    rot('footL', (1, 0, 0), -S * 0.25 * amp * math.cos(t)); rot('footR', (1, 0, 0), S * 0.25 * amp * math.cos(t))
    pb['root'].location = arm.data.bones['root'].matrix_local.to_3x3().inverted() @ Vector((0, 0, -bob * abs(math.cos(t))))
def key_all(f):
    for b in pb: b.keyframe_insert('rotation_quaternion', frame=f); b.keyframe_insert('location', frame=f)
actions = {}
def make(name, frames, fn):
    act = bpy.data.actions.new(name); arm.animation_data_create(); arm.animation_data.action = act
    for f in range(frames + 1): reset(); fn(f / frames); key_all(f + 1)
    actions[name] = act
def aimpose(r=AIM_R, l=AIM_L, lean=0.0):
    set_ik('ikR', r); set_ik('ikL', l); grip(1.0); rot('spine2', (1, 0, 0), -S * lean); rot('head', (1, 0, 0), S * lean * 0.6)
make('aim', 2, lambda u: (aimpose(lean=0.05), rot('thighL', (1, 0, 0), S * 0.08), rot('shinL', (1, 0, 0), K * 0.12), rot('thighR', (1, 0, 0), -S * 0.06)))
make('walk', 24, lambda u: (aimpose(lean=0.06), legs(u * 2 * math.pi, 0.42, 0.8, 0.02)))
make('run', 16, lambda u: (aimpose(Z((-0.075, -0.2, 1.14)), Z((0.0, -0.35, 1.17)), 0.2), legs(u * 2 * math.pi, 0.6, 1.3, 0.04)))
FREE_R = Z((-0.21, -0.03, 0.86)); FREE_L = Z((0.21, -0.03, 0.86))
make('idle', 2, lambda u: (set_ik('ikR', FREE_R), set_ik('ikL', FREE_L), grip(0.35)))
make('walkFree', 24, lambda u: (set_ik('ikR', Z((-0.21, -0.07 * math.sin(u * 6.28), 0.87))), set_ik('ikL', Z((0.21, 0.07 * math.sin(u * 6.28), 0.87))), grip(0.35), legs(u * 2 * math.pi, 0.4, 0.75, 0.02)))
def captive(u):
    set_ik('ikR', Z((-0.05, 0.14, 0.93))); set_ik('ikL', Z((0.05, 0.14, 0.93))); grip(0.5)
    rot('shinL', (1, 0, 0), K * 1.55); rot('shinR', (1, 0, 0), K * 1.55); rot('neck', (1, 0, 0), -S * 0.35)
make('captive', 2, captive)
def death(u):
    k = min(1, u * 1.6); set_ik('ikR', Z((-0.3, 0.08, 0.7))); set_ik('ikL', Z((0.3, 0.08, 0.7))); grip(0.3)
    rot('shinL', (1, 0, 0), K * 0.9 * k); rot('shinR', (1, 0, 0), K * 0.6 * k); rot('thighL', (1, 0, 0), S * 0.5 * k); rot('thighR', (1, 0, 0), S * 0.2 * k)
    rot('spine', (1, 0, 0), -S * 0.25 * k); rot('neck', (1, 0, 0), -S * 0.4 * k)
make('death', 20, death)
for a in actions.values(): a.use_fake_user = True
arm.animation_data.action = actions['aim']; scn.frame_set(1); bpy.context.view_layer.update()
mw = arm.matrix_world
info = {'wristR': list(mw @ pb['forearmR'].tail), 'wristL': list(mw @ pb['forearmL'].tail), 'headTop': max(P[i].z for i in groups['body']),
        'head': list(mw @ arm.data.bones['head'].head_local), 'eye': [0, eye_y, eye_z], 'neck': list(J['joint-neck']), 'waist': waist_z,
        'shoulderR': list(SH['R']), 'shoulderL': list(SH['L'])}
print('INFO', json.dumps(info))
bpy.ops.object.mode_set(mode='OBJECT')

# ---------- vật liệu có ảnh (xuất kèm GLB)
def img_mat(name, path, npath=None, rough=0.55):
    m = mat(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes.get('Principled BSDF')
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(path); nt.links.new(tx.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    if npath:
        tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = bpy.data.images.load(npath); tn.image.colorspace_settings.name = 'Non-Color'
        nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
img_mat('skin', SKIN_IMG, SKIN_NRM, 0.55); img_mat('hair', SKIN_IMG, SKIN_NRM, 0.7); img_mat('eye', EYE_IMG, None, 0.15)

# ---------- xuất GLB
for o in scn.objects: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS', export_force_sampling=True,
    export_def_bones=False, export_skins=True, export_morph=False, export_apply=False, export_yup=True, export_texcoords=True, export_normals=True, export_materials='EXPORT', export_image_format='JPEG', export_jpeg_quality=86)
print('exported', OUT, os.path.getsize(OUT))

if os.environ.get('PREVIEW'):
    cols = {'skin': (0.72, 0.52, 0.38, 1), 'hair': (0.05, 0.04, 0.03, 1), 'eye': (0.15, 0.1, 0.08, 1), 'shirt': (0.33, 0.38, 0.22, 1), 'pants': (0.3, 0.34, 0.2, 1), 'boots': (0.08, 0.07, 0.06, 1)}
    for m in bpy.data.materials: m.diffuse_color = cols.get(m.name, (1, 0, 1, 1))
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scn.collection.objects.link(cam); scn.camera = cam
    scn.render.engine = 'BLENDER_WORKBENCH'; scn.display.shading.color_type = 'MATERIAL'; scn.display.shading.light = 'STUDIO'
    scn.render.resolution_x = 420; scn.render.resolution_y = 640
    shots = [('aim', 1, (1.5, -2.5, 1.3), 82, 32), ('walk', 7, (1.5, -2.5, 1.3), 82, 32), ('run', 5, (2.6, 0.2, 1.1), 85, 92), ('captive', 1, (1.5, -2.5, 1.3), 82, 32), ('death', 20, (1.5, -2.5, 1.3), 82, 32), ('face', 1, (0.25, -0.75, 1.6), 88, 18)]
    for nm, fr, loc, rx, rz in shots:
        arm.animation_data.action = actions['aim' if nm == 'face' else nm]; scn.frame_set(fr)
        cam.location = loc; cam.rotation_euler = (math.radians(rx), 0, math.radians(rz)); cam.data.lens = 85 if nm == 'face' else 50
        scn.render.filepath = f'/tmp/mh_{nm}.png'; bpy.ops.render.render(write_still=True)
    print('previews done')

if os.environ.get('FACEPREV'):  # ảnh xem trước có vật liệu thật (Cycles): /tmp/mhface_<ETH>_<n>.png
    scn.render.engine = 'CYCLES'; scn.cycles.samples = 24; scn.cycles.device = 'CPU'
    scn.view_settings.view_transform = 'AgX'
    w = bpy.data.worlds.new('w'); scn.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.5, 0.55, 0.6, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.6
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = 3.5; sun.rotation_euler = (math.radians(55), 0, math.radians(-35)); scn.collection.objects.link(sun)
    for nm in ('shirt', 'pants', 'boots'):
        m = mat(nm); m.use_nodes = True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = {'shirt': (0.12, 0.15, 0.07, 1), 'pants': (0.1, 0.12, 0.06, 1), 'boots': (0.02, 0.02, 0.02, 1)}[nm]
    cam = scn.camera or bpy.data.objects.new('cam2', bpy.data.cameras.new('cam2'))
    if cam.name not in scn.collection.objects: scn.collection.objects.link(cam)
    scn.camera = cam; arm.animation_data.action = actions['idle']; scn.frame_set(1)
    scn.render.resolution_x = 520; scn.render.resolution_y = 600
    hz = info['head'][2] + 0.07
    for k, (loc, rz) in enumerate([((0.0, -0.62, hz), 0), ((0.36, -0.5, hz), 36), ((0.0, -2.6, 1.0), 0), ((0.03, -0.3, eye_z), 0)]):
        cam.location = loc; cam.rotation_euler = (math.radians(90), 0, math.radians(rz)); cam.data.lens = 85 if k != 2 else 40
        scn.render.filepath = f'/tmp/mhface_{ETH}_{k}.png'; bpy.ops.render.render(write_still=True)
    print('face previews done')
