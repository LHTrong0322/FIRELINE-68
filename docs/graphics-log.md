# Nhật ký đồ hoạ FIRELINE '68

## 2026-11-12 – v2 (nền tảng)
- Vật liệu PBR (albedo + normal + AO/roughness/metal) nướng bằng GPU cho: bê tông cốp pha, ván gỗ, nền đất đá, trần gỗ, bao cát, hòm đạn (stencil "ĐẠN 7,62"), vải quân phục, camo, kim loại súng, gỗ súng, sơn olive, da, da thuộc.
- Biến thiên vĩ mô theo toạ độ thế giới (chống lặp texture), vũng nước phản chiếu trên nền.
- Đèn bóng tròn có nón sáng thể tích giả, chập chờn; pool đèn động gán theo vị trí người chơi; bóng đổ từ đèn gần nhất (high: 1, ultra: 2).
- Hậu kỳ: MSAA x4 (HalfFloat), GTAO, Bloom, color grade "Realistic" (tham khảo phong cách Delta Force), CAS sharpen, vignette, film grain, chromatic aberration nhẹ.
- Dynamic resolution scaling giữ FPS; 4 mức chất lượng low/med/high/ultra.
- Nhân vật dựng lại bằng capsule: bộ đội (mũ cối + sao đỏ, dép cao su, khăn), lính Mỹ (M1 camo, áo giáp M69, giày lính); súng 3D chi tiết; tay có ngón trong góc nhìn thứ nhất; ngắm ADS.

## Backlog ý tưởng
- Decal máu/bụi trên tường, vết cháy sau nổ B40.
- Khói súng đọng lại trong không khí (volumetric fake), tàn lửa.
- Shell casing (vỏ đạn văng) có vật lý đơn giản.
- Hoạt ảnh nạp đạn chi tiết (tháo băng đạn).
- Screen-space reflections cho vũng nước (chỉ ultra).
- Biến thể tường: rễ cây, ống thông gió, dây điện võng giữa các đèn.
- Khuôn mặt nhân vật chi tiết hơn, hoạt ảnh chết theo ragdoll đơn giản.
- TAA / temporal upscaling cho mobile.

## 2026-11-12 – v3 bước 1: chất liệu chụp thật
- Thay chất liệu tự tạo bằng ảnh PBR quét từ vật thật của Poly Haven (CC0): tường bê tông `concrete_wall_006`, tường ván `wood_planks_dirt`, nền `dirt_floor`, trần `old_wood_floor`, cột/xà `rough_wood`, hòm đạn `green_rough_planks` (+ chữ stencil "ĐẠN 7,62" dạng decal), kim loại `green_metal_rust`. Mỗi bộ có diff + normal + ARM (AO/độ nhám/kim loại), 2K (tier med trở lên) và 1K (tier low).
- Phản chiếu môi trường bằng HDRI thật `boiler_room` (Poly Haven).
- Vẫn giữ chất liệu nướng GPU làm dự phòng nếu không tải được ảnh.
- Lính cầm súng đúng tư thế nhờ IK 2 khớp (trước đó dang tay chữ T).
- Tiếp theo: ánh sáng tính sẵn bằng Blender (baked GI), mô hình đồ vật thật, nhân vật có xương + hoạt ảnh.

## 2026-11-12 – v3.2: bản đồ lịch sử, NPC, giải cứu con tin, tối ưu
- 3 bản đồ: Địa đạo Củ Chi 1968 (trong hầm), Đồi A1 – Điện Biên Phủ 1954 (đêm, giao thông hào, hầm gạch, hố bộc phá, pháo sáng), Tà Cơn – Khe Sanh 1968 (sương sớm, đất đỏ bazan, đường băng thép PSP, dây thép gai, boongke bao cát, pháo).
- Ánh sáng ngoài trời: trăng/mặt trời có bóng đổ, bầu trời sao, sương mù, rừng cây + đồi núi xa, đống lửa bập bùng, pháo sáng thả dù.
- Chất liệu thật thêm: excavated_soil_wall, red_brick, red_laterite_soil_stones, brown_mud_02, metal_grate_rusty, burned_ground_01.
- Phe địch theo lịch sử: quân viễn chinh Pháp (1954: MAS-36, MAT-49, mũ M1 trơn) và lính Mỹ (1968).
- Tối ưu: gộp mảnh nhân vật (mergeGeometries, ~4x ít draw call), chuột thô (unadjustedMovement), nội suy vị trí người chơi online, gửi trạng thái 20Hz.

## 2026-11-12 – v3.3
- Cỏ tranh instanced (2 thẻ chéo, alpha test) lay theo gió trong vertex shader; dày ở Khe Sanh, thưa/khô ở Đồi A1.
- Mưa đêm Điện Biên Phủ (line streaks theo camera) + bề mặt ướt (giảm độ nhám nền/hào/tường) phản chiếu lửa và pháo sáng + tiếng mưa.

## 2026-11-13 — Nhân vật dựng bằng Blender (v3.4)
- Kỹ thuật: thân người liền một khối có xương (skinned mesh) thay cho ghép khối rời; hoạt ảnh làm sẵn trong Blender (IK 2 khớp để hai tay bám súng), chơi bằng AnimationMixer + crossfade, cộng thêm góc ngắm (pitch) lên xương ngực theo thời gian thực — cách làm "animation layer" phổ biến ở các game FPS lớn.
- Tệp: `tools/blender/build_soldier.py` (chạy bằng `pip install bpy`) → `public/assets/models/soldier.glb` (~340KB, 7 hoạt ảnh: aim, walk, run, idle, walkFree, captive, death).
- Game: `loadSoldierGLB()` + `buildSoldierSK()`; mũ, mặt, trang bị, súng gắn vào xương bằng `boneAttach()`. Nếu tải GLB lỗi sẽ tự quay về mô hình cũ (`buildSoldierProc`).
- Bài học: IK có pole target trong Blender bị kẹt khi mục tiêu gần vai → bỏ pole, solver tự gập khuỷu ra ngoài và đạt đúng vị trí.
- Kiểm tra: check.py low/high ĐẠT, playtest ĐẠT, ảnh cận cảnh `tools/closeup.py`.
- Backlog: nướng ánh sáng (lightmap) bằng Blender; thêm ngón tay/khuôn mặt dựng bằng Blender; quân phục có nếp gấp (normal map riêng); hoạt ảnh nạp đạn, ném lựu đạn, cúi người.

## 2026-11-13 — Ánh sáng tính sẵn + bóng nắng theo người chơi (v4.0)
- `bakeLighting()`: mỗi lần dựng bản đồ tính một ảnh ánh sáng (4 điểm ảnh/ô lưới): độ che khuất góc tường (AO) và ánh sáng của mọi đèn/đống lửa có kiểm tra bị tường che. Shader `addMacro` cộng ánh sáng này vào tường/sàn/hào → đèn ở xa vẫn toả ánh ấm, góc tường tối tự nhiên (trước đây chỉ vài đèn gần nhất có ánh sáng).
- Bóng mặt trời giờ đi theo người chơi (`followSun`, khung 96 m, bám lưới 4 m để không rung) → bóng nét hơn trên bản đồ rộng.
- Trời hoàng hôn mới (Him Lam) với mặt trời thấp, bầu trời cam.
- Backlog: dựng lại khuôn mặt bằng Blender; nếp gấp quân phục; ánh sáng tính sẵn cho cả trần hầm và vật thể.
