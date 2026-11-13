# Vẽ (bake) ảnh da cho thân người MakeHuman bằng cách "rải" màu theo toạ độ 3D lên lưới UV.
# Mọi chi tiết (môi, lông mày, râu lún phún, má hồng, quầng mắt, lỗ chân lông, tóc) đều được TẠO RA bằng thuật toán
# từ vị trí đỉnh + vùng ảnh hưởng của các "target" khuôn mặt MakeHuman (CC0) — không dùng ảnh của ai khác.
import numpy as np, cv2, math

def _hash3(p):
    return np.modf(np.sin(p[..., 0] * 127.1 + p[..., 1] * 311.7 + p[..., 2] * 74.7) * 43758.5453)[0] % 1.0

def vnoise(p):  # value noise 3D, p: (...,3)
    i = np.floor(p); f = p - i; f = f * f * (3 - 2 * f); out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[..., 0] if dx else 1 - f[..., 0]) * (f[..., 1] if dy else 1 - f[..., 1]) * (f[..., 2] if dz else 1 - f[..., 2])
                out = out + w * _hash3(i + np.array([dx, dy, dz], float))
    return out

def fbm(p, oct=4):
    a, s, t = 0.5, 1.0, 0
    for _ in range(oct): t = t + a * vnoise(p * s); s *= 2.03; a *= 0.5
    return t

def raster(tris_uv, attrs, size):
    """tris_uv (T,3,2) uv 0..1; attrs (T,3,C) -> ảnh (size,size,C) nội suy trọng tâm + mặt nạ phủ"""
    C = attrs.shape[2]; out = np.zeros((size, size, C), np.float32); cov = np.zeros((size, size), np.uint8)
    P = np.empty_like(tris_uv); P[..., 0] = tris_uv[..., 0] * size; P[..., 1] = (1 - tris_uv[..., 1]) * size
    for t in range(len(P)):
        a, b, c = P[t]
        x0 = max(int(math.floor(min(a[0], b[0], c[0]))) - 1, 0); x1 = min(int(math.ceil(max(a[0], b[0], c[0]))) + 1, size - 1)
        y0 = max(int(math.floor(min(a[1], b[1], c[1]))) - 1, 0); y1 = min(int(math.ceil(max(a[1], b[1], c[1]))) + 1, size - 1)
        if x1 < x0 or y1 < y0: continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(d) < 1e-9: continue
        l1 = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / d
        l2 = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / d
        l3 = 1 - l1 - l2; e = -0.02
        m = (l1 >= e) & (l2 >= e) & (l3 >= e)
        if not m.any(): continue
        v = l1[m, None] * attrs[t, 0] + l2[m, None] * attrs[t, 1] + l3[m, None] * attrs[t, 2]
        yy, xx = ys[m].astype(int), xs[m].astype(int)
        out[yy, xx] = v; cov[yy, xx] = 1
    return out, cov

def dilate(img, cov, n=24):
    img = img.copy(); cov = cov.astype(np.float32)
    k = np.ones((3, 3), np.float32)
    for _ in range(n):
        s = cv2.filter2D(img * cov[..., None], -1, k, borderType=cv2.BORDER_REPLICATE); w = cv2.filter2D(cov, -1, k, borderType=cv2.BORDER_REPLICATE)
        fill = (cov == 0) & (w > 0); img[fill] = s[fill] / w[fill][:, None]; cov = np.where(fill, 1.0, cov)
    return img

def srgb_to_lin(c): c = np.asarray(c, float) / 255; return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def lin_to_srgb(c): c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)

def bake(tris_uv, tri_pos, tri_mask, size, tone, hair_rgb=(18, 15, 13), lip_rgb=(176, 104, 92), stubble=0.25, seed=0.0, eye=None):
    """tri_mask channels: 0 lips,1 brows,2 lids,3 undereye,4 nose,5 cheek,6 beard,7 hair,8 ear"""
    attrs = np.concatenate([tri_pos, tri_mask], 2).astype(np.float32)
    img, cov = raster(tris_uv, attrs, size); img = dilate(img, cov)
    pos = img[..., :3].astype(np.float64) + seed; M = img[..., 3:]
    lips, brow, lids, under, nose, cheek, beard, hair, ear = [np.clip(M[..., k], 0, 1) for k in range(9)]
    base = srgb_to_lin(tone)
    col = np.ones(img.shape[:2] + (3,), np.float32) * base
    # biến thiên sắc độ da lớn + đốm nhỏ
    low = fbm(pos * 18.0, 3); col *= (0.93 + 0.12 * low)[..., None]
    mott = vnoise(pos * 160.0); col *= (0.97 + 0.05 * mott)[..., None]
    red = np.array([1.0, 0.82, 0.78]); warm = np.array([1.0, 0.9, 0.85])
    col *= 1 + ((cheek * 0.55 + nose * 0.45 + ear * 0.6)[..., None] * (red - 1) * 0.55)
    col *= 1 - (under[..., None] * np.array([0.12, 0.16, 0.1]))
    col *= 1 - (lids[..., None] * np.array([0.08, 0.12, 0.08]))
    # môi
    lipc = srgb_to_lin(lip_rgb) * (0.92 + 0.12 * vnoise(pos * 300.0))[..., None]
    lm = np.clip(lips * 1.6 - 0.25, 0, 1) ** 1.2; col = col * (1 - lm[..., None]) + lipc * lm[..., None]
    # râu lún phún (chân râu xanh xám dưới da)
    st = (vnoise(pos * 900.0) > 0.55).astype(np.float32) * 0.6 + 0.4
    bm = np.clip(beard * 1.4 - 0.2, 0, 1) * stubble * st; col *= 1 - bm[..., None] * np.array([0.5, 0.48, 0.42])
    # lông mày: vẽ theo hình học (cung trên mắt), sợi lông xiên ra ngoài
    hc = srgb_to_lin(hair_rgb); strand = np.zeros(pos.shape[:2])
    bmask = np.zeros(pos.shape[:2])
    if eye is not None:
        ey, ez = eye; ax = np.abs(pos[..., 0] - seed); t = np.clip((ax - 0.011) / 0.05, 0, 1)
        zc = ez + 0.0175 + 0.004 * np.sin(t * math.pi * 0.8) - 0.0015 * t
        half = 0.0068 * (1 - t) + 0.0032 * t
        inside = np.clip(1 - np.abs(pos[..., 2] - seed - zc) / half, 0, 1) * (ax > 0.010) * (ax < 0.058) * (pos[..., 1] - seed < ey + 0.012)
        strand = vnoise(np.stack([(ax * 900.0) + (pos[..., 2] - seed) * 500.0, (pos[..., 2] - seed) * 2600.0 - ax * 1300.0, pos[..., 1] * 50.0], -1))
        edge = np.clip((ax - 0.010) / 0.006, 0, 1) * np.clip((0.058 - ax) / 0.012, 0, 1)
        bmask = np.clip(inside * 1.8, 0, 1) ** 0.8 * (0.72 + 0.28 * strand) * edge * (0.8 + 0.2 * (1 - t))
    col = col * (1 - bmask[..., None] * 0.95) + hc * bmask[..., None] * 0.95
    # tóc (vùng tóc ngắn): sợi theo chiều dọc
    hs = vnoise(np.stack([pos[..., 0] * 700.0, pos[..., 1] * 700.0, pos[..., 2] * 90.0], -1))
    hm = np.clip(hair * 1.5 - 0.2, 0, 1)
    if eye is not None:
        ey, ez = eye; x, y, z = pos[..., 0] - seed, pos[..., 1] - seed, pos[..., 2] - seed
        ss = lambda v, w: np.clip(v / w * 0.5 + 0.5, 0, 1)
        hl = 0.004 * (vnoise(pos * 260.0) - 0.5)
        g = np.maximum(ss(z - (ez + 0.062) + hl + 0.012 * np.clip((np.abs(x) - 0.045) / 0.03, 0, 1), 0.007), ss(y - (ey + 0.075) + hl, 0.007) * ss(z - (ez - 0.045), 0.01))
        g *= 1 - (np.abs(x) > 0.066) * (z < ez + 0.03) * 1.0
        hm = np.where(hair > 0.01, np.maximum(hm * 0.0, g), g * (z > ez - 0.06))
    hcol = hc * (0.7 + 0.6 * hs)[..., None]
    col = col * (1 - hm[..., None]) + hcol * hm[..., None]
    rgb = (lin_to_srgb(col) * 255 + 0.5).astype(np.uint8)
    # bản đồ pháp tuyến: lỗ chân lông + nếp nhỏ + sợi tóc
    h = vnoise(pos * 1400.0) * 0.6 + vnoise(pos * 500.0) * 0.4
    h = h * (1 - hm) * (1 - lm * 0.5) * 0.6 + hs * hm * 0.7 + strand * bmask * 0.5
    h = cv2.GaussianBlur(h.astype(np.float32), (0, 0), 0.7)
    gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3)
    s = 0.14; n = np.stack([-gx * s, gy * s, np.ones_like(h)], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
    nrm = ((n * 0.5 + 0.5) * 255 + 0.5).astype(np.uint8)
    return rgb, nrm
